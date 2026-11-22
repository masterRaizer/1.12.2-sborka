# Передача дел: ассистент по сборке 1.12.2

Состояние на 22.11.2026. Этот файл читает каждый новый тред проекта «ассистент по сборке 1.12.2».

## Роль ассистента

Сам контент мода `modernbackports` пишут агенты проекта «Modern Backports мод» по промптам из `F:\промпты майн 1.12.2`.
Ассистент:
- проверяет их отчёты по файлам и git (не верит на слово);
- тестирует jar на тестовом сервере со всей сборкой;
- ставит готовые jar в Prism (с бэкапом `saves`);
- чинит лаги и ошибки сборки (конфиги, патчи jar);
- тестирует сторонний мод Shattered Citadels;
- делает квестовую линию (мод PackQuests + DefaultQuests.json BetterQuesting).

## Тестовый сервер со всей сборкой

`F:\minecraft-mods\_server-1.12.2`: Forge 14.23.5.2860, все моды из `1.12.2-edit\minecraft\mods` и `mods\1.12.2`, конфиги сборки.
- Убраны клиентские моды (лежат в `mods_client_only`): OptiFine, ShoulderSurfing, MoBends, CleanView, MouseTweaks,
  Durability101, ShulkerTooltip, BetterAdvancements, TravelersTitles. Там же старые версии заменённых jar.
- Запуск только через `drive.py` (stdin-команды после `Done`, `#sleep N` = пауза, в конце `stop`, лог в `console.log`):
  `python -I drive.py --start-timeout 300 --wait 5 "forge tps" "forge gen 0 64 0 1500" "#sleep 400" "forge tps"`
- Старт ~100–120 с. Мир задаётся `level-name` в `server.properties` (есть `world`, `world_m1`, `world_taiga`).
- Без игрока чанки у спавна не держатся: `/summon` пишет «out of the world». Мобов проверяет владелец в игре.
- Долгие прогоны запускать в фоне. Каскадную генерацию считать так:
  `grep -o "\[FML\]: .* loaded a new chunk" console.log | sed 's/\[FML\]: //; s/ loaded a new chunk//' | sort | uniq -c`
- `max-tick-time=-1` (watchdog выключен).

## Prism

- Рабочий инстанс `%APPDATA%\PrismLauncher\instances\1.12.2-edit`. Оригинальный `1.12.2(1)` не трогать.
- Перед заменой jar: игра закрыта (`tasklist | grep javaw`), бэкап `saves` в `F:\minecraft-mods\_saves-backup-before-<что>`.
- Убранные jar: `removed_mods\<номер>_<причина>` (сейчас 1–10, `7_replaced_by_update` для старых версий).

## Что сделано (кратко)

- 01b/01c/волна 1 (02a, 03a, 04a, 05a, 07a, 10a) слиты, общий jar `modernbackports-0.0.1.jar` стоит в Prism
  (бэкап `_saves-backup-before-wave1`). На сервере со всей сборкой: загружается, каскада от мода нет, TPS 20.
- Future Versions убран. Дальше поглощение Future MC, Unseen's, MoreBlocks: этапы 11a–11z (11a запущен владельцем).
- BuildCraft: `useSwappableSprites=false` (невидимые трубы с OptiFine).
- TAIGA: пропатчен `tools/taiga_patch` (каскад 373 → 0), оригинал в `removed_mods/10_original_taiga`.
- Shattered Citadels 1.6.2 стоит в Prism (сборки: https://github.com/masterRaizer/Mods-Forge-1.12.2-, ветка
  `claude/brave-franklin-ttdlk9`, папка `dist/`). На сервере: все постройки, старый мир 1.6.0/1.6.1 открывается.

## Открытые задачи

1. **Квесты (главная).** Большая линейка в стиле серверов McSkill HiTech: древо от старта до эндгейма по большим модам
   (IC2, Advanced Solar Panels, GraviSuite, Thermal, Mekanism, Ender IO, Immersive Engineering, AE2, Draconic, Tinkers,
   Forestry, BuildCraft и др.), отдельная кнопка.
   - Мод `F:\minecraft-mods\packquests` (git, шаблон как у modernbackports, сборка
     `JAVA_HOME=%USERPROFILE%\.gradle\jdks\eclipse_adoptium-25-amd64-windows.2 ./gradlew build`):
     кнопка «Квесты» слева от инвентаря (выживание и творческий) и в меню паузы, открывает BetterQuesting через
     рефлексию; команда `/packquests dump` (в фоне, с таймаутами на предмет) пишет `packquests-dump/items.tsv`,
     `entities.tsv`, `fluids.tsv`, `ores.tsv` в папку сервера. Последняя сборка с исправлением (`getTabLabel` был
     только клиентский) лежит в `build\libs`; проверить, что дамп записался.
   - BetterQuesting 3.5.312: квесты по умолчанию в `config/betterquesting/DefaultQuests.json` (формат как в
     `config/betterquesting/citadels_questline.json`, ключи с типами `name:8`). Новый мир берёт их сам, в старом
     `/bq_admin default load`. Линию Shattered Citadels (`citadels_questline.json`) включить отдельной главой со
     сдвигом ID.
   - План: генератор на Python (главы → квесты → зависимости → раскладка дерева), проверка каждого предмета
     по `items.tsv`, тест загрузки на сервере, ручная проверка владельцем.
2. **Трубы ProjectRed** в мире рисуются плоскими столбами: владелец должен попробовать выключить в OptiFine
   «Быстрый рендер», потом «Регионы рендера», анизотропную фильтрацию, MIP-текстуры.
3. **Каскадная генерация** (1137 чанков): MrTJPCore (руды ProjectRed) 84, Quark 33, Dynamic Trees 24.
4. **Shattered Citadels**: владелец проверяет в игре (`/citadel spawn tower|manor`, бой с магом, печати, библиотека).
   Вопрос агенту: летающая небесная цитадель (сейчас это башня с земли).
5. **Крупные биомы**: владелец пробует настройки типа мира BoP (Biome Size Large, Land Scheme Continents);
   если мало, RTG в отдельной копии сборки (проверить с Dynamic Trees).
6. UniDict: модуль EnderIO падает с NoSuchMethodError (рецепты UniDict для EnderIO не работают).
