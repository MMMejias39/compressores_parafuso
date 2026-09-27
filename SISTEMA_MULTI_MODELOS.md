# 🤖 SISTEMA MULTI-MODELOS — leia isto ao iniciar qualquer instância

**Instância de IA:** este arquivo documenta o sistema de IA multi-modelo já instalado
neste computador. Antes de chamar APIs externas, use o que já está configurado aqui.

## Como usar (terminal)
- `ai "pergunta"` → roteia automaticamente (qualidade → velocidade → disponibilidade, com fallback)
- `ai rota "pergunta"` → mostra a cadeia de modelos sem executar
- `ai status` → matriz de modelos/velocidade/quota
- `ai` → menu interativo (também: `ai 1`…`ai 11`, `ai deepseek`, `ai claude`)
- Script: `~/bin/ai` | PATH já configurado no `~/.bashrc`

## Modelos locais (GPU 8 GB — gratuitos, sem quota)
| Modelo | Especialidade | Velocidade |
|---|---|---|
| `4skl/gemma4-e4b-mtp` | multimodal (visão/áudio), 64K ctx — PADRÃO p/ simples | ~172 tok/s |
| `qwen2.5-coder:7b` | código curto | ~53 tok/s |
| `qwen2.5:7b` | raciocínio leve | ~52 tok/s |
| `llama3.1:8b` | uso geral | ~49 tok/s |

## Modelos cloud (conta Ollama do usuário)
| Modelo | Especialidade | Benchmark (questão-trem) |
|---|---|---|
| `glm-5.3-flash:cloud` | multimodal, 1M ctx, análise complexa | ✔ 156 km em 2,8 s |
| `glm-5.3:cloud` | coding de fronteira | ✔ 2,7 s |
| `kimi-k2.7-code:cloud` | agentic coding | ✔ 4,2 s |
| `deepseek-v4.1-flash:cloud` | visão nativa, raciocínio | ✔ 9,4 s |

## CLIs agentic (contas pagas)
- `claude` — Fable 5.1/Mythos (topo em coding/knowledge work) — ✔ ativa
- `gemini` — ⛔ créditos esgotados (429) — recarregar em ai.studio/projects
- `qwen` (Qwen Code) — ⚠️ config quebrada: aponta p/ modelo removido `gemma4:26b` + exige OPENAI_API_KEY

## Cadeias de roteamento (implementadas em ~/bin/ai)
- Simples → gemma4 → llama → glm-flash
- Raciocínio complexo → glm-flash → deepseek → glm-5.3 → claude
- Código complexo → claude → kimi → glm-5.3
- Código simples → qwen2.5-coder → kimi
- Visão → gemma4 (imagem anexa) → glm-flash
- Força manual: incluir "usar local" ou "na nuvem" na frase

## Regras de projeto (definidas pelo usuário)
1. Tarefa rápida/rodável local → usar LOCAL; complexa ou pesada demais → cloud.
2. Distribuir por melhor qualidade da especialidade; empate → mais rápido; depois → tokens disponíveis.
3. Ao falhar (quota/429/modelo inexistente) → pular automaticamente para o próximo da cadeia.

## Projeto ativo
*(Atualizado em 13/09/2026, reverificado em 27/09/2026 — o parágrafo anterior
descrevia o projeto como "material de ensino... avaliação 6,0/10; revisão em
curso pelo Kimi", estado de 12/09 já superado.)*

`~/Documentos/Compressores/` — coleção *Enciclopédia de Máquinas Rotodinâmicas*
mais duas implementações de referência:

| Artefato | Estado |
|---|---|
| **Volume 0** `Volume_0_Notacoes_e_Calculo.tex` | 42 p., 36 eq., 18 exercícios — backlog 8/8 |
| **Volume I** `Volume_I_Fundamentos.tex` | 87 p., 158 eq., ~50 figuras vetoriais |
| **Volume II** `compressores.tex` | 196 p., 228 eq., 28 figuras, 59 mecanismos de falha |
| **App Python** `aplicativo/` | Streamlit, 5 abas, 86 funções de teste / 102 casos |
| **App Rust** `compressor2/` | Axum + `sim_core`, 26 testes, WCAG 2.1 AA |

*(Volume II: "183 p., 227 eq." era status congelado desde 13/09/2026 — ver
`CONTEXTO.md`, "Correção do bloqueio de compilação + skill redacao-tecnica",
27/09/2026.)*

**Todos os relatórios de revisão externa estão encerrados** (Manus, Copilot,
Kimi 31/07 e 16/08, Gemini, Backlog Kimi 13/13, Backlog Vol. 0 8/8, Backlog
Edição Completa) — cada arquivo traz o cabeçalho de status com a verificação
item a item. As pendências que restam estão em `dicas_ollama.md` (itens 2–5 e
7) e na entrada de reverificação ao fim do `CONTEXTO.md`.

**Regras de redação técnica** (equação, figura, tabela, aspas, exercício):
skill `redacao-tecnica` (`.claude/skills/redacao-tecnica/SKILL.md`), criada
em 26/09/2026 — carregar antes de escrever ou revisar prosa de qualquer
volume, em vez de reler o `CONTEXTO.md` inteiro em busca da regra.

**Antes de rodar o app Python:** o `aplicativo/venv/` não existe na árvore —
recriar com `python3 -m venv venv && venv/bin/pip install -r requirements.txt`.
