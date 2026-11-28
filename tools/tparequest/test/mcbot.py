"""Minimal Minecraft 1.12.2 (protocol 340) offline-mode bot: login, keep-alive, teleport confirm, chat.
Enough to test server commands from real (non-op) players."""
import json
import socket
import struct
import threading
import time
import zlib


def varint(n):
    out = b""
    n &= 0xFFFFFFFF
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out += bytes([b | 0x80])
        else:
            return out + bytes([b])


def mcstr(s):
    b = s.encode("utf-8")
    return varint(len(b)) + b


def read_varint_buf(buf, i):
    n = shift = 0
    while True:
        b = buf[i]
        i += 1
        n |= (b & 0x7F) << shift
        shift += 7
        if not b & 0x80:
            break
    if n & 0x80000000:
        n -= 1 << 32
    return n, i


def read_str(buf, i):
    n, i = read_varint_buf(buf, i)
    return buf[i:i + n].decode("utf-8"), i + n


def flatten(comp):
    if isinstance(comp, str):
        return comp
    if isinstance(comp, list):
        return "".join(flatten(c) for c in comp)
    s = comp.get("text", "")
    if "translate" in comp:
        s += comp["translate"] + " " + " ".join(flatten(w) for w in comp.get("with", []))
    for e in comp.get("extra", []):
        s += flatten(e)
    return s


class Bot:
    def __init__(self, name, host="127.0.0.1", port=25599):
        self.name = name
        self.sock = socket.create_connection((host, port), timeout=30)
        self.threshold = -1
        self.chat = []  # (time, raw_json, text)
        self.pos = None
        self.dim = 0
        self.positions = []
        self.alive = True
        self.disconnect_reason = None
        self.lock = threading.Lock()
        self._login(host, port)
        self.t = threading.Thread(target=self._loop, daemon=True)
        self.t.start()

    # ---- framing ----
    def _recv_exact(self, n):
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("closed")
            data += chunk
        return data

    def _recv_varint(self):
        n = shift = 0
        while True:
            b = self._recv_exact(1)[0]
            n |= (b & 0x7F) << shift
            shift += 7
            if not b & 0x80:
                return n

    def _recv_packet(self):
        length = self._recv_varint()
        data = self._recv_exact(length)
        if self.threshold >= 0:
            dlen, i = read_varint_buf(data, 0)
            data = zlib.decompress(data[i:]) if dlen else data[i:]
        pid, i = read_varint_buf(data, 0)
        return pid, data[i:]

    def send(self, pid, payload=b""):
        body = varint(pid) + payload
        if self.threshold >= 0:
            if len(body) >= self.threshold:
                body = varint(len(body)) + zlib.compress(body)
            else:
                body = varint(0) + body
        with self.lock:
            self.sock.sendall(varint(len(body)) + body)

    # ---- login ----
    def _login(self, host, port):
        self.send(0x00, varint(340) + mcstr(host) + struct.pack(">H", port) + varint(2))
        self.send(0x00, mcstr(self.name))
        while True:
            pid, d = self._recv_packet()
            if pid == 0x03:
                self.threshold, _ = read_varint_buf(d, 0)
            elif pid == 0x02:
                return
            elif pid == 0x00:
                raise ConnectionError("login refused: " + read_str(d, 0)[0])

    # ---- play ----
    def _loop(self):
        try:
            while True:
                pid, d = self._recv_packet()
                if pid == 0x1F:  # keep alive
                    self.send(0x0B, d[:8])
                elif pid == 0x0F:  # chat
                    raw, _ = read_str(d, 0)
                    try:
                        text = flatten(json.loads(raw))
                    except Exception:
                        text = raw
                    self.chat.append((time.time(), raw, text))
                elif pid == 0x2F:  # player position and look
                    x, y, z = struct.unpack(">ddd", d[:24])
                    flags = d[32]
                    tid, _ = read_varint_buf(d, 33)
                    cur = self.pos or (0.0, 0.0, 0.0)
                    self.pos = (x + cur[0] if flags & 1 else x, y + cur[1] if flags & 2 else y,
                                z + cur[2] if flags & 4 else z)
                    self.positions.append((time.time(), self.dim, self.pos))
                    self.send(0x00, varint(tid))
                    if self.pos:
                        self.send(0x0E, struct.pack(">dddff?", self.pos[0], self.pos[1], self.pos[2], 0.0, 0.0, True))
                elif pid == 0x23:  # join game
                    self.dim = struct.unpack(">i", d[5:9])[0]
                elif pid == 0x35:  # respawn (dimension change)
                    self.dim = struct.unpack(">i", d[:4])[0]
                elif pid == 0x1A:  # disconnect
                    self.disconnect_reason = read_str(d, 0)[0]
                    break
        except Exception as e:  # noqa
            if self.alive:
                self.disconnect_reason = self.disconnect_reason or repr(e)
        self.alive = False

    def say(self, text):
        self.send(0x02, mcstr(text))

    def wait_chat(self, needle, since, timeout=5.0):
        end = time.time() + timeout
        while time.time() < end:
            for t, raw, text in list(self.chat):
                if t >= since and (needle in text or needle in raw):
                    return raw, text
            time.sleep(0.05)
        return None

    def wait_pos(self, pred, since, timeout=5.0):
        end = time.time() + timeout
        while time.time() < end:
            for t, dim, p in list(self.positions):
                if t >= since and pred(dim, p):
                    return dim, p
            time.sleep(0.05)
        return None

    def close(self):
        self.alive = False
        try:
            self.sock.close()
        except Exception:
            pass
