"""Ищет в мире точку в пещере (воздух) рядом с видимыми рудами для скриншота автотеста.

python -I -X utf8 find_view.py <мир> <ymin> <ymax> [радиус_чанков]
Печатает лучшие точки: позиция глаза, yaw/pitch на центр видимых руд, сколько и каких руд видно.
"""
import math, sys
import numpy as np

exec(open(__file__.replace("find_view.py", "count_ores.py"), encoding="utf-8").read().replace(
    'if __name__ == "__main__":\n    main()', ''))

world, ymin, ymax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
R = int(sys.argv[4]) if len(sys.argv) > 4 else 8
reg = block_registry(world)
ore_ids = {i for i, n in reg.items() if ("ore" in n.split(":")[1] and "oreberr" not in n and "ore_fluid" not in n)
           or n in ("forestry:resources", "ic2:resource")}
air = {i for i, n in reg.items() if n in ("minecraft:air", "minecraft:cave_air")}
# собрать кусок мира 3D: x,z в блоках, y 0..80
X0 = -R * 16; size = 2 * R * 16 + 16
vol = np.zeros((size, 81, size), dtype=np.uint16)
for lv in iter_chunks(world):
    cx, cz = lv["xPos"], lv["zPos"]
    if abs(cx) > R or abs(cz) > R: continue
    for s in lv["Sections"]:
        y0 = s["Y"] * 16
        if y0 > 80: continue
        ids = section_ids(s)[0].reshape(16, 16, 16)  # y, z, x
        for yy in range(16):
            if y0 + yy > 80: break
            vol[cx * 16 - X0:cx * 16 - X0 + 16, y0 + yy, cz * 16 - X0:cz * 16 - X0 + 16] = ids[yy].T
is_air = np.isin(vol, list(air))
is_ore = np.isin(vol, list(ore_ids))
# руда, у которой есть сосед-воздух (видна из пещеры)
exp = np.zeros_like(is_ore)
for ax in range(3):
    for d in (1, -1):
        exp |= np.roll(is_air, d, axis=ax)
vis = is_ore & exp
best = []
pts = np.argwhere(is_air[:, ymin:ymax + 1, :])
rng = np.random.default_rng(1)
if len(pts) > 40000:
    pts = pts[rng.choice(len(pts), 40000, replace=False)]
for x, yy, z in pts:
    y = yy + ymin
    if not is_air[x, y + 1, z] if y + 1 <= 80 else True: continue   # нужен проход в 2 блока
    sl = vis[max(0, x - 6):x + 7, max(0, y - 4):y + 5, max(0, z - 6):z + 7]
    n = int(sl.sum())
    if n >= 12:
        idx = np.argwhere(sl) + [max(0, x - 6), max(0, y - 4), max(0, z - 6)]
        best.append((n, x, y, z, idx.mean(axis=0)))
best.sort(key=lambda t: -t[0])
seen = []
for n, x, y, z, c in best:
    if any(abs(x - a) < 12 and abs(z - b) < 12 for a, b in seen): continue
    seen.append((x, z))
    ex, ey, ez = x + X0 + 0.5, y, z + X0 + 0.5
    dx, dy, dz = c[0] + X0 + 0.5 - ex, c[1] + 0.5 - (ey + 1.62), c[2] + X0 + 0.5 - ez
    yaw = math.degrees(math.atan2(-dx, dz)); pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    sl = vol[max(0, x - 6):x + 7, max(0, y - 4):y + 5, max(0, z - 6):z + 7][vis[max(0, x - 6):x + 7, max(0, y - 4):y + 5, max(0, z - 6):z + 7]]
    names = {}
    for b in sl: names[reg[int(b)]] = names.get(reg[int(b)], 0) + 1
    print("видно %d руд: tp %.1f %d %.1f yaw %.0f pitch %.0f  %s" % (n, ex, ey, ez, yaw, pitch, names))
    if len(seen) >= 6: break
