# Backlog — Edição Completa (`Enciclopedia_Completa.tex`)

**Origem:** o autor apontou (16/09/2026) que, na união dos três volumes, os
marcadores do PDF (outline/sidebar) mostram os Volumes I e II aninhados como
subitens do Volume 0 — cada capítulo fica um nível abaixo do anterior, e o
Volume I termina no nível 11, o II no nível 22. Os volumes são obras
independentes e devem aparecer como entradas irmãs de nível máximo.

## Implementado (nesta sessão, pendente de verificação)

Em `scripts/gerar_edicao_completa.py`:

1. **Pacote `bookmark`** adicionado ao preâmbulo gerado (logo após o
   hyperref): o hyperref sozinho calcula o aninhamento dos marcadores de
   forma relativa e se perde com as páginas de volume feitas via
   `\addcontentsline{toc}{part}`; o `bookmark` recalcula os níveis a partir
   dos níveis absolutos gravados no `.out`.
2. **Âncoras únicas por volume** (`ancora_volume()`): junto ao
   `\setcounter{section}{0}` de cada volume, o gerador agora emite
   `\renewcommand` de `\theHsection`, `\theHequation`, `\theHfigure` e
   `\theHtable` com prefixo `v0`/`v1`/`v2`. Antes disso o log tinha **633
   destinos duplicados** (`equation.` 368, `figure.` 38, `table.` 27,
   `section.` 20) — links e marcadores apontavam para a primeira ocorrência
   do nome, isto é, para o volume errado.

## Bloqueio que impediu a verificação nesta sessão

O `compressores.tex` **atual da árvore não compila** (estado pré-existente,
não introduzido nesta sessão): os blocos `NOMENCLATURA-CAP <n>` gerados por
`scripts/gerar_nomenclatura_por_capitulo.py` (arquivo não rastreado, trabalho
em andamento) foram inseridos **dentro** do argumento do `\section{...}` de
cada capítulo — entre o título e a chave de fechamento. Erro resultante:
`Paragraph ended before \ttl@straight@i was complete` (titlesec), fatal já no
Cap. 2.

## Próximos passos (na ordem)

1. Corrigir o ponto de inserção da nomenclatura por capítulo: o bloco
   `% >>> NOMENCLATURA-CAP` ... `% <<< NOMENCLATURA-CAP` deve ficar **depois**
   do fechamento do `\section{...}` (provável correção em
   `scripts/gerar_nomenclatura_por_capitulo.py` + reaplicação, ou edição
   direta dos 20+ pontos de inserção). Confirmar que `compressores.tex`
   compila 3× sem erros antes de seguir.
2. Regenerar: `python3 scripts/gerar_edicao_completa.py` e compilar
   `Enciclopedia_Completa.tex` 3× (o pacote `bookmark` precisa de uma
   passagem extra para estabilizar o `.bkm`).
3. Verificar o outline: `mutool show Enciclopedia_Completa.pdf outline` —
   VOLUME 0/I/II devem estar no nível máximo (irmãos), capítulos um nível
   abaixo, subseções dois níveis abaixo. Conferir também onde ficam as
   Partes I/II/III internas do Volume II (hoje entram como nível `part`,
   mesmo nível visual dos volumes no sumário impresso — decidir se isso é
   aceitável ou se devem aparecer um nível abaixo do Volume II).
4. Verificar o log (`grep -a`): 0 erros, `same identifier` reduzido ao
   caso conhecido e inofensivo `page.1` (numeração romana/arábica);
   overfulls dentro do baseline (38, máx. 4,79 pt).
5. Inspeção visual das páginas do sumário (`pdftoppm`) para confirmar que o
   sumário impresso não mudou de aparência (a correção mira só os
   marcadores/âncoras).

## Observação

A regeneração desta sessão sobrescreveu o `Enciclopedia_Completa.tex` da
árvore (arquivo gerado, descartável por definição) com conteúdo derivado do
fonte atualmente quebrado — não commitado de propósito. Após o passo 1, o
passo 2 o recria correto.
