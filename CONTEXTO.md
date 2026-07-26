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
  Integrado** (Capítulos 19 a 25 + Anexos de Implementação: EKF, VAE, PIML, MPC,
  PSO e a integração de tudo num motor de cálculo único). O Capítulo 1 (Introdução)
  fica antes da Parte I, como preâmbulo. A Seção 1.3 do próprio livro também
  descreve essa divisão — mantenha as duas em sincronia se o capítulo final de
  alguma das partes mudar.
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

## Diagramação — pendências e convenções (relatório de 26/07/2026)

Em 26/07/2026 foi feita uma revisão completa de diagramação do PDF compilado (compilação limpa
conferida, mais inspeção visual das 87 páginas via `pdftoppm`). O diagnóstico completo, com página/
linha de cada achado e a correção LaTeX sugerida, está em `relatorio_diagramacao.md` na raiz do
projeto — **leia esse arquivo antes de mexer em qualquer aspecto de layout** (quebra de página, capa,
tabelas, links, cabeçalho). Nenhuma das correções abaixo foi aplicada ao `.tex` ainda; ficaram só
diagnosticadas. Implemente mediante pedido explícito do autor, uma de cada vez, recompilando e
conferindo via `pdftoppm` antes de considerar concluída (mesma prática já usada para figuras).

**Retrofit pendente (afeta conteúdo já existente):**
- Links do `hyperref` sem `\hypersetup` → caixas vermelhas ao redor de toda referência/citação em
  praticamente todas as páginas. Adicionar `\hypersetup{colorlinks=true, linkcolor=..., citecolor=...,
  urlcolor=..., pdftitle=..., pdfauthor=...}` (ou `hidelinks` se o alvo for impressão P&B).
- Nenhum `\clearpage`/`\newpage` antes da maioria dos 27 `\section` de capítulo → capítulos começam no
  meio da página anterior, contradizendo o objetivo de capítulos autocontidos/referenciáveis
  isoladamente (ver "Visão de longo prazo" acima). Inserir `\clearpage` antes de cada `\section` de
  capítulo (os pontos já estão marcados no `.tex` pelos comentários `% --- Início do Capítulo N ---`).
- Falta `fancyhdr`/cabeçalho corrente com o nome do capítulo atual — hoje só há número de página.
- Falta `\usepackage{microtype}` — melhora justificação em todo o documento, adição de baixo risco.
- 11 das 14 tabelas (inclusive as duas de Nomenclatura) usam grade antiga (`|l|l|`, `\hline` em toda
  linha) em vez do estilo `booktabs` já carregado no preâmbulo e usado nas outras 3 — padronizar todas
  em `booktabs` (sem barras verticais).
- Capa (`titlepage`) muito austera para a extensão da obra e para o plano de virar "Volume I" de uma
  coleção versionada (ver "Visão de longo prazo") — não tem regra, cor, elemento gráfico nem rótulo de
  volume/versão. Ver relatório para sugestão mínima (regra horizontal + rótulo de volume/revisão,
  aproveitando a Figura 3.1 em miniatura).
- Capítulos sem identidade visual além do tamanho de fonte (são `\section`, não `\chapter` — a classe é
  `article`) — opcional, via `titlesec`.
- Larguras de figura (`0.55\textwidth` a `0.85\textwidth`) sem sistema — opcional, convergir para 2-3
  larguras-padrão por tipo de figura.

**Convenções a seguir a partir de agora em conteúdo novo** (para não acumular mais dívida do mesmo tipo
enquanto o retrofit acima não é feito):
- Todo `\section` novo de capítulo deve vir precedido de `\clearpage`.
- Toda tabela nova deve usar `booktabs` (`\toprule`/`\midrule`/`\bottomrule`, sem barras verticais),
  nunca o estilo de grade antigo — mesmo que o retrofit das tabelas existentes ainda não tenha sido
  feito.
- Colunas de tabela com texto corrido (tipo as de Nomenclatura) devem usar
  `>{\raggedright\arraybackslash}p{Xcm}` em vez de `p{Xcm}` justificado, para evitar espaçamento
  irregular em colunas estreitas.

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

Documento compila limpo, 85 páginas, sem erros/referências indefinidas/labels
duplicados. Alterações de 26/07/2026: (a) bibliografia completada a partir de
`documentos de apoio/referências iniciais.docx` (ver seção acima); (b) a Figura 3.1
deixou de ser o corte
esquemático 2D (o autor não gostou do resultado) e passou a ser um render 3D do par
de rotores engrenados, gerado por `fig_parafuso3d()` em `gen_figuras.py` a partir do
perfil da Figura 2.2 (ver seção "Figuras" acima). Parágrafo introdutório e caption da
Figura 3.1 foram reescritos de acordo. Verificação visual feita via `pdftoppm`
(prática usada consistentemente neste projeto para checar layout antes de considerar
uma figura pronta). (c) Criada `apresentacao_compressores.tex`/`.pdf`, apresentação
Beamer de 21 slides (tema Metropolis, 16:9) resumindo o livro para uso em reuniões
(ver seção "Arquivos e pastas" acima) — compila limpo, sem overfull visível, conferida
via `pdftoppm` slide a slide. Não há tarefas pendentes conhecidas.

Observação: há 4 JPEGs soltos em `figuras/` baixados pelo autor como referência
visual (thumbnails de baixa resolução, licença não verificada) — **não** usá-los no
documento; serviram só de inspiração para o render 3D da Figura 3.1.

(d) Todas as 45 referências do `thebibliography` foram verificadas uma a uma contra
fontes reais (normas, editoras, periódicos, DOIs). 3 tinham título fabricado ou não
verificável e foram corrigidas: `api684` (título real da norma API RP 684/TR 684-1),
`dompc` (título real do artigo, Control Engineering Practice 140:105676, 2023) e
`lysholm` (trocado o "livro" inexistente pela patente real e verificável US
2.111.568). `fleming` e `bently` foram completados (ano/volume e coautor faltantes).
Ver seção "Veracidade de referências e fontes" acima para a regra permanente daqui
em diante.

(e) O livro foi rediagramado em duas Partes explícitas via `\part{}` (article
class — não afeta a numeração de `\section`, que continua contínua 1-25 + Anexos
A/B): **Parte I — O Compressor e Seus Elementos** (Capítulos 2 a 18, inserida logo
antes do Capítulo 2) e **Parte II — Metodologia do Gêmeo Digital e Equacionamento
Integrado** (Capítulos 19 a 25 + Anexos de Implementação, inserida logo após a
Equação~(18.6) que fecha o Capítulo 18). O Capítulo 1 (Introdução) fica antes da
Parte I, como preâmbulo. O parágrafo da Seção 1.3 ("Estrutura do Documento e
Abordagem Metodológica") que já descrevia essas duas metades tinha faixas de
capítulo desatualizadas ("2 a 14" / "15 a 24", de uma versão anterior do livro com
menos capítulos) — foi corrigido para "2 a 18" / "19 a 25" ao mesmo tempo.

(f) Revisão completa de diagramação (layout) do PDF, com inspeção visual das 87
páginas via `pdftoppm`. Diagnóstico salvo em `relatorio_diagramacao.md` e resumido
na seção "Diagramação — pendências e convenções" acima. Nenhuma correção foi
aplicada ao `.tex` nesta sessão — ficou só o diagnóstico e as convenções para
conteúdo novo (quebra de página por capítulo, tabelas em `booktabs`). O retrofit do
conteúdo já existente (hyperref, cabeçalho corrente, microtype, tabelas antigas,
capa) é uma tarefa pendente conhecida, a ser feita mediante pedido do autor — ver
seção acima para a lista priorizada.
