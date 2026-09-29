---
name: qa-compilacao-latex
description: Checklist genérico de verificação antes de declarar pronta qualquer mudança num documento LaTeX (livro, artigo, relatório) — compilação limpa, leitura correta do log (frequentemente Latin-1), baseline de overfull hbox, inspeção visual das páginas alteradas com pdftoppm, varreduras baratas de regressão. Carregar ANTES de declarar pronta uma mudança em qualquer arquivo .tex, ou antes de revisar um PDF gerado por LaTeX.
---

# QA de compilação LaTeX com inspeção visual

Checklist genérico para qualquer projeto LaTeX. A lição central: **o log de
compilação limpo não garante que a página renderiza bem** — colisão de
cabeçalho, figura com eixo cortado, tabela estourando a margem, texto
ilegível por fonte pequena numa figura densa: nada disso gera erro ou warning
de compilação. Só aparece em inspeção visual direta do PDF renderizado.

## 1. Compilação

- `pdflatex -interaction=nonstopmode <arquivo>.tex` **3 vezes** (ou
  `latexmk -pdf`, que já resolve o número certo de passes) — referências
  cruzadas, sumário e bibliografia levam até 3 passes para estabilizar.
  Critério de pronto: 0 erros, 0 "Reference undefined", 0 "Label multiply
  defined".
- **O `.log` costuma estar em Latin-1**, não UTF-8 — `grep` puro falha em
  silêncio ao buscar acentos/caracteres especiais no log. Usar `grep -a`
  (força modo texto) para garantir que a busca realmente varre o arquivo.
- Se o projeto usa bibliografia (`biblatex`/`bibtex`), rodar o passe de
  bibliografia entre as compilações e conferir 0 "Warning: Citation ... on
  page ... undefined".

## 2. Baseline de overfull/underfull hbox

- Antes de mexer em qualquer coisa, estabelecer (ou localizar, se o projeto
  já documenta) o baseline atual: quantos overfull hbox existem hoje e qual
  a pior magnitude (em pt). `grep -a "Overfull \\\\hbox" <arquivo>.log`.
- **Qualquer overfull novo além do baseline é regressão até provado o
  contrário** — não é aceitável "só mais um pouco pior", cada novo overfull
  tem uma causa identificável (texto longo demais numa célula, palavra sem
  ponto de hifenização) que deveria ser corrigida na hora, não acumulada.
- Documentar o baseline no próprio projeto (README, changelog, ou uma skill
  específica do projeto) para a próxima sessão comparar sem precisar
  redescobrir o número do zero.

## 3. Inspeção visual (a etapa que o log nunca substitui)

- `pdftoppm -png -r 150 -f <pág-inicial> -l <pág-final> <arquivo>.pdf
  <prefixo>` gera imagens das páginas alteradas para inspeção direta.
- Rodar isso para **toda** página alterada nesta sessão, não só onde uma
  figura nova entrou — mudança de prosa pode empurrar uma tabela para uma
  quebra de página ruim, texto pode colidir com cabeçalho/rodapé.
- Vale em dobro para páginas com figura gerada por script (a geometria pode
  estar tecnicamente correta nos dados e ainda assim renderizar mal —
  eixo com escala errada, legenda sobrepondo curva, fonte pequena demais
  numa figura densa).

## 4. Varreduras baratas de regressão (adaptar a lista às convenções do projeto)

Rodar sobre o que foi editado nesta sessão, não o arquivo inteiro sempre:

- Aspas retas em prosa (`grep -o '"' <arquivo>.tex | wc -l`), se o projeto
  usa aspas tipográficas (`` ` `` / `'`) como convenção — cada `"` reto pode
  quebrar comportamento de pacotes de idioma (ex.: `babel` torna `"` um
  caractere ativo em alguns idiomas).
- Referências cruzadas hardcoded como texto solto (`grep -noE
  "[Ff]igura~?[0-9]+\.[0-9]+"` ou padrão equivalente) em vez de
  `\ref{}`/`\eqref{}` — sintoma de que uma referência vai dessincronizar na
  próxima renumeração.
- Labels duplicados ou não referenciados: cruzar `\label{}` contra
  `\ref{}`/`\eqref{}`/`\cite{}` no próprio `.tex` e no `.log`.
- Qualquer convenção de formatação específica do projeto (estilo de tabela,
  largura padrão de figura, marca de rascunho/IA) que a sessão possa ter
  quebrado sem querer.

## 5. Documentos derivados (edição combinada, PDF/A, etc.)

- Se o projeto gera um artefato combinado a partir de fontes separadas via
  script (ex.: "edição completa" concatenando volumes), esse artefato é
  **derivado e descartável** — nunca editar o gerado à mão. Regenerar pelo
  script e recompilar 3× sempre que uma fonte mudar.
- Conferir o outline/sumário do artefato combinado com uma ferramenta que
  leia a árvore de bookmarks do PDF (`mutool show`, `pdftk dump_data`, ou
  equivalente) — um outline mal aninhado (capítulos como filhos do volume
  errado) não aparece em nenhum warning de compilação.

## 6. Antes de declarar pronto (resumo executável)

1. Compilar 3× (ou `latexmk -pdf`) — 0 erros/refs indefinidas/labels
   duplicados, checado com `grep -a` no log.
2. Comparar overfull/underfull contra o baseline documentado do projeto.
3. `pdftoppm` + inspeção visual de toda página alterada.
4. Varreduras de regressão específicas das convenções do projeto.
5. Se existe artefato derivado combinado: regenerar e recompilar 3× também.
