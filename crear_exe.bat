@echo off
title Generador de Ejecutable Bot AGX
echo =============================================
echo    GENERANDO EJECUTABLE DEL BOT AGX
echo =============================================
echo.
echo 1. Limpiando versiones anteriores...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist *.spec del /q *.spec

echo.
echo 2. Verificando instalacion de PyInstaller...
python -m pip install pyinstaller --quiet

echo.
echo 3. Creando el archivo EXE (esto puede tardar un minuto)...
python -m PyInstaller --onefile --name "Bot_AGX_Orquestador" --hidden-import=mapeo_8000 --hidden-import=mapeo_8200 main.py

echo.
echo =============================================
echo    PROCESO TERMINADO
echo    Busca tu archivo en la carpeta "dist"
echo =============================================
pause
