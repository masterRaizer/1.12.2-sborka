# Передача дел: ассистент по сборке 1.12.2

Состояние на 25.11.2026 (после волны 4: 03b, 02c-axolotl, 05b, 04b, 10c, 07c). Этот файл читает каждый новый тред проекта «ассистент по сборке 1.12.2».

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

- **Этап 10d (музыка и пластинки) — черновой PR https://github.com/masterRaizer/modernbackports/pull/28 (25.11.2026),
  ждёт этапа M.** 6 пластинок (Relic, Precipice, Creator, Creator (Music Box) — временно в сундуках коридоров залов,
  Tears, Lava Chicken), сигнал компаратора 1.21 для всех пластинок мода, фоновая музыка 1.13–1.21 по биомам/Незеру/под
  водой/пещерам/меню, «Периодичность музыки» (кнопка на экране звука), свои пластинки из mp3/ogg (папка
  `minecraft\modernbackports\discs`, «Чистая пластинка»: 4 редстоуна, 4 обсидиана, чернильный мешок; сервер рассылает
  файлы). Решения владельца: старые треки C418 остаются в списках (их подменяет medivalmusic), JLayer для mp3 вшит.
  **При установке:** кроме jar положить `build\libs\modernbackports-music.zip` (137 МБ) в `1.12.2-edit\minecraft
esourcepacks\`
  (мод подключает его сам); `-uberdev.jar` не ставить. У владельца громкость музыки 0 — фоновую музыку он не услышит.
  Проверено: dev-сервер, самотест 39/39, автотесты в клоне `1.12.2-test-10d` PASS; сервер со всей сборкой — за M.
  Копии jar/пака `F:\minecraft-mods\_10d-jar`, скриншоты `F:\minecraft-mods\_10d-screens`, отчёт `docs/stages/10d.md`.

- **Этап 05e (дроп 1.21.11 «Mounts of Mayhem») — черновой PR https://github.com/masterRaizer/modernbackports/pull/30
  (25.11.2026), ждёт этапа M.** Ветка `stage/05e`, `wt\05e`, порт 25627, ID 2800–2899; промпт
  `F:\промпты майн 1.12.2\05e - Дроп 1.21.11.txt`. Копья 7 материалов (тычок 2–4,5 блока, таранный удар от скорости), чары
  «Рывок», наутилус и наутилус-зомби (приручение иглобрюхом, седло, рывок, броня 5 видов, «Дыхание наутилуса»),
  верблюд-кадавр, пустынник, лошадь-зомби как в 1.21.11 (событиями поверх ванильной), наездники при спавне, копья у
  мобов, ездовые не тонут, лут. Клиент 1.21.11 скачан с разрешения владельца
  (`PrismLauncher\libraries\com\mojang\minecraft\1.21.11`, javap-набор `F:\minecraft-mods\_extract\vanilla-1.21.11`).
  Проверено на dev-сервере: verify.py 0 ошибок, самотест `tools/s05e_test.py` 57/57, режим «всё выключено» чистый.
  Проверено в игре (клон `1.12.2-test-05e`, OptiFine, сценарий `packautotest/scenarios/05e.json` PASS, FPS 130–240):
  копья в руках мобов и игрока, тычок попал по кадавру с 3 блоков, верблюд-кадавр с седлом и без, пустынник, броня на
  лошади-зомби, наутилус (взрослый, малыш, с седлом и бронёй), наутилус-зомби обычный и коралловый, значок эффекта.
  Не проверено в игре: езда на наутилусе и рывок, «Рывок» у игрока, таран на скаку, естественный спавн. Сервер со всей
  сборкой — за этапом M. Копия jar `F:\minecraft-mods\_05e-jar`, отчёт `docs/stages/05e.md`.
  **Вопрос владельцу (25.11):** броня наутилуса лежит только в `artifacts:ocean_shrine` (в 1.12 нет кораблей и кладов) —
  добавлять ли её в сокровища рыбалки. Поза таранного удара снята со сценарием
  `05e-charge.json` и флагом `-Dmodernbackports.05e.fakeCharge=true` (из клона `1.12.2-test-05e` флаг уже убран).
  Jar SHA-1 `b8a7d48e…` (ветка 315b82c), скриншоты `F:\minecraft-mods\_05e-screens`.

## Этап 08-everbright («Вечносвет») — готов к слиянию (25.11.2026)

Черновой PR 31 в modernbackports, ветка `stage/08-everbright`, wt `F:/minecraft-mods/wt/08-everbright`.
Измерение ID 1201, 1 Biome ID, сущности 2700–2706. Проверено: verify.py, `tools/s08everbright_test.py` (самотест 8/8, 1000 чанков,
каскад 0), общий сервер (каскад в 1201 = 0 от всех модов, лог `console_08everbright.log`), автотест клиента в `1.12.2-test-08`
(сценарии `08-everbright`, `08-storm`, `08-boss`, `08-boss-armor`). В Prism НЕ ставился — после этапа M.
Владельцу: один раз вручную сразиться с Призывателем (в одном прогоне автотеста кадры боя были чёрные, не воспроизвелось).
Следующее измерение этапа 08: порт 25676, ID 2750–2799. Отчёт: `docs/stages/08-everbright.md` в ветке.

## Этап 05d (дропы 1.21.5–1.21.9) — готов к слиянию (25.11.2026)

Черновой PR 29 в modernbackports, ветка `stage/05d`, wt `F:/minecraft-mods/wt/05d`, сущности 2600–2602, пакет 2610.
Варианты коров/свиней/куриц и цветные яйца, счастливый гаст/гастёнок/высохший гаст/упряжь, медный голем + медные сундуки
и статуи, полки, медные факел/фонари/цепи/решётки, растения 1.21.5, упавшие деревья. Медные инструменты/броня/кусочек/
конская броня не регистрируются при Thermal Foundation (`copper.skipIfThermal`), рецепт медного сундука — сундук +
медный блок (8 слитков вокруг сундука занято Iron Chests). Проверено: verify.py, самотест 59/59, своя копия сервера
`F:\minecraft-mods\_server-05d` (порт 25677: старый мир и новый, TPS 20, каскада от мода нет), автотест
`1.12.2-test-05d` PASS. В Prism НЕ ставился — после этапа M. Отчёт `docs/stages/05d.md` в ветке.
**Тайм-аут клиента при входе**: FTB Quests грузит 3989 файлов квестов в игровом потоке; дольше 30 с — «Превышено время
ожидания». В packautotest квесты в клонах теперь убираются (флаг `--ftb-quests`). Для 1.12.2-edit и общего сервера
предложено `-Dfml.readTimeout=120` (аргумент JVM) — ждёт согласия владельца.

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
