# Backlog — Edição Completa (`Enciclopedia_Completa.tex`)

> **STATUS: ENCERRADO — bloqueio corrigido e outline verificado (26/09/2026).**
> Os dois itens implementados na sessão de 16/09/2026 (pacote `bookmark` +
> âncoras por volume) já estavam corretos; o que impedia a verificação era
> um bug real no gerador de nomenclatura por capítulo, não nos dois itens em
> si. Ambos confirmados funcionando nesta sessão — ver "Verificação final"
> abaixo.

**Origem:** o autor apontou (16/09/2026) que, na união dos três volumes, os
marcadores do PDF (outline/sidebar) mostram os Volumes I e II aninhados como
subitens do Volume 0 — cada capítulo fica um nível abaixo do anterior, e o
Volume I terminava no nível 11, o II no nível 22. Os volumes são obras
independentes e devem aparecer como entradas irmãs de nível máximo.

## Implementado em 16/09/2026 (confirmado correto nesta sessão)

Em `scripts/gerar_edicao_completa.py`:

1. **Pacote `bookmark`** adicionado ao preâmbulo gerado (logo após o
   hyperref): o hyperref sozinho calcula o aninhamento dos marcadores de
   forma relativa e se perde com as páginas de volume feitas via
   `\addcontentsline{toc}{part}`; o `bookmark` recalcula os níveis a partir
   dos níveis absolutos gravados no `.out`.
2. **Âncoras únicas por volume** (`ancora_volume()`): junto ao
   `\setcounter{section}{0}` de cada volume, o gerador emite
   `\renewcommand` de `\theHsection`, `\theHequation`, `\theHfigure` e
   `\theHtable` com prefixo `v0`/`v1`/`v2`, evitando destinos duplicados
   entre volumes.

## Bloqueio real (encontrado e corrigido em 26/09/2026)

**Causa raiz — não era o `compressores.tex` em si, era o gerador auxiliar.**
`scripts/gerar_nomenclatura_por_capitulo.py` (trabalho em andamento de
13/09/2026, que insere a tabela "Símbolos deste capítulo" logo após o
`\section{...}` de cada capítulo) tinha um regex que não lida com chaves
aninhadas:

```python
re.finditer(r"\\section\{([^}]*)\}(\s*\\label\{[^}]*\})?", texto)
```

A maioria dos capítulos usa `\section{\textbf{Título}}` — duas chaves de
fechamento em sequência. `[^}]*` para no **primeiro** `}` encontrado, que é o
do `\textbf{}`, não o do `\section{}`. O script então inseria o bloco de
nomenclatura **entre** as duas chaves de fechamento, deixando o `\section{}`
aberto por cima de um bloco inteiro (parágrafo com `\begin{longtable}`) —
exatamente a violação de argumento-de-um-parágrafo-só que o `titlesec`
reportava (`Paragraph ended before \ttl@straight@i was complete`). Afetou
**13 capítulos** que usam `\textbf{}` no título (2–13 e 15); os capítulos sem
essa marcação (14, 16 em diante) nunca tiveram o bug, porque `[^}]*` fecha
corretamente quando há só uma chave de nível.

**Correção aplicada:**
1. `compressores.tex` corrigido diretamente (fechamento das 13 seções +
   remoção da chave solta que a inserção tinha deixado para trás), depois
   **regenerado do zero** rodando o gerador já corrigido — a versão final em
   árvore é a saída do script, não a edição manual intermediária.
2. `scripts/gerar_nomenclatura_por_capitulo.py`: o regex de localização de
   `\section{...}` agora trata explicitamente o caso `\textbf{...}` aninhado
   antes de cair no caso genérico:
   ```python
   padrao_secao = re.compile(
       r"\\section\{(?:\\textbf\{[^}]*\}|[^}]*)\}(\s*\\label\{[^}]*\})?"
   )
   ```
   Rodar `python3 scripts/gerar_nomenclatura_por_capitulo.py --check` depois
   de qualquer edição na Nomenclatura confirma que a contagem de capítulos
   com tabela própria (26) e de entradas (154) não muda sem querer.
3. Como efeito colateral **corrigido, não introduzido**: o `\markboth{}{}`
   do Capítulo 9 (encurta o cabeçalho corrente, ver `CONTEXTO.md`,
   "Verificação visual do PDF compilado") tinha sido deslocado pela mesma
   corrupção — a regenteração pelo script já corrigido o recolocou na
   posição certa (logo após `\section{...}`, antes do bloco de
   nomenclatura), sem edição manual adicional.

## Verificação final (26/09/2026)

1. **`compressores.tex`**: `pdflatex` 3×, **196 páginas, 0 erros, 0
   referências indefinidas, 0 labels duplicados** (fora o `page.1` já
   conhecido e inofensivo). **36 overfull hboxes, máximo 2,01 pt** — mesmo
   baseline documentado, sem regressão.
2. **Inspeção visual** (`pdftoppm`) da abertura do Capítulo 2 (página 16) e
   do Capítulo 9 (página 57): título, tabela "Símbolos deste capítulo" e
   corpo do texto renderizando corretamente, sem sobreposição; cabeçalho
   corrente do Capítulo 9 em uma linha só, sem colisão com o número de
   página.
3. **Regeneração**: `python3 scripts/gerar_edicao_completa.py` e
   `pdflatex -interaction=nonstopmode Enciclopedia_Completa.tex` 3× —
   **314 páginas, 0 erros, 0 referências indefinidas, 0 labels duplicados**
   (fora `page.1`). **38 overfull hboxes, máximo 4,79 pt** — mesmo baseline
   já documentado (soma dos baselines dos volumes avulsos), sem regressão.
4. **Outline** (`mutool show Enciclopedia_Completa.pdf outline`): "VOLUME 0",
   "VOLUME I" e "VOLUME II" aparecem todos com a mesma indentação (1 tab) —
   **irmãos de nível máximo**, não mais aninhados progressivamente. Os
   capítulos de cada volume ficam um nível abaixo (2 tabs) e as subseções
   dois níveis abaixo (3 tabs), como esperado.
5. **Sumário impresso** conferido por `pdftoppm` — aparência inalterada; a
   correção mirou só marcadores/âncoras, como previsto.

## Observação registrada, não corrigida (decisão do autor, não bug)

As **Partes I/II/III internas do Volume II** continuam entrando no outline no
mesmo nível dos volumes (`\addcontentsline{toc}{part}{...}`, herdado de
`compressores.tex`, não alterado nesta sessão). Isso já estava assim antes do
bloqueio e é uma decisão de arquitetura em aberto, não uma regressão: se o
autor quiser as Partes um nível abaixo do respectivo volume no outline, é uma
mudança separada em `gerar_edicao_completa.py` (rotular essas entradas com um
nível de bookmark explícito via `\pdfbookmark`/`\belowpdfbookmark` em vez de
`\addcontentsline{toc}{part}{...}`).

## Nada commitado

Regra permanente do projeto — aguardando revisão e autorização explícita do
autor antes de qualquer commit.
