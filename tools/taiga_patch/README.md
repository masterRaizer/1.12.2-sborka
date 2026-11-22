# Патч TAIGA 1.3.4: каскадная генерация

`com/sosnitzka/taiga/util/Generator` ставит руды, метеориты и кубы породы в `chunkX*16 + nextInt(16)` без
ванильного сдвига +8, поэтому блоки на краю чанка подгружают ещё не созданный соседний чанк.
Патч добавляет `x += 8; z += 8` в начало `generateOreDescending`, `generateOreStoneVariant`, `generateOreBottom`,
`generateMeteor`, `generateCube`. `generateOre` с `WorldGenMinable` не трогается: там +8 уже есть.

Сборка и запуск (JDK 8, ASM из библиотек Forge-сервера `org/ow2/asm/asm-debug-all/5.2`):

    javac -cp asm-debug-all-5.2.jar -d . PatchTaiga.java
    java -cp "asm-debug-all-5.2.jar;." PatchTaiga taiga-1.12.2-1.3.4.jar taiga-1.12.2-1.3.4-nocascade.jar

Проверено на сервере со всей сборкой: 373 → 0 строк `Tinkers Alloying Addon loaded a new chunk`.
