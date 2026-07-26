> **Atualização de 26/07/2026**: todos os 8 itens abaixo já foram implementados no `.tex`
> (ver "Diagramação — convenções" no `CONTEXTO.md` para o detalhe de cada mudança). Este arquivo
> fica só como registro histórico do diagnóstico original.

# Relatório de Diagramação — `compressores.pdf`

**Documento analisado:** `compressores.pdf` (87 páginas, A4, gerado a partir de `compressores.tex`)
**Método:** compilação limpa conferida (`compressores.log` sem overfull/underfull box, sem referências
indefinidas), inspeção do preâmbulo/fonte LaTeX e renderização de todas as 87 páginas em imagem
(`pdftoppm`) para checagem visual página a página.
**Data:** 26/07/2026

Nenhum problema encontrado aqui é um erro de compilação — o PDF gera limpo. São, todos, decisões de
diagramação (layout) que afetam a experiência de leitura e a usabilidade do livro como obra de
referência consultável por capítulo, conforme a visão descrita em `CONTEXTO.md`.

---

## 1. Links do hyperref sem estilo (caixas vermelhas) — **alto impacto, correção trivial**

`\usepackage{hyperref}` é carregado sem nenhum `\hypersetup`. O padrão do pacote desenha uma **caixa
vermelha ao redor de toda referência cruzada, equação, citação e link** (`\ref`, `\eqref`, `\cite`).
Isso aparece em praticamente todas as páginas de corpo de texto — confirmado visualmente, por exemplo,
nas citações `[17]`, `[18]`, `[14]` da página 17 e nas referências de equação da página 19.

Para um livro pensado como obra de consulta (com dezenas de remissões por capítulo), isso é o item de
maior impacto visual negativo e o mais barato de corrigir.

**Diagramação recomendada:**
```latex
\hypersetup{
  colorlinks=true,
  linkcolor=black,      % ou um azul escuro discreto, ex.: RoyalBlue!70!black
  citecolor=black,
  urlcolor=black,
  pdftitle={Gêmeo Digital de Sistemas de Compressão Offshore},
  pdfauthor={Marcelo Moreira Mejias}
}
```
Se a intenção é impressão em papel (P&B), usar `hidelinks` no lugar de `colorlinks` remove as caixas
sem introduzir cor nenhuma. De qualquer forma, aproveitar para preencher `pdftitle`/`pdfauthor`: hoje
o PDF sai com metadados vazios (`pdfinfo` confirma Title/Author em branco), o que atrapalha citação e
organização do arquivo fora do LaTeX.

---

## 2. Capítulos (`\section`) não começam em página nova — **alto impacto, contradiz o objetivo do projeto**

Nenhum `\clearpage`/`\newpage` antecede a maioria dos 27 `\section` do documento (apenas o Capítulo 2,
que herda o `\clearpage` da página da Parte I). Na prática, um capítulo novo começa no meio da página
onde o anterior terminou.

Confirmado visualmente: na página 20, o Capítulo 3 ("Detalhamento de Componentes...") começa a menos
de um terço da página, logo abaixo do quadro "Diretriz Técnica Final" do Capítulo 2. O mesmo padrão se
repete na página 22 (Capítulo 4 começando logo após a Diretriz Técnica Final do Capítulo 3), e é a regra,
não a exceção, ao longo do livro.

Isso é o ponto mais importante do relatório porque **contradiz diretamente** a visão de longo prazo
registrada em `CONTEXTO.md`: o livro é concebido como uma "enciclopédia" nos moldes da *Techniques de
l'Ingénieur*, onde cada capítulo deve ser "autocontido e referenciável isoladamente". Um leitor que
abre o PDF direto no Capítulo 8 (por exemplo, via sumário ou referência de outro documento) cai no meio
de uma página com o fim de outro assunto acima. Isso também vale para impressão física — folhear o
livro procurando o início de um capítulo fica mais difícil sem um ponto fixo (início de página).

**Diagramação recomendada:** inserir `\clearpage` (ou `\newpage`) imediatamente antes de cada
`\section` de capítulo (não antes de `\subsection`). É uma mudança mecânica e de baixo risco — o
projeto já usa comentários `% --- Início do Capítulo N ---` antes de cada `\section`, então os pontos
de inserção já estão todos marcados no próprio arquivo.

*Trade-off a decidir com o autor:* isso vai aumentar a contagem de páginas (cada capítulo passa a
"desperdiçar" o espaço em branco até o fim da página anterior). Para um livro de referência, esse é
geralmente um trade-off aceito — é o mesmo motivo pelo qual todo livro impresso com `\chapter` sempre
começa em página nova.

---

## 3. Nenhum cabeçalho corrente (running header) — **médio-alto impacto**

O documento usa apenas o estilo de página padrão do `article` (número de página centralizado no
rodapé). Não há `fancyhdr` nem qualquer cabeçalho indicando em que capítulo/seção o leitor está.

Para um documento de 87 páginas pensado para consulta pontual (não leitura linear cover-to-cover,
como o próprio `CONTEXTO.md` deixa explícito), a ausência de cabeçalho corrente com o nome do
capítulo atual obriga o leitor a voltar ao sumário sempre que perde a referência de onde está.

**Diagramação recomendada:**
```latex
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\sectionmark}[1]{\markboth{#1}{}}
\fancyhead[L]{\nouppercase{\leftmark}}
\fancyhead[R]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
```
(ajustar `\leftmark`/lado conforme preferência; como não há `\chapter`, o marcador precisa vir de
`\sectionmark`).

---

## 4. Tabelas com estilos inconsistentes entre si — **médio impacto**

O documento carrega `booktabs`, mas das 14 tabelas (`\begin{table}`) apenas 3 de fato usam
`\toprule`/`\midrule`/`\bottomrule`. As outras 11 — inclusive as duas grandes tabelas de Nomenclatura
logo após o sumário — usam o estilo antigo `|l|l|l|l|}` com `\hline` em toda linha e barras verticais
(confirmado nas linhas 734–743, entre outras, e visualmente nas páginas 8–12 e 83).

O resultado é um livro que mistura dois sistemas visuais de tabela diferentes sem critério aparente
(não parece haver uma categoria de tabela — ex. "nomenclatura" vs. "modos de falha" — associada a cada
estilo).

**Diagramação recomendada:** padronizar todas as tabelas no estilo `booktabs` (sem barras verticais,
apenas regras horizontais finas). Como referência de conversão:
```latex
% antes
\begin{tabular}{|l|l|l|l|}
\hline
A & B & C & D \\ \hline
...
\end{tabular}

% depois
\begin{tabular}{llll}
\toprule
A & B & C & D \\ \midrule
...
\bottomrule
\end{tabular}
```
Nas tabelas de Nomenclatura (colunas largas com texto corrido), vale também trocar `p{Xcm}` justificado
por `>{\raggedright\arraybackslash}p{Xcm}` — hoje o texto justificado em colunas estreitas produz
espaçamento irregular entre palavras (visível, por exemplo, na célula "Potência (trabalho por unidade
de tempo)" da tabela da página 8).

---

## 5. Ausência do pacote `microtype` — **baixo esforço, ganho geral**

Não há `\usepackage{microtype}` no preâmbulo. É uma adição de uma linha, sem risco de quebrar
compilação ou referências, que melhora justificação (protrusion/expansion de fonte) em todo o
documento — reduz especialmente o efeito de espaçamento irregular em parágrafos justificados e nas
células de tabela mencionadas no item 4.

**Diagramação recomendada:**
```latex
\usepackage{microtype}
```
Colocar logo após `\usepackage[T1]{fontenc}`.

---

## 6. Capa muito austera para a extensão e ambição da obra — **impacto subjetivo, mas real**

A página de rosto (`\begin{titlepage}`) tem apenas três blocos de texto centralizados (título,
subtítulo, autor/data) sobre uma página quase inteiramente em branco, em Computer Modern padrão, sem
nenhuma regra, cor ou elemento gráfico. Para um documento de 87 páginas que o autor já concebe como o
"Volume I" de uma coleção maior (ver `CONTEXTO.md`, seção "Visão de longo prazo"), a capa atual não
comunica nem a extensão do trabalho nem a existência de um sistema de volumes/versionamento.

**Diagramação recomendada (mínima, sem exigir pacotes novos):**
- Uma regra horizontal (`\rule{\textwidth}{0.4pt}`) acima e abaixo do bloco de título, para dar
  ancoragem visual.
- Um rótulo de volume/edição já pensando na coleção futura, ex.: *"Enciclopédia de Máquinas
  Rotodinâmicas — Volume I"* acima do título atual, e uma linha de versão/data de revisão abaixo do
  autor (`Rev. 26/07/2026`) — isso é exatamente o "esquema de versionamento explícito" que o
  `CONTEXTO.md` já lista como direção futura do projeto, só que hoje não aparece em lugar nenhum do
  PDF em si (só no `.gitignore`/repositório).
- Opcionalmente, reaproveitar a Figura 3.1 (render 3D dos rotores, já produzida e com crédito CC BY-SA
  correto) em miniatura na capa — o livro já tem o material gráfico, só não o usa na abertura.

---

## 7. Capítulos sem elemento visual distintivo além do tamanho da fonte — **baixo impacto, opcional**

Como o "capítulo" é tecnicamente um `\section` (a classe é `article`, não `report`/`book`), o único
diferencial visual entre um título de capítulo e um título de subseção é o tamanho da fonte — não há
rótulo "Capítulo N", regra, ou faixa de cor separando estruturalmente a unidade que o próprio projeto
trata como a peça autocontida fundamental do livro.

**Diagramação recomendada (opcional):** redefinir o formato do `\section` com `titlesec` para incluir
o rótulo por extenso e uma regra fina abaixo do título:
```latex
\usepackage{titlesec}
\titleformat{\section}
  {\normalfont\Large\bfseries}
  {Capítulo \thesection}{1em}{}
  [\vspace{-0.5em}\rule{\textwidth}{0.4pt}]
```
Isso é uma mudança estética, não estrutural — pode ser adiada sem prejuízo funcional, diferente dos
itens 1 a 3.

---

## 8. Larguras de figura sem um sistema aparente — **baixo impacto, nota apenas**

As 15 figuras do livro usam larguras que variam de `0.55\textwidth` a `0.85\textwidth` sem um padrão
evidente ligado ao tipo de conteúdo (diagrama de blocos vs. gráfico técnico vs. render). Não chega a
prejudicar a leitura — cada figura individualmente está bem dimensionada para seu conteúdo — mas o
conjunto do livro ganharia em ritmo visual se houvesse 2–3 larguras-padrão (ex.: `0.6\textwidth` para
gráficos de uma curva, `0.75\textwidth` para diagramas com texto, `0.85\textwidth` para figuras
compostas/multi-painel) em vez de um valor ajustado individualmente por figura.

---

## Resumo priorizado

| # | Item | Impacto | Esforço |
|---|------|---------|---------|
| 1 | Caixas vermelhas do hyperref | Alto | Trivial (1 bloco `\hypersetup`) |
| 2 | Capítulos sem quebra de página | Alto | Baixo (inserir `\clearpage` x27, mecânico) |
| 3 | Sem cabeçalho corrente | Médio-alto | Baixo (`fancyhdr`, ~6 linhas) |
| 4 | Tabelas inconsistentes (grid vs. booktabs) | Médio | Médio (editar 11 tabelas) |
| 5 | Falta `microtype` | Baixo esforço / ganho geral | Trivial (1 linha) |
| 6 | Capa austera | Subjetivo, mas real | Baixo |
| 7 | Capítulo sem identidade visual própria | Baixo | Baixo-médio (opcional) |
| 8 | Larguras de figura sem sistema | Baixo | Baixo (opcional) |

Os itens 1, 2, 3 e 5 são os que eu recomendaria priorizar — todos de esforço baixo/trivial e impacto
direto na usabilidade do livro como obra de referência, que é o objetivo declarado do projeto. Os
itens 4, 6, 7 e 8 são melhorias de acabamento, com bom custo-benefício mas não urgentes.

Este relatório é apenas de diagnóstico — nenhuma alteração foi feita em `compressores.tex`. Posso
implementar qualquer um dos itens acima mediante confirmação.
