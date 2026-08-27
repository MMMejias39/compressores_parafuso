# Simulador de Sistema de Ar Comprimido — Compressor de Parafuso

Aplicativo web (Streamlit) que simula o trem completo de ar comprimido offshore
descrito no livro **"Gêmeo Digital de Sistemas de Compressão Offshore"**
(`../compressores.tex`):

filtro de admissão → estágio LP → intercooler → estágio HP → aftercooler →
separador de condensado → secador PSA → vaso pulmão/rede.

Todas as equações vêm do livro — o número de cada uma está citado no código
(ex.: `# Eq. 5.5 — trabalho politrópico por estágio`).

## Instalação

**Linux / macOS:**
```bash
cd aplicativo
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
cd aplicativo
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

## Execução

**Linux / macOS:**
```bash
cd aplicativo
venv/bin/streamlit run app.py
```

**Windows (PowerShell):**
```powershell
cd aplicativo
venv\Scripts\streamlit run app.py
```

**Windows (um clique):** dê duplo clique em `iniciar_simulador.bat`, dentro
desta pasta. Na primeira execução ele cria o ambiente virtual e instala as
dependências sozinho (pode levar alguns minutos, o torch é grande); nas
execuções seguintes só abre o servidor direto. Não precisa abrir terminal
nem digitar comando nenhum.

**Linux (um clique):** `iniciar_simulador.sh` faz o mesmo (portável — não
precisa editar nada, funciona em qualquer clone). Para rodar direto do
terminal: `./iniciar_simulador.sh`. Para um ícone clicável de verdade no
GNOME/KDE/etc., há também `iniciar_simulador.desktop` — mas esse arquivo
tem o caminho absoluto do `Exec=` fixado para esta máquina (por isso não
está versionado no git); se clonar o repositório num caminho diferente,
edite as linhas `Exec=`/`Path=` desse arquivo antes de usá-lo. Para
instalá-lo no menu de aplicativos do GNOME:
```bash
ln -sf "$(pwd)/iniciar_simulador.desktop" ~/.local/share/applications/
update-desktop-database ~/.local/share/applications
```

Abre no navegador em <http://localhost:8501>.

## Testes

**Linux / macOS:**
```bash
cd aplicativo
venv/bin/pytest tests/
```

**Windows (PowerShell):**
```powershell
cd aplicativo
venv\Scripts\pytest tests/
```

## Documentação

- **`IMPLEMENTACAO.md`** — arquitetura, filosofia de projeto, decisões e o porquê delas.
- **`GUIA_CODIGO.md`** — o que cada arquivo faz, módulo por módulo.
- **`MANUTENCAO.md`** — como estender, testar e manter o projeto.
- **`../CONTEXTO_app.md`** — histórico cronológico de sessões de desenvolvimento (achados, bugs, decisões — o "diário" por trás dos três documentos acima).

## Estrutura

```
aplicativo/
├── compressor_sim/
│   ├── constantes.py       # propriedades do ar e defaults (origem citada)
│   ├── nucleo.py           # estágios de compressão, motor, hood, carcaça, psicrometria
│   ├── subsistemas.py      # intercooler, separador, secador PSA, vaso/rede
│   ├── sistema.py          # cascata completa: simular(params) -> resultados
│   ├── dinamica.py         # simulação transiente do vaso/rede (VSD ou carga/alívio)
│   ├── psa_ciclo.py        # rodízio de N torres do secador PSA
│   ├── pi_telemetry.py     # telemetria OSIsoft PI, 26+ tags industriais (Tabela 18.1)
│   ├── treinamento_falhas.py # classificador m̂_falha (Eq. 29.2), arena de treinamento operacional
│   ├── frota_supervisorio.py # supervisório de frota offshore (N_frota), HI composto e RUL bayesiano
│   ├── ekf.py              # Filtro de Kalman Estendido (+ estado aumentado, Cap. 28.1)
│   ├── vae.py              # Autoencoder Variacional (detecção de anomalia)
│   ├── piml.py             # Physics-Informed ML (+ problema inverso, Cap. 23.8)
│   ├── mpc.py              # Controle Preditivo Baseado em Modelo
│   ├── pso.py              # Otimização por Enxame de Partículas
│   ├── calib_lm.py         # Calibração via Levenberg-Marquardt
│   └── cenarios_falha.py   # 10 cenários de falha isolada (Cap. 28.3)
├── tests/
│   ├── test_simulador.py   # testes de sanidade da física e dos algoritmos de IA
│   └── test_pi_treinamento.py # testes de telemetria PI, diagnóstico e supervisório
└── exemplos/
    └── instrumentacao_exemplo.csv # exemplo dos 9 pontos de medição da Tabela 18.1
```

Ver `GUIA_CODIGO.md` para o que cada módulo faz em detalhe.

## Convenções

- SI; pressões **absolutas** (Pa/bar), temperaturas em K no cálculo e °C na UI.
- Forma canônica de potência de estágio: **politrópica (Eq. 5.5)**.
- Parâmetros que o livro não fecha numericamente (vazão FAD, UA, volume do
  vaso etc.) estão marcados como "assumido" em `constantes.py` e na interface.

## Uso como biblioteca

```python
from compressor_sim import parametros_default, simular

res = simular(parametros_default() | {"pi_total": 9.0})
print(res["kpis"]["spc"], res["potencias"]["w_total"])
```
