# Plano de Manutenção

Como manter, estender e verificar este simulador com segurança. Para
arquitetura/decisões, ver `IMPLEMENTACAO.md`; para o que cada arquivo faz,
ver `GUIA_CODIGO.md`.

## Ciclo de vida de uma mudança

1. **Ler `../CONTEXTO_app.md` inteiro antes de mexer em qualquer coisa** —
   é o registro cronológico de decisões, achados e armadilhas já
   encontradas; evita redescobrir (ou reintroduzir) o mesmo bug duas vezes.
2. Implementar.
3. Rodar `venv/bin/pytest tests/ -q` — precisa ficar 100% verde antes de
   qualquer outra verificação.
4. Verificar a UI (ver "Como verificar mudanças na UI" abaixo).
5. Atualizar `CONTEXTO_app.md` com uma entrada nova (o que mudou, por quê,
   o que foi verificado) — nunca reescrever entradas antigas.
6. Se a mudança também afetar o livro (nova equação, correção), replicar
   lá **também** — ver "Sincronia entre livro e app" abaixo.
7. Nunca commitar sem pedido explícito do autor (regra permanente do
   projeto inteiro, livro e app).

## Como adicionar uma equação nova do livro

Checklist, na ordem:

1. Localizar a equação no `../compressores.tex` (número, capítulo, símbolos
   já usados na Nomenclatura) — nunca implementar de memória.
2. Escrever uma função **pura** (sem efeito colateral, sem acessar
   `params`/dicionários globais) em `nucleo.py` (física de estágio/motor/
   psicrometria) ou `subsistemas.py` (trocadores, PSA, vaso) — a que for
   mais parecida com as vizinhas já existentes. Docstring cita a equação:
   `"""... Eq. C.N — <fórmula em texto> """`.
3. Todo parâmetro numérico que a equação introduz e que o livro **não**
   fecha vai para `constantes.py` como `NOME_DEFAULT = valor  # ASSUMIDO
   (justificativa curta)`.
4. Encadear a chamada em `sistema.py`, no ponto certo da cascata (ver
   `GUIA_CODIGO.md` § `sistema.py` para a ordem dos 8 passos) — se o valor
   for um KPI, entra no dicionário `kpis` do retorno; se for um novo ponto
   de estado, no formato já usado em `nos`.
5. Se a equação precisar de um controle na UI, adicionar o slider/input no
   `st.expander` correspondente em `app.py`, com a mesma label "(assumido)"
   quando aplicável.
6. Escrever pelo menos um teste de sanidade física (a grandeza se move na
   direção certa quando o parâmetro-chave muda) em
   `tests/test_simulador.py`, no bloco do módulo correspondente.
7. Rodar a suíte inteira, não só o teste novo.
8. Documentar em `CONTEXTO_app.md` e, se for equação nova (não já coberta
   no `.tex`), considerar se o livro também precisa da citação.

## Como estender um dos 5 algoritmos de IA (EKF/VAE/PIML/MPC/PSO)

Mesma checklist acima, mais estes cuidados específicos, aprendidos de bugs
reais já encontrados (ver `CONTEXTO_app.md` para o diagnóstico completo de
cada um — resumo aqui):

- **Qualquer resíduo físico reimplementado em PyTorch** (não chamando
  `sistema.simular()` diretamente, porque precisa ser diferenciável) deve
  ser conferido contra os rótulos reais **antes** de treinar uma rede em
  cima dele: gere um pequeno dataset com `gerar_dataset()`, substitua a
  predição da rede pelos próprios rótulos (`pred_fake = torch.tensor(saidas,
  dtype=torch.float32)`), e confira que o resíduo é ~0 no valor correto do
  parâmetro físico e cresce monotonicamente para valores errados — só
  depois disso rodar um treino completo. Foi assim que o bug do problema
  inverso do PIML (16/08/2026, viés por ignorar a correção psicrométrica)
  foi encontrado e corrigido, em vez de gastar ciclos de treino tentando
  "consertar" hiperparâmetros de um resíduo com fórmula errada.
- **Todo resíduo físico em unidades reais (W, kg/s) precisa ser normalizado
  pela própria escala** antes de entrar na perda — sem isso, o primeiro
  passo de otimização satura a rede (unidades `tanh` presas em ±1) antes
  que qualquer balanceamento adaptativo de λ tenha chance de agir.
- **Identificação de parâmetro (EKF aumentado ou PIML inverso) só funciona
  se o parâmetro tiver efeito observável na escala do cenário testado** —
  antes de escrever um teste ou depurar convergência ruim, verifique a
  sensibilidade do resíduo/medição ao parâmetro em pontos de operação
  distintos (ex.: o efeito de K na Eq. 9.3 escala com δ/L — em δ/L de
  comissionamento, 0,002, K é quase inobservável frente a ruído de sensor
  típico; em δ/L=0,010, já é identificável). Um problema mal condicionado
  parece, à primeira vista, um bug de treino, mas é uma limitação física
  real do cenário escolhido.
- **Tolerâncias de teste sempre calibradas numericamente antes de
  escrever o `assert`** — rode o cenário via `python -c`, observe a
  convergência real (não uma expectativa teórica), só então escolha a
  margem. Testar em múltiplas sementes/pontos de partida antes de fixar.

## Dependências

- `streamlit`, `numpy`, `matplotlib`, `pytest`, `scipy`, `torch`, `pandas`,
  `openpyxl`: todas instaladas via `pip install -r requirements.txt`, sem
  cuidado especial. `pandas`/`openpyxl` (16/08/2026) servem o importador de
  telemetria do Conector PI System (sub-aba de "Sistema & Dinâmica";
  `pd.read_csv`/`pd.read_excel` do upload de arquivo) —
  `openpyxl` é o *engine* que o pandas exige para ler `.xlsx`, não usado
  diretamente no código.
  `torch` vem do índice padrão do PyPI (build com CUDA embutido, ~2GB a
  mais que um build CPU-only, mas funciona em máquinas com ou sem GPU
  NVIDIA sem precisar escolher índice manualmente) — **até 15/08/2026** o
  projeto usava deliberadamente um build CPU-only à parte (índice dedicado,
  `pip install torch --index-url .../cpu`), decisão revertida em
  16/08/2026 a pedido do autor para aproveitar a GPU quando disponível (ver
  `../CONTEXTO_app.md`, "Uso de GPU (CUDA) quando disponível"). Se algum
  dia for preciso voltar ao build CPU-only (ex.: ambiente de CI sem GPU e
  sensível a tamanho de imagem), o índice dedicado continua a forma
  correta de instalar — não é preciso reintroduzir isso no
  `requirements.txt` a menos que vire a prática padrão de novo.
- **Qualquer módulo novo que use PyTorch deve chamar
  `torch_device.obter_device()`** para escolher o device, em vez de deixar
  tensores no default implícito — ver `vae.py`/`piml.py` para o padrão
  (modelo e todo tensor do laço de treino movidos para `device`; saída de
  volta para NumPy sempre via `.cpu().numpy()`, nunca `.numpy()` direto,
  que falha se o tensor estiver em GPU).
- Ao atualizar qualquer dependência, rodar a suíte de testes completa
  depois — `numpy`/`torch` têm histórico de mudanças de API que quebram
  código numérico silenciosamente (sem erro, resultado diferente).

## Como verificar mudanças na UI

Em ordem de preferência:

1. **Claude-in-Chrome** (se a extensão estiver conectada): subir o
   servidor (`venv/bin/streamlit run app.py --server.headless true
   --server.port 8501`), navegar até `localhost:8501`, interagir de
   verdade com os controles alterados, conferir console sem erros,
   encerrar o servidor ao final (`pkill -f "streamlit run app.py"`) — não
   deixar rodando.
2. **`streamlit.testing.v1.AppTest`** (sempre disponível, mais rápido, sem
   navegador) quando a extensão não estiver conectada:
   ```python
   from streamlit.testing.v1 import AppTest
   at = AppTest.from_file("app.py", default_timeout=120)
   at.run()
   assert not at.exception
   # inspecionar at.metric, at.subheader, etc. por valores plausíveis
   ```
   Roda as 5 abas inteiras a cada execução (todo `with tab_x:` executa,
   independente de qual aba estaria visualmente selecionada, incluindo o
   conteúdo do Modo Treinamento quando ativado) — pega
   exceções de import, `KeyError` de `session_state` e colisão de `key=`
   entre widgets (já aconteceu uma vez, dois `st.slider` com o mesmo
   label+parâmetros sem `key` explícito).
3. **Nunca** confiar só em `pytest`/`python -c` para mudanças de UI — os
   módulos de `compressor_sim/` podem estar corretos e `app.py` ainda
   assim quebrar (import errado, `key` duplicada, parâmetro não definido
   na ordem certa do script).

**Cuidado ao reiniciar o servidor**: se um processo Streamlit já estava
rodando antes desta sessão (outro terminal do autor), não matar sem
perguntar. Depois de qualquer edição em `app.py`/`compressor_sim/`,
reiniciar o processo (matar + subir de novo) em vez de confiar no
autoreload do Streamlit, para não misturar código em disco com sessão de
navegador já aberta.

## Sincronia entre livro e app

As equações implementadas aqui devem **sempre** corresponder ao
`../compressores.tex` atual — se uma sessão futura corrigir uma equação no
livro (erro de unidade, renumeração), replicar a correção aqui também, e
vice-versa. Convenção já estabelecida: quando os dois precisam mudar na
mesma sessão, o **app primeiro, livro depois** (ou registrar explicitamente
a ordem escolhida em `CONTEXTO_app.md`), para o código nunca divergir
silenciosamente do texto por mais que o tempo entre as duas edições.

Três erros de unidade reais já foram encontrados **implementando o app** e
corrigidos no livro em seguida (Eqs. 9.8, 11.6, 15.7 — ver `../CONTEXTO.md`
e `CONTEXTO_app.md`) — reimplementar uma equação em código com teste
automatizado é, historicamente, o método mais eficaz de auditoria deste
projeto. Ao portar uma equação nova, considere isso um objetivo declarado,
não um efeito colateral.

## Escopo — o que está fora, de propósito

Lista viva (conferir `CONTEXTO_app.md`, seção "Pendências conhecidas", para
a versão sempre atualizada). Resumo no momento desta escrita (16/08/2026):

- VSD (Eq. 4.3) e decomposição de perdas de gearbox (Eq. 5.2): agregados
  num único parâmetro ASSUMIDO (`p_loss_hood_outros`), não modelados
  separadamente.
- Tubulação interestágios (Eq. 5.15): um trecho representativo (LP→HP),
  não os três segmentos do livro.
- Rotordinâmica/vibração espectral (Eq. 9.8), vida de rolamento (Cap. 11),
  folga residual por dilatação térmica (Eq. 9.7): sem representação —
  exigiriam um modelo de temperatura do rotor que o livro não fecha.
- `n_compressores` assume unidades **idênticas** no **mesmo** ponto de
  operação — sem lógica de carga desigual ou rodízio de seleção (N+1).
- Do vetor Λ do Cap. 28.1, agora com 4 elementos (K, η_mec, ζ_ref, ζ_valv —
  o quarto adicionado em 16/08/2026, coeficiente de perda de válvulas de
  alívio/retenção, Eq. 5.16), só K é identificável (EKF aumentado e PIML
  inverso) — os outros três exigiriam um canal de medição que o EKF/PIML
  ainda não usam (potência elétrica para η_mec, ΔP do filtro para ζ_ref,
  ΔP de válvula para ζ_valv).
- Parte III do app (orquestração EKF→VAE→PIML→prognóstico→MPC como um
  pipeline único, replicando o Capítulo 29 do livro): os algoritmos
  existem e funcionam cada um isoladamente na sub-aba "Motores de IA" da
  aba "Diagnóstico & IA", mas não há ainda uma
  demo que encadeie a saída de um como entrada do próximo.

Estender qualquer item desta lista é bem-vindo, mas cada um exige decidir
**de onde vem o dado/canal de medição novo** antes de escrever código — a
mesma disciplina que já orientou todo o app até aqui.

## Onde não mexer sem necessidade

- `constantes.py`: nunca duplicar um valor que já existe noutro nome —
  procure antes de adicionar.
- Convenção `m_dot` vs. `m_dot_seco` (ver `IMPLEMENTACAO.md`): não
  "corrigir" a cadeia de potência para reagir à umidade — já foi
  deliberadamente decidido que não deve (P·V=nRT).
- `psa_ciclo.py`: o estado de cada torre deve continuar vindo de um único
  cálculo de fase compartilhado (`fase = (t - offset) % t_ciclo`), nunca de
  comparações de ponto flutuante independentes por torre — já causou um bug
  de sincronização real (duas torres regenerando ao mesmo tempo por
  arredondamento).
