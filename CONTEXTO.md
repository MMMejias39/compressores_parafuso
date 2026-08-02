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
- **Explicação antes da equação**: toda equação deve ser precedida de um parágrafo
  didático explicando o que ela representa e o significado de cada termo — não
  apresente equações "cruas".
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

## Estado atual (última sessão)

Documento compila limpo, **135 páginas**, sem erros/referências
indefinidas/labels duplicados. Todos os 27 capítulos têm subseções e
aparecem estruturados no sumário. Repositório git inicializado (ver "Visão
de longo prazo" acima); histórico completo reescrito em 26/07/2026 para
remover trailers de coautoria (ver seção acima) — os hashes de commit
mudaram desde qualquer anotação anterior a essa reescrita, sempre confira
com `git log` em vez de citar um hash de memória. Tag `v1.0` no commit
inicial (recriada). Commits mais recentes, em ordem: `a1f8ffb` (correção do
`cmap`, 26/07/2026) → `693a2c6` (fora do escopo deste documento — não é
conteúdo do livro) → `27997b6` → `3417919` (os dois de dicas_kimi.md acima)
→ `8657b5c` (consolidação do trabalho pendente de 29-31/07, ver acima) →
`1d0ebc3` (correção deste próprio arquivo). Os commits seguintes
(`7a0d1cf`, `875e900`, `06ff51d`, `0b6534e`, `d637ae2`) são todos do
`aplicativo/` — fora do escopo deste documento — exceto `738cc1c`
(correção da Equação 15.7, ver seção acima), que é do livro. Sem trabalho
pendente sem commit no livro no momento — use `git log` para o histórico
exato.

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

Observação: há quatro arquivos soltos na raiz do projeto, não rastreados pelo
git e não criados por mim — `recomenda compressores.txt` (análise externa via
Copilot CLI, ver "Correção de extração de texto" acima),
`Manus_parecer_final_compressores.md` (análise externa da Manus AI, **lida e
implementada em 29-30/07/2026**, ver as duas seções acima), `dicas_kimi.md`
(análise externa da Kimi, **lida e implementada em 01/08/2026**, ver seção
acima) e `referências extras para as fórmulas.md` — este último **não é
markdown apesar da extensão**: é um `.odt` (OpenDocument Text) renomeado,
conteúdo binário, ainda não examinado. Não mexer em nenhum deles nem
incluí-los em commits sem o autor pedir explicitamente. Diferença de
qualidade entre os três relatórios já lidos, útil para calibrar ceticismo no
futuro: o Copilot acertou o sintoma e errou a causa; o Manus acertou os três
problemas normativos, todos confirmados na fonte primária; o Kimi acertou o
diagnóstico de diagramação mas subestimou a extensão de alguns itens (relatou
1 tabela com overfull grave, a varredura achou 5).

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
4. **Estudo de caso numérico de ponta a ponta** (sugestão comum aos dois
   pareceres externos): um exemplo resolvido com números reais atravessando
   Parte I e Parte II. É a maior adição possível em esforço, e nunca foi pedida
   pelo autor — não perseguir sem pedido explícito.

**Deliberadamente descartado**: a recomendação do Manus de abandonar o termo
"Enciclopédia" no título por ser ambicioso demais para 105 páginas. Contraria a
visão de longo prazo do autor registrada no topo deste arquivo — a obra é o
primeiro volume de uma coleção modular, e o título descreve o projeto, não o
volume isolado. Não reabrir sem o autor levantar o assunto.

Observação: há 4 JPEGs soltos em `figuras/` baixados pelo autor como referência
visual (thumbnails de baixa resolução, licença não verificada) — **não** usá-los no
documento; serviram só de inspiração para o render 3D da Figura 3.1.
