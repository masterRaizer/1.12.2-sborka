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
- Очередь: перед правкой `mods`/`server.properties` создать `_server-1.12.2\LOCK.txt` (тред и время); если файл есть, ждать.
  После прогона вернуть `level-name=world_taiga` и удалить LOCK.txt.

## Prism

- Рабочий инстанс `%APPDATA%\PrismLauncher\instances\1.12.2-edit`. Оригинальный `1.12.2(1)` не трогать.
- Перед заменой jar: игра закрыта (`tasklist | grep javaw`), бэкап `saves` в `F:\minecraft-mods\_saves-backup-before-<что>`.
- Убранные jar: `removed_mods\<номер>_<причина>` (сейчас 1–10, `7_replaced_by_update` для старых версий).

## Что сделано (кратко)

- 01b/01c/волна 1 (02a, 03a, 04a, 05a, 07a, 10a) слиты, общий jar `modernbackports-0.0.1.jar` стоит в Prism
  (бэкап `_saves-backup-before-wave1`). На сервере со всей сборкой: загружается, каскада от мода нет, TPS 20.
- Future Versions убран. Дальше поглощение Future MC, Unseen's, MoreBlocks: этапы 11a–11z (11a запущен владельцем).
- 11c (пчёлы, ульи, мёд, ягоды, бамбук, панда, василёк/ландыш/роза визера, рагу): черновой PR
  https://github.com/masterRaizer/modernbackports/pull/7 (ветка `stage/11c`), ждёт слияния этапом M. Тест переноса миров 14/14,
  генерация без каскада (в т. ч. с Future MC и Dynamic Trees), отчёт `docs/stages/11c.md` со списком «проверить в игре».
  Нашёл и исправил крэш в общем коде 11a (`LiveRemap.hideFromTabs`: Future MC на Kotlin падал на `setCreativeTab(null)`) —
  тот же патч нужен 11b/11d/11e (в 11f уже есть). Для 11z в `futuremc.cfg` выключить: «Spawn Rate»=0 у cornflower,
  lily of the valley, berry bush и пустой «Bee Nest Biome Spawns» (бамбук Future MC глушит код 11c, опции у него нет).
- BuildCraft: `useSwappableSprites=false` (невидимые трубы с OptiFine).
- TAIGA: пропатчен `tools/taiga_patch` (каскад 373 → 0), оригинал в `removed_mods/10_original_taiga`.
- Shattered Citadels 1.6.2 стоит в Prism (сборки: https://github.com/masterRaizer/Mods-Forge-1.12.2-, ветка
  `claude/brave-franklin-ttdlk9`, папка `dist/`). На сервере: все постройки, старый мир 1.6.0/1.6.1 открывается.

- **Tinkers' Backports** (свой мод, отдельный jar, 22.11.2026): перенос всего из Tinkers 1.7.10 и 3.x (3.12.1 для
  1.20.1, последняя). Код `F:\minecraft-mods\tinkersbackports` (локальный git, на GitHub ещё нет), сверка
  `docs/gap-list.md`, фаза 1 `docs/phase1-design.md`. Фаза 1 стоит в Prism и на тестовом сервере: 8 сплавов 3.x
  (rose gold, slimesteel, amethyst bronze, hepatizon, queen's slime, cinderslime, pewter, nicrosil), 5 неметаллов
  (кости, хорус, seared stone), 18 модификаторов, жидкости кварц/магма/ихор. Сервер: всё загружено, TPS 20,
  самотест `tinkersbackports selftest` (через drive.py) 65/65.
  Клиент: грузится без ошибок текстур (по логу), визуально не смотрели (доступ к экрану не дан).
  Бэкап saves: `_saves-backup-before-tinkersbackports`. Справочник TC3 (данные, текстуры MIT): `F:\minecraft-mods\_ref\tc3`.

## Открытые задачи

0. **Проверка в игре самим ассистентом (сделать первой).** Владелец хочет, чтобы ассистент сам всё проверял в клиенте
   на его ноутбуке, без ручных проверок. Сделать в PackQuests клиентский автотест:
   - если в `1.12.2-edit/minecraft` есть `packquests-autotest.json`, клиент заходит в мир `autotest` (создаёт его,
     если нет: творческий, читы, тип мира в сценарии), выполняет шаги (команды в чат, `/tp` с углами камеры, ожидание,
     открыть инвентарь, книгу квестов, JEI, произвольный GUI), делает скриншоты в `screenshots/autotest/<время>/`,
     пишет `autotest-report.txt` (шаги, ошибки из лога, FPS) и выходит из игры; файл сценария переименовывается;
   - запуск: `"%LOCALAPPDATA%\Programs\PrismLauncher\prismlauncher.exe" --launch 1.12.2-edit --world autotest`
     (Prism поддерживает `--world` и `--offline`), ждать выхода javaw, смотреть скриншоты через Read;
   - реальные миры не трогать; перед запуском проверить, что владелец не играет;
   - первые сценарии: волна 1 (мобы, шрифт, медь, аметист), трубы ProjectRed с OptiFine (с переключением
     `ofFastRender` в `optionsof.txt` между прогонами), Shattered Citadels (`/citadel spawn tower`, интерьер), кнопка «Квесты».
   - Запасной путь: computer use в приложении Claude (Настройки → Система → Computer use).
1. **Квесты (главная).** Большая линейка в стиле серверов McSkill HiTech: древо от старта до эндгейма по большим модам
   (IC2, Advanced Solar Panels, GraviSuite, Thermal, Mekanism, Ender IO, Immersive Engineering, AE2, Draconic, Tinkers,
   Forestry, BuildCraft и др.), отдельная кнопка.
   - Мод `F:\minecraft-mods\packquests` (git, шаблон как у modernbackports, сборка
     `JAVA_HOME=%USERPROFILE%\.gradle\jdks\eclipse_adoptium-25-amd64-windows.2 ./gradlew build`):
     кнопка «Квесты» слева от инвентаря (выживание и творческий) и в меню паузы, открывает BetterQuesting через
     рефлексию; команда `/packquests dump` (в фоне, с таймаутами на предмет) пишет `packquests-dump/items.tsv`,
     `entities.tsv`, `fluids.tsv`, `ores.tsv` в папку сервера. Дамп сделан 22.11 12:35 в `F:\minecraft-mods\_server-1.12.2\packquests-dump`:
     34623 стака предметов, 280 сущностей, 236 жидкостей, 1324 имени словаря руд. Мод PackQuests лежит в mods
     тестового сервера, в Prism ещё НЕ поставлен.
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
5. **Крупные биомы**: 22.11 сделаны карты биомов (генератор на тестовом сервере, 16×16 тыс. блоков, один сид):
   BoP по умолчанию ~300×300 блоков на биом, Large+Continents ~600×600 (океан 41%), Huge+Continents ~1100×1100.
   Тестовый мир `saves/BoP Large Continents test` в Prism (творческий, читы, сид 8040611399178049913), на сервере
   `world_bop_large`. Ждём решения владельца (Large или Huge); RTG только если мало.
   Важно для 11f/11z: в мире типа BIOMESOP Незер генерирует BoP (5 его биомов + ад, 655 настоящих чанков у 0,0),
   биомов Unseen's там нет, в отличие от мира DEFAULT.
   Инструмент карт: `F:\minecraft-mods\_toolsiomemap` (jar с командой `/biomemap` кладётся в mods сервера только на прогон,
   `render.py`, `region_map.py`, `region_biomes.py`).
6. UniDict: модуль EnderIO падает с NoSuchMethodError (рецепты UniDict для EnderIO не работают).
7. **Tinkers' Backports, фазы 2–4** (см. `F:\minecraft-mods\tinkersbackports\docs\gap-list.md`): 2 инструменты
   (кинжал, дротик, vein hammer, war pick, боевой топор и катласс из 1.7.10: их текстуры уже лежат в jar Tinkers 1.12),
   сердца 1.7.10, слизистая броня с элитрами; 3 плавильные блоки (сначала поставить Tinkers' Complement 0.4.3,
   скачивание спрошено у владельца 22.11); 4 деревья, острова и мобы из слизи. Tinkers' Antique 2.13.0.209
   (форк, заменяет TConstruct.jar) только после теста со всеми аддонами и согласия владельца.
