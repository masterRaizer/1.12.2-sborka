"""Правка конфигов генерации руд (тред «Руды», 22.11.2026).

Запуск: python -I patch_ores.py <папка config> [--check]
Каждый изменённый файл копируется рядом как <имя>.bak-ores (если копии ещё нет).
Новые файлы CoFH World 05_pack_*.json копируются из папки cofh рядом со скриптом.
Откат: rollback.bat (возвращает .bak-ores и удаляет 05_pack_*.json).
"""
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHANGED = []


def backup(path):
    bak = path + ".bak-ores"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)


def write_if_changed(cfg, rel, new_text, old_text):
    path = os.path.join(cfg, rel)
    if new_text == old_text:
        print("  уже так:", rel)
        return
    backup(path)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new_text)
    CHANGED.append(rel)
    print("  изменён:", rel)


def read(cfg, rel):
    with open(os.path.join(cfg, rel), encoding="utf-8", newline="") as f:
        return f.read()


def sub_once(text, pattern, repl, rel, flags=0):
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit("НЕ НАЙДЕНО в %s: %s" % (rel, pattern))
    return new


def forge_keys(cfg, rel, pairs, scope=None):
    """pairs: {'I:Key': 'value'}; scope: текст-заголовок блока, внутри которого искать."""
    old = read(cfg, rel)
    text = old
    start, end = 0, len(text)
    if scope:
        start = text.index(scope)
        # конец блока: первая строка, где закрывается скобка с тем же отступом
        indent = text.rfind("\n", 0, start) + 1
        ind = text[indent:start]
        m = re.compile(r"\n" + re.escape(ind) + r"\}").search(text, start)
        end = m.end()
    part = text[start:end]
    for key, val in pairs.items():
        part = sub_once(part, r"(^\s*" + re.escape(key) + r"=)[^\r\n]*", r"\g<1>" + val, rel, re.M)
    write_if_changed(cfg, rel, text[:start] + part + text[end:], old)


def ic2(cfg):
    rel = "IC2.ini"
    old = read(cfg, rel)
    want = {
        "worldgen / copper": {"enabled": "false"},
        "worldgen / lead": {"enabled": "false"},
        "worldgen / tin": {"enabled": "false"},
        "worldgen / uranium": {"enabled": "true", "count": "4", "size": "16",
                               "minHeight": "0", "maxHeight": "64"},
    }
    out, sec, seen = [], None, set()
    for line in old.splitlines(True):
        m = re.match(r"\s*\[(.+)\]\s*$", line)
        if m:
            sec = m.group(1).strip()
        elif sec in want:
            km = re.match(r"(\s*)([A-Za-z]+)(\s*=\s*)([^\r\n]*)(\r?\n?)$", line)
            if km and km.group(2) in want[sec]:
                line = km.group(1) + km.group(2) + km.group(3) + want[sec][km.group(2)] + km.group(5)
                seen.add((sec, km.group(2)))
        out.append(line)
    need = {(s, k) for s, d in want.items() for k in d}
    if need - seen:
        raise SystemExit("IC2.ini: не найдены ключи %s" % sorted(need - seen))
    write_if_changed(cfg, rel, "".join(out), old)


def ie(cfg):
    rel = "immersiveengineering.cfg"
    old = read(cfg, rel)
    text = old
    vals = {
        "ore_bauxite": ["17", "40", "85", "3", "100"],   # алюминий: источник IE, 3 жилы размера 17 (~22 блока)
        "ore_copper": ["0"], "ore_lead": ["0"], "ore_nickel": ["0"],
        "ore_silver": ["0"], "ore_uranium": ["0"],        # размер 0 = выключено (по описанию IE)
    }
    for key, nums in vals.items():
        m = re.search(r"I:" + key + r" <\r?\n((?:\s*-?\d+\r?\n){5})", text)
        if not m:
            raise SystemExit("IE: нет " + key)
        lines = m.group(1).splitlines(True)
        for i, v in enumerate(nums):
            lines[i] = re.sub(r"-?\d+", v, lines[i], count=1)
        text = text[:m.start(1)] + "".join(lines) + text[m.end(1):]
    write_if_changed(cfg, rel, text, old)


def thermal(cfg):
    rel = "cofh/world/01_thermalfoundation_ores.json"
    old = read(cfg, rel)
    d = json.loads(old)
    p = d["populate"]
    def pure(name, t):
        p[name]["generator"]["block"] = {"name": "thermalfoundation:ore", "properties": {"type": t}}
    p["copper"]["generator"]["cluster-size"] = 18; p["copper"]["cluster-count"] = 2
    p["tin"]["generator"]["cluster-size"] = 18; p["tin"]["cluster-count"] = 2
    pure("silver", "silver"); p["silver"]["generator"]["cluster-size"] = 18
    p["silver"]["cluster-count"] = {"min": 1, "max": 3}
    pure("lead", "lead"); p["lead"]["generator"]["cluster-size"] = 18
    p["lead"]["cluster-count"] = {"min": 1, "max": 3}
    p["nickel"]["generator"]["cluster-size"] = 17; p["nickel"]["cluster-count"] = 1
    p["copper_ocean"]["enabled"] = "false"
    p["copper_high"]["enabled"] = "false"
    new = json.dumps(d, indent="\t") + "\n"
    if "\r\n" in old:
        new = new.replace("\n", "\r\n")
    if json.loads(new) == json.loads(old):
        new = old
    write_if_changed(cfg, rel, new, old)


def adlods(cfg):
    for ore in ["coal", "iron", "gold", "redstone", "diamond", "lapis", "emerald"]:
        rel = "adlods/VanillaGen/%s.cfg" % ore
        old = read(cfg, rel)
        i = old.index("Dimensions {")
        j = old.index("S:blackList <", i)
        k = old.index(">", j)
        block = old[j:k]
        if re.search(r"^\s*0\s*$", block, re.M):
            write_if_changed(cfg, rel, old, old)
            continue
        nl = "\r\n" if "\r\n" in old else "\n"
        tail = block[block.rfind("\n") + 1:]          # отступ перед ">"
        new_block = "S:blackList <" + nl + "            0" + nl + tail
        write_if_changed(cfg, rel, old[:j] + new_block + old[k:], old)


def new_files(cfg):
    src = os.path.join(HERE, "cofh")
    for n in sorted(os.listdir(src)):
        if n.startswith("05_pack_") and n.endswith(".json"):
            dst = os.path.join(cfg, "cofh", "world", n)
            data = open(os.path.join(src, n), "rb").read()
            if os.path.exists(dst) and open(dst, "rb").read() == data:
                print("  уже так:", "cofh/world/" + n)
                continue
            open(dst, "wb").write(data)
            CHANGED.append("cofh/world/" + n)
            print("  новый:  ", "cofh/world/" + n)


def main():
    cfg = sys.argv[1]
    print("config:", cfg)
    try:
        thermal(cfg)
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        new_files(cfg)
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        adlods(cfg)
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        ic2(cfg)
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        forge_keys(cfg, "mekanism.cfg", {"I:CopperPerChunk": "0", "I:TinPerChunk": "0",
                                         "I:OsmiumPerChunk": "4", "I:OsmiumVeinSize": "18"})
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        ie(cfg)
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        forge_keys(cfg, "ProjectRed.cfg", {'B:"%s Ore"' % o: "false" for o in
                   ["Copper", "Electrotine", "Peridot", "Ruby", "Sapphire", "Silver", "Tin"]},
                   scope='"world gen" {')
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        forge_keys(cfg, "forestry/common.cfg", {"B:apatite": "false", "B:copper": "false", "B:tin": "false"},
                   scope="ore {")
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        forge_keys(cfg, "AppliedEnergistics2/AppliedEnergistics2.cfg",
                   {"I:quartzOresClusterAmount": "5", "I:quartzOresPerCluster": "17"}, scope="worldgen {")
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        forge_keys(cfg, "brandon3055/DraconicEvolution.cfg", {"B:disableOreSpawnOverworld": "true"})
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        forge_keys(cfg, "gobber.cfg", {"B:worldgenGobber": "true"})   # true = ВЫКЛЮЧИТЬ руду Gobber (так в моде)
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    try:
        forge_keys(cfg, "modernbackports/02a.cfg", {"B:copperOre": "false"})
    except FileNotFoundError as e:
        print("  нет файла, пропуск:", e.filename)
    print("изменено файлов:", len(CHANGED))


if __name__ == "__main__":
    main()
