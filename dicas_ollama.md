# DICAS OLLAMA — Ambiente de IA local/cloud do projeto
_Gerado em 12/09/2026. **Revisado em 12/09/2026 pelo Kimi K2.7 Code** e
**reverificado em 13/09/2026** (cada item conferido por busca direta nos
arquivos `.tex`; ver o estado individual abaixo)._

## 1. Ambiente disponível (Aliware M16 — 8 GB VRAM + 32 GB RAM)
- **Roteador automático:** `~/bin/ai "pergunta"` (escolhe modelo por qualidade → velocidade → disponibilidade, com fallback). `ai status` mostra a matriz; `ai rota "pergunta"` mostra a cadeia. *(Verificado: existe em `~/bin/ai`.)*
- **Locais (100% GPU, sem quota):** `gemma4-e4b-mtp` (multimodal, 64K ctx, 172 tok/s), `llama3.1:8b` (49), `qwen2.5-coder:7b` (53), `qwen2.5:7b` (52).
- **Cloud via conta Ollama:** `glm-5.3-flash:cloud` (multimodal, 1M ctx, 2,8 s), `glm-5.3:cloud` (coding fronteira, 2,7 s), `deepseek-v4.1-flash:cloud` (9,4 s), `kimi-k2.7-code:cloud` (4,2 s).
- **CLIs pagas:** `claude` (Fable 5.1 — topo em coding/agentic) | `gemini` (créditos esgotados) | `qwen-cli` (config quebrada; **ausente do PATH** na verificação de 12/09).
- Ex.: `ollama run glm-5.3-flash:cloud "revise este capítulo: $(cat cap.tex)"`.

## 2. Benchmark aplicado (questão de raciocínio; correta = 156 km)
- ✔️ Corretos: glm-5.3 (2,7 s), glm-5.3-flash (2,8 s), kimi (4,2 s), deepseek (9,4 s), claude (5,0 s), gemma4 (21 s incl. load; 172 tok/s).
- ❌ Errados (locais): qwen2.5 (96 km), qwen2.5-coder (225 km), llama3.1 (210 km).
- **Implicação para o projeto:** tarefas de raciocínio/escrita longa → cloud; edição LaTeX simples → local.

## 3. Correções solicitadas (priorizadas — material avaliado 6,0/10)

> Estado em 13/09/2026: **(1) resolvida**; **(6) parcial**; **(2)–(5), (7) e
> (8) pendentes** — cada uma reverificada por busca direta no `.tex`, não por
> leitura de registro anterior. O método de verificação está anotado em cada
> item, para que a próxima sessão possa repeti-lo em segundos.

1. **~~[teorias.tex + Volume_I_Fundamentos.tex] Duplicação~~ → RESOLVIDO (12/09/2026).** `teorias.tex`, `theorias.tex` (duplicata com "h") e `teorias.pdf` foram removidos do repositório (commits `a32859f`/`e21349d`); `Volume_I_Fundamentos.tex/pdf` é o volume canônico de fundamentos (87 páginas, 25 referências). Não há mais duplicação a consolidar.
2. **[compressores.tex] Ponte pedagógica:** no Cap. 1, inserir tabela "Capítulo do método → capítulos de fundamentos exigidos" e prever leituras prévias. *(**Pendente, reverificado em 13/09/2026**: `grep -i "pré-requisito\|leitura prévia\|Volume 0"` em `compressores.tex` retorna **0 ocorrências**. **Nota de escopo:** o Volume 0 — Notações e Cálculo Básico — foi criado em 12/09 e já está completo (42 páginas); a tabela pode (e deve) apontar também para os capítulos do Volume 0, não só do Volume I.)*
3. **[compressores.tex] Antecipar o método:** adicionar "Parte 0 — Trilha Rápida do Gêmeo Digital" (10–15 pág.) antes do Cap. 19, com o ciclo completo (sensores → modelo físico → PIML → calibração → detecção → atuação). *(**Pendente, reverificado em 13/09/2026**: `grep -i "trilha rápida\|PARTE 0"` retorna **0 ocorrências**.)*
4. **[compressores.tex] Apêndice A — Glossário de notação unificado:** tabelas símbolo/definição/unidade cruzando termodinâmica × mecânica × ML (o texto já admite a fragmentação; falta resolvê-la). *(**Pendente, reverificado em 13/09/2026**: o único `\section*{Gloss...}` do arquivo é o **Glossário de Anglicismos** (linha 3984), criado em 23/08/2026 a partir do parecer Manus. Ele resolve os anglicismos, **não** a notação — são dois itens distintos, e é fácil confundir um pelo outro ao conferir às pressas. Não há `\appendix` no documento.)*
5. **[compressores.tex] Objetivos de aprendizagem** no início de cada capítulo (2–4 bullets) + **2–3 exercícios resolvidos** por capítulo da Parte II e gabarito em apêndice. *(**Pendente, reverificado em 13/09/2026**: `grep -i "Objetivos de Aprendizagem\|Exercício"` retorna **0 ocorrências** em `compressores.tex`. **Precedente útil:** o Volume 0 já implementou exatamente esse padrão em 12/09 — 18 exercícios resolvidos, 2 por capítulo, com resolução completa citando as equações do próprio volume e sem usar nada além do que o capítulo ensinou — e serve de modelo direto para a Parte II. Esta é também a recomendação 2 do parecer Manus que ainda não foi atendida.)*
6. **[compressores.tex] Completar o ciclo do DT:** adicionar seções sobre sincronização de dados/latência, estimação de estados (observador/Kalman), quantificação de incerteza, validação do gêmeo contra dados reais e hierarquia de fidelidade (surrogate × alta fidelidade). *(**PARCIAL em 13/09/2026** — este item deixou de ser pendente por inteiro:*
   - *✅ **Estimação de estados**: coberta pelos Caps. 21 e 28 (EKF, EKF com estado aumentado).*
   - *✅ **Quantificação de incerteza**: ganhou subseção própria — "Quantificação de Incerteza (UQ)", `compressores.tex:3431` — mais a propagação GUM da Eq. 25.3.*
   - *⚠️ **Sincronização de dados/latência**: aparece só como bullet no pipeline de ingestão (`:2988`) e em menções esparsas; sem seção própria.*
   - *❌ **Validação do gêmeo contra dados reais**: 0 ocorrências.*
   - *❌ **Hierarquia de fidelidade** (surrogate × alta fidelidade): 0 ocorrências da expressão; `surrogate` aparece 3× em outro contexto.*
   *Ou seja: restam duas lacunas reais (validação e hierarquia de fidelidade) e uma parcial (latência).)*
7. **[apresentacao_compressores.tex] Acessibilidade:** adicionar texto/narração aos slides que hoje dependem só de figuras. *(**Pendente, reverificado em 13/09/2026**: 24 slides, 10 `\includegraphics`, nenhum com descrição textual associada.)*
8. **[organização] Mover `Gemini_ajuste.pdf`** para `arquivos_apoio/` (não é material de ensino). *(**RESOLVIDO em 13/09/2026** — movido para `arquivos_apoio/` com `git mv`, preservando o histórico.)*

## 4. Regras de edição
- Idioma PT-BR; manter estilo LaTeX existente; **não quebrar a compilação** — rodar `latexmk -pdf <arquivo>.tex` (ou `pdflatex` em 3 passagens) após cada bloco de edições e conferir 0 erros.
- **Rótulos e sumário:** nunca editar o `.toc` manualmente — ele é regenerado automaticamente pelo LaTeX; ao renomear seções ou mover blocos, basta recompilar (duas passagens no mínimo) e conferir os avisos de referência no `.log`. Preservar rótulos `\label{}` existentes; novos rótulos seguem o padrão `prefixo-capitulo-numero` (ex.: `eq:v1-c4-10`, `fig:v0-c8-1`).
- **Sem marcas de IA** em texto, comentários ou metadados dos `.tex`/`.pdf` — verificação permanente do projeto.
- **Commits:** apenas o descrito, em português, estilo conventional (`feat:`, `fix:`, `docs:`, `chore:`); verificação final sempre por clone fresco lendo os blobs (`git cat-file -p origin/main:<arq> | md5sum`), pois leituras locais de objeto se mostraram não confiáveis nesta máquina (ver `CONTEXTO.md`, "Aprendizados operacionais").
