@echo off
setlocal enabledelayedexpansion

:: --- Configurações Padrão ---
set "VENV_DIR=venv"
set "REQ_FILE=requirements.txt"
:: Pega o nome da pasta atual como nome do app
for %%I in ("%CD%") do set "APP_NAME=%%~nxI"

echo ====================================================
echo   Instalador/Compilador Generico Python
echo ====================================================

:: --- 1. Detectar Arquivo Principal ---
set "MAIN_FILE="
for %%f in (main.py app.py run.py index.py) do (
    if exist "%%f" (
        set "MAIN_FILE=%%f"
        goto :FOUND_MAIN
    )
)
:: Se nao encontrar nomes comuns, pega o primeiro .py (exceto setup.py)
for %%f in (*.py) do (
    if /I "%%f" neq "setup.py" (
        set "MAIN_FILE=%%f"
        goto :FOUND_MAIN
    )
)

:FOUND_MAIN
if "%MAIN_FILE%"=="" (
    echo [ERRO] Nenhum arquivo .py principal encontrado.
    echo Certifique-se de que o script esta na pasta do projeto.
    pause
    exit /b 1
)

echo.
echo Projeto: !APP_NAME!
echo Arquivo Principal: !MAIN_FILE!
set /p "USER_APP_NAME=Nome do executavel [!APP_NAME!]: "
if not "!USER_APP_NAME!"=="" set "APP_NAME=!USER_APP_NAME!"

:: --- 2. Ambiente Virtual ---
if not exist "!VENV_DIR!\Scripts\activate.bat" (
    echo.
    set /p "CREATE_VENV=Ambiente virtual nao encontrado. Criar agora? (s/n): "
    if /I "!CREATE_VENV!"=="s" (
        echo Criando ambiente virtual em .\!VENV_DIR!...
        python -m venv !VENV_DIR!
    )
)

if exist "!VENV_DIR!\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call !VENV_DIR!\Scripts\activate.bat
) else (
    echo [AVISO] Continuando sem ambiente virtual.
)

:: --- 3. Dependencias ---
if exist "!REQ_FILE!" (
    echo.
    echo Verificando dependencias (!REQ_FILE!)...
    python -m pip install --upgrade pip
    pip install -r !REQ_FILE!
)

:: --- 4. Compilacao ---
echo.
set /p "DO_COMPILE=Deseja gerar um executavel (.exe)? (s/n): "
if /I "!DO_COMPILE!"=="s" (
    echo Verificando PyInstaller...
    pip install pyinstaller

    :: Detectar pastas de dados comuns para incluir
    set "ADD_DATA_FLAGS="
    for %%d in (assets images static ffmpeg resources data icons) do (
        if exist "%%d\" (
            echo Incluindo pasta: %%d
            set "ADD_DATA_FLAGS=!ADD_DATA_FLAGS! --add-data "%%d;%%d""
        )
    )

    echo.
    echo Compilando !APP_NAME!...
    :: --noconsole e comum para apps GUI.
    pyinstaller --noconsole --onefile !ADD_DATA_FLAGS! --name "!APP_NAME!" "!MAIN_FILE!"

    if exist "dist\!APP_NAME!.exe" (
        echo.
        echo Movendo executavel para a raiz e limpando temporarios...
        move /y "dist\!APP_NAME!.exe" "."
        rmdir /s /q "build"
        rmdir /s /q "dist"
        del /q "!APP_NAME!.spec"
        echo Sucesso! '!APP_NAME!.exe' pronto na pasta raiz.
    ) else (
        echo [ERRO] Falha na compilacao. Verifique os logs acima.
    )
)

echo.
echo Processo finalizado.
pause
