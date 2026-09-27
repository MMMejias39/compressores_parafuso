# CONTEXTO_kimi.md — Gêmeo Digital de Sistemas de Compressão Offshore

## 1. Propósito deste arquivo

Este arquivo é o ponto de partida para sessões do Kimi Code neste repositório.
Leia-o por inteiro antes de propor qualquer alteração. Ele resume o projeto,
as convenções, o estado atual e a postura esperada de colaboração.

## 2. Visão geral

Este repositório contém a coleção *Enciclopédia de Máquinas Rotodinâmicas* e as
implementações de referência que a acompanham:

1. **O livro — Volume 0** (`Volume_0_Notacoes_e_Calculo.tex` → `.pdf`):
   *Notações e Cálculo Básico*. Volume de pré-requisitos matemáticos criado em
   12/09/2026: notação e linguagem simbólica, análise dimensional, funções,
   vetores, cálculo diferencial e integral, EDOs, séries e aproximações. 42
   páginas, 36 equações, 18 exercícios resolvidos.
2. **O livro — Volume I** (`Volume_I_Fundamentos.tex` → `.pdf`): *Fundamentos de
   Mecânica do Contínuo, Termofluidos e Sistemas de Medição*. Reúne os
   fundamentos de mecânica do contínuo, termodinâmica, mecânica dos fluidos,
   transferência de calor, sistemas de transferência, eletricidade, mecânica e
   instrumentação. 87 páginas, 158 equações, ~50 figuras vetoriais (TikZ/
   pgfplots versionadas no próprio `.tex`).
3. **O livro — Volume II** (`compressores.tex` → `compressores.pdf`): *Gêmeo
   Digital de Sistemas de Compressão Offshore*. Trata de compressores de
   parafuso rotativo isentos de óleo em plantas offshore e a metodologia de
   Gêmeo Digital (EKF, VAE, PIML, MPC, PSO, catálogo de 59 mecanismos de
   falha). 183 páginas, 227 equações, 28 figuras.
4. **O aplicativo Python** (`aplicativo/`): simulador web em Streamlit que
   implementa boa parte do Volume II. Cada equação do código cita a equação
   correspondente no livro. **5 abas** operacionais (Supervisório de Frota,
   Dashboard do Ativo, Diagnóstico & IA, Sistema & Dinâmica, Configurações),
   mais o Modo Treinamento ativado pela barra lateral.
5. **O aplicativo Rust 2.0** (`compressor2/`): reimplementação de alta
   performance (workspace Cargo, `sim_core` + servidor Axum/Tokio com SPA),
   criada em 27/08/2026. 26 testes unitários, conformidade WCAG 2.1 AA
   auditada.

Objetivo declarado: menor consumo energético, menor CO2eq e manutenção preditiva
baseada em condição real.

**Nomes canônicos — atenção.** `teorias.tex`/`teorias.pdf` foi o nome de
trabalho do Volume I e **não é mais o documento canônico** (removido do
repositório em 11/09/2026; a duplicata `theorias.*`, com "h", também). Se
esses arquivos aparecerem na árvore, são restos — ver "Aprendizados
operacionais" no `CONTEXTO.md` sobre a instabilidade que atingia qualquer
arquivo chamado `teorias.*` nesta máquina.

## 3. Estrutura do repositório

```
├── Volume_0_Notacoes_e_Calculo.tex/.pdf  # Volume 0 — pré-requisitos matemáticos
├── Volume_I_Fundamentos.tex/.pdf         # Volume I — fundamentos teóricos
├── compressores.tex/.pdf                 # Volume II — gêmeo digital
├── apresentacao_compressores.tex/.pdf    # apresentação Beamer derivada (24 slides)
├── CONTEXTO.md               # histórico cronológico dos livros
├── CONTEXTO_app.md           # histórico cronológico do app
├── CONTEXTO_kimi.md          # este arquivo
├── README.md                 # entrada geral do repositório
├── aplicativo/               # app Streamlit (Python)
│   ├── app.py
│   ├── compressor_sim/       # motor de cálculo + EKF/VAE/PIML/MPC/PSO
│   ├── tests/                # test_simulador.py, test_pi_treinamento.py
│   ├── README.md, IMPLEMENTACAO.md, GUIA_CODIGO.md, MANUTENCAO.md
│   └── ...
├── compressor2/              # app Rust 2.0 (workspace Cargo)
│   └── crates/{sim_core,app}/
├── scripts/                  # scripts de geração de figuras (Volume II)
│   ├── gen_figuras.py        # figuras matplotlib/3D
│   ├── bl_*.py               # scripts Blender para renders
│   └── blender_common.py
├── figuras/                  # figuras PDF usadas no Volume II
├── figuras_blender/          # renders PNG intermediários
└── arquivos_apoio/           # notas, backlogs, relatórios externos (NÃO TOCAR
                              # sem pedido explícito do autor)
```

## 4. Postura de trabalho e ética de colaboração

O autor (Marcelo Moreira Mejias) espera que a IA atue como **coautora técnica**, não como mera ferramenta de execução. Isso significa:

- Leia o contexto antes de agir. Não reinvente convenções já estabelecidas.
- Questione propostas ruins com evidência, mas respeite a decisão final do autor.
- Verifique antes de declarar pronto: compile o `.tex`, rode os testes, abra o
  app no navegador quando for pertinente.
- Não faça `commit` ou `push` sem pedido explícito do autor.
- Mantenha o diff mínimo e focado. Limpeza oportunista não é bem-vinda.
- Documente decisões em `CONTEXTO.md` / `CONTEXTO_app.md` quando forem
  estruturais.
- Se houver dúvida de escopo, pergunte. Não assuma.
- Colabore com o Claude como coautora complementar: o livro e o app são
  produtos únicos, e ambas as IAs devem manter consistência com as decisões
  registradas nos contextos, não criar estilos ou convenções divergentes.

Sobre autoria: a direção intelectual, o juízo de engenharia, a arquitetura do documento e as decisões finais são do autor. A IA colabora com redação, diagramação, código, verificação e sugestões. A atribuição de crédito é uma decisão do autor; a IA não deve exigir coautoria, mas um agradecimento genérico em "Agradecimentos" é razoável se o autor julgar adequado.

## 5. Convenções técnicas

### Livros (`compressores.tex`, `Volume_I_Fundamentos.tex`, `Volume_0_Notacoes_e_Calculo.tex`)

**Regras de redação (numeração/citação de equação, figura, tabela, aspas,
estrutura de capítulo, veracidade de referência, critério de exercício):
carregar a skill `redacao-tecnica`** (`.claude/skills/redacao-tecnica/SKILL.md`)
antes de escrever ou revisar prosa/equações — ela vale para qualquer IA que
trabalhe neste repositório (Claude ou Kimi), não é específica de sessão.

Fatos específicos deste projeto que a skill não cobre (não são regra de
redação genérica, são convenção de organização de arquivo):
- Compilar com `pdflatex` 3 vezes (ou `latexmk -pdf`). **`compressores.log` é
  Latin-1** — use `grep -a`, senão a busca falha em silêncio.
- Numeração de equações por volume: `eq:v0-c<cap>-<n>` (Vol. 0),
  `eq:v1-c<cap>-<n>` (Vol. I), `eq:s<cap>-<n>` (Vol. II).
- Figuras do Vol. II em `figuras/fig_<cap>_<n>_<desc>.pdf`, geradas por
  `scripts/gen_figuras.py`. **Vol. 0 e Vol. I usam figuras vetoriais TikZ/
  pgfplots escritas no próprio `.tex`** — não há gerador externo para eles.
- `\clearpage` antes de todo `\section` de capítulo. **Exceção conhecida e
  ainda em aberto: o Volume I não usa nenhum `\clearpage`** (10 capítulos, 0
  ocorrências) — desvio da convenção, pendente de decisão do autor.
- Nomenclatura centralizada no início de cada volume (Volume II: distribuída
  também por capítulo desde 13/09/2026, via
  `scripts/gerar_nomenclatura_por_capitulo.py` — ver `CONTEXTO.md`,
  "Backlog_edicao_completa.md" para o histórico do bug já corrigido nesse
  gerador).

### App Python (`aplicativo/`)

- Ambiente: `python3 -m venv venv`, `venv/bin/pip install -r requirements.txt`,
  `venv/bin/streamlit run app.py`. **O `venv/` não existe na árvore atual** —
  precisa ser recriado antes de rodar ou testar.
- Testes: `venv/bin/pytest tests/` — 86 funções de teste, 102 casos executados
  (três parametrizadas: PDP, `n_vasos`, catálogo de 10 cenários de falha).
- `torch` vem do índice padrão do PyPI (build com CUDA embutido);
  `compressor_sim/torch_device.py` decide GPU/CPU em tempo de execução.
- Cada função do núcleo cita a equação do livro que implementa. Parâmetros
  `ASSUMIDO` quando o livro não fecha valor devem ser sinalizados no código e
  na UI.
- UI: 5 abas na ordem estabelecida; ver no navegador antes de finalizar. Se o
  Claude-in-Chrome não estiver disponível, use `streamlit.testing.v1.AppTest`
  — pega colisão de `key=`, exceções de import e `KeyError` de `session_state`
  que o `pytest` não pega.

### App Rust (`compressor2/`)

- `cargo test --workspace` (26 testes) e `cargo run --bin compressor2`
  (servidor em `localhost:8080`).
- Física espelhada do Python: `sistema.rs` e `sistema.py` devem concordar.

## 6. Estado atual (verificado em 13/09/2026)

### Volume 0 — `Volume_0_Notacoes_e_Calculo.tex`
- Criado em 12/09/2026; backlog por criticidade (`Backlog_volume0.md`)
  implementado **8/8** no mesmo dia.
- 42 páginas, 10 capítulos, 36 equações, 7 figuras, 7 tabelas, 18 exercícios
  resolvidos. Compilação 3× com 0 erros, 0 overfulls, 0 referências
  indefinidas; varredura de auto-referência 0/36.

### Volume I — `Volume_I_Fundamentos.tex`
- 87 páginas, 158 equações, ~50 figuras vetoriais. Compilação limpa; os únicos
  overfulls são os dois de baseline (0,8 pt no Cap. 2; 4,8 pt na tabela de
  sensores do Cap. 9).
- **Todos os capítulos de conteúdo já foram reescritos** ao padrão "base física
  → hipótese com limites de validade → relações constitutivas → especializações
  → síntese": Cap. 2 Mecânica do Contínuo (825 linhas), Cap. 3 Termodinâmica
  (559), Cap. 4 Fluidos (527), Cap. 5 Transferência de Calor (539), Cap. 6
  Sistemas (402), Cap. 7 Eletricidade (1094), Cap. 8 Mecânica (349).
- **O mais curto e o candidato natural para a próxima expansão é o Cap. 9,
  Instrumentação e Medição (135 linhas)** — único que ainda não passou pela
  reescrita. O Cap. 10 (Síntese, 138 linhas) é curto por natureza.
- Bibliografia ampliada em 12/09 com indicações do autor (Özisik, Laney,
  Tenenbaum, Rollins, Filippo Filho, Bloch & Geitner, Nussenzveig, Fox &
  McDonald). Diretriz permanente: **usar as melhores bibliografias do mundo**,
  independentemente de país; obras nacionais entram por indicação do autor ou
  quando forem a melhor da categoria.

### Volume II — `compressores.tex`
- 183 páginas, 227 equações, 28 figuras, 59 mecanismos de falha catalogados
  (Tabela 28.2). 36 overfull hboxes, o maior com 2,01 pt — baseline
  documentado e cosmeticamente insignificante.
- Partes I (Caps. 2–18), II (19–27) e III (28–29, metodologia + estudo de caso
  integrado). Glossário de Anglicismos ao fim, antes da bibliografia.
- Todos os relatórios externos recebidos até hoje estão **encerrados**:
  `relatorio_diagramacao.md`, `dicas_kimi.md` (31/07 e 16/08),
  `dicas_COPILOT.md`, `Manus_parecer_final_compressores.md`,
  `Backlog_kimi_compress.md` (13/13) e `Gemini_ajuste.pdf`.
  `melhorias_gemini.md` está majoritariamente vencido — ver o cabeçalho de
  status no próprio arquivo.

### Apps
- **Python**: 5 abas, 86 funções de teste / 102 casos, Parte II completa (EKF,
  VAE, PIML, MPC, PSO) mais três caminhos de identificação de $K$ (EKF
  aumentado, PIML inverso, Levenberg-Marquardt). Painel de Falhas cobre 10 dos
  59 mecanismos. **`venv/` ausente na árvore atual.**
- **Rust 2.0**: 26 testes, 7 nós termodinâmicos, telemetria PI, supervisório de
  frota, ASME VIII Div. 1, WCAG 2.1 AA.
- Pendências do app: 49 mecanismos de falha restantes, treino multi-mecanismo,
  sensores portáteis, $\zeta_{valv}$, supervisório com estado persistente.

### Pendências abertas nos livros (verificadas em 13/09/2026)
1. `dicas_ollama.md` itens 2, 3, 4, 5, 7 e 8 — ver o próprio arquivo, que traz
   o estado conferido de cada um.
2. Cap. 6 do Vol. II segue sem nenhuma figura (única lacuna gráfica da Parte I).
3. Volume I sem `\clearpage` — decisão do autor.
4. Vol. II: validação do gêmeo contra dados reais e hierarquia de fidelidade
   (surrogate × alta fidelidade) ainda não têm seção própria.
5. Redes Bayesianas (Cap. 25) continuam citadas só por nome, sem equação.

## 7. O que fazer ao retomar

1. Ler `README.md`, `CONTEXTO.md` (fim) e `CONTEXTO_app.md` (fim).
2. Verificar `git status` e `git log --oneline -10` para saber o estado real —
   nunca confiar em hash ou contagem citada de memória em arquivo de contexto.
3. Se for mexer nos livros: carregar a skill `redacao-tecnica` antes de
   escrever qualquer prosa/equação, depois compilar 3× e inspecionar
   visualmente as páginas afetadas com `pdftoppm` (skill, seção 7).
4. Se for mexer no app: recriar o `venv` se necessário, rodar `pytest tests/` e
   abrir o Streamlit no navegador (ou `AppTest`).
5. Atualizar os `CONTEXTO*.md` correspondentes ao final da sessão, se o autor
   pedir "atualize contexto" ou se a mudança for estrutural.

## 8. Nota sobre qualidade e verificação

Antes de declarar uma tarefa concluída:
- Livro: checklist completo na skill `redacao-tecnica`, seção 7 (3 passagens
  de `pdflatex`, comparação com o baseline de overfulls, `pdftoppm` visual,
  varreduras de aspas/auto-referência).
- App: `pytest tests/` passando; verificar a UI no navegador quando houver
  mudança visual.
- Código: não deixar prints de debug, não alterar testes para encobrir bugs,
  não commitar sem autorização.
- **Relatório externo (Kimi, Gemini, Copilot, Manus): verificar cada achado
  contra o texto real ANTES de implementar, não depois.** Já houve falso
  positivo (Eq. 13.2 do Gemini) e diagnóstico de causa errado (Copilot).

---

*Última atualização: 13/09/2026 — estado conferido diretamente contra os
arquivos do repositório, não contra registros anteriores.*
