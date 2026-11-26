# Патч Trinkets and Baubles под BaublesEX

Кнопка «назад в Baubles» (id 55) в контейнере Trinkets and Baubles 0.33.2 отправляет пакет
`baubles.common.network.PacketOpenBaublesInventory` из Baubles 1.5.2. В BaublesEX такого класса нет:
клик по кнопке роняет клиент (NoClassDefFoundError). Патч меняет пакет на `PacketOpen(Option.EXPANSION)` BaublesEX.

Сборка и запуск (JDK 8, ASM из библиотек Forge `org/ow2/asm/asm-debug-all/5.2`):

    javac -cp asm-debug-all-5.2.jar -d . PatchXatBex.java
    java -cp "asm-debug-all-5.2.jar;." PatchXatBex "Trinkets and Baubles-Forge-1.12.2-0.33.2.jar" "Trinkets and Baubles-Forge-1.12.2-0.33.2-bex.jar"

Ссылка Artifacts на `baubles/common/Config` патча не требует: её переписывает сам BaublesEX (TransformerRenderConfig).
