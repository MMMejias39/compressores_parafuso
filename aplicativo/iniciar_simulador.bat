@echo off
setlocal enabledelayedexpansion
title Simulador de Compressor de Parafuso
cd /d "%~dp0"

REM --- Localiza o Python: tenta "python", cai para o launcher "py" ---
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo.
        echo [ERRO] Python nao foi encontrado no PATH.
        echo Instale em https://www.python.org/downloads/
        echo Durante a instalacao, marque a opcao "Add python.exe to PATH".
        echo.
        pause
        exit /b 1
    )
)

REM --- Primeira execucao: cria o ambiente virtual e instala as dependencias ---
if not exist "venv\Scripts\streamlit.exe" (
    echo.
    echo Primeira execucao: criando ambiente virtual e instalando dependencias...
    echo Isso pode levar alguns minutos ^(o torch sozinho tem varios GB^).
    echo.
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo.
        echo [ERRO] Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
    call venv\Scripts\pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERRO] Falha ao instalar as dependencias.
        pause
        exit /b 1
    )
)

echo.
echo Iniciando o simulador em http://localhost:8501 ...
echo O navegador deve abrir sozinho. Para encerrar o servidor, feche esta
echo janela ou pressione Ctrl+C.
echo.
call venv\Scripts\streamlit run app.py

echo.
echo Servidor encerrado.
pause
