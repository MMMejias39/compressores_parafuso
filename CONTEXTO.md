# Contexto do Projeto — Gêmeo Digital de Sistemas de Compressão Offshore

Este arquivo existe para que uma nova sessão do Claude (ou qualquer outra IA) possa
retomar o trabalho neste livro sem que o autor precise reexplicar tudo do zero.
Leia este arquivo inteiro antes de propor qualquer alteração no documento.

Quando o autor disser **"Atualize contexto"**, atualize este arquivo com um resumo do
que mudou na sessão atual (seguindo o estilo já usado abaixo). É um gatilho sob
demanda — fora dele, só reescreva este arquivo se a mudança for estrutural o
bastante para justificar (nova convenção, nova figura derivada, arquivo novo).

## O que é este projeto

`compressores.tex` é um livro técnico (~84 páginas) sobre construção de um Gêmeo
Digital completo para compressores de parafuso rotativo isentos de óleo usados em
plantas de ar comprimido offshore (óleo e gás). O autor escreveu o conteúdo original
com apoio de um GPAI e vem revisando/expandindo o documento em conjunto com o Claude
ao longo de várias sessões.

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
`scripts/venv/`, `scripts/__pycache__/`). Ainda não há nenhum commit — nunca crie
commits sem pedido explícito do autor.

## Arquivos e pastas

- `compressores.tex` — documento principal (fonte única de verdade).
- `compressores.pdf` — PDF compilado (84 páginas na última revisão).
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
`relatorio_diagramacao.md` na raiz do projeto. **Todos os 8 itens do relatório foram implementados**
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

O subdiretório `documentos de apoio/` guarda material da base inicial do trabalho.
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
2. **Capítulos 11 (864 palavras), 14 (923), 20 (974) e 6 (976)** são os mais
   curtos do livro depois da expansão dos Capítulos 12 e 13 — se o critério de
   "capítulo desenvolvido, não nota técnica" for aplicado adiante, começar por
   eles. (Contagem por `awk` sobre o `.tex`, incluindo marcação; serve para
   ranquear, não como número absoluto.)
3. **Redes Bayesianas (Cap. 25)** e os detalhes de MHE do `do-mpc` (Cap. 27)
   continuam citados só por nome, sem equação — pendência herdada do
   "Inventário de algoritmos da Parte II" acima.
4. ~~Estudo de caso numérico de ponta a ponta~~ — **feito em 15/08/2026**,
   ver "Parte III — Estudo de Caso Integrado, Capítulo 28" acima.

**Deliberadamente descartado**: a recomendação do Manus de abandonar o termo
"Enciclopédia" no título por ser ambicioso demais para 105 páginas. Contraria a
visão de longo prazo do autor registrada no topo deste arquivo — a obra é o
primeiro volume de uma coleção modular, e o título descreve o projeto, não o
volume isolado. Não reabrir sem o autor levantar o assunto.

Observação: há 4 JPEGs soltos em `figuras/` baixados pelo autor como referência
visual (thumbnails de baixa resolução, licença não verificada) — **não** usá-los no
documento; serviram só de inspiração para o render 3D da Figura 3.1.
