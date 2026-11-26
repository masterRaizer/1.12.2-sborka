# Передача дел: ассистент по сборке 1.12.2

Состояние на 26.11.2026 (после волны 9: 08-abyss, 08-outerend, 13-atm и этап 12 стоят в сборке; дальше M10 — 13-atm-2, 12-gaps-2). Этот файл читает каждый новый тред проекта «ассистент по сборке 1.12.2».

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
  Durability101, ShulkerTooltip, BetterAdvancements, TravelersTitles, Controlling (с 25.11). Там же старые версии заменённых jar.
- Запуск только через `drive.py` (stdin-команды после `Done`, `#sleep N` = пауза, в конце `stop`, лог в `console.log`):
  `python -I drive.py --start-timeout 300 --wait 5 "forge tps" "forge gen 0 64 0 1500" "#sleep 400" "forge tps"`
- Старт ~100–120 с. Мир задаётся `level-name` в `server.properties` (есть `world`, `world_m1`, `world_taiga`).
- Без игрока чанки у спавна не держатся: `/summon` пишет «out of the world». Мобов проверяет владелец в игре.
- Долгие прогоны запускать в фоне. Каскадную генерацию считать так:
  `grep -o "\[FML\]: .* loaded a new chunk" console.log | sed 's/\[FML\]: //; s/ loaded a new chunk//' | sort | uniq -c`
- `max-tick-time=-1` (watchdog выключен).
- В `drive.py` JVM-аргумент `-Dfml.readTimeout=120` (с 26.11, этап M волна 5): FTB Quests при входе грузит ~4000 файлов дольше 30 с.
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
  Проверка на копии сервера `_server-M-11znb` (после проверки удалена; логи сервера, автотестов и перепись мира — в
  `F:\minecraft-mods\_M-11znb-jar\logs`): копия world_taiga —
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
- **Волна 3: 07b, 10b, 02b, 02c слиты и стоят (этап M, 23.11.2026).** PR #15 (07b мобы голосований 2021–2023: глэр,
  проныра, туфовый голем, краб на пляжах + клешня, пингвин), #17 (10b экраны: создание мира с вкладками, вкладки творческого,
  «Специальные возможности», чат, размытие меню, экран загрузки 1.16, торговля 1.14, F3+F4), #18 (02b: слой сланца Y 0–8,
  сланцевые руды, светящийся спрут, рамка, таблички, аксолотль, коза, мешок), #20 (02c: капельник, туф, пышные и капельниковые
  пещеры) слиты в main modernbackports; отметка в backport-plan 40b6a7e. Пересечение этапов только `MbEarlyMixins.CONFIGS`
  (строки 10b и 02b, обе на месте); `DataFixes.CURRENT=7` не менялся. Jar SHA-1 `518643e6a433a4127db9d026bfeb62764b3cb50a`
  (main d3d8f58, `--no-daemon`, javap: SRG-имена), копия и логи `F:\minecraft-mods\_M-w3-jar`. verify.py `--fresh-world`:
  0 ошибок, 0 предупреждений, 363 блока, 421 предмет, 41 сущность.
  В 1.12.2-edit: старый jar → `7_replaced_by_update\modernbackports-0.0.1-before-M-w3.jar`, конфиги не менялись (07b/10b/02b/02c.cfg
  создаются сами; оба краба — решение владельца, `crab.hideQuarkCrabSpawns=false` по умолчанию). Бэкап saves
  `_saves-backup-before-M-w3`. Общий сервер: новый jar в mods, старый `mods_client_only\modernbackports-0.0.1-before-M-w3.jar`.
  Проверено на сервере (копия `_server-M-w3`, удалена): копия world_taiga — Forge ничего не спросил, исключений от мода нет,
  TPS 20; новый мир (сид 2026112303) — 1712 новых чанков Верхнего мира и 1446 Незера, TPS 20, каскада от modernbackports нет
  (MrTJPCore 15, Dynamic Trees 9, Quark 6, LLibrary 3); в мире сланец 1,26 млн блоков, туф, капельник, мох, лозы, спороцвет;
  из мобов волны сам появился только краб (3 шт.) — без перебора.
  Проверено в игре (клоны `1.12.2-test-M` и `1.12.2-test-M-chest`, OptiFine G5, «Быстрый рендер» вкл.; скриншоты
  `F:\minecraft-mods\_M-w3-screens`): 10b — меню паузы и настройки размыты, вкладки создания мира, F3+F4 (окно открыто через
  `-Dmodernbackports.10b.fakeF3`, в клоне потом убрано), торговля 1.14 (выбор сделки перекладывает оплату); 07b — все 5 мобов;
  02b-fauna — руды, рамки, аксолотли, спруты, козы, мешок; 02b-mech — коза сбила стойку; 02c — пышная и капельниковая пещеры
  целиком (исправленный `/mb02c tp`), котлы, костная мука; регресс 11b-stations и 11c-mobs-plants PASS. Ошибок мода в логах нет.
  Сбои сценариев, не мода: 10b-screens (часть торговли: `/summon` длиннее 256 символов), 10b-trade и 10b-blur требуют
  функцию жителя — перед прогоном скопировать `packautotest\scenarios\fixtures\mb10b\villager.mcfunction` в
  `saves\autotest\data\functions\mb10b\`; 02c — 2 тайм-аута `waitChunks` под нагрузкой.
  Не удалось проверить: настоящее нажатие F3+F4, экран загрузки 1.16, размытие с шейдерами; отлом рога козы (в этом прогоне не
  попал в кадр); наклон бросянки (свинья в сценарии висит, NoAI); голем из настоящего туфа (код берёт `modernbackports:tuff`
  при постройке — должно работать); естественный спавн глэра, проныры, пингвина, козы, спрута, аксолотля (нужен игрок рядом).
  Ветки stage/07b, 10b, 02b, 02c и worktree wt\07b, 10b, 02b удалены. Оставлены: `wt\02c` (ветка stage/02c-axolotl — спавн
  аксолотля в пышных пещерах, отдельный PR 02c, работа идёт) и `wt\02b-test` (test/02b-11znb).
- **Волна 4: 03b, 02c-axolotl, 05b, 04b, 10c, 07c слиты и стоят (этап M, 25.11.2026).** PR #22 (03b Глубокая тьма:
  вибрации, скалк-сенсоры, катализатор, крикун, хранитель и Тьма, древние города под горами), #24 (02c-axolotl: спавн
  аксолотля как в 1.18), #21 (05b крафтер, медь 1.21, варианты туфа), #25 (04b отделка брони, вишня, бамбук, подвесные
  таблички, резная полка), #26 (10c управление, спец. возможности, 14 правил игры, невидимые рамки), #27 (07c данжи
  проигравших мобов и биомов) слиты в main modernbackports; отметка в backport-plan 6f6deca. Чужие файлы (описаны в
  отчётах, конфликтов нет): 03b — `MbBlocks.sculkBlocks()` и `tools/s11z_mb_resources.py`; 04b — `compileOnly` JEI в
  `dependencies.gradle`; 10c — строка в `MbEarlyMixins.CONFIGS` и `SplashStyle`/`MixinSplashThread` 10b (чёрно-белый логотип).
  `DataFixes.CURRENT=7` не менялся. Jar SHA-1 `4c7fa31f40a9caa387a714c8e49f79ce9750505c` (main a9582bd, `--no-daemon`,
  javap: SRG-имена, JEI не упакован), копия, логи, перепись мира и листы скриншотов — `F:\minecraft-mods\_M-w4-jar`
  (первый прогон на f0407df без 10c/07c — в `old-f0407df`). verify.py `--fresh-world`: 0 ошибок, 0 предупреждений,
  485 блоков, 549 предметов, 46 сущностей.
  В 1.12.2-edit: старый jar → `7_replaced_by_update\modernbackports-0.0.1-before-M-w4.jar`, **поставлен мод Controlling
  3.0.12.2** (клиент, экран «Управление» 10c, SHA-1 `64e791db…`), конфиги не менялись (03b/04b/05b/07c/10c.cfg создаются
  сами; 07c.cfg по умолчанию: `rascal_cache.caveFallback=true`, `ice_fortress.minY=70` — ждут ответа владельца).
  Бэкап saves `_saves-backup-before-M-w4`. Общий сервер: новый jar в mods, старый
  `mods_client_only\modernbackports-0.0.1-before-M-w4.jar`, Controlling тоже в `mods_client_only`.
  Проверено на сервере (копия `_server-M-w4`, удалена): копия world_taiga — Forge ничего не спросил, исключений мода нет,
  TPS 20; новый мир (сид 2026112304) — 2283 чанка Верхнего мира и 1653 Незера, TPS 20, каскада от modernbackports нет
  (MrTJPCore 35, Quark 26, LLibrary 6, Dynamic Trees 4); древний город сам построился под горами (504 36 -328, 84 части,
  73 сундука, 354 сенсора, 53 крикуна, 94 катализатора), самотест 07c 9/9, сами появились 6 тайников проныры, 2 логова
  Чудища, 4 гнезда Инферно; хранителей и аксолотлей в мире 0 (без игрока не спавнятся), вишнёвых рощ в области не было.
  Проверено в игре (клоны `1.12.2-test-M`, `-M-chest`, `-M2`, `-M3`, OptiFine G5; листы `_M-w4-jar\sheets`, лучшие
  снимки `F:\minecraft-mods\_M-w4-screens`): 03b-mech и 03b-darkness — блоки скалка, сенсор зажёг лампу, хранитель со
  свечением, Тьма затемняет экран с OptiFine; 04b — отделка на броне спереди и сзади, значки, подсказка, вишня с
  падающими лепестками, плоты, подвесная табличка с надписью «Ура»; 05b — туф, решётки, лампы ночью, двери, крафтер и его
  экран; 02c — пещеры, бросянки, за минуту 7 аксолотлей в пышных пещерах; 07c — все 9 построек, волны и сундук награды;
  10c, 10c-b, 10c-rules — экран «Специальные возможности», блеск, укачивание, невидимая рамка, зарницы, экран Controlling,
  правила на экране создания мира; регресс 11b-stations, 11c-mobs-plants, 02b-fauna — PASS. 03b-deepdark (обычный мир BoP) — PASS со второго повтора: древний город построен в игре (-632 36 872; 51 сундук, 343 сенсора, 41 крикун, 75 катализаторов), на снимках из режима наблюдателя видны кирпичи и плитка сланца, скалк, сенсоры, вода и лава вокруг; первые два прогона снимали город раньше, чем сервер игры достроил его, третий отключился по тайм-ауту при первой генерации мира.
  Ошибок нашего мода в логах клиентов нет (только известное `netherite_layer_*.png`).
  После установки 10c-b повторён на содержимом самого 1.12.2-edit (`--refresh` без `--jar`, jar `4c7fa31f` и Controlling): PASS,
  экран «Управление» — Controlling (поиск, конфликты).
  Сбои не мода: при 3 клиентах одновременно память кончилась (каждый клиент растёт до 7–9 ГБ), встроенный сервер
  отстал и клиенты 11b/11c отключились по тайм-ауту — перезапущены по два, PASS. В сценарий
  `packautotest/scenarios/03b-deepdark.json` добавлены паузы после `/ancientcity generate` и `tp` (копия в
  `modernbackports/tools/autotest` старая).
  **Вопрос владельцу:** мод Champions делает мобов волн 07c «чемпионами» (на снимке босса гробницы полоса
  «Bingpot the Destroyer / Arctic» вместо «Фараон»; награда выпала). Исключить мобов `mb07c_*` из Champions или оставить?
  Открыто после M: 10c предлагает правило `doWardenSpawning` (в коде призыва 03b) и субтитры `entity.strider.saddle` (11g),
  `entity.frog.tongue` (03a); 07c — ответ владельца по `caveFallback`/`minY`; рядом с древним городом (467 29 -317) сам
  появился тайник проныры — проверить в игре, не врезается ли он в город.
  Не удалось проверить: вишнёвые рощи в настоящем мире, естественный спавн хранителя и аксолотлей рядом с игроком,
  бой с хранителем в игре, Гнездо Инферно в игре, чёрно-белый логотип загрузки, поиск в Controlling вводом текста,
  сон с процентом в мультиплеере, отделка и Тьма с шейдерами.
  Ветки stage/03b, 05b, 04b, 02c-axolotl, 10c, 07c и worktree wt\03b, 04b, 05b, 02c, 10c, 07c удалены. Остались
  `wt\06` (stage/06), `wt\05d`, `wt\10d` (новые этапы) и `wt\02b-test`.
- 11c (пчёлы, ульи, мёд, ягоды, бамбук, панда, василёк/ландыш/роза визера, рагу): черновой PR
  https://github.com/masterRaizer/modernbackports/pull/7 (ветка `stage/11c`), слит этапом M 23.11. Тест переноса миров 14/14,
  генерация без каскада (в т. ч. с Future MC и Dynamic Trees), отчёт `docs/stages/11c.md` со списком «проверить в игре».
  Нашёл и исправил крэш в общем коде 11a (`LiveRemap.hideFromTabs`: Future MC на Kotlin падал на `setCreativeTab(null)`) —
  тот же патч нужен 11b/11d/11e (в 11f уже есть). (Устарело: Future MC уже убран.) Для 11z в `futuremc.cfg` выключить: «Spawn Rate»=0 у cornflower,
  lily of the valley, berry bush и пустой «Bee Nest Biome Spawns» (бамбук Future MC глушит код 11c, опции у него нет).
- BuildCraft: `useSwappableSprites=false` (невидимые трубы с OptiFine).
- TAIGA: пропатчен `tools/taiga_patch` (каскад 373 → 0), оригинал в `removed_mods/10_original_taiga`.
- **Shattered Citadels 1.10.0 (26.11.2026, SHA-1 `0fb8e9ad…`) стоит в Prism (1.12.2-edit) и на общем сервере** (1.9.2 в `removed_mods_replaced_by_update` и `mods_client_only`; бэкап `_saves-backup-before-sc1100`; 1.9.2 в Prism была поставлена тоже 26.11). Новое: мосты через реки (7 видов по биому + 3 редких, каждый пятый с лагерем охраны и сундуком; `/citadel spawn bridge [вид] [fortified]`; конфиг `bridges`) и `compat/ForeignZones` — замки, храмы и мосты не строятся в зоне Припяти (рефлексия на `PripyatZone.touches`; с настоящим modernbackports НЕ проверено, только тестовой заглушкой — перепроверяет этап 14). Сервер: новый мир BOP 2500 чанков и world_taiga — Done, TPS 20, исключений мода 0, каскада от мода 0, естественный мост `snow_stone` построен. В игре (клон `1.12.2-test-citadels`, сценарий `citadels-1100-bridges.json`, снимки `F:\minecraft-mods\_shots-sc1100`): 12 мостов командой построены. Дальше по `wt\citadels\docs\TRANSFER.md`: хижины ведьм.
- **Shattered Citadels 1.9.2 (26.11.2026, SHA-1 `f1f89550…`, коммит 6bb7d6d) запушена и стоит на общем сервере; в Prism (1.12.2-edit) ПОКА 1.9.1 — игра была запущена, поставить при закрытой игре (бэкап saves, 1.9.1 в `removed_mods_replaced_by_update`).** Исправлено: одна полоска здоровья у боссов из модов (Барако, фараон), у решётки сокровищницы текст про идолов. Проверено: 143 теста, автотест `citadels-192-check.json` PASS (снимки), сервер world_taiga загрузился, TPS 20. Мосты через реки: решения владельца и дизайн в `wt/citadels/docs/superpowers/specs/2026-11-26-river-bridges-design.md`, ждёт одобрения владельца, кода ещё нет.
- **Shattered Citadels 1.9.1 стоит в Prism и на сервере (26.11.2026).** Разработка мода передана в этот проект: тред
  «Развивать мод Citadels дальше», клон `F:\minecraft-mods\wt\citadels` (ветка `claude/brave-franklin-ttdlk9`, сборка на JDK 21:
  `JAVA_HOME=%USERPROFILE%\.gradle\jdkszul_systems__inc_-21-amd64-windows.2 ./gradlew build --no-daemon -q`, Gradle 8.10 на JDK 25 не идёт).
  Сначала читать `docs/TRANSFER.md` репозитория мода. PR не открывать, пока владелец не попросит; jar в `dist/`.
  1.9.1 (SHA-1 `bb1dafa5…`): палитры, мебель и лут берут `modernbackports:*` вместо удалённых Future MC, Unseen's Nether, MoreBlocks
  (в логе 128 модовых вариантов палитр вместо 99). Сервер: новый мир BOP (1500 чанков, TPS 20, каскада от мода нет, строка
  «our temples take its desert and jungle sites»), старый мир от 1.9.0 открылся (13 записей). В игре (клон `1.12.2-test-citadels`,
  сценарии `packautotest/scenarios/citadels-s5-build.json` и `-check.json`, снимки `F:\minecraft-mods\_citadels-screens-pass2`):
  3 идола из тайников → 3 пьедестала → сокровищница открылась; коробка Mekanism кирпич и решётку не берёт; фараон Atum и Барако
  вызываются, после смерти печати сундука снимаются. Бэкап saves `_saves-backup-before-sc191`. Следующая работа: мосты через реки.

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

- **Волна 5: 10d, 05d, 05e, 08-everbright, 08-everdawn слиты и стоят (этап M, 26.11.2026).** PR #28 (10d музыка 1.13–1.21,
  6 пластинок, компаратор 1.21, «Периодичность музыки», свои пластинки mp3/ogg), #29 (05d дропы 1.21.5–1.21.9: варианты
  коров/свиней/куриц, счастливый/высохший гаст и упряжь, медный голем и медные сундуки/статуи, полки, медные факел/фонари/
  цепи/решётки, растения 1.21.5), #30 (05e дроп 1.21.11: копья, «Рывок», наутилусы, верблюд-кадавр, пустынник, лошадь-зомби),
  #31 (08-everbright: измерение «Вечносвет», dimension 1201), #32 (08-everdawn: измерение «Вечнозаря», dimension 1202) слиты
  в main modernbackports; рабочий `HANDOFF-08.md` удалён (57ae685), отметка в backport-plan 253e520. Чужие файлы только у 10d
  (строка в `MbEarlyMixins.CONFIGS`, `extra.gradle` → свой `music-10d.gradle`, `verify.py` ищет .ogg в build/generated).
  `DataFixes.CURRENT=7` не менялся. **Biome ID +2** (`modernbackports:everbright`, `modernbackports:everdawn`, только в своих
  измерениях) — занято ~154 из 256. Измерения 1201 и 1202 другими модами сборки не заняты (оба «registered» в логе).
  Jar SHA-1 `2573799c29ebe7cd8c476c0efebe02085eed1b3b` (main 1358e3b, `--no-daemon`, javap: SRG-имена; JLayer в
  `modernbackports.shadow.javazoom`), ресурс-пак `modernbackports-music.zip` SHA-1 `80c03561…` (137 МБ, 36 треков);
  копии, логи, перепись мира — `F:\minecraft-mods\_M-w5-jar` (первый jar без 08-everdawn `c6e3c2d4` — в `old-c6e3c2d4`).
  verify.py `--fresh-world`: 0 ошибок, 0 предупреждений, 580 блоков, 743 предмета, 67 сущностей.
  В 1.12.2-edit: старый jar → `7_replaced_by_update\modernbackports-0.0.1-before-M-w5.jar`, `modernbackports-music.zip` в
  `minecraft
esourcepacks` (мод подключает сам, в options.txt включать не нужно; у владельца громкость музыки 0 — фоновую
  музыку не слышно, пока не поднять ползунок «Музыка»), `-Dfml.readTimeout=120` уже был (поставлен этапом 05d), конфиги не
  менялись (10d/05d/05e/08-*.cfg создаются сами). Бэкап saves `_saves-backup-before-M-w5`.
  Общий сервер: новый jar в mods, старый `mods_client_only\modernbackports-0.0.1-before-M-w5.jar`; **в `drive.py` добавлен
  `-Dfml.readTimeout=120`** рядом с `-Xmx6G` (тайм-аут входа из-за загрузки квестов FTB), сервер с ним стартует (TPS 20).
  Проверено на сервере (копия `_server-M-w5`, удалена): копия world_taiga — Forge ничего не спросил, исключений мода нет,
  TPS 20; новый мир (сид 2026112506) — ~2720 новых чанков Верхнего мира, 1259 Незера, 695 «Вечносвета», TPS 20, каскада от
  modernbackports нет (MrTJPCore 58, Quark 27, Dynamic Trees 7, LLibrary 3, Raids 1); в world_taiga — 800 чанков «Вечнозари»
  и 599 «Вечносвета», каскада вообще нет. Перепись: опавшая листва 12 155, полевые цветы 819, куст 500, светлячки 61,
  высохший гаст 4, в «Вечносвете» 3 башни, бараны/медузы/вараны. Дом Привратника в этом сиде сам не построился (кандидаты
  отбракованы по рельефу; у 08 на другом сиде строился).
  Проверено в игре (клоны `1.12.2-test-M`, `-M2`, OptiFine G5, ресурс-пак музыки; лучшие снимки `F:\minecraft-mods\_M-w5-screens`):
  10d-music (списки музыки по биому, под водой, пещеры, творческий, Незер), 10d-discs2 (mp3 и ogg на «Чистой пластинке»
  играют в проигрывателе, кнопка «Частота» на экране звука), 05d, 05e (и повтор на итоговом jar), 08-storm, 08-boss,
  08-everdawn-lab — PASS; 08-everbright и 08-everdawn — все снимки на месте, сбоили только шаги `waitChunks` у портала (время,
  не мод); регресс 11b-stations, 11c-mobs-plants, 03b-mech — PASS. Ошибок мода в логах клиентов нет (только «Unable to parse
  metadata» у текстур брони copper/aquite/charoite/netherite — безвредно, как раньше у netherite).
  Сценарий `packautotest/scenarios/10d-music.json` исправлен (43ef8f4: огнестойкость перед Незером, игрок падал в лаву);
  `10d-discs.json` устарел (ставит проигрыватель до загрузки чанков) — использовать `10d-discs2.json`.
  Не удалось проверить: музыку на слух, музыку главного меню, пластинки в настоящих сундуках/дропе, рассылку своих пластинок
  на выделенный сервер с живым игроком; полёт на гасте и езду на наутилусе с клавиатуры, таран и «Рывок» у игрока; торговлю
  Привратника/Звездочёта (автотест не кликает по сущности), автопереплавку кирки зарника; естественный спавн новых мобов
  рядом с игроком; вишнёвые/пустынные биомы в тестовой области.
  Ветки stage/10d, 05d, 05e, 08-everbright, 08-everdawn и их worktree удалены. Остались `wt\06` (stage/06), `wt\02b-test`.
  **Вопросы владельцу из отчётов волны 5** (в итоговом сообщении M): броня наутилуса в рыбалке (05e); Creator (Music Box)
  временно в сундуках коридоров (10d); решения 05d «не утверждены явно» (медь при Thermal, варианты старых животных, вид
  1.21.5 у умеренных, гаст в бартере); декор и хребты измерений, ручной бой с боссами (08).
- **Волна 6: 08-undergarden и 08-bumblezone слиты и стоят (этап M, 26.11.2026).** PR #33 (08-undergarden: измерение
  «Глубинный сад», dimension 1203, мобы 2900–2905, заросший колодец с корневым катализатором в лесах/болотах/джунглях, гнилое
  гнездо и босс Гнилая матка, `/mb08u`) и #34 (08-bumblezone: измерение «Медовый улей», dimension 1204, мобы 2950–2956,
  пасека Пасечника в равнинах и лесах, осиное гнездо и Королева шершней, `/mb08b`) слиты в main modernbackports (2238a10,
  4e8e37a); отметка в backport-plan 8e91745. Чужих файлов нет, `DataFixes.CURRENT=7` не менялся. **Biome ID +2**
  (`modernbackports:deepgarden`, `modernbackports:honeyhive`, только в своих измерениях) — занято ~156 из 256.
  Генераторы входа: колодец вес 1102, пасека 1101 (равен палатке «Вечнозари» — не ошибка). Измерения 1201–1204 другими модами
  не заняты (все «registered» в логе).
  Jar SHA-1 `9c9257adf70d6fcf813228d5259eeacfacb353e9` (main 4e8e37a, `--no-daemon`, javap: SRG-имена во всех 133 классах
  двух этапов), копия, логи, листы — `F:\minecraft-mods\_M-w6-jar` (первый jar без улья `06504f3f` — в `old-06504f3f`).
  verify.py `--fresh-world`: 0 ошибок, 0 предупреждений, 619 блоков, 833 предмета, 80 сущностей. Ресурс-пак музыки не менялся
  (`80c03561…`).
  В 1.12.2-edit: старый jar → `7_replaced_by_update\modernbackports-0.0.1-before-M-w6.jar`, конфиги не менялись
  (08-undergarden/08-bumblezone.cfg создаются сами). Бэкап saves `_saves-backup-before-M-w6`.
  Общий сервер: новый jar в mods, старый `mods_client_only\modernbackports-0.0.1-before-M-w6.jar`; старт проверен (TPS 20,
  все 4 измерения registered), world_taiga переписан новым jar, лог `console_M-w6.log`.
  Проверено на сервере (копия `_server-M-w6`): копия world_taiga на старом и на итоговом jar — Forge ничего не спросил,
  исключений мода нет (108 исключений — те же чужие, что в волне 5), TPS 20; в старом мире 400 новых чанков 1203 и 354 чанка 1204 —
  каскада в измерениях нет. Новые миры: сид 2026112607 (jar без улья) — 1361 чанк Верхнего мира, 1108 «Глубинного сада», по 299 в 1201 и 1202,
  5 колодцев построились сами, `/mb08u selftest` 9/9; сид 2026112608 (итоговый) — 1489 Верхнего мира, 1024 «Медового улья»,
  269 «Глубинного сада», 300 «Вечносвета», 299 «Вечнозари», TPS 20, 2 пасеки и 3 колодца сами, `/mb08b selftest` 8/8,
  `/mb08u selftest` 9/9. Каскад только в Верхнем мире и только чужой (MrTJPCore 105, Quark 44, Dynamic Trees 23, LLibrary 6,
  Raids 1); в измерениях 1201–1204 — 0 от всех модов. Осиное гнездо в первой области (±260 блоков) не попалось, поэтому
  догенерированы 454 чанка 1204 вокруг кандидатов `/mb08b locate vespiary`: оба гнезда построились сами (-545 47 111,
  623 48 -321), каскада ни от одного мода нет, TPS 20 (лог `console_c_vespiary.log`).
  Проверено в игре (клоны `1.12.2-test-M`, `-M2`, OptiFine G5; скриншоты `F:\minecraft-mods\_M-w6-screens`): 08-undergarden,
  08-undergarden-nest, 08-undergarden-mobs — PASS (колодец, портал зажжён, 5 мобов, грибной лес светится, гнездо с печатью,
  матка в зале, ловец висит под потолком); 08-bumblezone-nest — PASS (гнездо, печать, бой с Королевой, полоса босса, лут);
  08-bumblezone и повтор 08-undergarden на итоговом jar — все снимки на месте, сбой только шага `waitChunks` (время);
  регресс 05e, 08-everdawn-lab, 11b-stations — PASS на итоговом jar; 08-everbright, 08-everdawn — только `waitChunks`.
  После установки 08-bumblezone-nest повторён на содержимом самого 1.12.2-edit (`--refresh` без `--jar`, jar `9c9257ad`): PASS.
  Ошибок нашего мода в логах клиентов нет.
  Замечание к сценарию `08-bumblezone`: снимок `01_apiary_outside` в этом прогоне снят вплотную к боковой стене пасеки (у этапа
  в `_08b-screens` — фасад с дверью). Точная причина не выяснена; похоже, `/mb08b place apiary` выполнился, пока не
  дождался шаг `waitChunks 15` перед ним (сбой по времени), и пасека встала иначе. Снимок изнутри нормальный. Проверить в
  `gen_08_bumblezone.py` (ждать чанки дольше перед `place apiary`).
  Не удалось проверить: бой с маткой руками, падение ловца в выживании, эффекты спорита/умбрита, проход через портал пешком,
  туман пещер и улья, торговлю Пасечника (автотест не кликает по сущности), «липкие» инструменты, бутылочку мёда от жука,
  естественный спавн клеща/шершня рядом с игроком, звуки.
  Ветки stage/08-undergarden и stage/08-bumblezone (удалённые) и клоны `wt\08-undergarden`, `wt\08-bumblezone` удалены.
  Копия сервера `_server-M-w6` удалена (логи в `_M-w6-jar\logs`); `_server-08b` (этап улья) можно удалить. Тогда оставались `wt\06`, `wt\02b-test`, `wt\08-otherside` (слиты волной 7).
  Ловушка для закрытых миров: на скриншотах ищи кадры «камера в стене» и падение игрока в творческом.
  **Вопросы владельцу волны 6** (в итоговом сообщении M): 08-undergarden — плотность монстров (`monsterDensity` 3), частота
  колодцев (`wellSpacing` 12), рецепт катализатора (выкл.); 08-bumblezone — вход (пасека или ещё жемчуг в гнездо), сила
  снаряжения, свет в улье, густой туман, пчёлы 11c, босс, плотность клеща/шершня. Сейчас всё по рекомендациям.
- **Волна 7: 08-otherside и 06 слиты и стоят (этап M, 26.11.2026).** PR #35 (08-otherside: измерение «Изнанка», dimension 1205,
  сущности 3000–3049: щелкун, разбитый, пиявка, удильщик, босс Сталкер 250 HP; вход — рамка из укреплённого сланца в центре
  древнего города 03b, зажигается «Сердцем глубин» с хранителя; цитадель и руины, `/mb08o`) и #23 (06: пробелы 1.13–1.16 —
  фантом и бессонница, черепаха, дельфин, лиса, странствующий торговец, кошка, утопленник, арбалет, ламинария, кораллы и рифы,
  проводник, пузырьковые столбы, клады, кораблекрушения, подводные руины, костёр душ, нерезная тыква; сущности 1700–1709)
  слиты в main modernbackports (b00f9dc, 7c0bf6e); отметка в backport-plan 45d577e (строки 06 → ЕСТЬ). Чужой файл только у 06:
  строка `mixins.modernbackports.06.json` в `MbEarlyMixins.CONFIGS`. `DataFixes.CURRENT=7` не менялся. **Biome ID +1**
  (`modernbackports:otherside`) — занято ~157 из 256 (у 06 новых биомов нет, рифы без Biome ID).
  Jar SHA-1 `b1fd2ac495b03d61683ac5f2a4aaed8bb78bcd8a` (main 7c0bf6e, `--no-daemon`, javap: SRG-имена в 234 классах s06 и
  s08otherside; первый jar без 06 не ставился), копия и логи — `F:\minecraft-mods\_M-w7-jar`. verify.py `--fresh-world`: 0 ошибок, 0 предупреждений, 669 блоков, 912 предметов, 95 сущностей.
  В 1.12.2-edit: старый jar → `7_replaced_by_update\modernbackports-0.0.1-before-M-w7.jar`, конфиги не менялись
  (06.cfg и 08-otherside.cfg создаются сами). Бэкап saves `_saves-backup-before-M-w7`.
  Общий сервер: новый jar в mods, старый `mods_client_only\modernbackports-0.0.1-before-M-w7.jar`; старт проверен (TPS 20,
  все 5 измерений 1201–1205 registered), world_taiga переписан новым jar, лог `console_M-w7.log`.
  Проверено на сервере (копия `_server-M-w7`): копия world_taiga — Forge ничего не спросил, исключений мода нет (108 — те же
  чужие), миксины 06 подключились (предупреждения mixin те же 47, что в волне 6), TPS 20, 350 новых чанков Верхнего мира и 354
  Изнанки без каскада в измерении. Новый мир (сид 2026112610, тестовый, самотест 06 включён только в копии): самотест 06 — 29/29,
  `/mb08o selftest` 12/12; 1454 чанка Верхнего мира, 951 Изнанки, по 182–200 в 1201–1204, TPS 20; затем 1265 чанков у океанского
  монумента (1256 -840) — 5 кораблекрушений и 18 кусков подводных руин построились сами, и 301 чанк Изнанки. Каскад только в
  Верхнем мире и только чужой (MrTJPCore, Quark, Dynamic Trees, LLibrary), в 1201–1205 — 0. Древние города 03b сами построились
  (88 36 8 и -168 36 72); после загрузки чанков города `/mb08o lightcity 88 36 8` нашёл рамку и зажёг портал (78 30 8).
  Своя цитадель в сгенерированной области в лог не пишется — проверена самотестом (4007 59 4007) и в игре.
  Проверено в игре (клоны `1.12.2-test-M`, `-M2`, OptiFine G5; скриншоты `F:\minecraft-mods\_M-w7-screens`): 08-otherside —
  все снимки, сбоили только 2 шага `waitChunks` (рамка зажглась, 5 мобов, Изнанка, цитадель, полоса «Сталкер», лут в хотбаре);
  08-otherside-city (обычный мир, сид 8205) — в центре древнего города горит портал, игрок в Изнанке на мрачном дёрне и снова
  у портала города, сбоили только 2 шага `waitChunks`; 06-gaps — PASS (торговец и лама, кошка, лисы, черепаха, утопленник и
  фантом горят днём, кораллы, морская трава, проводник, пузырьковые столбы, арбалет); регресс 03b-mech, 08-bumblezone-nest, 08-undergarden — PASS.
  После установки 08-otherside-city повторён на содержимом самого 1.12.2-edit (`--refresh` без `--jar`, jar `b1fd2ac4`):
  портал в городе и переход в Изнанку на снимках, сбоили только те же 2 шага `waitChunks`.
  Ошибок нашего мода в логах клиентов нет.
  Не удалось проверить: бой со Сталкером руками, слух разбитого на живом игроке, укус пиявки и бросок удильщика, убийство
  хранителя игроком в игре (только самотест), туман; у 06 — ИИ мобов (в сценарии мобы без ИИ), сундуки кораблей и карта
  сокровищ в игре, анимация арбалета, утопленники из зомби под водой, шейдеры.
  Ветки stage/06 и stage/08-otherside (локальные и удалённые) и worktree `wt\06`, `wt\08-otherside` удалены (всё было в main,
  незакоммиченного не было). Остались `wt\02b-test` и `wt\08-polish` (новый тред). Временные папки этапа 08o
  `F:\minecraft-mods\_server-08-otherside` и `_08o-jar` и моя копия `_server-M-w7` не удалены (удаление заблокировала проверка
  безопасности) — можно удалить руками.
  Следующее (шестое) измерение этапа 08: порт 25876, ID 3050–3099, измерение 1206.
  **Вопросы владельцу волны 7** (в итоговом сообщении M): 08-otherside — сердце с хранителя (тратится, 1 шт.), запасной рецепт
  входа (выкл.), темнота и туман, сила резонария/эхолита, мобы и босс 250 HP, сердце в сокровищнице, исключить ли мобов Изнанки
  из Champions; 06 — нерезная тыква (да), рифы 25 %, частоты кораблей и руин (как в 1.16), бессонница (вкл.). Сейчас всё по
  рекомендациям и как в ванили.

- **Стресс-тест всей сборки (26.11.2026, jar b1fd2ac4).** Своя копия сервера `F:\minecraft-mods\_server-stress` (моды и
  конфиги как в 1.12.2-edit; общий сервер не трогался), мир BIOMESOP сид 2026112620, `drive_stress.py` (ждёт генерацию по
  числу чанков в region, пишет GC-лог и JFR). ~13 000 чанков: Верхний мир 5 областей до ±8000, Незер, Край (внешние острова),
  1201–1205, Атум (17), Teletory (16). Генерация 25–35 чанков/с, TPS 20, паузы GC до 0,6 с, живая куча ~650 МБ.
  Каскад только чужой (MrTJPCore 112, Dynamic Trees 13, Quark 9, LLibrary 1). Время генерации по JFR: BoP 28 %,
  Better Caves (YUNG) 24 %, NotEnoughIDs 12 %, ProjectRed+scala ~6 %, весь modernbackports ~8 % (свои измерения).
  Клиент (автотест `packautotest/scenarios/stress-flight.json`, клон `1.12.2-test-stress`, с квестами FTB): PASS, загрузка
  161 с, вход в мир 45 с, FPS 190–235 (OptiFine), TPS 20 в покое; при перелётах по 300 блоков по новым чанкам TPS падал
  до 5,8 (генерация — в основном BoP и Better Caves). В 9 измерениях всё грузится, FPS ≥ 150.
  **Найдено и исправлено (PR https://github.com/masterRaizer/modernbackports/pull/38, черновик, ветка fix/stress-test,
  клон `F:\minecraft-mods\wt\stress-fixes`, jar `_server-stress\modernbackports-0.0.1-fix-b52d944.jar`):**
  1) утечка выгруженных измерений — Large Ore Deposits, ForgeEndertech, Collective, Modular Machinery CE держали миры в
  статических картах (20 `WorldServerMulti` в памяти при 2 загруженных); `stages.sperf.WorldLeakFix` чистит их → 3.
  2) мусорные предметы генерации (2 284 на 5 132 чанка: порох, листва, рельсы, цветы, факелы) — не создаются во время
  `Chunk.populate` (ранний миксин) → 0,12 на чанк. Конфиг `modernbackports/perf.cfg`. В Prism НЕ стоит (ждёт слияния M).
  Остались: опавшая листва/полевые цветы 05d и ламинария 06 выпадают предметами через 0–400 тиков после генерации
  (причина не найдена); в клиенте исправления не проверены (не хватило памяти). Инструменты: `_server-stress\region_entities.py`
  (сущности/предметы по region), `hprof_referrers.py` (кто держит объект в дампе), `log_summary.py`.
  Вопрос владельцу: Better Caves — самая тяжёлая часть генерации; облегчать его настройки — изменение пещер.

- **Этап 08-abyss: измерение «Бездна» готово, ждёт этапа M (26.11.2026).** Черновой PR
  https://github.com/masterRaizer/modernbackports/pull/39 (ветка `stage/08-abyss`, клон `F:\minecraft-mods\wt\08-abyss`),
  отчёт `docs/stages/08-abyss.md`, промпт `F:\промпты майн 1.12.2\08-abyss.txt`. Измерение 1207, сущности 3100–3105,
  порт 25926, вес генератора входа 1107, пакет `stages.s08abyss`, команда `/mb08a`, **Biome ID +1**
  (`modernbackports:abyss`). Вечная ночь, разломы-пропасти, лес ночедрева / открытая земля / мёрзлая пустошь; вход —
  алтарь разлома в холодных и горных биомах (ключ в сундуке) и рецепт ключа; босс Жнец пустоты в тёмном шпиле.
  jar SHA-1 `2addfa25…` (копия `F:\minecraft-mods\_08a-jar`), скриншоты `F:\minecraft-mods\_08a-screens\final`.
  Проверено на сервере: verify.py 0 ошибок, `/mb08a selftest` 9 из 9, 1000 чанков за 29 с, TPS 20; со всей сборкой
  (копия `_server-08-otherside`, мир `world_08a`, порт 25936 — в её `mods` остался jar этапа) — каскада в Бездне нет,
  алтарь и шпиль строятся сами. Проверено в игре (клон `1.12.2-test-08-abyss`): 61 снимок, FPS 149–240, сбоят только
  шаги `waitChunks`. Имена разведены с параллельным 08-outerend (`voidspire_*`, `gleamcap`).
  Декор Бездны (24 блока) уже в PR 39: main с 08-polish подтянут в ветку, строки добавлены в таблицы `S08pDecor`
  (при слиянии с 08-outerend возможен конфликт в этих таблицах — оставить обе правки); итоговый jar `2addfa25…`,
  `/mb08p selftest` 9 из 9. Владелец 26.11 на вопросы по балансу ответил «все да» — всё оставлено как есть. Следующее (восьмое) измерение: порт 25976, ID 3150–3199,
  измерение 1208.

- **Этап 08-outerend готов и ждёт этапа M (26.11.2026).** Шестое измерение «Внешний Край» (идея The Outer End, код и
  арт свои): dimension 1206, сущности 3050–3055 (долгоног, кристальный страж, осколочник, призрак разлома, босс Архонт
  250 HP, мерцалка), +1 Biome ID (`modernbackports:outerend`, будет ~158 из 256). Парящие острова в пустоте, три зоны,
  звёздное небо (рендерер Forge, работает с OptiFine G5), руды астрий и нуллит, звёздный шпиль с боссом раз в 24 чанка,
  27 блоков декора. Вход: рамка из звёздных кирпичей + звёздный ключ (крафты из материалов Края включены) и «разбитые
  врата» с ключом на внешних островах ванильного Края (вес генератора 1106). Команда `/mb08e`.
  Черновой PR https://github.com/masterRaizer/modernbackports/pull/37 (ветка `stage/08-outerend`, папка
  `F:\minecraft-mods\wt\08-outerend` — обычный клон, не worktree), отчёт `docs/stages/08-outerend.md`, итоговый jar
  SHA-1 `8050eacf…` (копия `F:\minecraft-mods\_08e-jar`), скриншоты `F:\minecraft-mods\_08e-screens\final`.
  Только новые файлы, общие и чужие не менялись, `DataFixes.CURRENT` не менялся.
  Проверено на сервере: verify.py 0/0; `/mb08e selftest` 13 из 13; dev — 1000 чанков за 29 с, TPS 20, каскада нет;
  копия сервера со всей сборкой `_server-08e` (порт 25886, можно удалить) — 1114 чанков Внешнего Края, 609 Верхнего
  мира, 2601 Края, разбитые врата и шпиль построились сами, TPS 20, каскада от мода нет (Quark 2 в Верхнем мире).
  Проверено в игре (клон `1.12.2-test-08-outerend`, OptiFine G5, сценарий `08-outerend.json`, генератор
  `gen_08_outerend.py 319 63 543`, сид 8206): 244 из 246 шагов, сбоили только `waitChunks`; острова, небо, 6 мобов,
  блоки, декор, шпиль и полоса босса на снимках, FPS 223.
  Не удалось проверить: бой с Архонтом руками, левитацию от призрака на игроке, естественный спавн рядом с игроком,
  врата в настоящем Крае в игре, выход из измерения обратно в Край пешком, звуки, шейдеры.
  **Вопросы владельцу** (в отчёте, 9 штук): вход только после дракона; ключ тратится; частота врат; сила астрия и
  нуллита; левитация от призрака у края острова; посох скачка; босс и частоты; яркость; жемчуг из эссенции.
  При слиянии с параллельным 08-abyss (1207) запустить verify.py: он ловит дубли имён. Следующая свободная шапка:
  порт 26026, ID 3200–3249, измерение 1208 (3100–3149/25926 — 08-abyss, 3150–3199/25976 — этап 12).

- **Этап 13-atm: металлы Allthemodium и звезда ATM готовы, ждут этапа M (26.11.2026).** Черновой PR
  https://github.com/masterRaizer/modernbackports/pull/41 (ветка `stage/13-atm`, клон `F:\minecraft-mods\wt-atm`),
  отчёт `docs/stages/13-atm.md`. Порт 26026, ID 3200–3249 (сущностей нет), пакет `stages.s13atm`, команда `/mb13`
  (`selftest`, `count <dim> <cx> <cz> <r>`), конфиг `modernbackports/13-atm.cfg`. Новых биомов, измерений, миксинов нет.
  Руды аллтемодиума (Верхний мир, Y 4–20) и анобтаниума (Край, Y 20–60); **вибраниум общий с TAIGA** (решение владельца):
  своей руды в сборке нет, рецепты берут `ingotVibranium`. Три сплава, инструменты и броня трёх ярусов (вибраниум и
  анобтаниум — улучшением +3 слитка, зачарования сохраняются), 4 ядра и звезда ATM из предметов больших модов
  (состав в конфиге `star.*`). jar SHA-1 `db53bd9e…` (копия `F:\minecraft-mods\_13-atm-jar`).
  **Генерацию в сборке ставит CoFH World:** `minecraft/config/cofh/world/05_pack_atm_ores.json` (репозиторий сборки,
  76d4b11) — при установке M положить в `config/cofh/world` инстанса 1.12.2-edit и общего сервера, иначе руд не будет
  (встроенный генератор мода включается только без CoFH World).
  Проверено на сервере: verify.py 0 ошибок, `s13atm_test.py` 13/13; со всей сборкой (копия `_server-13-atm`, порт 26036,
  сид 2026112613) — `/mb13 selftest` 63/63, все 32 чужих предмета рецептов найдены, аллтемодиум 0,59 блока/чанк,
  анобтаниум 0,72 на чанк острова Края, TPS 20, каскада от мода нет. В игре: автотест `packautotest/scenarios/13-atm.json`
  (клон `1.12.2-test-13-atm`) — см. отчёт этапа. Вопросы владельцу (частота анобтаниума, цена улучшения, сплавы в
  плавильнях, применение звезды) — в конце отчёта. Для треда квестов: финальная глава под `modernbackports:atm_star`.
  Замечание: на dev-сервере генератор Незера какого-то другого этапа даёт каскад при дозагрузке краевых чанков
  (сид 366633049454668766, лог `F:\minecraft-mods\wt-cascade1.log`).
- **13-atm, правки по ответам владельца (26.11.2026): черновой PR
  https://github.com/masterRaizer/modernbackports/pull/43, ветка `stage/13-atm-2`, ждёт этапа M.** Клон
  `F:\minecraft-mods\wt\13-atm`. Анобтаниум втрое реже (`unobtainiumChunkChance` 3 и `chunk-chance` 3 в
  `config/cofh/world/05_pack_atm_ores.json` — уже в репозитории сборки, **при установке jar скопировать этот файл в config
  инстанса и общего сервера**). Сплавы делаются в индукционной плавильне Thermal и плавильне сплавов Ender IO (IMC),
  рецепт верстака включается сам только без плавилен (`alloys.craftingTable`). Звезда ATM в инвентаре даёт ауру:
  Регенерация I, Спешка I, Скорость I, Ночное зрение владельцу и игрокам в 8 блоках (раздел конфига `aura`).
  Цена улучшения (3 слитка) оставлена. Проверено на сервере со всей сборкой: `selftest ok 76/76`, 3 из 3 рецептов в
  обеих плавильнях, анобтаниум 0,23 на чанк острова (было 0,72), TPS 20, каскада нет. В игре (подсказка звезды, значки
  эффектов): автотест `scenarios/13-atm.json`, результат — в отчёте этапа `docs/stages/13-atm.md`.
- **Apotheosis: проверка и конфиг (26.11.2026).** Apotheosis 1.12.5 и Placebo 1.6.1 стоят с мая — это последние версии
  для 1.12.2 (CurseForge), jar не менялись. ID: эффектов 133 из 256, зачарований 131, коллизий нет. Модули не выключать:
  зелья/книги/полки Apotheosis уже записаны в мирах, а пропатченный Enchanting Plus берёт уровни из его конфига.
  Зелья сопротивления/спешки/поглощения/усталости/иссушения дублируются у Quark, PotionCore, CoFH и Apotheosis — оставлено.
  Решения владельца (26.11): 1) в «случайных» спавнерах Deadly (`deadly.cfg`, категория `random spawners`, вес 0) нет
  боссов: Визер, Дракон, древний страж, гигант, Хранитель Хаоса, боссы Mowzie, `atum:pharaoh`, мимик, Варден и боссы
  измерений modernbackports (`stalker`, `hornet_queen`, `brood_mother`, `summoner`, `alchemist`, `barnacle`),
  `shatteredcitadels:guardian_mage`; 2) шанс брутальных/роевых спавнеров на чанк 0.12/0.15 → 0.04/0.05; 3) модификатор
  спавнера «без лимита мобов» больше не ставится хорусом (`spawner.cfg` `ignore_spawn_cap` item = `minecraft:barrier`),
  остальные модификаторы и добыча шёлковым касанием как были; 4) тростник не ограничивать (255). Скрипт
  `tools/apotheosis_tune.py <папка config/apotheosis> bosses spawners chorus`. **Новые боссы новых этапов появляются в
  списке с весом 1 — после каждого M обнулять их в `deadly.cfg` (дописать в BOSSES скрипта).** Проверено на сервере:
  новый мир (сид 2026112601), 1500 чанков, TPS 20, каскада от Apotheosis нет, 103 спавнера (39 роевых, 2 случайных
  по 80 мобов, боссов среди них нет). В игре (автотест `packautotest/scenarios/apotheosis.json`, клон
  `1.12.2-test-apotheosis`, скриншоты): стол с адскими полками открывается, хорус спавнер не меняет, сахар работает.
  Конфиг стоит в 1.12.2-edit и на общем сервере, бэкап saves `_saves-backup-before-apotheosis`.
  Лог «Had to late load enchantment info for aquaculture:*» — старый и безвредный.

- **Волна 8: 08-polish и perf (стресс-тест) слиты и стоят (этап M, 26.11.2026).** PR #36 (08-polish: декор пяти измерений —
  119 блоков, рецепты и камнерез; рецепты входов во все пять измерений включены, огниво — око Края + 2 алмаза; жемчуг Края в
  пчелиное гнездо → Медовый улей; Сердце глубин при каждом убийстве хранителя игроком; броня из скалка только в сундуках древнего
  города, 15 %; Изнанка светлее; фантомы 06 не прилетают) и #38 (пакет `sperf`, `config/modernbackports/perf.cfg`: `worldLeakFix` —
  освобождает выгруженные измерения из статических карт Large Ore Deposits/ForgeEndertech/Collective/MMCE, `noWorldgenItems` — не
  создаёт выпавшие предметы во время украшения чанка; обе части выключаются) + страховка 216e0a8 (флаг сбрасывается в начале тика).
  `DataFixes.CURRENT=7`, новых Biome ID нет. Jar SHA-1 `ae9074db85110f480644643b068b4d9ba7bc984c` (main 216e0a8, `--no-daemon`,
  javap: SRG-имена, refmap populate → `func_186034_a`), копия и логи — `F:\minecraft-mods\_M-w8-jar` (jar только 08-polish
  `7540c6f7` — в `old-7540c6f7`). verify.py `--fresh-world`: 0 ошибок, 788 блоков, 1014 предметов, 95 сущностей.
  **Конфиги не править руками:** миграция 08-polish при первом запуске сама ставит `craftableEntry=true` в пяти `08-*.cfg` и
  `insomniaSpawning=false` в `06.cfg` и пишет `08-polish.cfg` `defaultsVersion=1` (не удалять — иначе повторится). Проверено в
  1.12.2-edit и на общем сервере («0 -> 1 (6 values written)»). В репозитории сборки копий этих конфигов нет.
  В 1.12.2-edit: старый jar → `7_replaced_by_update\modernbackports-0.0.1-before-M-w8.jar`, бэкап saves `_saves-backup-before-M-w8`.
  Общий сервер: новый jar, старый `mods_client_only\modernbackports-0.0.1-before-M-w8.jar`, старт TPS 20, лог `_M-w8-jar\logs\console_shared_start.log`.
  Проверено на сервере (копия `_server-M-w8`): копия world_taiga — Forge ничего не спросил, исключений мода нет (108 — те же чужие),
  TPS 20; новый мир (сид 2026112612) — 1581 чанк Верхнего мира и по 389 в 1201–1205, каскад только чужой, `/mb08p selftest` 9/9,
  perf: «watches» 5 карт и «freed 1 unloaded world(s)» после выгрузки каждого измерения. Предметы из консольных `/summon item`,
  `/kill` коров и `setblock … destroy` выпали (найдены в region-файле, `_M-w8-jar\items_near.py`).
  Проверено в игре (клоны `1.12.2-test-M`, `-M2`, OptiFine G5; листы `_M-w8-jar\sheets`): 08-polish, 08-polish-decor, 08-otherside,
  08-undergarden — сбоили только `waitChunks`; 06-gaps и новый `M8-drops` (мобы и блоки в выживании, предметы подобраны) — PASS;
  1.12.2-edit `M8-main --main` — PASS.
  Не удалось проверить: крафт руками в верстаке, бросок жемчуга с клавиатуры, бой с хранителем руками, проход через портал пешком,
  шейдеры; по perf — опавшая листва, полевые цветы (05d), ламинария (06), корни Quark и мох пышных пещер всё ещё выпадают предметами
  через 0–400 тиков после генерации.
  Грабли теста предметов: на выделенном сервере спавн не предзагружается, `say @e` видит только загруженные чанки — смотреть region-файлы.
  Ветки stage/08-polish, fix/stress-test и их папки удалены. `_server-stress`, `_server-08-polish`, `1.12.2-test-08p` оставлены.
  **Вопросы владельцу волны 8:** броня из скалка (как алмазная, ×35, 15 % на сундук), фантомов убрать совсем (`phantomEnabled=false`),
  цена огнива входа (око Края + 2 алмаза).

- **Этап 15-story: сюжетная линия «Хроника пяти эпох» — код готов, ждёт проверки в игре и этапа M (26.11.2026).**
  Главная цель сборки по словам владельца: сюжет с выбором игрока и книга с «утерянными знаниями». Черновой PR
  https://github.com/masterRaizer/modernbackports/pull/40 (ветка `stage/15-story`, клон `F:\minecraft-mods\wt\15-story`),
  отчёт `docs/stages/15-story.md`, заметки `docs/stages/15-story-notes.md`, сюжет (одобрен владельцем)
  `docs/story-hronika-pyati-epoh.md`. Порт 26126, ID 3300–3349 (3300 — босс «Отголосок»), пакет `stages.s15story`,
  команда `/mb15`, конфиг `modernbackports/15-story.cfg`. Новых биомов и измерений нет.
  Книга на движке Mantle (уже в сборке), 87 записей, страницы открываются обрывками из сундуков, входом в измерения,
  боссами, крафтами; прогресс общий на команду FTB. Реликвии пяти эпох и выбор «взять себе / вернуть» (10 оберегов),
  события Тишины, «Обелиск эпох», волны, босс, три концовки. Чужой файл: `gradle/scripts/dependencies.gradle`
  (+2 compileOnly: Mantle, FTBLib).
  Проверено на сервере: dev 10/10; со всей сборкой (копия `_server-15-story`) самотест 11/11, TPS 20, каскада от мода
  нет, 108 исключений — чужой фон. 9 записей «недоступны в сборке» до слияния 13-atm, 14-pripyat, 08-abyss,
  08-outerend (включатся сами по именам). **В игре проверено** двумя автотестами (PASS, снимки `F:\minecraft-mods\_15-screens`): книга, страницы, выбор, концовка; не проверены бой у обелиска, обереги, события Тишины, два игрока; сценарии `15-story-pages.json` и
  `packautotest/scenarios/15-story.json`, клон `1.12.2-test-15-story`.
  Для 14-pripyat: учитывать метку `mb15_zone_calm` в PlayerPersisted NBT (радиация уровней 1–2 не действует).
  Для треда квестов: список невидимых достижений `modernbackports:story/<id>` — `docs/stages/15-story-advancements.md`.
  Вопросы владельцу: шанс обрывков, сила финала, ночной визит Тишины у базы, обереги в ячейках Baubles.
- **Волна 9: 08-abyss, 08-outerend, 13-atm и этап 12 слиты и стоят (этап M, 26.11.2026).** PR #39 («Бездна», измерение 1207,
  сущности 3100–3105), #37 («Внешний Край», измерение 1206, 3050–3055), #41 (13-atm: металлы Allthemodium, звезда ATM; руды —
  `config/cofh/world/05_pack_atm_ores.json`, анобтаниум в Крае втрое реже по решению владельца, 152d7e7), #42 (этап 12: рыхлый
  снег, свет, сырые руды, окрасы волков, полоса игроков, правила игры, команды /forceload /spectate /attribute /item replace /damage
  /ride /random /tick /fillbiome, жители 1.14; ID 3150–3199). **Ловушка словаря руд:** у TAIGA есть астрий (`blockAstrium`), и
  одинаковое имя у Внешнего Края лишало JAOPCA блока `jaopca:block_blockastrium` (Forge спрашивал о пропаже в мирах, где он был).
  Исправлено в main 8f7eae3: словарь Внешнего Края `oreOuterAstrium`/`ingotOuterAstrium`/`blockOuterAstrium`. Новым материалам
  давать имена словаря, которых нет у других модов. Jar SHA-1 `81816770fa388133c57e2eb5c773fb416af4d933` (main 8f7eae3,
  `--no-daemon`, javap: SRG-имена, refmap), копия и логи — `F:\minecraft-mods\_M-w9-jar`. verify.py `--fresh-world`: 0 ошибок,
  892 блока, 1204 предмета, 107 сущностей; Biome ID +2 (`abyss`, `outerend`).
  Проверено на сервере (копия `_server-M-w9`): свежая копия world_taiga — Forge ничего не спросил, `block_blockastrium` снова есть,
  TPS 20; новый мир (сид 2026112615) — 620 чанков Верхнего мира, по 357 в 1206 и 1207, TPS 20, каскад от мода 0 (только чужой:
  MrTJPCore, Dynamic Trees, Quark, LLibrary); самотесты `/mb08a` 9/9, `/mb08e` 13/13, `/mb13` 63/63, `/mb12` 47/47; команды этапа
  12 добавлены все, занятых имён нет. Раньше (jar 6fd9ea2e) новый мир 1385 чанков, по 650 в 1206/1207, Незер 318, по 272 в 1201–1205.
  Проверено в игре (автотесты, клоны `1.12.2-test-M`, `-M2`): 08-abyss-decor, 13-atm, 12-gaps PASS; 08-abyss, 08-outerend
  (повтор на новом jar) и регресс 08-polish — сбоили только ожидания дорисовки чанков после перехода в измерение, снимки прибытия
  нормальные. Apotheosis: Архонт (`modernbackports:archon`) и Жнец пустоты (`void_reaver`) обнулены в `deadly.cfg` (добавлены в
  BOSSES `tools/apotheosis_tune.py`). Установка: бэкап `_saves-backup-before-M-w9`; в 1.12.2-edit старый jar →
  `7_replaced_by_update\modernbackports-0.0.1-before-M-w9.jar`, конфиг ATM-руд и `deadly.cfg`, запуск с автотестом PASS (0 «Unidentified mapping»); общий сервер — то же
  (ставит `_M-w9-jar/install_shared.sh` после LOCK треда Citadels), старый jar `mods_client_only\modernbackports-0.0.1-before-M-w9.jar`. Ветки stage/08-abyss, 08-outerend, 12-gaps удалены (клоны 08-* тоже);
  **stage/13-atm не удалена:** в ней коммит f92b692 (отчёт автотеста), которого нет ни в main, ни в 13-atm-2 — слить в M10;
  `wt\12-gaps` оставлен (там незакоммиченные заметки, этап 12-2 идёт), `wt\13-atm` занят веткой 13-atm-2.

- **Этап 14-pripyat: зона «Припять» готова, ждёт этапа M (26.11.2026).** Черновой PR
  https://github.com/masterRaizer/modernbackports/pull/45 (ветка `stage/14-pripyat`, клон `F:\minecraft-mods\wt\14-pripyat`),
  отчёт `docs/stages/14-pripyat.md`, заметки `docs/stages/14-pripyat-notes.md`, промпт `F:\промпты майн 1.12.2\14-pripyat.txt`.
  Порт 26076, ID 3250–3299 (мобы 3250–3254), пакет `stages.s14pripyat`, команда `/mb14`, 1 Biome ID, вес генератора 2014.
  Биом один на мир (1600–2400 от спавна): город, АЭС с разрушенным 4-м блоком, радиация (`ic2:radiation`), мутанты,
  босс Химера в подземной лаборатории, лут. Проверено на сервере: dev 7/7, со всей сборкой (копия `_server-14`, seed 14,
  центр -1264 73 1040) selftest 12/12, 1099 чанков за 48 с, TPS 20, каскада от мода 0. Проверено в игре (автотест
  `scenarios/14-pripyat.json`, клон `1.12.2-test-14-pripyat`, скриншоты `F:\minecraft-mods\_14-screens\auto1..3`): город,
  АЭС, мобы, предметы, радиация, FPS 225–240. **Открыто:** Shattered Citadels строит замок поверх зоны — в Citadels
  нужно вызывать по reflection `modernbackports.stages.s14pripyat.PripyatZone.touches(world,x1,z1,x2,z2)`; в игре не
  видел стелу после правки буквы, лабораторию и бой с боссом. Jar этапа: `F:\minecraft-mods\_14-jar`.
  Следующая свободная шапка: порт 26126, ID 3300–3349. Вопросы владельцу — в отчёте этапа.

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
