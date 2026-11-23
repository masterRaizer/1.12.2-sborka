# Передача дел: ассистент по сборке 1.12.2

Состояние на 23.11.2026. Этот файл читает каждый новый тред проекта «ассистент по сборке 1.12.2».

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
- Убранные jar: `removed_mods\<номер>_<причина>` (сейчас 1–13, `7_replaced_by_update` для старых версий, `12_futuremc_absorbed` — Future MC, `13_nb_moreblocks_absorbed` — Unseen's Nether, Nether API, MoreBlocks).

## Что сделано (кратко)

- 01b/01c/волна 1 (02a, 03a, 04a, 05a, 07a, 10a) слиты, общий jar `modernbackports-0.0.1.jar` стоит в Prism
  (бэкап `_saves-backup-before-wave1`). На сервере со всей сборкой: загружается, каскада от мода нет, TPS 20.
- Future Versions убран. Дальше поглощение Future MC, Unseen's, MoreBlocks: этапы 11a–11z (11a запущен владельцем).
- **Волна поглощения 11b–11h завершена (этап M, 22–23.11.2026).** PR #7–#13 слиты в main modernbackports,
  `DataFixes.CURRENT=4`, общий jar (SHA-1 60cb5a31) стоит в 1.12.2-edit, бэкап saves `_saves-backup-before-M`,
  отчёт `docs/stages/M2.md` (коммит 07f534a). Сервер: новый мир и копия world_taiga (15 752 блока заменены, реестры
  level.dat до/после совпадают), TPS 20, каскада от мода нет; автотесты 11b-stations и 11c-mobs-plants PASS.
  609 предупреждений «Object did not get ID it asked for» при первом заходе в старый мир — норма (новые объекты).
  Ветки stage/11b–11h и worktree wt\11b–11h удалены.
- **Future MC убран из сборки (этап 11z, PR #14 слит 23.11.2026, коммит 96fd917; установлен этапом M 23.11).**
  Всё, что регистрировал Future MC, переходит на наши версии; `DataFixes.CURRENT=5`, старые числовые ID пишутся в
  `data/modernbackports_removed_mods.dat` мира и переписываются при первой загрузке чанков. Отчёт `docs/stages/11z.md`.
  Jar `modernbackports-0.0.1.jar` SHA-1 `d11b1fe7de5883a7a57255c173652c881fb005d9` (собран из main с `--no-daemon`;
  классы байт в байт как в jar 11z `34b8650e`, отличается только строка `ForceLoadAsMod` в манифесте, как у M2), копия
  `F:\minecraft-mods\_M-11z-jar`. Стоит в 1.12.2-edit и на сервере. В 1.12.2-edit: `Future-MC-0.2.21.jar` и
  `config\futuremc` → `removed_mods\12_futuremc_absorbed`, старый jar → `7_replaced_by_update\modernbackports-0.0.1-before-11z.jar`,
  заменены 4 конфига (apotheosis/enchantments.cfg — наши трезубцевые чары Max Level 50; veinminer/tools-and-blocks.json — без
  `futuremc`; Unseen's blocks_items_config.cfg — `modernbackports:blue_ice`; Unseen's world_config.cfg — «Ancient Debris Spawn
  Chances»=0, иначе Unseen's без Future MC удвоит обломки). Бэкап saves `_saves-backup-before-11z-futuremc`.
  На сервере Future MC и старый jar в `mods_client_only` (`modernbackports-0.0.1-before-11z.jar`), `config\futuremc` в
  `_server-1.12.2\removed_11z\config`. Проверка: копия world_taiga — Forge ничего не спросил («missing»/«Unidentified» 0),
  321 чанк переписан, 1277 новых чанков, TPS 20, каскада от мода нет (MrTJPCore 121, Quark 50, Dynamic Trees 24, LLibrary 6,
  Mowzie's Mobs 1 — чужие);
  автотесты в клоне `1.12.2-test-M`: 11z-before → 11z-after (бочка с алмазами и сотами цела, блоки и мобы на месте), 11b, 11c PASS.
  11c повторён после установки с `--refresh` из 1.12.2-edit (в сценарии 11c исправлен порядок: сначала ждать чанки, потом
  ставить улей и цветы, иначе setblock попадал в незагруженные чанки). Скриншоты `F:\minecraft-mods\_M-11z-screens`.
  **Для треда квестов:** `ftbquests/normal/chapters/*.snbt` и достижения/`quests/hitech.json` в packquests ссылаются на
  `futuremc:*` — перегенерировать с `modernbackports:*` (те же имена, кроме `banner_pattern` → `flower_banner_pattern`,
  `soul_fire_torch` → `soul_torch`, `soul_fire_lantern` → `soul_lantern`), snbt руками не править.
  **Для Shattered Citadels:** палитры/мебель/лут берут `futuremc:*` с запасным вариантом — добавить имена `modernbackports:*` первыми.
  Не переносятся из Future MC: «New Villager Gui» (окно торговли 1.14) и «Game Mode Switcher» (F3+F4) — кандидаты на этап интерфейса.
  Unseen's Nether и MoreBlocks убраны этапом 11z-nb (ниже).
- **Unseen's Nether, Nether API и MoreBlocks убраны (11z-nb, PR #16) и стоит 05c (PR #19); этап M 23.11.2026.**
  Оба PR слиты в main modernbackports (f5ce670, b24ebdf), отметка в backport-plan 2a93bf6. `DataFixes.CURRENT=7`
  (`nb`/`nether_api` — 6, `moreblocks` — 7; MoreBlocks нельзя убрать раньше Unseen's — `RemovedMods.checkOrder`).
  Jar `modernbackports-0.0.1.jar` SHA-1 `2893e2076a37776c6ac0a24bec2773f4eae4ceee` (main b24ebdf, `--no-daemon`, javap: SRG-имена),
  копия `F:\minecraft-mods\_M-11znb-jar`. verify.py `--fresh-world`: 0 ошибок, 0 предупреждений, 343 блока, 382 предмета, 32 сущности.
  В 1.12.2-edit: три jar и `config/Unseens Nether Backport`, `config/nether_api` → `removed_mods\13_nb_moreblocks_absorbed`
  (там же старые версии двух заменённых конфигов), старый jar → `7_replaced_by_update\modernbackports-0.0.1-before-11z-nb.jar`;
  заменены `apotheosis/enchantments.cfg` (Скорость души `modernbackports:soul_speed` Max Level 50, как было у `nb:soul_speed`)
  и `veinminer/tools-and-blocks.json` (без 13 строк `nb:`/`moreblocks:`). Бэкап saves `_saves-backup-before-11z-nb`.
  Общий сервер: три мода и старый jar в `mods_client_only` (`modernbackports-0.0.1-before-11z-nb.jar`), их конфиги в
  `_server-1.12.2\removed_11znb\config`, `world_taiga` перепишется при первом запуске.
  Проверка на копии сервера `F:\minecraft-mods\_server-M-11znb` (лог `console_taiga.log`, `console_new.log`): копия world_taiga —
  Forge ничего не спросил, 376 чанков переписаны (15 340 блоков), исключений от мода нет, TPS 20; новый мир — 1222 чанка
  Верхнего мира и 1352 Незера, TPS 20, каскада от modernbackports нет (MrTJPCore 67, Dynamic Trees 39, Quark 15, LLibrary 2,
  Apotheosis 2 — чужие); в мире 0 блоков `nb`/`moreblocks`, Незер наш (бастионы, 4 биома), бледный сад вырос (450 бревен,
  2 сердца). Руин порталов в области не попалось.
  Автотесты (клоны `1.12.2-test-M`, `1.12.2-test-M-chest`): 11znb-before → after/look/blocks/mech, 05c, 11b-stations,
  11c-mobs-plants — PASS; сундук с 8 вещами `nb:`/`moreblocks:` после удаления открылся, все вещи на месте (в сценарии
  11znb-before команда сундука разбита на `/replaceitem`, была длиннее 256 символов). Скриншоты `F:\minecraft-mods\_M-11znb-screens`.
  **Для треда квестов:** `nb:*`/`moreblocks:*` в квестах и достижениях заменить по `modernbackports/docs/stages/11z-nb-remap-list.md`
  (и `.csv`); `nb:soul_campfire` — несуществующий предмет. **Для Shattered Citadels:** то же для палитр.
  Поглощение закончено: разблокированы 06, 02c, 03b (02b/02c/03b расширяют блоки `stages.s11z.mb`, а не регистрируют заново).
  05c: броненосец, броня волка, скрипун, бледный дуб/мох/глазоцвет/смола, бледные сады в тёмных лесах; внешний вид сада в мире,
  анимации и звуки проверяет владелец (список в `docs/stages/05c.md`).
- 11c (пчёлы, ульи, мёд, ягоды, бамбук, панда, василёк/ландыш/роза визера, рагу): черновой PR
  https://github.com/masterRaizer/modernbackports/pull/7 (ветка `stage/11c`), слит этапом M 23.11. Тест переноса миров 14/14,
  генерация без каскада (в т. ч. с Future MC и Dynamic Trees), отчёт `docs/stages/11c.md` со списком «проверить в игре».
  Нашёл и исправил крэш в общем коде 11a (`LiveRemap.hideFromTabs`: Future MC на Kotlin падал на `setCreativeTab(null)`) —
  тот же патч нужен 11b/11d/11e (в 11f уже есть). (Устарело: Future MC уже убран.) Для 11z в `futuremc.cfg` выключить: «Spawn Rate»=0 у cornflower,
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

- **Графика как на MCSkill HiTech** (22.11.2026). У HiTech меню Celeritas (Cleanroom 0.5.15 + Java 25), к нам не
  переносится. Владелец выбрал «без Cleanroom»: OptiFine и JEI остаются. В 1.12.2-edit поставлены ScalingGUIs 1.0.3.0,
  NeverEnoughAnimations 1.0.6, LegendaryTooltips 1.1.11 (официальная, Modrinth), все только клиент (на сервере в
  `mods_client_only`). Настройки HiTech перенесены в `options.txt`/`optionsof.txt`, кроме дальности (12) и масштаба (4),
  копии `*.bak-graphics`. Бэкап `_saves-backup-before-graphics`. Автотест `packautotest/scenarios/graphics.json` PASS,
  FPS не просел. NEA не встраивается в наш MouseTweaks 2.10 (только предупреждение). Отчёт и таблица настроек:
  `F:\minecraft-mods\_ref\graphics-menu\report.md`. В packautotest добавлены шаги `hover`/`hoverSlot` и `gui: "modConfig:<modid>"`.

- **Генерация руд, верхний мир** (22–23.11.2026, владелец согласен оставить): у каждой руды один источник
  (медь — Thermal и медь 1.17 modernbackports, возвращена по просьбе владельца 23.11; олово/серебро/свинец/никель — Thermal, уран — IC2,
  алюминий — боксит IE, осмий — Mekanism, кварц — AE2), ≈1 жила на 16 блоков высоты, жилы на ~20 настоящих блоков больше.
  Ваниль и руды без настроек (апатит, рубин, сапфир, перидот, электротин, дракониевая) — в `config/cofh/world/05_pack_*.json`,
  Gobber генерирует сам (worldgenGobber=false, размер 10, шанс 6; `true` удаляет предмет gb:gobber_ore из миров, фикс 23.11),
  ванильная генерация в dim 0 запрещена через `adlods/VanillaGen` (ReplaceStandardGeneration=false, Ад не тронут).
  Разброс руд по частоте 163× → 4×, TPS 20, нового каскада нет. Стоит в 1.12.2-edit и на сервере; слито в main
  (PR #1, 23.11). Отчёт, скрипты (patch_ores.py, count_ores.py — подсчёт руд по .mca), откат `F:\minecraft-mods\_ref\ores\rollback.bat`:
  `F:\minecraft-mods\_ref\ores` и `tools/ores`. Бэкап saves `_saves-backup-before-ores`. Не тронуты TAIGA, самоцветы BoP, adlods.
  Изумруд и мезовое золото не измерены (в тестовой области не было гор/мезы). YUNG's Law превращает камень вдали от пещер в обсидиан.

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
   `world_bop_large`. **Владелец выбрал Huge (22.11):** `config/biomesoplenty/world.json` = continents + huge (сборка, сервер,
   репозиторий), `misc.cfg` «Default to BoP World Type»=true. world.json задаёт значения для новых BoP-миров без своих
   настроек (их generatorOptions пустые, поэтому world.json не удалять). Старые BoP-миры не меняются: настройки в них явные.
   Проверено: сервер (карта байт в байт = Huge), клиент автотестом в `1.12.2-test-bop` (4/4 точки, 96% чанков). RTG не нужен.
   Важно для 11f/11z: в мире типа BIOMESOP Незер генерирует BoP (5 его биомов + ад, 655 настоящих чанков у 0,0),
   биомов Unseen's там нет, в отличие от мира DEFAULT.
   Инструмент карт: `F:\minecraft-mods\_tools\biomemap` (jar с командой `/biomemap` кладётся в mods сервера только на прогон,
   `render.py`, `region_map.py`, `region_biomes.py`).
6. UniDict: модуль EnderIO падает с NoSuchMethodError (рецепты UniDict для EnderIO не работают).
7. **Tinkers' Backports, фазы 2–4** (см. `F:\minecraft-mods\tinkersbackports\docs\gap-list.md`): 2 инструменты
   (кинжал, дротик, vein hammer, war pick, боевой топор и катласс из 1.7.10: их текстуры уже лежат в jar Tinkers 1.12),
   сердца 1.7.10, слизистая броня с элитрами; 3 плавильные блоки (сначала поставить Tinkers' Complement 0.4.3,
   скачивание спрошено у владельца 22.11); 4 деревья, острова и мобы из слизи. Tinkers' Antique 2.13.0.209
   (форк, заменяет TConstruct.jar) только после теста со всеми аддонами и согласия владельца.
