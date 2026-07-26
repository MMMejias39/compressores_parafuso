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

## Estado atual (última sessão)

Documento compila limpo, 97 páginas, sem erros/referências indefinidas/labels
duplicados. Repositório git inicializado (ver "Visão de longo prazo" acima),
tag `v1.0` no commit inicial — use `git log` para o histórico exato.

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

Não há tarefas pendentes conhecidas.

Observação: há 4 JPEGs soltos em `figuras/` baixados pelo autor como referência
visual (thumbnails de baixa resolução, licença não verificada) — **não** usá-los no
documento; serviram só de inspiração para o render 3D da Figura 3.1.
