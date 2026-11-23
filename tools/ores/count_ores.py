"""Подсчёт руд в мире 1.12.2 по файлам .mca (тред «Руды»).

python -I count_ores.py <папка мира> [--radius R] [--out файл.json] [--dump-section]

- id блоков берутся из level.dat: FML -> Registries -> minecraft:blocks -> ids (K = имя, V = число);
- секции чанка: Blocks (+Add) + Data, а если стоит NotEnoughIDs — его поля (печатаются через --dump-section);
- считаются только чанки с TerrainPopulated=1, у которых все 8 соседей тоже есть и populated
  (края сгенерированной области недоделаны и занижают средние);
- слои высоты: 0-16, 16-32, 32-64, 64-128, 128-256.
"""
import gzip
import io
import json
import os
import struct
import sys
import zlib
from collections import defaultdict

# ---------- NBT ----------

def _read_tag(f, t):
    if t == 1: return struct.unpack(">b", f.read(1))[0]
    if t == 2: return struct.unpack(">h", f.read(2))[0]
    if t == 3: return struct.unpack(">i", f.read(4))[0]
    if t == 4: return struct.unpack(">q", f.read(8))[0]
    if t == 5: return struct.unpack(">f", f.read(4))[0]
    if t == 6: return struct.unpack(">d", f.read(8))[0]
    if t == 7:
        n = struct.unpack(">i", f.read(4))[0]; return f.read(n)
    if t == 8:
        n = struct.unpack(">H", f.read(2))[0]; return f.read(n).decode("utf-8", "replace")
    if t == 9:
        et = f.read(1)[0]; n = struct.unpack(">i", f.read(4))[0]
        return [_read_tag(f, et) for _ in range(n)]
    if t == 10:
        d = {}
        while True:
            tt = f.read(1)[0]
            if tt == 0: return d
            nl = struct.unpack(">H", f.read(2))[0]
            name = f.read(nl).decode("utf-8", "replace")
            d[name] = _read_tag(f, tt)
    if t == 11:
        n = struct.unpack(">i", f.read(4))[0]
        return list(struct.unpack(">%di" % n, f.read(4 * n)))
    if t == 12:
        n = struct.unpack(">i", f.read(4))[0]
        return list(struct.unpack(">%dq" % n, f.read(8 * n)))
    raise ValueError("tag %d" % t)


def read_nbt(data):
    f = io.BytesIO(data)
    t = f.read(1)[0]
    nl = struct.unpack(">H", f.read(2))[0]
    f.read(nl)
    return _read_tag(f, t)


def block_registry(world, what="minecraft:blocks"):
    lvl = read_nbt(gzip.open(os.path.join(world, "level.dat")).read())
    regs = lvl["FML"]["Registries"]
    ids = regs[what]["ids"]
    return {e["V"]: e["K"] for e in ids}


HILLS = {"minecraft:extreme_hills", "minecraft:smaller_extreme_hills", "minecraft:extreme_hills_with_trees",
         "minecraft:mutated_extreme_hills", "minecraft:mutated_extreme_hills_with_trees"}
MESA = {"minecraft:mesa", "minecraft:mesa_rock", "minecraft:mesa_clear_rock", "minecraft:mutated_mesa",
        "minecraft:mutated_mesa_rock", "minecraft:mutated_mesa_clear_rock"}


def iter_chunks(world, dim=None):
    rd = os.path.join(world, "DIM%d" % dim, "region") if dim else os.path.join(world, "region")
    for fn in os.listdir(rd):
        if not fn.endswith(".mca"): continue
        data = open(os.path.join(rd, fn), "rb").read()
        if len(data) < 8192: continue
        for i in range(1024):
            off = int.from_bytes(data[i * 4:i * 4 + 3], "big")
            if off == 0: continue
            p = off * 4096
            ln = struct.unpack(">i", data[p:p + 4])[0]
            comp = data[p + 4]
            raw = data[p + 5:p + 4 + ln]
            raw = zlib.decompress(raw) if comp == 2 else gzip.decompress(raw)
            yield read_nbt(raw)["Level"]


import numpy as np


def nibbles(arr):
    a = np.frombuffer(arr, dtype=np.uint8)
    out = np.empty(a.size * 2, dtype=np.uint16)
    out[0::2] = a & 15
    out[1::2] = a >> 4
    return out


def section_ids(sec):
    """Массивы id и meta на 4096 позиций (индекс = y<<8 | z<<4 | x)."""
    ids = np.frombuffer(sec["Blocks"], dtype=np.uint8).astype(np.uint16)
    if sec.get("Add") is not None:
        ids |= nibbles(sec["Add"]) << 8
    add2 = sec.get("Add2")                      # NotEnoughIDs, если id > 4095
    if add2 is not None:
        ids |= (np.frombuffer(add2, dtype=np.uint8).astype(np.uint16) if len(add2) == 4096
                else nibbles(add2)) << 12
    return ids, nibbles(sec["Data"])


LAYERS = [(0, 16), (16, 32), (32, 64), (64, 128), (128, 256)]


def main():
    world = sys.argv[1]
    radius = None
    out = None
    dump = "--dump-section" in sys.argv
    if "--radius" in sys.argv: radius = int(sys.argv[sys.argv.index("--radius") + 1])
    if "--out" in sys.argv: out = sys.argv[sys.argv.index("--out") + 1]
    dim = int(sys.argv[sys.argv.index("--dim") + 1]) if "--dim" in sys.argv else None
    reg = block_registry(world)
    want_names = {n for n in reg.values() if "ore" in n.split(":")[1] or n in (
        "forestry:resources", "minecraft:obsidian", "ic2:resource", "minecraft:netherrack", "appliedenergistics2:quartz_ore",
        "appliedenergistics2:charged_quartz_ore", "projectred-exploration:ore")}
    want_ids = {i for i, n in reg.items() if n in want_names}
    want_arr = np.array(sorted(want_ids), dtype=np.uint16)
    populated = {}
    chunks = []
    for lv in iter_chunks(world, dim):
        cx, cz = lv["xPos"], lv["zPos"]
        populated[(cx, cz)] = lv.get("TerrainPopulated", 0) == 1
        if radius is not None and (abs(cx) > radius or abs(cz) > radius):
            continue
        chunks.append(lv)
        if dump:
            for s in lv.get("Sections", []):
                print({k: (type(v).__name__, len(v) if hasattr(v, "__len__") else v) for k, v in s.items()})
                break
            dump = False
    counts = defaultdict(lambda: [0] * len(LAYERS))
    used = 0
    breg = block_registry(world, "minecraft:biomes")
    group_chunks = defaultdict(int)          # hills / mesa / other -> chunks
    group_ore = defaultdict(int)             # (group, key) -> blocks
    for lv in chunks:
        cx, cz = lv["xPos"], lv["zPos"]
        if not all(populated.get((cx + dx, cz + dz)) for dx in (-1, 0, 1) for dz in (-1, 0, 1)):
            continue
        used += 1
        bio = np.frombuffer(lv["Biomes"], dtype=np.uint8) if isinstance(lv.get("Biomes"), bytes) else np.array(lv.get("Biomes", [0]))
        names = [breg.get(int(b), "?") for b in bio]
        grp = "hills" if sum(n in HILLS for n in names) * 2 > len(names) else (
              "mesa" if sum(n in MESA for n in names) * 2 > len(names) else "other")
        group_chunks[grp] += 1
        for s in lv.get("Sections", []):
            ybase = s["Y"] * 16
            ids, meta = section_ids(s)
            mask = np.isin(ids, want_arr)
            if not mask.any(): continue
            for i in np.nonzero(mask)[0]:
                y = ybase + (int(i) >> 8)
                key = "%s:%d" % (reg[int(ids[i])], int(meta[i]))
                group_ore[(grp, key)] += 1
                for li, (a, b) in enumerate(LAYERS):
                    if a <= y < b:
                        counts[key][li] += 1
                        break
    groups = {g: {"chunks": n, "emerald_per_chunk": round(group_ore[(g, "minecraft:emerald_ore:0")] / n, 3),
                  "gold_per_chunk": round(group_ore[(g, "minecraft:gold_ore:0")] / n, 3)}
              for g, n in group_chunks.items()}
    print("группы биомов:", groups)
    res = {"world": world, "chunks": used, "layers": LAYERS, "groups": groups,
           "per_chunk": {k: [round(c / used, 3) for c in v] + [round(sum(v) / used, 3)]
                         for k, v in sorted(counts.items())}}
    print("чанков (populated, с соседями):", used)
    print("%-48s" % "блок:meta" + "".join("%9s" % ("%d-%d" % l) for l in LAYERS) + "%9s" % "всего")
    for k, v in sorted(res["per_chunk"].items(), key=lambda kv: -kv[1][-1]):
        print("%-48s" % k + "".join("%9.2f" % x for x in v))
    if out:
        json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
