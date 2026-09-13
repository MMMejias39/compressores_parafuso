# Gêmeo Digital de Sistemas de Compressão Offshore (Digital Twin & Industrial AI)

Este repositório reúne o ecossistema completo de engenharia, modelagem matemática, código-fonte e inteligência artificial industrial:

1. **O livro — Volume 0** — *Notações e Cálculo Básico* (`Volume_0_Notacoes_e_Calculo.tex`/`.pdf`). Pré-requisito matemático da coleção: notação e linguagem simbólica, análise dimensional, funções, vetores, cálculo diferencial e integral, equações diferenciais e séries/aproximações.
2. **O livro — Volume I** — *Fundamentos de Mecânica do Contínuo, Termofluidos e Sistemas de Medição: Bases Teóricas para Máquinas Rotodinâmicas* (`Volume_I_Fundamentos.tex`/`.pdf`). Reúne os fundamentos de mecânica dos sólidos e fluidos, termodinâmica aplicada, psicrometria, transferência de calor, eletricidade industrial, dinâmica de rotores e instrumentação.
3. **O livro — Volume II** — *Gêmeo Digital de Sistemas de Compressão Offshore: Diretrizes Técnicas, Modelagem e Implementação* (`compressores.tex`/`compressores.pdf`). Cobre a física rigorosa de um trem de compressão de ar de parafuso duplo *oil-free* em dois estágios, tratamento térmico/adsorção (PSA), armazenamento em vasos de pressão e a metodologia de Gêmeo Digital (EKF, VAE, PIML, MPC, PSO, identificação por problema inverso, catálogo de falhas causais e supervisório de frota).
4. **Aplicações de Simulação & Gêmeo Digital**:
   - **Versão Rust 2.0 (`compressor2/`)**: Implementação industrial de alta performance em Rust (Axum + Vanilla JS/Tailwind/Chart.js). Servidor assíncrono nativo, tempo de resposta sub-milissegundo, conformidade visual **WCAG 2.1 AA** (auditoria automatizada via Chrome Headless), arquitetura dinâmica de trens de compressores, 7 nós termodinâmicos, 26+ tags industriais OSIsoft PI, arena de treinamento de operadores com parecer causal e conformidade estrutural com **ASME VIII Div. 1**.
   - **Versão Python (`aplicativo/`)**: Simulador analítico e exploratório em Python 3.10+ com interface Streamlit, servindo de protótipo de pesquisa e validação física das equações.

---

## 🏭 Arquitetura do Sistema Físico e Nós Termodinâmicos

O simulador modela o trem contínuo de ar comprimido para instalações offshore (FPSO / Plataformas Fixas) e plantas de processo:

```
[Nó A: Atmosfera] ──> [Filtro de Admissão] ──> [Nó B: Sucção LP (Sub-atmosférica)]
       │
       ├──> [Estágio LP (Compressor Parafuso)] ──> [Nó C: Descarga LP]
       │
       ├──> [Intercooler Ar-Água] ──> [Nó D: Sucção HP]
       │
       ├──> [Estágio HP (Compressor Parafuso)] ──> [Nó E: Descarga HP]
       │
       ├──> [Aftercooler Ar-Água] ──> [Nó F: Saída Aftercooler]
       │
       ├──> [Separador Centrífugo] ──> [Secador por Adsorção PSA]
       │
       └──> [Nó G: Vaso Pulmão (Air Receiver)] ──> [Rede de Distribuição / Consumidores]
```

### Normas Técnicas e Critérios de Engenharia Atendidos:
- **ISO 1217 (Anexo C/E)**: Cálculo de vazão efetiva (FAD), consumo específico de energia (SPC) e rendimento isentrópico/isotérmico.
- **API 619**: Compressores rotativos de deslocamento positivo para serviços de petróleo e gás (limites de vibração RMS, temperaturas máximas de carcaça e folgas).
- **ISO 8573-1 (Classe 2)**: Monitoramento contínuo do Ponto de Orvalho sob Pressão (PDP $\le -40^\circ\text{C}$).
- **ASME VIII Div. 1**: Rastreamento estrutural de vasos de pressão, Pressão Máxima de Trabalho Admissível ($\text{PMTA} = 10.0\text{ bar}$), pressão mínima crítica de rede ($P_{mín} = 6.0\text{ bar}$) e taxa máxima de despressurização $\frac{dP}{dt}$.
- **ISA 18.2**: Gestão de alarmes industriais (Normal, Alerta High/Low, Trip HH/LL).
- **OSIsoft PI System**: Catálogo e exportador/importador de telemetria com mais de 26 tags industriais (Tabela 18.1).

---

## 🚀 Funcionalidades do Gêmeo Digital (Rust 2.0 & Python)

| Módulo / Tela | Descrição Física e Funcional | Algoritmos e Equações |
| :--- | :--- | :--- |
| **🚢 Supervisório de Frota** | Monitoramento de frota com $N$ compressores em paralelo, Health Index composto (HI) bilateral e prognóstico de Vida Útil Restante (RUL) com intervalo de confiança de 95%. | Eq. 26.4 (HI), Eq. 19.10 (RUL IC 95%), Eq. 21.7 (NIS $\chi^2$) |
| **📊 Dashboard do Ativo** | Visualização em tempo real dos 7 nós termodinâmicos, balanço exergético, emissões de $\text{CO}_2$, telemetria PI expansível e gráficos dinâmicos. | ISO 1217, Eq. 17.3 (Exergia Destruída), Eq. 11.11 (SPC) |
| **📡 Telemetria PI & Dados** | Geração de telemetria sintética com ruído calibrado, exportação CSV para PI DataLink e módulo de ingestão/upload com validação via filtro EKF. | Tabela 18.1 (26+ tags ISA 18.2), EKF NIS Test |
| **🔬 Diagnóstico & IA** | Classificador bayesiano de falhas por resíduo mínimo ponderado ($\hat{m}_{falha}$), explicabilidade SHAP, EKF de estado aumentado, PSO para setpoint ótimo $\pi^*$ e controle preditivo MPC. | Eq. 29.2 (Classificador), EKF (Cap. 28), PSO (Eq. 24.3), MPC (Cap. 14) |
| **🛠️ Sistema & Dinâmica** | Visão transiente do vaso pulmão ($P_{vaso}, P_{in}, P_{out}$) frente a perturbações de demanda, modos VSD vs Carga/Alívio, secador PSA (Gantt) e controle de parâmetros de integração ($T_{sim}, \Delta t$). | $\frac{dP}{dt} = \frac{RT}{V}(\dot{m}_{in} - \dot{m}_{out})$, Rampa VSD ($\tau=5s$), Limites ASME VIII |
| **🎯 Arena de Treinamento** | Simulador de casos cegos operacionais para operadores e engenheiros, avaliando hipótese causal, subsistema e severidade com parecer técnico fundamentado. | 11 mecanismos de falha do livro |
| **⚙️ Configurações & Trens** | Parametrização dinâmica de trens de compressores ($N=1\dots 12$), capacidade FAD unitária ($5\dots 80\text{ m}^3/\text{min}$), filosofias de redundância ($N+0, N+1, 2N$) e constantes construtivas. | API 619 / ISO 1217 |

---

## 💻 Como Executar

### 1. Versão Rust 2.0 (Axum + Web Industrial) — Recomendada

```bash
# Navegar até o diretório do projeto Rust
cd compressor2

# Executar a suíte de 26 testes unitários
cargo test --workspace

# Iniciar o servidor web
cargo run --bin compressor2
```
Acesse no navegador: **[http://localhost:8080](http://localhost:8080)**

### 2. Versão Python (Streamlit)

```bash
cd aplicativo

# Ativar ambiente virtual e instalar dependências
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt

# Executar os testes
pytest tests/

# Iniciar o Streamlit
streamlit run app.py
```
Acesse no navegador: **[http://localhost:8501](http://localhost:8501)**

---

## 🎨 Acessibilidade e Auditoria Visual (WCAG 2.1 AA)

A aplicação conta com alternância de temas (**☀️ Claro**, **🌙 Escuro** e **🖥️ Auto**) com regras semânticas de alto contraste ($CR \ge 7.0:1$), auditadas e aprovadas automaticamente via **Google Chrome Headless** em todas as telas e controles.

---

## 📂 Estrutura do Repositório

```
Compressores/
├── README.md                      # Visão geral do ecossistema
├── CONTEXTO.md                    # Fundamentação técnica e normas de engenharia (livro)
├── CONTEXTO_app.md                # Histórico cronológico de sessões de desenvolvimento (livro + interface)
├── Volume_0_Notacoes_e_Calculo.tex/.pdf  # Volume 0 — pré-requisitos matemáticos
├── Volume_I_Fundamentos.tex/.pdf  # Volume I — fundamentos teóricos
├── compressores.tex/.pdf          # Volume II — gêmeo digital (documento principal)
├── compressor2/                   # Implementação em Rust 2.0
│   ├── Cargo.toml                 # Workspace Cargo
│   ├── README.md                  # Documentação detalhada da stack Rust
│   └── crates/
│       ├── sim_core/              # Núcleo termodinâmico e algoritmos de IA em Rust
│       │   └── src/               # nucleo, sistema, dinamica, frota, pi_telemetry, etc.
│       └── app/                   # Servidor Axum, rotas REST e SPA Web
│           └── src/main.rs        # Frontend industrial de alto contraste e APIs
├── aplicativo/                    # Implementação em Python
│   ├── app.py                     # Dashboard Streamlit
│   ├── requirements.txt           # Dependências Python
│   ├── GUIA_CODIGO.md             # Documentação dos módulos Python
│   ├── IMPLEMENTACAO.md           # Detalhes de implementação
│   ├── MANUTENCAO.md              # Plano de manutenção e extensão
│   └── compressor_sim/            # Módulos analíticos Python
├── figuras/                       # Diagramas e esquemáticos técnicos
└── scripts/                       # Scripts auxiliares e de geração gráfica
```
