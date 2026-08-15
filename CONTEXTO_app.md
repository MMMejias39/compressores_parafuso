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

## Estado atual

Código compila sem erro de sintaxe, 41/41 testes passam
(`venv/bin/pytest tests/ -q`). Servidor Streamlit **não está rodando** no
momento — testado e encerrado ao fim da sessão de 15/08/2026 (ver "Balanço
térmico da carcaça" acima); a última vez que ficou de pé continuamente foi
após a correção de umidade (02/08/2026), sessão anterior.

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

## Pendências conhecidas

1. O app usa apenas os Capítulos 5, 9, 10, 11, 12, 13, 14, 15, 16 do livro
   (trem termodinâmico + psicrometria + rede). Motor elétrico (Cap. 4) e a
   Parte II inteira (EKF, VAE, PIML, MPC, PSO — Caps. 19-27) não têm
   nenhuma representação no simulador — candidato natural de expansão
   futura, mas não pedido ainda. Rotordinâmica/mancais (Caps. 8, 9, 11)
   agora tem cobertura **parcial**: Eq. 9.3 (eficiência volumétrica por
   folga) desde antes, e Eq. 9.6 (balanço térmico da carcaça, regime
   permanente) desde 15/08/2026 — ver seção acima. Seguem sem
   representação: velocidade crítica/torcional (Cap. 8), vibração
   espectral (Eq. 9.8), vida de rolamento (Cap. 11) e Eq. 9.7 (folga
   residual por dilatação térmica, que dependeria de um modelo de
   temperatura do rotor não fechado pelo livro).
2. `n_compressores` assume unidades **idênticas** operando no **mesmo**
   ponto de operação (mesma fração de carga cada uma) — não modela um
   cenário de carga desigual entre máquinas nem lógica de seleção de qual
   unidade liga/desliga (ex.: rodízio para igualar horas de operação,
   comum em plantas reais com N+1). Se um cenário desses for pedido,
   `dinamica.py` precisa de um estado por unidade, não um `x_c` agregado.
