# Documentação de Implementação — Simulador do Trem de Ar Comprimido

Este documento descreve **como o simulador é construído** — arquitetura,
decisões de projeto e o porquê delas. Para uma explicação função a função de
cada arquivo, ver `GUIA_CODIGO.md`. Para como manter/estender o projeto, ver
`MANUTENCAO.md`. Para o histórico de sessões de desenvolvimento (o "diário"
por trás destas decisões), ver `../CONTEXTO_app.md` — este documento é a
versão destilada e estável; aquele é o registro cronológico completo.

## Objetivo do sistema

Simular o trem de ar comprimido offshore descrito no livro *Gêmeo Digital de
Sistemas de Compressão Offshore* (`../compressores.tex`) — desde a admissão
até a rede de distribuição — como aplicativo web interativo, e demonstrar em
código funcional os cinco algoritmos de Gêmeo Digital da Parte II do livro
(EKF, VAE, PIML, MPC, PSO), incluindo os três caminhos de identificação de
parâmetro por problema inverso da Parte III (EKF aumentado e PIML, Caps.
23.8 e 28.1, mais calibração em lote via Levenberg-Marquardt,
`calib_lm.py`, 16/08/2026 — alternativa clássica aos dois primeiros, sem
filtro nem rede neural).

Não é um produto de engenharia para uso em campo — é uma implementação de
referência **pedagógica e de verificação**: toda equação do livro que entra
no código é citada pelo número (`# Eq. 5.5`), e a reimplementação em Python
funciona como auditoria independente do próprio texto (já encontrou e
corrigiu 3 erros de unidade no livro — ver `MANUTENCAO.md`).

## Filosofia de projeto

### Modelo gray-box, não caixa-preta nem física pura

O núcleo termodinâmico (`nucleo.py`, `subsistemas.py`, `sistema.py`) é
**física de primeiros princípios pura** — nenhuma rede neural, nenhum dado de
treino. Os cinco algoritmos de IA (`ekf.py`, `vae.py`, `piml.py`, `mpc.py`,
`pso.py`) operam **em cima** desse núcleo, nunca o substituindo: o VAE é
treinado sobre amostras que o próprio núcleo gera; o PIML usa o núcleo tanto
para rotular dados de treino quanto para expressar o resíduo físico; o MPC
otimiza sobre o mesmo balanço de massa algébrico do núcleo. Não existe, em
lugar nenhum deste app, uma rede treinada sobre dados que não vieram do
núcleo físico — não haveria como, já que não existe dado de planta real
disponível para este projeto.

### Toda equação é rastreável ao livro

Convenção não-negociável: qualquer fórmula implementada cita o número da
equação do livro em comentário ou docstring. Onde o livro não fecha um valor
numérico (ex. volume do vaso pulmão, constante de tempo do VSD), o parâmetro
é marcado **ASSUMIDO** — tanto em `constantes.py` quanto na label do widget
correspondente na UI. Essa é a mesma disciplina de veracidade do livro
(`../CONTEXTO.md`, "Veracidade de referências e fontes"), adaptada de
citação bibliográfica para número de engenharia.

### Unidades e convenções fixas

- SI em todo o núcleo de cálculo; pressões sempre **absolutas** (Pa
  internamente, bar na UI); temperaturas em **K** no cálculo, °C na UI.
- Forma canônica de potência de estágio: politrópica (Eq. 5.5) — não a forma
  isotérmica ou adiabática ideal, que só aparecem como referência de KPI
  (η_global).
- `m_dot` (vazão mássica "crua") e `m_dot_seco` (vazão de ar seco,
  corrigida pela psicrometria) são grandezas **distintas e ambas
  necessárias**: a cadeia de potência de compressão (P·V=nRT com vazão
  volumétrica fixa) é invariante à umidade e usa `m_dot`; todo balanço de
  massa real (condensado, purga, tabela de estados) usa `m_dot_seco`. Ver
  `GUIA_CODIGO.md` § `sistema.py` para a derivação completa.

### Uma unidade representativa, planta escalada depois

`sistema.simular()` calcula o trem termodinâmico completo para **uma única
unidade**. `n_compressores` unidades idênticas, no mesmo ponto de operação,
operam em paralelo — só as grandezas de planta (potência total, FAD total,
condensado total) são multiplicadas por `n_compressores`; grandezas
intensivas (eficiências, temperaturas, pressões, SPC) não mudam. A dinâmica
do vaso/rede (`dinamica.py`, `mpc.py`) usa a capacidade **total da planta**
(`m_dot_cap = nos[-1]["m_dot"] * n_compressores`), não a de uma unidade — do
contrário, `n_compressores` não teria efeito nenhum sobre a autonomia
simulada.

## Arquitetura — visão geral

```
                         ┌─────────────────┐
                         │  constantes.py   │  origem de todo default numérico
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                                        ▼
      ┌───────────────┐                        ┌──────────────┐
      │   nucleo.py    │                        │ subsistemas.py│
      │ (estágios,     │                        │ (intercooler, │
      │  psicrometria, │                        │  separador,   │
      │  motor, hood,  │                        │  PSA, vaso)   │
      │  carcaça)      │                        │               │
      └───────┬────────┘                        └───────┬───────┘
              │                                          │
              └───────────────────┬──────────────────────┘
                                   ▼
                          ┌────────────────┐
                          │   sistema.py    │   simular(params) -> resultados
                          │  (a cascata)    │   ponto de entrada de TUDO
                          └────────┬────────┘
                                   │
        ┌──────────┬──────────────┼───────────────┬─────────────┐
        ▼          ▼              ▼               ▼             ▼
  ┌──────────┐ ┌─────────┐  ┌───────────┐   ┌───────────┐  ┌─────────┐
  │dinamica.py│ │psa_ciclo│  │  ekf.py   │   │  vae.py   │  │ piml.py │
  │  (vaso    │ │  .py    │  │(estimação │   │(detecção  │  │(substi- │
  │  no tempo)│ │(rodízio │  │ de estado,│   │de anomalia│  │ tuto +  │
  │           │ │ torres) │  │ + K aum.) │   │multivar.) │  │problema │
  └─────┬─────┘ └─────────┘  └───────────┘   └───────────┘  │inverso) │
        │                                                    └─────────┘
        ▼
   ┌─────────┐
   │  mpc.py  │  (usa a mesma integração de dinamica.py)
   └─────────┘
        ▲
        │
   ┌─────────┐
   │  pso.py  │  (otimiza sobre `sistema.simular`, função de custo genérica)
   └─────────┘

  Todos os módulos acima são consumidos por app.py (interface Streamlit, 5
  abas: Supervisório de Frota / Dashboard do Ativo / Diagnóstico & IA /
  Sistema & Dinâmica / Configurações — mais o Modo Treinamento, ativado na
  barra lateral)
```

`sistema.py` é o único módulo que TODOS os outros (exceto `constantes.py`)
dependem direta ou indiretamente — é o "motor de cálculo único" do app,
equivalente em espírito ao Capítulo 18 do livro. Os módulos de IA (`ekf`,
`vae`, `piml`, `mpc`, `pso`) nunca reimplementam física própria — sempre
chamam `sistema.simular()` (ou, no caso do PIML, replicam uma fração mínima
e explicitamente documentada da física em forma diferenciável, ver
`GUIA_CODIGO.md` § `piml.py`).

## As cinco abas da interface

1. **🚢 Supervisório de Frota** — painel da frota offshore: $HI$ composto
   (Eq. 26.4), auditoria $NIS$ (Eq. 21.7) e $RUL$ bayesiano por máquina.
2. **📊 Dashboard do Ativo** — um único ponto de operação, calculado por
   `sistema.simular()`: KPIs, tabela de estados ao longo do trem,
   perfil P/T/PDP, motor/hood, carcaça, tubulação, balanço exergético e
   telemetria PI. Com o **Modo Treinamento** ativo (botão na barra lateral,
   banner em todas as abas), passa a exibir a Arena de Treinamento — desafio
   cego em 4 níveis de dificuldade e biblioteca técnica de mecanismos.
3. **🔬 Diagnóstico & IA** — duas sub-abas: **Laboratório de Falhas &
   Classificador m̂_falha** (10 cenários de falha isolada de
   `cenarios_falha.py`, classificação por resíduo mínimo Eq. 29.2) e
   **Motores de IA** (5 sub-abas: EKF & EKF Aumentado, VAE, PIML, MPC, PSO —
   os cinco algoritmos da Parte II mais os três caminhos de identificação
   de K: EKF aumentado, PIML inverso e calibração em lote via
   Levenberg-Marquardt). O EKF de 2 estados e o EKF aumentado rotulam o
   eixo de tempo em dias, não em passos abstratos — um "Δt entre medições"
   assumido converte o horizonte de simulação para a mesma escala de
   semanas do cenário do Capítulo 29. Cenário e parâmetros configuráveis na
   aba Configurações.
4. **🛠️ Sistema & Dinâmica** — três sub-abas: **Dinâmica Temporal**
   (`dinamica.simular_transiente()`, a rede respondendo no tempo a um
   perfil de demanda com evento de pico, nos modos VSD ou Carga/Alívio);
   **Secagem PSA** (`psa_ciclo.simular_ciclo_psa()`, rodízio de N torres
   com as 3 fases (adsorvendo/regenerando/resfriando) e os KPIs do
   Capítulo 15, incluindo o ponto de orvalho na saída do secador ao longo
   do tempo (`pdp_saida_c`) — serrilhado, reiniciando a cada troca de
   torre); e **Conector PI System** (gerador/exportador de telemetria,
   importador de arquivos externos e catálogo de tags).
5. **⚙️ Configurações** — geometria de equipamento e
   hiperparâmetros de algoritmo que não mudam de uma sessão de análise
   para a outra: tudo que antes vivia numa única barra lateral longa,
   exceto as condições de operação do momento (essas continuam na barra
   lateral, sempre visíveis). Ver `GUIA_CODIGO.md` § `app.py` para a
   ordem de execução.

## Por que os algoritmos de IA têm escopo reduzido frente ao livro

O EKF do livro (Eq. 21.2) estima um vetor de 5 estados
`[η_is,LP, η_is,HP, δ, R_f, σ_b]`. Este app modela só 2 deles no EKF
principal (`δ/L` e `R_f`) porque são os únicos com contraparte **calculável**
na cascata implementada — os outros três exigiriam um modelo de motor
elétrico e de engrenagem a um nível de detalhe que este simulador não tem
(rotordinâmica, fadiga de dente). A extensão de 16/08/2026 (EKF com estado
aumentado, `simular_ekf_aumentado`) segue a mesma regra: só o parâmetro K
(Eq. 9.3) foi portado dos três de Λ do livro (K, η_mec, ζ_ref), porque é o
único que aparece na mesma equação que já liga folga a uma medição existente
(`ṁ_seco`) — η_mec e ζ_ref exigiriam um canal de medição novo (potência
elétrica, ΔP do filtro) que o EKF ainda não usa. Essa é uma decisão
recorrente do projeto: **estender só até onde há um caminho de observação
real**, documentando explicitamente o que ficou de fora e por quê — nunca
implementar um mecanismo "para constar" sem que ele meça algo de verdade.

## Cache e performance da UI

Treinos de VAE/PIML (segundos a dezenas de segundos) são envolvidos em
`@st.cache_resource`, chaveados pelos parâmetros que afetam o resultado
(ponto de operação relevante + hiperparâmetros de treino) — mudar um slider
não relacionado não dispara retreino. EKF, PSO, MPC e a cascata estática são
baratos o suficiente (milissegundos a poucos segundos) para rodar a cada
interação sem cache.
