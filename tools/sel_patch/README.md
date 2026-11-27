# Патч Smooth Entity Light 4.0.4: свет предметов по яркости блока

Оригинал: CurseForge, проект 341845, файл 3024600 `SmoothEntityLight-4.0.4-MC1.12.2.jar`
(SHA-1 `762c4d5a0a963308cc0c6a064e3ca8ece8a73314`).

Что меняет:
- `ItemConfigHelper.getLightFromItemStack` вызывает `SELAutoLight.get`. Если предмета нет в списке
  «Light Items», а это блок, он светит яркостью своего блока (факел 14, светокамень 15). Только для
  списка «Light Items»; прожектор и «гаснет в воде» работают как раньше.
- В `@Mod` добавлено `acceptableRemoteVersions="*"`, чтобы клиент заходил на серверы без мода.
- Убраны `META-INF/fml_cache_*.json` (кэш аннотаций, иначе в нём старое значение `@Mod`).

Мод только клиентский, на сервер не ставить. Конфиг сборки `config/sel.cfg`:
`S:"Light Items"=glowstone_dust=10,lava_bucket=15` (блоки из списка убраны, они светят сами).

Сборка (JDK 25 из Gradle, `--release 8`; ASM `asm-debug-all-5.2` из кэша Gradle):

    javac --release 8 -d stubs-out $(find stubs -name '*.java')
    javac --release 8 -cp stubs-out -d auto src/lakmoore/sel/client/SELAutoLight.java
    javac --release 8 -cp asm-debug-all-5.2.jar -d tool PatchSel.java
    java -cp "asm-debug-all-5.2.jar;tool" PatchSel SmoothEntityLight-4.0.4-MC1.12.2.jar auto/lakmoore/sel/client/SELAutoLight.class SmoothEntityLight-4.0.4-MC1.12.2-autolight.jar

`stubs/` нужны только для компиляции (SRG-имена методов Minecraft), в jar не попадают.
