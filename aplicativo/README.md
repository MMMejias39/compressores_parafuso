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

## Documentação

- **`IMPLEMENTACAO.md`** — arquitetura, filosofia de projeto, decisões e o porquê delas.
- **`GUIA_CODIGO.md`** — o que cada arquivo faz, módulo por módulo.
- **`MANUTENCAO.md`** — como estender, testar e manter o projeto.
- **`../CONTEXTO_app.md`** — histórico cronológico de sessões de desenvolvimento (achados, bugs, decisões — o "diário" por trás dos três documentos acima).

## Estrutura

```
aplicativo/
├── app.py                  # interface Streamlit (4 abas — ver GUIA_CODIGO.md)
├── compressor_sim/
│   ├── constantes.py       # propriedades do ar e defaults (origem citada)
│   ├── nucleo.py           # estágios de compressão, motor, hood, carcaça, psicrometria
│   ├── subsistemas.py      # intercooler, separador, secador PSA, vaso/rede
│   ├── sistema.py          # cascata completa: simular(params) -> resultados
│   ├── dinamica.py         # simulação transiente do vaso/rede (VSD ou carga/alívio)
│   ├── psa_ciclo.py        # rodízio de N torres do secador PSA
│   ├── ekf.py               # Filtro de Kalman Estendido (+ estado aumentado, Cap. 28.1)
│   ├── vae.py               # Autoencoder Variacional (detecção de anomalia)
│   ├── piml.py              # Physics-Informed ML (+ problema inverso, Cap. 23.8)
│   ├── mpc.py               # Controle Preditivo Baseado em Modelo
│   └── pso.py               # Otimização por Enxame de Partículas
├── tests/test_simulador.py # testes de sanidade (pytest, 71 testes)
└── requirements.txt
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
