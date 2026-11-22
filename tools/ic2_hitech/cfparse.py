"""Minimal Java class-file reader/writer (constant pool, members, attributes) for byte-level patches."""
import struct

class CP:
    def __init__(self, entries): self.e = entries  # index -> (tag, value)
    def utf(self, i): return self.e[i][1]
    def cls(self, i): return self.utf(self.e[i][1])
    def nat(self, i): n, t = self.e[i][1]; return self.utf(n), self.utf(t)
    def ref(self, i):
        tag, (c, nt) = self.e[i]; return self.cls(c), *self.nat(nt)

def read_cp(b, off):
    n = struct.unpack_from('>H', b, off)[0]; off += 2
    e = [None] * n; i = 1
    while i < n:
        tag = b[off]; off += 1
        if tag == 1:
            ln = struct.unpack_from('>H', b, off)[0]; off += 2
            e[i] = (1, mutf8(b[off:off+ln])); off += ln
        elif tag in (3, 4): e[i] = (tag, b[off:off+4]); off += 4
        elif tag in (5, 6): e[i] = (tag, b[off:off+8]); off += 8; i += 1
        elif tag in (7, 8, 16, 19, 20): e[i] = (tag, struct.unpack_from('>H', b, off)[0]); off += 2
        elif tag in (9, 10, 11, 12, 17, 18): e[i] = (tag, struct.unpack_from('>HH', b, off)); off += 4
        elif tag == 15: e[i] = (tag, (b[off], struct.unpack_from('>H', b, off+1)[0])); off += 3
        else: raise ValueError('cp tag %d' % tag)
        i += 1
    return CP(e), off

def mutf8(raw):
    out = []; i = 0
    while i < len(raw):
        c = raw[i]
        if c < 0x80: out.append(chr(c)); i += 1
        elif c & 0xE0 == 0xC0: out.append(chr(((c & 0x1F) << 6) | (raw[i+1] & 0x3F))); i += 2
        else: out.append(chr(((c & 0x0F) << 12) | ((raw[i+1] & 0x3F) << 6) | (raw[i+2] & 0x3F))); i += 3
    return ''.join(out)

def enc_mutf8(s):
    out = bytearray()
    for ch in s:
        c = ord(ch)
        if 0 < c < 0x80: out.append(c)
        elif c < 0x800: out += bytes([0xC0 | (c >> 6), 0x80 | (c & 0x3F)])
        elif c < 0x10000: out += bytes([0xE0 | (c >> 12), 0x80 | ((c >> 6) & 0x3F), 0x80 | (c & 0x3F)])
        else:
            c -= 0x10000; hi = 0xD800 + (c >> 10); lo = 0xDC00 + (c & 0x3FF)
            out += enc_mutf8(chr(hi)) + enc_mutf8(chr(lo))
    return bytes(out)

def write_cp(cp):
    out = bytearray(struct.pack('>H', len(cp.e)))
    i = 1
    while i < len(cp.e):
        tag, v = cp.e[i]
        out.append(tag)
        if tag == 1: r = enc_mutf8(v); out += struct.pack('>H', len(r)) + r
        elif tag in (3, 4, 5, 6): out += v
        elif tag in (7, 8, 16, 19, 20): out += struct.pack('>H', v)
        elif tag in (9, 10, 11, 12, 17, 18): out += struct.pack('>HH', *v)
        elif tag == 15: out += struct.pack('>BH', *v)
        i += 2 if tag in (5, 6) else 1
    return bytes(out)

def read_attrs(b, off):
    n = struct.unpack_from('>H', b, off)[0]; off += 2; res = []
    for _ in range(n):
        name, ln = struct.unpack_from('>HI', b, off); off += 6
        res.append([name, bytearray(b[off:off+ln])]); off += ln
    return res, off

def write_attrs(attrs):
    out = bytearray(struct.pack('>H', len(attrs)))
    for name, data in attrs: out += struct.pack('>HI', name, len(data)) + data
    return bytes(out)

class ClassFile:
    def __init__(self, b):
        self.minor, self.major = struct.unpack_from('>HH', b, 4)
        self.cp, off = read_cp(b, 8)
        self.access, self.this, self.super_, ni = struct.unpack_from('>HHHH', b, off); off += 8
        self.interfaces = list(struct.unpack_from('>%dH' % ni, b, off)); off += 2 * ni
        self.fields, off = self._members(b, off)
        self.methods, off = self._members(b, off)
        self.attrs, off = read_attrs(b, off)
    def _members(self, b, off):
        n = struct.unpack_from('>H', b, off)[0]; off += 2; res = []
        for _ in range(n):
            acc, name, desc = struct.unpack_from('>HHH', b, off); off += 6
            attrs, off = read_attrs(b, off); res.append([acc, name, desc, attrs])
        return res, off
    def add(self, tag, v):
        for i, e in enumerate(self.cp.e):
            if e == (tag, v): return i
        self.cp.e.append((tag, v)); return len(self.cp.e) - 1
    def utf8(self, s): return self.add(1, s)
    def klass(self, name): return self.add(7, self.utf8(name))
    def string(self, s): return self.add(8, self.utf8(s))
    def nat(self, n, d): return self.add(12, (self.utf8(n), self.utf8(d)))
    def mref(self, owner, n, d): return self.add(10, (self.klass(owner), self.nat(n, d)))
    def to_bytes(self):
        out = bytearray(b'\xca\xfe\xba\xbe' + struct.pack('>HH', self.minor, self.major))
        out += write_cp(self.cp)
        out += struct.pack('>HHHH', self.access, self.this, self.super_, len(self.interfaces))
        out += struct.pack('>%dH' % len(self.interfaces), *self.interfaces)
        for group in (self.fields, self.methods):
            out += struct.pack('>H', len(group))
            for acc, name, desc, attrs in group: out += struct.pack('>HHH', acc, name, desc) + write_attrs(attrs)
        out += write_attrs(self.attrs)
        return bytes(out)
