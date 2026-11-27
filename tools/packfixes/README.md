# packfixes

Мелкие исправления сборки (клиент и сервер, каждое выключается в `config/packfixes.cfg`).
Сборка: скопировать шаблон dynlight (build.gradle, gradle/, gradlew, settings.gradle) в `F:\minecraft-mods\packfixes`,
`./gradlew --no-daemon build` на JDK 25 из `.gradle/jdks`.

- `dynamicTreesThickRings` (клиент): с VintageFix `dynamic_resources` модели грузятся после сшивки атласа, и Dynamic Trees
  не успевает зарегистрировать текстуры колец толстых стволов — низ/верх ствола 3×3 фиолетово-чёрный. Мод регистрирует
  кольца всех `BlockBranchThick` в `TextureStitchEvent.Pre` (HIGH).
- `vanillaAxesFullSpeed` (клиент и сервер, должно совпадать): TreeChopper делит скорость рубки на половину числа брёвен,
  и деревянный/каменный/железный топор на большом дереве медленнее руки. Мод (BreakSpeed, LOWEST) возвращает этим трём
  топорам обычную скорость по дереву; дерево по-прежнему валится целиком.
