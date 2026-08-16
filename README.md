# Gêmeo Digital de Sistemas de Compressão Offshore

Este repositório reúne dois artefatos que andam juntos:

1. **O livro** — *Gêmeo Digital de Sistemas de Compressão Offshore: Diretrizes
   Técnicas, Modelagem e Implementação* (`compressores.tex`/`compressores.pdf`),
   primeiro volume da coleção *Enciclopédia de Máquinas Rotodinâmicas*.
   Cobre a física de um trem de compressão de ar offshore (compressor de
   parafuso oil-free em dois estágios, tratamento, armazenamento) e a
   metodologia de Gêmeo Digital que se constrói sobre essa física — EKF, VAE,
   PIML, MPC, PSO, identificação por problema inverso, catálogo de mecanismos
   de falha e painel supervisório de frota.
2. **O aplicativo** (pasta `aplicativo/`) — um simulador web que implementa,
   em código real, boa parte do que o livro descreve. Não é pseudocódigo: toda
   equação do app cita o número correspondente no livro, e os cinco
   algoritmos da Parte II rodam de verdade sobre dados simulados.

Este README foca no aplicativo — como ele funciona, para que serve e como
prepará-lo para rodar. Para o livro, veja `compressores.pdf` diretamente ou
compile `compressores.tex` com `pdflatex` (3 passagens).

## O que o aplicativo faz

Simula o trem completo de ar comprimido de uma instalação offshore:

```
filtro de admissão → estágio LP → intercooler → estágio HP → aftercooler →
separador de condensado → secador PSA (adsorção) → vaso pulmão → rede
```

e expõe, na mesma interface, os cinco algoritmos de Gêmeo Digital da Parte II
do livro, cada um interativo e rastreável a uma seção específica:

- **EKF** (Filtro de Kalman Estendido) — estima folga interna e incrustação
  do intercooler a partir de medições ruidosas, incluindo uma variante de
  **estado aumentado** que identifica o coeficiente de vazamento $K$ como
  problema inverso (Cap. 28).
- **VAE** (Autoencoder Variacional) — detecção de anomalia por erro de
  reconstrução sobre 28 variáveis monitoradas.
- **PIML** (Physics-Informed ML) — rede substituta que respeita conservação
  de massa/energia, com uma segunda variante que identifica o mesmo $K$ acima
  por um caminho offline (Cap. 23.8).
- **MPC** (Controle Preditivo) — decide o setpoint de pressão antecipando
  demanda futura, comparado contra controle reativo.
- **PSO** (Otimização por Enxame) — busca o setpoint de pressão que minimiza
  consumo específico sob restrição de autonomia do vaso.

## Para que serve

Para explorar como o sistema físico responde a mudanças de condição (pressão
de rede, temperatura ambiente, demanda) e, principalmente, para ver os
algoritmos de Gêmeo Digital em ação sobre esse sistema — sem precisar de dados
reais de planta, que este projeto não possui. É uma ferramenta de estudo e
demonstração, não um sistema de operação contínua (essa lacuna, e o desenho
de um painel supervisório de frota para fechá-la, está descrita no
Capítulo 26 do livro, mas sem implementação de referência no app ainda).

## Como funciona (visão rápida)

- **`compressor_sim/`** — motor de cálculo puro (sem Streamlit), um módulo
  por subsistema/algoritmo. Cada função cita a equação do livro que
  implementa.
- **`app.py`** — interface Streamlit, 6 abas:
  - **⚙️ Operação estática** / **📈 Dinâmica temporal** / **🌀 Secagem PSA** —
    resultados do trem físico num ponto de operação, ao longo do tempo, e no
    ciclo do secador, respectivamente.
  - **🧠 Gêmeo Digital (EKF/PSO)** — os cinco algoritmos acima, cada um em
    sua própria seção.
  - **🎛️ Configurações** — geometria de equipamento e hiperparâmetros de
    algoritmo (o que normalmente não muda de uma análise para a outra).
  - **📂 Dados Medidos** — upload de referência (.xlsx/.csv) com a
    instrumentação real de uma planta, comparada contra a matriz de
    instrumentação do livro (Tabela 18.1, 9 pontos A–I).
- A barra lateral traz só as **condições de operação do momento**
  (temperatura ambiente, pressão de rede, demanda etc.) — tudo o que muda
  raramente vive na aba Configurações.

Detalhes de arquitetura, decisões de projeto e o guia módulo a módulo estão
em `aplicativo/IMPLEMENTACAO.md` e `aplicativo/GUIA_CODIGO.md`.

## Como preparar para rodar

### Pré-requisitos

- **Python 3.10 ou superior** ([python.org](https://www.python.org/downloads/))
- **Git** (para clonar o repositório)

O `requirements.txt` inclui `torch` (para os módulos VAE/PIML) — o instalador
padrão do PyPI já traz suporte a GPU NVIDIA embutido quando disponível, sem
nenhuma configuração extra em Linux ou Windows; sem GPU, roda em CPU
normalmente.

### Linux / macOS

```bash
git clone https://github.com/MMMejias39/compressores_parafuso.git
cd compressores_parafuso/aplicativo

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

streamlit run app.py
```

### Windows (PowerShell)

```powershell
git clone https://github.com/MMMejias39/compressores_parafuso.git
cd compressores_parafuso\aplicativo

python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

streamlit run app.py
```

Duas armadilhas comuns no Windows:

- Se `python` não for reconhecido, use o launcher `py` (`py -m venv venv`) —
  vem com o instalador oficial do Python para Windows.
- Se a ativação do venv falhar com um erro de política de execução do
  PowerShell, rode antes (numa sessão do PowerShell, não precisa admin):
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```

Em ambos os sistemas, o Streamlit abre automaticamente o navegador em
<http://localhost:8501> (se não abrir sozinho, acesse esse endereço
manualmente). Para encerrar, `Ctrl+C` no terminal onde o comando está
rodando.

### Testes

Com o venv já ativado (mesma sintaxe nos dois sistemas):

```bash
pytest tests/
```

71 testes de sanidade física — cada um verifica que uma grandeza se move na
direção fisicamente esperada quando um parâmetro muda.

## Documentação mais profunda

Dentro de `aplicativo/`:

- **`README.md`** — instruções de instalação/execução equivalentes às acima,
  com a estrutura de arquivos completa.
- **`IMPLEMENTACAO.md`** — arquitetura, filosofia de projeto, decisões e por quê.
- **`GUIA_CODIGO.md`** — o que cada arquivo faz, módulo por módulo.
- **`MANUTENCAO.md`** — como estender, testar e manter o projeto.

E na raiz do repositório:

- **`CONTEXTO.md`** / **`CONTEXTO_app.md`** — histórico cronológico de
  desenvolvimento do livro e do app, respectivamente (achados, bugs,
  decisões).
