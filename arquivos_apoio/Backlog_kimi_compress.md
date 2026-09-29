# Backlog de ajustes — `compressores.tex`

**Origem:** avaliação de ausências de acessórios e equacionamento de compressores
de ar industriais de alta potência (parafuso rotativo, oil-free, dois estágios,
aplicação offshore), sessão Kimi de 02/08/2026.
**Base analisada:** `compressores.tex` (135 páginas, 27 capítulos, ~200 equações
numeradas), `CONTEXTO.md`, `CONTEXTO_app.md` e os três pareceres externos
anteriores (Copilot, Manus, dicas_kimi).

**Status:** ✅ **IMPLEMENTADO — 13/13 itens em 02/08/2026.** O autor pediu o
backlog completo de uma vez; todos os itens foram implementados na mesma sessão
(registro completo em `../CONTEXTO.md`, seção "Backlog Kimi implementado — 13
itens (02/08/2026)"). Este arquivo fica preservado como histórico do
planejamento — as descrições abaixo referem-se ao estado do livro **antes** da
implementação. Pontos de verificação rápida do que foi feito:

- **BK-01** → `compressores.tex`, eq. 11.12 (`eq:s11-12`), condições ISO 1217
  verificadas contra fonte real; Nomenclatura e Cap. 16 (`\eqref`) atualizados.
- **BK-02** → nova subseção 5.9, eq. 5.14 ($P_{\text{int}}^* = \sqrt{P_1 P_2}$).
- **BK-03** → item EDM na subseção 4.4 + fechamento eletrostático com eq. 4.13;
  referência `erdman` (IEEE Trans. IA 32(2), 1996, DOI 10.1109/28.491472)
  verificada antes de citar.
- **BK-04** → linha "Posição Axial" ($\delta_{ax}$, μm) na Tabela 18.1 + frase
  no Cap. 11 ligando eqs. 11.5 → sensor → 11.6.
- **BK-05** → **decidido com o autor: a máquina real não tem MPV** — item
  removido da lista de acessórios (mantidas retenção e blow-down).
- **BK-06** → subseção 8.8, eq. 8.10 ($\omega_{cr,t}$ torcional, `api684`).
- **BK-07** → subseção 9.7, eq. 9.11 ($\eta_p \leftrightarrow \eta_{is}$).
- **BK-08** → subseção no Cap. 7 (TAN/ASTM D664, Karl Fischer/ASTM D6304,
  ISO 4406:2021 — as três verificadas antes de citar).
- **BK-09** → três inserções: hood como barreira acústica (ISO 2151:2004,
  verificada), silenciador de admissão somando perda à eq. 5.4, amortecedor de
  pulsação no Cap. 16.2 (`api618`).
- **BK-10** → subseção 9.8, eqs. 9.12/9.13 ($u_{\text{tip}}$, $M_{\text{tip}}$).
- **BK-11** → soft-sensor de $\dot{m}_w$, eq. 12.8 no Cap. 12.
- **BK-12** → aquecedores anticondensação no item 4.4, ligados à eq. 4.7.
- **BK-13** → nota de escopo junto ao item PSV no Cap. 3.6 (`asme8`).

Estratégia que evitou renumeração em cascata: toda equação nova foi inserida ao
fim do capítulo/subseção final — nenhuma equação preexistente mudou de número.
5 `\bibitem` novos, todos verificados contra fonte real: `erdman`, `iso4406`,
`astmd664`, `astmd6304`, `iso2151`.

--- 

*Texto original da proposta (estado pré-implementação) preservado abaixo.*
Cada item indica a lacuna, o local exato no `.tex`, o ajuste proposto e os
cuidados de convenção. Itens em ordem de prioridade sugerida (alta → baixa).

| ID | Item | Tipo | Prioridade | Capítulo(s) |
|----|------|------|-----------|-------------|
| BK-01 | Definir FAD e conversão ISO 1217 | Equacionamento | Alta | 11, 16 (3) |
| BK-02 | Pressão intermediária ótima LP/HP | Equacionamento | Alta | 5 (10) |
| BK-03 | Correntes de eixo (EDM) no motor VSD | Acessório + Falha | Alta | 4 |
| BK-04 | Posição axial na matriz de instrumentação | Acessório | Alta | 18 (11) |
| BK-05 | Revisar justificativa da MPV (resquício oil-flooded?) | Consistência | Alta | 5 |
| BK-06 | Análise torcional do trem (não só lateral) | Equacionamento | Média | 6 (8) |
| BK-07 | Relação eficiência politrópica × isentrópica | Equacionamento | Média | 9 (5) |
| BK-08 | Análise físico-química do óleo (TAN, água, ISO 4406) | Acessório | Média | 7 |
| BK-09 | Ruído aéreo, silenciadores e amortecedor de pulsação | Acessório | Média | 2, 5, 16 |
| BK-10 | Velocidade periférica do rotor e Mach de ponta | Equacionamento | Baixa | 9 (8) |
| BK-11 | Balanço explícito do lado da água (soft-sensor de vazão) | Equacionamento | Baixa | 10 (12) |
| BK-12 | Aquecedores anticondensação do motor | Acessório | Baixa | 3 (4) |
| BK-13 | Nota de escopo: dimensionamento da PSV (ASME VIII) | Escopo | Baixa | 3 (16) |

## Convenções obrigatórias ao implementar (resumo do CONTEXTO.md)

- Equação nova sempre em `\begin{equation}\label{eq:sC-N}` (numerada por
  capítulo), com parágrafo didático **antes** dela — nunca equação "crua".
  Inserir no meio de um capítulo exige renumeração em cascata dos labels
  seguintes e de todas as referências `\eqref` cruzadas (ver regra permanente
  em "Referenciamento de equações" do CONTEXTO.md).
- Verificar colisão de símbolos na Nomenclatura antes de introduzir qualquer
  letra nova (alfabeto grego ~90% saturado); símbolo novo entra na tabela de
  Nomenclatura correspondente.
- `\bibitem` novo **somente após verificação contra fonte real** (número de
  norma, DOI, editora) — regra permanente de veracidade. Os itens abaixo
  indicam referências candidatas já existentes na bibliografia ou a verificar.
- Aspas sempre `` `` `` e `''`, nunca `"` reto fora de `verbatim`. Termo
  inglês novo recorrente entra no `\hyphenation{}`.
- Tabelas novas em booktabs (`\toprule`/`\midrule`/`\bottomrule`); figura ou
  tabela nova com `\caption[curta]{longa}` e parágrafo que a referencia antes.
- Capítulo tocado mantém o bloco "Diretriz Técnica Final" coerente com o novo
  conteúdo. Compilar 3 passagens e inspecionar o log com `grep -a` (o
  `compressores.log` é Latin-1; `grep` sem `-a` falha silenciosamente).
- **Não commitar sem pedido explícito do autor.**

## Prioridade alta

### BK-01 — Definir FAD (*Free Air Delivery*) e conversão ISO 1217

**Lacuna:** o símbolo $\dot{V}_{\text{free\_air}}$ aparece em dois KPIs
centrais — $SPC$ (eq. 11.11, `compressores.tex:1571`) e $SPC_{\text{fleet}}$
(eq. 16.6, `compressores.tex:2084`) — mas não existe em nenhum lugar do livro
a equação que converte a vazão mássica medida para as condições de referência
de sucção. Sem ela, o SPC não é comparável entre dias quentes/frios, entre
plataformas, nem contra a folha de dados do fabricante (que reporta FAD nas
condições de referência da ISO 1217 — norma já citada, mas só para $\eta_{is}$).

**Ajuste proposto:** adicionar no Capítulo 11, logo após a eq. 11.11 (nova
`eq:s11-12`, posição final do capítulo — **não exige renumeração**), a
definição:

$$\dot{V}_{\text{FAD}} = \frac{\dot{m}}{\rho_{\text{ref}}}, \qquad
\rho_{\text{ref}} = \frac{P_{\text{ref}}}{R \cdot T_{\text{ref}}}$$

com $P_{\text{ref}}$, $T_{\text{ref}}$ e UR de referência **conforme o texto da
ISO 1217:2009/Amd 1:2016** (condições-padrão de admissão: verificar os valores
exatos contra a norma antes de inserir — regra de veracidade; não confiar em
memória). Texto deve explicar que é essa conversão que torna o SPC comparável
entre condições ambientais distintas. Atualizar a Nomenclatura (verificar se
$\dot{V}_{\text{free\_air}}$ já consta; unificar a grafia FAD/*free air*).
A mesma definição passa a valer para o Cap. 16 via `\eqref`.

### BK-02 — Pressão intermediária ótima entre os estágios LP/HP

**Lacuna:** o livro modela os dois estágios separadamente (eqs. 5.5, 9.9, 11.2)
e quantifica a penalidade térmica de um intercooler degradado (eq. 10.4), mas
nunca apresenta a condição de alocação da razão de compressão entre estágios —
a equação clássica de compressão multistágio: com inter-resfriamento perfeito,
o trabalho total é mínimo quando as razões de compressão são iguais,
$P_{\text{int}}^{*} = \sqrt{P_1 \cdot P_2}$, e o ótimo se desloca quando o
resfriamento intermediário é imperfeito ($T_{HP,\text{in}} > T_{LP,\text{in}}$).

**Ajuste proposto:** derivar a partir da soma das eqs. 5.5 dos dois estágios,
em subseção nova no Cap. 5 (após a eq. 5.9, dentro de 5.5, ou como fechamento
de 5.4) — **atenção: inserir antes da eq. 5.10 força renumeração de
`eq:s5-10` a `eq:s5-13` e suas referências cruzadas**; alternativa sem cascata
é colocá-la como subseção nova ao fim do Cap. 5, antes do "Equacionamento
Integrado". Conectar ao Cap. 10: um intercooler degradado não só penaliza o
estágio HP (eq. 10.4) como desloca a alocação ótima — o Gêmeo Digital ganha um
critério de "desvio do ponto de projeto de fábrica". Referências já na
bibliografia: `cengel`, `moran`, `hanlon` — **nenhuma referência nova
necessária**. Símbolo: usar a pressão interestágio já instrumentada na matriz
do Cap. 18 ($P_{d,lp}$ = $P_{s,hp}$), evitando criar letra nova.

### BK-03 — Correntes de eixo (EDM) nos rolamentos do motor alimentado por VSD

**Lacuna (a mais importante do lado dos acessórios):** o Cap. 4
(`compressores.tex:694-717`) cobre barras quebradas, isolamento (Arrhenius),
excentricidade e desbalanço de fases, mas omite o modo de falha mais
característico de motor de alta potência alimentado por inversor: a tensão de
modo comum do chaveamento PWM induz tensão no eixo, que descarrega através dos
rolamentos (corrente EDM), produzindo *fluting*/craterização das pistas — falha
prematura clássica em motores de centenas de kW com VSD. Não há menção aos
acessórios de mitigação (rolamento isolado no lado oposto ao acoplamento, anel
de aterramento de eixo, filtro de modo comum) nem ao indicador digital.

**Ajuste proposto:** novo item na subseção 4.4 ("Mecanismos de Falha e
Correlações para o Gêmeo Digital"), descrevendo o mecanismo (tensão de modo
comum → acoplamento capacitivo estator-rotor → descarga pelo filme de óleo do
rolamento), o indicador (padrão de craterização visível em inspeção; pico de
corrente de eixo medida; progressão ligada ao histórico de operação do VSD) e
os acessórios de mitigação. Referência candidata a **verificar** antes de
inserir: Erdman, Kerkman, Schlegel, Skibinski, "Effect of PWM Inverters on AC
Motor Bearing Currents and Shaft Voltages", *IEEE Transactions on Industry
Applications*, vol. 32, nº 2, 1996 (confirmar volume/páginas/DOI). Relacionar
com a eq. 4.7 (Arrhenius): EDM e envelhecimento térmico do isolamento são as
duas vias dominantes de mortalidade de motor com inversor.

### BK-04 — Posição axial do rotor HP na matriz de instrumentação

**Lacuna:** o livro equaciona a força axial do estágio HP (eq. 11.5,
$F_a = \Delta P \cdot A_{\text{rotor}}$) e a vida do rolamento de escora
(eq. 11.6), mas a matriz de variáveis do Cap. 18 (`compressores.tex:2219-2253`)
só tem vibração global $v_{\text{rms}}$ no ponto B — não há sonda de proximidade
de **posição axial**, que é instrumentação padrão API 670 em máquinas dessa
classe de potência e o sensor que fecha o loop entre o modelo de $F_a$ e a
realidade (desgaste do rolamento de escora se manifesta primeiro como deriva
de posição axial, muito antes de vibrar).

**Ajuste proposto:** adicionar linha ao ponto B (ou E) da Tabela 18.1 —
variável "Posição Axial", unidade $\mu\text{m}$, função "Desgaste do rolamento
de escora HP / deriva de $F_a$" — e uma frase no Cap. 11 ligando eq. 11.5 →
sensor → eq. 11.6. Cuidado de símbolo: **não usar $z$ nem $x$** (vetores de
medição e estado do EKF, eqs. 21.1/21.2); sugestão $p_{ax}$ ou $x_{ax}$
subscrito — conferir Nomenclatura. Referência API 670 a **verificar** (edição
atual) antes de citar; se não quiser referência nova, citar a própria API 619
já existente, que remete à prática de proximidade.

### BK-05 — Revisar a justificativa da MPV (possível resquício oil-flooded)

**Achado de consistência:** a subseção 5.7 (`compressores.tex:836`) lista a
"Válvula de Pressão Mínima (MPV)" que "mantém a pressão interna
($\approx 4\,\text{bar}$) para assegurar a lubrificação e vedação". Essa
justificativa é típica de compressor **oil-flooded**, onde a MPV mantém o tanque
separador pressurizado para circular o óleo injetado. Na arquitetura oil-free
deste livro, a lubrificação é pressurizada pela bomba dedicada (eq. 5.3) e os
selos de labirinto não dependem de contrapressão da rede. Provável resquício do
rascunho original com GPAI — mesma família do problema do Cap. 12 corrigido em
26/07/2026 (ver CONTEXTO.md, "inconsistência oil-free", com a regra permanente
de não reintroduzir linguagem de óleo injetado).

**Ajuste proposto:** verificar com o autor qual arranjo a máquina real dele
possui. Opções: (a) remover o item MPV da lista, mantendo retenção e
blow-down; (b) se a máquina real tem alguma válvula de contrapressão mínima,
reescrever a justificativa em termos corretos para oil-free (ex.: garantir
pressão mínima para o ar de varredura/buffer dos selos, se aplicável). Não
manter o texto atual — ele contradiz o balanço do circuito de óleo do Cap. 12.

## Prioridade média

### BK-06 — Análise torcional do trem completo (não só lateral)

**Lacuna:** há torção **estática** do eixo (eq. 6.5) e velocidade crítica
**lateral** com Diagrama de Campbell (eqs. 8.5–8.6, `compressores.tex:1148`),
mas não há modelo de frequências naturais **torcionais** do conjunto
motor–acoplamento–gearbox–rotores. Em máquinas de alta potência a análise
torcional é exigência da API 619 (para excitações como harmônicos de torque do
VSD e passagem de lóbulos), e a própria API RP 684 citada na bibliografia
(`compressores.tex:3264`) cobre *train torsionals* — a referência está lá, o
equacionamento não.

**Ajuste proposto:** subseção nova no Cap. 6 (após 6.4) ou no Cap. 8 (após
8.5, "Rotordinâmica e Velocidade Crítica"): modelo de duas/três inércias com
rigidezes de eixo e acoplamento,

$$\omega_{cr,t} = \sqrt{k_{t,\text{eq}} \left( \frac{1}{I_1} + \frac{1}{I_2} \right)}$$

mais critério de margem análogo à eq. 8.6, agora contra as excitações
torcionais ($1\times$, $2\times$ RPM, $f_{bp}$, GMF, harmônicos de torque do
VSD). Cuidados de símbolo: $k_t$ já existe (rigidez torcional do eixo, eq. 6.5)
e $J$ é o momento polar de **seção** na mesma equação — usar $I_i$ para
inércias de massa (convenção já usada em $I_{\text{acopl}}$, $I_{\text{sys}}$) e
$\omega_{cr,t}$ para a crítica torcional. **Inserir no meio do Cap. 6 força
renumeração de `eq:s6-6` a `eq:s6-8`** — preferir fim de subseção existente.
Referência: `api684` já na bibliografia — nenhuma nova necessária.

### BK-07 — Relação entre eficiência politrópica e isentrópica

**Lacuna:** o livro usa $\eta_{is}$ (KPI dos Caps. 9/11/17) e o índice
politrópico $n$ (eqs. 5.5, 9.5) lado a lado, sem a fórmula que os conecta.
Folhas de dados de compressores de alta potência frequentemente especificam
eficiência **politrópica**; sem a relação, o leitor não consegue confrontar o
modelo com literatura de fabricante.

**Ajuste proposto:** no Cap. 9, após a eq. 9.9, ou no Cap. 5 após a eq. 5.5
(**atenção à cascata** de renumeração; no Cap. 9 só existe `eq:s9-10` depois
da 9.9), apresentar:

$$\eta_p = \frac{\gamma - 1}{\gamma} \cdot \frac{n}{n - 1}, \qquad
\eta_{is} = \frac{\Pi^{(\gamma-1)/\gamma} - 1}{\Pi^{(\gamma-1)/(\gamma\,\eta_p)} - 1}$$

com o comentário de que $\eta_p$ é aproximadamente constante ao longo do mapa,
enquanto $\eta_{is}$ varia com a razão de pressão — por isso os dois KPIs não
são intercambiáveis. Referências: `moran`, `cengel`, `hanlon` — já existentes.

### BK-08 — Análise físico-química do óleo (TAN, água, ISO 4406)

**Lacuna:** o $SOH_{\text{oil}}$ (eq. 7.7) combina viscosidade, $\Delta P$ e
efetividade — todos **online**. Falta a tríade laboratorial de rotina em alta
potência: TAN (número de acidez), água no óleo e contagem de partículas
(ISO 4406). É o canal que detecta degradação do lubrificante **antes** de ela
aparecer na viscosidade ou no $\Delta P$ — complementar, não redundante, ao
soft-sensor existente.

**Ajuste proposto:** subseção curta no Cap. 7 (após 7.3, matriz de falhas do
sistema de óleo), apresentando os três ensaios como canal *offline* periódico
que alimenta o Gêmeo Digital (tendência de TAN e contagem de partículas como
entradas de degradação do óleo e de desgaste de componentes, respectivamente).
Referência a **verificar**: ISO 4406 (edição vigente) para o código de
contagem de partículas; ASTM D664/D974 para TAN — confirmar número e edição
contra fonte real antes de criar os `\bibitem`. `mobley` (já citado) cobre o
enquadramento em manutenção preditiva.

### BK-09 — Ruído aéreo, silenciadores e amortecedor de pulsação

**Lacuna:** o invólucro (hood) é modelado apenas termicamente (Cap. 2.4,
eqs. 2.2–2.3). Não há menção a silenciador de admissão/descarga nem a nível de
pressão sonora ($L_{pA}$) — item de especificação obrigatório em pacotes de
alta potência (limite típico de ocupação humana a bordo). Na mesma linha, o
Cap. 16 identifica o risco de ressonância acústica (eqs. 16.2–16.3) mas não
menciona o acessório físico de mitigação (amortecedor de pulsação /
*volume bottle* / ressonador de Helmholtz como dispositivo).

**Ajuste proposto:** (a) uma frase no Cap. 5.3 (admissão) listando o
silenciador de admissão como acessório cuja perda de carga se soma à eq. 5.4;
(b) nota no Cap. 2.4 de que o hood é também **barreira acústica**, com nível
garantido medido segundo código de ensaio de ruído — referência a **verificar**:
ISO 2151 (*Acoustics — Noise test code for compressors and vacuum pumps*),
edição vigente; (c) no Cap. 16.2, após o critério de ressonância, mencionar o
amortecedor de pulsação como mitigação de projeto (a API 618, já citada, trata
desses dispositivos — sem referência nova).

## Prioridade baixa

### BK-10 — Velocidade periférica do rotor e Mach de ponta

**Lacuna:** os capítulos 9 e 11 tratam folgas e vazamento sem nunca amarrar a
rotação à velocidade linear do rotor — parâmetro que governa o número de Mach
nas folgas e o regime de escoamento de fuga (eqs. 9.2–9.3, 11.3).

**Ajuste proposto:** no Cap. 9.1 (geometria), $u_{\text{tip}} = \pi \cdot
D_{\text{macho}} \cdot N_{\text{macho}} / 60$ e $M_{\text{tip}} = u_{\text{tip}}/a$
(com $a = \sqrt{\gamma R T}$), explicando seu papel no vazamento e no limite de
projeto de rotores oil-free. **Cuidado:** $u$ sozinho colide com o vetor de
entradas do EKF (eq. 21.2) — usar $u_{\text{tip}}$. Faixa típica de projeto só
entra se vier de fonte real citável (`fleming`/`hanlon`), senão omitir números
(regra de veracidade).

### BK-11 — Balanço explícito do lado da água (soft-sensor de vazão de água)

**Lacuna:** os trocadores são modelados pelo lado do ar com $UA$/$\epsilon$-NTU,
mas a vazão de água de resfriamento — variável que o Cap. 12 reconhece como
fonte de ambiguidade diagnóstica ("$\epsilon$ cai por fouling **ou** por água
mais lenta") — não tem equação própria para ser **inferida** quando não há
medidor de vazão de água (situação comum em campo).

**Ajuste proposto:** no Cap. 10.1 ou 12.3, adicionar $\dot{m}_w \cdot c_{p,w}
\cdot (T_{w,\text{out}} - T_{w,\text{in}}) = \dot{Q}$ apresentada como
soft-sensor de $\dot{m}_w$, coerente com a filosofia do Cap. 18 (matriz
real/virtual). Sem símbolo novo além de $\dot{m}_w$ (conferir Nomenclatura).

### BK-12 — Aquecedores anticondensação do motor

**Lacuna (menor):** em ambiente offshore úmido, motores de alta potência levam
aquecedores anticondensação (*space heaters*) que mantêm o enrolamento acima do
ponto de orvalho com a máquina parada — acessório ausente do Cap. 3/4, diretamente
ligado à vida do isolamento já modelada por Arrhenius (eq. 4.7).

**Ajuste proposto:** um item curto no Cap. 4.4 (ou na lista do Cap. 3),
ligando o acessório à eq. 4.7 e ao cenário "motor em standby em atmosfera
salina saturada" (complementa a lógica de standby da frota do Cap. 16).

### BK-13 — Nota de escopo: dimensionamento da PSV pela ASME VIII

**Lacuna (menor, possivelmente deliberada):** a PSV existe como acessório
(Cap. 3.6) e suas falhas estão na matriz do Cap. 16, mas seu dimensionamento
(área de orifício pela ASME VIII Div. 1) não é citado. Defensável como fora do
escopo de monitoramento — mas uma frase explícita de escopo ("o dimensionamento
do orifício de alívio é matéria de projeto, não do Gêmeo Digital; ver ASME
VIII") evita a aparência de omissão.

**Ajuste proposto:** uma frase no Cap. 3.6 junto ao item PSV. Referência
`asme8` já existente.

## Ausências confirmadas como fora de escopo (não cobrar do livro)

Registradas para não reabrir discussão futura:

- Geração matemática do perfil do rotor (perfis SRM/"N", envoltórias) — matéria
  de projeto do fabricante, não de operação/Gêmeo Digital.
- $V_i$ ajustável (*slide valve*/*slide stop*) — típico de parafuso de
  refrigeração e de algumas máquinas oil-flooded, não desta classe (oil-free
  de ar, $V_i$ fixo — já corretamente modelado como fixo na eq. 5.6).
- *Surge*/estonagem — fenômeno de turbomáquina, não se aplica a deslocamento
  positivo (corretamente ausente).
- Partida direta/*soft-starter* e corrente de partida — o acionamento é VSD
  por definição de escopo (partida suave intrínseca); o transient relevante
  (partida em vazio via blow-down) já está na eq. 13.5.

## Fechamento sugerido ao implementar

1. Implementar em ordem de prioridade, um item por sessão de trabalho, com
   compilação de 3 passagens e inspeção do log (`grep -a`) ao fim de cada um.
2. Itens que tocam capítulos usados pelo `aplicativo/` (BK-01 no mínimo:
   `constantes.py` já marca FAD como ASSUMIDO) devem ser refletidos no app —
   ver `CONTEXTO_app.md` antes de mexer lá.
3. Ao final de cada sessão de implementação, atualizar `CONTEXTO.md` (o gatilho
   "Atualize contexto" é do autor; sem ele, registrar aqui o que foi feito e
   riscar o item deste backlog).


---

# Propostas novas (pós-backlog BK)

## V0-01 — Criar o Volume 0: cálculo básico e notações para o leitor de entrada

**Origem:** pedido do autor em 08/09/2026 — "um volume 0 com os termos
básicos de cálculo e de notações, para que os mais leigos aprendam e que os
formados há mais tempo relembrem". Atende também a recomendação do parecer
Manus (26/07/2026, item 2): um capítulo preparatório para ampliar o público,
criando dois níveis de leitura.

**Status:** ✅ **IMPLEMENTADO — o Volume 0 existe e está completo.**
*(Atualizado em 13/09/2026; este bloco dizia "proposta de trabalho — nada
implementado" desde 08/09.)*

O volume foi criado em **12/09/2026** como `Volume_0_Notacoes_e_Calculo.tex`
(commit `5210d92`) e, no mesmo dia, passou por um backlog próprio por
criticidade, implementado 8/8 (commit `7db0080`). Estado final: **42 páginas,
10 capítulos, 36 equações, 7 figuras, 7 tabelas, 18 exercícios resolvidos**,
compilação 3× com 0 erros / 0 overfulls / 0 referências indefinidas e varredura
de auto-referência 0/36.

**Como as quatro decisões em aberto foram resolvidas:**
1. **Formato** — documento separado, como recomendado aqui.
2. **Numeração** — mantida: o Volume 0 é anterior e opcional, I e II não mudaram.
3. **Profundidade** — intuição geométrica + regra de uso, sem demonstrações.
4. **Exercícios** — decidido **a favor** pelo autor: 18 exercícios resolvidos,
   2 por capítulo de conteúdo.

O escopo sugerido abaixo foi cumprido quase integralmente, com uma correção de
fato encontrada na implementação: o **"teorema de Stokes"** citado no escopo é,
no Volume I, a *hipótese* de Stokes (fluido newtoniano) — o teorema integral do
rotacional **não** é usado na coleção, e entrou apenas como menção de uma frase.

O planejamento detalhado e o resultado item a item estão em `Backlog_volume0.md`
(na raiz). O texto abaixo fica como registro da proposta original.

**Conceito.** Um volume de entrada da coleção *Enciclopédia de Máquinas
Rotodinâmicas*, posicionado antes do Volume I, cuja única função é remover a
barreira de linguagem matemática: o leigo aprende do zero; o formado há
décadas reativa o vocabulário em uma leitura. Nenhuma física de máquinas aqui
— só a matemática e a notação sem as quais os volumes seguintes não abrem.

**Escopo sugerido (a validar com o autor):**

- **Cálculo elementar em uma variável** — funções, limites, derivada como taxa
  e como inclinação, regras de derivação, integral definida como acúmulo,
  teorema fundamental, integrais impróprias (aparecem em todas as vidas úteis
  do Vol. II).
- **Cálculo em várias variáveis** — derivadas parciais, gradiente, integrais
  duplas/triplas e de linha/superfície (teorema de Stokes usado no Cap. 2 do
  Vol. I).
- **Equações diferenciais** — ODEs de 1ª e 2ª ordem, lineares, com coeficientes
  constantes (oscilador massa–mola, circuito RC/RLC como motivação);
  menção ao que é uma EDP, sem resolvê-las.
- **Séries e aproximações** — séries de Taylor (base da linearização do EKF e
  do truncamento de Navier-Stokes), séries geométricas, ordem de grandeza e
  arredondamento significativo.
- **Notação de engenharia** — somatórios e produtórios, índices e o convenio
  de Einstein, delta de Kronecker, letras gregas (tabela de leitura), vetores e
  tensores em notação de negrito (igual ao Vol. I), números complexos e fasores
  (ponte para o Cap. 7 do Vol. I), unidades SI e prefixos.
- **Ferramentas de leitura** — como ler uma equação numerada, como seguir um
  balanço (entra = sai + acumula), o significado dos operadores ∇, ∂/∂t, D/Dt
  antes de encontrá-los no Vol. I.

**Decisões em aberto (perguntar ao autor antes de implementar):**

1. **Formato** — novo documento `volume0.tex` (ou nome a definir) com a mesma
   classe e identidade visual do Vol. I, ou prefácio expandido do Vol. I?
   (Recomendação: documento separado — um prefácio não dá conta de 60+ páginas
   e a coleção ganha um degrau de entrada real.)
2. **Númeração** — Volume 0 implica renumerar? Não: a numeração atual (I e II)
   permanece; o Volume 0 é anterior e opcional.
3. **Profundidade** — até onde vai: parar antes de qualquer demonstração não
   trivial, ou incluir demonstrações curtas didáticas? (Recomendação: só
   intuição geométrica + regra de uso; demonstrações remetem a bibliografia.)
4. **Exercícios** — incluir exercícios resolvidos? (O parecer Manus recomenda
   exemplos numéricos resolvidos como um dos meios de ampliar o público.)

**Convenções ao implementar (seguindo o padrão do Vol. I):**

- Mesma classe `article`, pacotes, identidade visual e estilo de tabela
  (booktabs, `\caption[curta]{longa}`).
- Equações numeradas `\label{eq:v0-c<cap>-<n>}`; parágrafo didático **antes**
  de cada equação; sem equação "crua".
- Nenhuma referência bibliográfica sem verificação contra fonte real; a
  bibliografia pode ser mínima (1–2 livros-texto de cálculo, a definir).
- Nenhuma figura na primeira versão, salvo pedido do autor — o Cap. 7 do
  Vol. I já registra a questão da primeira figura da coleção.
- Símbolos novos entram na Nomenclatura do próprio volume (não tocar a do
  Vol. I); evitar colisões com as letras já saturadas dos volumes I e II.
- **Sem marcas de ferramenta de IA** em texto, comentários ou metadados —
  regra declarada pelo autor em 08/09/2026.
- Compilar 3 passagens, inspecionar o log (`grep -a`), renderizar páginas com
  `pdftoppm` para conferência visual. **Não commitar sem pedido explícito.**
