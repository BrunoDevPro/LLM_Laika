@echo off
chcp 65001 >nul
cd /d "%~dp0"
if "%~1"=="" (
  echo Arraste o arquivo laika_rag.db para cima deste instalar_indice.bat.
  pause
  exit /b 1
)
if /i not "%~x1"==".db" (
  echo Esse arquivo nao e o indice. Arraste o laika_rag.db.
  pause
  exit /b 1
)
if not exist "data\rag" mkdir "data\rag"
echo Movendo o indice para data\rag ...
move /y "%~1" "data\rag\laika_rag.db" >nul
if errorlevel 1 ( echo Nao consegui mover o arquivo. & pause & exit /b 1 )
if exist data\rag\laika_rag_mini.db del data\rag\laika_rag_mini.db
echo Pronto! A busca completa sera usada no proximo conversar.bat.
pause
