# Сборка 1.12.2 (оптимизированная)

Самодельная сборка Minecraft **1.12.2** на **Forge 14.23.5.2860** для Prism Launcher. 165 модов: техника (IC2, Mekanism, Thermal, Ender IO, AE2, Draconic), Tinkers, Biomes O' Plenty, Quark, Mowzie's Mobs, Atum и др.

## Что в репозитории

| Путь | Что |
|---|---|
| [`MODS.md`](MODS.md) | полный список модов с SHA-1 и ссылками |
| `minecraft/config/` | все конфиги модов |
| `minecraft/options*.txt` | настройки игры и OptiFine |
| `instance/` | `instance.cfg` (память, JVM-аргументы) и `mmc-pack.json` (версии MC и Forge) для Prism |
| `tools/` | `gen_prompts.py` собирает готовые промпты и «ПОРЯДОК ЗАПУСКА.txt» из `docs/backport-prompts.md`; Python-скрипты: патчи Enchanting Plus и Tinkers' Addons, правки производительности, включение спавна в мирах |
| [`docs/CONTEXT.md`](docs/CONTEXT.md) | **сводка всей проделанной работы и что осталось** |
| [`docs/structure-mods.md`](docs/structure-mods.md) | какие постройки спавнят толпы мобов и как это настроить |
| [`docs/session-log.md`](docs/session-log.md) | полный лог переписки по оптимизации |
| [`docs/backport-prompts.md`](docs/backport-prompts.md) | промпты для агента Claude: слияние бэкпортов в один мод, контент 1.13–1.21, проигравшие на голосованиях мобы и данжи |
| [`docs/dimensions.md`](docs/dimensions.md) | какие измерения добавить, включая порты с новых версий |
| [`docs/manual-checklist.md`](docs/manual-checklist.md) | ручная проверка в игре после каждого этапа агента |

**Jar-файлов модов здесь нет.** Многие моды (например, OptiFine) запрещают перезалив, поэтому качайте их по [`MODS.md`](MODS.md).

## Как собрать инстанс

1. В Prism создайте инстанс Minecraft 1.12.2 + Forge 14.23.5.2860 (или скопируйте `instance/mmc-pack.json`).
2. Скачайте моды из `MODS.md` в `minecraft/mods/`.
3. Скопируйте `minecraft/config/` и `minecraft/options*.txt` поверх.
4. Память 6144/6144 МБ, Java 8, JVM-аргументы из `instance/instance.cfg`.
5. На ноутбуке с двумя видеокартами переключите `javaw.exe` на дискретную: Windows → Дисплей → Графика.
