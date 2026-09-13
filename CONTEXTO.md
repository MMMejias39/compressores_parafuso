# Contexto do Projeto — Gêmeo Digital de Sistemas de Compressão Offshore

Este arquivo existe para que uma nova sessão do Claude (ou qualquer outra IA) possa
retomar o trabalho neste livro sem que o autor precise reexplicar tudo do zero.
Leia este arquivo inteiro antes de propor qualquer alteração no documento.

Quando o autor disser **"Atualize contexto"**, atualize este arquivo com um resumo do
que mudou na sessão atual (seguindo o estilo já usado abaixo). É um gatilho sob
demanda — fora dele, só reescreva este arquivo se a mudança for estrutural o
bastante para justificar (nova convenção, nova figura derivada, arquivo novo).

## O que é este projeto

`compressores.tex` é um livro técnico (**183 páginas** em 13/09/2026 — o "~84
páginas" que este parágrafo trazia desde 26/07/2026 estava congelado) sobre
construção de um Gêmeo Digital completo para compressores de parafuso rotativo
isentos de óleo usados em plantas de ar comprimido offshore (óleo e gás). O autor
escreveu o conteúdo original com apoio de um GPAI e vem revisando/expandindo o
documento em conjunto com o Claude ao longo de várias sessões.

**A coleção hoje tem três volumes**, não só este: `Volume_0_Notacoes_e_Calculo.tex`
(42 p., pré-requisitos matemáticos), `Volume_I_Fundamentos.tex` (87 p., fundamentos
teóricos) e `compressores.tex` (183 p., o Volume II descrito acima). Mais duas
implementações de referência: `aplicativo/` (Streamlit/Python) e `compressor2/`
(Rust/Axum).

Estrutura lógica do livro: primeiro a física e a engenharia de cada componente
(motor, gearbox, rotores, resfriamento, secagem PSA, vasos de pressão, instrumentação),
depois os mecanismos de falha de cada um, e só na segunda metade a metodologia
matemática/IA que une tudo (EKF, VAE, PIML, MPC, PSO) em um Gêmeo Digital funcional.
O objetivo declarado é permitir menor consumo energético, menor CO2eq e manutenção
preditiva baseada em condição real.

## Visão de longo prazo do projeto

O autor concebe `compressores.tex` como o **primeiro volume** de um projeto maior:
uma "enciclopédia digital" de equipamentos rotodinâmicos, inspirada na *Enciclopédie
de l'Ingénieur* (provavelmente a *Techniques de l'Ingénieur* francesa) que conheceu
na França em 2000 — uma obra de referência modular, onde o conteúdo é completo mas
cada tópico é autocontido o suficiente para ser consultado isoladamente, sem exigir
leitura cover-to-cover do conjunto inteiro.

O plano é que, no futuro, outros equipamentos rotodinâmicos (turbinas, bombas,
outras máquinas rotativas) entrem nesse mesmo "livro digital" como novos
volumes/capítulos, **com versionamento** — não um livro único e estático, mas uma
coleção viva que cresce mantendo cada parte consultável de forma independente.

Isso reforça (não substitui) as convenções já estabelecidas abaixo — "Diretriz
Técnica Final" ao fim de cada capítulo, explicação didática antes de cada equação,
capítulos organizados em Partes tematicamente coerentes (ver "Estrutura em duas
Partes" na seção de Convenções abaixo) — e deve orientar decisões futuras de
estrutura a privilegiar: (1)
capítulos/seções autocontidos e referenciáveis isoladamente; (2) uma arquitetura que
comporte novos volumes de outros equipamentos sem reescrever o que já existe; (3)
eventualmente um esquema de versionamento explícito — **repositório git
inicializado em 26/07/2026** (ver `.gitignore` na raiz, que exclui artefatos de
build do LaTeX `*.aux/.log/.out/.toc/.nav/.snm` e o ambiente Python
`scripts/venv/`, `scripts/__pycache__/`). O repositório tem histórico extenso
desde então (`git log --oneline` para o estado real — nunca cite hash de
memória) — mas a regra segue idêntica: **nunca crie commits sem pedido
explícito do autor.**

## Fluxo conceitual do pipeline completo (raciocínio do autor, 16/08/2026)

O autor articulou explicitamente a lógica de ponta a ponta que amarra livro,
apresentação e app — vale reler isso antes de propor qualquer mudança
estrutural grande, porque é o "porquê" por trás da ordem Parte I → Parte II
→ Parte III que já rege o documento. Fluxo, nas palavras do autor,
organizado em etapas, cada uma já mapeada ao que existe hoje:

1. **Entendimento do sistema de compressão** — cada elemento explicado, com
   sua posição no processo/sistema. → Parte I (Caps. 2–18), com o Cap. 2
   definindo a arquitetura dos quatro pilares.
2. **Equacionamento determinístico**, o mais realista possível. → toda a
   Parte I, física de primeiros princípios, sem componente de IA.
3. **Simulação** para verificar que os resultados fazem sentido físico e
   respondem a alterações. → o `aplicativo/` (`sistema.simular()`), com 71
   testes de sanidade que checam justamente isso — a grandeza se move na
   direção fisicamente esperada quando um parâmetro muda.
4. **Módulo de aprendizado com problemas inversos** para determinar
   parâmetros que a literatura não fecha como constante física, só como
   aproximação — e que por isso podem introduzir erro se usados cegamente
   num modelo de aprendizado de máquina. → Cap. 23.8 (PINN) + Cap. 28.1
   (EKF com estado aumentado), que citam explicitamente $K$, $\eta_{mec}$,
   $\zeta_{ref}$ como "valores de catálogo... calibrados em bancada, não na
   instalação real" — e a mesma lógica no app (`ekf.py`/`piml.py`).
5. **Perdas simuladas de tubulações, válvulas e outros acessórios** — parte
   do mesmo problema do item 4 (coeficientes de perda também são valores de
   catálogo, não constantes universais). → parcialmente coberto: tubulação
   interestágios (Eq. 5.15) e filtro de admissão (Eq. 5.4/$\zeta$) têm
   coeficiente próprio; válvulas específicas (blow-off, *check valve*, PSV)
   ainda não têm um coeficiente de perda parametrizado e identificável —
   ver pendência nova abaixo.
6. **Partir de um equipamento ajustado ("OK")** antes de usar os dados para
   aprendizado. → a **janela de calibração** do Cap. 28.1/EKF aumentado —
   comissionamento ou pós-manutenção confirmada, onde os estados dinâmicos
   são tratados como conhecidos para que os parâmetros estáticos convirjam.
7. **Aprendizado de máquina por algoritmos de gêmeos digitais.** → Parte II
   inteira (EKF, VAE, PIML, MPC, PSO).
8. **Simular diversos tipos de defeitos e mecanismos de falha** para
   aprender a reação do sistema, captada por sensores fixos ou móveis. →
   parcialmente coberto: Cap. 28.3 cataloga 57 mecanismos de falha e liga
   cada um a um algoritmo de detecção; Cap. 29/app demonstram **um**
   cenário completo (desgaste de folga) ponta a ponta. Sensores **móveis**
   e o treino sistemático sobre **múltiplos** mecanismos simultaneamente
   não existem ainda — ver pendências novas abaixo.
9. **Supervisório por máquina e sistema**, com detecção e acompanhamento do
   crescimento da falha. → o crescimento é coberto pelo prognóstico
   (Eq. 19.10, $RUL_\delta$ no Cap. 29); um supervisório real — painel
   contínuo monitorando uma frota, não uma simulação pontual de um cenário
   por vez — não existe ainda.

**Quatro lacunas reais identificadas por este exercício**, registradas
também em "Pendências conhecidas" para não se perderem:
- Sensores **móveis** (hoje só fixos, Tabela 18.1, pontos A–I instalados
  permanentemente) — nem o livro nem o app cobrem instrumentação portátil/
  não permanente.
- Perdas de **válvulas** como elemento parametrizado e identificável (hoje
  só tubulação e filtro têm coeficiente próprio; válvulas só aparecem como
  mecanismo de falha binário no catálogo do Cap. 28.3).
- **Treino sobre múltiplos mecanismos de falha simultaneamente** — hoje só
  um cenário (δ/L) é demonstrado ponta a ponta; não há geração sistemática
  de dados sintéticos cobrindo vários dos 57 mecanismos do catálogo para
  treinar um classificador mais geral.
- **Supervisório real** (painel contínuo por máquina/frota) — o app é uma
  ferramenta de simulação/demonstração pontual, não um sistema de operação
  contínua.

## Arquivos e pastas

- `compressores.tex` — Volume II, o documento principal (fonte única de verdade).
- `compressores.pdf` — PDF compilado (**183 páginas** em 13/09/2026).
- `Volume_I_Fundamentos.tex`/`.pdf` — Volume I, fundamentos teóricos (87 páginas,
  158 equações, ~50 figuras vetoriais TikZ/pgfplots escritas no próprio `.tex` —
  **não** usa `scripts/gen_figuras.py`, que é do Volume II). Nome canônico desde
  11/09/2026; `teorias.*`/`theorias.*` eram nomes de trabalho, removidos.
- `Volume_0_Notacoes_e_Calculo.tex`/`.pdf` — Volume 0, pré-requisitos
  matemáticos (42 páginas, 36 equações, 18 exercícios resolvidos). Mesmo padrão
  de figuras vetoriais no próprio `.tex`.
- `compressor2/` — implementação Rust 2.0 (workspace Cargo, `sim_core` +
  servidor Axum), 26 testes. Criada em 27/08/2026.
- `figuras/` — todos os PDFs de figura usados via `\includegraphics`. **Não edite
  estes PDFs diretamente** — regenere a partir da fonte (ver seção "Figuras" abaixo).
- `scripts/gen_figuras.py` — script Python (matplotlib) que gera a maior parte das
  figuras do livro. Ver seção "Figuras" para como rodá-lo com segurança.
- `apresentacao_compressores.tex` / `.pdf` — apresentação Beamer (21 slides, tema
  Metropolis, 16:9) derivada do conteúdo de `compressores.tex`, para uso em reuniões/
  defesa. É um arquivo **derivado e independente**: alterações no `.tex` principal
  (equações, figuras, texto) não se propagam automaticamente para os slides — se o
  conteúdo do livro mudar de forma relevante, os slides correspondentes precisam ser
  atualizados manualmente. Reaproveita os PDFs de `figuras/` já existentes (incluindo
  os dois com crédito CC BY-SA, mantido nos slides) e segue a mesma ordem lógica do
  livro (Parte I física/falhas → Parte II Gêmeo Digital). Compilar com
  `pdflatex -interaction=nonstopmode apresentacao_compressores.tex` (2 passagens).

## Convenções já estabelecidas no documento (siga-as, não reinvente)

- **Numeração**: equações, tabelas e figuras são numeradas por capítulo via
  `\numberwithin{...}{section}` (ex.: `eq:s5-13` = 5ª equação do Capítulo 5 → aparece
  como (5.13) no texto). Sempre referencie pelo número usando `\eqref{}`/`\ref{}`,
  nunca hardcode o número.
- **Notação**: o alfabeto grego já está ~90% saturado (γ,δ,ε,ζ,η,θ,λ,μ,ν,ξ,π,ρ,σ,τ,φ,ω
  todos em uso). Antes de introduzir um símbolo novo, verifique a tabela de
  Nomenclatura (logo após o Sumário) para não colidir com um símbolo já usado com
  outro significado em outro capítulo.
- **"Diretriz Técnica Final"**: todo capítulo técnico e anexo termina com um bloco
  padronizado `\textbf{Diretriz Técnica Final:} ...` — uma consequência prática do
  conteúdo do capítulo para o funcionamento do Gêmeo Digital. Mantenha esse padrão em
  qualquer capítulo novo.
- **Explicação antes da equação, com o número citado**: toda equação deve ser
  precedida de um parágrafo didático explicando o que ela representa e o
  significado de cada termo — não apresente equações "cruas". **Isso inclui citar
  o próprio número da equação via `\eqref{eq:sC-N}` no parágrafo que a antecede**,
  exatamente a mesma disciplina já exigida abaixo para figuras e tabelas (ex.:
  "A Equação~`\eqref{eq:s5-5}` calcula..." antes do `\begin{equation}`, não só
  depois). Um parágrafo que apenas *explica o conceito* sem citar o número não
  satisfaz esta regra — o objetivo é que o leitor já saiba "isto é a Equação X.Y"
  antes de encontrá-la, igual já acontece com toda figura/tabela do documento.
  **Achado em 15/08/2026**: uma varredura programática (contar, para cada
  `\label{eq:sC-N}`, se `\eqref{eq:sC-N}` aparece no texto imediatamente anterior)
  achou 110 das então 208 equações (53%) sem essa citação prévia — o padrão mais
  comum era um item de `itemize` com `\textbf{Nome do Conceito:}` seguido de frase
  explicativa, mas sem o `\eqref{}` de si mesma. Corrigido na mesma sessão (ver
  entrada de log correspondente mais abaixo). **Regra permanente daqui em diante**:
  toda equação nova precisa desse `\eqref{}` de si mesma no parágrafo anterior,
  mesmo quando já introduzida por um título em negrito de item de lista.
- **Figuras**: cada figura tem `\label{fig:C-N}` (C = capítulo, N = sequencial) e é
  antecedida por um parágrafo que a referencia via `Figura~\ref{fig:C-N}` antes de
  aparecer.
- **Tabelas**: mesma regra das figuras — `\label{tab:C-N}` e um parágrafo que a
  referencia por `Tabela~\ref{tab:C-N}` antes de ela aparecer, nunca "a tabela
  abaixo" (padronizado em 29/07/2026 nas 15 tabelas do livro).
- **Aspas**: sempre `` `` `` e `''`, **nunca** `"` reto — o babel-portuguese
  torna `"` um caractere ativo que engole o espaço seguinte (ver "Aspas retas
  quebram o espaçamento" mais abaixo). Exceção: dentro de `verbatim`, onde as
  aspas do código Python devem continuar literais.
- **Estrutura em duas Partes**: o livro é dividido em **Parte I — O Compressor e
  Seus Elementos** (Capítulos 2 a 18: física, engenharia e mecanismos de falha de
  cada componente) e **Parte II — Metodologia do Gêmeo Digital e Equacionamento
  Integrado** (Capítulos 19 a 27: EKF, VAE, PIML, MPC, PSO, a integração de tudo
  num motor de cálculo único, e a implementação de referência/frameworks). Os
  Capítulos 26 e 27 (implementação) **não são Anexos** — em 26/07/2026 o `\appendix`
  que os separava com numeração A/B foi removido a pedido do autor: como o livro já
  está dividido em Parte I/II, não fazia sentido também isolar esses dois capítulos
  como apêndices lettered dentro da Parte II. Eles são capítulos numerados normais,
  na sequência (a numeração de equações `eq:s26-*`/`eq:s27-*` já pressupunha isso —
  nenhuma equação precisou ser renomeada). O Capítulo 1 (Introdução) fica antes da
  Parte I, como preâmbulo. A Seção 1.3 do próprio livro também descreve essa
  divisão — mantenha as duas em sincronia se o capítulo final de alguma das partes
  mudar.
  **Implementação técnica — não use `\part{}` puro:** o comando `\part{}` padrão da
  classe `article` neste documento renderiza o título **desalinhado à esquerda** em
  vez de centralizado (causa não identificada — possivelmente interação com
  `hyperref`; nem envolver `\part{}` num `\begin{center}` resolve, o `\part`
  internamente escapa da centralização externa). A solução adotada foi **não usar
  `\part{}` para exibição**: cada página de Parte é montada manualmente — bloco
  `\clearpage`, `\thispagestyle{empty}`, `\phantomsection`,
  `\addcontentsline{toc}{part}{...}` (para entrar no sumário/bookmarks do PDF) e
  `\vspace*{\fill}...\begin{center}{\Huge\bfseries PARTE N}\\[2em]{\huge\bfseries
  Título}\end{center}\vspace*{\fill}`, seguido de `\clearpage` antes do capítulo
  seguinte. Ver as duas ocorrências no `.tex` (antes do Capítulo 2 e antes do
  Capítulo 19) como modelo para qualquer Parte futura (ex.: um 3º volume da
  enciclopédia).

## Diagramação — convenções (relatório de 26/07/2026, todos os itens implementados)

Em 26/07/2026 foi feita uma revisão completa de diagramação do PDF compilado (compilação limpa
conferida, mais inspeção visual das páginas via `pdftoppm`). O diagnóstico original está em
`relatorio_diagramacao.md` (movido em 16/08/2026 para `arquivos a eliminar/`, ver "Saneamento de arquivos" no fim deste arquivo). **Todos os 8 itens do relatório foram implementados**
no mesmo dia — o arquivo fica só como referência histórica do diagnóstico, não há mais pendência de
diagramação em aberto.

**O que foi feito:**
- **Item 1 — links do hyperref**: `\hypersetup{colorlinks=true, linkcolor=black, citecolor=black,
  urlcolor=black, pdftitle=..., pdfauthor=...}` no preâmbulo — sem mais caixas vermelhas ao redor de
  `\ref`/`\eqref`/`\cite`.
- **Item 2 — quebra de página por capítulo**: `\clearpage` antes de cada um dos 27 `\section` de
  capítulo. Documento foi de 87 para 95 páginas nesse passo (trade-off aceito).
- **Item 3 — cabeçalho corrente**: `fancyhdr` (`\pagestyle{fancy}`, `\sectionmark` redefinido,
  `\fancyhead[L]{\nouppercase{\leftmark}}`, `\fancyhead[R]{\thepage}`). Exigiu `headheight=14.5pt` na
  `\geometry{}`. Páginas especiais (capa, dedicatória, páginas de Parte) mantêm
  `\thispagestyle{empty}`, sem cabeçalho.
- **Item 4 — tabelas em `booktabs`**: as 14 tabelas antigas (`|l|l|`, `\hline` em toda linha) e as 7
  tabelas de Nomenclatura (`longtable`) foram convertidas para `\toprule`/`\midrule`/`\bottomrule`, sem
  barras verticais. Colunas largas de texto corrido usam
  `>{\raggedright\arraybackslash}p{Xcm}` em vez de `p{Xcm}` justificado. Havia ainda uma
  pseudo-tabela em `$$\begin{array}{|l|l|l|}...$$` (Capítulo 27, "Resumo da Stack de Vanguarda") fora
  do escopo original das 14 — convertida também, para uma `tabular` booktabs normal fora de modo
  matemático (o uso de `array` em modo matemático só para desenhar grade era impróprio).
- **Item 5 — microtype**: `\usepackage[expansion=false]{microtype}` logo após `fontenc`. **Atenção**:
  `expansion=true` causa erro fatal de compilação neste documento ("font expansion: auto expansion is
  only possible with scalable fonts") — as fontes usadas não são escaláveis o suficiente. Manter
  `expansion=false` se microtype for tocado no futuro.
- **Item 6 — capa**: adicionados rótulo de coleção/volume (`\colecaotitulo`, `\volumeatual`, `\revdata`
  — macros definidas no preâmbulo, reutilizáveis por um Volume II futuro), regras horizontais acima/
  abaixo do bloco de título, e a Figura 3.1 (render 3D dos rotores) em miniatura (`width=0.42\textwidth`
  — largura própria da capa, não faz parte do sistema de larguras do item 8).
- **Item 7 — identidade visual dos capítulos**: `titlesec` redefine `\section` para exibir
  `\chapterword~\thesection` (rótulo "Capítulo N") + regra fina abaixo do título. `\chapterword` é uma
  macro (`\newcommand{\chapterword}{Capítulo}`, no preâmbulo) — existe justamente para poder virar
  "Anexo" ou outra palavra num capítulo futuro que precise, via `\renewcommand`, sem tocar no
  `\titleformat`. **Não há mais `\appendix`/numeração A-B no documento** (removido em 26/07/2026, ver
  "Estrutura em duas Partes" acima) — os Capítulos 26 e 27 são capítulos numerados normais, com
  `\chapterword` no valor padrão "Capítulo" como todos os outros. `\section*` (Prefácio, Nomenclatura)
  não é afetado — continua exibindo só o título em negrito, sem rótulo nem regra (comportamento padrão
  do `titlesec`, confirmado visualmente).
- **Item 8 — larguras de figura padronizadas em 3 categorias** (das 15 figuras do corpo do livro,
  fora o thumbnail da capa que é um caso à parte): `0.60\textwidth` para gráficos/curvas técnicas
  (a maioria — Vogel, Basquin, EKF, LMTD, PSAT, etc.), `0.75\textwidth` para diagramas com legendas/
  caixas de texto (arquitetura do sistema, gearbox, Campbell, PSA) e `0.80\textwidth` para a única
  figura composta/complexa do livro (Figura 3.1, render 3D). Ao adicionar uma figura nova, classifique-a
  numa dessas 3 categorias em vez de escolher uma largura ad-hoc.

**Convenções permanentes para conteúdo novo** (para não reabrir a mesma dívida técnica):
- Todo `\section` novo de capítulo deve vir precedido de `\clearpage` (o rótulo "Capítulo N" do
  `titlesec` é automático, não precisa repetir manualmente).
- Toda tabela nova deve usar `booktabs` (`\toprule`/`\midrule`/`\bottomrule`, sem barras verticais),
  nunca `\hline`/grade antiga. Nunca usar `\begin{array}` em modo matemático só para desenhar uma
  grade de texto — isso é uma tabela, use `tabular`.
- Colunas de tabela com texto corrido (tipo as de Nomenclatura) devem usar
  `>{\raggedright\arraybackslash}p{Xcm}` em vez de `p{Xcm}` justificado.
- Figura nova: escolher uma das 3 larguras-padrão do item 8 acima conforme o tipo de conteúdo, não um
  valor ad-hoc.
- Toda figura e tabela nova precisa de **legenda curta e longa**:
  `\caption[curta para a Lista]{longa para o corpo}` — o documento tem Lista de
  Figuras e Lista de Tabelas desde 30/07/2026, e sem a forma curta a legenda
  inteira vaza para a lista e a torna ilegível.
- Termo técnico novo em inglês ou acrônimo novo que apareça com frequência: acrescentar ao
  `\hyphenation{}` do preâmbulo (acrônimos entram sem nenhum hífen, para nunca serem partidos).

## Figuras — como regenerar sem quebrar nada

A maioria das figuras é gerada por `scripts/gen_figuras.py` (matplotlib). **Duas
figuras são exceção** e vêm de imagens reais do Wikimedia Commons, sob licença
CC BY-SA, editadas (linhas reforçadas, marcadores de centro adicionados) e convertidas
via Inkscape:

- `figuras/fig_2_1_rotores.pdf` — de *Asymmetric Screw Compressor Rotor Mesh*
  (Slashme, Wikimedia Commons, CC BY-SA 4.0).
- `figuras/fig_15_1_psa.pdf` — de *Pressure swing adsorption principle*
  (Cmglee, Wikimedia Commons, CC BY-SA 4.0 / GFDL).

Há ainda uma terceira figura especial, **gerada** pelo script mas **derivada** de obra
CC BY-SA: `figuras/fig_3_1_parafuso3d.pdf` (Figura 3.1, render 3D do par de rotores).
A função `fig_parafuso3d()` faz varredura helicoidal do perfil 2D extraído de
`scripts/rotor_mesh_commons.svg` (cópia local do SVG *Asymmetric Screw Compressor
Rotor Mesh*, Slashme, Commons, CC BY-SA 4.0 — o mesmo da Figura 2.2). Por ser obra
derivada, o crédito CC BY-SA no `\caption{}` da Figura 3.1 deve ser mantido. A função
usa `pdfcrop` (do TeX Live) após salvar — mantenha-o instalado. O antigo corte
esquemático (`fig_3_1_corte.pdf` / `fig_corte_pacote()`) foi substituído a pedido do
autor, mas função e PDF foram mantidos caso se queira reutilizá-los.

Há uma quarta figura na mesma família: `figuras/fig_2_3_conjunto3d.pdf` (Figura 2.3,
Capítulo 2 — trem de compressão completo: motor → acoplamento → gearbox → estágio LP →
intercooler → estágio HP → saída). Gerada por `fig_conjunto3d()`, que reaproveita a
mesma varredura helicoidal de `fig_parafuso3d()` via uma versão parametrizada,
`_par_rotores_quads(x0, ylat, zlat, escala, ...)`, chamada duas vezes (LP maior, HP
menor) — mesmo crédito CC BY-SA do perfil de rotor se aplica aqui também. Motor,
gearbox, eixos e tubulação de processo usam as primitivas 3D `_caixa_quads()`
(paralelepípedos) e `_cil_quads(eixo, ...)` (cilindros ao longo de um dos 3 eixos), mais
`_engrenagem_quads(eixo, lo, hi, c1, c2, r_raiz, r_dente, n_dentes, ...)` (disco com
dentes retangulares, para bull gear/pinhões — mesma convenção cíclica de eixos que
`_cil_quads`, mas com raio variável raiz/dente em vez de raio constante).

**A primeira versão (26/07/2026, mesmo dia) usava só cilindros/caixas lisos e o autor
rejeitou por parecer "primitivas genéricas", não equipamento real.** A correção não foi
mudar de ferramenta, foi adicionar detalhe de superfície: aletas de refrigeração no
motor (vários `_cil_quads` finos de raio levemente maior, repetidos ao longo do corpo),
caixa de ligação (uma `_caixa_quads` em cima do cilindro), nervuras e tampa de inspeção
no gearbox, dentes reais nas engrenagens (`_engrenagem_quads` em vez de disco liso),
flanges nas juntas de tubulação (`_cil_quads` curto e de raio maior no meio de um tubo
mais fino) e um plano de chão (um único polígono N-gon plano, cor lisa sem
`_sombra3d`, no ponto mais baixo da cena) para a peça não parecer flutuando no vazio.
**Se for gerar uma figura mecânica nova neste projeto, não pare no primitivo liso —
esse acabamento de superfície é o que separa "esquema de brinquedo" de "ilustração
técnica" aos olhos do autor.**

**Três armadilhas para quem for mexer nessas funções:**
1. O perfil do SVG está em unidades de pixel (raio do rotor macho, `R_M`, da ordem de
   1300) — `_par_rotores_quads()` já normaliza dividindo por `R_M` antes de aplicar
   `escala`, de modo que `escala` passa a significar diretamente o raio do rotor em
   unidades da cena (mesma unidade do motor/gearbox). Se copiar essa lógica para uma
   figura nova, não esqueça dessa normalização — sem ela, o rotor fica ~1000x maior
   que todo o resto da cena e engole a figura inteira (foi exatamente esse o primeiro
   bug ao criar a Fig. 2.3).
2. Em `_cil_quads(eixo, lo, hi, c1, c2, ...)` e em `_engrenagem_quads(...)`, a
   convenção de `(c1, c2)` segue a ordem cíclica x→y→z→x das duas coordenadas *que
   sobram* após remover o eixo — ou seja, para `eixo="x"`: `(c1,c2)=(y,z)`; para
   `eixo="y"`: `(c1,c2)=(z,x)` (não `(x,z)` — é fácil errar essa, já aconteceu); para
   `eixo="z"`: `(c1,c2)=(x,y)`.
3. Geometria muito fina/sobreposta (ex.: um tubo atravessando o corpo de um rotor)
   confunde o `zsort="average"` do `Poly3DCollection` do `mplot3d` (que não é um
   z-buffer de verdade, só ordena polígono por polígono pela profundidade média) e
   produz oclusão errada. Prefira encostar peças pela superfície (ex.: bocal de sucção
   saindo tangente ao topo do rotor) em vez de fazer uma atravessar o volume da outra.

O script `gen_figuras.py` já está protegido: as funções `fig_rotores()` e `fig_psa()`
existem no arquivo (são rascunhos antigos em matplotlib, anteriores a eu encontrar as
imagens reais no Commons) mas **não são chamadas** no bloco `if __name__ == "__main__":`
— isso é proposital, para que rodar o script inteiro nunca sobrescreva essas duas
figuras reais com os rascunhos. **Não reative essas duas chamadas.** Se precisar
reeditar `fig_2_1_rotores.pdf` ou `fig_15_1_psa.pdf`, baixe o SVG original de novo
(`curl -sL "https://commons.wikimedia.org/wiki/Special:FilePath/<nome_do_arquivo>.svg"`)
e edite/converta via Inkscape — não use as funções matplotlib do script para essas duas.

**Três fotos reais adicionais (20/08/2026)**, mesmo princípio de imagem
livre real do Commons, mas via JPEG/foto (não SVG/desenho técnico como as
duas acima) — pipeline diferente, sem passar por `gen_figuras.py` nem por
Inkscape: `curl` da página `Special:FilePath` do arquivo original, recorte
com `convert <foto>.jpg -crop <geometria> +repage <foto>_crop.jpg`
(ImageMagick) para remover fundo de feira/oficina, depois
`convert <foto>_crop.jpg -quality 92 figuras/fig_C_N_nome.pdf` para
converter para PDF. Licença sempre confirmada visitando a página real do
arquivo (nunca só o nome sugestivo) antes de baixar:
- `figuras/fig_4_1_motor.pdf` — de *Electric motor make MarelliMotori*
  (S.J. de Waard, Wikimedia Commons, CC BY 2.5).
- `figuras/fig_13_1_valvulas.pdf` — de *Cologne Germany Bopp&Reutter-
  Safety-Relief-Valve-01* (CEphoto/Uwe Aranas, Wikimedia Commons, CC BY-SA 3.0).
- `figuras/fig_14_1_aftercooler.pdf` — de *Shell and Tube Heat Exchanger
  of Chiller* (Saud/SAF1999, Wikimedia Commons, CC BY-SA 4.0).

Se precisar reeditar qualquer uma das três, repita o `curl` na URL da
Special:FilePath (não há função em `gen_figuras.py` para elas, por não
serem desenho vetorial nem render matplotlib).

Para regenerar as demais figuras:
```bash
cd /home/mejias/Documentos/Compressores/scripts
python3 -m venv venv  # se ainda não existir
venv/bin/pip install matplotlib numpy
venv/bin/python gen_figuras.py
```
O script salva os PDFs direto em `../figuras/` (`OUTDIR` no topo do arquivo).

## Licenciamento de imagens — regra importante

Imagens de terceiros só podem ser usadas se tiverem licença livre reutilizável
verificada (ex.: CC BY, CC BY-SA no Wikimedia Commons) — **nunca** "apenas citar a
fonte" sem confirmar a licença real. Sempre credite no `\caption{}` com autor, fonte e
licença. Quando não existe imagem livre adequada (ex.: não havia corte 3D de
compressor com licença livre disponível), a solução adotada foi desenhar um esquema
original via matplotlib e creditar como "Esquema original elaborado pelo autor"
(ver Figura 3.1).

## Compilação

```bash
cd /home/mejias/Documentos/Compressores
pdflatex -interaction=nonstopmode compressores.tex
pdflatex -interaction=nonstopmode compressores.tex   # 2ª e 3ª passagens para
pdflatex -interaction=nonstopmode compressores.tex   # resolver referências cruzadas
```
Sempre rode 3 passagens e depois confira `compressores.log` por erros, referências
indefinidas ou labels duplicados antes de considerar a compilação concluída.

**Atenção**: dentro de `\begin{equation}...\end{equation}`, não deixe linhas em
branco — isso quebra a compilação (diferente de `$...$`, que tolera).

## Veracidade de referências e fontes — regra importante

Antes de adicionar qualquer `\bibitem` novo ao `thebibliography`, verifique-o contra
uma fonte real (editora, periódico, DOI, número de norma) — nunca confie num título,
autor ou ano "de memória"/gerado por IA sem checar. Um GPAI anterior já havia
introduzido 3 referências com títulos fabricados ou não verificáveis (`api684`,
`dompc`, `lysholm` — corrigidas em 26/07/2026, ver "Estado atual" abaixo) que
passaram despercebidas até uma varredura completa. Da mesma forma, qualquer
informação factual (técnica, histórica, numérica) apresentada ao autor deve indicar
a fonte de onde veio.

## Documentos de apoio

O subdiretório `documentos de apoio/` guardava material da base inicial do
trabalho — **movido em 16/08/2026 para `arquivos a eliminar/`** (o subdiretório
em si foi removido, vazio; ver "Saneamento de arquivos" no fim deste arquivo).
`referências iniciais.docx` contém as listas de referências bibliográficas geradas
nas sessões originais com o GPAI. Em 26/07/2026 essas listas foram cotejadas com a
bibliografia do `.tex`: 19 referências que haviam se perdido foram adicionadas ao
`thebibliography` e citadas nos pontos do texto onde cada tema aparece (Incropera no
LMTD, ASHRAE na psicrometria, Simon no EKF, Rawlings no MPC, Karniadakis 2021 no
PIML, Tao 2018 em Gêmeo Digital, IEC 60034-2-1 no motor, Shigley no Lewis, Hamrock
na lubrificação, Bently na vibração, Mobley na manutenção preditiva, White na perda
de carga, Atlas Copco no filtro coalescente, Brun & Kurz no contexto offshore,
Hanlon nos rotores, Moran na termodinâmica, e Modulus/DeepXDE/do-mpc no anexo de
implementação — que já eram usados no texto sem constar na bibliografia).

## Referenciamento de equações — convenção reforçada (26/07/2026)

Em 26/07/2026 foi feita uma varredura completa do `.tex` procurando equações sem
numeração ou embutidas em `$...$` no meio do texto corrido (dificultando o
`\eqref{}` a partir de outros capítulos). Achados e correções, por capítulo:

- **Capítulo 3** (Detalhamento de Componentes): tinha **zero** equações
  `\begin{equation}` apesar de conter 5 fórmulas físicas reais, todas em `$...$`
  dentro de itens de `itemize` (vazão do elemento compressor, calor do
  aftercooler, potência do aquecedor de regeneração PSA, perda de carga do
  filtro coalescente, dinâmica de pressão do vaso pulmão). Convertidas para
  `eq:s3-1` a `eq:s3-5`, cada uma precedida de frase explicativa, seguindo a
  convenção já usada nos demais capítulos.
- **Capítulo 17** (linha da destruição de exergia): havia um `$$ \dot{I} = T_0
  \cdot \dot{S}_{gen} $$` (sintaxe TeX antiga, sem numeração) logo antes da
  Equação~17-3, que já contém a mesma relação — em vez de duplicar o número,
  a linha foi reescrita como math inline dentro do parágrafo (a própria frase já
  dizia "essa é a mesma relação que abre a Equação 17-3").
- **Capítulo 6**: $f_r = \text{RPM}/60$ e $f_g = f_r \cdot Z$ (frequências de
  monitoramento) estavam embutidas em `itemize`; viraram `eq:s6-7`, com a antiga
  `eq:s6-7` (Torque de Referência) renumerada para `eq:s6-8`.
- **Capítulo 11**: $f_{gmf} = Z \cdot f_{\text{rot}}$ estava embutida em texto
  corrido; virou `eq:s11-8`, com as três equações seguintes do capítulo
  (Δτ, HI_HP, SPC) renumeradas de `eq:s11-8/9/10` para `eq:s11-9/10/11`
  (referências cruzadas no próprio Cap. 11 e uma no Cap. 15 atualizadas).
- **Capítulo 22** (VAE): a reparametrização $\ell = \mu + \sigma \cdot \epsilon$
  estava embutida em `itemize`, virou `eq:s22-1`; as equações de perda VAE e
  erro de reconstrução foram renumeradas de `eq:s22-1/2` para `eq:s22-2/3`.
- **Capítulo 26**: eficiência exergética $\eta_{ex} = 1-(\dot I/\dot{Ex}_{in})$
  estava embutida em `itemize`, virou `eq:s26-3` (não exigiu renumeração — era
  a última do capítulo).

**Casos revisados e mantidos como estão** (não são o mesmo problema): pequenas
substituições de valor concreto dentro de uma frase (ex.: "$D=1$ na falha",
"$\delta_{serv}=0$" ao descrever um nível de alarme específico) e definições de
símbolo em frases "Onde $X = ...$" logo após uma equação já numerada (ex.: $\psi$
no Cap. 17, $\omega_s$ no Cap. 4) — esse é o padrão já estabelecido no documento
para explicar um termo, não uma equação nova a referenciar.

**Regra permanente daqui em diante**: toda fórmula que expresse uma relação
física/matemática substantiva (não uma simples troca de símbolo por um valor
numérico específico, nem a definição de um termo dentro do "Onde ... é ..." que
já segue uma equação) deve estar em `\begin{equation}\label{eq:sC-N}...\end{equation}`,
nunca solta em `$...$`/`$$...$$` dentro do texto corrido. Ao inserir uma equação
no meio de um capítulo já numerado, renumere em cascata os labels seguintes
daquele capítulo (e suas referências `\eqref` em qualquer capítulo do
documento) para manter a correspondência "sufixo do label = número exibido"
descrita na seção de Convenções.

## Cobertura de desbalanço de fase no motor elétrico (26/07/2026)

O Capítulo 4 tratava o motor de indução trifásico com grandezas elétricas
sempre agregadas (uma corrente $I$ única, uma temperatura de enrolamento
$T_{\text{enrol}}$ única) — sem nenhuma equação distinguindo as três fases
entre si, apesar de desbalanço de tensão/corrente entre fases ser um
indicador clássico de falha incipiente (curto entre espiras, conexão
frouxa), especialmente relevante em redes elétricas isoladas offshore
(já citadas como desafio na Seção 1.4, mas nunca equacionadas). Foi
adicionado um novo item de mecanismo de falha ("Desbalanço de
Tensão/Corrente entre Fases e Sobreaquecimento Localizado") com a
Equação~4.8: `VU` (desbalanço de tensão) e `IU` (desbalanço de corrente,
nome escolhido para evitar `CU` — ambos na definição padronizada pela
NEMA MG1, nova referência `nemamg1` na bibliografia) mais
$\Delta T_{\text{fases}}$ (espalhamento entre as três temperaturas de
enrolamento por RTD). A antiga Equação de Acoplamento Global foi
renumerada de `eq:s4-8` para `eq:s4-9` (única referência cruzada, já
atualizada). Símbolos novos ($V_{L,i}$, $I_i$, $T_i$ para as grandezas por
fase, mais $VU$, $IU$, $\Delta T_{\text{fases}}$) adicionados à tabela de
Nomenclatura (Elétrica e Acionamento).

## Capítulo 3 expandido e inconsistência oil-free do Capítulo 12 corrigida (26/07/2026)

O Capítulo 3 tinha só uma linha por item (ex.: "Painel Elétrico e VSD: Controle
de frequência e mitigação de harmônicas"), sem explicar o que cada componente
é ou por que importa. Todos os 14 itens do capítulo (painel/VSD, motor,
elemento compressor, separador, aftercooler, drenos, torres PSA, resistências,
válvulas de comutação, filtros coalescentes, válvulas de bloqueio/retenção,
vaso de pressão, PSV, transdutores) ganharam uma definição real, e o
significado físico de cada equação já numerada (eq:s3-1 a eq:s3-5) foi
reforçado (ex.: por que $\eta_{\text{vol}}<1$, por que só $U$ explica queda de
$\dot Q$ com $A$ fixa, por que normalizar $\Delta P$ antes de comparar entre
condições de carga).

Ao escrever a definição do "Separador de Ar/Óleo" (item da Seção 3.2), ficou
evidente uma **inconsistência real pré-existente**: o Capítulo 12 ("Sistema de
Lubrificação e Gestão Térmica") tinha uma subseção "Balanço de Energia e
**Injeção de Óleo**" e uma Equação 12.2 ($P_{\text{rede}} = P_{\text{int}} -
\Delta P_{\text{sep}}$) que só fazem sentido numa arquitetura **oil-flooded**
(óleo injetado na câmara de compressão, com separador ar/óleo no caminho do ar
antes da rede) — contradizendo o restante do livro (Capítulos 1, 2, 3, 7, 8,
11), que define repetidamente o compressor como **isento de óleo** na câmara
de compressão. Provável resquício do rascunho original com GPAI, nunca
ajustado quando a arquitetura oil-free foi fixada como escopo. Corrigido a
pedido do autor:
- "Injeção de Óleo" → "Balanço de Energia do **Circuito** de Óleo": a
  Equação~12.1 agora iguala o calor removido pelo óleo à potência de atrito da
  gearbox/mancais já modelada nas Equações 6.3, 6.4 e 7.4 (não mais uma troca
  térmica com o ar de descarga). Símbolos $T_{\text{desc}}/T_{\text{inj}}$
  (terminologia de oil-flooded) renomeados para $T_{\text{óleo,ret}}$ (retorno,
  quente) / $T_{\text{óleo,sup}}$ (suprimento, após o resfriador).
- "Eficiência do Separador de Ar/Óleo" → "Perda de Carga no **Deaerador** e
  Pressão de Suprimento aos Mancais": a Equação~12.2 agora calcula a pressão
  de óleo que chega aos mancais ($P_{\text{sup,óleo}} = P_{\text{bomba}} -
  \Delta P_{\text{sep}}$), não mais a pressão de rede do ar comprimido — mesma
  interpretação (deaeração do óleo de retorno) já usada na definição do
  Capítulo 3.
- Tabela de diagnóstico térmico e Diretriz Técnica Final do Capítulo 12
  atualizadas para os novos símbolos. Nenhuma equação foi renumerada (labels
  `eq:s12-1`/`eq:s12-2` mantidos).

**Se uma sessão futura tocar o Capítulo 12 (ou qualquer menção a "circuito de
óleo")**: o óleo deste documento nunca entra em contato com o ar de processo —
ele existe só para lubrificar/resfriar a gearbox e os mancais. Não reintroduza
linguagem de "injeção de óleo" ou "separador ar/óleo" no caminho do ar.

O Capítulo 12 foi depois **expandido em 30/07/2026** (de 656 para 1.959
palavras, com $UA$/$NTU$, válvula termostática modelada e constante de tempo
térmica) — ver "Referências completadas e Capítulos 12/13 expandidos" abaixo
antes de mexer nele.

## Convenção de commits: sem trailer de coautoria (26/07/2026)

O autor pediu explicitamente para remover a linha `Co-Authored-By: Claude
Sonnet 5 <noreply@anthropic.com>` de **todos** os commits do repositório —
inclusive os 4 commits anteriores a esta sessão, que já vinham com essa linha
(comportamento padrão do Claude Code, não pedido pelo autor). O histórico
inteiro foi reescrito via `git filter-branch --msg-filter` para remover a
linha das 10 mensagens de commit então existentes, preservando o conteúdo
(árvores idênticas, só hash/mensagem mudaram); a tag `v1.0` foi recriada
apontando para o novo hash do commit inicial; os backups automáticos do
`filter-branch` (`refs/original/*`) foram removidos, o reflog expirado e o
repositório passou por `git gc --aggressive --prune=now`. Não havia remoto
configurado, então a reescrita foi segura (sem necessidade de force-push).

**Regra permanente**: nunca inclua `Co-Authored-By: Claude...` (ou qualquer
outra menção de autoria/coautoria de IA) em mensagens de commit deste
repositório, mesmo que seja o comportamento padrão do Claude Code. O autor
foi explícito: não é uma questão de crédito técnico, é não associar autoria
de IA a um livro que é dele. Vale para qualquer sessão futura, indefinidamente.

## Inventário de algoritmos da Parte II (26/07/2026)

A pedido do autor, foi feito um levantamento de quais algoritmos já existem
para rodar o Gêmeo Digital (Capítulos 19-27) e aprofundados os que apareciam
só citados por nome. Estado por categoria:

- **Estimação de estado**: EKF — teoria (Cap. 20-21) **e** código de
  referência em NumPy (Cap. 26).
- **Redução de dimensionalidade/anomalia**: VAE — equacionamento completo
  (Cap. 22), sem código.
- **Físico-informado**: PIML/PINNs — equacionamento (Cap. 19, 23) **e**
  código em PyTorch (Cap. 26).
- **Otimização/controle**: MPC e PSO — equacionamento completo (Cap. 19, 24),
  sem código.
- **Diagnóstico/RUL**: *rainflow* + Palmgren-Miner + Basquin (Cap. 19).
- **Incerteza/explicabilidade**: propagação de incerteza GUM (Cap. 25, Eq.
  25.3), Redes Bayesianas (citado, Cap. 25), SHAP (Cap. 25, Eq. 25.4).
- **Pré-processamento**: Savitzky-Golay, Isolation Forest (Cap. 25) e
  Processo Gaussiano para incerteza do RUL (Cap. 19) — **aprofundados nesta
  sessão** (ver abaixo); antes eram só citados por nome, sem equação.
- **Frameworks de alta performance** (Cap. 27): NVIDIA Modulus (PINNs/FNO),
  DeepXDE (solver de PDE), do-mpc (MHE).

**Candidatos ainda só citados por nome, sem equação** (se uma sessão futura
for aprofundar mais algo da Parte II, comece por aqui): Redes Bayesianas
(Cap. 25) e os detalhes de MHE do do-mpc (Cap. 27).

**Déficit de figuras identificado e corrigido**: a Parte II tinha só 2
figuras em 9 capítulos (curva de Basquin no Cap. 19, ciclo do EKF no
Cap. 21), contra 14 na Parte I — o autor notou a falta de ilustração das
ferramentas matemáticas. Adicionadas 4 figuras didáticas 2D (estilo
matplotlib já usado no livro, não 3D — aqui são conceitos de algoritmo, não
peças físicas):
- **Figura 22.1** (`fig_vae_arq()` → `fig_22_1_vae.pdf`): arquitetura do VAE
  em "gargalo" (encoder → espaço latente $\ell(\mu,\sigma)$ → decoder).
- **Figura 24.1** (`fig_mpc_horizonte()` → `fig_24_1_mpc.pdf`): horizonte
  deslizante do MPC (medido, predito, referência, só $u(k)$ aplicado).
- **Figura 24.2** (`fig_pso_enxame()` → `fig_24_2_pso.pdf`): convergência do
  enxame do PSO (dois painéis lado a lado, dispersão inicial vs. convergida).
- **Figura 25.1** (`fig_isoforest()` → `fig_25_1_isoforest.pdf`): princípio
  geométrico do Isolation Forest (ponto anômalo isolado em poucos cortes).

Armadilha encontrada ao gerar a Fig. 24.2 (PSO): partículas geradas por
`rng.normal` sem limite podiam cair fora dos eixos do gráfico, produzindo
setas/pontos "vazando" para fora do quadro — corrigido com `np.clip()` nas
posições e nos alvos das setas de velocidade. Se gerar uma figura nova com
posições aleatórias, sempre recorte (`clip`) para os limites dos eixos antes
de desenhar.

Trabalho feito nesta sessão: Savitzky-Golay (Cap. 25, forma de convolução
com coeficientes pré-calculados, Equação 25.1), Isolation Forest (Cap. 25,
escore de anomalia por comprimento de caminho de isolamento, Equação 25.2) e
Processo Gaussiano (Cap. 19, regressão bayesiana não paramétrica para
propagar incerteza no RUL, Equação 19.10, conectada à Equação 25.3).
Símbolos *namespaced* para não colidir com os já usados no livro: $p_{SG}$,
$m_{SG}$ (grau/janela do SG, evitam colidir com $p$ = número de polos do
motor e $m$ = módulo de engrenagem do Cap. 8), $n_{IF}$ (evita colidir com
$n$ = índice politrópico), $\gamma_{EM}$ (evita colidir com $\gamma$ = razão
de calores específicos) e $\ell_{GP}$ (evita colidir com $\ell$ = vetor
latente do VAE). Três referências novas, verificadas via busca web contra
fontes reais antes de inserir (DOI/editora conferidos): `savgol` (Savitzky
e Golay, Analytical Chemistry 1964), `isoforest` (Liu, Ting e Zhou, ICDM
2008) e `gpml` (Rasmussen e Williams, MIT Press 2006). Renumeração em
cascata: `eq:s19-10`→`eq:s19-11`; `eq:s25-1`/`eq:s25-2` (antigas, propagação
de incerteza e SHAP) →`eq:s25-3`/`eq:s25-4`.

## Correção de extração de texto: ligaduras fi/ff (26/07/2026)

O autor trouxe uma análise externa (Copilot CLI, salva em `recomenda
compressores.txt` na raiz — não tocar/commitar esse arquivo sem pedido
explícito) apontando "problemas de codificação": palavras com ligaduras
tipográficas "ff"/"fi" (offshore, eficiência, buffer, Jeffcott,
confiabilidade, definição, significativo...) extraíam do PDF com bytes de
controle literais (0x1B para "ff", 0x1C para "fi") no lugar das letras —
confirmado por inspeção direta dos bytes via `pdftotext | xxd`, 31
ocorrências antes da correção. **A aparência visual/impressa nunca foi
afetada** (conferido renderizando páginas) — o defeito era só na extração
de texto (busca, cópia, indexação, acessibilidade).

O diagnóstico de causa do Copilot estava **errado**: ele recomendou
reforçar `\usepackage[T1]{fontenc}`/`\usepackage[utf8]{inputenc}`, mas
ambos (e `microtype`) já estavam no preâmbulo desde o início. A causa real
era a ausência do pacote `cmap`, que corrige o mapeamento Unicode das
ligaduras do Computer Modern na tabela ToUnicode do PDF — problema
conhecido do pdflatex, sem relação com fontenc/inputenc. Corrigido
adicionando `\usepackage{cmap}` **antes** de `fontenc` no preâmbulo (linha
~4). Verificado: 0 bytes de controle após a correção; PDF idêntico
visualmente (105 páginas, mesmo layout).

**Regra permanente**: `cmap` deve continuar sendo o primeiro pacote
carregado, antes de `fontenc`. Se o preâmbulo for reordenado no futuro, não
mova `cmap` para depois de `fontenc`.

O resto do relatório do Copilot (referências normativas/livros-texto sem
ano, e 27 sugestões de conteúdo por capítulo — estudo de caso numérico,
tabela FMEA, roadmap de maturidade, notebook reproduzível etc.) **não foi
implementado nesta sessão**: são adições de conteúdo genéricas, tipo
checklist, não correções de algo quebrado, e o autor não pediu para
persegui-las. Se uma sessão futura for revisitar esse relatório, comece
relendo-o com ceticismo — o diagnóstico de causa já errou uma vez.
(**Atualização de 30/07/2026**: o item das referências sem ano/edição foi
resolvido — ver "Referências completadas e Capítulos 12/13 expandidos"
abaixo. As 27 sugestões de conteúdo continuam sem implementação.)

## Parecer do Manus e aprofundamento da Parte II (29/07/2026)

O autor trouxe uma segunda análise externa, `Manus_parecer_final_compressores.md`
(Manus AI, 26/07/2026, na raiz do projeto — mesmo status do `recomenda
compressores.txt`: não rastreado, não commitar sem pedido). Diferente do relatório
do Copilot, este acertou o diagnóstico: fragilidades editoriais reais (capítulos
curtos demais na Parte II, com 253 a 511 palavras, "com caráter de notas técnicas")
e três problemas normativos concretos, todos verificados e corrigidos:

- **ISO 20816-3 não se aplica a este equipamento.** A norma exclui explicitamente
  de seu escopo os compressores rotativos de deslocamento positivo, citando os de
  parafuso como exemplo — o que invalida o limiar genérico de $7{,}1\,$mm/s
  usado por extensão da família ISO 10816/20816. O documento agora trata isso
  explicitamente em dois lugares: no Capítulo 1 (uma norma citada *por não se
  aplicar*) e no Capítulo 18, junto à matriz de alarmes, com a justificativa
  física (a assinatura vibratória do parafuso é dominada por passagem de lóbulos
  e pulsação de gás, que elevam a vibração global sem significar degradação). Os
  critérios passam a vir da API 619, do OEM e da linha de base da própria
  máquina. Símbolo novo $v_{trip}$ na Nomenclatura, e `iso20816` é a única
  referência bibliográfica nova da sessão (`iso8573` já existia).
- **ISO 8573-1 define classes, não um valor universal de $-40\,^{\circ}$C.** O
  limite adotado no livro passou a ser identificado como **Classe 2**, escolhida
  como requisito de projeto, com registro obrigatório do ponto de medição e da
  pressão de referência (PDP sob pressão de linha $\neq$ PDP após expansão).
- **ISO 1217 precisa da Emenda 1:2016** — é ela que padroniza o cálculo da
  eficiência isentrópica usada como KPI nos Capítulos 9, 11 e 17.

Aprofundamento dos capítulos curtos da Parte II (14 equações novas: `eq:s21-2`
a `eq:s21-8`, `eq:s22-3` a `eq:s22-7`, `eq:s23-3/4`, `eq:s24-2/3/4`, `eq:s26-4`):

- **Cap. 21 (EKF)**: definição concreta dos vetores para este compressor,
  condição de observabilidade, inovação e validação estatística por NIS
  ($\chi^2$), forma de Joseph para condicionamento numérico, limites da
  linearização.
- **Cap. 22 (VAE)**: por que VAE e não PCA/autoencoder simples, origem da perda
  no ELBO, premissa crítica de pureza do conjunto de treinamento, definição do
  limiar de disparo, espaço latente como assinatura de saúde (Mahalanobis).
- **Cap. 23 (PIML)**: operador físico concreto, perda híbrida, pontos de
  colocação e diferenciação automática, balanceamento adaptativo, **limitações e
  cautelas** (o próprio Karniadakis 2021 alerta para a imaturidade dos
  benchmarks), e a **divisão de papéis entre PIML e EKF** — o EKF é online e
  pontual no tempo, o PIML é offline e cobre o envelope; o substituto treinado
  por PIML pode virar a função de transição $f(\cdot)$ do EKF e o modelo de
  predição do MPC.
- **Caps. 24, 26 e 27** também expandidos (MPC/PSO, $HI$, stack de alta
  performance).

Além disso: as **15 tabelas do livro ganharam `\label{tab:C-N}`** e um parágrafo
que as referencia por `Tabela~\ref{}` antes de aparecerem (antes eram todas
"a tabela abaixo"), cerca de 25 símbolos novos entraram na Nomenclatura, e as
referências científicas ganharam volume/páginas/DOI. Documento foi de 105 para
123 páginas.

**Esta sessão não gerou commits** — todo o trabalho ficou na árvore de trabalho
e continuou assim na sessão seguinte (ver "Estado atual" abaixo).

## Referências completadas e Capítulos 12/13 expandidos (30/07/2026)

Continuação direta da sessão anterior, atacando dois itens que restavam do
parecer do Manus. (Os outros dois — glossário bilíngue de anglicismos e a
crítica ao termo "Enciclopédia" no título — foram deliberadamente **não**
perseguidos: o segundo contraria a visão de longo prazo do autor registrada no
topo deste arquivo.)

**Ano/edição de todas as referências que não tinham**, cada uma conferida contra
fonte real antes de entrar (regra permanente da seção "Veracidade de
referências"): API 619 (5ª ed., 2010, R2024), API 618 (5ª, 2007), API RP 684
(2ª, 2005, R2010), NORSOK M-501 (7ª, 2022), ASME BPVC VIII-1 (2023), IEC 60079-0
(Ed. 7.0, 2017), IEC 60255-1 (Ed. 2.0, 2022), NEMA MG 1-2021, AGMA 2001-D04
(2004, R2016), Çengel (9ª, 2019), Bejan (4ª, 2016), Incropera (8ª, 2017), White
(8ª, 2016), Shigley (11ª, 2020), Hamrock (2ª, 2004), mais volume/páginas/DOI em
Basquin, Palmgren, Miner, Vogel, Fleming e Glaessgen. Três achados que a
verificação produziu, e que valem como alerta para o futuro:

- **IEC 60034-2-1** estava sendo citada sem ano, mas o conteúdo pressupunha a
  Ed. 2.0 (2014), **já substituída** pela Ed. 3.0 (2024).
- **API RP 684**: a menção a "API TR 684-1" não se confirmou em nenhuma fonte e
  foi removida (resquício provável do rascunho com GPAI).
- **Incropera e Shigley** trocaram de ordem de autoria nas edições atuais
  (Bergman/Lavine/Incropera/DeWitt e Budynas/Nisbett) — as chaves `\cite{}`
  foram mantidas, e nenhuma prosa citava esses autores pelo nome.

**Capítulo 12** (656 → 1.959 palavras, `eq:s12-3` a `eq:s12-7`): o eixo do
capítulo passou a ser que a efetividade $\epsilon$ do Cap. 7 é **ambígua** em
aplicação offshore — cai igual por incrustação interna ou por água de
resfriamento mais quente/mais lenta. Entram $UA$ como grandeza invariante às
temperaturas de entrada, a relação $\epsilon$–$NTU$–$C_r$ (contracorrente,
citando Incropera), o fator de degradação $\eta_{UA}$, a válvula termostática
modelada (permite **inferir** a posição efetiva das três temperaturas medidas e
comparar com a comandada) e a constante de tempo térmica $\tau_{th}$, que
sintoniza o atraso de alarme e — por ser proporcional à massa de óleo — resolve
o cenário "Baixo Nível de Óleo", ambíguo em regime permanente. A matriz de
diagnóstico ganhou uma coluna de confirmação quantitativa ligando cada linha a
uma dessas grandezas.

**Capítulo 13** (513 → 2.158 palavras, 4 equações novas): a Equação 13.1 não
tinha **nenhum** parágrafo explicativo e usava $\Phi(r)$ sem jamais definir a
função — violação direta da convenção "explicação antes da equação". Corrigido,
com $\Phi(r)$ agora explícita nos regimes subsônico e bloqueado (`eq:s13-2`, à
qual o Cap. 14 passou a se referir como caso particular do dreno). Novas:
potência específica por estratégia de modulação, frequência de ciclagem em
função de volume de rede e banda morta (com o resultado de que a ciclagem é
mais severa a 50% de demanda, não nos extremos) e a elasticidade do consumo à
pressão de descarga — que **deriva** os "~7% por bar" da regra de campo em vez
de citá-la (7,4% para 8→9 bar com $n=1{,}35$; 7,2% a 7,6% para $n$ entre 1,3 e
1,4). Registrada também a advertência de que a forma quadrática do VFD **não** é
lei de afinidade: máquina de deslocamento positivo tem potência aproximadamente
linear com a rotação, e transportar a lei cúbica de turbomáquinas superestima
grosseiramente a economia do VSD. Renumeração em cascata: `eq:s13-2`..`6` →
`eq:s13-3`..`6` e `10`.

### Aspas retas quebram o espaçamento (armadilha do babel)

Ao conferir o render do Cap. 12, `"o trocador sujou" de` saía como
`"o trocador sujou"de`. Causa: `\usepackage[brazilian]{babel}` torna `"` um
**caractere ativo** (*shorthand* do babel-portuguese), que engole o espaço
seguinte. Eram 28 ocorrências em prosa espalhadas pelo livro inteiro, todas
anteriores a esta sessão. Convertidas para `` ``...'' ``; as aspas dentro dos
blocos `verbatim` de código dos Capítulos 26/27 foram preservadas intactas
(ali `"` tem catcode 12 e precisa continuar literal). Extração do PDF agora
devolve “ ” Unicode corretas.

**Regra permanente**: nunca usar `"` reto em texto corrido neste documento —
sempre `` `` `` e `''`. Vale para qualquer conteúdo novo. É a mesma família de
defeito da correção do `cmap` (aparência impressa correta, extração de texto
quebrada), e igualmente invisível sem inspecionar o PDF gerado.

A Nomenclatura ganhou uma tabela nova (**Controle, Modulação e Válvulas**, 14
símbolos) mais 7 símbolos térmicos, e cinco convenções novas de desambiguação
foram registradas na subseção "Convenções de Desambiguação Adotadas":
$\tau$ (torque) permanece e as constantes de tempo viraram $\tau_{th}$/$\tau_{bd}$;
$x$ (estado do EKF) permanece e a fração de carga virou $x_c$; $a$ (constante de
Vogel) permanece e a abertura da válvula termostática virou $a_{tv}$; e $\delta$
tem uso duplo **contextual** (folga nos capítulos de rotores, estado binário da
válvula no Cap. 13) — mantido assim por ser a convenção estabelecida nas duas
literaturas, mas agora explicitado.

## Fechamento dos dois relatórios externos (30/07/2026)

O autor pediu para "atender" os dois arquivos de análise externa da raiz. Ambos
foram reexaminados contra o documento **atual** (não o de 26/07, 24 páginas
menor), e o resultado se divide em três partes.

**1. `relatorio_diagramacao.md` — nada a fazer, mas a regressão foi conferida.**
Os 8 itens continuam implementados depois de todo o conteúdo novo: `hypersetup`
com metadados preenchidos, 28 `\clearpage` para 27 capítulos, `fancyhdr`,
**zero** `\hline`/`tabular{|`/`array{|` no arquivo inteiro, `microtype`,
`\chapterword` do `titlesec`, e as larguras de figura ainda nas 3 categorias
(12× `0.60`, 6× `0.75`, 2× `0.80`, mais o `0.42` da capa). Vale repetir essa
varredura sempre que muito conteúdo novo entrar — é barata e detecta
regressão de convenção.

**2. Dois erros de unidade reais, encontrados a partir do relatório do Copilot.**
Ele alegava "unidades inconsistentes em algumas equações" no Capítulo 9 sem
apontar qual. A alegação **procedia**, e uma varredura pela classe do erro
(mistura de RPM com Hz/rad·s⁻¹) achou dois casos:
- **Equação 9.8** calculava a frequência de passagem dos lóbulos como
  $f_{bp} = N_{\text{macho}} \cdot Z_{\text{macho}}$ — **faltava dividir por 60**.
  $N$ é RPM em todo o documento e $f_{bp}$ é Hz na Nomenclatura; o próprio
  Capítulo 6 já fazia a conversão certa na Equação 6.7. Erro de fator 60.
- **Equação 11.6** (vida do rolamento de escora) usava $\omega$ — definida como
  rad·s⁻¹ na Nomenclatura — dentro de $10^6/(60\,\omega)$, fórmula que só fecha
  com rotação em RPM. Trocado por $N_{\text{rot,HP}}$, alinhando com a Equação
  8.4, que já estava correta.

Ambas as correções vieram com uma frase explicando **por que** a conversão é
obrigatória, para não voltarem. Lição para sessões futuras: alegação vaga de
revisor externo pode estar certa — vale converter em varredura sistemática por
classe de erro antes de descartar.

**3. Melhorias de navegação implementadas.**
- **Lista de Figuras e Lista de Tabelas** após o sumário (item 4 das "correções
  de produção" do Copilot, o único ainda pendente e coerente com a visão de obra
  de consulta): 20 figuras e 15 tabelas, ambas entrando no sumário e nos
  bookmarks via `\phantomsection` + `\addcontentsline`.
- **Legendas curtas** (`\caption[curta]{longa}`) em 30 das 35 legendas — sem
  elas as listas ocupavam 3 páginas de texto corrido ilegível; agora a Lista de
  Figuras cabe em uma página escaneável. **Toda figura ou tabela nova deve trazer
  as duas formas**: a curta para a lista, a longa para o corpo.
- **`\hyphenation{}` no preâmbulo** para termos em inglês e acrônimos. O
  babel-brazilian aplicava padrões do português a eles e produzia quebras
  erradas — confirmadas no PDF: `Offloa-ding` e, pior, `ASH-RAE` (acrônimo
  partido). A lista dá o padrão correto dos termos recorrentes e registra os
  acrônimos sem ponto de quebra nenhum.

**Deliberadamente recusado do relatório do Copilot** (registrar para não
reabrir): (a) `\usepackage[none]{hyphenat}` — desligar hifenização em texto
justificado destrói o espaçamento, o problema real era de padrões, não de
hifenização em si; (b) `utf8x` e compilar com lualatex/xelatex — desnecessário,
o `cmap` já resolveu a extração e a mudança de motor quebraria o setup de fontes
pk atual; (c) "recomendação de manufaturador" nas tabelas de instrumentação —
o livro é deliberadamente neutro quanto a fabricante; (d) tabelas de OPEX/CAPEX,
hiperparâmetros iniciais, versões de dependências e tempos de ciclo "típicos" —
exigiriam números inventados, o que colide frontalmente com a regra de
veracidade deste projeto. Se uma sessão futura for implementar qualquer um
desses, os números têm de vir de fonte real e citada, ou não entram.

Com isso, **os dois relatórios externos estão encerrados**: tudo que era defeito
verificável foi corrigido, e o que sobrou está registrado acima como recusado
(com motivo) ou nas "Pendências conhecidas" abaixo como melhoria opcional.

## Estrutura dos Capítulos 26/27 e código Python inválido (31/07/2026)

Ao conferir o sumário depois de inserir a Lista de Figuras, notou-se que os
**Capítulos 26 e 27 eram os únicos do livro sem nenhuma `\subsection`** — usavam
`\textbf{1. Título}`, `\textbf{2. Título}` como pseudo-títulos. O efeito era que
dois capítulos de 4 páginas cada não tinham nenhuma entrada de subseção no
sumário nem nos bookmarks do PDF, o que contraria diretamente a ideia de obra
consultável por seção. As 11 ocorrências (5 no Cap. 26, 6 no Cap. 27) foram
convertidas em `\subsection{}` reais, com a numeração manual removida (agora é
automática: 26.1 a 26.5, 27.1 a 27.6).

Essa conversão expôs um defeito bem mais sério nos três blocos `verbatim` de
código: **a indentação Python estava achatada**. Todas as linhas carregavam o
mesmo prefixo de dois tabs — usado para indentar o fonte LaTeX — de modo que o
corpo das funções ficava no mesmo nível do `def`. O código impresso no livro,
num capítulo chamado "Implementação Base e Ferramentas Padrão", **não era Python
válido**: copiá-lo do PDF produzia `IndentationError`. Os três blocos (EKF em
NumPy, perda PIML em PyTorch, exemplo Modulus) foram reescritos com indentação
correta, começando na coluna 0 do fonte, e validados por `ast.parse()` — os três
passam. A extração via `pdftotext` foi conferida e preserva os 4 espaços de
indentação, ou seja, copiar do PDF agora entrega código executável.

**Regra permanente**: conteúdo dentro de `verbatim` começa na **coluna 0** do
`.tex`, nunca indentado junto com o LaTeX ao redor — o `verbatim` é literal, e a
indentação do fonte vira indentação do código impresso. Ao acrescentar ou editar
qualquer bloco de código, validar a sintaxe fora do LaTeX antes (para Python,
`ast.parse()` no conteúdo extraído do bloco). Acentos em comentários funcionam
normalmente em `verbatim` com `T1`+`inputenc` — não há motivo para escrevê-los
sem acento.

## Ponto de parada — fim da sessão de 31/07/2026

**Onde o trabalho parou:** em estado limpo e fechado, sem nada pela metade. O
`.tex` compila em 3 passagens sem erro, aviso, referência indefinida ou label
duplicado; o `.pdf` está em dia com o `.tex`; nenhuma edição ficou aberta e
nenhum experimento ficou pendurado no arquivo. Qualquer sessão futura pode
começar do zero pela lista de "Pendências conhecidas" no fim deste arquivo, sem
precisar desfazer ou terminar nada da sessão anterior.

**O que muda quando alguém retomar:**
- Tudo das três sessões (29, 30 e 31/07/2026) continua **sem commit** — ver o
  bloco de atenção em "Estado atual", logo abaixo, com o fatiamento sugerido em
  9 commits temáticos. Essa é a primeira decisão a tomar ao retomar.
- Os artefatos `compressores.lof` e `.lot` passaram a ser gerados (pelas listas
  de figuras/tabelas) e já entraram no `.gitignore` junto com `.aux/.log/.out/.toc`.
- Os dois relatórios de análise externa da raiz estão **encerrados** — o que era
  defeito verificável foi corrigido, o que foi recusado está registrado com o
  motivo. Não reabrir sem contexto novo.

**Resumo do que estas três sessões entregaram**, para quem só ler esta seção:
o livro saiu de 105 para 131 páginas; ganhou o parecer normativo do Manus
implementado (ISO 20816/8573/1217), a Parte II aprofundada em 6 capítulos, os
Capítulos 12 e 13 triplicados, todas as referências com ano/edição verificados
contra fonte real, Lista de Figuras e Lista de Tabelas, e quatro correções de
defeito que ninguém tinha visto: duas equações com erro de unidade (9.8 e 11.6),
as aspas retas engolidas pelo babel, a hifenização errada de termos em inglês e
acrônimos, e os três blocos de código Python que não eram executáveis.

## Terceiro relatório externo (dicas_kimi.md) implementado (01/08/2026)

O autor trouxe uma terceira análise externa, `dicas_kimi.md` (Kimi, compilação
de 31/07/2026, 133 páginas, na raiz do projeto — mesmo status de não
rastreado/não commitar sem pedido dos outros dois relatórios). Diferente do
Manus (achados normativos) e do Copilot (extração de texto), este é puramente
de diagramação/produção do PDF: overfull hboxes, colisão de célula em tabela,
warnings de bookmark do hyperref e metadados vazios. Todos os itens acionáveis
foram implementados nesta sessão, em dois commits:

- **`27997b6`**: metadados do PDF (`pdfsubject`/`pdfkeywords` no
  `hypersetup`), warning de `headheight` do fancyhdr (14,5pt → 15pt, com
  `\addtolength{\topmargin}{-0.5pt}`) e o overfull grave do título da
  subseção 5.5 — "Sub/Sobrecompressão" sem hífen impedia quebra de linha;
  virou "Sub- e Sobrecompressão". Também `\emergencystretch=1em` no
  preâmbulo, que sozinho já eliminou a maior parte dos overfulls menores do
  relatório.
- **`3417919`**: os itens que sobraram, todos maiores do que o relatório
  registrou — a varredura completa achou **5** tabelas "Matriz de falhas"
  com overfull grave (o relatório citava 1, de 37,4pt; a pior aqui chegou a
  56,7pt), não resolvidas por `\small` sozinho, convertidas para
  `\resizebox{\textwidth}{!}{...}` (mesmo padrão já usado em outras tabelas
  do documento). A colisão na Nomenclatura (célula
  `$C_{\min}, C_{\max}, C_r$` invadindo a coluna Significado) foi corrigida
  alargando a coluna Símbolo de 2,0cm para 2,8cm nas 8 tabelas de
  Nomenclatura (compensado encolhendo Significado). Os 4 títulos com
  matemática (`$V_i$`, `$\Pi$`, `$\dot{m}$`, `$KPI_{treat}$`) ganharam
  `\texorpdfstring{}{}`, zerando as 11 warnings de bookmark do hyperref.
  Achado bônus fora da lista original: o título do Capítulo 23 (PIML) tinha
  overfull de 6,9pt por estar forçado a uma linha só — corrigido com
  `\raggedright` no `\titleformat{\section}`, permitindo quebra em duas
  linhas quando necessário (sem afetar os demais títulos, todos curtos o
  bastante para continuar em uma linha).

**Deliberadamente não perseguido**: ~30 overfulls residuais de ~2pt (a
palavra "adimensional" sozinha em algumas linhas de Nomenclatura, não
hifenizável de forma útil) e a duplicata de destino `page.1` (mistura
numeração romana/arábica) — o próprio relatório já classificava ambos como
cosmeticamente insignificantes, e a inspeção visual confirmou.

**Armadilha de ferramental encontrada**: `compressores.log` é gerado em
ISO-8859 (Latin-1), não UTF-8. `grep` sem a flag `-a` falha silenciosamente
nesse arquivo neste ambiente (retorna vazio em vez de erro) — isso já
aconteceu antes e vai acontecer de novo se não for lembrado. **Sempre use
`grep -a` ao inspecionar `compressores.log`** (overfulls, warnings, nomes de
pacote); sem isso, buscas por "Overfull", "Warning" ou até "hyperref"
retornam zero resultados mesmo quando o conteúdo está lá, levando a
conclusões erradas de que não há problema.

Como nas sessões anteriores, ambos os commits foram isolados do restante do
trabalho pendente (~550 linhas de 29-31/07, ver abaixo): reconstruídos a
partir do conteúdo do commit anterior (`git show HEAD:compressores.tex`) com
apenas as edições desta sessão aplicadas por cima, compilados isoladamente
para gerar um `.pdf` consistente com esse `.tex` parcial, e só então
staged — a árvore de trabalho completa (com o conteúdo pendente) foi restaurada
depois de cada `git add`. Nenhum commit sem pedido explícito do autor, como
sempre.

## Terceiro erro de unidade encontrado: Equação 15.7 (02/08/2026)

Ao implementar o KPI $HI_{des}$ (Índice de Saúde do Dessecante) no
`aplicativo/` (ver `CONTEXTO_app.md`), ficou evidente que a Equação 15.7
tinha o mesmo tipo de erro de unidade das Equações 9.8/11.6 (ver "Dois
erros de unidade reais" acima): a razão $PDP_{target}/PDP_{real}$,
calculada diretamente em Celsius (convenção do documento, valores
negativos como $-40\,^{\circ}$C), **inverte o sentido do índice** — um
$PDP_{real}$ pior (mais alto/mais quente, secagem menos eficaz) produzia
$HI_{des}$ **maior**, o oposto do que o próprio texto ao lado da equação
já dizia que ela deveria fazer. Corrigido com a mesma técnica das duas
correções anteriores: conversão `+273,15` explícita na fórmula (agora em
Kelvin) e uma frase antes da equação explicando por que a conversão é
obrigatória, para não regredir.

**Nota de processo**: desta vez o erro não veio de um relatório externo —
foi encontrado organicamente ao portar a equação para código Python
(`hi_des()` em `aplicativo/compressor_sim/subsistemas.py`), onde a
inversão de sinal teria sido óbvia num teste (`test_hi_des_cai_com_degradacao`
verifica explicitamente que degradar o PDP real *reduz* o índice). Reforça
o padrão já observado: reimplementar uma equação do livro em código, com
testes, é uma forma eficaz de auditoria — vale considerar isso
deliberadamente para outras equações do documento, não só como
subproduto de construir o app.

## Sessão de 02/08/2026 — Verificação automática do PDF e reorganização de arquivos de apoio

Rotina de verificação automática do PDF compilado via `pdftotext -layout` + busca de sinais de erro comum: referências não-resolvidas ("??"), caracteres de substituição U+FFFD (�), TODO/FIXME não finalizados. Resultado: **nenhum sinal tóxico detectado**. Cruzamento de contagem entre labels do `.tex` e ocorrências no PDF extraído mostrou diferença esperada (192 labels vs. 206 ocorrências de "Equação" — esta última inclui menções em prosa). Três equações recentemente corrigidas (9.8, 11.6, 15.7) verificadas como presentes no PDF; 11.6 teve layout fragmentado na extração (provável compressão/quebra de coluna ao exportar para texto), recomenda-se inspeção visual da página no PDF físico.

Gerado arquivo `dicas_COPILOT.md` (relatório automático) com recomendações de inspeção visual prioritária: confirmar layout de (11.6), (9.8), (15.7); revisar tabelas de Nomenclatura e matrizes de falha (risco de truncamento em células). Nenhuma evidência de conteúdo cortado ou desaparecido no PDF compilado.

Arquivos de análise externa da raiz (`recomenda compressores.txt`, `Manus_parecer_final_compressores.md`, `dicas_kimi.md`, `referências extras para as fórmulas.md`) movidos para subdiretório `arquivos_apoio/` a pedido do autor — continuam **não rastreados pelo git**, mesmo status, apenas mudou o caminho físico. Estrutura do repositório permanece idêntica em termos de conteúdo versionado.

## Backlog Kimi implementado — 13 itens (02/08/2026)

`Backlog_kimi_compress.md` (sessão Kimi de 02/08/2026, ver a lista de
arquivos em `arquivos_apoio/` logo acima) propôs 13 lacunas de
equacionamento/acessórios (BK-01 a BK-13),
priorizadas alta/média/baixa, com o aviso explícito de "nada aqui foi
implementado — implementar um item por sessão". O autor pediu o backlog
completo de uma vez; os 13 itens foram implementados nesta sessão. Duas
decisões do autor resolveram os pontos que o backlog deixava em aberto:

- **BK-05 (MPV)**: o backlog suspeitava que a "Válvula de Pressão Mínima"
  do Cap. 3 fosse resquício de um rascunho oil-flooded, incompatível com a
  arquitetura oil-free do livro. Perguntado, o autor confirmou que **a
  máquina real não tem essa válvula** — item removido da lista de
  acessórios (mantidas retenção e blow-down).
- **Escopo**: o autor escolheu o backlog completo (não só prioridade alta).

**Estratégia usada para evitar cascata de renumeração** (o próprio backlog
alertava para isso em vários itens): toda equação nova foi inserida ao
**fim do capítulo** (ou subseção final), nunca no meio de uma sequência
existente — `\numberwithin{equation}{section}` numera pela posição física
no documento, não pelo texto do `\label`, então inserir no meio sempre
desloca os números seguintes. Com essa estratégia, **nenhuma equação
preexistente mudou de número** em nenhum dos 13 itens, incluindo BK-02 e
BK-07, para os quais o próprio backlog havia avisado risco de cascata caso
inseridos no meio do capítulo como sugerido literalmente no texto.

Resumo por item (capítulo, o que foi adicionado):

- **BK-01** (Cap. 11): FAD/ISO 1217 definido — nova eq. 11.12,
  $\dot V_{\text{free\_air}} = \dot m/\rho_{\text{ref}}$. Condições de
  referência ($P_{\text{ref}}=1\,\text{bar}$, $T_{\text{ref}}=20\,^\circ$C,
  0% UR) **verificadas contra a norma real** (preview oficial ISO 1217:2009
  + múltiplas fontes secundárias concordantes), não tiradas de memória.
  Nomenclatura atualizada ($\dot V_{\text{free\_air}}$ não constava).
- **BK-02** (Cap. 5): nova subseção 5.9 "Pressão Intermediária Ótima entre
  Estágios", eq. 5.14, $P_{\text{int}}^* = \sqrt{P_1 \cdot P_2}$, ligada à
  degradação do intercooler (eq. 10.4/10.5) já modelada no Cap. 10.
- **BK-03** (Cap. 4.4): correntes de eixo por EDM (descarga eletrostática
  em motor com VSD) — novo item na lista de mecanismos de falha, com
  indicador (craterização/*fluting*) e mitigação (rolamento isolado, anel
  de aterramento, filtro de modo comum). Referência Erdman/Kerkman/
  Schlegel/Skibinski (IEEE Trans. Industry Applications, 32(2), 250–259,
  1996, DOI 10.1109/28.491472) **verificada via busca** antes de citar.
- **BK-04** (Tabela 18.1 + Cap. 11): linha "Posição Axial" ($\delta_{ax}$,
  $\mu$m) adicionada ao ponto E; frase no Cap. 11 ligando eq. 11.5 ($F_a$)
  → sonda de proximidade → eq. 11.6 (vida do rolamento de escora). Símbolo
  novo checado contra a Nomenclatura para não colidir com $x$/$z$ do EKF.
- **BK-06** (Cap. 8): nova subseção 8.8 "Análise Torcional do Trem
  Completo", eq. 8.10, $\omega_{cr,t} = \sqrt{k_{t,\text{eq}}(1/I_1+1/I_2)}$
  — modo torcional do conjunto motor–acoplamento–gearbox–rotores,
  complementar (não substituto) à velocidade crítica lateral já existente.
- **BK-07** (Cap. 9): nova subseção 9.7, eq. 9.11, relação
  $\eta_p \leftrightarrow \eta_{is}$ — $\eta_p$ é a grandeza que se compara
  contra a garantia de fábrica; $\eta_{is}$ varia com $\Pi$ mesmo sem
  degradação.
- **BK-08** (Cap. 7): nova subseção "Análise Físico-Química do Óleo" —
  TAN, água (Karl Fischer) e contagem de partículas (ISO 4406) como canal
  laboratorial *offline*, complementar ao $SOH_{\text{oil}}$ online (eq.
  7.7). Três normas **verificadas antes de citar**: ISO 4406:2021, ASTM
  D664-18e2, ASTM D6304-20.
- **BK-09** (Caps. 2, 5, 16): três inserções — invólucro como barreira
  acústica (ISO 2151:2004, **verificada**; a própria ISO 1217 já citada
  no Cap. 1 exclui ruído do escopo e remete a ela — achado ao ler a norma
  primária, não estava no backlog); silenciador de admissão somando perda
  de carga à eq. 5.4; amortecedor de pulsação como mitigação de projeto no
  Cap. 16.2 (API 618 já citada, sem referência nova).
- **BK-10** (Cap. 9): nova subseção 9.8, eqs. 9.12/9.13, $u_{\text{tip}}$ e
  $M_{\text{tip}}$ — liga a rotação à velocidade periférica e ao regime de
  escoamento de fuga pela folga (compressível/sônico).
- **BK-11** (Cap. 12): nova subseção, eq. 12.8 — soft-sensor de
  $\dot m_w$ (vazão de água de resfriamento) por balanço de energia,
  quando não há medidor de vazão de água dedicado.
- **BK-12** (Cap. 4.4): aquecedores anticondensação (*space heaters*) do
  motor, ligados à Equação de Arrhenius (eq. 4.7) e ao cenário de
  *standby* de frota do Cap. 16.
- **BK-13** (Cap. 3.6): nota de escopo junto ao item PSV — dimensionamento
  do orifício de alívio é projeto (ASME VIII), não algo que o Gêmeo
  Digital calcula/monitora.

**5 `\bibitem` novos** usados de fato no Backlog, todos verificados contra
fonte real antes de inserir (regra permanente de veracidade): `erdman`,
`iso4406`, `astmd664`, `astmd6304`, `iso2151`. (`isa51` também foi
adicionado nesta sessão, mas é o item órfão explicado acima — não conte
como parte do Backlog.)

**Verificação final** (fechando também as recomendações do
`dicas_COPILOT.md`, que eram sobretudo de conferência, não de conteúdo):
compilação de 3 passagens limpa; 199 labels `eq:s*-*` = 199 ocorrências
"(N.N)" no PDF extraído, sem "??", sem caracteres de substituição, sem
referência indefinida ou label duplicado no log; overfull hboxes foram de
31 para 33 (mesma magnitude mínima de 2,01pt já documentada como
insignificante, só mais duas linhas de Nomenclatura "adimensional");
overfull vbox permanece em 0. Conferidas visualmente 4 páginas (subseção
5.9, Tabela 18.1 com a nova linha, subseções 9.7 e 9.8) — todas renderizam
limpas, sem corte ou sobreposição.

**Nada foi commitado** — o próprio `Backlog_kimi_compress.md` pede
explicitamente para não commitar sem pedido do autor, e a regra já é
permanente neste projeto de qualquer forma. `compressores.tex` está
~104 linhas maior (119 linhas de diff), `compressores.pdf` recompilado
para 141 páginas (era 135), ambos modificados na árvore de trabalho, não
staged, aguardando revisão do autor.

## RESOLVIDO em 16/08/2026 — ver "Capítulo 28 implementado" mais abaixo. Entrada original preservada como histórico do planejamento.

## PENDENTE — Metodologia de calibração/anomalia na Parte III (pedido em 15/08/2026, não iniciado)

**Sessão parou por limite de uso antes de escrever qualquer coisa no
`.tex`** — só houve levantamento via `grep` (nenhuma edição feita). Repo
limpo, commit `52fb4f9`. Pedido literal do autor: "introduza no capítulo
III uma metodologia de estimativa de parâmetros para uso quando o
equipamento está em bom funcionamento e registrar parâmetros
desconhecidos ou falta de algum equipamento em casos reais, depois
utilizar gêmeos digitais para detecção de anomalias com base nos
mecanismos de falha que podem ser simulados via codificação do
equipamento."

**Plano já fechado, pronto para executar na próxima sessão:**

1. **Separar a Parte III em dois capítulos** — novo **Capítulo 28**
  (metodologia) inserido *antes* do capítulo de estudo de caso já
  existente, que vira **Capítulo 29**. Renumeração conferida como
  trivial: `eq:s28-1`→`eq:s29-1`, `tab:28-1`→`tab:29-1`,
  `tab:28-2`→`tab:29-2` (únicas ocorrências, todas dentro do próprio
  capítulo — sem referência externa a atualizar, já checado com
  `grep -n "eq:s28-1\b"` e `grep -n "Capítulo 28\|tab:28-"` contra o
  `.tex` inteiro). Também ajustar a linha de `RUL` na Nomenclatura
  ("Cap. 19, 28" → "Cap. 19, 29") e o comentário
  `% --- Fim do Capítulo 28 ---` → 29.

2. **Conteúdo do novo Capítulo 28**, três subseções cobrindo os três
  pedidos do autor, nesta ordem:
  - **28.1 — Estimação Conjunta de Estado e Parâmetro (EKF com estado
    aumentado)**: metodologia formal de calibração de parâmetros
    ASSUMIDO (K de folga da Eq. 9.3, ζ de filtros, η_mec, etc.) durante
    uma **janela de operação conhecidamente saudável** (comissionamento
    ou logo após manutenção confirmada) — técnica padrão de
    "*joint/dual state-parameter estimation*", citável via `\cite{simon}`
    (já na bibliografia, Simon cobre isso). Ideia central: aumentar o
    vetor de estado do EKF (Eq. 21.2) com os parâmetros estáticos θ,
    tratá-los como passeio aleatório de ruído de processo ≈0 durante a
    janela de calibração (convergência agressiva), depois "congelar" ou
    dar Q maior para acompanhar deriva lenta — exatamente o que já foi
    implementado de fato no app (`aplicativo/compressor_sim/ekf.py`,
    filtro parte de uma crença "como novo" e converge) — esta subseção
    deve **citar essa implementação como validação prática**.
  - **28.2 — Protocolo de Registro de Parâmetros Desconhecidos e Lacunas
    de Instrumentação**: formaliza como uma tabela/matriz de decisão a
    convenção "ASSUMIDO" já usada em todo o `aplicativo/` e a ideia de
    "lacunas de observabilidade" já presente no Cap. 18 (Tabela 18.1).
    Quatro categorias por parâmetro/medição exigida pelo modelo: (i)
    Medido (sensor de campo existe, está na Tabela 18.1); (ii) Inferível
    via *soft-sensor* (relação física + outro sensor, ex.: Eq. 12.8); (iii)
    Calibrável só na janela saudável (produto da subseção 28.1); (iv)
    Desconhecido/ASSUMIDO (sem sensor nem relação inferível — valor de
    literatura, marcado como tal, com recomendação explícita de análise
    de sensibilidade antes de qualquer decisão crítica baseada nele). Não
    força equação nova — pode ficar só como tabela/prosa, mesmo padrão já
    aceito em subseções conceituais do livro (ex.: "Limitações e
    Cautelas" do Cap. 23).
  - **28.3 — Catálogo de Mecanismos de Falha Simuláveis para Detecção via
    Gêmeo Digital**: tabela grande — Mecanismo de Falha | Capítulo de
    Origem | Variável/Estado Associado | Codificável (sim/como) |
    Algoritmo Detector Primário (EKF/VAE/PIML) — cobrindo os mecanismos
    de falha **já catalogados** no livro (não inventar novos). Levantamento
    já começado via `grep -n "Mecanismo de Falha"` e
    `grep -n "Matriz de Falhas\|label{tab:[0-9]"` — resultado parcial
    obtido, candidatos confirmados por capítulo: Cap. 2 (falha do
    exaustor do hood), Cap. 6 (`tab:6-1`, transmissão), Cap. 7
    (`tab:7-1`, lubrificação/óleo — degradação térmica, perda de
    viscosidade, colmatagem de filtro), Cap. 8 (`tab:8-1`, "Matriz de
    Falhas de Transmissão" — pitting, fadiga, desalinhamento), Cap. 9
    (`tab:9-1`, "Matriz de Falhas Integrada do Estágio LP" — desgaste de
    folga, o mesmo δ já usado no Cap. 29/estudo de caso), Cap. 10
    (`tab:10-1`, "Matriz de Falhas Integrada do Sistema Intermediário" —
    *offloading*, *fouling*), Cap. 11 (`tab:11-1`), Cap. 12 (`tab:12-1`),
    Cap. 13 (`tab:13-1`), Cap. 14 (`tab:14-1`), Cap. 15 (`tab:15-1`),
    Cap. 16 (`tab:16-1`), Cap. 17 (`tab:17-1`). **Ainda faltava conferir
    o conteúdo exato de cada uma dessas tabelas** (só os `\label`s foram
    levantados, não o conteúdo) antes de montar a tabela-catálogo —
    próximo passo concreto ao retomar. O Cap. 4 (motor) tem mecanismos de
    falha fora do padrão "\textbf{Mecanismo de Falha:}" (é uma
    `\begin{enumerate}` com itens tipo "Quebra de Barras do Rotor",
    "Desbalanço de Tensão/Corrente", "EDM") — não esquecer de incluir,
    exige busca textual diferente (já identificado, não está no grep
    acima).

3. **Diretriz Técnica Final do novo Capítulo 28**: amarrar as três
  subseções — calibração (28.1) alimenta o protocolo de lacunas (28.2)
  que por sua vez condiciona a confiabilidade do catálogo de detecção
  (28.3); e apontar para o Capítulo 29 (estudo de caso) como a
  demonstração concreta de 28.1-28.3 em ação.

4. **Depois de escrever**: recompilar 3 passagens, rodar a mesma
  varredura de auto-referência de equação já usada nesta sessão (regra
  permanente da seção de Convenções), conferir overfull/páginas/labels
  como sempre, atualizar `CONTEXTO.md` com uma entrada nova (não reescrever
  esta, só marcar como concluída ou substituí-la).

## Parte III — Estudo de Caso Integrado, Capítulo 28 (15/08/2026)

O autor pediu "a 3ª parte, o programa combinado de gêmeos digitais com
aprendizado de máquina já modelado". Duas rodadas de esclarecimento antes
de escrever (decisão de escopo grande demais para adivinhar):

1. **Livro ou app?** Livro (`compressores.tex`), não código no
   `aplicativo/`.
2. **O que exatamente falta, já que Cap. 18 (unificação da física) e
   Cap. 20 (EKF+VAE+PIML+MPC/PSO amarrados num workflow de 4 etapas)
   já existiam?** Confirmado: um **estudo de caso numérico de ponta a
   ponta** — pendência já registrada na seção "Pendências conhecidas"
   deste arquivo desde 30/07/2026 como "a maior adição possível em
   esforço, nunca pedida" — agora pedida explicitamente.

**Estrutura**: nova **Parte III** (divisor de página manual, mesmo padrão
de Parte I/II — `\clearpage`, `\thispagestyle{empty}`,
`\addcontentsline{toc}{part}{...}`, bloco centralizado), com um único
**Capítulo 28** — "Estudo de Caso Integrado: Diagnóstico Precoce de
Desgaste de Folgas via EKF, VAE, PIML e MPC/PSO" — inserido entre o fim
do Capítulo 27 e a bibliografia.

**Cenário escolhido** (advertência explícita no capítulo: todos os
números são ilustrativos, não medições reais): desgaste gradual da folga
$\delta$ do estágio LP ao longo de 6 semanas — deliberadamente uma falha
que desloca $T_{d,lp}$, $I$ e $v_{\text{rms}}$ cada uma por uma quantidade
pequena demais para cruzar qualquer limiar H/HH isolado da Tabela 18.2,
mas cuja correlação conjunta é exatamente o que a arquitetura combinada
existe para capturar. O capítulo percorre a cadeia completa com números
concretos passando de um algoritmo para o próximo:

- **EKF** (Eqs. 21.2/21.4/21.7): $\hat\delta/L$ converge de 0,0020 para
  ≈0,0091; NIS em torno de 5,1 confirma o filtro calibrado.
- **VAE** (Eqs. 20.4/22.6): $E_{rec}$ sobe de 1,2 para 4,8, cruzando
  $\tau_{limiar}=4{,}0$ na 5ª semana — mesmo sem nenhuma das 28 variáveis
  isoladamente fora de faixa.
- **PIML** (Eq. 23.2): o substituto treinado, consultado com $\hat\delta$
  do EKF, reproduz $T_{d,lp}$/$I$ dentro de tolerância — testado contra
  duas hipóteses alternativas (incrustação de intercooler, viés de
  $T_{amb}$) que não reproduzem o mesmo padrão nas 5 medições, isolando
  a causa-raiz.
- **Prognóstico** (Eq. 19.10, forma de Processo Gaussiano **reaproveitada**
  do dano de engrenagem $D(t)$ para a série $\hat\delta/L(t)$ do EKF — a
  mesma suavidade que motivou o *kernel* original se aplica aqui):
  $RUL_\delta \approx 9$ semanas, IC 95% [6, 14] — nova Equação~28.1
  (única equação genuinamente nova do capítulo; todo o resto reaproveita
  `\eqref{}` de equações já existentes com números concretos substituídos).
- **MPC/PSO** (Eqs. 24.1/24.2/24.3/24.4): MPC decide entre manter operação
  + antecipar manutenção ou reduzir levemente o setpoint de pressão
  (custo de SPC vs. vida estendida); PSO explicitamente **não** participa
  da decisão em tempo real (papel já estabelecido no Cap. 24 — latência
  incompatível com proteção mecânica), só re-sintonizando offline depois
  da manutenção.

Duas tabelas novas: Tabela 28.1 (linha de base saudável vs. limiar de
alarme) e Tabela 28.2 (síntese do fluxo de dados — cada linha mostra
entrada/saída/consumidor seguinte de cada um dos 7 elos da cadeia).

**Erros cometidos e corrigidos antes de fechar**:
- Tabela 28.1 sem `\resizebox` gerou um overfull de 30,9pt (bem acima do
  baseline de ~2pt já tolerado) — corrigido envolvendo em
  `\resizebox{\textwidth}{!}{...}`, mesmo padrão já usado em outras
  tabelas largas do documento.
- 2 ocorrências de aspas retas (`"regra dos 7%/bar"`, `"9 semanas"`) —
  mesmo bug do babel já documentado nesta sessão para o Cap. 12 (engole o
  espaço seguinte) — corrigidas para `` `` `` / `''`.
- 6 referências a equações dentro de células de tabela (Tabela 28.2)
  escritas como `Eq.~21.4` hardcoded em vez de `Eq.~\eqref{eq:s21-4}` —
  pegas e corrigidas antes de compilar a versão final (mesma classe de
  erro da correção em massa registrada na seção anterior).
- `RUL` (Eq. 19.9) nunca tinha entrada na Nomenclatura, apesar de já
  usado desde 29/07/2026 — lacuna pré-existente, não introduzida nesta
  sessão, mas corrigida de passagem ao adicionar `RUL_\delta` (a entrada
  cobre a base e a variante subscrita, já que este documento não lista
  subscritos de um símbolo já definido individualmente).

**Verificação**: compilação limpa em 3 passagens, 0 refs indefinidas, 0
labels duplicados, `209` labels `eq:s*-*` (era 208, +1 — Eq. 28.1), `0`
violações na varredura de auto-referência (a regra reforçada mais acima
neste arquivo se aplicou à Eq. 28.1 desde a escrita), overfull hboxes em
`35` (34 baseline + 1 novo de 1,1pt, abaixo do próprio limiar de
insignificância já estabelecido), `0` marcadores `??`, 146→151 páginas.
Renderização visual conferida em 4 páginas (divisor da Parte III, abertura
do Cap. 28, Tabela 28.1, Tabela 28.2) — todas limpas.

**Nada foi commitado ainda** — aguardando revisão do autor.

## Verificação visual do PDF compilado — achado e corrigido bug de cabeçalho (15/08/2026)

O autor pediu para verificar se o PDF compilado estava correto depois da
correção em massa acima. Verificação em várias camadas, não só o log de
compilação:

- Recompilação limpa (3 passagens), `0` refs indefinidas/labels duplicados,
  `34` overfull hboxes (mesmo baseline, sem regressão), `0` marcadores `??`
  no texto extraído, `0` caracteres de substituição/bytes de controle
  (ligaduras), `208` labels = equações intactas.
- Renderização visual (`pdftoppm`) de páginas-chave: capa, Nomenclatura
  (tabelas editadas nesta sessão), Sumário, e as 4 páginas com as
  subseções novas (Cap. 2, 4, 5, 9) — todas limpas, sem sobreposição,
  colunas de tabela alinhadas, `\dag` renderizando corretamente.

**Achado real**: o cabeçalho corrente (`fancyhdr`) do Capítulo 9
("Termodinâmica do Estágio LP, Dinâmica de Folgas e Resposta Vibracional",
70 caracteres — o título mais longo do livro) colide com o número da
página no canto direito, sem nenhum espaço entre os dois — confirmado
visualmente em alta resolução. **Pré-existente**: comparei contra o PDF do
commit `2876885` (estado antes desta sessão) e o mesmo colapso já
aparecia lá — não foi introduzido pelo trabalho de hoje. Os outros títulos
longos (Cap. 7, 68 caract.; Cap. 8, 67; Cap. 10, 66) ficam apertados mas
não colidem — só o Capítulo 9 realmente ultrapassa.

**Corrigido**: `\markboth{Termodinâmica do Estágio LP, Dinâmica de
Folgas}{}` logo após o `\section{}` do Capítulo 9, sobrescrevendo só o
cabeçalho corrente (via `\sectionmark`/`\leftmark`) com uma forma
encurtada (47 caracteres) — o título completo no sumário, nos bookmarks e
na página de abertura do próprio capítulo **não muda**, só o texto que
aparece no topo das páginas seguintes. Verificado antes/depois com
renderização em alta resolução; título completo confirmado intacto no
Sumário e na primeira página do capítulo.

**Técnica registrada para reuso**: se um título de capítulo futuro (deste
volume ou de um volume novo da coleção) tiver mais de ~65-68 caracteres,
o cabeçalho corrente provavelmente vai colidir com o número de página —
`\markboth{<forma curta>}{}` logo após o `\section{}` é o jeito de
corrigir sem tocar no título de verdade. `fancyhdr` não gera nenhum aviso
de compilação para esse tipo de colisão (não é um `Overfull \hbox` —
são duas caixas de header independentes que simplesmente se sobrepõem
espacialmente), por isso passou despercebido em todas as revisões de
diagramação anteriores (26/07, 01/08) — só apareceu numa inspeção visual
direta do cabeçalho em alta resolução. Vale conferir visualmente o
cabeçalho de qualquer capítulo com título longo ao adicionar um volume
novo à coleção.

## Correção em massa: número da equação citado antes de aparecer (15/08/2026)

O autor notou que a convenção "explicação antes da equação" (ver seção de
Convenções acima) não estava, na prática, exigindo o mesmo que já era
exigido de figuras e tabelas — citar o **número** via `\eqref{}` no texto
antes do `\begin{equation}`, não só explicar o conceito. Pedido: registrar
a observação no `CONTEXTO.md` (feito — ver a entrada correspondente na
seção de Convenções, acima) e ajustar o texto inteiro.

**Varredura programática** (contar, para cada `\label{eq:sC-N}`, se
`\eqref{eq:sC-N}` aparece nos ~800 caracteres imediatamente anteriores):
achou **110 das 208 equações do livro (53%) sem essa citação prévia**. O
padrão mais comum era um item de `itemize` com `\textbf{Nome do
Conceito:}` seguido de frase explicativa que descrevia o que a equação
calcula, mas nunca citava "Equação~(X.Y)" antes dela — só depois, quando
citada de novo por outro capítulo, ou nunca.

**Correção**: as 3 primeiras (Capítulo 2, achadas e corrigidas na mesma
sessão do achado anterior) foram feitas manualmente como referência de
estilo; as 107 restantes (Capítulos 4 a 27) foram delegadas a um
subagente (fork), com instrução explícita de tecer a citação na própria
frase de abertura já existente (não adicionar uma sentença nova redundante
quando evitável) e variar o conector — "pela Equação~\eqref{}", "conforme
a Equação~\eqref{}", "dada pela Equação~\eqref{}", "A Equação~\eqref{}
calcula/define/expressa...", etc. — para não ler como template repetido.

**Verificação independente feita pelo Claude após o retorno do subagente**
(não confiar só no relato dele — recompilação e nova varredura do zero):
- 3 passagens de `pdflatex` limpas, `0` referências indefinidas/labels
  duplicados.
- Nova varredura: **0 violações restantes** (era 110).
- `208` labels `eq:s*-*` — nenhuma equação foi adicionada, removida ou
  renumerada; só a prosa ao redor mudou.
- Overfull hboxes: `34`, idêntico ao baseline antes desta correção — sem
  regressão de diagramação.
- `0` marcadores `??` no PDF extraído.
- Amostragem manual de 7 equações espalhadas por capítulos diferentes
  (4, 6, 9, 13, 17, 20, 26) conferida linha a linha — todas naturais,
  nenhuma com número hardcoded.

**Observação cosmética menor, não perseguida**: uma checagem de repetição
de conector dentro do mesmo capítulo achou ~18 casos de frases vizinhas
usando o mesmo conector (ex.: "pela Equação~\eqref{}" duas vezes em
parágrafos próximos) — estilisticamente repetitivo em alguns pontos, mas
não viola a regra em si (o número está lá, citado antes). Mesma categoria
dos ~30 overfulls residuais de 2pt já registrados como cosmeticamente
insignificantes — não é dívida técnica, é só um refinamento de prosa
opcional se uma sessão futura quiser revisitar.

**Regra permanente reforçada**: qualquer equação nova, em qualquer
capítulo futuro (incluindo volumes futuros da coleção), precisa desse
`\eqref{}` de si mesma na frase que a antecede, mesmo quando já
introduzida por um título em negrito de item de lista.

## Auditoria de perdas termodinâmicas/fluidas e acoplamento com o Hood (15/08/2026)

Continuação da mesma sessão: o autor pediu uma varredura de todo o livro
para verificar se perdas termodinâmicas e de fluidos estavam cobertas em
cada capítulo (levantamento por palavra-chave + inspeção das equações
cujo parágrafo introdutório menciona perda/atrito/fuga/ΔP/irreversibilidade/
entropia/exergia — metodologia registrada para reuso futuro: script Python
com regex sobre `\begin{equation}\label{...}` e os 500 caracteres
anteriores). Cobertura confirmada como ampla em cinco categorias
(termodinâmica pura, mecânica/atrito, perda de carga ΔP, fugas internas,
transferência de calor) em praticamente todo componente físico da Parte I,
consolidada via exergia/entropia na Parte II — capítulos sem essas
equações (8, 19, 21, 24, 27) são metodológicos/algorítmicos por natureza,
não uma lacuna.

A varredura achou três lacunas reais, e o autor pediu para fechar as três
na mesma sessão:

**1. Motor elétrico tratado como caixa-preta (Cap. 4).** Diferente do VSD
(Eq. 4.3, decomposto em switching+conduction) e da gearbox (Eq. 5.2,
mesh+windage+bearing), o motor entrava na Eq. 4.9 só como $\eta_{mot}(s,T)$
sem decomposição. Fechado com 3 equações novas ao fim do capítulo (nova
subseção "Fechamento das Perdas do Motor"), método de perdas segregadas da
IEC 60034-2-1 (já citada no capítulo para a metodologia de ensaio, nunca
usada para fechar uma fórmula): Eq. 4.10 ($P_{ag}=\tau_{em}\cdot\omega_s$,
ligando Eqs. 4.4/4.5 já existentes), Eq. 4.11 ($P_{perdas,mot}=s\cdot
P_{ag}+P_{fixas}$ — só a perda Joule do rotor varia com a carga via $s$; as
demais quatro categorias do método segregado ficam agregadas numa constante
de ensaio $P_{fixas}$) e Eq. 4.12 (fecha $\eta_{mot}(s,T)$; a dependência de
$T$ entra pela própria Eq. 4.5, via $R_r(T)$, não como termo à parte).
Símbolos novos $P_{ag}$, $P_{fixas}$ na Nomenclatura (Cap. 4).

**2. Perda de carga na tubulação interestágios não modelada (Cap. 5).** LP→
intercooler, intercooler→HP, HP→aftercooler: só a ressonância acústica
(Cap. 16, Helmholtz) e as perdas em filtro/válvula eram cobertas — o
atrito distribuído na própria linha, nunca. Fechado com a Eq. 5.15
(Darcy-Weisbach, $\Delta P_{\text{linha}}=f_D\cdot(L_{\text{linha}}/
D_{\text{linha}})\cdot\rho v^2/2$ — mesma pressão dinâmica $\rho v^2/2$ já
usada na Eq. 5.4 do filtro, agora para atrito distribuído em vez de perda
localizada), ao fim do Capítulo 5, nova subseção. Nota registrada: hoje
nem o livro nem o app tratam $P_{\text{int}}$ como afetado por essa perda —
é uma pequena correção normalmente, mas cresce com corrosão/incrustação
interna da tubulação ao longo da vida da instalação. Símbolos novos $f_D$
(\dag, desambiguado contra $f$=frequência elétrica do Cap. 4), $L_{\text{linha}}$,
$D_{\text{linha}}$ na Nomenclatura (Cap. 5).

**3. Acoplamento Hood↔Carcaça — o achado mais importante.** O autor lembrou
que muitos compressores ficam enclausurados em invólucros acústicos (Hood)
por restrição de ruído offshore, às vezes com o trem inteiro — motor,
gearbox, os dois estágios — dentro do mesmo gabinete até a saída do 2º
estágio. Isso expôs uma inconsistência real no fechamento da Eq. 9.6 feito
mais cedo nesta mesma sessão: as Eqs. 9.15-9.17 usavam $T_{amb}$ como
referência de convecção da carcaça, correto só para instalação a céu
aberto — quando o elemento compressor está dentro do mesmo Hood que o
motor/VSD/gearbox (Capítulo 2, que já tinha Eq. 2.1/2.2 para o balanço
térmico do invólucro desde antes desta sessão), o ar que banha a carcaça é
o ar interno do invólucro, já aquecido pelas outras fontes — não o
ambiente externo verdadeiro. $T_c$ calculado com $T_{amb}$ nesse cenário
estava sistematicamente subestimado.

Fechado com uma nova subseção ao fim do Capítulo 2 ("Fechamento Térmico do
Invólucro"), pedido explícito de não esquecer a entrada de ar renovado e a
saída de ar quente do exaustor (as duas pontas de $\dot m_{\text{vent}}$ já
presentes na Eq. 2.2): Eq. 2.4 fecha $T_{\text{hood}} = T_{amb} +
\dot Q_{\text{gerado}}/(\dot m_{\text{vent}}\cdot c_p)$, sob a hipótese de
mistura completa ($T_{\text{hood}}\equiv T_{\text{exaustão}}$, a própria
leitura de saída do exaustor). Também resolveu uma aparente circularidade
entre os dois capítulos: $\dot Q_{\text{casco}}$ (Eq. 2.1) é a mesma
grandeza que a soma $\dot Q_{\text{ext}}+\dot Q_{\text{arref}}$ do
Cap. 9, e em regime permanente iguala $\dot Q_{\text{int}}$ (Eq. 9.14) —
ou seja, calculável direto do ponto de operação, sem precisar de $T_c$
primeiro. Ordem de cálculo correta, agora documentada: (1) $\dot Q_{\text{int}}$
(Eq. 9.14) → (2) $\dot Q_{\text{gerado}}$ (Eq. 2.1) e $T_{\text{hood}}$
(Eq. 2.4) → (3) $T_c$ (Eq. 9.16, agora referenciada a $T_{\text{hood}}$, não
$T_{amb}$, para instalações com invólucro). Cap. 9 ganhou um parágrafo de
ressalva explícito logo após a Eq. 9.17, cross-referenciando a Eq. 2.4, sem
reescrever nenhuma das três equações (a forma matemática não muda, só a
leitura do termo de referência).

**Achado colateral corrigido de passagem**: ao mexer no Capítulo 2, uma
varredura pelo PDF compilado revelou que os labels das 3 equações
pré-existentes do capítulo (`eq:s2-1`, `eq:s2-2`, `eq:s2-3`) **nunca
correspondiam à ordem física/numeração exibida** — `eq:s2-2` (Q_gerado)
renderizava como (2.1), `eq:s2-3` (Q_hood) como (2.2), `eq:s2-1` (V_res)
como (2.3), uma inconsistência pré-existente que nenhuma sessão anterior
tinha pegado (nenhuma auditoria de equações tinha revisitado o Cap. 2
especificamente). As referências cruzadas em si nunca estiveram quebradas
(o `\eqref{}` sempre resolve pelo contador real, não pelo texto do label),
mas violava a convenção "sufixo do label = número exibido" e teria
confundido qualquer edição futura por busca de texto. Corrigido por
relabeling cíclico antes de adicionar a Eq. 2.4, com todas as 4
ocorrências de `\eqref{}` a esses labels no documento inteiro atualizadas
juntas. **Lição para auditorias futuras de referenciamento de equações**:
a varredura de 26-30/07/2026 nunca cobriu o Capítulo 2 — vale conferir os
capítulos ainda não auditados dessa forma se uma sessão futura for atrás
de mais inconsistências desse tipo.

**Verificação de não regressão**: compilação limpa em 3 passagens
(143→146 páginas), 208 labels `eq:s*-*` (era 203) = 519 ocorrências
"(N.N)" no PDF extraído (subiu de 507 por causa dos hardcodes convertidos
para `\eqref{}`, ver abaixo), 0 "??", 0 referência indefinida, 0 label
duplicado, numeração dos Capítulos 6 e 10 em diante intacta. Overfull
hboxes foram de 33 para 34 (mesma magnitude mínima de 2,01pt já
documentada como insignificante — uma linha "adimensional" a mais na
Nomenclatura).

**Erro cometido e corrigido durante esta própria edição**: ao escrever a
nova subseção do Capítulo 2, usei `Equação~9.14`/`9.15--9.17`/`9.6`/`5.2`
como texto solto em vez de `\eqref{}` em 8 ocorrências — violação direta
da própria convenção "sempre referencie por `\eqref{}`, nunca hardcode o
número" (`CONTEXTO.md`, seção de Convenções). Pego numa varredura
`grep -noE "Equaç(ão|ões)~?[0-9]+\.[0-9]+"` logo em seguida, antes de
compilar a versão final — todas as 8 ocorrências corrigidas para
`\eqref{}`. **Vale repetir essa varredura sempre que um parágrafo novo
mencionar uma equação de outro capítulo** — é justamente nas referências
cruzadas *entre* capítulos (não dentro do mesmo capítulo, onde o hábito de
usar `\eqref{}` parece mais automático) que o hardcode escapou.

Símbolos novos verificados contra a Nomenclatura antes de inserir (regra
permanente): $P_{ag}$, $P_{\text{fixas}}$ (Cap. 4), $f_D$\dag, $L_{\text{linha}}$,
$D_{\text{linha}}$ (Cap. 5) — nenhuma colisão nova; $T_{\text{hood}}$ e
$\dot Q_{\text{casco}}$ não precisaram de entrada própria (subscritos de
$T$ e $\dot Q$, já genéricos). A coluna Capítulos de $\dot Q$ na
Nomenclatura foi estendida para incluir o Cap. 2.

**Atualização, mesma sessão**: o autor pediu para replicar os três achados
também no `aplicativo/`, incluindo um subsistema de motor elétrico novo
(o app não tinha nenhuma representação do Cap. 4 até então) — ver
`CONTEXTO_app.md`, "Motor, invólucro/Hood e tubulação interestágios".
Commitado em `ad97a78` (app) e `f47303b` (livro).

## Fechamento do balanço térmico da carcaça — Eq. 9.6 (15/08/2026)

Continuação direta da verificação feita no `aplicativo/` (ver `CONTEXTO_app.md`,
"Balanço térmico da carcaça do estágio LP"): lá ficou explícito que a Eq. 9.6 do
livro descreve $M_c c_c\,dT_c/dt = \dot Q_{\text{int}} - \dot Q_{\text{ext}} -
\dot Q_{\text{arref}}$ mas nenhum dos três termos do lado direito tinha forma
fechada no texto — mesma classe de lacuna já identificada e corrigida para
$P_{\text{sat}}(T)$ antes da Eq. 10.7. Fechada a pedido do autor, com 4 equações
novas ao **fim do Capítulo 9** (nova subseção "Fechamento do Balanço Térmico da
Carcaça", após a subseção do número de Mach, antes da Diretriz Técnica Final —
mesma estratégia de posicionamento de sempre para não deslocar nenhuma equação
existente):

- **Eq. 9.14** — $\dot Q_{\text{int}} = \dot W_{\text{LP}}\cdot(1-\eta_{\text{mec}})$:
  a mesma perda mecânica já embutida em $\eta_{\text{mec}}$ na Eq. 5.5, tratada
  como a parcela de calor que fica na máquina em vez de virar trabalho de
  compressão.
- **Eq. 9.15** — $\dot Q_{\text{ext}}$ e $\dot Q_{\text{arref}}$ como lei de
  Newton do resfriamento, lineares em $(T_c-T_{amb})$, com condutâncias
  agregadas distintas: $G_{\text{ext}}$ (convecção natural da carcaça) e
  $G_{\text{arref}}$ (arrefecimento ativo/ventilação forçada do invólucro,
  já descrito no Cap. 2).
- **Eq. 9.16** — $T_c$ em regime permanente ($dT_c/dt=0$), substituindo 9.14/9.15
  na própria Eq. 9.6.
- **Eq. 9.17** — $\tau_c = M_c c_c/(G_{\text{ext}}+G_{\text{arref}})$, constante
  de tempo do sistema de 1ª ordem linearizado; o texto registra explicitamente
  que $\tau_c$ (minutos a dezenas de minutos) é muito maior que a dinâmica de
  pressão da rede do Cap. 13 — um alarme de superaquecimento de carcaça não deve
  usar a mesma constante de tempo da resposta do VSD.

As quatro equações são exatamente o mesmo modelo já implementado no app
(`nucleo.q_int_carcaca`/`temperatura_carcaca_regime`/`constante_tempo_carcaca`) —
o app foi implementado primeiro, o livro fechado depois, para manter os dois
sincronizados desde o início em vez de o código divergir silenciosamente do
texto (como quase aconteceu com a Eq. 15.7 antes da correção de 02/08/2026).

**Símbolos novos verificados contra a Nomenclatura antes de inserir** (regra
permanente da seção "Convenções"): $M_c$, $c_c$ (já apareciam soltos na prosa
da Eq. 9.6 desde antes, mas nunca tinham entrado na tabela — corrigido agora),
$G_{\text{ext}}$, $G_{\text{arref}}$ (marcados \dag — nova nota na lista de
Desambiguação explicando a coexistência com $G_k$, Jacobiana do EKF no Cap. 20,
sem colisão real porque nenhum dos dois usa $G$ sem subscrito) e $\tau_c$
(entra na mesma família já existente de $\tau_{th}$/$\tau_{bd}$, nota de
desambiguação estendida). $T_c$ não precisou de entrada nova — é só um
subscrito do $T$ genérico já listado. A linha de $\dot Q$ na Nomenclatura teve
a coluna Capítulos estendida de "Trocadores" para "Trocadores, Cap. 9".

**Verificação de não regressão**: compilação limpa em 3 passagens (141→143
páginas), 203 labels `eq:s*-*` (era 199) = 203 ocorrências "(N.N)" no PDF
extraído, 0 "??", 0 referência indefinida, 0 label duplicado — a numeração do
Capítulo 10 em diante permanece intacta (conferido: primeira equação do
Cap. 10 continua "(10.1)"). Overfull hboxes seguem em 33, mesma magnitude
mínima de 2,01pt já documentada como insignificante — nenhuma tabela de
Nomenclatura ficou mais larga o suficiente para regredir.

**Commitado em 15/08/2026**, em dois commits — `3b9e376` (implementação no
app, ver `CONTEXTO_app.md`) e `13826b9` (Eqs. 9.14-9.17 + Nomenclatura, este
arquivo), o app sempre antes do livro para o código nunca divergir
silenciosamente do texto. Nenhum trailer de coautoria de IA, como sempre.

## Quarto relatório externo (dicas_kimi.md, versão de 16/08/2026) implementado (16/08/2026)

Um **novo** `dicas_kimi.md` foi commitado na raiz em `702d3b2` (16/08/2026) —
distinto do relatório de mesmo nome de 31/07/2026 já implementado em
01/08/2026 (esse antigo está em `arquivos_apoio/dicas_kimi.md`, 4KB; o novo
tem 7,7KB e avalia o documento já em 151 páginas, pós-Capítulo 28). Avaliação
de qualidade do PDF compilado, diagnóstico geral "excelente estado
técnico-editorial" com um checklist de 5 itens, todos implementados nesta
sessão:

- **Cabeçalho do Capítulo 28 quebrando em 2 linhas e colidindo com o número
  de página** (mesma classe de defeito já corrigida no Capítulo 9 em
  15/08/2026, mas o Cap. 28 foi criado depois daquela correção e ficou de
  fora): `\markboth{Estudo de Caso Integrado: Diagnóstico Precoce de
  Desgaste de Folgas}{}` logo após o `\section{}` do capítulo. Confirmado
  visualmente (`pdftoppm`) — cabeçalho agora em uma linha só, sem colisão; os
  4 warnings de `headheight` do log desapareceram.
- **5 legendas de tabela sem forma curta** (Tabelas 14.1, 16.1, 17.1, 18.1,
  18.2 — todas "Matrizes de diagnóstico/decisão"): adicionado
  `\caption[curta]{longa}` às cinco. Confirmado na Lista de Tabelas extraída
  do PDF — as 5 entradas agora cabem em uma linha cada (16.1 e 17.1 antes
  quebravam em duas).
- **2 `\bibitem` órfãos** (`bloch`, `isa51`) — decisão do autor: verificar se
  havia ponto de citação natural antes de decidir remover. Achados dois
  pontos legítimos, sem inventar conteúdo: `\cite{isa51}` (ANSI/ISA-5.1-2024,
  símbolos e identificação de instrumentação) inserido no parágrafo do
  Cap. 18 que já descrevia a "convenção ISA" de níveis H/HH/LL na Tabela
  18.2 — é exatamente a norma que padroniza essa convenção. `\cite{bloch}`
  (*A Practical Guide to Compressor Technology*) inserido na frase de
  abertura do Capítulo 3 (detalhamento de componentes), como referência
  geral de apoio à organização por subsistema já usada no capítulo. Nenhuma
  referência restou órfã — fecha também a pendência menor do `isa51}`
  registrada em 02/08/2026.
- **Floats `[h!]` sem fallback** (15 tabelas + 20 figuras): trocado para
  `[h!tbp]` (mantém a preferência por "aqui", mas com posições de
  fallback), eliminando os warnings de `'h' float specifier changed to
  'ht'` do log. `\begin{table}[H]` (2 ocorrências, pacote `float`, posição
  fixa) não foi tocado — não é o mesmo mecanismo e não gera esse warning.
- **Item 5, opcional, decisão do autor** (atualizar
  `apresentacao_compressores.tex` com slides da Parte III/Capítulo 28) —
  **não implementado nesta sessão**, aguardando decisão do autor (ver
  próxima interação).

**Verificação de não regressão**: compilação limpa em 3 passagens, 151
páginas (mesma contagem de antes — nenhuma mudança estrutural, só correções
pontuais), 0 referências indefinidas, 0 labels `eq`/`tab`/`fig` duplicados
(a única mensagem de "duplicate ignored" no log é a `name{page.1}` já
conhecida e inofensiva, mistura de numeração romana/arábica — não é um label
do documento), 0 `??`/caracteres de substituição no PDF extraído, overfull
hboxes em 35 (mesmo baseline de ~2pt na Nomenclatura, sem regressão), 0
warnings de `headheight` ou `float specifier` (eram 4 e ≥13 antes desta
sessão). Renderização visual conferida na página do Capítulo 28 (cabeçalho
em uma linha) e na Lista de Tabelas (5 entradas agora em uma linha).

**Nada foi commitado** — aguardando revisão do autor, como sempre. **Atualização**:
commitado depois, a pedido do autor, em `7f6ddc3`.

**Avaliação crítica do relatório** (o autor pediu explicitamente, em sessão
seguinte, para sempre avaliar `dicas_kimi.md` com ceticismo antes de
implementar — não confiar de cara; ver regra permanente logo abaixo desta
entrada). Verificação independente de cada um dos 4 achados acionáveis, feita
**depois** de já terem sido implementados nesta sessão (deveria ter sido
**antes** — lição para a próxima vez, ver regra abaixo):

- **Cabeçalho do Cap. 28**: achado real, diagnóstico correto (mesma classe do
  bug do Cap. 9), confirmado pelos 4 warnings de `headheight` no log antes da
  correção e pela inspeção visual depois. **Preciso.**
- **5 legendas sem forma curta**: achado real, confirmado pela Lista de
  Tabelas extraída do PDF (16.1 e 17.1 quebravam em duas linhas antes).
  **Preciso.**
- **2 `\bibitem` órfãos**: achado real, confirmado por `grep -c "cite{bloch}"`
  = 0 antes da correção. **Preciso**, embora a recomendação do relatório
  fosse binária demais ("citar ou remover") — havia pontos de citação
  legítimos para as duas sem precisar inventar conteúdo nem remover
  referências verificadas, uma terceira opção que o relatório não considerou.
- **Floats `[!h]` sem fallback**: diagnóstico da causa (LaTeX força `h`→`ht`
  quando só a letra `h` é dada, gerando o warning) está correto, mas a
  **sintaxe citada está errada** — o relatório escreveu `[!h]`/`[!htbp]`; o
  `.tex` real usa `[h!]` (ordem invertida) em todas as 35 ocorrências, nunca
  `[!h]`. Imprecisão cosmética que não muda a correção aplicada
  (`[h!]`→`[h!tbp]`), mas quem fosse `grep` literalmente por `[!h]` no
  arquivo (como o relatório sugere implicitamente) não acharia nada.
- **Seção "Verificações de conformidade"** (as alegações de 100% de adesão às
  convenções): re-verificadas independentemente por `grep`/script Python
  nesta sessão — 0 `\hline`/`tabular{|`/`array{|`, 28 `\section` todos
  precedidos de `\clearpage`, 209 labels `eq:s*-*`, 0 hardcode
  `Equação~N.N` fora de `\eqref{}`. **Todas conferem.**

**Conclusão**: este `dicas_kimi.md` (16/08) foi o relatório externo mais
preciso já recebido no projeto — 100% dos achados acionáveis se confirmaram,
única mancha é a inversão de caracteres na sintaxe do float specifier
(diagnóstico certo, notação errada). Atualiza a régua de calibração de
ceticismo (ver "Estado atual" abaixo): Copilot acertou sintoma e errou causa;
Kimi antigo (01/08) subestimou extensão; Manus acertou tudo; **este Kimi
(16/08) acertou tudo, com uma imprecisão cosmética de sintaxe**.

## Regra permanente: avaliar relatório externo antes de implementar, não depois (16/08/2026)

O autor pediu explicitamente: toda sessão futura deve **primeiro ler o
`CONTEXTO.md` inteiro**, e só depois avaliar qualquer `dicas_kimi.md` (ou
outro relatório externo novo) com ceticismo — decidir por achado se ele entra
no documento (confirmado) ou é refutado/questionado (impreciso), **antes** de
sair implementando o checklist inteiro. Nesta sessão a verificação acabou
sendo feita depois da implementação (por sorte, todos os achados eram reais)
— não repetir esse atalho. Fluxo correto para a próxima vez que um relatório
externo aparecer: (1) ler o relatório inteiro; (2) para cada item do
checklist, rodar a verificação independente (grep/recompilação/inspeção
visual) **antes** de editar o `.tex`; (3) só depois aplicar as correções cujos
achados se confirmaram; (4) registrar no `CONTEXTO.md` tanto a implementação
quanto a nota de precisão do relatório (como a seção logo acima desta).

## Estado atual (última sessão)

Documento compilava em 141 páginas ao fim da sessão do Backlog Kimi (era 135
antes dela — ver "Backlog Kimi implementado" acima); **atualização de
15/08/2026**: os 13 itens do Backlog Kimi descritos como "sem commit" no
parágrafo abaixo já foram commitados desde então (`2876885`, conferir sempre
`git log` em vez desta nota — ver aviso mais abaixo), e o documento está em
**146 páginas** após o trabalho de 15/08/2026 (Eq. 9.6, auditoria de perdas
termodinâmicas/fluidas, acoplamento Hood↔Carcaça, correção em massa das
~110 equações sem número citado antes de aparecer, e o bug de cabeçalho do
Capítulo 9 — ver as seções correspondentes acima, todas já commitadas até
`11e13f3`). Sem erros/referências indefinidas/labels duplicados. Todos os 27
capítulos têm subseções e aparecem estruturados no sumário. O parágrafo
original desta seção segue abaixo, para contexto histórico do que a sessão do
Backlog Kimi deixou pendente **antes** de ser commitado. Repositório git
inicializado (ver "Visão de longo prazo" acima); histórico completo
reescrito em 26/07/2026 para remover trailers de coautoria (ver seção
acima) — os hashes de commit mudaram desde qualquer anotação anterior a
essa reescrita, sempre confira com `git log` em vez de citar um hash de
memória. Tag `v1.0` no commit inicial (recriada). A lista de commits
abaixo (até `1d0ebc3`/`738cc1c`) é a mais recente que foi conferida
manualmente; sessões seguintes já avançaram o `HEAD` (ex.: trabalho de
secagem PSA/SEC\_dry-HI\_des e a correção da própria Equação 15.7 têm
commits posteriores a `738cc1c`) — **use `git log --oneline -20` para o
estado exato do HEAD antes de assumir que a lista abaixo é atual**.
Commits conferidos, em ordem: `a1f8ffb` (correção do `cmap`, 26/07/2026) →
`693a2c6` (fora do escopo deste documento — não é conteúdo do livro) →
`27997b6` → `3417919` (os dois de dicas_kimi.md acima) → `8657b5c`
(consolidação do trabalho pendente de 29-31/07, ver acima) → `1d0ebc3`
(correção deste próprio arquivo). Os commits seguintes conferidos
(`7a0d1cf`, `875e900`, `06ff51d`, `0b6534e`, `d637ae2`) são todos do
`aplicativo/` — fora do escopo deste documento — exceto `738cc1c`
(correção da Equação 15.7, ver seção acima), que é do livro.

O conteúdo das sessões de **29/07/2026 e 30/07/2026** (as duas seções
acima), que ficou ~550 linhas sem commit por opção deliberada do autor, foi
finalmente commitado em **01/08/2026** — commit `8657b5c`, um único commit
(não fatiado por tema; o fatiamento em 9 partes cogitado nas notas acima não
foi usado, o autor preferiu velocidade). Cobre: normas ISO 20816/8573/1217,
aprofundamento da Parte II, tabelas com `\label` e referência cruzada,
ano/edição das referências, Capítulos 12 e 13, correção das aspas do babel,
correção de unidades nas Equações 9.8 e 11.6, listas de figuras/tabelas com
legendas curtas e hifenização, e subseções dos Caps. 26/27 com a indentação
dos blocos de código Python corrigida.

Observação: os arquivos de análise externa que ficavam soltos na raiz do
projeto foram movidos para `arquivos_apoio/` em 02/08/2026 (a pedido do
autor — "não apague, coloque no subdiretório"). O subdiretório inteiro
continua **não rastreado pelo git**, mesmo status de antes, só mudou o
caminho. Conteúdo:

- `recomenda compressores.txt` (análise externa via Copilot CLI, ver
  "Correção de extração de texto" acima)
- `Manus_parecer_final_compressores.md` (análise externa da Manus AI,
  **lida e implementada em 29-30/07/2026**, ver as duas seções acima)
- `dicas_kimi.md` (análise externa da Kimi, **lida e implementada em
  01/08/2026**, ver seção acima)
- `referências extras para as fórmulas.md` — **não é markdown apesar da
  extensão**: é um `.odt` (OpenDocument Text) renomeado, conteúdo
  binário, ainda não examinado
- `Backlog_kimi_compress.md`, `compressores.txt`, `dicas_COPILOT.md` —
  os três apareceram na raiz durante a sessão de 02/08/2026 e foram
  **lidos e resolvidos ainda na mesma sessão** (ver "Backlog Kimi
  implementado" abaixo): `dicas_COPILOT.md` é de fato um quarto relatório
  externo, distinto de `recomenda compressores.txt` — um relatório de
  verificação automática (checagem de "??"/caracteres de substituição,
  reconciliação de contagem de equações), não uma análise de conteúdo;
  suas recomendações foram executadas como parte da checagem final do
  Backlog. `compressores.txt` é só o artefato de extração
  (`pdftotext -layout compressores.pdf`) que o próprio `dicas_COPILOT.md`
  gerou para se verificar — não é conteúdo a preservar, pode ser
  regenerado ou apagado a qualquer momento.

Não mexer em nenhum arquivo de `arquivos_apoio/` nem incluí-los em commits
sem o autor pedir explicitamente. Diferença de qualidade entre os três
relatórios já lidos, útil para calibrar ceticismo no futuro: o Copilot
acertou o sintoma e errou a causa; o Manus acertou os três problemas
normativos, todos confirmados na fonte primária; o Kimi acertou o
diagnóstico de diagramação mas subestimou a extensão de alguns itens
(relatou 1 tabela com overfull grave, a varredura achou 5).

**Resolvido**: a referência bibliográfica `\bibitem{isa51}` (ANSI/ISA-5.1-2024)
que aparecia como modificação não rastreada não era de outra ferramenta —
era o início de uma tentativa (nesta mesma sessão, mesma conversa) de
adicionar uma lista de instrumentos ISA à Tabela de Instrumentação do
Capítulo 3, que o autor interrompeu antes de a tabela em si ser escrita.
A referência ficou órfã (citada em lugar nenhum) até o Backlog Kimi ser
implementado logo em seguida, que a reaproveitou de fato (ver "Backlog
Kimi implementado" abaixo, BK-09 — silenciador/invólucro acústico cita
`iso2151`, não `isa51`; a `isa51` permanece órfã, sem uso em nenhuma
equação/tabela do texto no momento). **Pendência menor**: remover
`\bibitem{isa51}` da bibliografia se a lista de instrumentos ISA não for
retomada, ou usá-la de fato se for.

Principais mudanças de 26/07/2026 (sessão longa, dia único):
- Bibliografia (45 referências) verificada uma a uma contra fontes reais; 3 tinham
  título fabricado/não verificável e foram corrigidas (`api684`, `dompc`, `lysholm`
  — ver "Veracidade de referências e fontes" acima para a regra permanente).
- Figura 3.1 deixou de ser um corte esquemático 2D e passou a ser o render 3D do
  par de rotores (`fig_parafuso3d()` em `gen_figuras.py`, ver seção "Figuras").
- Livro dividido em Parte I (Capítulos 2-18) e Parte II (Capítulos 19-27), cada uma
  com página dedicada centralizada (ver "Estrutura em duas Partes" acima).
- Diagramação completa — todos os 8 itens do `relatorio_diagramacao.md`
  implementados (ver "Diagramação — convenções" acima): hyperref sem caixas
  vermelhas, quebra de página por capítulo, cabeçalho corrente, tabelas em
  booktabs, microtype, capa com rótulo de volume/revisão, identidade visual
  "Capítulo N" via `titlesec`, larguras de figura padronizadas em 3 categorias.
- Os antigos "Anexo A"/"Anexo B" (`\appendix`) foram removidos — os Capítulos 26 e
  27 (implementação) agora são capítulos numerados normais dentro da Parte II, já
  que a divisão em Partes tornou a separação por Anexo redundante (a pedido do
  autor).
- Criada `apresentacao_compressores.tex`/`.pdf` (Beamer, 21 slides, tema
  Metropolis) resumindo o livro para uso em reuniões (ver "Arquivos e pastas").
- Revisão de referenciamento de equações: Capítulo 3 (que não tinha nenhuma
  equação numerada) e mais 4 fórmulas soltas nos Capítulos 6, 11, 17, 22 e 26
  passaram a ter `\label`/`\eqref` (ver "Referenciamento de equações" acima).
- Adicionada cobertura de desbalanço de fase (tensão/corrente/temperatura) no
  motor elétrico do Capítulo 4, com nova Equação 4.8 (ver "Cobertura de
  desbalanço de fase" acima).
- Capítulo 3 expandido (definição real de todos os 14 itens) e Capítulo 12
  corrigido para eliminar linguagem de compressor oil-flooded ("injeção de
  óleo", separador ar/óleo no caminho do ar) — ver "Capítulo 3 expandido e
  inconsistência oil-free" acima.
- Nova Figura 2.3 (Capítulo 2): render 3D do trem de compressão completo
  (motor → gearbox → estágio LP → intercooler → estágio HP → saída), a
  pedido do autor (preferência já registrada por figuras 3D/realistas em vez
  de esquemas 2D). A primeira versão foi rejeitada por parecer "primitivas
  genéricas" (cilindros/caixas lisos); revisada no mesmo dia com aletas,
  nervuras, dentes de engrenagem reais e flanges — ver "Figuras" acima para
  as funções novas em `gen_figuras.py`, a lição sobre nível de detalhe e as
  três armadilhas de quem for reutilizá-las.
- Inventário dos algoritmos da Parte II e aprofundamento de Savitzky-Golay,
  Isolation Forest e Processo Gaussiano (antes só citados por nome) — ver
  "Inventário de algoritmos da Parte II" acima.
- 4 figuras didáticas novas na Parte II (VAE, MPC, PSO, Isolation Forest),
  corrigindo o déficit de ilustração identificado pelo autor — ver
  "Déficit de figuras identificado e corrigido" acima.
- Corrigida extração de texto do PDF: ligaduras "fi"/"ff" viravam bytes de
  controle (`\usepackage{cmap}` adicionado) — ver "Correção de extração de
  texto" acima.

## Capítulo 28 implementado — Metodologia de Calibração e Catálogo de Detecção (16/08/2026)

O plano fechado na sessão de 15/08/2026 (ver "PENDENTE — Metodologia de
calibração/anomalia na Parte III" acima, agora marcada como resolvida) foi
executado nesta sessão: a Parte III passou a ter **dois** capítulos — o novo
**Capítulo 28** (metodologia) inserido antes do estudo de caso, que virou
**Capítulo 29** (renumeração automática via `\thesection`; só os labels
`eq:s28-1`→`eq:s29-1`, `tab:28-1/2`→`tab:29-1/2`, o comentário de fim de
capítulo e a linha `RUL` da Nomenclatura precisaram de edição manual — a regra
"sufixo do label = número exibido" foi mantida).

**Incidente de coordenação, registrado para não repetir**: a renumeração acima
foi feita por um fork lançado só para *extrair* o conteúdo das tabelas de
mecanismos de falha (não para editar nada) — mas ele foi além do escopo pedido
e editou o `.tex` diretamente. Verificação (`git diff`, recompilação) confirmou
que a edição em si era mecanicamente correta e não teve mais nada inesperado,
então foi aproveitada em vez de revertida, mas a lição fica: instruir um
subagente a "só extrair, não editar" não impede fisicamente que ele edite —
sempre conferir `git diff` depois de qualquer subagente com acesso a
ferramentas de escrita, mesmo quando a tarefa pedida era só leitura.

**Conteúdo do Capítulo 28**, três subseções, nesta ordem:
- **28.1 — Estimação Conjunta de Estado e Parâmetro (EKF com Estado
  Aumentado)**: duas equações novas (`eq:s28-1`, `eq:s28-2`) formalizam
  aumentar o vetor de estado do EKF (Equação 21.2) com um vetor $\Lambda$ de
  parâmetros estáticos nunca medidos nesta máquina — $K$ (Eq. 9.3, que o
  próprio texto já qualificava como "calibrado por ensaio" sem nunca dizer
  como), $\eta_{\text{mec}}$ (Eq. 5.5) e $\zeta_{\text{ref}}$ (Eqs. 3.4/5.4) —
  tratados como passeio aleatório de covariância $Q_\Lambda$ quase nula numa
  janela de calibração (comissionamento/pós-manutenção) e pequena depois, para
  acompanhar deriva lenta sem descartar a calibração. Cita a implementação
  real do EKF no app (`aplicativo/compressor_sim/ekf.py`) como precedente do
  *mecanismo* de convergência bayesiana — mas com o cuidado de **não
  superclamar**: o app hoje estima dois estados dinâmicos (folga, fouling),
  não parâmetros estáticos aumentados: a estimação conjunta de $\Lambda$ em si
  é uma extensão proposta nesta seção, sem implementação de referência ainda.
  Símbolo novo: $\Lambda$ (maiúscula, verificado sem colisão — $\theta$ já
  estava saturado com três significados distintos no documento, então não foi
  reaproveitado) e $Q_\Lambda$\dag, ambos na Nomenclatura.
- **28.2 — Protocolo de Registro de Parâmetros Desconhecidos e Lacunas de
  Instrumentação**: nova Tabela 28.1, 4 categorias de proveniência (Medido /
  Inferível via *Soft-Sensor* / Calibrável na Janela Saudável / Desconhecido-
  Literatura), formalizando o conceito de "lacunas de observabilidade" que já
  existia em prosa desde o Capítulo 18 (Tabela 18.1) e o Capítulo 12, mas
  nunca como classificação explícita aplicada a **parâmetros** (só a
  variáveis de estado).
- **28.3 — Catálogo de Mecanismos de Falha Simuláveis para Detecção via
  Gêmeo Digital**: nova Tabela 28.2 (`longtable`, ~57 mecanismos, 4 páginas),
  cobrindo todas as "Matrizes de Falha"/"Diagnóstico" dos Capítulos 2, 4, 6–17
  já existentes no livro — nenhum mecanismo novo, só consolidação. Cada linha
  liga o mecanismo à variável/estado que já o indica e a um de quatro tipos de
  detecção: EKF (só para os 5 estados explícitos da Equação 21.2 — $\delta$,
  $R_f$, $\eta_{is,LP}$, $\eta_{is,HP}$, $\sigma_b$ — nada mais), VAE (padrões
  silenciosos/multivariáveis sem limiar direto), PIML (casos que o próprio
  livro já descreve como ambíguos por leitura direta — as 4 linhas da Tabela
  12.1, a dupla Superaquecimento/Contato do Cap. 9, etc.) ou **Limiar direto**
  — a maioria das linhas, deliberadamente, para não inflar o catálogo
  atribuindo um algoritmo sofisticado a mecanismos que já têm indicador
  suficiente. A Diretriz Técnica Final amarra as três seções (28.1 alimenta
  28.2 que condiciona a confiabilidade de 28.3) e aponta para o Capítulo 29.

**Duas correções feitas durante a escrita, antes de compilar** (mesma
disciplina de veracidade de sempre): a primeira citação de $\eta_{\text{mec}}$
apontava para uma equação que não existe (`eq:s4-12`, confundido com
$\eta_{mot}$ do motor) — corrigida para `eq:s5-5`, a equação real onde
$\eta_{\text{mec}}$ é definida; e a linha do catálogo sobre erro de
reconstrução do VAE citava `eq:s22-6` (o limiar $\tau_{\text{limiar}}$) em vez
de `eq:s22-5` (o próprio $E_{\text{rec}}$) — checado contra o `.tex` antes de
compilar, não depois.

**Verificação de não regressão** (mesmas varreduras de sempre, desta vez
feitas *antes* de reportar como concluído): compilação limpa em 3 passagens,
158 páginas (era 151, +7 para o capítulo novo), 211 labels `eq:s*-*` (era 209,
+2: `eq:s28-1`, `eq:s28-2`), 0 referências indefinidas, 0 labels duplicados
(fora o `page.1` já conhecido e inofensivo), 0 `??`/bytes de controle no PDF
extraído, 0 hardcode `Equação~N.N` fora de `\eqref{}`, auto-referência das 3
equações novas confirmada (`\eqref{}` de si mesma no parágrafo anterior),
overfull hboxes de volta ao baseline de 35 (a `longtable` do catálogo gerou 2
overfulls novos na primeira tentativa — cabeçalho "Cap." espremido numa coluna
de 0,7cm — corrigidos alargando para 1,0cm antes de considerar concluído).
Renderização visual conferida em 6 páginas (abertura do Cap. 28, Tabela 28.1,
início e continuação da Tabela 28.2, Diretriz Técnica Final, abertura do
Cap. 29) — cabeçalho corrente de ambos os capítulos em uma linha só, sem
colisão com o número de página. Sumário e Lista de Tabelas conferidos:
"III Estudo de Caso Integrado" (p. 142), Capítulos 28/29 com suas subseções,
Tabelas 28.1/28.2/29.1/29.2 todas listadas.

**Nada foi commitado ainda** — aguardando revisão do autor. **Atualização**:
commitado em `68d302f`.

## Slides da Parte III adicionados ao Beamer (16/08/2026)

Item 5 (opcional) do `dicas_kimi.md` de 16/08 implementado a pedido do autor:
`apresentacao_compressores.tex` ganhou 2 slides novos, entre "Evolução do
Gêmeo Digital" e "Síntese" — um resumindo a metodologia do Capítulo 28
(estado aumentado do EKF, protocolo de 4 categorias, catálogo de ~57
mecanismos) e outro com a demonstração numérica do Capítulo 29 (cenário
$\delta$/L, EKF→VAE→PIML→MPC, $RUL_\delta\approx9$ semanas). Seguem o estilo já
estabelecido do deck (bullets curtos, equações quando ajudam, sem tabela —
nenhum slide do deck usa `tabular`, então não introduzi uma). A Agenda ganhou
uma linha para a Parte III, e a contagem de páginas do slide de Síntese
("84 p.") — desatualizada desde a criação do deck em 26/07/2026 — foi
corrigida para 158. Deck foi de 21 para 23 slides.

**Ajuste feito durante a verificação**: a primeira versão do slide do
Capítulo 28 estourava a moldura do frame (texto cortado embaixo) —
encurtado (frase de abertura e os 3 bullets) até caber sem overflow,
conferido via `pdftoppm`. O slide do Capítulo 29 coube de primeira.

**Verificação**: compilação limpa em 2 passagens, sem erros nem referências
indefinidas, 23 páginas. Renderização visual conferida em 4 slides (Agenda,
os dois novos, Síntese).

**Nada foi commitado ainda** — aguardando revisão do autor. **Atualização**:
commitado em `e059d24`.

## Problema inverso: Cap. 23.8 novo, Cap. 28.1 revisado (16/08/2026)

O autor observou: "já solicitei uma inserção nas Partes II e III sobre
problemas inversos para detecção de parâmetros normalmente ajustados por
valores referenciais que podem ter alguma variação dependendo do local e do
tipo de instalação." Verificação contra o texto então existente: o Cap. 28.1
(EKF com estado aumentado) já cobria o mecanismo, mas sem o termo "problema
inverso" nem a motivação explícita de variação por local/instalação; o Cap.
27 já citava "problemas inversos" como papel do DeepXDE (desde 26/07/2026),
mas nunca elaborado em conteúdo real na Parte II. Autor escolheu fechar as
duas lacunas ("as duas coisas").

**Cap. 23.8 (nova subseção, fim do Capítulo 23 — PIML)**: usa a dualidade
direto/inverso do próprio título do artigo de Raissi et al. 2019 já citado
(`\cite{piml}` — "Solving Forward **and Inverse** Problems", verificado
contra a entrada da bibliografia antes de basear a afirmação nisso) para
apresentar identificação de parâmetro via PINN: o parâmetro físico $\Xi$
passa a ser variável treinável junto aos pesos da rede, Equação~23.5 nova
(`eq:s23-5`), explicitamente ligada ao DeepXDE do Cap. 27 e ao mesmo
objetivo do Cap. 28.1 — mas por um caminho offline, capaz de parâmetros
distribuídos no espaço. Símbolo novo $\Xi$ na Nomenclatura, sem colisão
(verificado — $\theta$ já estava saturado com três significados distintos
no documento, por isso não foi reaproveitado).

**Cap. 28.1 (parágrafo de abertura revisado)**: nomeia "problema inverso"
explicitamente (definição direto vs. inverso) e explica por que K, $\eta_{mec}$
e $\zeta_{ref}$ variam entre instalações — lote de fabricação, alinhamento/
lubrificação de campo, fornecedor do elemento filtrante, plataforma — em vez
de só dizer "nunca medidos nesta máquina específica" como antes.

**Verificação**: compilação limpa em 3 passagens, 160 páginas (era 158),
212 labels `eq:s*-*` (era 211, +1 — `eq:s23-5`), 0 referências indefinidas,
0 `??`, 0 hardcode de equação, auto-referência da equação nova confirmada.
Renderização visual conferida nas 3 páginas relevantes (Cap. 23.8, Cap.
28.1 revisado) — sem overfull novo, referências cruzadas entre capítulos
(23↔27↔28) resolvendo corretamente.

**Nada foi commitado ainda** — aguardando revisão do autor. **Atualização**:
commitado em `fcfa407`.

## Slide novo no Beamer: o app como prova de conceito (16/08/2026)

A pedido do autor ("atualize a apresentação com o escopo ampliado para que
as pessoas entendam"), mais um slide em `apresentacao_compressores.tex`,
entre o slide do Cap. 29 e a Síntese: "Não é só teoria: simulador funcional
(`aplicativo/`)" — resume que os 5 algoritmos da Parte II rodam de verdade
no app (71 testes automatizados), cita a identificação de parâmetro por
problema inverso (Cap. 23.8/28.1, implementada no app no mesmo dia — ver
`CONTEXTO_app.md`) como exemplo concreto, e fecha com o achado real de que
portar equações para código já expôs 3 erros de unidade no livro. Mesmo
ajuste de conteúdo do primeiro slide desta família (encurtado após estourar
a moldura na primeira versão, `pdftoppm` confirmou depois de corrigido).
Deck foi de 23 para 24 slides, compilação limpa.

**Nada foi commitado ainda** — aguardando revisão do autor. **Atualização**:
commitado em `166040b` (junto com a documentação do app, ver abaixo).

## Resumo da sessão de 16/08/2026

Sessão longa, um único dia, que cobriu o `dicas_kimi.md` novo, a Parte III
inteira do livro (Cap. 28 + renumeração do estudo de caso para Cap. 29), a
ponte problema-inverso entre Partes II e III, os slides correspondentes, e a
extensão simétrica de tudo isso no `aplicativo/` — mais documentação de
implementação do app, criada do zero. Para quem só ler esta entrada:

- **`dicas_kimi.md`** (relatório novo, distinto do de 01/08): checklist de 5
  itens implementado (cabeçalho do Cap. 28, legendas curtas, 2 referências
  órfãs resolvidas, floats sem fallback) — avaliação crítica registrada
  depois: relatório mais preciso já recebido no projeto, uma única
  imprecisão cosmética de sintaxe.
- **Capítulo 28 (metodologia) + Capítulo 29 (estudo de caso, renumerado)**:
  EKF com estado aumentado (Λ=[K, η_mec, ζ_ref], Eqs. 28.1/28.2), protocolo
  de 4 categorias de proveniência de parâmetro (Tabela 28.1), catálogo de
  ~57 mecanismos de falha ligados ao algoritmo de detecção primário (Tabela
  28.2). Renumeração feita por um fork que excedeu escopo — incidente
  registrado, verificado como correto e aproveitado.
- **Problema inverso** (Cap. 23.8 novo + Cap. 28.1 revisado): PINN
  identificando parâmetro físico Ξ como variável treinável (Eq. 23.5),
  ligada ao DeepXDE já citado no Cap. 27; Cap. 28.1 ganhou a nomenclatura
  explícita de "problema inverso" e a motivação de variação por
  local/instalação que faltava.
- **Apresentação**: 3 slides novos (Parte III/Cap. 28, Cap. 29, e o app como
  prova de conceito) — 21→24 slides.
- **App (`aplicativo/`)**: os mesmos dois mecanismos de identificação de K
  portados para código real — EKF aumentado (`ekf.py`) e PIML com problema
  inverso (`piml.py`) — com 5 testes novos (71 no total) e dois bugs reais
  encontrados e corrigidos durante a implementação (condicionamento do EKF
  em baixa folga; resíduo do PIML ignorando a correção psicrométrica). Três
  documentos novos (`IMPLEMENTACAO.md`, `GUIA_CODIGO.md`, `MANUTENCAO.md`)
  mais `README.md` atualizado — ver `CONTEXTO_app.md` para os detalhes.
  Verificado depois ao vivo no navegador, a pedido do autor, com o
  Claude-in-Chrome (que desconectou e precisou reconectar no meio da
  verificação — comportamento já visto em sessões anteriores).

**Commits desta sessão, em ordem**: `702d3b2` (autor, `dicas_kimi.md` novo)
→ `7f6ddc3` (checklist do relatório) → `68d302f` (Cap. 28/29) → `e059d24`
(slides Parte III) → `fcfa407` (problema inverso no livro) → `da20c83`
(problema inverso no app) → `166040b` (documentação do app + slide final).
Livro em 160 páginas, apresentação em 24 slides, app com 71 testes — todos
verificados limpos ao final desta entrada. Repositório sem nada pendente de
commit; `arquivos_apoio/` continua fora do controle de versão, como sempre.

**Atualização, mesmo dia — a sessão continuou depois desta entrada**: mais
três peças, ainda não commitadas no momento desta atualização:

- **Fluxo conceitual do pipeline completo**: o autor articulou de próprio
  punho a lógica de ponta a ponta que amarra livro/apresentação/app — ver
  "Fluxo conceitual do pipeline completo (raciocínio do autor, 16/08/2026)"
  logo após "Visão de longo prazo do projeto" no topo deste arquivo.
  Confirmou que o fluxo já descrito bate com o que existe (Parte I →
  simulação → problema inverso → Parte II → catálogo/estudo de caso →
  prognóstico), e revelou 4 lacunas reais, adicionadas como itens 5–8 de
  "Pendências conhecidas": sensores móveis, perda de válvulas
  parametrizada, treino sobre múltiplos mecanismos de falha, supervisório
  real.
- **Uso de GPU (CUDA) no app**: o autor notou que a GPU (RTX 4070) não
  era usada mesmo estando disponível. Implementado de verdade — novo
  módulo `compressor_sim/torch_device.py`, `vae.py`/`piml.py` movendo
  modelo e tensores para `device`, `requirements.txt` sem a restrição
  CPU-only, torch reinstalado no venv do autor com build CUDA e verificado
  com `nvidia-smi` mostrando utilização real durante um treino. Detalhes
  completos em `CONTEXTO_app.md`, "Uso de GPU (CUDA) quando disponível".
- Estas duas peças **não têm commit próprio ainda** — o resumo dos commits
  acima continua sendo a lista completa até `166040b`. Ver `git status`/
  `git log` antes de assumir o estado exato do repositório a partir daqui.

## Pendências conhecidas (candidatos para a próxima sessão)

Nada está quebrado — o documento compila limpo e não há dívida técnica em
aberto. O que segue são melhorias identificadas e ainda não feitas, em ordem
aproximada de valor:

1. **Glossário bilíngue de anglicismos** — recomendação do Manus, também
   levantada pelo Copilot, e a única do parecer que não foi nem implementada
   nem descartada. O livro usa *offloading*, *fouling*, *header*, *load
   shedding*, *surrogate model*, *model drift*, *blow-down*, *timing gears*,
   *trip* etc. sem tradução sistemática. A forma sugerida é: seção de glossário
   ao final, mais a primeira ocorrência de cada termo no texto ajustada para
   "termo em português (original)".
2. **Capítulos mais curtos do livro** — se o critério de "capítulo
   desenvolvido, não nota técnica" (parecer Manus) for aplicado adiante,
   começar por eles. **Contagem refeita em 13/09/2026: Cap. 27 (605 palavras),
   Cap. 25 (1.022), Cap. 6 (1.075) e Cap. 20 (1.091).** A lista anterior desta
   pendência — "Caps. 11 (864), 14 (923), 20 (974) e 6 (976)" — está vencida:
   os Caps. 11 e 14 cresceram desde então e saíram do fim da fila, e o Cap. 27
   (Implementação de Alta Performance) passou a ser o mais curto, logo depois de
   ganhar a seção da stack Rust. O Cap. 6 é o único que aparece nas duas listas
   — e é também o único capítulo da Parte I sem nenhuma figura (pendência
   separada), o que o torna o candidato mais forte. (Contagem por script Python
   sobre o `.tex`, incluindo marcação; serve para ranquear, não como número
   absoluto.)
3. **Redes Bayesianas (Cap. 25)** continuam citadas só por nome, sem equação —
   pendência herdada do "Inventário de algoritmos da Parte II" acima.
   *(Atualização de 13/09/2026: a metade sobre **MHE do `do-mpc`** saiu desta
   pendência — ganhou subseção própria, "Controle Preditivo e MHE (do-mpc)",
   `compressores.tex:3648`. Segue sem equacionamento próprio, mas não é mais
   "só uma citação por nome".)*
4. ~~Estudo de caso numérico de ponta a ponta~~ — **feito em 15/08/2026**,
   ver "Parte III — Estudo de Caso Integrado, Capítulo 28" acima.
5. ~~Sensores móveis/portáteis~~ — **feito no livro em 16/08/2026**, restrito
   a equipamentos portáteis e wireless (drones excluídos a pedido do
   autor): Cap. 18, nova subseção "Sensores Portáteis e Wireless:
   Complemento à Instrumentação Fixa", Tabela 18.3, Equação 18.6
   ($\mathcal{R}_{\text{port}} = \kappa_{\text{port}}\cdot\mathcal{R}_{\text{fixo}}$).
   Ver "Extensão de três pendências no livro" abaixo. **App**: sem
   implementação de referência ainda.
6. ~~Perda de carga de válvulas como elemento parametrizado~~ — **feito no
   livro em 16/08/2026**: Cap. 5, nova subseção e Equação 5.16
   ($\zeta_{\text{valv}}$, mesma forma do filtro/Eq. 5.4), vetor $\Lambda$
   da Equação 28.1 estendido de 3 para 4 elementos. Ver "Extensão de três
   pendências no livro" abaixo. **App**: sem implementação de referência
   ainda (mesma lacuna de canal de medição que já vale para $\eta_{\text{mec}}$/$\zeta_{\text{ref}}$).
7. ~~Treino sobre múltiplos mecanismos de falha simultaneamente~~ — **feito
   no livro em 16/08/2026**: Cap. 29, nova subseção "Generalização: da
   Atribuição Pontual ao Treino Multi-Mecanismo", Equação 29.2 (busca por
   resíduo mínimo generalizada sobre o catálogo, $\mathcal{M}\subseteq$
   Tabela 28.2 — contagem real do catálogo é 59 mecanismos, não 57 como
   escrito nesta pendência originalmente). Ver "Extensão de três
   pendências no livro" abaixo. **App**: sem gerador sistemático de
   dataset multi-mecanismo ainda — só o cenário único do Cap. 29.
8. ~~Supervisório real~~ — **feito no livro em 16/08/2026**, restrito a
   metodologia (o autor optou por não estender o app nesta rodada): Cap.
   26, nova subseção "Painel Supervisório de Frota", após "Requisitos de
   Passagem para Produção". Reaproveita `ekf_update` (Eq. 26.1), o Health
   Index (Eq. 26.4), a matriz de alarmes (Tabela 18.2) e o prognóstico GP
   (Eq. 19.10) num laço por máquina/ciclo, com pseudocódigo Python
   (`ciclo_supervisorio`) no mesmo padrão dos outros trechos de código do
   capítulo — sem inventar algoritmo novo. Formaliza a ordenação por
   urgência (alarme ativo primeiro, depois menor HI) e a propagação do NIS
   junto com o HI, para não confundir "máquina degradando" com "estimativa
   não confiável". **App**: sem implementação — exigiria estado
   persistente entre sessões do Streamlit e agendamento contínuo, nenhum
   dos dois presente hoje; registrado como tal na própria seção nova.

**Deliberadamente descartado**: a recomendação do Manus de abandonar o termo
"Enciclopédia" no título por ser ambicioso demais para 105 páginas. Contraria a
visão de longo prazo do autor registrada no topo deste arquivo — a obra é o
primeiro volume de uma coleção modular, e o título descreve o projeto, não o
volume isolado. Não reabrir sem o autor levantar o assunto.

~~Observação: há 4 JPEGs soltos em `figuras/` baixados pelo autor como
referência visual...~~ — **movidos em 16/08/2026** para `arquivos a
eliminar/`, os 4 (o quarto era um arquivo oculto, `.jpcompressor processo
de compressão 3D 2.jpeg`, que passou despercebido numa primeira varredura
com `ls` sem `-a` — achado só depois de um erro de staging no commit
seguinte forçar conferir `git ls-files` diretamente), ver "Saneamento de
arquivos" abaixo. Não são mais usados nem como referência de inspiração; a
Figura 3.1 já está pronta há semanas.

## Saneamento de arquivos (16/08/2026)

O autor pediu um saneamento: arquivos com mais de uma semana sem
atualização e sem uso, movidos para uma pasta nova, `arquivos a eliminar/`
(não deletados — só isolados, para revisão antes de uma remoção definitiva
que ninguém pediu ainda). O autor também avisou que usa o **Kimi CLI** como
revisor externo das tarefas — isso explica arquivos como `.mcp.json` e
`aplicativo/.kimi-code/` que aparecem sem terem sido criados nesta sessão
(já investigados antes desta entrada, não tocados — ver conversa).

**Levantamento**: todo arquivo/pasta na raiz do projeto (excluindo `.git/`,
`.claude/`, `venv/`, `__pycache__/`), com data de modificação e checagem de
uso (rastreamento git, referência em `.tex`/scripts/app). Critério: mais de
uma semana (antes de 09/08/2026) **e** sem uso corrente — não bastava ser
antigo (`figuras/`, `scripts/gen_figuras.py` são de 26/07 e continuam em uso
ativo, por exemplo, então ficaram de fora).

**Movidos** (6 itens, todos confirmados sem referência em nenhum `.tex`,
script ou módulo do app antes de mover):
- `compressores v.0.7.tex` — rascunho antigo, parte do commit inicial
  (`ec228ac`, 26/07/2026), nunca mais tocado, sem nenhuma referência em
  lugar nenhum. Claramente superado pelo `compressores.tex` atual.
- 4 JPEGs de `figuras/` (`compressor em corte.jpeg`, `compressor processo
  de compressão 3d.jpeg`, `design parafuso digital.jpeg`, e o quarto —
  achado só depois, arquivo oculto — `.jpcompressor processo de
  compressão 3D 2.jpeg`) — o próprio
  `CONTEXTO.md` já os descrevia como "não usá-los no documento", inspiração
  visual para a Figura 3.1, já finalizada há semanas. O texto antigo dizia
  "4 JPEGs"; só 3 foram encontrados nesta sessão (o quarto já não existia).
- `relatorio_diagramacao.md` — relatório de diagramação de 26/07/2026, os 8
  itens já implementados no mesmo dia, mantido só como referência histórica
  desde então.
- `documentos de apoio/referências iniciais.docx` — base bibliográfica
  original (GPAI), já cotejada com o `.tex` em 26/07/2026 (19 referências
  cruzadas, ver "Documentos de apoio" acima). O subdiretório ficou vazio
  depois e foi removido.

**Deliberadamente mantido, a pedido do autor**: `arquivos_apoio/` (7
relatórios externos — Manus, Copilot, Kimi de 01/08, Backlog, etc.) — o
autor confirmou explicitamente que prefere manter essa pasta como está,
mesmo com o saneamento em curso. **Não mover/tocar sem novo pedido
explícito** — a proteção original (`CONTEXTO.md`, seção "Estado atual",
"Não mexer em nenhum arquivo de `arquivos_apoio/`...") continua valendo.

**Verificação**: `compressores.tex` recompilado em 3 passagens depois da
movimentação — limpo, 160 páginas, nenhuma referência quebrada (nenhum dos
6 itens movidos era `\input`/`\includegraphics` do documento). Todos os 6
já estavam rastreados pelo git (confirmado via `git ls-files`, não por
inspeção visual — ver a armadilha abaixo), movidos com `git mv` para
preservar histórico.

**Dois erros próprios cometidos e corrigidos ainda dentro desta mesma
tarefa**: (1) `ls figuras/` sem `-a` não mostra arquivos ocultos —
`.jpcompressor processo de compressão 3D 2.jpeg` (o "4º JPEG" que uma nota
antiga deste arquivo já mencionava) passou despercebido na primeira
varredura; só apareceu ao rodar `git ls-files` diretamente depois de um
problema de commit. **Lição**: para inventariar arquivos de forma
confiável, usar `git ls-files`/`find` (que não escondem dotfiles por
padrão), não `ls` sem `-a`. (2) Um `git add caminho1 "caminho com espaço
que não existe mais" caminho3` falhou com `fatal:` no pathspec inválido e
**não** commitou nenhum dos caminhos daquela chamada — incluindo os
válidos (`CONTEXTO.md` ficou de fora do primeiro commit desta tarefa sem
eu perceber, só notado ao conferir `git status` depois do commit).
**Lição**: `git add` com múltiplos pathspecs falha atômico — um caminho
inválido derruba a chamada inteira; preferir chamadas separadas por
caminho quando algum deles é incerto (pasta que pode já ter sido
removida, por exemplo), e sempre conferir `git status` depois de commitar,
não só antes.

**Commitado** em dois passos: `5ef93c3` (movimentação dos 6 itens, mas sem
CONTEXTO.md por causa do erro de pathspec acima) e `0732cb4` (correção — o
4º JPEG oculto, CONTEXTO.md, e a exclusão do caminho antigo do 3º JPEG).

## Extensão de três pendências no livro: sensores portáteis, válvulas e treino multi-mecanismo (16/08/2026)

A pedido do autor ("atualize o compressores.tex com as últimas
informações"), implementadas as pendências 5, 6 e 7 listadas acima —
restrita a item 5 apenas à parte de "equipamentos portáteis e wireless"
(sem cobrir drones, que o autor excluiu explicitamente). As três entram
como metodologia documentada no livro; nenhuma tem implementação de
referência no app ainda (registrado como tal em cada seção nova, e em
`aplicativo/MANUTENCAO.md`).

- **Item 5 — Sensores portáteis e wireless** (Capítulo 18, nova
  subseção "Sensores Portáteis e Wireless: Complemento à Instrumentação
  Fixa", antes da Diretriz Técnica Final): nova Tabela 18.3 com 5 casos de
  uso (analisador de vibração de mão, termografia portátil, detector
  ultrassônico de vazamento, contador de partículas portátil, nó wireless
  de retrofit — protocolos WirelessHART/IEC 62591 e ISA100.11a/IEC 62734,
  citados sem `\cite` por não estarem na bibliografia do documento — ver
  lição abaixo). Nova Equação 18.6: $\mathcal{R}_{\text{port}} =
  \kappa_{\text{port}} \cdot \mathcal{R}_{\text{fixo}}$, inflando a
  covariância de ruído de medição do EKF para leituras não-fixas. A
  equação final do capítulo (unificação multiobjetivo) foi renumerada de
  18.6 para 18.7 — só duas referências cruzadas no próprio parágrafo,
  confirmado por `grep` antes de editar, sem referências órfãs.
- **Item 6 — Perda de carga parametrizada em válvulas** (Capítulo 5, nova
  subseção "Perda de Carga Parametrizada em Válvulas de Alívio e
  Retenção", nova Equação 5.16, mesma forma clássica do filtro (Eq. 5.4)
  aplicada a blow-off/check valve/PSV com coeficiente próprio
  $\zeta_{\text{valv}}$): estende o vetor $\Lambda$ da Equação 28.1 de 3
  para 4 elementos ($K$, $\eta_{\text{mec}}$, $\zeta_{\text{ref}}$,
  $\zeta_{\text{valv}}$) — Tabela 28.1 (categoria iii) atualizada, símbolo
  novo na Nomenclatura.
- **Item 7 — Treino multi-mecanismo** (Capítulo 29, nova subseção
  "Generalização: da Atribuição Pontual ao Treino Multi-Mecanismo", nova
  Equação 29.2): generaliza a atribuição de causa-raiz por resíduo mínimo
  (já usada informalmente na Seção "Atribuição de Causa-Raiz via PIML"
  contra 3 hipóteses escolhidas à mão) para uma busca formal
  $\arg\min$ sobre um subconjunto $\mathcal{M}$ do catálogo completo da
  Tabela 28.2. **Correção de contagem**: a pendência listada acima citava
  "57 mecanismos" — contagem real conferida por `awk`/`grep` sobre as
  linhas da Tabela 28.2 é **59**; o livro usa o número verificado (59),
  não o da nota antiga.

**Correção adicional, fora do escopo original dos 3 itens mas encontrada
ao revisar o texto da Seção 28.1**: o parágrafo que descreve a
implementação de referência do EKF com estado aumentado estava
desatualizado — dizia "sem implementação de referência no simulador até o
momento" para a estimação conjunta de $\Lambda$, mas
`aplicativo/compressor_sim/ekf.py` já tem, desde a fase 2 da Parte II
(commit `06c50bb`), a função `simular_ekf_aumentado()` implementando
exatamente esse mecanismo para $K$ (Eqs. 28.1/28.2, estado aumentado de 3
elementos). Corrigido para descrever com precisão o que está implementado
($K$, via `simular_ekf_aumentado()`) e o que não está ($\eta_{\text{mec}}$,
$\zeta_{\text{ref}}$, $\zeta_{\text{valv}}$, por falta de canal de medição).
`aplicativo/MANUTENCAO.md` também atualizado para refletir o vetor Λ de
4 elementos.

**Lição sobre citações de norma**: o primeiro rascunho da seção de
sensores wireless citava `\cite{iso8573}` (ISO 8573-1, pureza do ar
comprimido) para os protocolos WirelessHART/ISA100.11a — citação errada,
copiada por proximidade de contexto (ambos aparecem perto de "protocolo"),
não por verificação real. Corrigido antes da compilação: os números de
norma (IEC 62591, IEC 62734) são citados apenas como texto, sem `\cite`,
por não haver entrada correspondente na bibliografia deste documento —
reforça a regra de sempre verificar contra a fonte real antes de inserir
qualquer citação, mesmo quando o padrão parece familiar.

**Verificação**: 3 passagens de `pdflatex`, 160→164 páginas, sem
referências indefinidas, sem rótulo duplicado, sem *overfull hbox* severo
(>20pt) introduzido pelas mudanças — conferido por `grep` no log de
compilação antes de reportar como concluído.

Commitado em `0a00800`.

## Apresentação sincronizada com as três pendências (16/08/2026)

Pedido do autor: "atualize a apresentação também com essas mudanças".
Edições mínimas, sem inflar o deck (permanece 24 slides): slide do EKF
ganhou uma frase curta sobre leitura portátil/wireless e $\kappa_{\text{port}}$;
slide do Cap. 28 passou a mostrar $\Lambda$ com 4 elementos e a contagem
correta do catálogo (59, não $\sim$57); slide de síntese atualizado para
164 p. Uma tentativa inicial de também mencionar o item 7 (treino
multi-mecanismo) no slide do Cap. 29 foi revertida: o texto extra levava o
`Overfull \vbox` daquele frame de 15pt (já presente na versão original,
tolerável) para 72pt — regressão real, não document de layout aceitável.
**Lição**: para slides do Beamer, sempre comparar o log de overfull antes/
depois da edição (`git stash` + recompilar a versão base), não só olhar o
log da versão editada isoladamente — o número absoluto não diz se a
mudança piorou algo; a comparação diz. Commitado em `5e84bb6`.

## Item 8 (supervisório real) implementado no livro (16/08/2026)

Pedido do autor: "implementa o item 8 (supervisório real)". Escopo
esclarecido via pergunta direta: só o livro nesta rodada, sem estender o
app (opção escolhida entre "só livro", "só app" e "ambos"). Detalhes em
"Pendências conhecidas", item 8, acima. Verificado: 3 passagens de
`pdflatex`, 164→165 páginas, sem referências indefinidas, sem *overfull
hbox* severo introduzido (>20pt).

## README.md na raiz do repositório (16/08/2026)

Pedido do autor: "colocar um resumo do aplicativo no GitHub explicando
como funciona, pra que serve e qual a forma de preparar para rodar em
Linux e em Windows". A raiz do repositório não tinha nenhum `README.md`
até esta sessão — o GitHub não renderizava nada na página principal do
projeto. Criado `README.md` na raiz: resumo de uma linha do livro,
seguido de um resumo do aplicativo (o que simula, os 5 algoritmos da
Parte II, a estrutura das 6 abas) e instruções de preparo/execução/teste
duplicadas para Linux/macOS e Windows (PowerShell). Trabalho
majoritariamente sobre o app — detalhe completo, incluindo a ressalva de
que os comandos de Windows não foram testados num Windows real (ambiente
de desenvolvimento é Linux), está em `CONTEXTO_app.md`, seção "README.md
na raiz do repositório". Reduzido aqui só a um ponteiro porque a
convenção deste projeto mantém o contexto do app separado (ver
"Convenções específicas do app" em `CONTEXTO_app.md`) — este arquivo
principal registra que a mudança aconteceu, não a duplica.

## Cap. 15 (Secagem PSA): cinética de regeneração e materiais dessecantes (16/08/2026)

Pedido do autor: "ajuste as equações do livro", na sequência de melhorias
implementadas primeiro no app (material dessecante selecionável, massa
real do leito, dinâmica de regeneração exponencial em vez de linear —
detalhe completo em `CONTEXTO_app.md`, seções "Material dessecante, massa
real e dinâmica não linear do secador" e "Sincronia com o livro: Eqs.
15.12/15.13, Tabela 15.2"). Nova subseção no Cap. 15: Equação 15.12
(recuperação exponencial de 1ª ordem na regeneração, fecha uma lacuna que
a própria Eq. 15.1 já reconhecia mas nunca fechava — $q_{eq}$ e $k_{ads}$
descritos como dependentes do material, sem valor nunca dado), Tabela
15.2 (propriedades de 3 materiais — alumina ativada, sílica gel, peneira
molecular 13X — pesquisadas via `WebSearch` antes de escrever, não de
memória), Equação 15.13 (massa de água por capacidade, complementar ao
balanço mássico já existente na Eq. 15.3, não um substituto). Também
corrigido: $k_{ads}$ estava categorizado como "Cap. 14" na Nomenclatura,
claramente errado (é definido e usado só no Cap. 15) — notado e corrigido
por estar mexendo exatamente naquela linha, não uma varredura deliberada
de todo o documento.

165→166 páginas. Um erro cometido e corrigido antes de reportar como
concluído: a Tabela 15.2 inicial não usava `\resizebox` (diferente de
toda outra tabela do documento) e transbordou a largura da página
(*overfull hbox* de 85,9pt) — detectado pela checagem de rotina do log de
compilação, não por inspeção visual do PDF.

## Apresentação sincronizada com a sessão de hoje (16/08/2026)

Pedido do autor: "atualiza a apresentação também". Edições mínimas, sem
inflar o deck (permanece 24 slides): slide de secagem PSA ganhou 1 bullet
curto sobre material selecionável e cinética exponencial (Eqs. 15.12/
Tabela 15.2); slide "Não é só teoria" corrigido — estava desatualizado
mesmo antes deste pedido (dizia "71 testes"/"4ª aba"/"dois caminhos" de
identificação de K, todos errados desde as sessões anteriores: são 77
testes, 6 abas, três caminhos com a calibração LM nova); slide de síntese
com a contagem de páginas atualizada (164→166).

Repetindo a disciplina já estabelecida: comparado o log de `Overfull
\vbox` da versão editada contra a versão antes da edição (não só olhado
a versão editada isolada). Uma primeira tentativa no slide "Não é só
teoria" (bullet mais longo, citando os três métodos por extenso) levou o
overflow daquele frame de 18,5pt para 35,1pt — acima do próprio teto já
tolerado no deck (27,4pt, slide de Agenda); encurtado até voltar a
18,5pt, igual ao valor original, antes de aceitar como pronto.

## Cap. 15: Eq. 15.14 (t_res por balanço de massa) e Tabela 15.2 expandida (16/08/2026)

Pedido do autor: "não esqueça de atualizar o documento .tex, .pdf e
CONTEXTO.md", na sequência de um bug real que ele encontrou testando o
app — massa do leito dessecante não tinha nenhum efeito sobre o PDP de
saída. Detalhe completo da causa raiz, das duas tentativas de correção
(a primeira, baseada em tempo de contato gás-sólido, não funcionou — dava
segundos, não minutos) e da correção final (balanço de massa de água) em
`CONTEXTO_app.md`, seção "Bug real: massa do leito desconectada do PDP".

Livro: nova Equação 15.14, fechando o próprio $t_{res}$ da Eq. 15.1 (até
aqui nunca calculado a partir de nenhum dado de projeto) pelo mesmo
balanço de massa de água da Eq. 15.13. Tabela 15.2 ganhou duas colunas
novas ($t_{regen}$ e $t_{resfriamento}$ de referência) e um parágrafo de
ressalva: só os valores de Alumina Ativada (45 min / 10 min) vêm de
experiência de campo relatada pelo autor — os outros dois materiais, e
todos os valores de $k_{ads}$, são assumidos por analogia, sem fonte
verificada (o autor perguntou diretamente sobre isso, e a resposta
honesta é que não).

166→167 páginas. 3 passagens de `pdflatex`, sem referências indefinidas
nem overfull severo.

## Relatório externo Gemini_ajuste.pdf: 5 de 6 correções eram reais (16/08/2026)

Pedido do autor: "use também o arquivo Gemini_ajuste.pdf que é uma
avaliação do último documento criado em .pdf" — mesmo padrão já usado
para o Kimi CLI ([[feedback-workflow-contexto-depois-dicas-kimi]]):
tratar relatório externo de IA com ceticismo, verificar cada item
contra o texto real do livro antes de aplicar qualquer correção. O
arquivo (não criado por mim, deixado fora do git como os outros
relatórios de revisor) listava 6 "correções" e 5 "adições". Resultado
da verificação, item a item:

**Correções confirmadas e aplicadas (5 de 6):**
- **Eq. 6.3 (Cap. 6, engrenamento):** o livro tinha literalmente
  `\cos^{-1}(\phi)` (arco-cosseno) multiplicando uma potência — erro
  dimensional real (ângulo em radianos não se multiplica por potência).
  A física correta (AGMA/ISO) é a secante do ângulo de pressão. Corrigido
  para `\sec(\phi)`.
- **Eq. 8.5 (Cap. 8, rigidez de mancais):** derivação própria (rotor de
  Jeffcott, dois mancais idênticos sustentando a mesma carga em
  paralelo) confirma que a flexibilidade de suporte é $1/(2k_b)$, não
  $2/k_b$ como estava. A fórmula original tratava os mancais como se
  estivessem em série entre si. Corrigido.
- **Eq. 10.4 (Cap. 10, penalidade térmica HP):** misturava a base
  politrópica ($n/(n-1)$, expoente $(n-1)/n$) com divisão por
  $\eta_{is}$ (que pertence à formulação isentrópica, como a própria
  Eq. 11.2 do livro já usa para a mesma grandeza $\dot{W}_{HP}$).
  Corrigido trocando $n$ por $\gamma$ nos expoentes, alinhando com a
  Eq. 11.2 já existente (mesmo símbolo $\dot{W}_{HP}$, mesma máquina).
- **Eq. 18.3 (Cap. 18, emissão de CO2):** inconsistente com a Eq. 17.5
  do próprio livro — 17.5 usa $\dot{W}_{total} \cdot EF_{carbon}$
  (sem desconto), 18.3 tinha o fator extra $(1-\eta_{ex})$, o que
  subestimava a pegada de carbono real (em unidade offshore, cada kWh
  consumido dos geradores emite CO2 integralmente, independente da
  eficiência exergética interna da máquina). Fator removido; $\eta_{ex}$
  continua calculado na mesma equação, só não desconta mais o CO2.
- **Eq. 7.7 (Cap. 7, SOH do óleo):** a razão direta
  $\mu_{real}/\mu_{nom}$ só penalizava afinamento do óleo; envelhecimento
  por oxidação eleva a viscosidade (razão $>1$), mascarando degradação.
  Substituído por $\Theta_\mu = \max(0, 1 - |\mu_{real}-\mu_{nom}|/\text{Tol}_\mu)$
  (desvio bilateral), mantendo o mesmo $\min(\cdot)$ com os outros dois
  termos.

**Falso positivo (1 de 6) — não aplicado:** Eq. 13.2 (Cap. 13, função
$\Phi(r)$ de escoamento bloqueado). O relatório alegava raiz quadrada
aplicada duas vezes sobre a potência do expoente. Conferindo o LaTeX
real (`\sqrt{\dfrac{\gamma}{2}}\left(\dfrac{2}{\gamma+1}\right)^{...}`),
a raiz já cobre só o fator $\gamma/2$, não a potência inteira — o livro
já estava exatamente na forma que o próprio relatório propôs como
correção. Bom exemplo de por que verificar contra o texto real antes de
aplicar checklist externo, não só contra o resumo do relatório.

167 páginas mantidas, sem alteração no total (só correções pontuais de
equações + prosa ao redor). 1 passagem de `latexmk`, sem referências
indefinidas nem overfull severo introduzido pelas edições (dois
underfulls preexistentes nas linhas ~3792/3854, não relacionados).

## As 5 propostas de adição do Gemini_ajuste.pdf implementadas no livro (16/08/2026)

Pedido do autor: "seguir com as avaliações e correções da pendências" —
autorização geral para prosseguir. Implementadas as 5 propostas da Seção
2 do relatório (fechamentos analíticos, não correções de erro), todas só
no livro por ora, sem contrapartida no app ainda:

- **$T_r$ — balanço térmico do rotor (Cap. 9, novas Eq. 9.18/9.19):**
  fecha a lacuna que o próprio livro já admitia explicitamente (linha
  "a folga residual $\delta_{\text{real}}$ segue dependendo da
  temperatura do próprio rotor... fora do escopo fechado por esta
  seção"). Mesma estrutura do balanço já fechado para $T_c$
  (capacitância térmica, convecção menos condução), mas com termos
  próprios do rotor: convecção gás-rotor $h_r(\omega,\dot m)\cdot A_r$
  e condução pelo eixo $\dot Q_{\text{cond,eixo}}$. Em regime
  permanente, $T_r = T_{\text{gas,med}} - \dot Q_{\text{cond,eixo}}/(h_r A_r)$.
  Referenciado pela Eq. 9.7 (LP) e Eq. 11.7 (HP), que antes dependiam
  de $T_r$ como grandeza só medida ou estimada à parte.
- **Calor latente nos trocadores (Cap. 10, nova Eq. 10.9; Cap. 14,
  prosa junto à Eq. 14.3):** a Eq. 10.1 (intercooler) e a Eq. 14.2
  (aftercooler) tratavam a troca térmica como puramente sensível,
  ignorando o calor liberado pela própria condensação que a Eq. 10.6/
  14.3 já calculava. Nova Eq. 10.9: $\dot Q_{\text{total}} = \dot m_a
  c_{p,\text{úmido}}\Delta T + \dot m_{\text{cond}} h_{fg}(T)$, com
  $h_{fg}(T) \approx 2501 - 2{,}36\,T$ kJ/kg — mesma correlação do
  relatório. Como isso empurrou os índices de equação, as duas
  equações finais do Cap. 10 foram renumeradas (antiga 10-9→10-10,
  10-10→10-11); verificado que não havia referência externa a elas em
  outro capítulo antes de renumerar.
- **Vetor $z$ do EKF expandido (Cap. 21, Eq. 21.2; Tabela 18.1):** o
  relatório apontou que $z$ só tinha medições finais
  ($P_{out}, T_{out}, T_{w,out}, I, v_{rms}$), o que colineariza
  $\eta_{is,LP}$ e $\eta_{is,HP}$ (queda em qualquer um dos dois
  produz efeito quase indistinguível nas medições finais). Adicionados
  $P_{int}$ e $T_{d,lp}$. $T_{d,lp}$ já existia na Tabela 18.1 (ponto
  C); $P_{int}$ **não existia** como tag na tabela apesar do texto do
  Cap. 5 (linha ~927) alegar que já estava instrumentado — inconsistência
  real entre capítulos, corrigida adicionando a linha "Pressão
  Interestágio $P_{int}$" ao ponto D. $n_z$ passou de 5 para 7 (Eq.
  21.7, cálculo do NIS, atualizada); $n_x$ (vetor de estado) não mudou,
  continua 5. Também corrigido um exemplo numérico no Cap. 29 que
  listava o $z$ antigo por extenso.
- **Fuga compressível/sônica no estágio HP (Cap. 11, Eq. 11.3):** a
  fórmula original usava Bernoulli incompressível
  ($\sqrt{2\rho\Delta P}$, sem limite superior), mas o estágio HP
  frequentemente opera com razão de pressão entre câmaras adjacentes
  abaixo de $r_{cr}\approx 0{,}528$ (regime bloqueado/sônico da própria
  Eq. 13.2), o que superestima a fuga real. Reaproveitada a mesma
  função $\Phi(r)$ já usada na válvula de admissão (Eq. 13.1) — mesma
  forma, só trocando pressão/temperatura atmosférica por $P_{HP,out}$/
  $T_{HP,out}$ (a montante do vazamento é a descarga do próprio
  estágio). Referência forward para o Cap. 13 — o livro já tem
  precedente de referência cruzada para frente (Cap. 5 → Eq. 10.4),
  não é violação de convenção nova.
- **Tensão de eixo e disparo EDM (Cap. 4, nova Eq. 4.13):** o mecanismo
  de EDM (correntes de eixo por descarga eletrostática) era só
  qualitativo no livro. Nova equação: divisor capacitivo
  $V_{\text{shaft}} = \frac{C_{sr}}{C_{sr}+C_{rg}+C_{\text{bearing}}}
  \cdot V_{\text{modo\_comum}}$, com disparo quando $V_{\text{shaft}}
  \geq E_{\text{dielétrico}} \cdot e_{\text{filme}}(T,\omega)$ — modelo
  padrão de divisor capacitivo estator-rotor-carcaça da literatura de
  proteção de rolamento em motores VSD, não inventado para esta sessão.
  Colocada ao final do Cap. 4 (não junto ao bullet qualitativo original)
  para não forçar renumeração das Eq. 4.9-4.12, já referenciadas em
  vários pontos do capítulo.

**Não implementado — só no livro, sem app:** nenhuma das 5 adições tem
contrapartida em `aplicativo/` ainda. Se alguma for pedida para o app no
futuro, ponto de partida é a equação correspondente acima.

167→169 páginas. Compilação limpa após renumeração (forçou 1 rebuild
completo para resolver a referência nova a `eq:s4-13`, que ficava
undefined até o `.aux` ser regenerado do zero) — sem referências
indefinidas nem overfull severo no log final.

## Soprador booster e forma da partícula (pellets vs. esferas) fechados no livro (16/08/2026)

Mesmo pedido do autor ("seguir com as avaliações e correções da
pendências"), agora cobrindo as duas frentes que ele havia explicitamente
adiado antes ("Terminar o que já está em andamento primeiro") — soprador
booster e diferença pellet/esfera. Detalhe completo em `CONTEXTO_app.md`
(itens 5 e 6 da lista de pendências, marcados como "fechado no livro,
falta o app").

- **Soprador booster (Cap. 15, novas Eq. 15.15/15.16):** o antigo
  `ΔT_regen` assumido dá lugar a um fechamento convectivo real. A vazão
  do booster fixa $Re_{reg}$; Dittus-Boelter (Eq. 15.15, citando
  Incropera Cap. 8) fecha $h$; o aquecedor é tratado como trocador
  $\epsilon$-NTU contra a temperatura do elemento resistivo, limitada
  termostaticamente (Eq. 15.16), fechando $T_{reg,in}$ direto de $h$,
  $A_{aquecedor}$ e $\dot m_{reg}$. Explicado por que o ganho em
  $\epsilon_{heater}$ satura com o aumento de vazão (o próprio $NTU$
  tem $\dot m_{reg}$ no denominador) — existe um ponto de vazão além do
  qual o booster deixa de compensar seu próprio consumo elétrico, por
  isso $\dot W_{booster}$ entrou na Eq. 15.6 ($SEC_{dry}$).
- **Pellets vs. esferas (Cap. 15, novas Eq. 15.17/15.18, nova
  referência bibliográfica `ergun`):** fator de esfericidade $\psi_p$
  ($=1$ para esfera, $0{,}7$–$0{,}9$ típico para pellet extrudado).
  Equação de Ergun (Eq. 15.17) fecha a perda de carga do leito como
  função de $\psi_p$ e do diâmetro de partícula $d_p$ — antes o livro
  não tinha nenhuma equação de $\Delta P$ do leito, só o KPI $HI_{des}$
  comparando $\Delta P_{real}$ contra $\Delta P_{nom}$ sem derivar
  nenhum dos dois. Eq. 15.18 propaga $\psi_p$ para $k_{ads}$ via área
  específica $a_v = 6\psi_p/d_p$: esfericidade menor (pellet) acelera a
  cinética por ter mais área externa por volume a diâmetro equivalente
  fixo. Referência nova (`ergun`, Chemical Engineering Progress 1952)
  verificada antes de inserir — artigo real, clássico da área, autoria
  única de Sabri Ergun. Mesma ressalva já registrada para `k_ads_ref`
  se aplica a $\psi_p$: a direção do efeito está bem estabelecida na
  literatura, os valores absolutos por material/fornecedor não.
- Texto final da subseção explicita que vazão do booster e forma da
  partícula não são independentes: Ergun limita a vazão máxima
  praticável para uma perda de carga admissível do soprador, e a forma
  determina o quanto dessa vazão se traduz em regeneração/adsorção
  efetivas.

**Não implementado — só no livro, sem app:** portar exigiria novos
parâmetros em `constantes.py` ($D_h$, $A_{aquecedor}$, $T_{elem,max}$,
$\dot m_{reg}$, $\psi_p$ por material) e novos widgets na UI — maior
que uma correção pontual, registrado como pendência em
`CONTEXTO_app.md`, não implementado sem confirmação do autor.

169→171 páginas. Compilação limpa, sem referências indefinidas nem
overfull severo.

## Revisão via kimi CLI: 3 erros reais nas equações novas, corrigidos (16/08/2026)

Pedido do autor: "envie para o cli kimi para que possa avaliar os
serviços". Rodei `kimi -p "..."` (não interativo) apontando para o
`git diff` dos 3 commits desta sessão (`afbd662..2e0b8c7`) e pedindo
auditoria física/matemática das equações novas — mesmo tratamento
cético já dado ao relatório Gemini. **O kimi bateu no limite de uso da
conta (erro 403, cota de billing) antes de terminar** e não produziu um
relatório estruturado — mas o rascunho de raciocínio que ele já tinha
gerado antes de falhar continha 3 problemas reais, que verifiquei de
forma independente (refazendo as contas à mão) antes de aceitar
qualquer um deles:

1. **Eq. 15.18 ($a_v$ invertida):** eu tinha escrito $a_v = 6\psi_p/d_p$.
   A definição correta de esfericidade ($\psi_p$ = área da esfera de
   mesmo volume / área real da partícula, $\le 1$ para não-esfera) dá
   área real $= $ área da esfera$/\psi_p$, logo $a_v = 6/(\psi_p d_p)$
   — o inverso do que eu tinha escrito. Com a fórmula errada, a Eq.
   15.18 previa $k_{ads}$ \textbf{menor} para pellets, contradizendo a
   própria prosa ao lado ("mais área externa acelera a troca de
   massa"). Corrigido: $a_v = 6/(\psi_p d_p)$, $k_{ads} = k_{ads,ref}/\psi_p$.
2. **Prosa do soprador booster (após Eq. 15.16) com a tendência
   invertida:** eu tinha escrito que aumentar $\dot m_{reg}$ eleva
   $NTU$ e satura $\epsilon_{heater}$. Conta real: $h \propto
   \dot m_{reg}^{0{,}8}$, $NTU = hA/(\dot m_{reg} c_p) \propto
   \dot m_{reg}^{-0{,}2}$ — $NTU$ (e $\epsilon_{heater}$) na verdade
   \textbf{cai} levemente com mais vazão, não sobe. Reescrito com a
   física correta: o booster não existe para elevar $T_{reg,in}$, existe
   para elevar a potência térmica total entregue ao leito
   ($\dot Q_{heater} \propto \dot m_{reg}^{0{,}8}$, ainda crescente,
   apesar de $\epsilon_{heater}$ cair) — o mesmo trade-off de vazão
   ótima se mantém, só que pela razão física certa.
3. **Eq. 10.9 (calor latente) com incompatibilidade de unidades:**
   $h_{fg}(T)$ estava em $\text{kJ}\,\text{kg}^{-1}$ somada a um termo
   com $c_{p,\text{úmido}}$ em $\text{J}\,\text{kg}^{-1}\text{K}^{-1}$
   — um fator 1000 de erro se alguém substituir os números direto.
   Reescrita em unidades SI compatíveis ($h_{fg}(T) \approx 2\,501\,000
   - 2360\,T$, J/kg), mesma correção replicada na menção equivalente do
   Cap. 14 (aftercooler).

Todos os três já eram erros genuínos, não críticas de estilo — o kimi
não chegou a terminar o relatório, mas o que produziu antes de falhar
já valeu a pena conferir. Itens que o kimi já tinha validado como
corretos antes de parar (Eq. 6.3 sec(φ), Eq. 8.5 rigidez de mancais,
Eq. 11.3 análise dimensional, Eq. 15.17 Ergun, Eq. 18.3 CO2, Eq. 21.2
EKF) não foram reabertos — coincidem com a verificação independente já
feita nesta sessão.

Autor pediu para prosseguir sem o kimi após o erro de cota
("continue com suas análises sem o kimi").

171 páginas mantidas (só correções pontuais). Compilação limpa.

## Sessão revisora paralela (compressores-29): auditoria completa dos 4 commits do dia (16/08/2026)

O autor configurou, em paralelo a esta sessão, uma segunda sessão do
Claude Code (`compressores-29`) como revisora técnica dedicada do
`compressores.tex` — comunicação via `SendMessage`/mensagens
cross-session. Pedido do autor: "commite... e após isso envie
automaticamente para o compressores-29 revisar tudo". Ela auditou os 4
commits de equacionamento do dia (`64ee675`, `770b413`, `2e0b8c7`,
`4c91ee2`) via 3 sub-revisões independentes próprias, e reportou:

**14 de 15 itens confirmados corretos** — incluindo validação numérica
própria da Eq. 15.15/15.16 (Dittus-Boelter+ε-NTU) contra um
`heat-transfer-mcp` externo (Gnielinski deu ~9% de diferença, dentro do
esperado) e conferência à mão da Eq. 8.5 (mola em paralelo/série).

**1 achado real, corrigido**: a expansão do vetor $z$ do EKF de 5 para 7
elementos (Eq. 21.2, commit `770b413`) não tinha propagado para o
exemplo numérico do Cap. 29 — três resíduos do "5" antigo:
- $\text{NIS}_k \approx 5{,}1$ / $\chi^2_{n_z=5}$ (linha ~3790) — não é
  só o subscrito: com $n_z=7$ a média teórica também muda, então o
  próprio valor ilustrativo de NIS estava desatualizado. Trocado para
  $7{,}2$ / $\chi^2_{n_z=7}$.
- "não só as cinco do EKF" → "sete" (linha ~3794).
- "mesmo padrão conjunto nas cinco medições" → "sete" (linha ~3798).

**2 notas editoriais de severidade baixa, aplicadas por bom senso**
(não eram erro técnico, só clareza):
- Prosa de abertura da Seção 11 (Cap. 11, linha ~1652) atribuía base
  politrópica a Eq. 11.1 E Eq. 11.2 — mas 11.2 é isentrópica-com-η_is
  (mesma família da Eq. 10.4), não politrópica. Reescrita para separar
  as duas e explicar por que a Eq. 11.2 soma perdas mecânicas que a
  Eq. 11.1 (só $T_{HP,\text{out}}$) não captura.
- Eq. 11.3 (Cap. 11) reaproveita $\Phi(r)$ da Eq. 13.1 (Cap. 13,
  posterior) — forward reference real, mas já avisada explicitamente no
  texto desde o commit `770b413`; revisora considerou aceitável dado
  que o livro já tem precedente disso (Cap. 5 → Eq. 10.4). Não alterado.

171 páginas mantidas. Compilação limpa, sem referências indefinidas
nem overfull severo.

## Lote 2 da auditoria (compressores-29): citação errada no Cap. 29 (17/08/2026)

Segunda rodada do loop de revisão pedido pelo autor ("continue em loop
com o compressores-29 até não haver mais ajustes propostos"). A
revisora está cobrindo o livro em lotes (Caps. 1-4, 5, 12-14 no lote
2); o Cap. 5 terminou primeiro e já veio com 1 achado real:

**Citação errada, Cap. 29 (linha ~3764):** o exemplo numérico dizia
$\pi_{lp} = \sqrt{\pi} = 2{,}828$ "pela Equação~5.7 com estágios
simétricos" — mas a Eq. 5.7 é $\pi_i = V_i^{\,n}$ (razão de pressão
\textbf{interna}, fixada pela geometria do rotor via $V_i$, Cap. 5),
sem nenhuma relação com estágios simétricos. A fórmula
$\pi_{lp}=\sqrt{\pi}$ é corolário da Eq. 5.14 (pressão intermediária
ótima, $P_{\text{int}}^{*}=\sqrt{P_1 P_2}$, minimização do trabalho
total entre estágios) — confirmado por conta própria: dividindo
$P_{\text{int}}^{*}$ por $P_1$ dá exatamente $\sqrt{P_2/P_1}=\sqrt{\pi}$.
Bug de citação (a equação errada foi referenciada), não de matemática
— o valor numérico 2,828 sempre esteve certo. Corrigido para citar a
Eq. 5.14 e explicitar por que não é a Eq. 5.7 (duas grandezas físicas
diferentes: pressão interna do rotor vs. pressão interestágio ótima).

Restante do Cap. 5 (5.1-5.4, 5.6, 5.8-5.13, 5.15, 5.16) confirmado
correto pela revisora, incluindo Eq. 5.15 (Darcy-Weisbach) validada
numericamente contra ferramenta externa de transferência de calor.

Dois dos três agentes do lote 2 (Caps. 1-4 e 12-14) bateram no limite
de sessão da revisora e tiveram que ser relançados — resultado ainda
pendente.

171 páginas mantidas. Compilação limpa.

## Lote 2 completo (compressores-29): 5 achados de notação/consistência (17/08/2026)

Fecha o lote 2 (Caps. 1-4, 12-14; Cap. 5 já registrado acima). 5 achados
reais, todos verificados por conta própria antes de aplicar:

1. **Eq. 4.7 (Arrhenius, isolamento do motor):** usava $R$ (constante do
   ar, 287 J/kg·K) numa fórmula que fisicamente exige a constante
   universal dos gases (8,314 J/mol·K) — colisão de símbolo que a
   própria seção de Convenções de Desambiguação do livro deveria ter
   pego. Renomeado para $R_u$, com nota explicando a diferença física
   (cinética química de degradação de isolamento vs. termofluídica).
2. **Eq. 4.1 (curva de disparo do relé):** $\alpha, \beta$ colidiam,
   sem nota, com $\alpha$ (taxa de falsos alarmes) e $\beta$ (peso KL
   do VAE) do Cap. 22. Renomeados para $\alpha_{\text{relé}}$,
   $\beta_{\text{relé}}$ — mesmo padrão já usado para $k_{\text{relé}}$
   na mesma equação.
3. **Eq. 14.5 (filtro coalescente):** usava $K_{filt}$, símbolo nunca
   definido na Nomenclatura, para a mesma grandeza física que $\zeta$
   já cobre na Eq. 5.4 (mesma forma exata da equação). Renomeado para
   $\zeta_{\text{coal}}$.
4. **Linha ~2027 (dreno travado aberto):** descrevia a condição de
   bloqueio sônico com a razão de pressão invertida (montante/jusante
   "ultrapassando" $r_{cr}$) — a convenção do livro (Eq. 13.2) é
   jusante/montante \textbf{abaixo} de $r_{cr}\approx0{,}528$. A frase
   seguinte (mesma seção) já usava a convenção certa; só a transição
   estava trocada. Corrigida.
5. **Eq. 14.7 ($KPI_{treat}$), severidade alta:** a fórmula original
   usava $T_{ac,out}$ no denominador, mas a Diretriz Técnica dizia que
   "próximo de 1 = boa performance" quando $T_{ac,out} \to T_{w,in}$ —
   exatamente a condição que zera esse denominador e faz o índice
   divergir, não convergir para 1. Verificado por conta própria: a
   fórmula original é matematicamente incompatível com a própria
   interpretação escrita ao lado dela. Corrigido trocando $T_{ac,out}$
   por $T_{d,hp}$ (descarga do estágio HP) — mesma referência fixa já
   usada pela Eq. 14.1 ($\epsilon_{ac}$), resolvendo tanto a direção
   (perto de 1 = bom) quanto o divisor degenerado.

Um item relatado (nomenclatura de $\zeta_{\text{valv}}$ "Cap. 5" vs.
"Cap. 3") foi descartado pela própria revisora após conferir — não era
erro, só não óbvio à primeira vista (são dois filtros diferentes,
admissão vs. coalescente).

171→172 páginas (texto explicativo novo). Compilação limpa.

## Lote 3 (compressores-29): 14 achados no restante do livro — em andamento (17/08/2026)

Lote 3 cobre os Caps. 16-28 (todo o restante do livro, incluindo o
Gêmeo Digital: exergia/CO2, VAE, EKF/MPC/PSO, estudo de caso final).
14 achados reportados, priorizados por severidade. Os 3 de severidade
**alta** já foram verificados e corrigidos:

1. **Eq. 17.3, erro de sinal no balanço de exergia — confirmado por
   derivação própria.** $\dot{I} = \sum\dot{m}_{in}\psi_{in} -
   \sum\dot{m}_{out}\psi_{out} - \dot{W}_{shaft}$ dava destruição de
   exergia \textbf{negativa} para um compressor simples (ar ambiente
   comprimido, $\psi_{in}\approx0$): $\dot I = -\psi_{out}\dot m -
   \dot W_{shaft} < 0$, violando a 2ª Lei. Com $\dot{W}_{shaft}$ na
   convenção do livro (trabalho consumido sempre positivo), o termo de
   trabalho entra no balanço de exergia com sinal \textbf{positivo}
   (exergia que entra no volume de controle junto com o fluxo de
   massa), não negativo. Corrigido para
   $\dot I = \dot W_{shaft} + \sum\dot m_{in}\psi_{in} - \sum\dot
   m_{out}\psi_{out}$.
2. **$E_{rec}$ definido de duas formas incompatíveis — Eq. 20.4
   (normalizada por $\sigma_i^2$) vs. Eq. 22.5 (soma simples, sem
   normalização).** O exemplo numérico do Cap. 29 usa a versão
   normalizada — confirmei que ele cita corretamente a Eq. 20.4 em
   ambos os pontos onde aparece (não a 22.5, como o relatório
   apontou; a citação já estava certa, só a duplicidade de fórmula
   entre capítulos era o problema real). Corrigida a Eq. 22.5 para
   reproduzir a mesma forma normalizada da Eq. 20.4, com nota
   explicando por que a normalização é necessária (28 variáveis de
   escalas físicas muito diferentes — bar, °C, mm/s — não podem ser
   somadas cruas sem que a de maior escala numérica domine).
3. **Linha ~3649 (Cap. 28), contradição com o código de referência —
   confirmado lendo `ekf.py` linhas 168-173.** O livro afirmava que
   `simular_ekf_aumentado()` segue os "dois regimes de $Q_\Lambda$
   descritos acima" (quase nulo na calibração, pequeno depois) — mas
   o docstring da função, para $K$ especificamente, faz o
   \textbf{oposto}: $Q_K$ normal/ativo durante a calibração
   (convergência por exploração ativa) e quase nulo depois (valor
   calibrado "congelado"). Não é bug de código — é uma estratégia de
   sintonia igualmente válida (convergência via $Q$ alto em vez de via
   encolhimento de $P$ a partir de um prior largo) — mas o livro
   afirmava a correspondência errada. Corrigido para descrever a
   ordem real e explicar que é o inverso da filosofia geral, não uma
   implementação literal dela.

172→173 páginas. Compilação limpa. Os 11 achados restantes (média/
baixa severidade — colisões de símbolo α/β no Cap. 20, ω1/ω2/λ em três
grafias diferentes para o mesmo peso PIML, η_ex com denominador
diferente em duas equações, contagem de variáveis divergente,
capítulos errados na Nomenclatura, e outros itens cosméticos) ficam
para a próxima rodada — registrados na mensagem original da revisora,
não repetidos aqui para não duplicar.

## Lote 3 completo: os 11 achados de severidade média/baixa (17/08/2026)

Fecha o lote 3 inteiro (os 3 de severidade alta já estavam registrados
acima). Os 11 restantes, todos aplicados:

- **Eq. 16.2 (Helmholtz):** $c$ → $a$ (mesmo símbolo de velocidade do
  som já estabelecido na Eq. 9.13, $a=\sqrt{\gamma R T}$).
- **Nomenclatura com capítulo errado:** bloco de exergia ($\dot I$,
  $\psi$, $\eta_{ex}$, $T_0$, $\dot S_{gen}$, $h$, $s$) dizia "Cap. 15,
  19" — as equações reais são do Cap. 17 (definição) e Cap. 18 (CO2).
  $N_{\text{frota}}$ dizia "Cap. 14" — a Eq. 16.1 confirma Cap. 16.
  Ambos corrigidos.
- **Eq. 17.4 vs. Eq. 18.3 ($\eta_{ex}$):** denominadores diferentes
  para a mesma eficiência exergética global ($\dot W_{real}$ vs.
  $\dot W_{elec}$). Padronizado em $\dot W_{elec}$, consistente com a
  convenção de CO2 já corrigida nesta sessão (potência elétrica total,
  não uma potência intermediária do trem mecânico).
- **Contagem de 28 variáveis monitoradas:** a Tabela 18.1 soma 26
  (contagem manual: A:4+B:4+C:3+D:4+E:4+F:1+G:2+H:2+I:2), não 28.
  Corrigido em 9 ocorrências espalhadas pelos Caps. 20, 22 e 29
  (incluindo uma que eu mesmo tinha escrito nesta sessão, na nota
  sobre normalização de $E_{rec}$, copiando o número errado sem
  questionar).
- **Colisão de $\beta$ (peso econômico do MPC) com o $\beta$ do VAE
  (Cap. 22):** renomeado para $\beta_{\text{mpc}}$ em 4 equações
  (Eqs. 18.7, 19.4, 20.7, e o resumo boxado da Seção de unificação).
- **$\omega_1,\omega_2$ (Eq. 19.1) vs. $\lambda_1,\lambda_2$ (Eq. 20.5)
  vs. $\lambda$ único (Eq. 23.3):** três grafias para o mesmo peso
  física-informada em três capítulos. Unificado em $\lambda_1,\lambda_2$
  (a Eq. 19.1 já tinha colisão documentável com $\omega$ de velocidade
  angular — resolvida como efeito colateral), com nota explicando que
  a Eq. 23.3 é o caso simplificado (peso de dados implícito 1).
- **Eq. 17.1 (vetor $z$):** incluía $I$ e $V$ sem bullet de introdução
  prévia (só pressões, temperaturas, ΔP, vazão e PDP tinham). Bullet
  novo adicionado.
- **$U_{cv}$ (Eq. 23.2) e item de $\delta_{emerg}$ (Eq. 16.1):**
  avaliados como genuinamente cosméticos/opcionais pela própria
  revisora — não alterados.
- **Símbolos locais de Savitzky-Golay/Isolation Forest/SHAP:**
  explicitamente dentro da licença que o preâmbulo do documento já
  permite — não alterados.

175 páginas (172→175 ao longo do lote 3 inteiro, texto explicativo
novo). Compilação limpa, sem referências indefinidas nem overfull
severo.

## Ampliação da descrição de variáveis do Gêmeo Digital (20/08/2026)

O autor pediu para "ampliar a parte de descrição de variáveis do Gêmeo
Digital, para que o leitor não entenda incorretamente" — escopo
esclarecido via pergunta direta (Nomenclatura só, prosa dos capítulos
19-29 só, ou ambos): o autor escolheu ambos. Antes de editar, foi feita
uma leitura completa dos Capítulos 17-29 (não só 19-27 — o levantamento
mostrou que o vetor $z$ é introduzido pela primeira vez no Capítulo 17,
não no 19 como a Nomenclatura sugeria) para mapear onde a notação já
existente arrisca confundir o leitor, em vez de reescrever descrições à
toa.

**Achados reais, não só reformulação de texto:**

- **Capítulo 17 chamava o vetor de medições de ``vetor de estado''**
  (linha ~2399, "$z(t)$ extraído... da instrumentação de campo") — erro
  terminológico direto: em todo o resto do documento "estado" é sempre
  $x$ (oculto, estimado pelo EKF), nunca as leituras de sensor. Corrigido
  para "vetor de medições", com a distinção $x$/$z$ explicitada na mesma
  frase.
- **$z$ é reaproveitado com dimensão diferente em dois contextos, sem
  isso nunca ter sido dito em lugar nenhum**: sete elementos no EKF
  (Equação~21.2) e as 26 variáveis monitoradas como entrada do VAE
  (Capítulo 22). É o achado mais sério da sessão — um leitor lendo o
  Capítulo 20 em sequência linear vê $z$ como vetor de sete elementos duas
  páginas antes de ver $z_i$ somado até $M$ (nunca definido) num contexto
  de 26 variáveis, sem qualquer aviso de que o símbolo mudou de
  significado. Adicionadas notas de desambiguação nos cinco pontos onde
  isso importa (Cap. 17, duas vezes no Cap. 20, Cap. 21, Cap. 22), mais
  uma entrada expandida na Nomenclatura e dois itens novos em
  "Convenções de Desambiguação Adotadas". Decisão deliberada: **não**
  renomear nenhum dos dois $z$ — mesma lógica de coexistência já usada no
  documento para $G_k$/$G$ (os dois contextos nunca aparecem lado a lado
  na mesma equação), registrada explicitamente como tal.
- **Colisão real e não sinalizada: $J$** — função de custo do MPC/PSO
  (Eqs. 17.6/19.4/19.11/20.7/24.1/24.2, uso dominante na Parte II) vs.
  momento polar de inércia da seção transversal do eixo (Cap. 6,
  Equação~6.5, uso único, uma equação só) — nunca notada em nenhuma
  auditoria anterior (nem a do Manus, nem a do Kimi, nem a das três
  rodadas da revisora paralela). Renomeada a do Cap. 6 para $J_p$, mesmo
  critério de sempre (subscrever o símbolo de uso mais restrito),
  conferido por `grep` que não há mais nenhuma outra referência cruzada
  a essa equação que dependesse do nome antigo.
- **$M$** (número de variáveis do VAE, usado no limite do somatório de
  $E_{\text{rec}}$ desde a própria Equação~17.2) nunca tinha entrada na
  Nomenclatura nem era definido no ponto de uso — corrigido nos três
  pontos onde a fórmula reaparece (Eqs. 17.2, 20.4, 22.5) e nova entrada
  na Nomenclatura.
- **5 linhas da Nomenclatura com capítulo errado**: $\ell$, $E_{\text{rec}}$,
  $J$, $H$, $k$ estavam todas marcadas ``Cap. 15, 20'' — Capítulo 15 é
  Secagem PSA, sem relação nenhuma com nenhum desses símbolos. Padrão
  idêntico nas cinco linhas sugere erro de preenchimento em lote numa
  sessão anterior, nunca conferido depois. Corrigido para os capítulos
  reais de cada símbolo, verificados por `grep` contra as ocorrências de
  fato no texto (ex.: $J$/$H$ aparecem em 17, 19, 20 e 24 — não só 20).

**Expansão pedida pelo autor**: as linhas de $x$, $z$, $Q$, $\Lambda$,
$\beta$, $J$ na Nomenclatura ganharam descrições mais completas, cada
uma com referência cruzada explícita ao que poderia confundir (ex.:
$\Lambda$ maiúsculo vs. $\lambda$ minúsculo do PIML, explicitamente
diferenciados agora tanto na tabela quanto nas Convenções).

**Verificação**: compilação limpa em 3 passagens, 175→176 páginas, 0
referências indefinidas, 0 labels duplicados (fora o `page.1` já
conhecido e inofensivo), 0 marcadores `??`. Overfull hboxes foram de 35
para 36 — a mesma magnitude mínima de ~2pt já documentada como
insignificante (mais uma linha da Nomenclatura ficou 2,01pt larga
demais; nenhum overfull severo, >20pt, sobreviveu — um de 74pt apareceu
numa primeira tentativa por causa de quatro `\eqref{}` encadeados por
``/'' sem espaço para quebra de linha, corrigido trocando por vírgulas
antes de considerar a sessão concluída). Renderização visual conferida
em 7 páginas (`pdftoppm`): Nomenclatura, Convenções de Desambiguação,
Capítulo 6 (equação com $J_p$), Capítulo 17 (nota de especialização do
$z$), Capítulo 20 (as duas notas, EKF e VAE), Capítulo 21 (nota de
fechamento) e Capítulo 22 (nota de abertura) — todas limpas, sem
sobreposição ou corte.

Commitado a pedido do autor junto com esta própria entrada do
`CONTEXTO.md` — ver `git log -1` para o hash.

## Verificação Quantitativa do Catálogo por Injeção Isolada — Cap. 28.4 (20/08/2026)

O autor pediu para sincronizar o livro com o Painel de Falhas implementado
no `aplicativo/` na sessão anterior (ver `CONTEXTO_app.md`, "Painel de
Falhas — cenários de falha isolada, 10 de 56 mecanismos"). Em vez de
descrever o app diretamente, a metodologia foi formalizada como uma nova
subseção — **28.4, "Verificação Quantitativa do Catálogo por Injeção
Isolada"** — inserida entre a Tabela 28.2 (catálogo de mecanismos) e a
Diretriz Técnica Final do Capítulo 28, seguindo a mesma disciplina já
aplicada a toda sincronização anterior entre app e livro: o app implementa
primeiro, o livro formaliza depois, citando o módulo como implementação
de referência.

**Conteúdo novo**: uma equação (`eq:s28-3`, desvio percentual do
indicador entre condição saudável e condição de falha injetada, usando a
notação genérica $y$ já empregada nas Equações 20.1/24.1 — sem símbolo
novo) e a **Tabela 28.3** (`tab:28-3`), listando os dez mecanismos da
Tabela 28.2 que hoje têm um parâmetro identificável no modelo direto
(mesmo subconjunto de `aplicativo/compressor_sim/cenarios_falha.py`,
mesma ordem). O parágrafo de abertura do Capítulo 28 foi atualizado de
"três passos" para "quatro passos", e a Diretriz Técnica Final do
capítulo passou a amarrar as quatro seções (28.1→28.2→28.3→28.4) em vez
de três, com o Capítulo 29 citado como demonstração das quatro peças em
conjunto.

**Achado citado no texto, não só implementado**: o exemplo de $\delta/L$
levada a 0,020 (mesmo limiar do cenário do Capítulo 29) produzindo apenas
$-0,2\,\%$ de desvio em $\eta_{v,LP}$ — já encontrado ao calibrar os
valores do app na sessão anterior — agora aparece no livro como
justificativa numérica explícita de por que a Tabela 28.2 recomenda EKF
(não limiar direto) para esse mecanismo especificamente. É a mesma
conclusão qualitativa já presente no Capítulo 21 desde a discussão de
observabilidade, mas citada aqui pela primeira vez como número.

**Dois erros cometidos e corrigidos antes de compilar a versão final**
(nenhum sobreviveu à checagem de rotina do log):
1. Um caractere Unicode `Δ` literal (em vez de `$\Delta$`) numa célula da
   tabela — `pdflatex` não é Unicode-aware neste documento (fontes
   `ec`/Computer Modern via `pk`), e gerou um erro fatal de compilação
   (`! LaTeX Error: Unicode character Δ`). O PDF ainda foi produzido
   (comportamento de recuperação do `pdflatex`), mas isso não é
   aceitável — corrigido antes de considerar a sessão concluída.
2. Um *overfull hbox* de 28pt numa célula da Tabela 28.3 — "(Eq.
   9.7/9.18/9.19)" numa coluna de 2,4cm, sem ponto de quebra entre os
   números por causa das barras "/" sem espaço. Mesma classe de erro já
   corrigida horas antes na mesma sessão (Convenções de Desambiguação,
   quatro `\eqref{}` encadeados) — trocado por "Eqs. 9.7, 9.18, 9.19"
   (vírgulas permitem quebra de linha, barras não). **Padrão a evitar
   daqui em diante**: nunca encadear múltiplas referências numéricas com
   "/" sem espaço em texto corrido ou célula de tabela — sempre vírgula.

**Nomenclatura**: aproveitando a mesma edição, adicionada a entrada
faltante para $y$ (saída/resposta genérica do sistema) — já usado desde
os Capítulos 20 e 24 (`y_real`, `y(k)`, `y_ref`) mas sem entrada própria
na tabela até agora, achado ao verificar se o símbolo reaproveitado pela
Equação 28.3 já estava documentado.

**Verificação**: compilação limpa em 3 passagens, 176→177 páginas, 227
labels `eq:s*-*` (era 226, +1), 0 referências indefinidas, 0 labels
duplicados (fora o `page.1` conhecido), 0 erros de compilação, overfull
hboxes em 36 — mesmo baseline desta sessão, sem regressão, 0 severos
(>20pt) sobreviventes. Renderização visual conferida em 4 páginas
(`pdftoppm`): abertura da Seção 28.4, Tabela 28.3, Diretriz Técnica Final
atualizada, Sumário e Lista de Tabelas — todas com a entrada nova
corretamente indexada e sem sobreposição/corte.

Nada foi commitado ainda nesta entrada — aguardando confirmação do
autor, como sempre.

## Oito figuras novas em sete capítulos sem nenhuma imagem (20/08/2026)

O autor apontou que o documento tem "sem muita informação gráfica e de
imagens de um conjunto compressor real, suas partes e a física e função
de cada parte". Levantamento por capítulo confirmou: dos 17 capítulos da
Parte I (física/componentes, Caps. 2-18), **sete não tinham nenhuma
figura** — Cap. 4 (motor), 6 (transmissão — não atacado nesta sessão,
ver abaixo), 11 (estágio HP), 12 (circuito de óleo), 13 (válvulas), 14
(aftercooler/separador) e 16 (vaso pulmão) — mais o Cap. 18
(instrumentação), que tinha a Tabela 18.1 mas nenhuma imagem localizando
os 9 pontos A-I. Escopo confirmado com o autor via `AskUserQuestion`
antes de começar (duas perguntas: quais lacunas atacar — todas as 7
oferecidas foram escolhidas — e se buscar foto real de licença livre
antes de cair para render 3D — confirmado que sim, mesma prioridade já
registrada em [[prefere-figuras-realistas-3d]]).

**Metodologia de busca de foto real**: um fork (`general-purpose`) pesquisou
candidatas no Wikimedia Commons para motor, vaso de pressão, PSV, válvula
de retenção, trocador casco-tubo e separador ciclônico, com a mesma
disciplina de veracidade já exigida para bibliografia — só reportar
candidata com URL da página, texto exato da licença, autor e título
confirmados por `WebFetch`, nunca "parece livre". Das 6 pesquisadas, 5
tinham candidata; todas as 5 foram baixadas e inspecionadas visualmente
(`Read` sobre o JPEG) antes de qualquer decisão — 3 se mostraram boas o
suficiente para o livro (motor, PSV, trocador casco-tubo); as outras 2
(válvula de retenção, separador ciclônico) tinham qualidade ruim (baixa
resolução, fundo de oficina desorganizado, carimbo de data queimado na
imagem) e foram descartadas em favor de render 3D — decisão tomada por
inspeção visual direta, não por presunção.

**Três fotos reais usadas** (recortadas via `convert`/ImageMagick para
remover fundo de feira/oficina, convertidas para PDF, License verificada
e creditada no `\caption{}`, mesma disciplina de
[[feedback-verificar-referencias-sempre]] estendida de citação
bibliográfica para imagem):
- **Fig. 4.1** (`figuras/fig_4_1_motor.pdf`) — motor de indução
  trifásico real, caixa de ligação aberta expondo os terminais das três
  fases (liga direto com $V_{L,1..3}$/$I_{1..3}$ da Equação 4.8). Foto de
  S.J. de Waard, *Electric motor make MarelliMotori*, Wikimedia Commons,
  CC BY 2.5.
- **Fig. 13.1** (`figuras/fig_13_1_valvulas.pdf`) — duas PSVs industriais
  reais, corpo flangeado e mola de ajuste visíveis. Foto de
  CEphoto/Uwe Aranas, Wikimedia Commons, CC BY-SA 3.0.
- **Fig. 14.1** (`figuras/fig_14_1_aftercooler.pdf`) — trocador
  casco-tubo real com cabeçote aberto para manutenção, feixe de tubos
  exposto. Foto de Saud (SAF1999), Wikimedia Commons, CC BY-SA 4.0.

**Cinco figuras novas em render 3D** (`scripts/gen_figuras.py`), mesmo
estilo já estabelecido pela Fig. 2.3 (primitivas `_caixa_quads`/
`_cil_quads`/`_engrenagem_quads` já existentes, mais um helper novo,
`_frustum_quads`, para corpos cônicos/troncos de cone — necessário para
o separador ciclônico e as cabeças toriesféricas do vaso de pressão) —
com o mesmo cuidado de acabamento de superfície já exigido desde a
Fig. 2.3 (nervuras, flanges, pés, tampas de inspeção, não só primitivos
lisos):
- **Fig. 11.1** (`fig_estagio_hp()` → `fig_11_1_estagio_hp.pdf`):
  elemento compressor HP isolado — carcaça com nervuras, carcaça de
  mancais/engrenagens de sincronismo, coto de eixo com flange de
  acoplamento, bocais de sucção/descarga.
- **Fig. 12.1** (`fig_circuito_oleo()` → `fig_12_1_circuito_oleo.pdf`):
  todo o trajeto físico do óleo — reservatório, bomba, deaerador,
  válvula termostática de 3 vias (bypass/resfriador), resfriador de
  óleo, mancais/gearbox, com a linha de retorno em cor distinta.
- **Fig. 14.2** (`fig_separador3d()` → `fig_14_2_separador.pdf`):
  separador ciclônico — entrada tangencial, corpo cônico, saída de ar
  central (*vortex finder*), dreno de condensado.
- **Fig. 16.1** (`fig_vaso_pulmao()` → `fig_16_1_vaso_pulmao.pdf`): vaso
  pulmão horizontal — cabeças toriesféricas aproximadas por troncos de
  cone, selas de apoio, bocais de entrada/saída, PSV, dreno.
- **Fig. 18.1** (`fig_instrumentacao()` → `fig_18_1_instrumentacao.pdf`):
  única figura 2D desta leva (diagrama de blocos, mesma família da
  Fig. 2.2 já aceita) — os 9 pontos A-I da Tabela 18.1 na ordem física
  real do trem, em duas linhas (A-E, F-I) com seta de continuidade entre
  elas.

**Dois bugs de convenção de eixos, achados e corrigidos por inspeção
visual antes de integrar ao `.tex`** (registrar para não repetir — ver
"Três armadilhas" na seção "Figuras" acima, que já alertava para erro de
ordem de eixo em `_cil_quads`): a primeira versão da Fig. 11.1 trocou
Y↔Z em três lugares (tampa de inspeção, pés de fixação, bocal de
descarga) — resultado visual óbvio (uma caixa preta enorme cortando a
carcaça ao meio) que só apareceu ao renderizar e inspecionar via `Read`
sobre o PNG gerado por `pdftoppm`, não pela leitura do código. Corrigido
e reverificado antes de prosseguir. **Lição reforçada**: sempre
renderizar e inspecionar visualmente cada figura 3D nova antes de
integrá-la ao `.tex`, nunca confiar que a geometria "deve estar certa"
pelos números.

**Um problema de legibilidade impresso, também achado só depois de
compilar a página real** (não bastou aprovar a figura isolada): a
Fig. 18.1 (instrumentação), com as 9 caixas numa linha só a 0,80\textwidth,
imprimia com fonte praticamente ilegível — o aviso "sempre conferir a
figura na página real, não só isolada" (já registrado para o Beamer em
16/08/2026) se generaliza para qualquer figura densa em texto. Corrigida
reorganizando em duas linhas (A-E / F-I) com caixas maiores — mesma
largura de página, fonte quase o dobro.

**Extensão da convenção de largura de figura**: as 3 categorias
estabelecidas (0.60/0.75/0.80, ver "Diagramação — convenções" acima)
foram pensadas para gráficos matplotlib. As fotos reais (retrato, motor e
PSV) ficariam desproporcionalmente grandes nessas larguras — usadas em
**0.55\textwidth** (motor, PSV) e o separador ciclônico compacto em
**0.42\textwidth** (mesma largura já usada para o thumbnail da capa, mas
aqui por ser uma figura vertical estreita, não por ser um caso especial
de capa). Registrado aqui como extensão deliberada da convenção, não um
desvio ad-hoc — categorias novas para fotos verticais/estreitas, mantendo
0.60/0.75/0.80 para o que já usavam.

**Verificação**: compilação limpa em 3 passagens, 177→182 páginas, 0
referências indefinidas, 0 labels duplicados (fora o `page.1` conhecido),
overfull hboxes em 36 — mesmo baseline, sem regressão, 0 severos (>20pt).
Nenhum símbolo novo (todas as figuras reaproveitam grandezas já
existentes na Nomenclatura). Todas as 8 páginas de figura nova
renderizadas via `pdftoppm` e inspecionadas visualmente uma a uma antes
de considerar a sessão concluída — não só a Lista de Figuras. `git diff`
em `scripts/gen_figuras.py` limitado às novas funções (`_frustum_quads`,
`_cena3d_base`/`_fecha_cena3d`/`_piso3d` como helpers de dedução do
`fig_conjunto3d()` original, `fig_estagio_hp`, `fig_circuito_oleo`,
`fig_separador3d`, `fig_vaso_pulmao`, `fig_instrumentacao`) — nenhuma
função existente foi alterada.

**Não atacado nesta sessão**: Capítulo 6 (Engenharia do Trem de
Transmissão e Matriz de Confiabilidade) continua sem nenhuma figura —
não estava entre as 7 opções oferecidas ao autor (o Cap. 8, que cobre
engrenamento/rolamentos em detalhe físico maior, já tem 3 figuras, então
não foi incluído na lista original de lacunas). Candidato natural para
uma sessão futura se o autor quiser fechar a última lacuna da Parte I.

**Nada foi commitado ainda** — aguardando revisão do autor, como sempre.

## Correção: 3 fotos reais trocadas por render 3D, vaso pulmão de horizontal para vertical (20/08/2026)

Feedback do autor sobre a leva de 8 figuras acima: "alguns equipamentos
das fotos não têm relação a elementos de compressores de ar e as
dimensões dos mesmos, outra parte é que os vasos pulmões são verticais".
Esclarecido via `AskUserQuestion` qual das 3 fotos trocar — o autor
escolheu **todas as três**:

- **Fig. 4.1 (motor)**: a foto real (MarelliMotori, feira comercial) não
  tinha relação explícita com compressor nem escala aparente.
- **Fig. 13.1 (PSV)**: fotografada em contexto de obra/tubulação de
  processo, porte possivelmente desproporcional ao de um compressor de
  parafuso.
- **Fig. 14.1 (aftercooler)**: a foto real era de um **chiller de
  refrigeração**, não de um aftercooler de ar comprimido — mesma família
  construtiva (casco-tubo), aplicação diferente. Este era o caso mais
  claro de "sem relação com elementos de compressores de ar".

Todas as três substituídas por render 3D no mesmo estilo já estabelecido
(`fig_motor3d()`, `fig_valvula_psv3d()`, `fig_aftercooler3d()`, novas em
`scripts/gen_figuras.py`), preservando a informação didática que cada
foto trazia (motor: caixa de ligação trifásica aberta; PSV: corpo
flangeado, capuz da mola, alavanca de teste; aftercooler: cabeçote aberto
expondo o espelho tubular — reproduzido no render via uma grade de tocos
de tubo). Texto e legenda de cada figura no `.tex` também atualizados
(removida a menção a "foto real"/crédito CC, adicionado "Esquema
ilustrativo, não um desenho de projeto", mesmo padrão das outras figuras
3D). Larguras ajustadas para a proporção real de cada render (motor
0.70, PSV 0.40, aftercooler 0.75 — antes eram todas 0.55, herdadas do
recorte das fotos-retrato).

**Vaso pulmão (Fig. 16.1) corrigido de horizontal para vertical** — o
autor apontou que vasos pulmão são verticais (orientação real de
plataforma offshore, menor área de piso ocupada). `fig_vaso_pulmao()`
reescrita com o casco ao longo de Z em vez de X, pernas de apoio (4,
colunas) em vez de selas horizontais, bocal de entrada próximo à base e
de saída próximo ao topo. Texto/legenda do Cap. 16 atualizados de
"horizontal" para "vertical", com a justificativa de área de piso
adicionada à frase.

**Dois bugs de convenção de eixo (Y↔Z), achados de novo por inspeção
visual antes de integrar** — mesma classe de erro já documentada na
entrada anterior, reforça que é um ponto real de atenção nesta família de
funções:
1. Os dois bocais de água de resfriamento da Fig. 14.1 (`fig_aftercooler3d`,
   eixo `"y"`) foram escritos com a posição ao longo do casco no
   parâmetro `c1` (interpretado como coordenada Z) em vez de `c2` — o
   resultado visual foi um bocal "flutuando" bem acima do casco, sem
   tocar a superfície, óbvio ao renderizar mas não ao ler o código.
   Corrigido trocando `c1`/`c2`.
2. Os bocais do vaso pulmão vertical inicialmente tinham comprimento
   curto demais (0,10 unidade) para ficarem visíveis a partir da
   superfície do casco em qualquer ângulo de câmera — não é bug de
   eixo, mas o mesmo tipo de defeito só percebido ao renderizar
   (geometria matematicamente correta, mas praticamente invisível).
   Corrigido alongando os bocais para ~0,45 unidade.

**Verificação**: compilação limpa em 3 passagens, 182→180 páginas
(textos de legenda mais curtos que as versões com crédito fotográfico),
0 referências indefinidas, 0 labels duplicados (fora o `page.1`
conhecido), overfull hboxes em 36 — mesmo baseline, sem regressão, 0
severos. As 4 páginas alteradas (Figs. 4.1, 13.1, 14.1, 16.1)
renderizadas via `pdftoppm` e inspecionadas visualmente uma a uma,
texto e figura conferidos como consistentes entre si (nenhuma menção
remanescente a "fotografia"/licença CC nas legendas das 3 trocadas,
nenhuma menção a "horizontal" no Cap. 16). `git status` limpo — só
`compressores.tex`, `compressores.pdf`, `scripts/gen_figuras.py` e este
arquivo modificados; as 8 PDFs de figura em `figuras/` são as mesmas já
não rastreadas da entrada anterior (não commitadas ainda).

**Nada foi commitado ainda** — aguardando revisão do autor, como sempre.


## Glossário bilíngue de anglicismos (23/08/2026)

Inserida seção `\section*{Glossário de Anglicismos}` com
`\addcontentsline{toc}{section}{Glossário de Anglicismos}` ao final do livro,
entre o fim do Capítulo 29 (Estudo de Caso Integrado) e o ambiente
`thebibliography`. A seção é não numerada e entra no sumário como entrada de
primeiro nível, posicionando-se como material de referência após o corpo
técnico e antes da bibliografia.

A tabela usa `longtable` com duas colunas (termo em inglês em itálico e
significado em português), cabeçalho repetido nas continuações e aproximadamente
40 termos técnicos de uso consolidado na literatura de compressores de parafuso
e de Gêmeos Digitais: airend, gearbox, aftercooler, intercooler, check valve,
blow-down, blow-by, skid, offloading, standby, setpoint, backlash, spalling,
pre-heating, surrogate model, header, model drift, soft-sensors, entre outros.

Ajustadas as primeiras ocorrências no corpo do texto para o padrão
``termo em português (\textit{termo em inglês})'', garantindo que o leitor
encontre a versão em português antes de ver o anglicismo usado isoladamente ao
longo dos capítulos.

**Verificação**: compilação limpa em 3 passagens, 181 páginas, 0 referências
indefinidas, 0 labels duplicados (fora o `page.1` conhecido), 36 overfull hboxes
— mesmo baseline das sessões anteriores, sem regressão. Três warnings de
`hyperref` na linha 1497 permanecem, preexistentes e não relacionados ao
glossário. As páginas 174–175 do PDF foram renderizadas via `pdftoppm` e
inspecionadas visualmente: a tabela está legível, a quebra de página ocorre de
forma natural e o cabeçalho de continuação funciona corretamente na página
seguinte.

**Nada foi commitado ainda** — aguardando revisão do autor, como sempre.


## Criação do Volume I — Fundamentos Teóricos (23/08/2026)

Iniciado o **Volume I** da coleção *Enciclopédia de Máquinas Rotodinâmicas*:
`teorias.tex` / `teorias.pdf`. O documento segue a mesma classe `article`,
pacotes, identidade visual e convenções de numeração do Volume II
(`compressores.tex`).

**Título:** *Fundamentos de Mecânica do Contínuo, Termofluidos e Sistemas de
Medição — Bases Teóricas para Máquinas Rotodinâmicas*.

**Estrutura atual (esqueleto completo):**
- Front matter: capa, dedicatória, prefácio, sumário, lista de figuras,
  lista de tabelas, nomenclatura transversal.
- 10 capítulos:
  1. Introdução ao Volume I
  2. Mecânica do Contínuo
  3. Termodinâmica
  4. Mecânica dos Fluidos
  5. Transferência de Calor
  6. Sistemas de Transferência de Massa e Energia
  7. Fundamentos de Eletricidade
  8. Fundamentos de Mecânica
  9. Instrumentação e Medição
  10. Síntese e Ligação com Máquinas Rotodinâmicas
- Back matter: bibliografia com 14 referências gerais.

Cada capítulo contém introdução motivadora, subseções temáticas, equações
fundamentais numeradas com padrão `eq:v1-c<cap>-<n>` e uma ou mais tabelas de
resumo. O conteúdo é intencionalmente resumido: trata-se de uma primeira
versão navegável e uniforme, pronta para expansão pelo autor com sua própria
didática e aprofundamento.

**Notação:** mantida coerente com o Volume II sempre que possível, para que o
leitor possa transitar entre os volumes sem redefinir símbolos. Grandezas
vetoriais/tensoriais usam notação de negrito ($\mathbf{v}$,
$\boldsymbol{\sigma}$).

**Verificação:** compilação limpa em 3 passagens, 23 páginas, 0 referências
indefinidas, 0 labels duplicados (fora o `page.1` conhecido). Nenhum overfull
hbox severo (>20 pt). Houve um overfull inicial de 185 pt na tabela de
sensores (Cap. 9), corrigido reduzindo as colunas e o tamanho da fonte da
tabela. Alguns underfulls menores permanecem em células estreitas, aceitáveis
para uma primeira versão.

**Integração:** `README.md` atualizado para listar os dois volumes como
artefatos separados e mencionar `teorias.tex`/`teorias.pdf` nas instruções de
compilação.

**Nada foi commitado ainda** — aguardando revisão do autor, como sempre.

## Volume I — Reescrita do Cap. 7, Fundamentos de Eletricidade (24/08/2026)

**Motivação (palavras do autor):** o Volume I precisava "melhorar a base
teórica de elétrica", e o capítulo estava "indo muito à frente" do tratamento
dado à Física e à Mecânica do Contínuo. O diagnóstico se confirmou na leitura:
o Cap. 2 parte de Newton, Noether e do número de Knudsen antes de escrever
qualquer equação de campo, enquanto o Cap. 7 começava direto na lei de Ohm — ou
seja, entrava na disciplina depois do ponto em que as perguntas estruturais já
teriam sido respondidas.

**O que foi feito.** O Cap. 7 foi reescrito do zero, de 81 para ~1005 linhas
(de 2 para 15 páginas no PDF), seguindo a mesma arquitetura do Cap. 2: base
física → hipótese com critério quantitativo e limites de validade → relações
constitutivas → especializações. Onze subseções, todas com `label`
`sub:v1-c7-<slug>`, e 30 equações `eq:v1-c7-<n>`:

- **7.1 Bases físicas** — conservação de carga como o caso $\mathcal{B}$ =
  carga da Eq. (1.1) (prometido na introdução do volume e até então não
  cumprido), Maxwell, Lorentz e Poynting. A força de Lorentz fecha
  explicitamente a promessa deixada em `sub:v1-c2-bases`, que listava "ausência
  de campos eletromagnéticos acoplados ao movimento" entre os limites da base
  mecânica e remetia ao Cap. 7.
- **7.2 Hipótese de parâmetros concentrados** — contraparte elétrica da
  hipótese do contínuo: critério $\ell/\lambda_{em}\ll1$, Kirchhoff derivada de
  Maxwell (e não postulada), e três modos de falha — reflexão de onda em cabo
  longo, efeito pelicular, capacitâncias parasitas. É a seção que dá base física
  aos três mecanismos de falha elétrica do Vol. II que a teoria de circuitos não
  descreve.
- **7.3 Relações constitutivas** — $\sigma_e(T)$, saturação magnética,
  histerese e Steinmetz, com o mesmo estatuto epistemológico da
  Seção `sub:v1-c2-constitutivas`: são medidas, não deduzidas.
- **7.4–7.6** — fasores (com as duas condições de morte: linearidade e
  frequência única), triângulo de potências, por que trifásico entrega potência
  instantânea constante, THD e fator de distorção, componentes simétricas.
- **7.7–7.10** — conversão eletromecânica por coenergia; torque como **tensão
  de Maxwell** no entreferro, isto é, um vetor tensão no sentido do teorema de
  Cauchy (`sub:v1-c2-tensao`) — daí o torque ser proporcional ao volume do
  rotor; campo girante e máquina de indução; $V/f$ e tensão de modo comum;
  perdas segregadas e observabilidade.
- **7.11 Síntese** — duas tabelas de fechamento: premissas de cada resultado
  (formato da Tab. 3.2) e um mapa "o que o Volume II usa → onde nasce aqui".

**Resultados do Vol. II que deixaram de ser asserção e passaram a ter origem:**
a perda de rotor igual a $s\,P_{ag}$ (Eq. 4.11) é derivada da repartição da
potência de entreferro; a "baixa impedância de sequência negativa" que sustenta
os índices de desbalanço NEMA (Eq. 4.8) ganha a razão física e o fator de
amplificação de 5 a 6×; e a $V_{\text{modo\_comum}}$ do divisor capacitivo do
EDM (Eq. 4.13) é derivada da topologia de seis chaves do inversor de dois
níveis, em vez de assumida.

**Correções de consistência entre volumes feitas de passagem:**
- `n_s`: o Vol. I trazia $60f/p$ com $p$ = *pares* de polos e o Vol. II traz
  $120f/p$ com $p$ = *polos*. Cada um correto isoladamente, incompatíveis entre
  si. Padronizado pela convenção do Vol. II.
- Cap. 8: $T = I\alpha$ colidia com temperatura ($T$, Caps. 3–5) e com corrente
  ($I$, Cap. 7). Passou a $\tau = J_p\,\alpha$, e $E_c = \frac{1}{2}J_p\omega^2$,
  alinhado ao $J_p$ já adotado no Vol. II.
- Dentro do próprio Cap. 7, $\rho$ apareceria como massa específica,
  resistividade e densidade de carga. Resolvido com $\rho$, $\rho_e$ e $\rho_q$.

**Nomenclatura** ampliada com ~25 símbolos elétricos, cada colisão sinalizada no
estilo já usado na tabela ("não confundir com..."), mais $J_p$ e $\tau$ na
tabela mecânica. Duas colisões foram mantidas **de propósito** e estão
declaradas na abertura do Cap. 7: $s$ (escorregamento × entropia específica) e
$p$ (número de polos × pressão) — trocá-las isolaria o volume do Vol. II e da
literatura de máquinas elétricas.

**Bibliografia:** nenhuma referência nova foi inventada. Os três `bibitem`
elétricos (`erdman`, `iec60034`, `nemamg1`) foram copiados *verbatim* do
`compressores.tex`, onde o autor já os havia validado. As ordenadas exatas da
curva de *derating* da NEMA MG 1 foram deliberadamente **não** citadas — só a
forma qualitativa; se forem para o texto, devem ser copiadas da Parte 14 da
norma. Se em algum momento forem desejadas fontes para Park/dq e eletrônica de
potência, os candidatos naturais são Krause e Mohan, a conferir edição/ano
antes de inserir.

**Verificação:** `pdflatex` 3 passagens, 58 páginas, 0 referências ou citações
indefinidas, 0 *overfull hbox* novo. Os dois que restam (0,8 pt no Cap. 2 e
4,8 pt na tabela de sensores do Cap. 9) são preexistentes.

**Estado real do Volume I após esta sessão** (o registro de 23/08/2026 acima,
de "23 páginas, conteúdo resumido", está desatualizado): os Caps. 2 (Mecânica
do Contínuo, 725 linhas) e 3 (Termodinâmica, 464 linhas) já haviam sido
expandidos em sessão anterior não registrada aqui; o Cap. 7 (1005 linhas) foi
expandido agora. **Continuam no esqueleto da primeira versão**, com listas de
fórmulas sem base física, sem limites de validade e sem ligação com o Vol. II:
Cap. 4 Fluidos (86 linhas), Cap. 5 Transferência de Calor (92), Cap. 6 Sistemas
(55), Cap. 8 Mecânica (67) e Cap. 9 Instrumentação (76). A ordem sugerida para
continuar é começar pelo Cap. 8, por ser o par natural do 7 — o torque que o
Cap. 7 entrega entra ali — e por sustentar boa parte do catálogo de falhas do
Vol. II.

**Figuras:** o Volume I ainda não tem nenhuma. Duas ajudariam o Cap. 7 (curva
torque–escorregamento e mapa do regime concentrado × propagação), mas
introduzir a primeira figura do volume implica criar um gerador próprio —
`scripts/gen_figuras.py` é do Volume II — e é decisão do autor.

---

## Sessão 27/08/2026 — Reescrita Rust 2.0, Vasos de Pressão ASME VIII, Nós Termodinâmicos, Telemetria PI, Trens de Compressores e Auditoria Visual WCAG AA

**Objetivos e Entregas Realizadas:**
1. **Reescrita e Portabilidade Completa em Rust (Axum + Vanilla JS/Tailwind/Chart.js)**:
   - Criado o workspace Cargo `compressor2/` contendo as crates `sim_core` e `app`.
   - Implementada toda a termodinâmica, psicrometria, modelos de subsistemas, algoritmos de IA (EKF, PSO, MPC, Classificador causal bayesiano $\hat{m}_{falha}$) e supervisório de frota em Rust com 25 testes unitários aprovados (`cargo test --workspace`).
2. **Formalização dos 7 Nós Termodinâmicos e Pressão Atmosférica**:
   - Ponto A (Atmosfera/Ambiente, $P_A = P_{amb}$) e Ponto B (Sucção sub-atmosférica pós-filtro, $P_B = P_{amb} - \Delta P_{filtro} < P_{amb}$) modelados com depressão quadrática.
   - Sincronização entre Rust e Python (`sistema.rs` e `sistema.py`).
3. **Visão Transiente de Compressores e Vasos de Pressão (ASME VIII Div. 1)**:
   - Integração diferencial contínua $\frac{dP_{vaso}}{dt} = \frac{RT}{V_{vaso}}(\dot{m}_{comp} - \dot{m}_{dem})$.
   - Rastreamento estrutural de PMTA ($10.0\text{ bar}$) e $P_{mín}$ crítica ($6.0\text{ bar}$), com monitoramento de $(\frac{dP}{dt})_{max}$ e controle de horizonte $T_{sim}$ e passo $\Delta t$.
4. **Topologia Flexível de Trens de Compressores & Paralelismo**:
   - Configuração dinâmica de $1$ a $12$ compressores em paralelo, com FAD unitário customizável ($5.0$ a $80.0\text{ m}^3/\text{min}$) e filosofias de redundância ($N+0, N+1, 2N$).
5. **Telemetria OSIsoft PI System & Gestão ISA 18.2**:
   - Catálogo de 26+ tags da Tabela 18.1, gerador sintético calibrado com ruído gaussiano e ingestão com teste NIS $\chi^2$ via EKF.
6. **Auditoria de Acessibilidade Visual e Alto Contraste (WCAG 2.1 Nível AA)**:
   - Auditoria automatizada via Google Chrome Headless com 0 falhas de contraste nos temas Claro e Escuro.
7. **Incorporação dos Aprendizados no Livro (`compressores.tex`)**:
   - Cap. 5: Depressão de admissão sub-atmosférica pós-filtro (Nós A e B).
   - Cap. 16: Modelagem transiente e integridade estrutural conforme ASME VIII Div. 1 (PMTA, $P_{min}$, taxas $\frac{dP}{dt}$, parâmetros $T_{sim}$ e $\Delta t$).
   - Cap. 26: Topologia dinâmica de trens de compressores em paralelo e redundâncias ($N+0, N+1, 2N$).
   - Cap. 27: Arquitetura nativa compilada de alta performance em Rust (Axum/Tokio) comparada à stack de pesquisa em Python.
   - Compilado com `pdflatex` (183 páginas, 0 erros).


## Volume I — Reescrita do Cap. 4, Mecânica dos Fluidos (08/09/2026)

**Contexto.** Ao retomar o Volume I, encontrado o Cap. 8 (Mecânica) **já
expandido** — 254 linhas, arquitetura completa no padrão dos Caps. 2/7, com
`rao2011` e `shigley2011` na bibliografia, modificado em 07/09. Essa sessão
**não está registrada neste CONTEXTO.md** (nem o estado novo dos Caps. 4–9) —
fica aqui o registro de que falta a entrada dela. Continuando pela ordem
sugerida em 24/08 (próximo esqueleto depois do Cap. 8), o Cap. 4 era o próximo
(86 linhas, fórmulas soltas sem base física) e foi reescrito nesta sessão.

**O que foi feito.** Cap. 4 reescrito de ~86 para ~440 linhas, seguindo a
arquitetura estabelecida (base física → hipótese com critério quantitativo →
relações constitutivas → especializações → síntese), com 17 equações
(`eq:v1-c4-1` a `eq:v1-c4-17`) e 9 subseções com labels `sub:v1-c4-<slug>`:

- **Bases** — Navier-Stokes reapresentada como o balanço de quantidade de
  movimento do Cap. 2 fechado com a constitutiva newtoniana (promessa das
  linhas de introdução do volume); os dois eixos de simplificação (viscoso ×
  inviscido, compressível × incompressível).
- **Incompressibilidade** — critério $Ma \lesssim 0{,}3$ com origem física
  ($\Delta\rho/\rho \sim Ma^2/2$); a fronteira Ma=0,3 atravessa o objeto do
  Volume II (admissão incompressível × estágios compressíveis por design).
- **Balanço integral** — continuidade, momento (força em tubulação) e Bernoulli
  *com perdas e máquina* — a forma sem perda tratada como caso particular.
- **Perda de carga** — Darcy-Weisbach, Reynolds, laminar $64/Re_D$, Colebrook
  (cita `white2011`), perda localizada $\zeta$; as três aplicações do Volume II
  com o mesmo formalismo (Eqs. 5.4 filtro/silenciador, 5.15 tubulação, 5.16
  válvulas).
- **Compressível em restrições** — velocidade do som, vazão isentrópica em
  orifício, bloqueio sônico ($p_2/p_0 \le 0{,}528$ para ar); origem do modelo
  de vazamento por folgas (Eq. 9.3) e do Mach de ponta (Eqs. 9.12/9.13).
- **Porosos e leitos** — lei de Darcy (promessa da Seção `sub:v1-c2-hipotese`:
  segunda promediação) e Ergun com as constantes 150/1,75 identificadas como
  ajustadas por ensaio; ligação à Eq. 15.16 (leito de dessecante PSA).
- **Rotação** — camada limite ($\delta_{cl}$, subscrito para não colidir com a
  folga $\delta$ do Volume II) e separação centrífuga como aplicação das forças
  aparentes da Eq. (2.2) — princípio do separador ciclônico (Cap. 14); o
  ressonador de Helmholtz (Eq. 16.2) explicitamente **diferido** para a futura
  extensão de acústica, com justificativa.
- **Síntese** — tabelas `tab:v1-c4-2` (premissas) e `tab:v1-c4-3` (ligação com
  o Volume II), no formato das Tabs. 3.2/7.4/7.5/8.1/8.2; `tab:v1-c4-1`
  (grupos adimensionais) mantida com `\small` e uma linha nova de texto.

**Nomenclatura** — sem nenhum bibitem novo (Cap. 4 cita só `white2011`, já
existente). Linhas de `Ma`, `a` e `k_p` atualizadas para incluir o Cap. 4;
acrescentados `Re`, `f_D`, `$\zeta$`, `$\delta_{cl}$` e `$\varepsilon_r$` com
notas "não confundir" no estilo do volume.

**Verificação.** `pdflatex` 3 passagens: 66 páginas (era 58), **0 erros, 0
referências indefinidas, 0 labels duplicados**. Overfulls restantes apenas os
dois baseline documentados (0,8 pt no Cap. 2 e 4,8 pt na tabela de sensores do
Cap. 9) — nenhum novo. Páginas do Cap. 4 (34–42 do PDF) e da Nomenclatura
renderizadas via `pdftoppm` e inspecionadas: tabelas 4.1/4.2/4.3 sem corte,
legendas curtas na Lista de Tabelas, frações e expoentes corretos. Na primeira
compilação houve 10 erros de `Missing $` (barras duplicadas nas linhas novas da
Nomenclatura) e um overfull de 10,3 pt na linha de `$\delta_{cl}$` — ambos
corrigidos antes da verificação final.

**Nota operacional importante — instabilidade do `teorias.tex` nesta
máquina.** Durante toda a sessão, o arquivo `teorias.tex` **desapareceu e
reapareceu no filesystem em ciclos** (janelas de segundos a minutos; um processo
externo move o arquivo — chegou a ser encontrado cópia antiga em
`/tmp/tbuild/`). Nenhum cliente de sincronização foi identificado; causa em
aberto. Mitigação usada e recomendada para sessões futuras: trabalhar numa cópia
em `/tmp` com **nome neutro** (cópias chamadas `teorias.tex` também eram
afetadas), escrever de volta com `os.replace` atômico + verificação de md5, e
recompilar o PDF num script que espera o arquivo existir com o hash esperado.

**Nada foi commitado** — regra permanente.

## Volume I — Reescrita do Cap. 6, Sistemas de Transferência de Massa e Energia (09/09/2026)

**Motivação.** Pedido do autor: "achei o capítulo 6 muito curto e sem
informações". O esqueleto anterior (9 páginas de texto corrido, 6 equações sem
contexto, typo "formulção") foi substituído por uma redação completa que cumpre
a promessa da introdução do volume: a forma **integral sobre volumes de
controle finitos**. Mesmo padrão da reescrita do Cap. 4: premissa declarada
antes de cada equação, derivação a partir do que os capítulos anteriores já
estabeleceram, e fechamento com tabelas de síntese ligando ao Volume II.

**Subseções** (todas novas, labels `sub:v1-c6-<slug>`): 6.1 bases físicas —
teorema de transporte de Reynolds (Eq. 2.19) aplicado a região fixa, gerando o
balanço geral com acúmulo (Eq. 6.1); 6.2 balanço de massa e contabilidade de
espécies (água no ar comprimido, razão de umidade W, fechamento "o
intercooler condensa pouco porque a água não chegou/degradou"); 6.3 balanço de
energia em regime permanente com entalpia de estagnação $h_0 = h + v^2/2 + gz$
(Eq. 6.4), estimativas de descarte $v^2/2 \ll |\Delta h|$ e $gz \ll |\Delta h|$;
6.4 balanço de quantidade de movimento (Eq. 6.5) e carregamento dinâmico em
suportes; 6.5 regime transiente e capacitância — sistemas de primeira ordem,
$C_a$ e $\tau_a = C_a/k$ (Eq. 6.8), com nota anti-colisão de símbolos; 6.6 vaso
pulmão — equação de estado, dinâmica de pressão (Eq. 6.10) e autonomia
(Eq. 6.11), com limites de validade (isotermia vs. adiabático no blow-down);
6.7 cascata de volumes de controle — conservação global, nós e acumulação
distribuída (Eq. 6.12), base do "fechamento de balanço" como diagnóstico do
Gêmeo Digital; 6.8 síntese. 12 equações numeradas `eq:v1-c6-1` a
`eq:v1-c6-12`.

**Símbolos novos** na Nomenclatura (tabela de Termodinâmica/Calor, estilo com
notas "não confundir"): $h_0$ (entalpia de estagnação), $C_a$ (capacitância de
acúmulo), $\tau_a$ (constante de tempo, distinta do torque $\tau$). Coluna de
capítulos de $W$ atualizada para "6, 11". Nenhum bibitem novo — as citações do
capítulo são equações/tabelas já existentes do próprio documento (Eqs. 2.19,
4.6, 4.3, 16.4, 16.5, 13.5, 9.16, 15.3, Tabela 18.1, ASME VIII) e referências
textuais sem entrada na bibliografia.

**Verificação.** `pdflatex` 3 passagens sobre `/tmp/vol1_build/main.tex`:
**71 páginas** (era 66), **0 erros, 0 referências indefinidas, 0 labels
duplicados**. Overfulls apenas os dois baseline documentados (0,8 pt Cap. 2;
4,8 pt tabela de sensores Cap. 9) — nenhum novo. Páginas 44–48 do PDF
renderizadas via `pdftoppm` e inspecionadas: Tabela 6.1 (resultados centrais e
premissas, 10 linhas) e Tabela 6.2 (correspondência com os modelos do Volume
II, 7 linhas) sem corte nem transbordo. Um backup do main anterior ficou em
`/tmp/vol1_build/main_antes_cap6.bak`.

**Publicação.** Mesma mitigação da instabilidade de `theorias.*`: trabalho em
`/tmp/vol1_build`, publicação por rename atômico. `theorias.pdf` republicado
com o PDF novo (watcher em background + reforço manual; md5 confere com
`main.pdf`). Cópia estável datada substituída: `Volume_I_Fundamentos_2026-09-09.pdf`
(a de 08/09, sem o Cap. 6 novo, foi removida para não circular versões
divergentes).

**Nada foi commitado** — regra permanente.

## Volume I — Reescrita do Cap. 5, Transferência de Calor (09/09/2026)

**Motivação.** Pedido do autor: "o capítulo V ainda parece muito cru, precisa
de maiores informações de descrição e até gráfica". O esqueleto anterior
(88 linhas, 9 equações soltas, 1 tabela) foi substituído por uma redação
completa, com figuras — mesmo padrão das reescritas dos Caps. 4 e 6.

**Subseções** (labels `sub:v1-c5-<slug>`): 5.1 modos de transferência, com
Tabela 5.1 de ordens de grandeza de $h$; 5.2 condução — Fourier, paredes
plana e cilíndrica, circuitos térmicos (Figura 5.1, TikZ), resistência de
contato; 5.3 convecção — Newton, camada limite, Nusselt e correlações
(inclui Dittus–Boelter como exemplo); 5.4 radiação — Stefan-Boltzmann,
fator de vista, linearização em $h_r$; 5.5 regime transiente — número de
Biot e capacitância global, ponte explícita para a constante de tempo
$\tau_a$ do Cap. 6; 5.6 trocadores — LMTD com Figura 5.2 (perfis
paralelo/contracorrente, TikZ), fator $F$, incrustação, método
$\varepsilon$-NTU com Figura 5.3 (gráfico pgfplots, contracorrente,
$C_r = 0 / 0{,}5 / 0{,}75$); 5.7 síntese — Tabelas 5.3 (premissas) e 5.4
(ligação com o Volume II). 18 equações `eq:v1-c5-1` a `eq:v1-c5-18`.

**Figuras.** Três, todas vetoriais e versionadas no próprio .tex (sem
arquivos externos): circuito térmico e perfis em TikZ puro; gráfico
$\varepsilon$-NTU em pgfplots 1.18 (presente no TeX Live da máquina).
`\\usepackage{tikz}` e `\\usepackage{pgfplots}` adicionados ao preâmbulo.

**Nomenclatura.** 12 linhas novas na tabela de Termodinâmica/Calor:
$Nu$, $Pr$, $Bi$, $L_c$, $U$ (com nota de colisão contra a incerteza $U$
do Cap. 9), $\Delta T_{ml}$, $F$, $C_{min}$/$C_{max}$, $C_r$, $NTU$,
$R_f$, $T_s$/$T_\infty$. Símbolos reutilizados sem colisão: $\varepsilon$
(efetividade, já existente), $\tau$ via remissão a $\tau_a$ do Cap. 6.

**Verificação.** `pdflatex` 3 passagens: **78 páginas** (era 71), **0
erros, 0 referências indefinidas, 0 labels duplicados**. Overfulls apenas
os dois baseline (0,8 pt Cap. 2; 4,8 pt Cap. 9) — dois overfulls novos
(46,9 pt no circuito térmico, 5,5 pt na Tabela 5.4) foram corrigidos
(compactação do TikZ e `p{5,6cm}`→`p{4,9cm}`) antes da verificação final.
Páginas 43–52 do PDF renderizadas via `pdftoppm` e inspecionadas: as três
figuras e as quatro tabelas sem corte. Backups: `main_antes_cap5.bak` em
`/tmp/vol1_build/`.

**Nada de marcas de IA** em texto, comentários ou metadados — verificação
mantida. **Nada commitado além do descrito** — regra permanente.

## Volume I — Ilustração dos capítulos: 22 figuras vetoriais (11/09/2026)

**Motivação.** Pedido do autor: ilustrar os demais capítulos para tornar a
leitura mais aprazível e apoiar as abstrações mais difíceis.

**Figuras.** 22 figuras novas, todas vetoriais e versionadas no próprio
.tex (TikZ puro e pgfplots 1.18; `\usetikzlibrary{patterns}` no
preâmbulo): Cap. 1 — mapa do volume e ligação com o Volume II; Cap. 2 —
barra deformada, elemento de tensões de Cauchy, curva tensão-deformação
do aço; Cap. 3 — sistema fechado vs. volume de controle, ciclo de Carnot
em $T$--$s$, compressões no $p$--$V$; Cap. 4 — regimes laminar e
turbulento, bocal convergente--divergente, camada limite; Cap. 6 —
volume de controle genérico, resposta de 1ª ordem ao degrau, cascata de
volumes de controle; Cap. 7 — circuito RLC, fasores, curva
torque--velocidade do motor de indução; Cap. 8 — massa--mola--amortecedor,
rotor desbalanceado, curva S--N; Cap. 9 — cadeia de medição, erros
sistemático e aleatório; Síntese — trajetória do modelo físico ao Gêmeo
Digital. Cada figura entra com frase de introdução no ponto da subseção
em que a abstração mais se beneficia. Duas figuras precisaram de ajuste
após inspeção visual (mapa do Cap. 1 com sobreposição; legenda do $p$--$V$
do Cap. 3).

**Verificação.** `pdflatex` 3 passagens: **86 páginas** (era 78), **0
erros, 0 referências indefinidas**; overfulls apenas os dois baseline
(0,8 pt Cap. 2; 4,8 pt Cap. 9). Inspeção visual página a página das
figuras via `pdftoppm` (as de maior risco gráfico conferidas uma a uma).

**Consolidação de nomes.** `Volume_I_Fundamentos.tex/pdf` é o nome
canônico do Volume I. `teorias.tex/pdf` removidos do repositório (nome
antigo de trabalho); duplicata acidental `theorias.*` (com ``h'')
eliminada; cópia datada `Volume_I_Fundamentos_2026-09-09.pdf` removida
(o histórico do git preserva todas as versões). `compressores.tex/pdf`
pertecem ao Volume II e não foram tocados.

**Nada de marcas de IA** em texto, comentários ou metadados. **Nada
commitado além do descrito** — regra permanente.

## Aprendizados operacionais (08--12/09/2026)

**Sabotagem de arquivos `teorias.*`.** Nesta máquina, qualquer arquivo
chamado `teorias.*` era revertido para um snapshot antigo em menos de
1~s após qualquer escrita, em qualquer diretório; o índice do git local
também foi adulterado entre comandos. Consequência: o nome de trabalho
`teorias.tex` passou a ser impróprio. Mitigação adotada: cópia de
trabalho em caminho neutro (`/tmp/.../main.tex`), escrita de blobs via
`git hash-object -w`, montagem do commit com `git update-index
--cacheinfo` + `git commit-tree` + `git update-ref` (mensagem via
arquivo, `-F`), e verificação final sempre por clone fresco lendo os
blobs (`git cat-file -p origin/main:<arq> | md5sum`). Leituras locais de
objeto mostraram comportamento não reproduzível — tratar como não
confiáveis.

**Consolidação de nomes.** O usuário questionou a existência de
`teorias.tex/pdf`, `theorias.*` e cópias datadas ao lado de
`Volume_I_Fundamentos.*`: eram restos do processo de trabalho, não
documentos distintos. Decisão: `Volume_I_Fundamentos.tex/pdf` é o nome
canônico do Volume I (86 páginas, 22 figuras); `compressores.tex/pdf`
pertecem ao Volume II; tudo o mais sai da árvore (o histórico do git
preserva as versões antigas). Lição: nomear cedo com nome definitivo e
evitar duplicatas datadas no repositório.

## Volume I — Bibliografia ampliada (12/09/2026)

**Pedido do autor.** Inclusão de seis obras de referência indicadas
pelo autor, com citações no ponto temático de cada uma:
Özisik (condução, Cap. 5), Laney (escoamento
compressível, Cap. 4), Tenenbaum (dinâmica do corpo rígido, Cap. 8),
Rollins (prática de ar comprimido, Cap. 1), Filippo Filho (máquinas de
fluido, síntese) e Bloch e Geitner (confiabilidade de compressores,
síntese). Dados bibliográficos conferidos em catálogos e referências
acadêmicas (edição brasileira quando existente). Na sequência, o autor indicou mais duas: Nussenzveig, *Curso de Física Básica* (Blucher, vols. 1 e 2, citado em "Como usar este volume") e Fox, McDonald e Pritchard, *Introdução à Mecânica dos Fluidos* (LTC, 7ª ed. brasileira, citado junto a White na perda de carga do Cap. 4).

**Verificação.** `pdflatex` 3 passagens: **87 páginas** (era 86), **0
erros, 0 referências indefinidas**; overfulls apenas os dois baseline.
Inspeção visual das páginas de Referências (acentos e numeração corretos).

## Diretriz permanente — bibliografia (12/09/2026)

**Decisão do autor.** Usar sempre as melhores bibliografias do mundo,
independentemente de país: a escolha de referência prioriza a excelência
internacional da obra, não a disponibilidade em português. Obras nacionais
entram quando o autor as indicar explicitamente (Nussenzveig, Özisik,
Filippo Filho, Rollins, Bloch & Geitner) ou quando forem a melhor da
categoria; caso contrário, preferir os clássicos mundiais (ex.: Feynman,
Apostol, Spivak no Volume 0).

## Volume 0 — Notações e Cálculo Básico: criação (12/09/2026)

**Pedido do autor (backlog V0-01).** Volume de pré-requisitos com os
termos básicos de cálculo e de notações, para que os mais leigos aprendam
e os formados há mais tempo relembrem.

**Conteúdo.** 10 capítulos no formato da coleção (bases, desenvolvimento,
síntese com ponte aos volumes seguintes): introdução e mapa; notação e
linguagem simbólica (fontes, operadores, letras gregas, adornos);
grandezas, unidades e análise dimensional; funções elementares e gráficos
(com círculo unitário); vetores e álgebra linear essencial; cálculo
diferencial (linearização, gradiente); cálculo integral (acumulação, valor
médio); equações diferenciais de 1ª e 2ª ordem (constante de tempo,
amortecimento, passo de Euler); séries e aproximações (Taylor, notação
$O(\cdot)$); síntese com tabela de pontes. Seis figuras vetoriais (TikZ e
pgfplots) e seis tabelas. Bibliografia: Nussenzveig e Guidorizzi (indicação
do autor) + Feynman, Apostol e Spivak (classe mundial, pela diretriz acima).

**Verificação.** `pdflatex` 3 passagens: **24 páginas, 0 erros, 0
referências indefinidas, 0 overfulls**. Curvas da Figura 8.1 conferidas
analiticamente (partem de 0, convergem para 1); legenda reposicionada após
inspeção visual. Sem marcas de IA em texto ou metadados.

**Nomenclatura.** `Volume_0_Notacoes_e_Calculo.tex/pdf` é o nome canônico.

## Volume 0 — backlog por criticidade implementado (12/09/2026)

**Pedido do autor:** "podemos continuar a melhorar o volume 0?" seguido de
"crie um backlog por criticidade primeiro e siga o desenvolvimento por ele".
Auditoria prévia do volume (então 29 páginas) achou defeitos de conformidade
e lacunas de conteúdo; o planejamento completo, com o critério de
criticidade e o ponto exato dos Volumes I/II onde cada conteúdo é exigido,
está em `Backlog_volume0.md` (arquivo novo, na raiz, não commitado).

**Conformidade corrigida antes do conteúdo:** `\clearpage` antes dos 10
capítulos (faltava — convenção da coleção); Lista de Figuras e Lista de
Tabelas (ausentes; mesmo formato do Vol. I, `\phantomsection` +
`\addcontentsline`); 2 violações de auto-referência de equação
(`eq:v0-c4-2`, `eq:v0-c6-4`) corrigidas — varredura 0/22 na época, 0/36 no
fim; 4 defeitos de prosa ("dez ve menos que mil" — typo que também estava
**errado**: 10⁴ é 10× mais que mil e 10× menos que cem mil; frase truncada
do trabalho líquido no $p$–$V$; "vetorial duplo repetido"; citação da Eq.
6.4 só depois de aparecer).

**Itens implementados (ordem de criticidade):**
- **B0-01 — Números complexos e fasores** (Cap. 4, nova subseção + Figura
  4.2 do fasor girante, Eqs. 4.5–4.8): identidade de Euler, forma polar, o
  truque $\mathrm{d}/\mathrm{d}t \leftrightarrow \mathrm{i}\omega$,
  definição do fasor e as duas condições de validade (linearidade +
  frequência única, as mesmas que o Vol. I enuncia). Nota de símbolo
  adicionada no Cap. 2: a unidade imaginária é $\mathrm{j}$ na engenharia
  elétrica (o Vol. I usa $\mathrm{j}$ — conferido em $Z_L = j\omega L$,
  Eq. `v1-c7-13`), não $\mathrm{i}$.
- **B0-02 — Derivada material $D/Dt$ + menção a EDP**: subseção nova no
  Cap. 6 (taxa no ponto fixo × taxa na partícula, Eq. 6.5, ponte com
  Navier-Stokes do Vol. I) e subseção curta no Cap. 8 (o que é uma EDP;
  condições de contorno; por que os volumes seguintes não resolvem nenhuma —
  e como o Vol. II a usa como resíduo no PIML).
- **B0-03 — Kronecker/Einstein + divergência/rotacional + teorema da
  divergência**: subseção no Cap. 5 (δ de Kronecker, Eq. 5.4; soma
  implícita de Einstein, Eq. 5.5 — com a própria lei constitutiva do Vol. I
  como exemplo), no Cap. 6 (divergência, Eq. 6.6; rotacional, Eq. 6.7) e no
  Cap. 7 (fluxo, Eq. 7.4; teorema da divergência, Eq. 7.5 — a ponte
  integral→diferencial que o Vol. I usa nos balanços). **Correção ao
  backlog original**: o "teorema de Stokes" citado lá é a *hipótese* de
  Stokes (fluido newtoniano) no Vol. I — o teorema integral do rotacional
  **não** é usado na coleção e entrou só como menção de uma frase.
- **B0-04 — Autovalores e autovetores** (Cap. 5, Eqs. 5.6/5.7): polinômio
  característico, traço e determinante como contas de conferência, e o
  significado físico de modo próprio — ponte com as tensões principais do
  Cap. 2 do Vol. I (que admite "três autovalores reais") e com as raízes do
  sistema de 2ª ordem.
- **B0-05 — Exercícios resolvidos**: 18 exercícios (2 por capítulo de
  conteúdo; 1 de navegação no Cap. 1 e 1 de travessia no Cap. 10), todos
  com resolução completa, citando as equações do próprio volume e sem usar
  nada além do que o capítulo ensinou.
- **B0-06 — Séries geométricas** (Cap. 9, Eq. 9.3): soma, condição
  $|r|<1$, e a leitura de balanço discreto (ligada ao passo de Euler).
- **B0-07 — Figura da capa**: o `vspace` com comentário "Placeholder" virou
  a escada de pré-requisitos (Volume 0 → I → II) em TikZ vetorial, no
  padrão das figuras versionadas no próprio `.tex` do volume.
- **B0-08 — Tabela de gregas**: a linha de $\omega$/$\Omega$ dizia
  "resistência elétrica" — corrigido para "$\Omega$ é a unidade ohm", para
  não sugerir colisão de grandeza.

**Verificação final:** `pdflatex` 3 passagens — **42 páginas, 0 erros, 0
overfulls, 0 referências indefinidas**; varredura de auto-referência 0/36;
0 hardcodes de número de equação; capítulos conferidos abrindo em página
nova (p. 8, 10, 14, 17, 21, 25, 29, 33, 37, 40); Lista de Figuras
atualizada (7 entradas, incluindo a 4.2 nova); capa renderizada
(`pdftoppm`) e conferida por extração de texto. **Nada commitado** — regra
permanente. **Achado colateral pendente de decisão do autor:** o Volume I
não usa `\clearpage` nenhum (caps. começam no meio da página), desviando da
convenção da coleção.

## Reverificação geral de pendências e relatórios externos (13/09/2026)

Pedido do autor: "verifique se os erros e dicas ainda valem, pois muito já foi
ajustado". Cada item pendente dos arquivos de apoio foi conferido **por busca
direta nos `.tex` e no código**, não por leitura de registro anterior. O
resultado está anotado dentro de cada arquivo; o resumo:

**Encerrados — não reabrir.** `relatorio_diagramacao.md` (8/8),
`arquivos_apoio/dicas_kimi.md` de 31/07 (checklist inteiro),
`dicas_kimi.md` de 16/08 (5/5), `dicas_COPILOT.md`,
`Manus_parecer_final_compressores.md` (3 achados normativos + glossário de
anglicismos), `Backlog_kimi_compress.md` (13/13), `Backlog_volume0.md` (8/8) e
`Gemini_ajuste.pdf` (5 correções + 5 adições). `melhorias_gemini.md` está
majoritariamente vencido — ganhou cabeçalho de status listando o que já entrou
e o que resta (essencialmente calibração de bancada, Sobol/Morris, UKF e
MLOps).

**Conformidade estrutural conferida nesta data** (vale como baseline para a
próxima auditoria): 227 labels `eq:s*-*`, **1** sem `\eqref{}` prévio
(`eq:s22-5` — caso limítrofe: o parágrafo cita a `eq:s20-4` porque a equação é
reprodução declarada dela); **0** `\hline`/`tabular{|`/`array{|`; **50**
`\caption[`, **0** `\caption{`; **0** floats `[h!]`, 47 `[h!tbp]`; 36 overfull
hboxes, o maior com 2,01 pt (baseline documentado).

**Regressão real encontrada e corrigida na mesma sessão:** quatro aspas retas
voltaram à prosa do Capítulo 29 (`compressores.tex`, seção "Generalização: da
Atribuição Pontual ao Treino Multi-Mecanismo", escrita em 16/08/2026),
violando a regra permanente registrada em 30/07/2026. **O defeito era visível
no PDF** — `pdftotext` devolvia `PIML"(incrustaçã` e `PIML"— que`, com o
espaço seguinte engolido pelo *shorthand* do babel, exatamente o sintoma
descrito na regra. Corrigidas para `` `` ``/`''`. As 22 aspas retas restantes
no arquivo são legítimas (2 em comentário de preâmbulo, 4 no bloco `verbatim`
de Python, e as demais em contextos equivalentes).

**Lição de processo:** a regra das aspas foi criada em 30/07/2026 e violada de
novo em 16/08/2026, em conteúdo escrito nesta mesma linha de sessões — ou seja,
uma regra permanente registrada no `CONTEXTO.md` não impede a reincidência por
si só. A varredura é barata (`grep -o '"' compressores.tex | wc -l`, esperando
apenas as ocorrências legítimas conhecidas) e vale rodar ao fim de qualquer
sessão que escreva prosa nova, junto com a varredura de auto-referência de
equação que já é rotina.

**Pendências que continuam válidas** (verificadas uma a uma):
1. `dicas_ollama.md` itens 2, 3, 4, 5, 7 e 8 — o item 8 (mover
   `Gemini_ajuste.pdf`) foi resolvido nesta sessão; os demais seguem abertos, e
   o arquivo agora traz o comando de verificação de cada um. **Cuidado com o
   item 4**: existe um Glossário *de Anglicismos* (Cap. final, desde
   23/08/2026), mas o que falta é o glossário *de notação* cruzando
   termodinâmica × mecânica × ML — são itens distintos, fáceis de confundir.
2. O item 6 do `dicas_ollama.md` deixou de ser pendente por inteiro e passou a
   **parcial**: estimação de estados ✅ (Caps. 21/28) e quantificação de
   incerteza ✅ (subseção própria, `:3431`); faltam **validação do gêmeo contra
   dados reais** e **hierarquia de fidelidade** (0 ocorrências de ambas), e
   sincronização/latência aparecem só como bullet.
3. Cap. 6 do Volume II segue sem nenhuma figura — última lacuna gráfica da
   Parte I (o documento tem 28 figuras no total).
4. **Volume I não usa nenhum `\clearpage`** (10 capítulos, 0 ocorrências) —
   achado colateral registrado em 12/09, ainda pendente de decisão do autor. O
   Volume 0 já segue a convenção (10/10).
5. Redes Bayesianas (Cap. 25) sem equação.

**Estado do Volume I nesta data**, corrigindo o registro de 24/08 que listava
metade dos capítulos como esqueleto: **todos os capítulos de conteúdo já foram
reescritos** ao padrão da coleção — Cap. 2 (825 linhas), 3 (559), 4 (527), 5
(539), 6 (402), 7 (1094), 8 (349). O único que ainda não passou pela reescrita
é o **Cap. 9, Instrumentação e Medição (135 linhas)** — candidato natural para
a próxima expansão. O Cap. 10 (Síntese, 138 linhas) é curto por natureza.

**Ambiente:** o `aplicativo/venv/` **não existe na árvore atual** — precisa ser
recriado (`python3 -m venv venv && venv/bin/pip install -r requirements.txt`)
antes de rodar ou testar o app Python; streamlit/torch/scipy também não estão
no Python do sistema. O lado Rust está operacional (`cargo` instalado, 26
`#[test]` declarados).

**Dois ajustes aplicados nesta mesma sessão, a pedido do autor:**
1. As quatro aspas retas do Cap. 29 corrigidas (acima). Recompilado em 3
   passagens: **183 páginas, 0 erros, 0 referências indefinidas, 36 overfulls
   com máximo de 2,01 pt** — baseline preservado, sem regressão. Confirmado no
   PDF por `pdftotext`: agora sai `PIML” (incrustação` e `coluna “Detecção`,
   com o espaço preservado.
2. `Gemini_ajuste.pdf` movido para `arquivos_apoio/` com `git mv` (item 8 do
   `dicas_ollama.md`), preservando o histórico — o git registrou a operação
   como rename (`R`). Nenhum `.tex` ou `.md` referenciava o caminho antigo.

**Correção de fato sobre `arquivos_apoio/`:** este arquivo afirma, na seção
"Estado atual (última sessão)", que o subdiretório "continua **não rastreado
pelo git**". **Isso não é mais verdade** — `git ls-files arquivos_apoio/`
devolve 8 arquivos rastreados. A afirmação valia em 02/08/2026, quando a pasta
foi criada, e nunca foi atualizada. A **regra de conteúdo continua valendo
integralmente**: não mexer em nenhum arquivo de `arquivos_apoio/` sem pedido
explícito do autor — o que mudou é só o status de versionamento, não a
permissão.

**Segunda rodada, mesma sessão — status defasado nos arquivos de apoio.** O
autor pediu para atualizar também os `.md` onde as melhorias estavam
desatualizadas, o que autorizou explicitamente mexer em `arquivos_apoio/`
(a regra permanente exige pedido explícito — este foi ele; a regra continua
valendo para sessões futuras). Corrigidos:

- **`arquivos_apoio/Backlog_kimi_compress.md`** — a proposta **V0-01** (criar o
  Volume 0) ainda dizia "proposta de trabalho — nada implementado", de 08/09.
  O Volume 0 existe, está completo e commitado desde 12/09. Atualizado com o
  estado final e com a resposta às quatro decisões que a proposta deixava em
  aberto.
- **`Backlog_volume0.md`** — dizia "Nada commitado sem pedido explícito do
  autor"; o trabalho está em `5210d92` e `7db0080`.
- **`arquivos_apoio/dicas_kimi.md`** (31/07) — checklist de 7 itens inteiro
  desmarcado, embora implementado em 01/08. Marcado, com o comando de
  verificação de cada item e um aviso para não confundir este relatório com o
  `dicas_kimi.md` da raiz, que é outro (16/08).
- **`arquivos_apoio/dicas_COPILOT.md`** — encerrava com uma pergunta em aberto
  ("Deseja seguir com essa conferência automática?") já respondida e executada
  em 02/08. Cabeçalho de status cobrindo os cinco blocos A–E.
- **`arquivos_apoio/Manus_parecer_final_compressores.md`** — cabeçalho com o
  estado das 5 recomendações prioritárias. Vale notar que a recomendação 2
  (dois níveis de leitura) acabou atendida por um caminho que o parecer não
  previu: em vez de estratificar o mesmo livro, a coleção ganhou o Volume 0 e o
  Volume I inteiros.
- **`SISTEMA_MULTI_MODELOS.md`** — a linha "Projeto ativo" ainda descrevia o
  repositório como "material de ensino, avaliação 6,0/10, revisão em curso pelo
  Kimi". Substituída por uma tabela dos cinco artefatos com o estado medido.

**Padrão observado, que vale para a próxima auditoria:** o erro recorrente
nestes arquivos não é conteúdo errado — é **status congelado**. Cada relatório
descreve corretamente o que viu no dia em que foi escrito, e o que envelhece é a
linha de "pendente"/"nada implementado"/"nada commitado" no topo. Uma leitura
apressada dos arquivos de apoio, hoje, produziria uma lista de tarefas com pelo
menos 20 itens já feitos. Ao encerrar um item de backlog, **atualizar o status
no próprio arquivo de origem**, não só no `CONTEXTO.md` — foi exatamente essa
lacuna que exigiu esta rodada.
