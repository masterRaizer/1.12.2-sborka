"""End-to-end test of tparequest on a bare Forge 2860 server with two non-op bots.
Usage: python -I run_test.py <server_dir> <java_exe>"""
import os
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcbot import Bot  # noqa: E402

srv, java = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(srv, "config"), exist_ok=True)
with open(os.path.join(srv, "config", "tparequest.cfg"), "w", encoding="utf-8") as f:
    f.write("general {\n    B:enabled=true\n    I:timeoutSeconds=5\n    B:allowTpaHere=true\n    B:allowCrossDimension=true\n}\n")
for fn in ("ops.json",):
    p = os.path.join(srv, fn)
    if os.path.exists(p):
        os.remove(p)

log = open(os.path.join(srv, "test-console.log"), "w", encoding="utf-8", errors="replace")
proc = subprocess.Popen([java, "-Xmx2G", "-jar", "forge-1.12.2-14.23.5.2860.jar", "nogui"], cwd=srv,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
lines = []


def reader():
    for raw in proc.stdout:
        s = raw.decode("utf-8", "replace")
        lines.append(s)
        log.write(s)
        log.flush()


threading.Thread(target=reader, daemon=True).start()


def console(cmd):
    proc.stdin.write((cmd + "\n").encode())
    proc.stdin.flush()


def wait_line(needle, timeout):
    end = time.time() + timeout
    while time.time() < end:
        if any(needle in s for s in lines):
            return True
        if proc.poll() is not None:
            return False
        time.sleep(0.2)
    return False


results = []


def check(name, ok, info=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + ("  " + str(info) if info and not ok else ""), flush=True)


try:
    assert wait_line("Done (", 240), "server did not start"
    check("mod registered commands", any("TPA commands registered" in s for s in lines))
    a = Bot("Alice")
    time.sleep(1)
    b = Bot("Bob")
    time.sleep(3)
    check("bots joined (vanilla clients, not op)", a.alive and b.alive, (a.disconnect_reason, b.disconnect_reason))

    # 1. /tpa + clickable accept
    console("tp Bob 100 4 100")
    console("tp Alice 0 4 0")
    time.sleep(1.5)
    t = time.time()
    a.say("/tpa Bob")
    got = b.wait_chat("хочет телепортироваться", t)
    check("target gets request text", got)
    btn = b.wait_chat("/tpaccept Alice", t)
    check("accept button has RUN_COMMAND /tpaccept Alice", btn and '"run_command"' in btn[0], btn)
    deny = b.wait_chat("/tpadeny Alice", t)
    check("deny button has /tpadeny Alice", deny and '✖' in deny[0])
    check("hint line with typed command", b.wait_chat("Или введите /tpaccept", t))
    check("sender gets confirmation", a.wait_chat("Запрос отправлен игроку Bob", t))
    t = time.time()
    b.say("/tpaccept")
    moved = a.wait_pos(lambda d, p: abs(p[0] - 100.5) < 2 and abs(p[2] - 100.5) < 2, t)
    check("/tpaccept teleports Alice to Bob", moved, a.positions[-3:])
    check("sender told accepted", a.wait_chat("принял ваш запрос", t))

    # 2. deny
    console("tp Alice 0 4 0")
    time.sleep(1.5)
    t = time.time()
    a.say("/tpa Bob")
    b.wait_chat("хочет", t)
    b.say("/tpadeny Alice")
    check("/tpadeny tells sender", a.wait_chat("отклонил ваш запрос", t))
    time.sleep(1)
    check("deny does not move", abs(a.pos[0] - 0.5) < 2, a.pos)

    # 3. /tpahere
    t = time.time()
    b.say("/tpahere Alice")
    check("tpahere text", a.wait_chat("зовёт вас", t))
    a.say("/tpaccept Bob")
    moved = a.wait_pos(lambda d, p: abs(p[0] - 100.5) < 2, t)
    check("/tpahere moves Alice (accepting player) to Bob", moved)

    # 3b. alias /tpaacept (owner's spelling)
    console("tp Alice 0 4 0")
    time.sleep(1.5)
    t = time.time()
    a.say("/tpa Bob")
    b.wait_chat("хочет", t)
    b.say("/tpaacept")
    moved = a.wait_pos(lambda d, p: abs(p[0] - 100.5) < 2 and abs(p[2] - 100.5) < 2, t)
    check("alias /tpaacept accepts", moved)

    # 4. errors
    t = time.time()
    a.say("/tpa Alice")
    check("self request refused", a.wait_chat("самому себе", t))
    a.say("/tpa Nobody")
    check("offline target refused", a.wait_chat("не в сети", t))
    b.say("/tpaccept")
    check("no requests message", b.wait_chat("нет входящих", t))
    a.say("/tpacancel")
    check("nothing to cancel message", a.wait_chat("нет отправленных", t))

    # 5. cancel
    t = time.time()
    a.say("/tpa Bob")
    b.wait_chat("хочет", t)
    a.say("/tpacancel")
    check("cancel tells target", b.wait_chat("отменил запрос", t))

    # 6. timeout (5 s in test config)
    t = time.time()
    a.say("/tpa Bob")
    check("timeout: sender told", a.wait_chat("истёк", t, timeout=9))
    check("timeout: target told", b.wait_chat("истёк", t, timeout=2))
    b.say("/tpaccept")
    check("expired request can't be accepted", b.wait_chat("нет входящих", t, timeout=3))

    # 7. cross-dimension: Bob to the Nether, Alice /tpa Bob
    console("forge setdimension Bob -1")
    time.sleep(3)
    console("tp Bob 20 70 20")
    time.sleep(1.5)
    check("Bob is in the Nether", b.dim == -1, b.dim)
    console("tp Bob ~ ~ ~")
    time.sleep(1)
    print("bob server:", [s.strip()[-50:] for s in lines if "Teleported Bob" in s][-1:], "bob bot:", b.positions[-4:], flush=True)
    t = time.time()
    a.say("/tpa Bob")
    b.wait_chat("хочет", t)
    b.say("/tpaccept")
    moved = a.wait_pos(lambda d, p: d == -1 and abs(p[0] - 20.5) < 2 and abs(p[2] - 20.5) < 2, t, timeout=8)
    check("cross-dimension teleport to Nether", moved, (a.dim, [(round(tt-t,2), d, pp) for tt, d, pp in a.positions if tt >= t]))
    console("tp Alice ~ ~ ~")
    time.sleep(1)
    print("server says:", [s.strip()[-60:] for s in lines if "Teleported Alice" in s][-1:], flush=True)

    # 8. logout cancels
    t = time.time()
    b.say("/tpa Alice")
    a.wait_chat("хочет", t)
    b.close()
    check("logout of sender cancels request", a.wait_chat("вышел с сервера", t, timeout=6))
    check("Alice still connected", a.alive, a.disconnect_reason)
    a.close()
    time.sleep(2)
finally:
    try:
        console("stop")
        proc.wait(60)
    except Exception:
        proc.kill()
    log.close()

exc = [s for s in lines if "Exception" in s or "ERROR" in s]
print("console exceptions/errors:", len(exc))
for s in exc[:10]:
    print("  ", s.strip()[:200])
failed = [n for n, ok in results if not ok]
print("RESULT: %d/%d passed" % (len(results) - len(failed), len(results)))
sys.exit(1 if failed else 0)
