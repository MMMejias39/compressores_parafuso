# Dicas de melhoria — `compressores.pdf`

Avaliação de qualidade do documento (151 páginas, A4, compilado em 16/08/2026,
3 passagens de `pdflatex`, a partir de `compressores.tex` no commit `f6cfefb`).
Diagnóstico geral: documento em excelente estado técnico-editorial — compilação
limpa, 0 referências indefinidas, 0 labels duplicados, 0 marcadores `??`, 0
caracteres de substituição/bytes de controle na extração. As convenções
permanentes do projeto (autocitação de equações, booktabs, `\clearpage` por
capítulo, larguras de figura padronizadas) estão **100% respeitadas** — ver
seção "Verificações de conformidade" ao final. Os itens abaixo são os poucos
ajustes pendentes, em ordem de prioridade.

## 1. Defeitos visuais reais (prioridade alta)

### 1.1 Cabeçalho corrente do Capítulo 28 quebra em duas linhas e colide com o número da página

- O título do Cap. 28 ("Estudo de Caso Integrado: Diagnóstico Precoce de
  Desgaste de Folgas via EKF, VAE, PIML e MPC/PSO", ~100 caracteres) é o mais
  longo do livro e não cabe em uma linha de cabeçalho. O `fancyhdr` o quebra em
  duas linhas, que avançam sobre a área do número de página — confirmado
  visualmente (`pdftoppm`, páginas 143–146 do PDF).
- O log registra **4× `Package fancyhdr Warning: \headheight is too small
  (15.0pt): Make it at least 27.11469pt`** a partir da página 142 — exatamente
  o trecho do Cap. 28. A necessidade de 27 pt (= duas linhas de texto) confirma
  que o cabeçalho está quebrando.
- É a **mesma classe de defeito já corrigida no Capítulo 9** em 15/08/2026
  (ver `CONTEXTO.md`, "bug de cabeçalho"): na época o `\markboth{...}{}` foi
  aplicado só ao Cap. 9, e o Cap. 28 foi criado depois, sem a correção. O
  fancyhdr não gera `Overfull \hbox` para essa colisão — o warning de
  `headheight` é o único sinal no log; o defeito em si só é visível por
  inspeção visual do cabeçalho.
- **Correção sugerida:** inserir `\markboth{Estudo de Caso Integrado: Diagnóstico
  Precoce de Desgaste de Folgas}{}` (ou forma curta equivalente, ~60 caracteres)
  logo após o `\section{}` do Cap. 28 (`compressores.tex:3398`). Não aumentar
  `\headheight` para 27 pt — isso deslocaria o corpo de texto de **todas** as
  páginas do livro para acomodar um único capítulo.
- **Regra preventiva sugerida:** todo título de capítulo com mais de ~65
  caracteres deve receber `\markboth{<forma curta>}{}` no momento da criação —
  vale para os volumes futuros da coleção.

## 2. Legendas sem forma curta (prioridade média)

- 5 das 37 legendas de tabela não têm a forma curta `\caption[curta]{longa}`:
  Tabelas 14.1 (`compressores.tex:1999`), 16.1 (`:2220`), 17.1 (`:2338`),
  18.1 (`:2399`) e 18.2 (`:2469`) — todas "Matrizes de diagnóstico" com
  legendas longas.
- Efeito concreto já visível na Lista de Tabelas: as entradas 16.1 e 17.1
  quebram em duas linhas cada, descaracterizando a lista como índice escaneável
  de uma página — exatamente o problema que motivou a convenção em 30/07/2026.
- **Correção sugerida:** adicionar a forma curta às 5 legendas (ex.:
  `\caption[Matriz de diagnóstico de tratamento primário]{...}` — a curta pode
  repetir a longa quando ela já é breve, como na 14.1).

## 3. Referências bibliográficas órfãs (prioridade média)

- Duas entradas do `thebibliography` não são citadas em nenhum ponto do texto:
  - `\bibitem{bloch}` (Bloch, *A Practical Guide to Compressor Technology*,
    `compressores.tex:3540`) — **achado novo**, não registrado no `CONTEXTO.md`.
  - `\bibitem{isa51}` (ANSI/ISA-5.1-2024, `compressores.tex:3504`) — órfã
    conhecida desde 02/08/2026 (pendência já registrada no `CONTEXTO.md`).
- Em ambos os casos a decisão é binária: citar onde o tema aparece (Bloch é
  citável nos capítulos de arquitetura/componentes; ISA-5.1 se a lista de
  instrumentos do Cap. 3 for retomada) ou remover da bibliografia. Referência
  não citada em obra de referência passa impressão de enchimento.

## 4. Warnings cosméticos (prioridade baixa)

- **13× `LaTeX Warning: '!h' float specifier changed to '!ht'`** — floats
  pedidos com `[!h]` que o LaTeX promove. Trocar `[!h]` por `[!htbp]` nos
  floats afetados elimina o ruído do log (sem mudança visual relevante, já que
  o LaTeX já impõe o `!ht` na prática). Mesmo item já apontado na versão
  anterior deste relatório (31/07/2026), ainda não endereçado.
- **2 underfull hboxes** — insignificantes.
- **1× `destination with the same identifier (name{page.1})`** — mistura de
  numeração romana/arábica; inofensivo, já conhecido.
- **35 overfull hboxes de ~2,01 pt** — todos na Nomenclatura (a palavra
  "adimensional" e similares), mesma magnitude já classificada como
  cosmeticamente insignificante em sessões anteriores. Não regrediu (baseline
  histórico: 31–35).

## 5. Sincronia entre livro e apresentação (prioridade baixa, decisão do autor)

- `apresentacao_compressores.tex` (Beamer, 21 slides) **não menciona a Parte
  III / Capítulo 28** — foi derivado do livro em 26/07/2026 e nunca atualizado
  com o estudo de caso integrado (adicionado em 15/08/2026). Como o
  `CONTEXTO.md` registra, a propagação não é automática: se os slides forem
  usados em reunião sobre a versão atual do livro, falta a "cereja" — a
  demonstração ponta a ponta EKF→VAE→PIML→MPC com números concretos, que é
  justamente o material mais vendável da obra. Sugestão: 1–2 slides novos
  resumindo o Cap. 28 (cenário δ/L, RUL ≈ 9 semanas, tabela de fluxo de dados).

## 6. Observações sem necessidade de ação

- **Aspas retas**: restam apenas 4 ocorrências, todas dentro de **comentários**
  do preâmbulo (`compressores.tex:25-26`, explicando o histórico de
  hifenização) — não são impressas, não violam a regra. Prosa e `verbatim`
  estão limpos.
- **`\cite[...]{shigley}`** aparece com argumento opcional (capítulo do livro)
  — uma varredura ingênua por `\cite{shigley}` falharia em encontrá-lo; a
  referência **está** citada e não é órfã.
- Capa: data automática vs. "Rev." — manter a convenção já estabelecida de
  revisão manual.

## Verificações de conformidade (o que foi conferido e está 100%)

Executadas por varredura programática sobre o `.tex` e sobre o texto extraído
do PDF (`pdftotext -layout`), nesta data:

- 209 labels `eq:s*-*`, **todos** com `\eqref` de si mesmos no parágrafo
  anterior (regra de 15/08/2026 — zero violações).
- 0 hardcodes do tipo `Equação~N.N` fora de `\eqref{}`.
- 0 `\hline`, 0 `tabular{|...|}`, 0 `array{|...|}` — booktabs em 100% das
  tabelas.
- 28 `\section` de capítulo, todos precedidos de `\clearpage`.
- Larguras de figura dentro das 3 categorias padronizadas + o `0.42` da capa
  (0.60 / 0.75 / 0.80 / 0.42 — nenhuma largura ad-hoc).
- Todas as figuras e tabelas referenciadas por `\ref{}` antes de aparecerem.
- Nenhuma linha em branco dentro de `\begin{equation}`.
- 0 referências a labels inexistentes; 0 labels duplicados.
- Extração do PDF: 0 bytes de controle (ligaduras), 0 U+FFFD, 0 `??`.

## Checklist resumido

- [ ] `\markboth{...}{}` no Cap. 28 (cabeçalho de 2 linhas + 4 warnings de
      `headheight`) — **prioridade alta**
- [ ] Forma curta de `\caption` nas Tabelas 14.1, 16.1, 17.1, 18.1 e 18.2
- [ ] Resolver os órfãos `\bibitem{bloch}` e `\bibitem{isa51}` (citar ou remover)
- [ ] Trocar `[!h]` por `[!htbp]` nos 13 floats (silencia warnings do log)
- [ ] (Opcional, decisão do autor) Atualizar `apresentacao_compressores.tex`
      com 1–2 slides da Parte III

— Relatório gerado em 16/08/2026 sobre `compressores.tex` @ `f6cfefb` (151 páginas).

## 7. Aprendizados das sessões do Volume I (12/09/2026)

- Nomear arquivos com o nome definitivo desde o início; nomes de trabalho
  temporários geram duplicatas (`teorias`, `theorias`, cópias datadas) que
  confundem o autor. Nome canônico do Volume I: `Volume_I_Fundamentos.tex/pdf`.
- Verificar sempre o estado real do repositório por clone fresco; índices e
  leituras locais de objeto podem divergir do remoto de forma não reproduzível.
- Comandos de stage seguros quando o índice local é suspeito:
  `git hash-object -w <arquivo>`, `git update-index --cacheinfo`,
  `git commit-tree` (mensagem com `-F <arquivo>`), `git update-ref`,
  depois `git push`; verificação final por `git cat-file -p origin/main:<arq>`.
