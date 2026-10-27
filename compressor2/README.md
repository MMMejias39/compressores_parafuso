# Digital Twin Compressor 2.0 (Rust & Axum Web Stack)

Implementação de alta performance e rigor normativo do **Gêmeo Digital de Compressores de Parafuso Duplo Oil-Free em Dois Estágios**.

---

## 🏛️ Arquitetura do Workspace Cargo

O projeto é estruturado como um workspace Rust modular:

```
compressor2/
├── Cargo.toml
├── README.md
└── crates/
    ├── sim_core/              # Biblioteca pura de simulação e algoritmos de IA
    │   ├── Cargo.toml
    │   └── src/
    │       ├── constantes.rs  # Constantes físicas universais e propriedades do ar úmido
    │       ├── nucleo.rs      # Termodinâmica dos estágios LP/HP e psicrometria
    │       ├── subsistemas.rs # Intercooler, aftercooler, separador, vaso pulmão
    │       ├── sistema.rs     # Cascata completa dos 7 nós (Pontos A a G)
    │       ├── dinamica.rs    # Balanço diferencial contínuo dP/dt e limites ASME VIII
    │       ├── psa_ciclo.rs   # Adsorção por modulação de pressão (PSA)
    │       ├── mpc.rs         # Controle Preditivo Baseado em Modelo
    │       ├── pso.rs         # Otimização por Enxame de Partículas (π*)
    │       ├── calib_lm.rs    # Calibração em lote via Levenberg-Marquardt
    │       ├── ekf.rs         # Filtro de Kalman Estendido com teste NIS
    │       ├── pi_telemetry.rs# Catálogo de 26+ tags industriais OSIsoft PI (ISA 18.2)
    │       ├── frota.rs       # Supervisório de frota offshore com RUL probabilístico (IC 95%)
    │       └── treinamento.rs # Diagnóstico causal de falhas e arena de treinamento
    └── app/                   # Aplicação servidora Axum e Single-Page Application (SPA)
        ├── Cargo.toml
        ├── assets/
        │   ├── tailwind.input.css   # Fonte do design system (tokens + componentes)
        │   ├── app.css              # Gerado pelo Tailwind CLI — versionado
        │   └── chart.umd.min.js     # Chart.js 4.4.1 vendorizado (MIT) — versionado
        └── src/
            ├── main.rs        # Servidor assíncrono Tokio/Axum, rotas REST e assets embutidos
            ├── index.html     # SPA industrial (HTML + CSS componentizado + JS)
            └── bin/benchmark.rs # Benchmark de tempo de resposta das rotas
```

---

## 🔬 Normas Técnicas Atendidas

- **ISO 1217**: Medição de vazão FAD e cálculo de Consumo Específico de Energia (SPC em $\text{kW}\cdot\text{min}/\text{m}^3$).
- **API 619**: Parâmetros de compressores de deslocamento positivo, folgas relativas e limites de vibração.
- **ISO 8573-1**: Monitoramento contínuo de Ponto de Orvalho sob Pressão (PDP Classe 2 $\le -40^\circ\text{C}$).
- **ASME VIII Div. 1**: Rastreamento estrutural de vasos de pressão, PMTA ($10.0\text{ bar}$), $P_{min}$ ($6.0\text{ bar}$) e taxa de variação $\frac{dP}{dt}$.
- **ISA 18.2 / OSIsoft PI**: Mapeamento completo de telemetria industrial com tags analógicas e calculadas.
- **WCAG 2.1 AA**: Conformidade de acessibilidade e alto contraste auditada no Google Chrome.

---

## 🚀 Como Compilar e Executar

### Testes Unitários
```bash
cargo test --workspace
```
*Garante a aprovação dos 26 testes físicos, matemáticos e de convergência dos algoritmos de IA.*

### Execução do Servidor Web
```bash
cargo run --bin compressor2
```
Acesse: **`http://localhost:8080`**

A porta pode ser trocada por variável de ambiente, útil quando a 8080 já está
ocupada por outro serviço ou reservada pelo sistema (nesse caso o `bind` falha
com `WSAEACCES`):

```bash
PORT=8090 cargo run --bin compressor2   # bash
$env:PORT=8090; cargo run --bin compressor2   # PowerShell
```

### Interface: totalmente offline

A SPA não depende de nenhuma CDN. O `main.rs` embute os assets no binário com
`include_bytes!` e os serve em `/assets/app.css`, `/assets/chart.umd.js` e
`/favicon.svg`. Isso é requisito de operação offshore (rede isolada): a
interface abre completa mesmo sem internet.

### Alterar a interface

O HTML vive em `crates/app/src/index.html` e o CSS-fonte em
`crates/app/assets/tailwind.input.css`. Depois de editar qualquer um dos dois,
regenere o CSS compilado:

```bash
cd crates/app
tailwindcss -i assets/tailwind.input.css -o assets/app.css \
            --content src/index.html --minify
```

`assets/app.css` é **versionado de propósito**: assim `cargo build` funciona
sem Node/npm instalado. Use o [Tailwind CLI standalone](https://github.com/tailwindlabs/tailwindcss/releases)
(v3.4.x) — não é necessário `package.json`. Depois de regerar o CSS, basta
`cargo build` (o `include_str!`/`include_bytes!` já registra a dependência).

---

## 🎛️ Notas de interface

- **Acessibilidade**: abas seguem o padrão ARIA (`role="tablist"`/`tab`/`tabpanel`,
  `aria-selected`, `aria-controls`), navegação por setas/Home/End, regiões de
  alarme com `aria-live`, link de salto para o conteúdo, anel de foco visível em
  todos os controles e respeito a `prefers-reduced-motion`.
- **Temas**: claro/escuro/auto via `localStorage`, com contraste AA nos dois modos.
- **Responsivo**: barra lateral e abas se reorganizam abaixo de 1024 px; todo o
  conteúdo é servido por um único binário.
- **Impressão**: `@media print` esconde navegação e sombras para gerar relatórios.
- **Mapa do Conjunto**: aba com a elevação do pacote e a vista 3D, os 12 pontos de
  medição com as tags PI e download das figuras em PDF vetorial. As imagens são
  geradas por `scripts/desenhar_conjunto.py` e `scripts/desenhar_conjunto_3d.py`
  e ficam embutidas no binário.

---

## 📡 Endpoints REST da API

| Rota | Método | Descrição |
| :--- | :---: | :--- |
| `/` | `GET` | SPA Web Industrial completa (HTML5 + CSS compilado + Chart.js) |
| `/assets/app.css` | `GET` | Design system compilado (embutido no binário) |
| `/assets/chart.umd.js` | `GET` | Chart.js 4.4.1 vendorizado (embutido no binário) |
| `/assets/conjunto-pontos.png` | `GET` | Elevação do conjunto com os pontos de medição A–I |
| `/assets/conjunto-pontos.pdf` | `GET` | A mesma figura em vetor (para impressão) |
| `/assets/conjunto-3d.png` | `GET` | Vista 3D do conjunto |
| `/assets/conjunto-3d.pdf` | `GET` | A vista 3D em vetor |
| `/favicon.svg` | `GET` | Ícone da aplicação |
| `/api/health` | `GET` | Health check da aplicação e versão |
| `/api/simular` | `POST` | Executa o balanço estático dos 7 nós termodinâmicos |
| `/api/frota` | `GET` | Retorna o painel da frota de compressores (`?n_compressores=N&fad_unitario=X`) |
| `/api/pi/snapshot` | `GET` | Snapshot instantâneo das tags OSIsoft PI do ponto de operação atual |
| `/api/telemetria` | `POST` | Gera snapshot de telemetria multivariável OSIsoft PI com ruído calibrado |
| `/api/dinamica/simular` | `POST` | Simulação transiente contínua ($P_{vaso}, P_{in}, P_{out}$) com $T_{sim}$ e $\Delta t$ |
| `/api/treinamento/caso` | `POST` | Sorteia caso operacional cego com mecanismo de falha |
| `/api/treinamento/catalogo` | `GET` | Retorna o catálogo de mecanismos de falha da arena de treinamento |
| `/api/treinamento/avaliar` | `POST` | Avalia hipótese causal do operador e emite parecer técnico |
| `/api/diagnostico/classificar` | `POST` | Classificador bayesiano de resíduo mínimo ponderado $\hat{m}_{falha}$ |
| `/api/psa/simular` | `POST` | Simulação de ciclagem e Gantt das torres adsortivas PSA |
| `/api/mpc/simular` | `POST` | Controle preditivo de pressão e antecipação de carga |
| `/api/pso/otimizar` | `POST` | Otimização estocástica de setpoint via enxame de partículas |
| `/api/ekf/simular` | `POST` | Filtro de Kalman Estendido com estimação de folgas e fouling |

