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
        └── src/
            ├── main.rs        # Servidor assíncrono Tokio/Axum, rotas REST e interface industrial
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

---

## 📡 Endpoints REST da API

| Rota | Método | Descrição |
| :--- | :---: | :--- |
| `/` | `GET` | SPA Web Industrial completa (HTML5 / Tailwind / Chart.js) |
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

