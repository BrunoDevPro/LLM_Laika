@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Instalando a Laika (so precisa fazer uma vez) ===
set PY=
python --version >nul 2>nul && set PY=python
if not defined PY ( py -3 --version >nul 2>nul && set "PY=py -3" )
if not defined PY (
  echo Python nao encontrado.
  echo Instale o Python 3.12 em https://www.python.org/downloads/
  echo e marque a opcao "Add python.exe to PATH" na instalacao.
  pause
  exit /b 1
)
%PY% --version
if not exist .venv\Scripts\python.exe %PY% -m venv .venv
if not exist .venv\Scripts\python.exe ( echo Erro ao criar o ambiente virtual. & pause & exit /b 1 )
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
  echo Erro ao instalar o PyTorch. Se o seu Python for muito novo,
  echo instale o Python 3.12, apague a pasta .venv e rode este arquivo de novo.
  pause
  exit /b 1
)
.venv\Scripts\python -m pip install tokenizers numpy
if errorlevel 1 ( echo Erro ao instalar as bibliotecas. & pause & exit /b 1 )
echo.
echo === Pronto! Agora abra o conversar.bat ===
pause
