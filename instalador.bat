@echo off
setlocal enabledelayedexpansion

:: --- Configurações ---
set "VENV_DIR=venv"
set "REQ_FILE=requirements.txt"
set "APP_NAME=ProcessadorDeImagens"
set "MAIN_FILE=main.py"

echo ====================================================
echo   Iniciando Compilacao: !APP_NAME!
echo ====================================================

:: 1. Criar Ambiente Virtual se nao existir
if not exist "!VENV_DIR!\Scripts\activate.bat" (
    echo [1/5] Criando ambiente virtual...
    python -m venv !VENV_DIR!
) else (
    echo [1/5] Ambiente virtual ja existe.
)

:: 2. Ativar e Instalar Dependencias
echo [2/5] Instalando/Atualizando dependencias...
call !VENV_DIR!\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r !REQ_FILE! --quiet

:: 3. Compilar com PyInstaller
echo [3/5] Gerando executavel (isso pode demorar um pouco)...
:: --noconsole (esconde o terminal ao abrir o app)
:: --onefile (gera apenas um .exe)
:: --clean (limpa o cache do pyinstaller)
pyinstaller --noconsole --onefile --clean --name "!APP_NAME!" "!MAIN_FILE!"

:: 4. Mover executavel e Limpar sujeira
echo [4/5] Organizando arquivos e limpando temporarios...
if exist "dist\!APP_NAME!.exe" (
    move /y "dist\!APP_NAME!.exe" "."
    
    :: Limpeza agressiva das pastas de build
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    if exist "!APP_NAME!.spec" del /q "!APP_NAME!.spec"
    
    echo.
    echo ====================================================
    echo   SUCESSO: !APP_NAME!.exe gerado na raiz!
    echo ====================================================
) else (
    echo.
    echo [ERRO] Falha ao gerar o executavel. Verifique as mensagens acima.
)

pause
