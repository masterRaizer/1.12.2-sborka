"""Собирает готовые .txt промпты из docs/backport-prompts.md.

Запуск: python tools/gen_prompts.py "F:\\промпты майн 1.12.2"
Каждому промпту добавляется шапка (этап, ветка, папка, порт, диапазон ID) и блок КОНТЕКСТ.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "backport-prompts.md")
MAIN_DIR = r"F:\minecraft-mods\modernbackports"
WT_DIR = r"F:\minecraft-mods\wt"

# Этапы, которые работают прямо в main (строго по одному).
MAIN_STAGES = {"00", "01a", "01b", "09", "M"}

WAVES = [
    ("Шаг 1 (один чат, строго по очереди)", ["00", "01a", "01b"], False),
    ("Волна 1 (параллельно)", ["02a", "03a", "04a", "05a", "07a", "10a"], True),
    ("Волна 2 (параллельно)", ["02b", "03b", "05c", "06", "07b", "10b"], True),
    ("Волна 3 (параллельно)", ["02c", "04b", "05b", "07c", "10c"], True),
    ("Волна 4 (параллельно)", ["05d", "08"], True),
    ("Финал (один чат)", ["09"], False),
]
ALL_PARALLEL = [s for _, st, par in WAVES if par for s in st] + ["01c"]


def header(stage):
    if stage in MAIN_STAGES:
        return (
            f"ЭТАП: {stage}\n"
            f"ВЕТКА: main (worktree НЕ создавать, PR не нужен, коммить и пушь прямо в main)\n"
            f"ПАПКА: {MAIN_DIR}\n"
            f"ПОРТ: 25500\n"
            f"ДИАПАЗОН ID: 0-99 (core)\n"
            f"Этот этап выполняется, когда другие чаты НЕ работают. docs/backport-plan.md обновляешь сам.\n"
        )
    i = ALL_PARALLEL.index(stage)
    port = 25600 + i
    lo = (i + 1) * 100
    extra = ""
    if stage == "08":
        extra = ("Если параллельно портируется несколько измерений, в каждом чате добавь к ЭТАПУ имя:\n"
                 "08-<имя> (ветка stage/08-<имя>, папка wt\\08-<имя>), а порт и диапазон ID увеличь\n"
                 "на 50 для каждого следующего измерения.\n")
    return (
        f"ЭТАП: {stage}\n"
        f"ВЕТКА: stage/{stage}\n"
        f"ПАПКА: {WT_DIR}\\{stage}\n"
        f"ПОРТ: {port}\n"
        f"ДИАПАЗОН ID: {lo}-{lo + 99}\n"
        + extra
    )


def main(out):
    s = open(SRC, encoding="utf-8").read()
    ctx = re.search(r"## Общий блок «Контекст»\n\n```\n(.*?)```", s, re.S).group(1).strip()
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if re.match(r"^(\d\d[a-z]?|M) - .*\.txt$", f):
            os.remove(os.path.join(out, f))
    titles = {}
    for m in re.finditer(r"\n## (\d\d[a-z]?|M) — (.+?)\n\n```\n(.*?)```", s, re.S):
        num, title, body = m.groups()
        titles[num] = title
        body = body.replace("[КОНТЕКСТ]", ctx).strip()
        text = header(num) + "\n" + body + "\n"
        fn = f"{num} - " + re.sub(r'[\\/:*?"<>|]', "", title).strip() + ".txt"
        open(os.path.join(out, fn), "w", encoding="utf-8-sig").write(text)

    lines = ["ПОРЯДОК ЗАПУСКА", "=" * 15, "",
             "Каждый файл = отдельный новый чат с агентом. Копируй файл целиком.",
             "Следующую волну начинай, только когда все чаты волны закончили и прошёл M (слияние).",
             "Одновременно держи 2–3 чата: так меньше шансов упереться в лимит. Остальные этапы волны запускай по мере освобождения.",
             "Перед M и после него пройди «ЧЕК-ЛИСТ ручной проверки.txt» с итоговым jar.", ""]
    for name, stages, par in WAVES:
        lines.append(name + ":")
        for st in stages:
            lines.append(f"   {st} - {titles.get(st, '?')}")
        if par:
            lines.append("   затем: M - Слияние волны (один чат, когда все этапы волны открыли PR)")
        lines.append("")
    lines += ["Необязательно, в любой момент между волнами (как отдельный параллельный чат):",
              f"   01c - {titles.get('01c', '?')} (одна группа фич за раз, затем M)", "",
              "Порт измерений (08): один файл на одно измерение. Заполни в нём <НАЗВАНИЕ>, <МОД> и т. д.", ""]
    open(os.path.join(out, "ПОРЯДОК ЗАПУСКА.txt"), "w", encoding="utf-8-sig").write("\n".join(lines))
    print(len(titles), "prompts written to", out)


if __name__ == "__main__":
    main(sys.argv[1])
