"""Remove CustomMobSpawner from the test instance and re-enable the vanilla mob spawner in every world.

level.dat is gzip NBT; the gamerule is a TAG_String: 08 | 00 0D 'doMobSpawning' | 00 05 'false'.
Replacing it with a length-4 'true' string is valid NBT (no offsets to fix). Backups: level.dat.cms.bak
"""
import gzip, os, shutil, sys

ROOT = os.path.expandvars(r"%APPDATA%\PrismLauncher\instances\1.12.2-edit")
MODS = os.path.join(ROOT, "minecraft", "mods")
SAVES = os.path.join(ROOT, "minecraft", "saves")
BK = os.path.join(ROOT, "removed_mods", "6_custommobspawner")

os.makedirs(BK, exist_ok=True)
jar = os.path.join(MODS, "CustomMobSpawner-3.11.5.jar")
if os.path.exists(jar):
    shutil.move(jar, BK); print("moved CustomMobSpawner")

OLD = b"\x08\x00\x0ddoMobSpawning\x00\x05false"
NEW = b"\x08\x00\x0ddoMobSpawning\x00\x04true"
for w in os.listdir(SAVES):
    p = os.path.join(SAVES, w, "level.dat")
    if not os.path.exists(p): continue
    data = gzip.open(p).read()
    n = data.count(OLD)
    if n:
        shutil.copyfile(p, p + ".cms.bak")
        with gzip.open(p, "wb") as f: f.write(data.replace(OLD, NEW))
    check = gzip.open(p).read()
    state = "true" if NEW in check or b"doMobSpawning\x00\x04true" in check else "false/absent"
    print(f"{w.encode('unicode_escape').decode()}: fixed {n}, now {state}")
