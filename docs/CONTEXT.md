# Контекст работы над сборкой

Сводка всего, что было сделано и решено. Полная переписка в [session-log.md](session-log.md).

## Исходные данные

- **Сборка:** самодельная, Minecraft 1.12.2, Forge 14.23.5.2860, Prism Launcher.
- **Железо:** i7-14650HX, RTX 5060 Laptop, экран 240 Гц.
- **Оригинальный инстанс:** `1.12.2(1)` («1.12.2»), его не трогали.
- **Тестовый инстанс:** `1.12.2-edit`, название «1.12.2 ТЕСТ (оптимизация)», группа «Тесты». Все изменения сделаны только здесь.
- Всё, что убрано или заменено, лежит в `%APPDATA%\PrismLauncher\instances\1.12.2-edit\removed_mods\` в пронумерованных папках, так что любой файл можно вернуть.

## Что сделано

### 1. Главная причина лагов: видеокарта
Игра шла на встроенной Intel. `javaw.exe` из `PrismLauncher\java\eclipse_temurin_jre8.0.492+9\bin\` переключён на RTX 5060 (Windows → Дисплей → Графика → Высокая производительность). В итоге **FPS ~50 → ~150**, тик сервера около 3 мс.

### 2. Чистка модов
| Папка в `removed_mods` | Что убрано | Почему |
|---|---|---|
| `1_junk` | Enchanting Plus для MC 1.5.1 (лежал под именем `corpse-library-Plus`), `litlaunch`, `IvToolkit`, `geckolib`, `omlib`, `bdlib` (и `llibrary`, потом возвращён для Mowzie's Mobs) | мёртвые файлы и библиотеки без зависимых модов |
| `2_duplicates` | Hardcore Revival, Inventory Tweaks | дубли PlayerRevive и Inventory Sorter |
| `3_lag` | Fast Leaf Decay | 39 срабатываний каскадной генерации, вызывал фризы при исследовании |
| `4_original_eplus` | оригинальный Enchanting Plus | заменён пропатченным |
| `5_original_tinkersaddons` | оригинальный Tinkers' Addons | заменён пропатченным |
| `6_custommobspawner` | CustomMobSpawner | отключал ванильный спавн (`doMobSpawning false`), а Mo'Creatures в сборке нет |
| `7_replaced_by_update` | CodeChickenLib 3.2.2 | обновлён до 3.2.3.358 ради Ender Storage |
| `8_castle_dungeons` | Castle Dungeons + его конфиг | замки с десятками спавнеров давали жуткие лаги, решено убрать совсем (19.11.2026) |
| `9_futureversions` | Future Versions + старый `futuremc.cfg` | дубль Future MC, заменён своим модом modernbackports с миграцией миров (этап 01b). Бэкап миров до миграции: `F:\minecraft-mods\_saves-backup-before-01b` (19.11.2026) |
| `12_futuremc_absorbed` | Future MC 0.2.21 + `config/futuremc` | всё его перенесено в modernbackports (этапы 11a–11h), миры переписываются при первой загрузке (этап 11z, 23.11.2026). Бэкап миров: `F:\minecraft-mods\_saves-backup-before-11z-futuremc` |
| `13_nb_moreblocks_absorbed` | Unseen's Nether Backport 0.7, Nether API 1.4.2, MoreBlocks 1.7.0 + `config/Unseens Nether Backport`, `config/nether_api`; старые `apotheosis/enchantments.cfg` и `veinminer/tools-and-blocks.json` | всё перенесено в modernbackports (этапы 11f–11h, 11z-nb), миры переписываются при первой загрузке (DataFixer 7, 23.11.2026). Бэкап миров: `F:\minecraft-mods\_saves-backup-before-11z-nb` |

Файлы с чужими именами переименованы по содержимому: TravelersTitles, Gobber, Artifacts, SwingThroughGrass, LargeOreDeposits.

### 3. Настройки
| Что | Было | Стало |
|---|---|---|
| Дальность прорисовки | 8 | 12 |
| Лимит FPS | 60 | 240 |
| Графика | быстрая | детальная, мипмапы 4 |
| OptiFine | — | Render Regions, Fast Render, Fast Math вкл; Smart Animations **выкл** (дублировал VanillaIcecreamFix и LoliASM) |
| LoliASM | — | выключена обработка крашей (её делает VanillaFix, был конфликт 20 мая) и отладочный лог |
| Память | 1–6 ГБ | ровно 6 ГБ (стоит `AlwaysPreTouch`) |
| JVM | — | убраны `UseFastAccessorMethods`, `AggressiveOpts`, `Xverify:none` |

### 4. Патчи модов (скрипты в `tools/`)
- **Enchanting Plus** (`EnchantingPlus-1.12.2-5.0.176-apoth2.jar`):
  - ползунок берёт максимальный уровень из конфига Apotheosis, а не ванильный. 8 мест в байткоде;
  - зачарование показывается, если оно подходит по ванильному правилу **или** предмет разрешает его сам (`canApplyAtEnchantingTable`). Теперь модовые кирки (Draconic и др.) получают Эффективность, Удачу и Шёлковое касание.
  - `config/apotheosis/enchantments.cfg`: 89 многоуровневых зачарований подняты до **50** (предел конфига 127), Ледоход оставлен 17. `config/eplus.cfg`: `costFactor` 1.0 → 0.25.
- **Tinkers' Addons** (`TinkersAddons-1.12.1-1.0.7-stackable.jar`): тулкиты можно ставить сколько угодно раз (до 1000). Железный и золотой дают +1 слот за каждый, алмазный +2, эндер +3.

### 5. Добавлено 24 мода
Biomes O' Plenty, Dynamic Trees + DT BoP, Quark + AutoRegLib, Mowzie's Mobs (+ llibrary), Atum 2, Waystones, Nature's Compass, Champions, Serene Seasons, Aquaculture 2, Immersive Engineering, Storage Drawers + Chameleon (CurseForge-версия, с Modrinth была dev-сборка и крашила), Iron Jetpacks, Ender Storage, Thermal Dynamics, VeinMiner, Clumps, AI Improvements, **Entity Culling + RenderLib** (не рисует мобов за стенами; работает с MixinBooter, MixinBootstrap не нужен).

Итог: игра грузится около 100 с, без вылетов.

### 6. Настройки мира (BoP)
Тип мира «Biomes O' Plenty», структуры ВКЛ. Land Mass Vanilla/Continents, Temperature и Rainfall Medium Zones, Biome Size Medium, Amplitude 1.1.

## Открытые вопросы

### Постройки, которые спавнят толпы мобов
Подробно в [structure-mods.md](structure-mods.md). Главный виновник, **Castle Dungeons**, удалён. Остались Mowzie's Mobs (деревни бараку), Raids Backport (аванпосты), Quark (Monster Boxes, пиратские корабли), Better Mineshafts.

### Что осталось
- [ ] Решить, какие правила против толп мобов включать: `maxEntityCramming 8`, реже деревни бараку, отключить Monster Boxes и пиратов Quark. Это меняет геймплей, поэтому ждёт решения.
- [ ] В мирах, где уже сгенерированы замки Castle Dungeons, они остались: это ванильные блоки и спавнеры. Новые замки больше не появятся.
- [x] Каскадная генерация TAIGA (373 случая на 950 чанков, главный источник фризов при исследовании): пять генераторов в `com/sosnitzka/taiga/util/Generator` ставили блоки без сдвига +8. Пропатчено `tools/taiga_patch/PatchTaiga.java` (22.11.2026), после патча 0 случаев на 1137 чанках. Оригинал в `removed_mods/10_original_taiga`.
- [ ] Остальная каскадная генерация на 1137 чанках: MrTJPCore (руды ProjectRed) 84, Quark 33, Dynamic Trees 24.
- [x] Невидимые трубы BuildCraft: OptiFine не мог загрузить ~800 спрайтов BuildCraft. Исправлено `useSwappableSprites=false` в `config/buildcraft/main.cfg` (20.11.2026), ошибок `Error uploading sprite single` больше нет.
- [ ] Трубы ProjectRed в мире рисуются плоскими цветными столбами (иконки в инвентаре нормальные). Проверяется настройками OptiFine (Fast Render, Render Regions, анизотропная фильтрация).
- [ ] Перенести всё в основную сборку. В старых мирах включить `/gamerule doMobSpawning true`.
- [ ] (опционально) spark для профилирования, если снова будут фризы.
