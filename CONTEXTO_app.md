# Contexto do Aplicativo — `aplicativo/`

Este arquivo documenta o simulador Streamlit em `aplicativo/`, separado do
`CONTEXTO.md` principal (que trata do livro `compressores.tex`) a pedido do
autor. Leia este arquivo antes de mexer em qualquer coisa dentro de
`aplicativo/`.

## O que é

Aplicativo web (Streamlit) que simula o trem completo de ar comprimido
offshore descrito no livro `../compressores.tex`: filtro de admissão →
estágio LP → intercooler → estágio HP → aftercooler → separador de
condensado → secador PSA → vaso pulmão/rede. Todas as equações do núcleo
termodinâmico citam o número da equação do livro no código-fonte (ex.:
`# Eq. 5.5 — trabalho politrópico por estágio`).

O app foi criado fora desta sessão de acompanhamento contínuo (autor +
Claude), com contribuição de outras IAs ("palpites de outras IAs" — autor).
Esta sessão (01/08/2026) não encontrou nenhum registro prévio dele em
memória nem no `CONTEXTO.md` principal — foi a primeira vez que o Claude
Code leu o código deste diretório.

## Estrutura

```
aplicativo/
├── app.py                  # interface Streamlit (ponto de entrada, 3 abas)
├── compressor_sim/
│   ├── constantes.py       # propriedades do ar e defaults (ASSUMIDO onde o livro não fecha valor)
│   ├── nucleo.py           # estágios de compressão + psicrometria
│   ├── subsistemas.py      # intercooler, separador, secador PSA, vaso/rede
│   ├── sistema.py          # cascata completa: simular(params) -> resultados (1 unidade + totais de planta)
│   ├── dinamica.py         # simulação transiente do vaso/rede (VSD ou carga/alívio)
│   └── psa_ciclo.py        # rodízio de N torres do secador PSA (Eq. 15.1/15.2)
├── tests/test_simulador.py # testes de sanidade (pytest) — 36 testes, todos passando
└── requirements.txt        # streamlit, numpy, matplotlib, pytest
```

## Como rodar

```bash
cd aplicativo
python3 -m venv venv        # se ainda não existir
venv/bin/pip install -r requirements.txt
venv/bin/streamlit run app.py --server.headless true --server.port 8501
```
Abre em `http://localhost:8501`. Testes: `venv/bin/pytest tests/ -q`.

**Cuidado ao reiniciar o servidor**: se um processo Streamlit já estiver
rodando na porta 8501 iniciado fora desta sessão (outro terminal do autor,
por exemplo), não mate o processo sem perguntar antes — foi exatamente essa
a situação em 01/08/2026 (processo com `PPID` de outro terminal, não desta
sessão). Depois de editar `app.py` ou qualquer módulo de `compressor_sim/`,
reinicie o processo (mata + sobe de novo) em vez de confiar no
autoreload/rerun do Streamlit — evita estado dessincronizado entre o código
em disco e a sessão do navegador já aberta.

## Convenções específicas do app

- SI; pressões **absolutas** (Pa/bar); temperaturas em K no cálculo, °C na UI.
- Forma canônica de potência de estágio: **politrópica (Eq. 5.5)**.
- Todo parâmetro que o livro não fecha numericamente (vazão FAD, UA, volume
  do vaso, `n_compressores`, `tau_vsd` etc.) é marcado como **ASSUMIDO** em
  `constantes.py`/`dinamica.py` e na label do widget na UI — mesma regra de
  veracidade do livro (`CONTEXTO.md`, "Veracidade de referências e fontes"),
  adaptada para números de engenharia em vez de citações bibliográficas.
- `sistema.simular()` calcula o trem termodinâmico (`nos`, potências em
  `potencias`) para **uma unidade representativa**; `n_compressores`
  unidades idênticas operam em paralelo no mesmo ponto de operação. Só as
  grandezas de planta (`potencias.w_total_planta`, `kpis.fad_total_m3_min`,
  `kpis.condensado_total_planta_kg_h`) são multiplicadas por
  `n_compressores` — grandezas intensivas (SPC, eficiências, temperaturas,
  pressões) não mudam com a contagem de unidades, e a tabela "Pontos de
  estado ao longo do trem" continua representando uma unidade só. Ver
  docstring de `sistema.simular()`.
- A capacidade que alimenta a dinâmica do vaso/rede (`dinamica.py`, aba
  "Dinâmica temporal") é a **capacidade total da planta**
  (`m_dot_cap = nos[-1]["m_dot"] * n_compressores`), não a de uma unidade —
  do contrário aumentar `n_compressores` não teria efeito nenhum sobre a
  autonomia/resposta a picos de demanda simulada.

## Sessão de 01/08/2026 — dois problemas reais corrigidos

**1. Gráfico de pressão reto no modo VSD (`dinamica.py`).** A lei de
controle usava `x_c = demanda/capacidade` de forma instantânea — fiel à
definição de regime permanente da Equação 13.7 do livro (`x_c =
V̇_demanda/V̇_nom`), mas aplicada ponto a ponto na simulação temporal isso
faz `dP/dt = R·T/V·(ṁ_in − ṁ_out) = 0` o tempo inteiro, porque `ṁ_in` passa
a seguir `ṁ_demanda` perfeitamente. Resultado: o gráfico de pressão da rede
no modo VSD nunca se movia, não importa o que se mudasse nos sliders
(horizonte, evento de pico, banda). Corrigido modelando a resposta do VSD
como uma **rampa de 1ª ordem** com constante de tempo `tau_vsd` (novo
parâmetro **ASSUMIDO**, exposto como slider "Constante de tempo de rampa do
VSD τ [s]", default 5 s): `x_c` persegue o alvo de regime permanente em vez
de saltar para ele instantaneamente. Fisicamente correto — um inversor real
não acompanha a demanda com resposta infinita — e consistente com o próprio
livro, que menciona explicitamente (linha ~2903 do `.tex`, contexto do peso
$\rho$ do MPC) que perseguir cada flutuação de pressão com mudança abrupta
de frequência do VSD é um comportamento indesejado a evitar, ou seja, uma
resposta com alguma inércia é a leitura fisicamente certa.
Testes de regressão: `test_vsd_pressao_reage_a_evento_de_demanda`,
`test_vsd_pressao_constante_sem_evento`.

**2. Sem suporte a múltiplos compressores em paralelo.** O simulador só
modelava uma máquina isolada — não havia como representar uma planta
offshore real, tipicamente com N compressores idênticos em paralelo
alimentando um cabeçalho/vaso comum. Adicionado `n_compressores` (1–10,
ASSUMIDO, default 1 — não muda o comportamento de quem não mexer nele) como
novo parâmetro em `constantes.py`/`sistema.py`/`app.py`, com as grandezas de
planta descritas na seção de convenções acima. Também corrigido de
passagem: o KPI `dp_dt_vaso_bar_min` (Eq. 16.4, balanço de massa do
vaso/rede) usava vazão de saída de **uma** unidade mesmo antes dessa
feature existir — agora usa `m_dot_util * n_compressores`, senão o balanço
de pressão da rede ficaria sistematicamente errado (superestimando o
esvaziamento) assim que o app passasse a existir com N ajustável.
Teste de regressão: `test_n_compressores_escala_totais_sem_afetar_por_unidade`.

Testado interativamente pelo autor após cada correção (app já estava
rodando desde antes desta sessão; reiniciado a cada mudança de código,
sempre com confirmação prévia por não ser processo desta sessão) — ambos os
comportamentos confirmados como esperados (N=3 avaliado, "os números fazem
sentido").

## Aba de ciclo de torres do secador PSA (01/08/2026, commit `875e900`)

A pedido do autor, adicionado o rodízio de N torres do secador PSA como
3ª aba do app ("🌀 Secagem PSA"), com um seletor de topologia análogo ao
`n_compressores`: **N vasos por compressor** (cada unidade em paralelo tem
seu próprio secador dedicado — o gráfico é idêntico em todas, já que operam
no mesmo ponto) ou **N vasos para o sistema** (um único banco compartilhado,
dimensionado para a vazão total da planta — a purga escala por
`n_compressores`).

Novo módulo `compressor_sim/psa_ciclo.py`: generaliza o princípio de duas
torres da Figura 15.1 do livro para N em rodízio round-robin. A Eq. 15.1
(`q_d = q_eq·exp(-k_ads·t_ads/t_res)`) rege a capacidade de adsorção durante
a fase ativa de cada torre; a recuperação durante a regeneração é uma
**simplificação de modelagem** (retorno linear a q_eq) — não é uma equação
do livro, já que o Capítulo 15 não fecha a cinética de dessorção, e está
marcada como tal no docstring do módulo. A vazão de purga usa a Eq. 15.2.

**Armadilha de ponto flutuante encontrada e corrigida**: a primeira
implementação calculava o estado de cada torre (adsorvendo/regenerando)
independentemente via `(t - offset_i) % t_ciclo < t_ads_max` por torre —
isso falhava esporadicamente em fronteiras exatas de chaveamento (ex.:
`n_vasos=3`, `t_ciclo=8.0`), produzindo instantes com 0 ou 2 torres
regenerando simultaneamente por arredondamento, quebrando a invariante
física do sistema (sempre exatamente 1 regenerando). Corrigido computando
um **índice de slot global determinístico**
(`slot = floor(t/t_regen)`, `torre_regenerando = slot % n_vasos`) como
fonte única de verdade, eliminando a ambiguidade por construção em vez de
tentar sincronizar N comparações independentes. **Se essa lógica for tocada
de novo**: nunca decidir o estado de cada torre com comparações de ponto
flutuante independentes entre si — sempre derivar de um cálculo
compartilhado único.

5 testes novos, incluindo um parametrizado (`n_vasos` = 2, 3, 4) que
verifica a invariante "exatamente 1 torre regenerando" — foi esse teste que
pegou o bug acima antes de chegar ao app.

Testado interativamente pelo autor via navegador (extensão Claude-in-Chrome
não conectada nesta sessão, então a verificação visual foi só do autor, não
minha) — confirmado "os gráficos aparecem certos".

## KPIs do Cap. 15 — SEC_dry e HI_des (02/08/2026, commit `0b6534e`)

Completado o trio "Indicadores Globais de Performance" do Cap. 15 na aba
de Secagem PSA — faltavam `SEC_dry` (Eq. 15.6) e `HI_des` (Eq. 15.7);
`η_purge` (Eq. 15.9) já existia desde a criação do app.

- **`SEC_dry`**: soma potência do aquecedor + tambor rotativo, dividida
  pela vazão de ar seco. Este app modela só o secador PSA a frio, **não**
  o secador de tambor rotativo (HOC) que o Cap. 15 também descreve — a
  parcela do tambor é sempre 0 (`W_DRUM_PADRAO` em `constantes.py`),
  mantida como parâmetro explícito de `subsistemas.sec_dry()` em vez de
  omitida, para não esconder essa limitação de escopo.
- **`HI_des`**: índice de saúde do dessecante a partir de ΔP e PDP
  "medidos" — dois sliders novos na barra lateral (`dp_real_psa`,
  `pdp_real_c`), mesmo padrão já usado para o fouling do intercooler
  (valor assumido/medido, default = condição saudável, ajustável pelo
  usuário para simular degradação).

**Achado durante a implementação, e corrigido no livro logo em seguida**
(02/08/2026, commit `738cc1c` do `compressores.tex`): a Equação 15.7,
avaliada literalmente com PDP em °C (com sinal), invertia o sentido do
índice — um PDP real *pior* (mais alto/mais quente) gerava `HI_des`
*maior*, o oposto do que o índice deveria sinalizar. Mesma classe de erro
de unidade das Equações 9.8/11.6 (ver `CONTEXTO.md`), corrigida da mesma
forma: conversão `+273,15` explícita na fórmula do livro. A implementação
aqui (`hi_des()` em `subsistemas.py`) já convertia para Kelvin desde a
criação — o livro é que estava desalinhado, agora os dois concordam.

4 testes novos, incluindo verificação direta de que degradar ΔP ou PDP
reduz `HI_des` (não aumenta) — é esse teste que teria pego o erro de
sinal acima se a conversão para Kelvin não tivesse sido feita.

## Revisão física: umidade, PDP e resfriamento do PSA (02/08/2026, commit `a53ef67`)

O autor testou o app deliberadamente atrás de furos físicos antes de partir
para simulação de defeitos, e achou dois reais:

**1. Vazão mássica "aumentando" depois do secador.** Não era bem isso —
`m_dot` na tabela de estados sempre foi vazão de AR SECO (convenção
psicrométrica padrão: só a água condensa, o ar seco não muda), então
ela nunca caía nos pontos de condensação, só a razão de umidade `w`
caía. Sem uma coluna de vazão TOTAL para comparar, parecia que a massa
"sumia sem explicação" até o secador. Adicionado `m_dot_total` (=
ṁ_seco·(1+w)) em cada ponto — essa sim cai a cada condensação, e de
novo (por purga, não secagem) no secador.

**2. Ciclo do secador sem tempo de resfriamento.** O rodízio de torres
alternava direto entre regenerando e adsorvendo, sem o tempo que a
alumina leva para esfriar antes de voltar a adsorver com eficiência —
fase física real, ausente do primeiro modelo. `psa_ciclo.py` reescrito
com 3 fases (Adsorvendo → Regenerando → **Resfriando**, nova duração
`t_resfriamento_min`). Consequência importante: a cobertura contínua
(sempre ≥1 torre adsorvendo) deixou de ser garantida por construção —
com N de torres insuficiente para o tempo de resfriamento, pode haver
um intervalo em que **nenhuma** torre seca o ar. O módulo não esconde
isso mais: calcula `n_adsorvendo_min`/`tempo_sem_secagem_min` e o app
mostra um alerta vermelho quando ocorre.

Isso levou a duas melhorias adicionais, feitas na mesma varredura:
- **PDP em cada ponto do trem** (não só no secador): nova inversão
  numérica (bisseção) da Eq. 10.7 em `nucleo.py` — a fórmula de Buck com
  os 3 parâmetros do livro não tem inversa fechada simples, então em vez
  de aproximar com a forma "Magnus" de 2 parâmetros (mais comum, mas
  diferente da equação do livro), a inversão é numérica sobre a própria
  `p_sat()`. Verificado por *round-trip* exato (erro < 1e-3°C) e por
  consistência física: pontos saturados pelo intercooler/aftercooler dão
  PDP = T exatamente, como deveria. Secador passou a entregar ar
  saturado no PDP "medido" (`pdp_real_c`) em vez de W=0 fixo (ar
  "infinitamente seco", sem base física) — liga de vez a leitura de PDP
  usada em `HI_des` ao restante do balanço de massa.
- **Terceira pergunta do autor, sobre umidade e potência**: por que a
  potência de compressão não sobe com a umidade do ar de admissão? A
  resposta correta **não** é "deveria subir" — para vazão volumétrica
  fixa (compressor de deslocamento positivo), `P·V=nRT` diz que o
  trabalho de compressão não depende de quais moléculas são admitidas
  (ar ou vapor), só do número total de mols. A lacuna real era outra: o
  app não reduzia o AR SECO realmente entregue por essa mesma vazão
  volumétrica quando a umidade sobe. Nova variável `m_dot_seco`
  (fórmula psicrométrica padrão ASHRAE, `v = (R_ar·T/P)·(1+1,6078·W)`)
  substitui `m_dot` em todo balanço de massa real (condensado, calor
  sensível, purga, tabela de estados) — a cadeia de potência
  (`v_dot_lp`/`v_dot_hp`) continua deliberadamente em `m_dot` original,
  sem essa correção, porque é ela que deve ficar ~invariante à umidade.
  **Armadilha evitada**: minha primeira ideia (antes de derivar com
  cuidado) era fazer a potência subir com a umidade — estaria errada.
  Só percebi ao aplicar `P·V=nRT` explicitamente. Se uma sessão futura
  for mexer aqui de novo: qualquer "correção de umidade" que reduza
  `v_dot_lp`/`v_dot_hp` (não só `m_dot_seco`) está repetindo esse erro.

12 testes novos nesta sessão, incluindo verificação de que a potência
varia menos de 1% entre UR 10% e 95% (mas o ar seco entregue cai ~4% e o
condensado sobe de 0,1 para 16 kg/h no mesmo intervalo) — 36 no total.

## Balanço térmico da carcaça do estágio LP — Eq. 9.6 (15/08/2026)

O autor perguntou se as equações do estágio LP já cobriam transferência de
calor nos equipamentos. Verificação (não só no app — no livro): a Eq. 5.5
(trabalho do estágio) trata calor só implicitamente via índice politrópico
$n$; o Capítulo 9 (Termodinâmica do Estágio LP) tem uma equação explícita
para o próprio equipamento — o balanço térmico da carcaça (Eq. 9.6,
$M_c c_c \, dT_c/dt = \dot Q_{\text{int}} - \dot Q_{\text{ext}} -
\dot Q_{\text{arref}}$) — que não estava implementada no app. Implementada
nesta sessão.

**Novas funções em `nucleo.py`** (seção "Carcaça e balanço térmico do
estágio LP"):
- `q_int_carcaca(w_estagio, eta_mec)`: proxy de $\dot Q_{\text{int}}$. O
  livro não fecha como calcular esse termo a partir de outras grandezas do
  capítulo — a simplificação adotada é a própria perda mecânica já embutida
  na Eq. 5.5 via $\eta_{\text{mec}}$ (potência que não realiza trabalho de
  compressão e fica como calor dentro da máquina): $\dot Q_{\text{int}} =
  \dot W \cdot (1-\eta_{\text{mec}})$.
- `temperatura_carcaca_regime(q_int, cond_ext, cond_arref, t_amb)`: $T_c$ em
  regime permanente ($dT_c/dt=0$), com $\dot Q_{\text{ext}}$ e $\dot
  Q_{\text{arref}}$ modelados como condutâncias lineares em $(T_c-T_{amb})$
  (lei de Newton do resfriamento) — convecção natural da carcaça vs.
  arrefecimento ativo/ventilação forçada do invólucro, dois termos
  separados como no livro.
- `constante_tempo_carcaca(m_c, c_c, cond_ext, cond_arref)`: $\tau_c =
  M_c c_c/(\text{cond}_{ext}+\text{cond}_{arref})$.
- `temperatura_carcaca(...)`: solução analítica de 1ª ordem $T_c(t) =
  T_{c,ss} + (T_{c0}-T_{c,ss})\cdot e^{-t/\tau_c}$ — mesma forma já usada
  para a rampa do VSD em `dinamica.py`, mas **não está fiada a nenhuma aba
  de tempo do app ainda** (só o valor de regime permanente é exibido na
  aba 1; a função existe pronta para uma futura integração temporal, ver
  "Pendências" abaixo).

**4 novos parâmetros ASSUMIDO** em `constantes.py`/sidebar (expander
"Carcaça do estágio LP — balanço térmico (Eq. 9.6)"): `m_carcaca` (300 kg),
`c_carcaca` (460 J/kg·K, calor específico típico do ferro fundido —
propriedade de material, não uma citação bibliográfica), `cond_ext_carcaca`
(10 W/K) e `cond_arref_carcaca` (20 W/K). Com os defaults do livro/app,
$\dot Q_{\text{int}} \approx 843\,$W, $T_c \approx 58\,^\circ$C
($\Delta T \approx 28\,^\circ$C acima dos 30 °C de ambiente), $\tau_c
\approx 77\,$min — ordens de grandeza fisicamente plausíveis para a carcaça
de um elemento compressor (conferido manualmente antes de fixar os
defaults, não são números de fábrica).

**Integração em `sistema.py`**: o cálculo entra logo após o estágio LP
(`w_lp`), antes do intercooler — 4 novos KPIs: `q_int_carcaca_w`,
`t_carcaca_c`, `delta_t_carcaca_c`, `tau_carcaca_min`. Exibidos na aba
"Operação estática" como um novo bloco de métricas, com legenda explicando
a simplificação (regime permanente, não transiente) e registrando
explicitamente que a **Eq. 9.7 (folga residual por dilatação térmica) não
foi implementada** — exigiria um modelo à parte para a temperatura do
rotor ($\Delta T_r$), que o livro não fecha e que o app não modela em
lugar nenhum hoje.

5 testes novos (`test_q_int_carcaca_proporcional_a_perda_mecanica`,
`test_temperatura_carcaca_regime_sem_calor_fica_no_ambiente`,
`test_temperatura_carcaca_regime_cresce_com_q_int_e_cai_com_condutancia`,
`test_temperatura_carcaca_transiente_converge_para_regime`,
`test_simular_expoe_carcaca_lp_eq_9_6`) — 41 no total, todos passando.
Verificado também que o app sobe sem erro em runtime (servidor iniciado e
testado com `curl`, depois encerrado — não ficou rodando ao fim da sessão).

**Fechamento no livro, mesma sessão**: as fórmulas de $\dot Q_{\text{int}}$,
$\dot Q_{\text{ext}}$/$\dot Q_{\text{arref}}$, $T_c$ regime e $\tau_c$ acima
não ficaram só no app — foram formalizadas como Eqs. 9.14-9.17 no
`compressores.tex` logo em seguida (commit `13826b9`), ver "Fechamento do
balanço térmico da carcaça — Eq. 9.6" no `CONTEXTO.md` principal. As duas
implementações usam exatamente o mesmo modelo, de propósito.

**Pendência aberta por este trabalho**: a função `temperatura_carcaca()`
(transiente completo) existe mas não está conectada a nenhuma simulação no
tempo — um candidato natural seria acoplá-la à aba "Dinâmica temporal"
(`dinamica.py`), mostrando $T_c(t)$ evoluindo junto com a pressão da rede
durante um evento de pico de demanda. Não implementado por não ter sido
pedido; só o valor de regime permanente está na aba 1 hoje.

## Parte II no app: VAE, PIML e MPC reais (fase 2 de 2 — 15/08/2026)

Continuação direta da fase 1 (EKF/PSO, seção abaixo). Autor pediu para
completar os 5 algoritmos + integração. **PyTorch e SciPy instalados**
no venv do app (antes não existiam): `pip install torch --index-url
https://download.pytorch.org/whl/cpu` (build CPU, ~192MB — a build padrão
do PyPI vem com CUDA, vários GB, desnecessário aqui) e `pip install
scipy`. `requirements.txt` atualizado: `scipy>=1.16` direto; `torch`
deixado **fora** da lista automática de propósito, com instrução em
comentário — o índice CPU dedicado não é o padrão do `pip install -r`.

**A Parte III (demo integrada) ficou pendente** — não implementada nesta
sessão; ver "Pendência" ao final desta entrada.

### VAE (`compressor_sim/vae.py`, Eqs. 20.4, 22.1-22.7)

Autoencoder variacional treinado sobre amostras sintéticas de operação
saudável (não existe dado de planta real). **Achado real ao testar**: a
primeira versão usava 16 features dominadas por pressões/temperaturas
que — mesmo achado já registrado para a aba "Dinâmica temporal" — são
**invariantes** a δ/L e R_f neste modelo (só dependem do ponto de
operação fixo). Um cenário claramente degradado (δ/L=0,015 contra
comissionamento 0,002) não disparava a anomalia porque 12 das 16
features não carregavam nenhum sinal. Corrigido: feature vector reduzido
a 12 grandezas, com `m_dot_seco` (sinal real de δ/L via Eq. 9.3)
explicitamente incluído — antes ausente por descuido — e ruído sintético
reduzido de 0,2% para 0,03% da leitura (o sinal físico de degradação é
da ordem de décimos percentuais; ruído maior o encobria por construção,
não por realismo de sensor). Limiar de disparo calibrado
estatisticamente (média + 3σ do erro de reconstrução em validação
saudável, Eq. 22.6) — não escolhido à mão. Resultado final verificado:
E_rec ≈ 0,2-0,6 em operação saudável, ≈ 11-12 em δ/L=0,015 (bem acima do
limiar ≈ 10-13, que varia por seed de treino).

### PIML (`compressor_sim/piml.py`, Eqs. 23.1-23.4)

Substituto treinado para prever [T_LP,out, T_HP,in, ṁ_seco,
Q̇_intercooler] a partir de [π, T_amb, δ/L, R_f, FAD], com resíduo
físico do balanço de energia do intercooler (forma algébrica em regime
permanente da Eq. 10.1 — este simulador não tem EDPs para diferenciação
automática, então o resíduo aqui é a contraparte estacionária dos
resíduos de conservação de massa/energia do livro, Eq. 23.2) avaliado em
pontos de colocação sem rótulo, inclusive fora da faixa de treino.
Balanceamento adaptativo de λ (Eq. 23.4) implementado de fato via
`torch.autograd.grad` nas magnitudes dos gradientes de cada termo.

**Bug real encontrado e corrigido**: a rede não aprendia nada — `L_data`
ficava travado em ~1,02 (espaço normalizado) por centenas de épocas,
mesmo com bastante treino. Causa: o resíduo físico é medido em watts
(escala ~10⁴, ao quadrado ~10⁶-10⁸), ordens de grandeza acima do erro de
dados já padronizado (~O(1)) — com `λ_inicial=1,0`, o primeiro passo de
otimização levava um gradiente de até ~1,4×10⁶, saturando todas as
unidades `tanh` da rede permanentemente (unidades mortas) antes que o
balanceamento adaptativo de λ tivesse qualquer chance de agir (ele só
corrige a cada 5 épocas, devagar demais para um choque no passo 0).
Corrigido normalizando o resíduo físico pelo próprio desvio-padrão de
Q̇ antes de elevar ao quadrado (não muda a física exigida, $\mathcal{F}=0$
continua $\mathcal{F}=0$, só evita o choque numérico) e reduzindo
`λ_inicial` para 0,1. Depois da correção: `L_data` cai de 1,10 para
~0,005 em 400 épocas, `L_physics` de 0,12 para ~0,0005, λ estabiliza
perto de 1,1-1,2. Erro médio de predição verificado: T_LP,out ≈0,9°C,
ṁ_seco ≈0,001-0,0014 kg/s, resíduo físico médio ≈55-65 W (livro é
explícito, Cap. 23 "Limitações e Cautelas": a penalização é fraca, o
resíduo deve ser medido, não presumido nulo — a UI reporta esse número
em vez de escondê-lo).

### MPC (`compressor_sim/mpc.py`, Eqs. 24.1/24.2)

Horizonte deslizante real (não um esquema simplificado): a cada passo,
`scipy.optimize.minimize` (L-BFGS-B) resolve a sequência ótima de
x_c(k) sobre um horizonte H usando a **mesma** integração de Euler do
balanço de massa do vaso/rede já usada em `dinamica.py` (Eq. 16.4/13.4)
como restrição de propagação — só x_c(0) é de fato aplicado antes de
reotimizar no passo seguinte (princípio da Fig. 24.1). Deliberadamente
**não** encadeia o substituto PIML como modelo de predição do MPC (ao
contrário da recomendação do Cap. 24 para sistemas caros de avaliar):
o balanço de massa já é uma expressão fechada barata o bastante para
ser avaliada milhares de vezes sem precisar de substituto — registrado
explicitamente no docstring do módulo para não parecer uma omissão.

**Achado real ao testar**: com os defaults de demanda do resto do app
(8 m³/min, ~97% da capacidade instalada), um evento de pico satura
qualquer controlador (MPC ou reativo) igualmente, e a comparação não
mostra diferença nenhuma. A UI do MPC usa sliders de demanda/pico
**próprios**, independentes do resto do app, com defaults deliberadamente
folgados (5 m³/min base, pico ×1,4). Com essa margem, verificado que o
MPC rastreia a pressão de referência com desvio médio ~4x menor que o
controle reativo (antecipa a demanda futura conhecida em vez de só
reagir ao instante atual) — resultado consistente entre o teste manual e
o teste via `pytest`.

### Verificação — Claude-in-Chrome indisponível a sessão inteira

A extensão nunca reconectou nesta sessão. Em vez de continuar caindo para
renderização de figuras isoladas, foi usado o **framework de teste
headless nativo do Streamlit** (`streamlit.testing.v1.AppTest`) — roda o
`app.py` inteiro (as 4 abas, todo o conteúdo de cada `with tab_x:`
executa a cada rerun, independente de qual aba está visualmente
selecionada) num harness que expõe qualquer exceção Python levantada
durante a execução, sem precisar de navegador. **Achado real, e a razão
de valer a pena registrar esta técnica para sessões futuras**: pegou um
bug de verdade que nem `pytest` nem `curl`/log jamais capturariam —
`StreamlitDuplicateElementId`, dois `st.slider("Épocas de treino", 100,
500, 300, 50)` idênticos (um para VAE, um para PIML) colidindo no ID
automático do Streamlit (baseado em label+parâmetros). Corrigido com
`key=` explícito nos 4 sliders de amostras/épocas de VAE e PIML.
Confirmado depois: `at.run()` sem exceção, 4 abas detectadas, todos os
`st.metric`/`st.subheader` esperados presentes com valores fisicamente
plausíveis (E_rec da VAE corretamente classificando o cenário de teste
como anômalo, MPC 76% melhor que o controle reativo no teste). Cache
(`st.cache_resource`) confirmado funcionando: 1ª execução ~14s, 2ª
execução (mesmo estado) ~4,9s.

**Recomendação para sessões futuras**: se o Claude-in-Chrome estiver
indisponível ao testar mudanças na UI deste app, usar `AppTest` antes de
recorrer a scripts de figura isolados — é mais barato e pega uma classe
inteira de bugs (colisão de IDs, exceções de import, `KeyError` em
`session_state`) que a verificação por função isolada não pega, porque
exercita o `app.py` real, com o Streamlit real, não uma reimplementação
paralela da mesma lógica.

**Achado colateral**: um caractere cirílico (`б` em vez de `b`) entrou
por acidente no docstring de `mpc.py` durante a escrita — pego por uma
varredura Unicode deliberada (`unicodedata.name()` procurando
`CYRILLIC`/`GREEK` fora do conjunto de letras gregas já usadas de
propósito no documento) logo depois de escrever os 5 módulos novos.
Vale repetir essa varredura ao escrever conteúdo novo extenso — o
caractere é visualmente quase idêntico ao Latin `b` e não haveria como
notar por leitura visual do código.

### Testes

10 testes novos (4 VAE, 4 PIML, 2 MPC) — **66 no total, todos passando**,
suíte completa em ~8-10s (o aumento vem do treino real de VAE/PIML
dentro dos testes, não simulação simplificada).

### Pendência desta fase

A **Parte III do app** (demo integrada replicando o Capítulo 28 do
livro — EKF→VAE→PIML→prognóstico→MPC/PSO como um pipeline único) não foi
implementada — os 5 algoritmos existem e funcionam cada um na sua própria
seção da aba "Gêmeo Digital", mas não há ainda uma orquestração que
encadeie a saída de um como entrada do próximo, na mesma aba/fluxo. Fica
para uma próxima sessão, se pedido.

## Parte II no app: EKF e PSO reais (fase 1 de 2 — 15/08/2026)

O autor pediu para implementar a Parte II e a Parte III do livro
(EKF/VAE/PIML/MPC/PSO) também no app, "preciso que isso apareça". Dado o
tamanho — 5 algoritmos + a integração da Parte III —, foi combinado
**fasear**: EKF e PSO primeiro (só NumPy, já disponível), VAE/PIML/MPC
depois (exigem PyTorch e SciPy, dependências novas, ainda não instaladas
nesta sessão). Esta entrada documenta a fase 1.

**Nova aba "🧠 Gêmeo Digital (EKF/PSO)"** — 4ª aba do app.

### EKF (`compressor_sim/ekf.py`, Eqs. 21.2/21.4/21.7/21.8)

O livro define o vetor de estado da Eq. 21.2 como $x=[\eta_{is,LP},
\eta_{is,HP}, \delta, R_f, \sigma_b]$ — mas só $\delta$ (folga, via Eq. 9.3)
e $R_f$ (fouling do intercooler, via Eq. 10.5) têm contraparte
**calculável** neste simulador; os demais dependeriam de um motor
elétrico/engrenagem modelados a um nível de detalhe que o app não tem.
Escopo do EKF aqui, portanto, **reduzido a esses dois estados**:

- **Estado** $x = [\delta/L, R_f]$; **medição** $z = [\dot m_{\text{seco}},
  T_{HP,in}]$ — os dois canais que de fato respondem a $x$ na cascata real
  (`nucleo.eficiencia_volumetrica` e `subsistemas.ua_com_fouling`).
- **Jacobianos numéricos** (diferenças finitas centradas) em vez de
  analíticos — chamam `sistema.simular()` diretamente como $g(x)$, então
  não há necessidade de derivar a cascata inteira à mão; tecnicamente
  equivalente à Eq. 21.3, mais barato de manter correto.
- **Modelo de transição $f(x)=x$** (passeio aleatório) — o livro não fecha
  uma dinâmica própria de evolução para $\delta$/$R_f$, então a incerteza
  de processo $Q$ absorve a deriva esperada.
- Forma de Joseph (Eq. 21.8) para a covariância, NIS (Eq. 21.7) para
  auto-auditoria do filtro.
- **Demo na UI**: o cenário é configurável (valor verdadeiro inicial/final
  de $\delta/L$ e $R_f$ ao longo de um horizonte de passos, níveis de
  ruído de medição e de processo) — default reproduz a mesma deriva do
  Capítulo 28 do livro ($\delta/L$: 0,002→0,009). **O filtro sempre parte
  de uma crença fixa de comissionamento** ($\delta/L=0{,}002$, $R_f=0$),
  independente do valor verdadeiro configurado, para que a convergência
  mostrada seja estimação de verdade, não o filtro sabendo a resposta de
  antemão. Gráficos: estimativa vs. verdade com banda $\pm1\sigma$ para
  cada estado, e NIS ao longo do tempo com a referência $n_z=2$.

### PSO (`compressor_sim/pso.py`, Eqs. 24.3/24.4)

Implementação padrão (peso de inércia decaindo linearmente de 0,9 a 0,4,
mesma recomendação do Cap. 24). Aplicado a um problema real do app:
minimizar o SPC (Eq. 11.11) variando a pressão de rede $\pi$, sujeito a
manter a autonomia do vaso (Eq. 16.5) acima de um mínimo — restrição
imposta por penalidade (PSO básico não trata restrições nativamente),
rodado sob demanda via botão (não a cada mudança de slider, por ser mais
caro que o resto do app).

**Achado ao testar**: com o default original da restrição (5 min) e os
demais defaults do app (vaso de 2 m³, demanda de 8 m³/min), a autonomia
real nunca chega a 5 min em nenhum ponto da faixa de $\pi$ pesquisada
(5–12 bar) — o custo fica monotônico e o "ótimo" cai exatamente na borda
superior da busca, já resolvido na 1ª iteração, produzindo um gráfico de
convergência sem nenhuma variação visível (não é bug — é o comportamento
correto de PSO/penalidade para um problema sem mínimo interno na região
viável). Corrigido trocando o default da restrição para 1 min, valor que
cruza a curva de autonomia dentro da própria faixa de $\pi$ pesquisada e
produz um ótimo interno de verdade ($\pi\approx9{,}9$ bar com os demais
defaults) — com uma nota explicando o caso de borda para quando o autor
reconfigurar a restrição para um valor mais alto.

### Testes e verificação

7 testes novos (2 de sanidade da medição EKF, 2 de convergência/deriva do
EKF, 1 de calibração do NIS, 3 do PSO — mínimo quadrático conhecido,
histórico não regride, minimização real de SPC) — **56 no total, todos
passando**. Claude-in-Chrome continuou desconectado nesta sessão (mesma
limitação já registrada) — verificado chamando `ekf.simular_ekf()` e
`pso.otimizar()` diretamente com os mesmos parâmetros do `app.py`,
salvando as figuras geradas e inspecionando visualmente: banda de
incerteza do EKF estreitando corretamente ao longo dos ciclos, NIS
oscilando em torno da referência teórica, convergência do PSO com forma
de curva real (não mais reta) após a correção do default. Log do servidor
sem traceback, `/_stcore/health` respondeu `ok`, servidor encerrado ao
final.

### Pendência desta fase

VAE (detecção de anomalia), PIML (substituto físico) e MPC (controle
preditivo) ficam para uma próxima sessão — exigem instalar PyTorch (VAE/
PIML) e SciPy (MPC), gerar dados de treino sintéticos (não existe dado
real), e são significativamente mais trabalhosos de fazer bem (o próprio
livro já registra, na Seção "Limitações e Cautelas" do Cap. 23, que PINNs
são notoriamente mais difíceis de convergir que redes convencionais). A
Parte III (Capítulo 28) do app — a demonstração integrada — depende dos
três, então também fica para depois.

## Gráficos temporais: temperatura do leito PSA e P/T por ponto do trem (15/08/2026)

O autor pediu gráficos "em tempo real" das secadoras, além de P/T de
entrada/saída de cada parte do sistema. Duas questões de escopo
clarificadas com o autor antes de implementar: (1) sobrepor P/T nos 3
gráficos já existentes da aba PSA, em vez de um gráfico novo separado; (2)
P/T de cada ponto do trem evoluindo no tempo, sincronizado com a aba
"Dinâmica temporal" (não só a tabela/gráfico estático da aba 1).

**Achado importante antes de implementar o item 2**: neste modelo, a
pressão e a temperatura em cada ponto do trem (`sistema.simular()`)
dependem só do ponto de operação fixo — pressão de rede, temperaturas
ambiente/água, índice politrópico — **nunca da vazão** (`fad_m3_min`).
Um compressor de deslocamento positivo a razão de pressão fixa entrega o
mesmo P/T em qualquer fração de carga do VSD; só a vazão mássica muda.
Isso significa que "re-simular a cascata inteira a cada passo de tempo"
geraria exatamente os mesmos valores em todo instante — **redundante e
caro** (chamar `sistema.simular()` centenas/milhares de vezes por
recarga da página) para um resultado que já é conhecido de antemão.
Implementação adotada em vez disso: usar os valores de `res["nos"]` (já
calculados uma vez) e mascará-los com `NaN` nos instantes em que o
compressor está parado (`din["x_c"] <= 0.02`) — no modo VSD isso nunca
acontece (`x_c_min` = 30% por padrão), então as linhas ficam contínuas;
no modo Carga/Alívio, as linhas **somem** durante os intervalos de
alívio, mostrando o padrão liga/desliga real. Muito mais barato
(nenhuma chamada extra a `simular()`) e tão correto quanto a
re-simulação completa, dado que o resultado seria idêntico.

**Novo gráfico na aba "Dinâmica temporal"**: dois painéis lado a lado
(Pressão × tempo, Temperatura × tempo), uma linha por ponto do trem (6
pontos, mesma paleta `tab10`), com legenda e a explicação acima em
`st.caption()` — para o autor não interpretar "linhas retas" como bug.

**Aba "Secagem PSA"**: `psa_ciclo.simular_ciclo_psa()` ganhou dois
parâmetros novos, `t_entrada_c` (temperatura na entrada do secador — usa
`res["nos"][4]["t_c"]`, a saída do aftercooler) e `delta_t_regen` (salto
do aquecedor de regeneração, Eq. 3.3, já existente em `constantes.py`).
Nova saída `temp_c[torre, tempo]`: perfil **triangular** por torre —
constante em `t_entrada_c` durante a adsorção, sobe linearmente até
`t_entrada_c + delta_t_regen` durante a regeneração, desce linearmente de
volta durante o resfriamento. Mesma simplificação de modelagem já
adotada para a recuperação de capacidade (`q_norm`) — o Cap. 15 não
fecha a dinâmica térmica do leito, então o app usa rampas lineares em vez
de inventar uma constante de tempo não citada no livro. Sobreposto como
eixo Y secundário (tracejado) no gráfico "Capacidade de adsorção
normalizada por torre" já existente — não um gráfico novo. Pressão de
entrada/saída do secador é constante no horizonte (mesma razão do achado
acima) e é reportada como texto na legenda, não como linha reta redundante.

**Testes**: 1 novo (`test_psa_temperatura_do_leito_sobe_na_regeneracao_e_
desce_no_resfriamento`) — 49 no total, todos passando; os 4 testes já
existentes de `simular_ciclo_psa` foram atualizados com os 2 parâmetros
novos (obrigatórios, sem default, mesmo estilo dos demais parâmetros da
função).

**Verificação**: Claude-in-Chrome ficou indisponível nesta sessão
(extensão desconectada) — verificado em vez disso chamando as mesmas
funções de plotagem do `app.py` diretamente via script Python (mesmos
parâmetros, mesmas chamadas a `dinamica.simular_transiente`/
`psa_ciclo.simular_ciclo_psa`), salvando as figuras em PNG e inspecionando
visualmente: painel P/T por ponto mostra linhas constantes com um gap
visível no modo Carga/Alívio (confirmando o comportamento liga/desliga);
gráfico da PSA mostra o perfil triangular de temperatura corretamente
sincronizado com as transições de estado de cada torre. Log do servidor
sem traceback, `/_stcore/health` respondeu `ok`. Servidor encerrado ao
final — não ficou rodando.

## Motor, invólucro/Hood e tubulação interestágios (Eqs. 4.10-4.12, 2.1, 2.4, 5.15 — 15/08/2026)

Continuação direta da mesma sessão: uma auditoria pedida pelo autor sobre
cobertura de perdas termodinâmicas/fluidas no livro achou três lacunas
reais (motor tratado como caixa-preta, tubulação interestágios sem ΔP, e
uma inconsistência real — a Eq. 9.6 usando $T_{amb}$ mesmo quando a
carcaça está dentro do mesmo invólucro do motor/gearbox, achado a partir
de uma observação do autor sobre Hoods acústicos offshore). As três foram
fechadas no livro primeiro (ver `CONTEXTO.md`, "Auditoria de perdas
termodinâmicas/fluidas e acoplamento com o Hood") e depois replicadas
aqui, incluindo a construção de um **subsistema de motor elétrico do zero**
— o app não tinha nenhuma representação do Capítulo 4 até esta sessão.

**Motor (Eqs. 4.10-4.12), 3 funções novas em `nucleo.py`**:
`potencia_entreferro()`, `perdas_motor()`, `eficiencia_motor()`.
Simplificação deliberada: em vez de reconstruir o circuito equivalente
completo do motor (Eqs. 4.4/4.5, que exigiriam parâmetros de placa como
$V_{th}$, $R_{th}$, $X_{th}$, $R_r$, $X_r$ — não disponíveis neste app),
$P_{ag}$ é obtido invertendo a Eq. 4.12 a partir da potência de eixo já
calculada pelo resto da cascata ($P_{eixo,mot} = W_{LP}+W_{HP}+$perdas
$V_i$, **sem** o aquecedor de regeneração PSA, que é carga elétrica
resistiva, não potência mecânica de eixo). Dois parâmetros novos ASSUMIDO:
`s_motor` (escorregamento, 0,02) e `p_fixas_motor` (perdas fixas de
ensaio, 1500 W).

**Invólucro/Hood (Eqs. 2.1/2.4), 2 funções novas**: `calor_gerado_hood()`
e `temperatura_hood_regime()`. $\dot Q_{\text{casco}}$ (Eq. 2.1) é
identificado com $\dot Q_{\text{int}}$ da carcaça (Eq. 9.14) — a mesma
identidade de regime permanente derivada no livro, que evita precisar de
$T_c$ para calcular $T_{\text{hood}}$. As perdas de VSD+gearbox (Eqs.
4.3/5.2) não são decompostas neste app — agregadas num único parâmetro
ASSUMIDO `p_loss_hood_outros` (2000 W), documentado como simplificação
explícita (o livro tem os três termos separados; o app não implementa
VSD nem decomposição de gearbox). Novo parâmetro `m_dot_vent` (vazão de
ventilação forçada, 0,5 kg/s).

**Acoplamento com a carcaça (Eq. 9.16 emendada)**: novo toggle
`hood_enclausurado` (bool, default `True`) — quando ligado, a Eq. 9.16 usa
$T_{\text{hood}}$ como referência de convecção em vez de $T_{amb}$; quando
desligado (instalação a céu aberto), volta ao comportamento original desta
mesma sessão. **O default mudou de comportamento em relação à primeira
implementação da Eq. 9.6** (mais cedo nesta sessão): antes, $T_c$ sempre
usava $T_{amb}$ diretamente; agora, por padrão (`hood_enclausurado=True`),
usa $T_{\text{hood}}$ — com os defaults do livro/app, $T_c$ default subiu
de ≈58°C para ≈68°C, porque $T_{\text{hood}}$ (≈40°C) já é mais quente que
o ambiente puro (30°C). Isso é uma correção física, não uma regressão —
documentado aqui para não confundir quem comparar números com a sessão
anterior.

**Tubulação interestágios (Eq. 5.15)**: função `delta_p_linha()`
(Darcy-Weisbach). Calculada como diagnóstico entre a descarga do estágio
LP e a sucção do HP (**um trecho representativo**, não os três segmentos
separados do livro — LP→intercooler, intercooler→HP, HP→aftercooler —,
simplificação para não reestruturar toda a cascata de pressão existente).
**Não realimenta** a cascata principal (`p_inter` segue sendo usado como
antes em todo o resto do cálculo) — reportada como KPI (`dp_linha_mbar`,
`p_hp_suc_efetiva_bar`), mesma lógica que o PDP já usa no app (grandeza
informativa por ponto, sem alterar o balanço de massa). Três parâmetros
novos ASSUMIDO: `f_d_linha` (0,02), `l_linha` (3 m), `d_linha` (0,10 m —
ajustado de um primeiro valor de 0,05 m depois de notar velocidade de
escoamento fisicamente alta demais, ~39 m/s, no valor original; 0,10 m dá
~10 m/s, dentro da faixa de projeto típica).

7 testes novos (funções puras + 3 testes de integração via `simular()`,
incluindo o que verifica que `hood_enclausurado=True` produz $T_c$ maior
que `False`) — 48 no total, todos passando.

**Teste real no navegador (Claude-in-Chrome), não só `curl`**: subiu o
servidor, abriu `localhost:8501` e navegou pela UI de fato — abriu os 3
expanders novos na barra lateral ("Motor e invólucro (Hood)", "Carcaça do
estágio LP", "Tubulação interestágios") e conferiu que todos os controles
(escorregamento, perdas fixas do motor, vazão de ventilação, perdas de
VSD/gearbox, fator de atrito de Darcy, comprimento/diâmetro da linha)
aparecem com os defaults corretos. Os 3 blocos de métricas novos na aba
"Operação estática" renderizam com os valores exatos já conferidos por
`pytest`/`python -c` ($\eta_{mot}=94{,}7\%$, $T_{\text{hood}}=40{,}4\,^\circ$C,
$T_c=68{,}5\,^\circ$C, $\Delta P_{\text{linha}}=0{,}73\,$mbar). **Testado o
toggle "Compressor dentro de invólucro (Hood)?" ao vivo**: desmarcar fez
$T_{\text{referência}}$ cair de $40{,}4$ para $30{,}0\,^\circ$C (= $T_{amb}$
exato) e $T_c$ cair de $68{,}5$ para $58{,}1\,^\circ$C — reativo e correto,
sem precisar recarregar a página. Console do navegador sem erros/exceções.
Servidor encerrado ao final — não ficou rodando ao fim da sessão.

**Pendências abertas por este trabalho**: VSD (Eq. 4.3) e decomposição de
perdas da gearbox (Eq. 5.2) continuam sem representação própria no app —
`p_loss_hood_outros` é um placeholder agregado, não um modelo. Os três
segmentos de tubulação do livro (Eq. 5.15) foram reduzidos a um só. Se uma
sessão futura quiser fechar esses pontos, o padrão já está estabelecido
(funções puras em `nucleo.py`, parâmetros ASSUMIDO em `constantes.py`,
threading em `sistema.py`).

## Estimação de parâmetro por problema inverso — EKF aumentado e PIML (Cap. 28.1/23.8, 16/08/2026)

Portadas para o app as duas adições do livro desta mesma sessão (ver
`CONTEXTO.md`, "Capítulo 28 implementado" e a entrada do Cap. 23.8): K, o
coeficiente de vazamento fixo da Equação 9.3, deixa de ser um valor de
catálogo assumido e passa a ser **identificado a partir de dados**, por dois
caminhos complementares — exatamente o par que o livro descreve (online via
EKF, offline via PINN).

**Achado real, e por que os dois módulos não foram uma tradução direta do
livro**: a primeira versão de cada mecanismo divergiu. No EKF aumentado, com
os defaults do resto do app (δ/L=0,002, ruído de sensor 1e-4 kg/s), o efeito
de K sobre ṁ_seco é menor que o próprio ruído de medição — o problema é mal
condicionado por construção nesses valores (K multiplica δ/L na Eq. 9.3, e
δ/L de comissionamento é pequena de propósito). No PIML, o resíduo da Eq. 9.3
reimplementado à mão em PyTorch (para ser diferenciável em Ξ) inicialmente
ignorava a correção psicrométrica que `sistema.py` já aplica a `m_dot_seco`
(`m_dot/(1+1,6078·w_amb)`) — um viés sistemático de alguns % que dominava
completamente o efeito real de Ξ (da ordem de décimos de %), fazendo Ξ
divergir para >0,7 tentando compensar um viés que não tinha relação com ele.
Confirmado isolando o resíduo contra os próprios rótulos reais (sem rede):
zero exatamente no K real só depois da correção.

### EKF com estado aumentado (`compressor_sim/ekf.py`, Eqs. 28.1/28.2)

`medicao_aumentada()` e `simular_ekf_aumentado()`, novos, ao lado das funções
de 2 estados já existentes (preservadas sem alteração de comportamento —
`passo_ekf()` ganhou um parâmetro `medicao_fn` injetável, default o
`medicao()` original, para reaproveitar o mesmo ciclo predição-correção sem
duplicar código). Estado x_aug = [δ/L, R_f, K]. Implementa os dois regimes de
$Q_\Lambda$ da Seção 28.1 via `q_proc_calibracao`/`q_proc_operacao` e
`n_passos_calibracao`: na janela de calibração, δ/L e R_f têm Q quase nulo
(tratados como conhecidos) enquanto K é livre; depois, K "congela" (Q
pequeno) e δ/L volta a acompanhar deriva como no EKF original. **δ/L maior
durante a calibração identifica K melhor** (efeito escala com δ/L,
Eq. 9.3) — por isso a demo da UI usa δ/L=0,010 como referência de
calibração, não o valor de comissionamento (0,002) do resto do app.

### PIML — identificação por problema inverso (`compressor_sim/piml.py`, Eq. 23.5)

`treinar_com_identificacao()`, nova, ao lado de `treinar()` (preservada sem
alteração). Mesma perda híbrida e balanceamento adaptativo de λ (Eq. 23.4) já
existentes, mas o resíduo físico é `_residuo_inverso()` — a Eq. 9.3 (balanço
mássico), com Ξ como `torch.nn.Parameter` otimizado no mesmo `Adam` dos
pesos da rede, não o resíduo de energia do intercooler (Eq. 23.2, que
continua intocado em `treinar()`). `_residuo_inverso()` recalcula a razão de
umidade ponto a ponto via `nucleo.razao_umidade()` **fora** do grafo do
PyTorch (não depende de Ξ nem dos pesos, só de `t_amb`/`ur_amb`/`p_amb`) para
replicar exatamente a correção psicrométrica de `sistema.py` — ver o achado
acima.

### Testes e verificação

5 testes novos (3 EKF aumentado, 2 PIML) — **71 no total, todos passando**.
Tolerâncias calibradas numericamente antes de escrever os `assert`s (rodando
os cenários via `python -c` e inspecionando a convergência), não escolhidas
a priori — Ξ/K convergem de forma robusta entre sementes e pontos de partida
diferentes (testado 0,02 e 0,09 como crença inicial, 3 seeds), sempre dentro
de ±0,003 do K real (0,05).

**Verificação em duas camadas**: `streamlit.testing.v1.AppTest` primeiro (0
exceções, 4 abas, todos os `st.metric` novos com valores plausíveis) e depois
**Claude-in-Chrome real** (extensão conectada nesta sessão, ao contrário das
duas sessões anteriores) — servidor subido, navegado até a aba "Gêmeo
Digital", as duas seções novas roladas e conferidas visualmente: o gráfico de
K mostra convergência de 0,03 (crença inicial) para a faixa 0,050-0,056
durante a janela de calibração (fundo cinza), permanecendo estável depois; o
δ/L fica plano na janela e retoma a deriva depois; o gráfico de Ξ do PIML
mostra a mesma assinatura de overshoot-e-correção já documentada para λ em
sessões anteriores, estabilizando perto de 0,047. Console do navegador sem
erros. Servidor encerrado ao final — não ficou rodando.

**Símbolos novos na UI/código**: nenhum parâmetro `ASSUMIDO` novo em
`constantes.py` — K, η_mec e ζ_ref já existiam como constantes fixas
(`K_FOLGA`, `ETA_MECANICA`, `ZETA_FILTRO`); esta sessão os torna
*identificáveis*, não os introduz. `xi_inicial`/`k_inicial_aum` (crenças de
partida, deliberadamente diferentes do valor real) são parâmetros de cenário
da demo, não do modelo físico.

**Pendência aberta por este trabalho**: apenas K (Eq. 9.3) foi portado dos
três parâmetros de Λ do livro (K, η_mec, ζ_ref) — η_mec e ζ_ref não têm
contraparte observável nos dois canais de medição atuais do EKF (ṁ_seco,
T_HP,in) nem no resíduo de energia/massa já implementados no PIML; estendê-los
exigiria um canal de medição novo (ex. potência elétrica para η_mec, ΔP do
filtro para ζ_ref) e fica para uma sessão futura, se pedido.

**Commitado em `da20c83`.**

## Documentação de implementação criada (16/08/2026)

A pedido do autor, três documentos novos em `aplicativo/`, complementares a
este arquivo (que continua sendo o registro cronológico de sessão — os três
abaixo são a versão destilada e estável, para humanos que não precisam do
histórico completo):

- **`IMPLEMENTACAO.md`**: arquitetura (diagrama de dependência entre
  módulos em texto), filosofia de projeto (gray-box, rastreabilidade a
  equação do livro, convenção `m_dot`/`m_dot_seco`, uma unidade
  representativa + escala de planta), as 4 abas, e por que os algoritmos de
  IA têm escopo reduzido frente ao vetor completo do livro.
- **`GUIA_CODIGO.md`**: cada módulo de `compressor_sim/` explicado, na
  ordem de dependência (constantes → núcleo → subsistemas → sistema →
  dinâmica/PSA → EKF/VAE/PIML/MPC/PSO → app.py) — inclui o passo a passo
  dos 8 estágios de `sistema.simular()`.
- **`MANUTENCAO.md`**: checklist para adicionar equação nova, cuidados
  específicos para estender os algoritmos de IA (destilados dos bugs reais
  desta e de sessões anteriores — verificar resíduo contra rótulos reais
  antes de treinar, normalizar resíduo pela própria escala, checar
  observabilidade do parâmetro antes de depurar convergência), gestão de
  dependências (torch fora do `requirements.txt`, motivo), protocolo de
  verificação de UI (Claude-in-Chrome > AppTest > nunca só pytest),
  disciplina de sincronia livro↔app, e a lista de escopo fora (resumo
  vivo — a versão completa continua na seção "Pendências conhecidas" deste
  arquivo).

`README.md` também atualizado (estava desatualizado desde antes do EKF/VAE/
PIML/MPC/PSO existirem — só citava os 4 módulos originais da cascata
estática) e agora linka os três documentos novos.

**Nada foi commitado ainda** — aguardando revisão do autor. **Atualização**:
commitado em `166040b`, junto com o slide novo do Beamer (ver `CONTEXTO.md`).
Também verificado ao vivo no navegador (Claude-in-Chrome, a pedido do
autor): servidor subido, aba "Gêmeo Digital" aberta, roladas e conferidas as
duas seções desta entrada — a extensão desconectou entre mensagens no meio
da verificação (precisou reconectar, comportamento já visto em sessões
anteriores) mas os gráficos de convergência de K (EKF aumentado, ~0,054) e
de Ξ (PIML, ~0,047) renderizaram corretamente, ambos perto do K real
(0,05). Servidor encerrado ao final.

## Uso de GPU (CUDA) quando disponível (16/08/2026)

O autor notou, testando ao vivo, que o app roda mas a GPU (RTX 4070 Laptop,
visível via `nvidia-smi`) não é usada, e pediu para ajustar o
`requirements.txt` para "optar pelo melhor build de acordo com a
configuração do computador" e remover a restrição CPU-only.

**`compressor_sim/torch_device.py` (novo módulo)**: um único ponto de
decisão, `obter_device()`, que devolve `torch.device("cuda")` se
`torch.cuda.is_available()`, senão `"cpu"` — resultado cacheado (consultar
o driver não é gratuito). Reaproveitado por `vae.py` e `piml.py`, em vez de
cada um decidir por conta própria.

**`vae.py`/`piml.py`**: todo `torch.tensor(...)` que entra no laço de
treino ganhou `device=device`; os dois modelos (`VAE`, `SubstitutoPIML`) e
o parâmetro treinável `xi` (problema inverso, Eq. 23.5) são criados/movidos
para `device` antes do otimizador; toda leitura de volta para NumPy
(`prever()`, `erro_reconstrucao()`) passou a usar `.cpu().numpy()` em vez
de `.numpy()` — necessário porque um tensor em GPU não converte direto
para NumPy. `_residuo_inverso()` (problema inverso do PIML) ganhou um
parâmetro `device` explícito, propagado dos dois pontos onde é chamada
dentro de `treinar_com_identificacao()`; sem isso, os tensores que a
função cria internamente (a partir de `entradas_coloc`, um array NumPy)
ficariam na CPU enquanto o resto do grafo está na GPU, e o PyTorch levanta
`RuntimeError` por tensores em devices diferentes na mesma operação — essa
foi a única armadilha real desta mudança, pega e corrigida antes de rodar
o treino completo.

**`requirements.txt`**: a restrição CPU-only removida — `torch` volta a
ser instalado do índice padrão do PyPI (build com CUDA embutido,
funciona em máquinas com ou sem GPU NVIDIA; a parte CUDA só fica sem uso
se não houver GPU). Comentário atualizado explicando a troca.

**Instalação de fato refeita nesta sessão** (não só o `requirements.txt`
editado): `pip uninstall torch` seguido de `pip install "torch>=2.4"` no
venv do autor — build CPU (`2.13.0+cpu`) trocado por build CUDA
(`2.13.0+cu130`), download de ~2GB de pacotes `nvidia-*`/`cuda-*`
adicionais. `torch.cuda.is_available()` confirmado `True`, GPU identificada
corretamente como "NVIDIA GeForce RTX 4070 Laptop GPU".

**Verificação em três camadas**: (1) `pytest` — 71/71 continuam passando
sem nenhuma mudança de tolerância; (2) checagem direta de que os modelos
treinados ficam de fato em `cuda:0` (`next(modelo.parameters()).device`),
não só que `torch.cuda.is_available()` retorna `True`; (3) `nvidia-smi`
amostrado durante um treino real (2000 amostras, 1500 épocas) — utilização
de GPU saiu de 0% para 10% e memória alocada subiu de 296 para 354 MiB,
confirmando atividade real na GPU, não só detecção. `AppTest` confirmado
sem exceções depois da reinstalação do torch.

**Achado honesto, registrado para não gerar expectativa errada**: para o
tamanho atual de rede (5→48→48→4 no PIML, 12→32→32→~12 no VAE) e dataset
(centenas a poucos milhares de amostras), o ganho de velocidade da GPU é
modesto — 10% de utilização não é uma carga que satura o hardware. A GPU
está genuinamente em uso agora, mas o benefício prático maior viria se o
escopo crescer (redes maiores, mais amostras, treino repetido em lote) —
exatamente o cenário da pendência de "treino sobre múltiplos mecanismos de
falha simultaneamente" registrada em `../CONTEXTO.md`.

**Nada foi commitado ainda** — aguardando revisão do autor.

## Estado atual

Código compila sem erro de sintaxe, **66/66 testes passam**
(`venv/bin/pytest tests/ -q`, ~8-10s) — 41 após a Eq. 9.6, mais 7 do
motor/Hood/tubulação, mais 1 da temperatura do leito PSA, mais 7 do
EKF/PSO, mais 10 de VAE/PIML/MPC (ver "Parte II no app: VAE, PIML e MPC
reais", "Parte II no app: EKF e PSO reais", "Gráficos temporais" e
"Motor, invólucro/Hood e tubulação interestágios" acima). 4ª aba do app
("🧠 Gêmeo Digital") cobre os 5 algoritmos da Parte II — EKF, PSO, VAE,
PIML, MPC — em 5 módulos novos (`compressor_sim/{ekf,pso,vae,piml,mpc}.py`).
**PyTorch e SciPy agora instalados** no venv (antes só NumPy) —
`requirements.txt` atualizado, `torch` fica de fora da instalação
automática de propósito (índice CPU dedicado, ver seção acima).

**Servidor Streamlit ESTÁ RODANDO no momento** (`localhost:8501`,
processo em background) — reiniciado pela última vez após a correção do
bug de colisão de `key` dos sliders de VAE/PIML, com o código final desta
sessão. Verificado sem exceção via `streamlit.testing.v1.AppTest`
(Claude-in-Chrome ficou indisponível a sessão toda — ver a seção acima
para o porquê de usar `AppTest` em vez de renderização isolada). Commit mais recente do app: `a9c5059` (15/08/2026, fase 2/VAE-PIML-MPC,
commitado logo após esta entrada ser escrita).

O diretório `aplicativo/` foi commitado em 01/08/2026 (commit `693a2c6`,
junto com este arquivo e as linhas de `.gitignore` para
`aplicativo/venv/`/`aplicativo/**/__pycache__/`, a pedido explícito do
autor). O commit ficou escopado só ao aplicativo — outras mudanças
pendentes na árvore de trabalho na mesma hora (correções de diagramação do
`compressores.tex` via `dicas_kimi.md`, mais o trabalho não commitado de
29-31/07 já descrito no `CONTEXTO.md` principal) foram deixadas de fora
deliberadamente, incluindo as outras duas mudanças de `.gitignore`
(`*.lof`/`*.lot` do livro e `.claude/settings.local.json`) que não tinham
relação com o app. **Commit mais recente do app**: `3b9e376` (15/08/2026,
balanço térmico da carcaça — ver seção acima); use `git log -- aplicativo/`
em vez desta nota para o histórico completo e atualizado.

**Este arquivo é deliberadamente separado do `CONTEXTO.md` principal** — a
pedido do autor, não é referenciado a partir de lá. Sessões futuras que só
lerem o `CONTEXTO.md` principal não vão saber que este arquivo existe;
confira sempre se `aplicativo/` foi tocado antes de assumir que não há
contexto para ele.

## Reorganização visual: 6 abas, tema profissional, upload de instrumentação (16/08/2026)

Pedido do autor: "melhorar a aparência do aplicativo, com uma visão mais
profissional e abas superiores ou laterais com ícones ou abreviaturas e
uma aba configurações para definição de diversos parâmetros que não devem
mudar frequentemente. Também preciso de uma área para incluir um arquivo
excel ou csv com as variáveis disponíveis medidas e o layout e locais onde
ficam as variáveis." Duas perguntas de escopo resolvidas antes de
implementar (via pergunta direta ao autor): abas continuam no topo (não
lateral — a barra lateral já é usada para parâmetros, virar navegação
colidiria); o upload de instrumentação é só referência/documentação
(não alimenta a simulação) e espelha as colunas da Tabela 18.1 do livro.

**Mudanças em `app.py`** (reorganização grande, ~1470 linhas):
- `st.tabs([...])` passou a ser criado **antes** de `params = {...}` (não
  depois, como era) — necessário porque a nova aba "Configurações" precisa
  renderizar e atribuir suas variáveis Python antes de `params` ser
  montado. Os corpos de `tab_est`/`tab_din`/`tab_psa`/`tab_gd` continuam
  onde estavam, só a criação dos objetos de aba subiu. Ver `GUIA_CODIGO.md`
  § `app.py` para a ordem completa.
- Nova aba **🎛️ Configurações**: todo parâmetro de geometria de
  equipamento (massa térmica da carcaça, tubulação, motor/Hood, PSA
  topologia/sintonia) e todo hiperparâmetro de algoritmo (épocas, amostras,
  σ de ruído, Q de processo, enxame do PSO) — a maior parte do que antes
  vivia numa única barra lateral de ~90 controles. Organizada em 2 colunas
  de `st.expander`s.
- Barra lateral **reduzida a 6 expanders**: Ambiente, Compressor (só π e
  δ/L — ponto de operação), Resfriamento/secagem (só T_água e R_f —
  estado medido/atual), Vaso pulmão/rede (só demanda), Dinâmica temporal
  (só horizonte/modo/evento/fator), Secagem PSA (só horizonte + ΔP/PDP
  reais medidos). Critério de corte: fica na barra lateral o que descreve
  a *condição do momento*; vai para Configurações o que descreve *esta
  máquina* ou *este experimento*.
- Nova aba **📂 Dados Medidos**: `st.file_uploader` (.xlsx/.csv) +
  `pd.read_csv`/`pd.read_excel`, comparado contra uma tabela de referência
  embutida (cópia literal da Tabela 18.1 do livro, 24 linhas, 9 pontos
  A-I — conferida via `Read` direto do `compressores.tex` antes de
  transcrever, não de memória). Calcula cobertura (quantos dos 9 pontos
  aparecem na coluna "Ponto" do arquivo enviado) e lista os que faltam.
  Testado ao vivo via Claude-in-Chrome com um CSV de 4 linhas (pontos A,
  B, C, H) — reportou corretamente "4/9" cobertos e "D, E, F, G, I"
  faltando.
- **7 captions com referência stale a "barra lateral"** corrigidas para
  apontar à aba Configurações, depois que os widgets correspondentes
  foram movidos (`grep -n "barra lateral" app.py` antes e depois da
  mudança, um por um) — inclui os captions do motor/Hood, carcaça, EKF,
  PSO, e MPC. Um caso (`_FAIXAS_PIML_APP`, faixa de δ/L de treino do PIML
  inverso) **não** foi corrigido por não ser widget nenhum, sempre foi uma
  constante hardcoded — texto já estava impreciso antes desta sessão,
  fora do escopo desta mudança.
- `.streamlit/config.toml` novo: tema com a mesma paleta de
  `scripts/gen_figuras.py` (NAVY `#1f3b57`, BLUE `#2b6cb0`) e
  `toolbarMode = "minimal"` (esconde o menu de deploy do Streamlit).
- `pandas`/`openpyxl` adicionados a `requirements.txt` (pandas já vinha
  como dependência transitiva do Streamlit, mas não estava declarado
  explicitamente; openpyxl não estava instalado — sem ele, `pd.read_excel`
  falha em arquivos `.xlsx`).

**Verificação**: `venv/bin/pytest tests/ -q` — 71/71 (módulos de cálculo
não foram tocados, só `app.py`). `streamlit.testing.v1.AppTest` — 6 abas
detectadas, sem exceção. Servidor reiniciado e testado ao vivo via
Claude-in-Chrome: tema visual aplicado, aba Configurações com os
expanders corretos, upload de CSV funcionando fim a fim (ver acima).

**Documentação atualizada**: `GUIA_CODIGO.md` (§ `app.py`, ordem de
execução), `IMPLEMENTACAO.md` ("As seis abas da interface"), `README.md`
(árvore de arquivos), `MANUTENCAO.md` (contagem de abas no AppTest,
dependências novas).

## README.md na raiz do repositório (16/08/2026)

Pedido do autor: "colocar um resumo do aplicativo no GitHub explicando
como funciona, pra que serve e qual a forma de preparar para rodar em
Linux e em Windows". Até esta sessão, a raiz do repositório **não tinha
nenhum `README.md`** — o GitHub não renderizava nada na página principal
do projeto, só a listagem de arquivos.

**Novo `README.md` na raiz**: resumo do livro (1 parágrafo) seguido de um
resumo focado no app — o que ele simula, os 5 algoritmos da Parte II
(EKF, VAE, PIML, MPC, PSO) com uma frase cada, a estrutura das 6 abas, e
instruções de preparo/execução/teste **duplicadas para Linux/macOS e
Windows (PowerShell)** lado a lado, incluindo as duas armadilhas comuns
do Windows: comando `python` não reconhecido (usar o launcher `py`) e
política de execução do PowerShell bloqueando a ativação do venv
(`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`).

**`aplicativo/README.md` também atualizado**: as seções "Instalação",
"Execução" e "Testes" ganharam o comando equivalente para Windows ao lado
do de Linux/macOS (`venv\Scripts\...` vs. `venv/bin/...`), para quem
entra direto nessa pasta sem passar pelo README da raiz.

Nenhum comando foi testado de fato em Windows nesta sessão (ambiente de
desenvolvimento é Linux) — a sintaxe segue a convenção padrão do `venv`
do Python para PowerShell, não uma verificação empírica neste projeto.
Se algum comando falhar num Windows real, é o primeiro lugar a
conferir.

## Exemplo de arquivo para upload na aba "Dados Medidos" (16/08/2026)

O autor testou a aba "Dados Medidos" (ver "Reorganização visual" acima) e
perguntou onde estava o arquivo de exemplo — não havia nenhum: o CSV usado
para verificar a funcionalidade durante a implementação foi criado só no
diretório temporário da sessão (`scratchpad`), nunca fez parte do
repositório.

Corrigido com duas peças:
- **`aplicativo/exemplos/instrumentacao_exemplo.csv`** — cópia completa da
  Tabela 18.1 do livro (25 linhas, os 9 pontos A-I, incluindo a coluna
  "Função"), em ASCII puro (sem subscritos/gregas Unicode, para abrir sem
  problema de encoding em qualquer planilha eletrônica, inclusive no
  Excel do Windows).
- **Botão "⬇️ Baixar exemplo"** (`st.download_button`) na própria aba,
  logo acima do `file_uploader` — lê o arquivo via
  `Path(__file__).parent / "exemplos" / ...` (caminho relativo ao próprio
  `app.py`, não ao diretório de trabalho, para funcionar independente de
  onde o Streamlit for iniciado). Evita o usuário ter que caçar o arquivo
  no sistema de arquivos.

**Verificação**: `pytest`/`AppTest` sem exceção; testado ao vivo via
Claude-in-Chrome — upload do próprio `instrumentacao_exemplo.csv` mostrou
corretamente "25 variáveis carregadas" e "9/9 pontos cobertos" (mensagem
de sucesso, não de aviso).

## Terceiro caminho de calibração (LM), PDP dinâmico e horizonte em dias (16/08/2026)

Pedido do autor em três partes, na sequência de uma pergunta sobre por
que o problema inverso usa EKF/PIML em vez de Levenberg-Marquardt (LM):
"pode extender para esta opção?"; "a temperatura de ponto de orvalho ao
longo do tempo na saída da secadora, consegue fazer isso?"; "aumentar
para até dias a questão do acompanhamento dos compressores, visto que o
processo vai demonstrando falhas em tempos mais dilatados". As três
implementadas nesta sessão, sem pedir esclarecimento adicional (escopo já
estava claro dos meus próprios comentários anteriores + do pedido em si).

**1. `compressor_sim/calib_lm.py`** (novo módulo): terceiro caminho de
identificação de K, ao lado do EKF aumentado (online) e do PIML (offline,
com rede) — `calibrar_k_lm()` via `scipy.optimize.least_squares
(method="lm")`, batch, direto contra `sistema.simular()`, pelos mesmos 2
canais do EKF aumentado (ṁ_seco, T_HP,in — mesma ordem de
`ekf.medicao_aumentada`, para os três caminhos serem comparáveis).
Verificado por `python -c` antes de integrar na UI: converge para
K≈0,0476-0,0509 (real 0,05) em 3-4 avaliações do modelo físico,
**independente do chute inicial** (testado com k0 ∈ {0,02; 0,05; 0,10} —
mesmo resultado nos três, ao contrário do PIML, sensível à inicialização
dos pesos). Nova subseção na aba "🧠 Gêmeo Digital" entre PIML-inverso e
MPC; novos hiperparâmetros (amostras, K inicial, ruído) na aba
Configurações.

**2. `pdp_saida_c` em `psa_ciclo.py`**: série temporal do ponto de
orvalho na saída do secador — o Cap. 15 não fecha essa relação (só o KPI
estático HI_des, Eq. 15.7), então é uma simplificação de modelagem nova,
documentada como tal: a cada instante, a torre relevante é a que está
adsorvendo com menor `q_norm` (mais perto do *breakthrough*), interpolada
linearmente entre `PDP_ALVO_C` (leito novo) e `pdp_entrada_c` (nenhuma
remoção — mesmo limite usado quando nenhuma torre está adsorvendo). Novo
gráfico na aba "Secagem PSA", entre a capacidade/temperatura por torre e
o chaveamento — mostra visualmente o serrilhado esperado (cada troca de
torre reinicia a degradação daquele leito), confirmado ao vivo via
Claude-in-Chrome.

**3. Horizonte do EKF em dias, não só "passos"**: novo widget "Δt entre
medições [horas]" (Configurações, aba EKF) — converte o eixo x dos 3
gráficos do EKF de 2 estados e dos 2 gráficos do EKF aumentado de
"passo" para "Tempo [dias]" (`t_dias = passos * dt_horas / 24`), sem
alterar o cálculo do filtro (Q/R continuam por-passo). Sliders de
horizonte estendidos de 150→2000 passos (EKF) e 60→2000 passos (EKF
aumentado, pós-calibração) — testado ao vivo com 2000 passos × 1h ≈ 83,3
dias, renderizou em segundos (perf verificada antes via `python -c`:
1000 passos ≈ 0,76 s). Motivação explícita do autor: mecanismos de falha
reais (a mesma folga/incrustação do Cap. 29) se desenvolvem em semanas,
não minutos — o eixo em dias torna essa escala visível sem forçar o
usuário a fazer a conversão de cabeça.

**Testes novos**: `test_lm_calibra_k_proximo_do_real_com_ruido_baixo`,
`test_lm_converge_igual_independente_do_chute_inicial`,
`test_psa_pdp_saida_degrada_com_carga_do_leito_e_satura_no_pdp_entrada`,
`test_psa_pdp_saida_no_pdp_entrada_quando_nenhuma_torre_adsorve` — 75/75
testes passam (71 antigos + 4 novos, nenhum removido). Os 5 testes
existentes de `simular_ciclo_psa()` precisaram do novo argumento
obrigatório `pdp_entrada_c` (breaking change de assinatura, não escondido
atrás de um default). Um teste de monotonicidade do PDP inicialmente
falhou por escolher um horizonte que cruzava exatamente uma troca de
torre — corrigido restringindo a janela de verificação à mesma fase de
adsorção já usada pelo teste de capacidade vizinho (`t < 6.0`), não um
bug de implementação.

**Documentação atualizada**: `GUIA_CODIGO.md` (§ `psa_ciclo.py`, nova §
`calib_lm.py`), `IMPLEMENTACAO.md` ("três caminhos de identificação de K",
horizonte em dias, PDP dinâmico).

## Material dessecante, massa real e dinâmica não linear do secador (16/08/2026)

Pedido do autor, ao ver o app ao vivo: "estou estranhando também a
responsividade dos gráficos, está tudo muito linear para um equipamento
real. Além disso não pode faltar a massa do adsorvedor e as opções de
materiais adesorventes, como alumina, sílica, etc." — na sequência de ter
perguntado antes "não achei a massa do adsorvedor" (resposta: de fato não
existia, porque a Eq. 15.1 do livro é inteiramente normalizada, sem massa
nenhuma — ver conversa).

Valores de propriedade dos materiais **pesquisados via `WebSearch` antes
de codificar** (não inventados de memória): ScienceDirect "Activated
Alumina" (densidade 600-800 kg/m³, capacidade 7-12% em baixa UR) e guias
de peneira molecular 13X (capacidade dinâmica >25% em alta UR, PDP até
-73°C). Usados valores representativos de **baixa UR** (regime real de um
secador de ar comprimido já pré-secado por aftercooler+separador), não a
capacidade estática máxima de folha de dados — sempre maior e enganosa
para este uso.

**`constantes.py`**: novo dict `MATERIAIS_DESSECANTE` — Alumina Ativada
(750 kg/m³, 10%, k_ads=1.5), Sílica Gel (700 kg/m³, 8%, k_ads=1.2),
Peneira Molecular 13X (720 kg/m³, 18%, k_ads=1.8), todos ASSUMIDO com a
fonte anotada. `MATERIAL_PSA_DEFAULT` e `MASSA_LEITO_PSA_DEFAULT_KG`
(200 kg/torre).

**`psa_ciclo.py`**: dois parâmetros novos e obrigatórios em
`simular_ciclo_psa()` — `capacidade_trabalho`, `massa_leito_kg`. Nova
saída `agua_adsorvida_kg` = (1 − q_norm) × capacidade × massa, por torre
e por passo de tempo. **Recuperação de capacidade na regeneração e
temperatura do leito trocadas de reta linear para aproximação
exponencial de 1ª ordem** (`TAXA_1A_ORDEM=4`, >98% de recuperação dentro
da própria janela de fase) — resposta física real de um processo
térmico/de transporte, não uma reta com quina abrupta no fim da fase.
Isso é, em si, a resposta à reclamação de "responsividade... muito
linear": as curvas de capacidade e água adsorvida agora têm a forma
côncava esperada de um equipamento real, visíveis lado a lado com o
material selecionável no gráfico "Água adsorvida por torre [kg]".

**`app.py`**: nova aba Configurações → Secagem PSA ganhou `st.selectbox`
de material (preenche automaticamente o default de `k_ads_psa`, ainda
ajustável) e `st.number_input` de massa do leito. Novo gráfico "Água
adsorvida por torre [kg] — {material}" na aba Secagem PSA, com linha de
capacidade máxima de referência. Testado ao vivo via Claude-in-Chrome:
trocar o material (Alumina → Peneira Molecular 13X) atualizou o título,
a capacidade máxima (20 kg → 36 kg) e a legenda do gráfico em tempo real.

**Testes novos**: `test_materiais_dessecante_tem_propriedades_fisicamente_plausiveis`,
`test_agua_adsorvida_kg_cresce_na_adsorcao_e_some_apos_regeneracao` — 77/77
passam (75 antigos + 2 novos). Um teste existente de temperatura
(`test_psa_temperatura_do_leito_sobe_na_regeneracao_e_desce_no_resfriamento`)
tinha uma asserção calibrada para a reta linear antiga (`== 105.0 ±1`);
corrigida para uma verificação relativa (`> 95% do salto`), compatível
com a nova curva assintótica em vez de recalibrar um número mágico.

## Sincronia com o livro: Eqs. 15.12/15.13, Tabela 15.2 (16/08/2026)

Pedido do autor, na sequência direta do trabalho acima: "ajuste as
equações do livro". Antes desta sessão, a cinética de regeneração
(dessorção) e as propriedades de material dessecante eram lacunas
**reconhecidas mas nunca fechadas** pelo Cap. 15 — a Eq. 15.1 já
mencionava "$q_{eq}$... isoterma do dessecante" e "$k_{ads}$... específica
da alumina ativada ou peneira molecular" sem nunca lhes dar um valor.
Achado útil ao reler o capítulo antes de editar: a **Eq. 15.3 já existia**
(balanço mássico de água via $W_{in}-W_{out}$, $M_{ads}(t)=\int
\dot m_{water}\,dt$) — não seria substituída, e sim complementada por uma
segunda via de estimativa (capacidade × massa, mais barata quando não há
sensor contínuo de $W_{out}$).

Adicionado ao `compressores.tex`, Cap. 15: nova subseção "Cinética de
Regeneração e Propriedades do Material Dessecante", entre "Cinética de
Adsorção e Balanço de Massa" e "Termodinâmica do Secador de Tambor
Rotativo" — Eq. 15.12 (recuperação exponencial de 1ª ordem, simétrica à
Eq. 15.1, novo símbolo $\kappa_{regen}$), Tabela 15.2 (as mesmas 3
materiais/valores de `constantes.py`, mesma fonte), Eq. 15.13
($M_{ads,cap} = [q_{eq}-q_d(t)]\cdot M_{leito}$, a via de estimativa por
capacidade) e um parágrafo novo de diagnóstico: divergência persistente
entre Eq. 15.3 e Eq. 15.13 indica que o material degradou abaixo do
catálogo. Nomenclatura: $\kappa_{regen}$\dag e $M_{leito}$ adicionados;
$k_{ads}$ corrigido de "Cap. 14" para "Cap. 15" (categorização já estava
errada antes desta sessão — só notada por estar mexendo exatamente ali).

**Erro cometido e corrigido antes de reportar como concluído**: a
primeira versão da Tabela 15.2 usava `tabular` puro (sem `\resizebox`),
diferente de toda outra tabela deste documento — gerou um *Overfull
\textbackslash hbox* de 85,9pt (a tabela literalmente não cabia na
largura da página). Descoberto pelo próprio hábito de sempre conferir o
log de compilação por *overfull* >20pt antes de reportar, não por
inspeção visual do PDF. Corrigido envolvendo em `\resizebox{\textwidth}{!}`,
mesmo padrão das ~20 outras tabelas do livro.

**Verificação**: 3 passagens de `pdflatex`, 165→166 páginas, sem
referências indefinidas, sem rótulo duplicado, sem overfull severo após a
correção.

## Bug real: massa do leito desconectada do PDP + 3 pedidos em sequência (16/08/2026)

O autor testou o app ao vivo e reportou, em mensagens sucessivas na mesma
sessão: "a temperatura de ponto de orvalho não está sustentando... mesmo
aumentando absurdamente a quantidade de alumina, não está fazendo sentido
técnico"; depois "os gráficos das torres também estão errados"; depois
perguntou se havia "erro na integração ao longo do tempo" (resposta: não
há nenhum solver numérico neste módulo, tudo é fórmula fechada — `exp()`
avaliada em cada ponto, vetorizado, sem passo-a-passo tipo Euler/RK4); e
por fim três pedidos novos: horizonte de simulação em dias, tempos reais
de regeneração/resfriamento da Alumina (experiência de campo do autor) e
aproveitamento do calor dos estágios na regeneração. Dois pedidos
adicionais (soprador booster para aumentar h de convecção; verificar a
dinâmica de adsorção "equacionada" de fato) foram **conscientemente
adiados** — o autor escolheu, via pergunta direta, terminar o que já
estava em andamento antes de abrir essas duas frentes novas.

**Causa raiz do bug**: `massa_leito_kg` (adicionado na sessão anterior)
só alimentava `agua_adsorvida_kg` (um display derivado) — nunca entrava
na cinética de esgotamento do leito (`q_norm`, Eq. 15.1), porque `t_res`
continuava sendo um slider independente. Resultado: qualquer massa de
alumina produzia exatamente a mesma curva de PDP.

**Duas tentativas até a fórmula certa** (ambas verificadas por `python -c`
antes de integrar na UI, não só "parecia razoável"):
1. Tempo de contato gás-sólido (volume de vazios do leito / vazão
   volumétrica de ar, com porosidade 0,40 pesquisada via `WebSearch` —
   fonte: faixa 0,36-0,46 para pellets/esferas empacotados). **Não
   funcionou**: dava t_res em segundos (0,001-3,5 min mesmo a 2000 kg),
   ordens de grandeza menor que a escala de minutos já calibrada de
   `k_ads` — o leito esgotava quase instantaneamente independente da
   massa, só um pouco menos errado que antes.
2. Balanço de massa de água: `t_res = (massa_leito_kg * capacidade_trabalho)
   / (m_dot_ar * W_in * 60)`, com `W_in` calculado via
   `nucleo.razao_umidade(pdp_entrada_c+273,15, p_high, 1.0)` (nova
   dependência: `psa_ciclo.py` passou a importar `nucleo`). **Funcionou**:
   verificado que massa de 1→2000 kg move t_res de 1,4→2729 min e PDP
   máximo de +25,5°C→-39,8°C de forma suave e monotônica. `POROSIDADE_LEITO_PSA`
   (da tentativa 1) removida por ficar sem uso — não escondida, deletada.

**Consequência**: o "tempo de residência" deixou de significar o que o
nome sugere fisicamente (contato gás-sólido) — passou a ser "tempo até
saturação total à carga atual", uma grandeza de balanço de massa. Livro
(Eq. 15.14) documenta essa reinterpretação explicitamente, não esconde a
mudança de significado atrás do mesmo símbolo $t_{res}$.

**Recalibração de defaults**: com a fórmula corrigida, os defaults
antigos (200 kg, t_ads=6 min) ficavam com t_res≈273 min — bed
"comicamente" sobredimensionado para um ciclo de 6 min. Novos defaults:
`t_ads_psa`=60 min, `t_regen_psa`/`t_resfriamento_psa` agora vêm de
`MATERIAIS_DESSECANTE[material]["t_regen_ref_min"/"t_resfriamento_ref_min"]`
(45/10 min para Alumina — **única fonte real, experiência de campo do
autor**; Sílica Gel e Peneira Molecular reaproveitam os mesmos números
por analogia, sem fonte própria — marcado assim no código e no livro).
Sliders estendidos: `horizonte_psa` 120→7200 min (5 dias — testado 3 dias/
86401 pontos em 0,035s, sem problema de performance), `t_ads_psa` até 240
min, `t_regen_psa` até 90 min, `t_resfriamento_psa` até 20 min.

**Aproveitamento de calor da regeneração (Eqs. 15.10/15.11)**: já existia
no livro desde antes desta sessão, nunca implementado no app. Agora sim:
`sistema.py` reordenado — `p_aquecedor_nominal` (Eq. 3.3) calculado no
passo do secador, mas o valor final `p_aquecedor` só fecha depois de
`q_gerado_hood` (passo 8b), como `max(0, p_aquecedor_nominal -
eps_recup_psa*(q_aftercooler+q_gerado_hood))`. Novo slider `eps_recup_psa`
(Configurações, default 0,5). `w_total`/`eta_global`/`spc_valor`/`sec_dry`
precisaram ser deslocados para depois dessa correção (reordenação real do
arquivo, não só um valor trocado) — Q_óleo fica de fora por não haver
circuito de óleo modelado neste app, omissão explícita, não escondida.
Testado ao vivo: com os defaults, Q_disp (22,66 kW) é ~10× maior que o
aquecedor nominal (2,26 kW) — resultado plausível, não bug (o purge é uma
fração pequena da vazão total, e o aftercooler sozinho rejeita a maior
parte do calor de compressão) — verificado por conta manual batendo com
os números exibidos antes de aceitar como correto.

**Honestidade sobre `k_ads_ref`**: o autor perguntou diretamente se a
"dinâmica de adsorção dos materiais" tinha sido equacionada de verdade.
Resposta: não — os valores de `k_ads_ref` (1,5/1,2/1,8) nunca foram
verificados contra literatura ou ensaio, só uma ordenação relativa
assumida (peneira molecular mais rápida, sílica mais lenta). Marcado
explicitamente como tal no código, na UI (help text do slider) e no
livro (Tabela 15.2) — não apresentado como precisão que não existe.
Registrado como pendência real, não resolvido nesta sessão.

**Testes novos**: `test_psa_mais_massa_de_dessecante_melhora_pdp_e_t_res`
(regressão direta do bug — t_res escala linear com massa, PDP melhora
monotonicamente), `test_recuperacao_de_calor_reduz_potencia_do_aquecedor`
— 79/79 passam (77 antigos + 2 novos). Assinatura de
`simular_ciclo_psa()` mudou de novo (`t_res_min` removido, `densidade_kg_m3`
adicionado e depois removido na mesma sessão, ao trocar de fórmula) — 8
call sites de teste atualizados via substituição em lote.

**Pendências explicitamente adiadas, a pedido do próprio autor**:
1. Soprador booster antes da resistência de aquecimento, para aumentar o
   coeficiente de convecção — exigiria um modelo de transferência de
   calor no aquecedor (h, área) que não existe hoje; `delta_t_regen`
   continua um valor assumido, não calculado.
2. Diferença de troca (pellets vs. esferas) e vazão diferenciada do
   soprador — parte da mesma frente acima, não iniciado.

**Documentação atualizada**: `GUIA_CODIGO.md` (§ `psa_ciclo.py` e §
`sistema.py`, ordem real de dependência 8a/8b documentada).

## Soprador booster, forma da partícula e temperatura do rotor no app (16/08/2026)

Pedido do autor: "commite no .tex e no aplicativo" seguido de escolha via
pergunta — as três frentes que só existiam no livro até então (ver
"Soprador booster e forma de partícula fechados no livro" em
`CONTEXTO.md`) portadas para o app. Diferente do padrão usual desta
sessão, cada uma foi **verificada ao vivo no navegador antes de aceitar
como correta** — e essa verificação achou 3 bugs reais, todos corrigidos
antes do commit final:

**Novos parâmetros (`constantes.py`)**: `COND_ROTOR_W_K`, `Q_COND_EIXO_W`,
`DELTA_NOM_UM`, `ALPHA_ROTOR`, `ALPHA_CARCACA`, `L_ROTOR_M`, `L_CARCACA_M`
(rotor); `PSI_P_ESFERA`, `PSI_P_PELLET`, `D_P_PARTICULA_M`,
`POROSIDADE_LEITO_PSA`, `L_LEITO_PSA_M`, `D_VASO_PSA_M` (leito PSA);
`D_H_AQUECEDOR_M`, `A_AQUECEDOR_M2`, `T_ELEM_MAX_C`,
`M_DOT_REG_DEFAULT_KG_S`, `ETA_SOPRADOR_BOOSTER`, `MU_AR_REGEN`,
`K_AR_REGEN`, `PR_AR` (soprador/aquecedor).

**Novas funções**: `nucleo.temperatura_rotor_regime` e
`nucleo.folga_residual_termica` (Eqs. 9.19/9.7); `subsistemas.
coef_conveccao_forcada` (Dittus-Boelter, Eq. 15.15), `subsistemas.
perda_carga_ergun` (Eq. 15.17), `subsistemas.k_ads_por_forma` (Eq. 15.18).
O fechamento do aquecedor (Eq. 15.16, $\epsilon$-NTU) **reaproveita**
`subsistemas.saida_trocador`, já existente para o intercooler — nenhuma
função nova para isso.

**Integração em `sistema.py`**: T_rotor/δ_real calculados após T_carcaça
(novos KPIs `t_rotor_c`, `delta_t_rotor_c`, `folga_residual_um`); o
antigo `DP_NOM_PSA` fixo usado em HI_des (Eq. 15.7) foi substituído por
um valor calculado via Ergun a partir da vazão/geometria/forma de
partícula atuais (novo KPI `dp_nom_psa_calc_bar`) — `dp_real_psa`
(medido) continua com o default antigo, então HI_des deixa de ser
exatamente 1,0 por construção no caso saudável (ver ressalva abaixo).

**Integração em `psa_ciclo.py`**: **nenhuma mudança de assinatura** —
decisão deliberada para não arriscar quebrar os 8 call sites de teste já
existentes. O soprador e a forma de partícula entram por fora: `app.py`
calcula $h$, $T_{reg,in}$ (logo, $\Delta T_{regen}$ efetivo) e
$k_{ads}$ corrigido por $\psi_p$ **antes** de chamar
`simular_ciclo_psa()`, passando os resultados nos parâmetros já
existentes (`delta_t_regen`, `k_ads`).

**Novos widgets (`app.py`, aba Configurações → Secagem PSA)**: rádio
"Forma da partícula" (Esfera/Pellet) e slider "Vazão do soprador
booster". Novas métricas na aba "Operação estática" (T_rotor, ΔT_rotor,
δ_real) e uma legenda na aba "Secagem PSA" mostrando h, T_reg,in,
ΔT_regen calculado, k_ads efetivo, potência do booster e SEC_dry
com/sem booster.

**3 bugs reais encontrados na verificação ao vivo (não seriam pegos só
pelos 79 testes automatizados, que continuaram passando o tempo todo)**:

1. **Falso alarme de HI_des**: os primeiros valores ASSUMIDOS de
   geometria do leito ($D_{vaso}=0{,}5$ m, $L=1$ m, $d_p=3$ mm,
   $\varepsilon=0{,}40$) davam ΔP via Ergun de só ~6 mbar — 50× menor
   que o antigo `DP_NOM_PSA` (300 mbar) — disparando HI_des≈0,02 e o
   banner de "dessecante degradado" logo na carga inicial do app, sem
   qualquer degradação real configurada. Recalibrados em conjunto
   ($D_{vaso}=0{,}30$ m, $L=2{,}3$ m, $d_p=1{,}5$ mm,
   $\varepsilon=0{,}38$ — geometria ainda realista) para reproduzir a
   mesma ordem de grandeza do valor antigo (~200 mbar) no ponto de
   operação default.
2. **Falso alarme de contato metálico (δ_real negativo)**: com
   $\delta_{nom}=100$ µm, a dilatação térmica diferencial rotor/carcaça
   no ponto de operação default (~140 µm) já excedia a folga nominal,
   dando $\delta_{real}=-40$ µm — risco de rubbing sinalizado numa
   máquina "saudável" por padrão. Corrigido para
   $\delta_{nom}=250$ µm, dando $\delta_{real}\approx+110$ µm.
3. **Aquecedor de regeneração não aquecia**: `saida_trocador(t_quente_in,
   t_fria_in, ua, c_min)` foi chamada com os argumentos trocados
   ($T_{elem,max}$ no lugar de "quente", o ar no lugar de "frio") — a
   função interpola do primeiro argumento em direção ao segundo
   conforme $\epsilon$ cresce, então a chamada errada fazia $T_{reg,in}$
   convergir para a temperatura do ar de entrada (25°C), não para a do
   elemento (250°C). Resultado antes da correção: $T_{reg,in}=34{,}8$°C
   (praticamente sem aquecimento); depois: $T_{reg,in}=240{,}2$°C —
   batendo com o cálculo manual de conferência ($\epsilon\text{-NTU}$
   com $NTU\approx3{,}14$, $\epsilon\approx0{,}96$).

Todos os três só apareceram ao rodar o app de verdade no navegador e
olhar os números — reforça a prática já registrada no `CLAUDE.md`
("For UI or frontend changes, start the dev server and use the feature
in a browser before reporting the task as complete"), que quase foi
pulada aqui por vir de uma sessão que trabalhou o dia inteiro só no
`.tex`.

79/79 testes passando (nenhum teste novo — os 3 bugs eram de
integração/calibração, não de lógica unitária isolada, e os testes
existentes não exercitam esses caminhos novos). Servidor Streamlit
reiniciado e verificado limpo (sem exceções, sem warnings de aplicação)
antes do commit.

## Pendências conhecidas

1. **[Item desatualizado — corrigido em 16/08/2026]** O app cobre os
   Capítulos 5, 9, 10, 11, 12, 13, 14, 15, 16 do livro (trem termodinâmico
   + psicrometria + rede) e um recorte do Cap. 4 (motor elétrico —
   $\eta_{mot}$ simplificado via Eqs. 4.10-4.12; VSD, Eq. 4.3, continua
   sem representação própria). A Parte II (EKF, VAE, PIML, MPC, PSO) **já
   está implementada** desde 15/08/2026 (ver "Parte II no app" acima) —
   este item dizia o contrário até esta correção, claramente obsoleto
   (ficou sem atualização por várias sessões). Rotordinâmica/mancais
   (Caps. 8, 9, 11)
   agora tem cobertura **parcial**: Eq. 9.3 (eficiência volumétrica por
   folga) desde antes, Eq. 9.6 (balanço térmico da carcaça, regime
   permanente) desde 15/08/2026, e Eq. 9.7/9.18/9.19 (temperatura do
   rotor e folga residual térmica, regime permanente) desde 16/08/2026 —
   ver seção "Soprador booster, forma da partícula e temperatura do
   rotor no app" abaixo. Seguem sem representação: velocidade crítica/
   torcional (Cap. 8), vibração espectral (Eq. 9.8), vida de rolamento
   (Cap. 11).
2. `n_compressores` assume unidades **idênticas** operando no **mesmo**
   ponto de operação (mesma fração de carga cada uma) — não modela um
   cenário de carga desigual entre máquinas nem lógica de seleção de qual
   unidade liga/desliga (ex.: rodízio para igualar horas de operação,
   comum em plantas reais com N+1). Se um cenário desses for pedido,
   `dinamica.py` precisa de um estado por unidade, não um `x_c` agregado.
3. ~~GPU disponível na máquina do autor (RTX 4070) não é usada~~ —
   **resolvido em 16/08/2026**, ver "Uso de GPU (CUDA) quando disponível"
   abaixo.
4. **Quatro extensões metodológicas implementadas só no livro em
   16/08/2026** (pendências 5-8 do `CONTEXTO.md` principal, seção
   "Pendências conhecidas") — nenhuma tem implementação de referência
   neste simulador ainda:
   - **Sensores portáteis/wireless** (Cap. 18, Eq. 18.6,
     $\mathcal{R}_{\text{port}} = \kappa_{\text{port}}\cdot\mathcal{R}_{\text{fixo}}$)
     — o app não simula leitura assíncrona/de menor confiança; todo canal
     do EKF (`ekf.py`) usa a mesma $\mathcal{R}$ fixa por chamada.
   - **$\zeta_{\text{valv}}$, coeficiente de perda de válvulas** (Cap. 5,
     Eq. 5.16) — estende $\Lambda$ da Eq. 28.1 para 4 elementos (ver
     `MANUTENCAO.md`, seção "Escopo"); exigiria um canal de $\Delta P$ de
     válvula que nem `sistema.py` nem a Tabela 18.1 têm hoje.
   - **Treino multi-mecanismo** (Cap. 29, Eq. 29.2, busca por resíduo
     mínimo generalizada sobre o catálogo de 59 mecanismos) — o app só
     reproduz o cenário único de desgaste de folga; falta o gerador
     sistemático de dataset sintético multi-mecanismo e a busca
     $\arg\min$ correspondente.
   - **Painel supervisório de frota** (Cap. 26, nova subseção, laço
     `ciclo_supervisorio` em pseudocódigo) — o app roda um cenário e uma
     máquina por execução do Streamlit, sem estado persistente entre
     sessões nem agendamento contínuo; reproduzir o painel exigiria as
     duas peças, nenhuma presente hoje.

   Se qualquer uma dessas for pedida para o app no futuro, o ponto de
   partida é a seção correspondente do `compressores.tex` (números acima)
   — a arquitetura já está descrita lá, falta só o código.
5. **[Resolvido no app em 16/08/2026]** Soprador booster na regeneração —
   ver seção "Soprador booster, forma da partícula e temperatura do
   rotor no app" abaixo.
6. **[Resolvido no app em 16/08/2026]** Diferença de forma do dessecante
   (pellets vs. esferas) — ver mesma seção abaixo. Vazão diferenciada do
   soprador **por forma de partícula** (ex.: soprador dimensionado
   automaticamente para não estourar um ΔP máximo) continua não
   implementada — a vazão do booster é um slider independente, não
   otimizada em função de ψ_p.
7. **`k_ads_ref` não verificado** (autor perguntou diretamente, 16/08/2026,
   ver "Bug real: massa do leito desconectada do PDP" acima) — os 3
   valores de referência (1,5/1,2/1,8) são uma ordenação relativa
   assumida, não uma medição nem valor de literatura confirmado.
