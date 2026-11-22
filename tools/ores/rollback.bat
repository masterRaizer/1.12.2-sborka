@echo off
chcp 65001 >nul
rem Откат правок генерации руд (тред «Руды», 22.11.2026).
rem Запуск: rollback.bat            - откатить инстанс 1.12.2-edit
rem         rollback.bat server     - откатить тестовый сервер
rem         rollback.bat <папка config> - откатить любую папку config
rem Игра/сервер должны быть закрыты. Уже созданные чанки не меняются: откат влияет только на новые чанки.
set "CFG=%APPDATA%\PrismLauncher\instances\1.12.2-edit\minecraft\config"
if /I "%~1"=="server" set "CFG=F:\minecraft-mods\_server-1.12.2\config"
if not "%~1"=="" if /I not "%~1"=="server" set "CFG=%~1"
echo Откат в "%CFG%"
if exist "%CFG%\cofh\world\01_thermalfoundation_ores.json.bak-ores" ( copy /Y "%CFG%\cofh\world\01_thermalfoundation_ores.json.bak-ores" "%CFG%\cofh\world\01_thermalfoundation_ores.json" >nul && del "%CFG%\cofh\world\01_thermalfoundation_ores.json.bak-ores" && echo   вернул cofh/world/01_thermalfoundation_ores.json ) else ( echo   нет копии cofh/world/01_thermalfoundation_ores.json )
if exist "%CFG%\adlods\VanillaGen\coal.cfg.bak-ores" ( copy /Y "%CFG%\adlods\VanillaGen\coal.cfg.bak-ores" "%CFG%\adlods\VanillaGen\coal.cfg" >nul && del "%CFG%\adlods\VanillaGen\coal.cfg.bak-ores" && echo   вернул adlods/VanillaGen/coal.cfg ) else ( echo   нет копии adlods/VanillaGen/coal.cfg )
if exist "%CFG%\adlods\VanillaGen\iron.cfg.bak-ores" ( copy /Y "%CFG%\adlods\VanillaGen\iron.cfg.bak-ores" "%CFG%\adlods\VanillaGen\iron.cfg" >nul && del "%CFG%\adlods\VanillaGen\iron.cfg.bak-ores" && echo   вернул adlods/VanillaGen/iron.cfg ) else ( echo   нет копии adlods/VanillaGen/iron.cfg )
if exist "%CFG%\adlods\VanillaGen\gold.cfg.bak-ores" ( copy /Y "%CFG%\adlods\VanillaGen\gold.cfg.bak-ores" "%CFG%\adlods\VanillaGen\gold.cfg" >nul && del "%CFG%\adlods\VanillaGen\gold.cfg.bak-ores" && echo   вернул adlods/VanillaGen/gold.cfg ) else ( echo   нет копии adlods/VanillaGen/gold.cfg )
if exist "%CFG%\adlods\VanillaGen\redstone.cfg.bak-ores" ( copy /Y "%CFG%\adlods\VanillaGen\redstone.cfg.bak-ores" "%CFG%\adlods\VanillaGen\redstone.cfg" >nul && del "%CFG%\adlods\VanillaGen\redstone.cfg.bak-ores" && echo   вернул adlods/VanillaGen/redstone.cfg ) else ( echo   нет копии adlods/VanillaGen/redstone.cfg )
if exist "%CFG%\adlods\VanillaGen\diamond.cfg.bak-ores" ( copy /Y "%CFG%\adlods\VanillaGen\diamond.cfg.bak-ores" "%CFG%\adlods\VanillaGen\diamond.cfg" >nul && del "%CFG%\adlods\VanillaGen\diamond.cfg.bak-ores" && echo   вернул adlods/VanillaGen/diamond.cfg ) else ( echo   нет копии adlods/VanillaGen/diamond.cfg )
if exist "%CFG%\adlods\VanillaGen\lapis.cfg.bak-ores" ( copy /Y "%CFG%\adlods\VanillaGen\lapis.cfg.bak-ores" "%CFG%\adlods\VanillaGen\lapis.cfg" >nul && del "%CFG%\adlods\VanillaGen\lapis.cfg.bak-ores" && echo   вернул adlods/VanillaGen/lapis.cfg ) else ( echo   нет копии adlods/VanillaGen/lapis.cfg )
if exist "%CFG%\adlods\VanillaGen\emerald.cfg.bak-ores" ( copy /Y "%CFG%\adlods\VanillaGen\emerald.cfg.bak-ores" "%CFG%\adlods\VanillaGen\emerald.cfg" >nul && del "%CFG%\adlods\VanillaGen\emerald.cfg.bak-ores" && echo   вернул adlods/VanillaGen/emerald.cfg ) else ( echo   нет копии adlods/VanillaGen/emerald.cfg )
if exist "%CFG%\IC2.ini.bak-ores" ( copy /Y "%CFG%\IC2.ini.bak-ores" "%CFG%\IC2.ini" >nul && del "%CFG%\IC2.ini.bak-ores" && echo   вернул IC2.ini ) else ( echo   нет копии IC2.ini )
if exist "%CFG%\mekanism.cfg.bak-ores" ( copy /Y "%CFG%\mekanism.cfg.bak-ores" "%CFG%\mekanism.cfg" >nul && del "%CFG%\mekanism.cfg.bak-ores" && echo   вернул mekanism.cfg ) else ( echo   нет копии mekanism.cfg )
if exist "%CFG%\immersiveengineering.cfg.bak-ores" ( copy /Y "%CFG%\immersiveengineering.cfg.bak-ores" "%CFG%\immersiveengineering.cfg" >nul && del "%CFG%\immersiveengineering.cfg.bak-ores" && echo   вернул immersiveengineering.cfg ) else ( echo   нет копии immersiveengineering.cfg )
if exist "%CFG%\ProjectRed.cfg.bak-ores" ( copy /Y "%CFG%\ProjectRed.cfg.bak-ores" "%CFG%\ProjectRed.cfg" >nul && del "%CFG%\ProjectRed.cfg.bak-ores" && echo   вернул ProjectRed.cfg ) else ( echo   нет копии ProjectRed.cfg )
if exist "%CFG%\forestry\common.cfg.bak-ores" ( copy /Y "%CFG%\forestry\common.cfg.bak-ores" "%CFG%\forestry\common.cfg" >nul && del "%CFG%\forestry\common.cfg.bak-ores" && echo   вернул forestry/common.cfg ) else ( echo   нет копии forestry/common.cfg )
if exist "%CFG%\AppliedEnergistics2\AppliedEnergistics2.cfg.bak-ores" ( copy /Y "%CFG%\AppliedEnergistics2\AppliedEnergistics2.cfg.bak-ores" "%CFG%\AppliedEnergistics2\AppliedEnergistics2.cfg" >nul && del "%CFG%\AppliedEnergistics2\AppliedEnergistics2.cfg.bak-ores" && echo   вернул AppliedEnergistics2/AppliedEnergistics2.cfg ) else ( echo   нет копии AppliedEnergistics2/AppliedEnergistics2.cfg )
if exist "%CFG%\brandon3055\DraconicEvolution.cfg.bak-ores" ( copy /Y "%CFG%\brandon3055\DraconicEvolution.cfg.bak-ores" "%CFG%\brandon3055\DraconicEvolution.cfg" >nul && del "%CFG%\brandon3055\DraconicEvolution.cfg.bak-ores" && echo   вернул brandon3055/DraconicEvolution.cfg ) else ( echo   нет копии brandon3055/DraconicEvolution.cfg )
if exist "%CFG%\gobber.cfg.bak-ores" ( copy /Y "%CFG%\gobber.cfg.bak-ores" "%CFG%\gobber.cfg" >nul && del "%CFG%\gobber.cfg.bak-ores" && echo   вернул gobber.cfg ) else ( echo   нет копии gobber.cfg )
if exist "%CFG%\modernbackports\02a.cfg.bak-ores" ( copy /Y "%CFG%\modernbackports\02a.cfg.bak-ores" "%CFG%\modernbackports\02a.cfg" >nul && del "%CFG%\modernbackports\02a.cfg.bak-ores" && echo   вернул modernbackports/02a.cfg ) else ( echo   нет копии modernbackports/02a.cfg )
if exist "%CFG%\cofh\world\05_pack_vanilla_ores.json" ( del "%CFG%\cofh\world\05_pack_vanilla_ores.json" && echo   удалил cofh/world/05_pack_vanilla_ores.json )
if exist "%CFG%\cofh\world\05_pack_forestry_ores.json" ( del "%CFG%\cofh\world\05_pack_forestry_ores.json" && echo   удалил cofh/world/05_pack_forestry_ores.json )
if exist "%CFG%\cofh\world\05_pack_projectred_ores.json" ( del "%CFG%\cofh\world\05_pack_projectred_ores.json" && echo   удалил cofh/world/05_pack_projectred_ores.json )
if exist "%CFG%\cofh\world\05_pack_draconic_ores.json" ( del "%CFG%\cofh\world\05_pack_draconic_ores.json" && echo   удалил cofh/world/05_pack_draconic_ores.json )
if exist "%CFG%\cofh\world\05_pack_gobber_ores.json" ( del "%CFG%\cofh\world\05_pack_gobber_ores.json" && echo   удалил cofh/world/05_pack_gobber_ores.json )
echo Готово.
pause
