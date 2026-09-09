#!/usr/bin/env bash
# Abre o simulador (Streamlit) com um único clique/comando — equivalente
# Linux do iniciar_simulador.bat (Windows). Cria o ambiente virtual e
# instala as dependências na primeira execução; nas seguintes, só abre.

cd "$(dirname "${BASH_SOURCE[0]:-$0}")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
    echo
    echo "[ERRO] python3 não foi encontrado no PATH."
    echo "Instale o Python 3 (ex.: 'sudo apt install python3 python3-venv' no Ubuntu/Debian)."
    echo
    read -rp "Pressione Enter para fechar..."
    exit 1
fi

if [ ! -x "venv/bin/streamlit" ]; then
    echo
    echo "Primeira execução: criando ambiente virtual e instalando dependências..."
    echo "Isso pode levar alguns minutos (o torch sozinho tem vários GB)."
    echo
    if ! python3 -m venv venv; then
        echo
        echo "[ERRO] Falha ao criar o ambiente virtual."
        echo
        read -rp "Pressione Enter para fechar..."
        exit 1
    fi
    if ! venv/bin/pip install -r requirements.txt; then
        echo
        echo "[ERRO] Falha ao instalar as dependências."
        echo
        read -rp "Pressione Enter para fechar..."
        exit 1
    fi
fi

echo
echo "Iniciando o simulador em http://localhost:8501 ..."
echo "O navegador deve abrir sozinho. Para encerrar o servidor, feche esta"
echo "janela ou pressione Ctrl+C."
echo

venv/bin/streamlit run app.py

echo
echo "Servidor encerrado."
read -rp "Pressione Enter para fechar..."
