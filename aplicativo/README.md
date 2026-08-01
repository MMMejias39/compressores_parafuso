# Simulador de Sistema de Ar Comprimido — Compressor de Parafuso

Aplicativo web (Streamlit) que simula o trem completo de ar comprimido offshore
descrito no livro **"Gêmeo Digital de Sistemas de Compressão Offshore"**
(`../compressores.tex`):

filtro de admissão → estágio LP → intercooler → estágio HP → aftercooler →
separador de condensado → secador PSA → vaso pulmão/rede.

Todas as equações vêm do livro — o número de cada uma está citado no código
(ex.: `# Eq. 5.5 — trabalho politrópico por estágio`).

## Instalação

```bash
cd aplicativo
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Execução

```bash
cd aplicativo
venv/bin/streamlit run app.py
```

Abre no navegador em <http://localhost:8501>.

## Testes

```bash
cd aplicativo
venv/bin/pytest tests/
```

## Estrutura

```
aplicativo/
├── app.py                  # interface Streamlit (ponto de entrada)
├── compressor_sim/
│   ├── constantes.py       # propriedades do ar e defaults (origem citada)
│   ├── nucleo.py           # estágios de compressão + psicrometria
│   ├── subsistemas.py      # intercooler, separador, secador PSA, vaso/rede
│   └── sistema.py          # cascata completa: simular(params) -> resultados
├── tests/test_simulador.py # testes de sanidade (pytest)
└── requirements.txt
```

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
