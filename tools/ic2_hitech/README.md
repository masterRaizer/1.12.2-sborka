# IC2 сервера McSkill HiTech в сборке

Владелец попросил (22.11.2026) поставить IC2 сервера HiTech 1.12.2 вместо нашего (ради очков-радара).
Их jar `industrialcraft-2-2.8.221-ex112-client.jar` (клиент HiTech, `C:\Users\avito\McSkill\clients\Hitech1122jvm21\mods`)
частично собран под Java 16 (44 класса, версия 60), а сборка на Java 8.

- `downgrade.py in.jar out.jar` — переводит классы > 52 на Java 8 прямо в байткоде: убирает NestHost/NestMembers
  (private у вложенных классов -> package), заменяет `invokedynamic StringConcatFactory` на вызов сгенерированного
  статического метода со StringBuilder (длина кода та же, StackMapTable не трогается), `IntBuffer.rewind()` -> Buffer.
- `apirefs.py` + `Check8.java` — проверка, что переведённые классы зовут только API Java 8.
- `ic2refs.py ic2.jar <папки mods>` — какие моды ссылаются на классы/методы IC2, которых нет в новом jar.
- `patch_invslot.py` — Advanced Solar Panels 4.3.0 под конструкторы InvSlot нового IC2
  (TileEntityInventory -> IInventorySlotHolder). Advanced Machines чинит `advmachinespatch-1.0.jar` (Su5eD).

Проверено: тестовый сервер (загрузка, TPS 20, генерация 1200 чанков без каскада от IC2, предметы IC2 в копии мира),
клиент (автотест `packautotest/scenarios/hitech-ic2-xray.json`: радар, шлемы, реактор, консервер, РИТЭГ, IVSU/UVSU,
трансформаторы IV/UV, зарядная плита, ASP, Advanced Machines, пенобетон).
Окно руд — мод ResourcesRadar (клиент HiTech); серверную часть, без которой радар не включается, даёт свой мод
`hitechcompat` (F:\minecraft-mods\hitechcompat).
