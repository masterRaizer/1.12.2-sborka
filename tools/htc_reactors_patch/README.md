# Патч htc_reactors 1.0.0 (HiTech reactors): блоки на выделенном сервере

Мод `htc_reactors` (VoidStudio, клиент McSkill HiTech) переведён на Java 8 инструментами `tools/ic2_hitech`
(`htc_reactors-1.0.0-j8.jar`). Своего серверного прокси у мода нет, `addproxy.py` дописал пустой
`ru/thetzddark/htc_reactors/server/ServerProxy`.

Ошибка: блоки, их ItemBlock и 4 TileEntity регистрирует `client/registry/RegistryBlocks.registerBlocks`
(`RegistryEvent.Register<Block>`), а подписывает его на `MinecraftForge.EVENT_BUS` только конструктор
`client/ClientProxy`. `CommonProxy` подписывает только `RegistryItems`, пустой `ServerProxy` — ничего. Поэтому на
выделенном сервере нет `htc_reactors:nuclear_reactor`, `nanite_complex`, `nanite_configuration_bench`,
`nanite_modification_station`, `reactor_casing` (3 вида), `nanite_casing` (2 вида) — 9 стаков, на которых
стоят 9 квестов и 10 достижений PackQuests. В одиночной игре всё есть (там работает ClientProxy).

Патч: в `ServerProxy.<init>` после `super()` добавлено `MinecraftForge.EVENT_BUS.register(new RegistryBlocks())`.
ClientProxy и CommonProxy не тронуты (на клиенте нет двойной подписки), имена реестра те же. В `RegistryBlocks` нет
`@SideOnly` и клиентских типов в сигнатурах; клиентские вызовы (`ModelLoader`, `ModelBakery`) только в теле
`registerBlockModel`, его вызывает лишь `ModelRegistryEvent` клиента.

Сборка и запуск (ASM из библиотек Forge-сервера `org/ow2/asm/asm-debug-all/5.2`, javac любой с `--release 8`):

    javac --release 8 -cp asm-debug-all-5.2.jar -d . PatchHtcReactors.java
    java -cp "asm-debug-all-5.2.jar;." PatchHtcReactors htc_reactors-1.0.0-j8.jar htc_reactors-1.0.0-j8-srvfix.jar

Вход SHA-1 `d2bdad8b31af5f316517a6c6cb85b57018d71a04`, выход `7b9b1ed2b3d0890834c17c652314edbf71d64137`
(отличается только `ServerProxy.class`).

Проверено на сервере со всей сборкой (новый мир): `packquests dump` — все 9 стаков блоков есть, `packquests check` —
ни одной проблемы с `htc_reactors`, все 4385 достижений загружены; `setblock` реактора, нанитного комплекса,
корпуса и верстака — «Block placed», `testforblock` находит; исключений нет, TPS 20.

MixedMod (`MixedMod-1.1.5-j8.jar`, тоже с пустым ServerProxy) проверен так же: его ClientProxy регистрирует только
клиентское (Discord, OBJLoader, HUD/подсказки), предметы регистрирует CommonProxy; реестр сервера и клиента совпадает
(11 предметов), патч не нужен.
