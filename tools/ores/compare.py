"""Сравнение old/new: блоков руды на чанк по слоям, все источники одной руды сложены."""
import json, sys

RES = [
    ("Уголь", ["minecraft:coal_ore:0"]),
    ("Железо", ["minecraft:iron_ore:0"]),
    ("Золото", ["minecraft:gold_ore:0"]),
    ("Редстоун", ["minecraft:redstone_ore:0"]),
    ("Алмаз", ["minecraft:diamond_ore:0"]),
    ("Лазурит", ["minecraft:lapis_ore:0"]),
    ("Изумруд", ["minecraft:emerald_ore:0"]),
    ("Медь", ["thermalfoundation:ore:0", "ic2:resource:1", "mekanism:oreblock:1", "projectred-exploration:ore:3",
              "forestry:resources:1", "immersiveengineering:ore:0", "modernbackports:copper_ore:0"]),
    ("Олово", ["thermalfoundation:ore:1", "ic2:resource:3", "mekanism:oreblock:2", "projectred-exploration:ore:4",
               "forestry:resources:2"]),
    ("Серебро", ["thermalfoundation:ore:2", "projectred-exploration:ore:5", "immersiveengineering:ore:3"]),
    ("Свинец", ["thermalfoundation:ore:3", "ic2:resource:2", "immersiveengineering:ore:2"]),
    ("Никель", ["thermalfoundation:ore:5", "immersiveengineering:ore:4"]),
    ("Уран", ["ic2:resource:4", "immersiveengineering:ore:5"]),
    ("Боксит (алюминий)", ["immersiveengineering:ore:1"]),
    ("Осмий", ["mekanism:oreblock:0"]),
    ("Истинный кварц", ["appliedenergistics2:quartz_ore:0"]),
    ("Заряженный кварц", ["appliedenergistics2:charged_quartz_ore:0"]),
    ("Апатит", ["forestry:resources:0"]),
    ("Рубин", ["projectred-exploration:ore:0"]),
    ("Сапфир", ["projectred-exploration:ore:1"]),
    ("Перидот", ["projectred-exploration:ore:2"]),
    ("Электротин", ["projectred-exploration:ore:6"]),
    ("Дракониевая", ["draconicevolution:draconium_ore:0"]),
    ("Гоббер", ["gb:gobber_ore:0"]),
]


def get(d, keys):
    out = [0.0] * 6
    for k in keys:
        for i, v in enumerate(d["per_chunk"].get(k, [0] * 6)):
            out[i] += v
    return out


def main():
    old = json.load(open(sys.argv[1], encoding="utf-8"))
    new = json.load(open(sys.argv[2], encoding="utf-8"))
    hdr = ["0–16", "16–32", "32–64", "64–128"]
    lines = ["| Руда | " + " | ".join("%s было → стало" % h for h in hdr) + " | Всего было → стало |",
             "|---|" + "---|" * (len(hdr) + 1)]
    for name, keys in RES:
        o, n = get(old, keys), get(new, keys)
        cells = ["%.1f → **%.1f**" % (o[i], n[i]) for i in range(4)]
        lines.append("| %s | %s | %.1f → **%.1f** |" % (name, " | ".join(cells), o[5], n[5]))
    print("\n".join(lines))
    print()
    # разброс внутри слоя (по рудам, у которых этот слой входит в диапазон, > 0.5 блока)
    for i, h in enumerate(hdr):
        for tag, d in (("было", old), ("стало", new)):
            vals = sorted((get(d, k)[i], nm) for nm, k in RES if get(d, k)[i] > 0.5)
            if vals:
                print("слой %s %s: руд %d, мин %.1f (%s), макс %.1f (%s), макс/мин %.0f×" % (
                    h, tag, len(vals), vals[0][0], vals[0][1], vals[-1][0], vals[-1][1], vals[-1][0] / vals[0][0]))
    print("обсидиан (YUNG's Law) было/стало:", old["per_chunk"].get("minecraft:obsidian:0"),
          new["per_chunk"].get("minecraft:obsidian:0"))


if __name__ == "__main__":
    main()


# ширина диапазона высот (в блоках): было (все источники вместе) / стало
RANGE = {"Уголь": (128, 128), "Железо": (64, 64), "Золото": (32, 32), "Редстоун": (16, 16), "Алмаз": (16, 16),
         "Лазурит": (32, 32), "Медь": (96, 35), "Олово": (60, 35), "Серебро": (40, 25), "Свинец": (64, 25),
         "Никель": (24, 15), "Уран": (64, 64), "Боксит (алюминий)": (45, 45), "Осмий": (60, 60),
         "Истинный кварц": (60, 60), "Рубин": (8, 8), "Сапфир": (8, 8), "Перидот": (12, 12), "Электротин": (16, 16),
         "Дракониевая": (6, 6), "Гоббер": (10, 10)}


def density():
    old = json.load(open(sys.argv[1], encoding="utf-8"))
    new = json.load(open(sys.argv[2], encoding="utf-8"))
    rows = ["| Руда | Диапазон было → стало | Блоков на 16 высоты: было → стало |", "|---|---|---|"]
    vo, vn = [], []
    for name, keys in RES:
        if name not in RANGE: continue
        wo, wn = RANGE[name]
        o = get(old, keys)[5] / (wo / 16.0)
        n = get(new, keys)[5] / (wn / 16.0)
        vo.append((o, name)); vn.append((n, name))
        rows.append("| %s | %d → %d | %.1f → **%.1f** |" % (name, wo, wn, o, n))
    print("\n".join(rows))
    vo.sort(); vn.sort()
    print("\nбыло: от %.1f (%s) до %.1f (%s), разброс %.0f×" % (vo[0][0], vo[0][1], vo[-1][0], vo[-1][1], vo[-1][0] / vo[0][0]))
    print("стало: от %.1f (%s) до %.1f (%s), разброс %.1f×" % (vn[0][0], vn[0][1], vn[-1][0], vn[-1][1], vn[-1][0] / vn[0][0]))


if "--density" in sys.argv:
    density()
