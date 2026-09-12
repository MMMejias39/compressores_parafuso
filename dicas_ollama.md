# DICAS OLLAMA — Ambiente de IA local/cloud do projeto
_Gerado em 12/09/2026. **Revisado em 12/09/2026 pelo Kimi K2.7 Code** (estado conferido no repositório; itens resolvidos marcados)._

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

> Estado em 12/09/2026: **(1) resolvida**; **(2)–(8) pendentes** — verificadas
> uma a uma contra o repositório.

1. **~~[teorias.tex + Volume_I_Fundamentos.tex] Duplicação~~ → RESOLVIDO (12/09/2026).** `teorias.tex`, `theorias.tex` (duplicata com "h") e `teorias.pdf` foram removidos do repositório (commits `a32859f`/`e21349d`); `Volume_I_Fundamentos.tex/pdf` é o volume canônico de fundamentos (87 páginas, 25 referências). Não há mais duplicação a consolidar.
2. **[compressores.tex] Ponte pedagógica:** no Cap. 1, inserir tabela "Capítulo do método → capítulos de fundamentos exigidos" e prever leituras prévias. *(Verificado: o Cap. 1 ainda não tem essa tabela. **Nota de escopo:** o Volume 0 — Notações e Cálculo Básico — foi criado em 12/09; a tabela pode (e deve) apontar também para os capítulos do Volume 0, não só do Volume I.)*
3. **[compressores.tex] Antecipar o método:** adicionar "Parte 0 — Trilha Rápida do Gêmeo Digital" (10–15 pág.) antes do Cap. 19, com o ciclo completo (sensores → modelo físico → PIML → calibração → detecção → atuação). *(Verificado: não existe no arquivo.)*
4. **[compressores.tex] Apêndice A — Glossário de notação unificado:** tabelas símbolo/definição/unidade cruzando termodinâmica × mecânica × ML (o texto já admite a fragmentação; falta resolvê-la). *(Verificado: o único glossário existente é o de Anglicismos, ao fim do documento — não resolve a notação.)*
5. **[compressores.tex] Objetivos de aprendizagem** no início de cada capítulo (2–4 bullets) + **2–3 exercícios resolvidos** por capítulo da Parte II e gabarito em apêndice. *(Pendente.)*
6. **[compressores.tex] Completar o ciclo do DT:** adicionar seções sobre sincronização de dados/latência, estimação de estados (observador/Kalman), quantificação de incerteza, validação do gêmeo contra dados reais e hierarquia de fidelidade (surrogate × alta fidelidade). *(Pendente — o Cap. 28 cobre EKF/VAE/PIML/MPC, mas os pontos de sincronização, latência, validação contra dados reais e hierarquia de fidelidade continuam sem seção própria.)*
7. **[apresentacao_compressores.tex] Acessibilidade:** adicionar texto/narração aos slides que hoje dependem só de figuras. *(Pendente.)*
8. **[organização] Mover `Gemini_ajuste.pdf`** para `arquivos_apoio/` (não é material de ensino). *(Verificado: o arquivo segue na raiz do repositório. Pendente.)*

## 4. Regras de edição
- Idioma PT-BR; manter estilo LaTeX existente; **não quebrar a compilação** — rodar `latexmk -pdf <arquivo>.tex` (ou `pdflatex` em 3 passagens) após cada bloco de edições e conferir 0 erros.
- **Rótulos e sumário:** nunca editar o `.toc` manualmente — ele é regenerado automaticamente pelo LaTeX; ao renomear seções ou mover blocos, basta recompilar (duas passagens no mínimo) e conferir os avisos de referência no `.log`. Preservar rótulos `\label{}` existentes; novos rótulos seguem o padrão `prefixo-capitulo-numero` (ex.: `eq:v1-c4-10`, `fig:v0-c8-1`).
- **Sem marcas de IA** em texto, comentários ou metadados dos `.tex`/`.pdf` — verificação permanente do projeto.
- **Commits:** apenas o descrito, em português, estilo conventional (`feat:`, `fix:`, `docs:`, `chore:`); verificação final sempre por clone fresco lendo os blobs (`git cat-file -p origin/main:<arq> | md5sum`), pois leituras locais de objeto se mostraram não confiáveis nesta máquina (ver `CONTEXTO.md`, "Aprendizados operacionais").
