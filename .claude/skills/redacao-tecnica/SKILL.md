---
name: redacao-tecnica
description: Convenções obrigatórias de redação técnica desta coleção (Volume 0, Volume I, Volume II/compressores.tex e a Edição Completa gerada) — numeração e citação de equações, figuras e tabelas, aspas, estrutura de capítulo, veracidade de referências e critério de elaboração de exercícios. Carregar ANTES de escrever ou editar qualquer prosa, equação, figura, tabela ou exercício em um dos volumes .tex, ou antes de revisar um capítulo existente contra essas convenções.
---

# Redação técnica — Enciclopédia de Máquinas Rotodinâmicas

Estas são as regras permanentes do projeto para prosa e equacionamento nos
volumes `.tex` (`Volume_0_Notacoes_e_Calculo.tex`, `Volume_I_Fundamentos.tex`,
`compressores.tex`) e na Edição Completa gerada
(`scripts/gerar_edicao_completa.py` → `Enciclopedia_Completa.tex`, **nunca**
editada à mão). O histórico de *por que* cada regra existe — o achado ou
incidente que a motivou — está em `CONTEXTO.md`/`CONTEXTO_kimi.md`; esta skill
traz só a regra em forma acionável. Se uma regra aqui parecer ambígua num caso
concreto, ler a seção correspondente do `CONTEXTO.md` antes de decidir.

Esta skill cobre **prosa e equacionamento do livro**. Metodologia de backlog
(como levantar/priorizar/fechar item) está em `dicas_backlog.md`; convenções
de código do app Python estão em `aplicativo/MANUTENCAO.md`.

## 1. Equações

- Toda equação numerada usa `\begin{equation}\label{eq:<prefixo>}...\end{equation}`
  — nunca solta em `$...$`/`$$...$$` no meio do texto corrido, salvo troca de
  símbolo por valor numérico específico ou definição de termo num "Onde
  $X=...$" que já segue uma equação numerada.
- Prefixo do label por volume: `eq:v0-c<cap>-<n>` (Volume 0), `eq:v1-c<cap>-<n>`
  (Volume I), `eq:s<cap>-<n>` (Volume II). Preservar labels existentes.
- **Toda equação cita `\eqref{}` de si mesma no parágrafo que a antecede** —
  não basta explicar o conceito, o número tem que aparecer antes dela.
  Verificação: para cada `\label{eq:...}`, `\eqref{}` do mesmo label deve
  aparecer nos ~2-3 parágrafos anteriores.
- **Equação nova entra sempre ao fim do capítulo/subseção**, nunca no meio —
  a numeração é por posição física (`\numberwithin{equation}{section}`), e
  inserir no meio força renumeração em cascata de todos os labels e
  `\eqref{}` seguintes daquele capítulo, em qualquer volume que os cite.
- Referencie equações **sempre** por `\eqref{}`, nunca hardcode
  `Equação~9.6` como texto solto — nem mesmo em prosa que cita um capítulo
  diferente do que está sendo editado. Ao encadear várias referências em
  sequência (célula de tabela ou frase), usar vírgulas (`Eqs. 9.7, 9.18`),
  nunca barra sem espaço (`9.7/9.18/9.19` já causou overfull hbox por falta
  de ponto de quebra de linha).
- Nunca deixe linha em branco dentro de `\begin{equation}...\end{equation}`
  — quebra a compilação (diferente de `$...$`, que tolera).
- Verifique colisão de símbolo na Nomenclatura/Índice de Símbolos do volume
  antes de introduzir letra nova — o alfabeto grego já está ~90% saturado no
  Volume II. Símbolo reaproveitado com significado distinto em contextos que
  nunca coexistem na mesma equação é aceitável (documentado na tabela como
  "não confundir com..."), mas precisa de nota explícita nos dois pontos de
  uso, nunca silenciosa.

## 2. Figuras e tabelas

- `\label{fig:C-N}` / `\label{tab:C-N}`, sempre referenciadas por
  `Figura~\ref{}` / `Tabela~\ref{}` **antes** de aparecerem no texto — nunca
  "a figura/tabela abaixo".
- `\caption[curta]{longa}` sempre — sem a forma curta, a legenda inteira
  vaza para a Lista de Figuras/Tabelas e a torna ilegível como índice
  escaneável.
- Tabelas em `booktabs` (`\toprule`/`\midrule`/`\bottomrule`), nunca
  `\hline`/grade com barras verticais. Coluna de texto corrido largo usa
  `>{\raggedright\arraybackslash}p{Xcm}`, não `p{Xcm}` justificado puro.
- Larguras de figura padronizadas (Volume II): `0.60\textwidth` para
  gráficos/curvas técnicas; `0.75\textwidth` para diagramas com legenda/caixa
  de texto; `0.80\textwidth` para figura composta/complexa única; `0.55`
  para fotos verticais/estreitas; `0.42` para figura estreita ou thumbnail de
  capa. Escolher a categoria pelo tipo de conteúdo, não um valor ad-hoc.
- Floats sempre com fallback: `[h!tbp]`, nunca só `[h!]`.
- Imagem de terceiros só com licença livre **verificada na página real**
  (não só "parece livre" nem nome de arquivo sugestivo) — creditar autor,
  fonte e licença no próprio `\caption{}`.
- **Sempre renderizar e inspecionar visualmente** (`pdftoppm`) qualquer
  figura nova, e a página inteira onde ela entra — o log de compilação não
  acusa geometria errada (eixo trocado, bloco cortando outro, texto
  ilegível por causa de fonte pequena numa figura densa). Isso vale em
  dobro para figuras 3D geradas por `scripts/gen_figuras.py`.

## 3. Prosa

- Aspas **sempre** `` `` `` e `''`, nunca `"` reto em texto corrido — o
  babel-portuguese torna `"` um caractere ativo que engole o espaço
  seguinte (defeito invisível na compilação, só aparece na extração de
  texto ou em inspeção atenta do PDF). Exceção: dentro de `verbatim`
  (código), onde `"` deve continuar literal.
- Termo técnico em inglês recorrente ou acrônimo novo: acrescentar ao
  `\hyphenation{}` do preâmbulo (acrônimo sem nenhum ponto de quebra).
  Primeira ocorrência de anglicismo no corpo do texto: "termo em português
  (\textit{termo em inglês})"; o Glossário de Anglicismos ao fim do Volume
  II lista os já cobertos.
- **Sem marcas de IA** em texto, comentário ou metadado de nenhum `.tex`
  ou `.pdf` — regra permanente, sem exceção.

## 4. Estrutura de capítulo

- `\clearpage` imediatamente antes de todo `\section` de capítulo (Volume 0
  e Volume II seguem essa convenção; o Volume I é uma exceção conhecida e
  ainda pendente de decisão do autor — não copiar esse desvio para conteúdo
  novo).
- Título de capítulo com mais de ~65 caracteres provavelmente colide com o
  número de página no cabeçalho corrente (`fancyhdr`) sem gerar nenhum aviso
  de compilação — só aparece em inspeção visual. Adicionar
  `\markboth{<forma curta, ~60 caracteres>}{}` logo após o `\section{...}`
  (antes de qualquer bloco de nomenclatura gerado).
- Toda `\section*` de front matter (Prefácio, Nomenclatura/Índice de
  Símbolos, Glossário, Agradecimentos) também precisa do `\markboth{}{}`
  correspondente — `\section*` não atualiza `\leftmark` sozinha, e sem isso
  o cabeçalho corrente mente sobre em que seção o leitor está.
- Todo capítulo técnico (e anexo, se houver) termina com um bloco
  `\textbf{Diretriz Técnica Final:} ...` — uma consequência prática do
  capítulo para o Gêmeo Digital.

## 5. Veracidade de referências e fontes

- Nenhum `\bibitem` novo entra sem ser verificado contra fonte real
  (editora, periódico, DOI, número/edição de norma) — nunca por "parece
  familiar" ou de memória. Já houve título fabricado e norma citada sem a
  emenda/edição que o conteúdo pressupunha.
- Qualquer número de norma citado só como texto (sem `\cite`, por não haver
  `\bibitem` correspondente) deve ser verificado com o mesmo rigor antes de
  aparecer no texto — não copiar por proximidade de contexto com outra
  citação já existente.
- Quando outro volume já traz um `\bibitem` validado para o mesmo autor/obra,
  copiar a chave *verbatim* em vez de redigir uma nova.
- Toda informação factual (técnica, histórica, numérica) citada ao autor ou
  inserida no texto deve indicar a fonte de onde veio.

## 6. Critério de elaboração de exercícios (e de qualquer prosa didática)

Regra criada depois de achar exercícios com aritmética correta mas
elaboração falha — vale para exercício resolvido e para qualquer prosa que
"resolve" algo (exemplo numérico, estudo de caso):

1. **Fechamento pergunta↔resposta**: toda formulação que a resolução usa
   está anunciada no enunciado (como dado, equação citada, ou o próprio
   produto pedido) ou ensinada no capítulo — nunca aparece pela primeira vez
   dentro da resolução. Se falta a ferramenta, ensine-a no capítulo; não a
   contrabandeie na resposta.
2. **Responder o que foi perguntado**: se o enunciado pede um número, a
   resolução entrega aquele número, não um substituto conveniente. Regra
   prática/aproximação entra como comentário *depois* da resposta exata.
3. **Enunciado sem redundância nem ambiguidade**: cada grandeza aparece uma
   vez, com o tipo certo (escalar × vetor); todo termo técnico é definido
   ali ou no capítulo.
4. **Toda conta refeita à mão** antes de aceitar como correta — inclusive as
   dos comentários interpretativos.
5. **A leitura física decorre do que foi calculado** — não comparar
   grandezas incompatíveis nem concluir mais do que os números mostram.
6. **Coerência com a prosa do próprio capítulo** — a resolução não pode
   contradizer o que o capítulo já afirmou, nem atribuir efeito à causa
   errada.

Verificação barata: para cada símbolo/equação citado numa resolução, `grep`
o volume procurando onde foi definido **antes** daquele ponto. Um símbolo que
só aparece dentro da resolução é o sintoma.

## 7. Antes de declarar pronto

1. `pdflatex -interaction=nonstopmode <arquivo>.tex` **3 vezes** (ou
   `latexmk -pdf`) — 0 erros, 0 referências indefinidas, 0 labels
   duplicados. `<arquivo>.log` é **Latin-1**: use `grep -a`, nunca `grep`
   puro, ou a busca falha em silêncio.
2. Comparar contagem de overfull hboxes contra o baseline documentado
   (Volume 0 = 0; Volume I = 2, máx. 4,79 pt; Volume II = 36, máx. 2,01 pt;
   Edição Completa = 38, máx. 4,79 pt) — overfull novo é regressão até
   provado o contrário.
3. `pdftoppm` nas páginas alteradas e inspeção visual direta — o log limpo
   não garante que a página renderiza bem (colisão de cabeçalho, tabela
   cortada, figura com eixo trocado nunca aparecem como erro/warning).
4. Varreduras baratas de regressão, quando a sessão escreveu prosa nova:
   - Aspas retas: `grep -o '"' <arquivo>.tex | wc -l`, conferir cada
     ocorrência contra as legítimas já conhecidas (comentário de preâmbulo,
     `verbatim`).
   - Auto-referência de equação: cada `\label{eq:...}` tem `\eqref{}` de si
     mesma no parágrafo anterior?
   - `grep -noE "Equaç(ão|ões)~?[0-9]+\.[0-9]+"` — qualquer resultado é um
     hardcode de número que deveria ser `\eqref{}`.
5. Se a Edição Completa também precisa refletir a mudança: regenerar com
   `python3 scripts/gerar_edicao_completa.py` e recompilar 3× — nunca editar
   `Enciclopedia_Completa.tex` à mão, é artefato gerado e descartável.
6. **Nada de commit sem pedido explícito do autor** — regra permanente do
   projeto inteiro, livro e código.
