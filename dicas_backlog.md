# Dicas de melhoria — como gerar backlog (livro e programação)

**Objetivo:** especializar, para este repositório, a metodologia genérica de
backlog — princípios gerais, template de item e anti-padrões viraram a skill
`gestao-backlog` (`.claude/skills/gestao-backlog/SKILL.md`; carregue-a antes
de escrever ou revisar qualquer item). A calibração de achado de revisor
externo (Copilot/Kimi/Gemini/Manus) virou a skill `calibracao-revisor-externo`
(`.claude/skills/calibracao-revisor-externo/SKILL.md`). Este arquivo traz só o
que é específico deste projeto: as varreduras do livro (`.tex`), as quatro
fontes de backlog de código, e os exemplos aplicados aos dois domínios. A
implementação em si já tem convenção em `CONTEXTO.md`, `CONTEXTO_kimi.md` e
`aplicativo/MANUTENCAO.md`. Sintetiza o que funcionou (`Backlog_volume0.md`,
`arquivos_apoio/Backlog_kimi_compress.md`, `Backlog_edicao_completa.md`).

---

## 3. Backlog do livro (`.tex`)

### 3.1 Varreduras que geram itens (baratas, rodam em minutos)

Cada uma pega uma classe de defeito inteira e já rendeu itens reais neste
repositório:

| Varredura | Como | Já pegou |
|---|---|---|
| Auto-referência de equação | para cada `\label{eq:sC-N}`/`eq:v0-*`/`eq:v1-*`, há `\eqref{eq:...}` no parágrafo anterior? | 110 de 208 equações sem citação prévia (15/08/2026) |
| `\eqref` dentro de bloco de exercício | o `\label` correspondente aparece **antes** no arquivo? | `\binom` nunca definido (Ex. 9.1 do Vol. 0) |
| Aspas retas em prosa | `grep -o '"' <arq>.tex \| wc -l` e conferir as ocorrências legítimas conhecidas | regressão no Cap. 29 (13/09/2026), visível no PDF |
| Booktabs | `\hline`, `tabular{`, `array{` | 11 tabelas em estilo antigo (26/07/2026) |
| Forma curta de legenda | `\caption{` sem o `[curta]` | 5 matrizes de diagnóstico |
| Floats sem fallback | `[h!]`/`[h!tbp]` | 47 floats |
| Labels duplicados / refs indefinidas | `grep -a` no `.log` (é Latin-1) | 633 destinos duplicados na Edição Completa |
| `\section*` de front matter sem `\markboth` | conferir Prefácio/Nomenclatura/Glossário/Agradecimentos | cabeçalho mentindo ("Lista de Tabelas" na Nomenclatura) |
| Contagem de palavras por capítulo | script Python sobre o `.tex` | Caps. 27 (605 p.), 25, 6, 20 como os mais curtos |
| Colisão de símbolo | cruzar símbolo novo com a Nomenclatura (alfabeto grego ~90% saturado no Vol. II) | — |
| `\bibitem` não citado | para cada chave, `\cite` existe? | `bloch`, `isa51` órfãs |
| Anglicismo sem entrada no glossário | comparar termos do texto com o Glossário de Anglicismos | ~40 termos cobertos desde 23/08/2026 |
| Exercício: o que a resolução usa está no enunciado/capítulo? | `grep` do símbolo no volume antes do ponto de uso | Ex. 9.1, 8.2 do Vol. 0 |

### 3.2 Critério de prioridade (o que cada nível significa)

- **P1 — bloqueia a leitura dos volumes seguintes.** O conteúdo é pressuposto
  por um capítulo de outro volume sem nunca ter sido ensinado (fasores → Cap. 7
  do Vol. I; derivada material → Cap. 2 do Vol. I).
- **P2 — formalismo usado explicitamente** nos volumes seguintes, sem o
  vocabulário (convenção de Einstein, teorema da divergência, autovalores).
- **P3 — didática e acabamento** (objetivos de aprendizagem, exercícios
  resolvidos, figura faltante).
- **P4 — cosmético ou decisão do autor** (redação de tabela, `ω`/`Ω`).

**Conformidade precede conteúdo.** Defeitos de convenção (aspas, booktabs,
`\clearpage`, auto-referência) entram antes de conteúdo novo — foi a ordem do
backlog do Volume 0 e evita corrigir o mesmo defeito duas vezes.

### 3.3 Restrições que o item precisa respeitar (ou vira item quebrado)

As regras de redação em si (equação ao fim do capítulo, `\eqref` de si mesma
antes de aparecer, `\ref`/`\caption[curta]{longa}` de figura e tabela, prefixo
de label por volume, sem marcas de IA) foram extraídas para a skill
`redacao-tecnica` — carregue-a ao escrever o item, em vez de reconferir esta
lista. Ficam aqui só as restrições específicas de **backlog** (não de prosa):

- Compilar 3× após cada bloco e conferir o log com `grep -a`; nunca editar `.toc`.
- A Edição Completa é **derivada e descartável**: mudou volume → regenerar
  (`scripts/gerar_edicao_completa.py`) e recompilar 3×; nunca editar
  `Enciclopedia_Completa.tex` à mão.
- **[Resolvido em 26/09/2026]** O `compressores.tex` chegou a ficar quebrado
  (13 blocos `NOMENCLATURA-CAP` inseridos dentro do argumento do `\section`,
  por um regex do gerador que não tratava `\textbf{}` aninhado) — já
  corrigido no `.tex` e no próprio gerador
  (`scripts/gerar_nomenclatura_por_capitulo.py`). Ver `Backlog_edicao_completa.md`
  para o diagnóstico completo; nenhum backlog novo precisa mais desse passo 0.

### 3.4 Fechamento de um item de livro

1. `pdflatex` 3× — 0 erros, 0 referências indefinidas.
2. Contagens comparadas ao baseline registrado (páginas, equações, overfulls:
   Vol. 0 = 0; Vol. I = 2, máx. 4,79 pt; Vol. II = 36, máx. 2,01 pt; Edição
   Completa = 38, máx. 4,79 pt). Overfull novo é regressão até provado o
   contrário.
3. `pdftoppm` nas páginas alteradas — o log esteve limpo em todas as versões
   da capa; o defeito só aparecia no render.
4. Varreduras de aspas + auto-referência.
5. Status atualizado no `.md` de origem, e entrada no `CONTEXTO.md` se for
   estrutural.

---

## 4. Backlog de programação (`aplicativo/`, `compressor2/`)

### 4.1 De onde vêm os itens (as quatro fontes)

1. **Matriz de cobertura livro ↔ app.** O código cita a equação que implementa;
   o caminho inverso (equações do livro sem contraparte no app) é a fonte
   natural de backlog e já vive em `MANUTENCAO.md` § "Escopo — o que está fora,
   de propósito". Manter essa lista viva em vez de re-derivá-la a cada sessão.
2. **Pendências registradas** nos `CONTEXTO*.md` — sempre re-verificadas, pois
   podem ter virado feito (houve entrada que dizia o oposto do real por várias
   sessões).
3. **Paridade Python × Rust.** `sistema.rs` e `sistema.py` devem concordar;
   divergência encontrada é item de backlog em qualquer dos dois lados.
4. **Catálogo × implementação.** 59 mecanismos de falha no livro (Tabela 28.2)
   × 10 cenários em `cenarios_falha.py` — a diferença é um backlog pronto,
   já numerado.

### 4.2 Filtro de observabilidade — o filtro que economiza mais tempo

Antes de promover "implementar a equação X" a item executável, perguntar:

> **Existe canal de medição para o parâmetro que a equação introduz?**

Se não existe, o item não é executável — é **bloqueado por instrumentação**, e
vai para a lista de escopo com a justificativa, não para o backlog. Caso real e
recorrente: do vetor Λ = [K, η_mec, ζ_ref, ζ_valv] (Eq. 28.1, 4 elementos), só
**K** é identificável — os outros três exigiriam potência elétrica, ΔP de
filtro e ΔP de válvula, canais que nem o EKF nem a Tabela 18.1 têm. A regra do
projeto é explícita: **nunca implementar um mecanismo "para constar" que não
mede nada de verdade.**

### 4.3 Classificação do item e critério de pronto

| Tipo | Critério de pronto |
|---|---|
| **Física nova** | função pura, docstring citando o nº da eq. (`"""Eq. 5.5 — ..."""`), parâmetro não fechado como `ASSUMIDO` em `constantes.py`, teste de sanidade direcional (a grandeza se move na direção física esperada) |
| **Algoritmo (EKF/VAE/PIML/MPC/PSO)** | resíduo físico conferido contra os rótulos **antes** de treinar (`pred_fake`); resíduo em unidade real normalizado pela própria escala; tolerância de `assert` calibrada por execução real, não teoria; validado em múltiplas sementes |
| **Identificação de parâmetro** | sensibilidade do resíduo ao parâmetro verificada em pontos de operação distintos antes de escrever o teste (K é quase inobservável em δ/L de comissionamento; identificável em δ/L=0,010) |
| **UI** | `AppTest` (pega exceção de import, `KeyError` de `session_state`, colisão de `key=`) + verificação no navegador quando há mudança visual; processo Streamlit reiniciado, não confiado ao autoreload |
| **Paridade Rust** | `cargo test --workspace` verde; concordância numérica `sistema.rs` × `sistema.py` |
| **Infra** | venv recriado quando ausente; dependência nova → suíte completa depois; módulo novo com `torch` chama `torch_device.obter_device()` |

### 4.4 Ordem de execução de um item de código

1. Baseline primeiro: rodar `venv/bin/pytest tests/ -q` **antes** de mexer
   (102 casos esperados; se o `venv/` não existe, recriar — ele nunca está na
   árvore).
2. Implementar com o diff mínimo e focado.
3. Suíte 100% verde.
4. Verificação de UI (§4.3).
5. Entrada nova no `CONTEXTO_app.md` (nunca reescrever entradas antigas).
6. Sincronia com o livro: **app primeiro, livro depois**, registrando a ordem.
7. **Nada de commit sem pedido explícito do autor.**

### 4.5 Fechamento de um item de código

- `pytest` completo + contagem de casos.
- UI verificada (AppTest ou navegador).
- Se o livro também mudou: `pdflatex` 3× e contagens de baseline.
- Status atualizado no `.md` de origem do item.

---

## 5. Anti-padrões

Lista genérica (item sem verificação, revisor externo sem checagem, reabrir
item encerrado, etc.) na skill `gestao-backlog`. Específico deste projeto,
fora da lista genérica:

- Inserir equação no meio de capítulo (renumeração em cascata) — regra
  completa na skill `redacao-tecnica`.

---

## 6. Rotina barata de fim de sessão

Rotina genérica (varreduras do que foi editado, comparar contra baseline,
atualizar status, estado do repositório limpo) na skill `gestao-backlog`, §5.
Neste projeto, a rotina completa de compilação/inspeção visual está na skill
`qa-compilacao-latex`; as varreduras específicas do livro (aspas,
auto-referência, booktabs, labels duplicados) estão na tabela §3.1 acima, e o
baseline de páginas/equações/overfulls está documentado em `CONTEXTO.md` e na
skill `redacao-tecnica`, §7.

---

## 7. Exemplo aplicado

**Livro** (padrão `Backlog_volume0.md`):

```markdown
### BK-14 — Hierarquia de fidelidade (surrogate × alta fidelidade)
- **Onde é exigido:** Cap. 27 (Implementação de Alta Performance) e Cap. 23
  (PIML) — o livro promete "horas para milissegundos" sem definir quando o
  substituto substitui e quando o modelo de alta fidelidade é obrigatório.
- **Gap (evidência):** `grep -ci "hierarquia de fidelidade" compressores.tex`
  → 0; `surrogate` aparece 3×, em outro contexto.
- **Ação:** subseção nova ao fim do Cap. 23, com critério de fidelidade por
  uso (controle em tempo real × auditoria), equação ao fim da subseção.
- **Verificação:** pdflatex 3×, 0 erros; varredura de auto-referência;
  pdftoppm nas páginas do Cap. 23.
- **Prioridade:** P2 — item 6 do `dicas_ollama.md`, já classificado como
  lacuna real na reverificação de 13/09/2026.
- **Status:** pendente.
```

**Programação** (padrão `MANUTENCAO.md` § Escopo):

```markdown
### APP-07 — Gerador de dataset multi-mecanismo
- **Onde é exigido:** Eq. 29.2 do livro (busca por resíduo mínimo generalizada
  sobre M ⊆ Tabela 28.2) e a sub-aba "Laboratório de Falhas" do app.
- **Gap (evidência):** `len(CATALOGO_CENARIOS)` → 10, contra 59 mecanismos da
  Tabela 28.2.
- **Ação:** varredura paramétrica sobre `sistema.simular()` combinando
  severidade × ponto de operação para cada mecanismo; saída: dataset rotulado.
- **Bloqueio a declarar no item:** mecanismos cujo parâmetro não tem canal de
  medição não entram (filtro de observabilidade, §4.2).
- **Verificação:** teste novo com 2 mecanismos e checagem de que o classificador
  (Eq. 29.2) recupera o rótulo correto em ambos.
- **Prioridade:** P1 — é o que destrava o item 7 das pendências do livro.
- **Status:** pendente.
```

---

*Gerado a partir da leitura dos 23 `.md` do repositório e de checagens diretas
no `.tex` e no código. Nada commitado — regra permanente.*
