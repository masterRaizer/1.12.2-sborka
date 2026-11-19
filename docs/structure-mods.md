# Моды, чьи постройки могут спавнить толпы мобов

Проверено по активным модам и конфигам тестовой сборки.

## Обычный мир

| Мод | Что генерирует | Опасность | Конфиг |
|---|---|---|---|
| **Castle Dungeons** | замки с десятками ванильных спавнеров (каждый держит до 6 мобов) | 🔴 главная причина | `config/castle_dungeons/`: `section-size` 24, чем больше, тем реже замки |
| **Mowzie's Mobs** | деревни бараку (сразу пачка туземцев), логова Wroughtnaut и Frostmaw | 🟠 | `config/mowziesmobs.cfg`: `generation_frequency=12`, `generation_chance=0.8` (0 = выключить) |
| **Raids Backport** | аванпосты разбойников, патрули, рейды | 🟠 | `config/raids/outposts.cfg`, `patrols.cfg` |
| **Quark** | пиратские корабли, Monster Boxes в пещерах, разнообразные данжи | 🟡 | `config/quark.cfg`: `Pirate ships`, `Monster boxes`, `Varied dungeons` (все `true`) |
| **Better Mineshafts** | большие шахты с пещерными пауками | 🟡 | `config/bettermineshafts-1_12_2.cfg` |

## Другие измерения
- **Atum**: пирамиды и данжи (только измерение Atum).
- **Unseen's Nether Backport**: бастионы и структуры Незера.

## Усиливают мобов
- **Champions**: элитные мобы, в замке со спавнерами это особенно тяжело.

## Уже стоит против лагов
- **Entity Culling**: не рисует невидимых мобов (FPS).
- **AI Improvements**: облегчает ИИ мобов (TPS).
- **Clumps**: склеивает сферы опыта.

## Рычаги (не применены, ждут решения)
1. `/gamerule maxEntityCramming 8` (по умолчанию 24).
2. Castle Dungeons: `section-size` 24 → 32–40.
3. Mowzie's Mobs: `generation_frequency` бараку 12 → 30–40 или 0.
4. Quark: `Monster boxes=false`, `Pirate ships=false`.

Изменения генерации действуют только на **новые** чанки.
