# Guia do Código — Módulo por Módulo

Explicação do que cada arquivo faz e como se encaixa no todo, na ordem em
que um leitor novo deveria percorrê-los (dependências antes de quem depende
delas). Para a arquitetura geral e as decisões de projeto, ver
`IMPLEMENTACAO.md`. Para instruções de manutenção, ver `MANUTENCAO.md`.

## `compressor_sim/constantes.py`

Toda constante física (R do ar, cp, γ) e todo valor default do simulador,
num único lugar. Cada linha comenta a origem: um número do livro (com a
equação, ex. `K_FOLGA = 0.05  # coeficiente K da Eq. 9.3`) ou **ASSUMIDO**
(engenharia razoável, sem fonte no livro — ex. `V_VASO_DEFAULT`,
`TAU_VSD`). Nenhuma outra parte do código deveria ter um número mágico —
qualquer constante nova entra aqui primeiro (ver `MANUTENCAO.md`).

## `compressor_sim/nucleo.py`

Funções puras (sem estado, sem I/O) da física de um estágio de compressão e
da psicrometria do ar úmido. Três grupos:

- **Compressão** (`potencia_politropica`, `perda_vi`, `temperatura_descarga`,
  `eficiencia_volumetrica`, `razao_pressao_interna`): as Eqs. 5.5–5.9, 9.3 e
  11.1 do livro, uma função por equação.
- **Motor, invólucro e carcaça** (`potencia_entreferro`, `perdas_motor`,
  `eficiencia_motor`, `calor_gerado_hood`, `temperatura_hood_regime`,
  `q_int_carcaca`, `temperatura_carcaca_regime`, `constante_tempo_carcaca`,
  `temperatura_carcaca`): Eqs. 4.10–4.12 (motor), 2.1/2.4 (hood), 9.6/9.14–
  9.17 (carcaça do LP). `temperatura_carcaca` é a única com solução
  **temporal** fechada (1ª ordem); as demais são regime permanente.
- **Psicrometria** (`p_sat`, `razao_umidade`, `pressao_vapor`, `ur_de_w`,
  `temp_orvalho_c`, `condensado`, `cp_umido`, `densidade_ar`): Eqs. 10.6–10.8.
  `temp_orvalho_c` inverte a fórmula de Buck (Eq. 10.7) por **bisseção**
  numérica — não há forma fechada simples com os 3 parâmetros do livro.

Nenhuma função aqui chama outra função de `nucleo.py` que dependa de
resultado anterior na cascata — são blocos independentes que `sistema.py`
combina na ordem certa.

## `compressor_sim/subsistemas.py`

Mesmo espírito de `nucleo.py` (funções puras, uma por equação), mas para os
subsistemas depois do estágio de compressão: intercooler/aftercooler
(`lmtd`, `u_real`, `ua_com_fouling`, `efetividade`, `eps_ntu_contracorrente`,
`saida_trocador`, `calor_trocado` — Eqs. 10.1–10.5, 12.4), separador de
condensado (`arraste` — Eq. 14.4), secador PSA (`purga_psa`, `eta_purga`,
`potencia_aquecedor`, `sec_dry`, `hi_des` — Eqs. 15.2, 15.6, 15.7, 15.9,
3.3) e vaso pulmão/rede (`dp_dt_vaso`, `autonomia_vaso` — Eqs. 16.4, 16.5).

`hi_des` merece nota: a razão PDP precisa estar em **Kelvin**, não Celsius
com sinal — usar °C diretamente inverteria o sentido do índice (mesma
classe de erro de unidade corrigida no livro para as Eqs. 9.8/11.6/15.7).

## `compressor_sim/sistema.py` — a cascata

O coração do simulador. `parametros_default()` devolve o dicionário de
parâmetros default (uma entrada por constante de `constantes.py`);
`simular(par=None)` mescla overrides sobre esse default e executa a cascata
completa em 8 passos, cada um comentado com a numeração das equações:

0. **Admissão**: FAD → densidade do ar → `m_dot` (Eq. 9.3 corrige por
   eficiência volumétrica) → `m_dot_seco` (correção psicrométrica ASHRAE,
   `v = (R·T/P)·(1+1,6078·W)`) → perda de carga do filtro (Eq. 5.4).
   **`m_dot` e `m_dot_seco` divergem por design**: a cadeia de potência
   (passos 2 e 4) usa `m_dot` porque, a vazão volumétrica fixa, o trabalho
   de compressão não depende de quais moléculas são admitidas (P·V=nRT);
   todo balanço de massa real (passos 3, 5, 6, 7) usa `m_dot_seco`.
1. **Divisão de estágios**: razão de pressão por estágio geométrica
   (intercooler ideal, estágios simétricos).
2. **Estágio LP**: potência politrópica (Eq. 5.5) + perda V_i (Eqs. 5.8/5.9)
   + temperatura de descarga (Eq. 11.1).
   - **2b**: calor interno conduzido à carcaça (Eq. 9.14) — calculado aqui,
     mas a temperatura da carcaça em si só fecha no passo 8b (depende da
     referência térmica do hood, definida mais adiante).
3. **Intercooler**: UA degradado por fouling (Eq. 10.5) → temperatura de
   saída via ε-NTU (Eq. 12.4) → condensado (satura na pressão intermediária).
4. **Estágio HP**: mesma estrutura do passo 2, na pressão intermediária.
   - **4b**: perda de carga na tubulação interestágios (Eq. 5.15) —
     **diagnóstico**, não realimenta a cascata principal (`p_inter` segue
     sendo tratado como valor único, como no resto do livro).
5. **Aftercooler + separador**: mesma estrutura do intercooler, seguida de
   arraste de água residual (Eq. 14.4).
6. **Secador PSA**: purga (fração fixa `fator_purga`), saída saturada no
   PDP "medido" (`pdp_real_c`, um slider — não W=0 fixo).
7. **Vaso pulmão/rede**: `dP/dt` diagnóstico (Eq. 16.4) e autonomia até o
   limite (Eq. 16.5) — usa a vazão de **planta** (`m_dot_util * n_comp`).
8. **Totais e KPIs**: potência total, η_global (referência isotérmica),
   SPC (Eq. 11.11).
   - **8b**: motor (Eqs. 4.10–4.12) → hood (Eqs. 2.1/2.4, com a identidade
     Q_casco = Q_int em regime permanente que fecha a circularidade entre
     as duas equações) → carcaça (Eq. 9.16, referenciada a T_hood ou T_amb
     conforme o toggle `hood_enclausurado`).

O retorno é um dicionário com três chaves: `nos` (lista de 6 pontos de
estado — P, T, PDP, `m_dot`/`m_dot_total`/`w` em cada um), `potencias`
(componentes de potência + totais de planta) e `kpis` (~25 indicadores).
`avisos` acumula mensagens quando alguma grandeza sai de uma faixa
fisicamente esperada (ex. efetividade fora de [0,1]).

## `compressor_sim/dinamica.py`

Integração explícita de Euler do balanço de massa do vaso/rede (mesma
Eq. 16.4/13.4 de `subsistemas.dp_dt_vaso`, mas evoluída passo a passo no
tempo) sob dois modos de controle do Cap. 13: **VSD** (`x_c` persegue o
alvo de regime permanente por uma rampa de 1ª ordem com constante `τ_vsd` —
sem essa rampa, `dP/dt` seria sempre ~0 e a pressão nunca se moveria) e
**Carga/Alívio** (histerese em banda `ΔP_db`, com frequência de ciclagem
teórica da Eq. 13.8).

## `compressor_sim/psa_ciclo.py`

Generaliza a alternância de 2 torres da Figura 15.1 para N torres em
rodízio round-robin, com **3 fases** por torre: adsorvendo (Eq. 15.1),
regenerando (recuperação linear até `q_eq` — simplificação de modelagem, o
Cap. 15 não fecha a cinética de dessorção) e **resfriando** (fase extra:
capacidade já restaurada quimicamente, mas o leito ainda quente é pouco
eficaz). A cobertura contínua (≥1 torre sempre adsorvendo) **não é
garantida por construção** — o módulo calcula e expõe
`tempo_sem_secagem_min`, e a UI alerta se for maior que zero.

## `compressor_sim/ekf.py` — Filtro de Kalman Estendido

Duas gerações de funções, lado a lado:

- **EKF de 2 estados** (`medicao`, `passo_ekf`, `simular_ekf` — Eqs.
  21.2/21.4/21.7/21.8): estado `x=[δ/L, R_f]`, medição
  `z=[ṁ_seco, T_HP,in]`. Jacobianos por diferenças finitas centradas sobre
  a própria `sistema.simular()` (evita derivar a cascata inteira à mão).
  Modelo de transição `f(x)=x` (passeio aleatório) — o livro não fecha uma
  dinâmica própria para δ/R_f, então `Q` absorve a deriva esperada.
  Covariância pela forma de Joseph (numericamente estável); NIS para
  auto-auditoria do filtro.
- **EKF com estado aumentado** (`medicao_aumentada`,
  `simular_ekf_aumentado` — Eqs. 28.1/28.2): estado `x_aug=[δ/L, R_f, K]`.
  `passo_ekf` ganhou um parâmetro `medicao_fn` injetável justamente para
  reaproveitar o mesmo ciclo de predição-correção nas duas gerações, sem
  duplicar código. A novidade real está fora da equação: dois regimes de
  `Q` (`q_proc_calibracao`/`q_proc_operacao`, escolhidos por
  `n_passos_calibracao`) — na janela de calibração, δ/L e R_f têm `Q`
  quase nulo (tratados como conhecidos) para que K convirja; depois, K
  "congela" (`Q` pequeno) e δ/L volta a acompanhar deriva livre.

## `compressor_sim/torch_device.py`

Módulo minúsculo, uma função só: `obter_device()` devolve `cuda` se uma GPU
NVIDIA estiver disponível (`torch.cuda.is_available()`), senão `cpu` —
resultado cacheado. `vae.py` e `piml.py` chamam essa função em vez de cada
um decidir por conta própria, e movem modelo + todo tensor do laço de
treino para o device retornado (`.to(device)`/`device=device`). Não exige
nenhuma configuração manual: `requirements.txt` instala o build padrão do
PyTorch (já com suporte a CUDA embutido), e este módulo decide em tempo de
execução se ele é de fato usado.

## `compressor_sim/vae.py` — Autoencoder Variacional

`extrair_features()` reduz o resultado de `sistema.simular()` a 12
grandezas (não as 28 do livro — este simulador não tem 28 saídas
independentes), deliberadamente enfatizando `m_dot_seco` e a efetividade do
intercooler, as duas que de fato carregam sinal de δ/L e R_f neste modelo
(a maioria das pressões/temperaturas é invariante ao ponto de operação
fixo). `gerar_dataset_saudavel()` sintetiza amostras em torno da condição
de comissionamento com ruído de sensor simulado — não há dado de planta
real. A classe `VAE` implementa o gargalo probabilístico (reparametrização,
Eq. 22.1); `treinar()` otimiza o ELBO invertido (erro de reconstrução +
β·KL, Eq. 22.3) e roda em GPU quando disponível (ver `torch_device.py`
acima); `erro_reconstrucao()` é o sensor virtual de anomalia (Eq.
20.4/22.5); `calibrar_limiar()` fixa o gatilho estatisticamente (média + 3σ
sobre validação saudável, Eq. 22.6) — nunca um valor escolhido à mão.

## `compressor_sim/piml.py` — Physics-Informed Machine Learning

Duas funções de treino, lado a lado, compartilhando a mesma rede
(`SubstitutoPIML`, MLP 5→48→48→4) e o mesmo padrão de perda híbrida (Eq.
23.3) com λ balanceado adaptativamente pela razão de magnitude dos
gradientes (Eq. 23.4, via `torch.autograd.grad`):

- **`treinar()`** (Eqs. 23.1–23.4): resíduo físico é o balanço de energia
  do intercooler (`_residuo_fisico`, forma algébrica em regime permanente
  da Eq. 10.1), avaliado em pontos de colocação sem rótulo — inclusive fora
  da faixa de treino.
- **`treinar_com_identificacao()`** (Eq. 23.5, problema inverso): resíduo é
  a Eq. 9.3 (balanço mássico, `_residuo_inverso`), com o coeficiente K
  tratado como incógnita Ξ — um `torch.nn.Parameter` otimizado no mesmo
  `Adam` dos pesos da rede, não fixo em `params_base`. `_residuo_inverso`
  recalcula a correção psicrométrica (`m_dot`→`m_dot_seco`) ponto a ponto
  via `nucleo.razao_umidade()` **fora** do grafo do PyTorch (não depende de
  Ξ nem dos pesos) — ignorar essa correção foi o bug real da primeira
  versão (viés sistemático dominando o efeito real de Ξ, que é pequeno);
  ver `MANUTENCAO.md` para o diagnóstico completo, útil como referência se
  um resíduo físico novo for adicionado aqui no futuro.

Ambas as funções normalizam o resíduo físico pela própria escala da saída
(`escala_residuo`) antes de elevar ao quadrado — sem isso, o primeiro passo
de treino satura as unidades `tanh` da rede de forma irrecuperável (o
resíduo em unidades reais é ordens de grandeza maior que o erro de dados já
padronizado). Ambas também rodam em GPU quando disponível (`torch_device.py`
acima). `_prever_colocacao()` (nova, extraída na refatoração de 16/08/2026)
concentra o padrão "padronizar entrada → avaliar rede → desnormalizar
saída" que se repetia 4 vezes (duas por função, uma no passo de treino e
outra no balanceamento de λ) — as duas funções de treino chamam essa única
função em vez de duplicar as três linhas. `_residuo_inverso()` não recebe
mais `device` como parâmetro explícito: como sempre é chamada com o
`pred_coloc` que `_prever_colocacao()` devolveu, ela lê o device direto do
próprio tensor (`pred_coloc.device`) — mais simples que propagar o
parâmetro por dois pontos de chamada.

## `compressor_sim/mpc.py` — Controle Preditivo

Horizonte deslizante real: a cada passo, `resolver_horizonte()` chama
`scipy.optimize.minimize` (L-BFGS-B) para achar a sequência ótima de
`x_c(k)` sobre um horizonte H, minimizando erro de rastreio + esforço de
controle (Eq. 24.1) sujeito à mesma integração de Euler de `dinamica.py`
como restrição de propagação (`_propagar_pressao`). Só `x_c(0)` é aplicado
antes de reotimizar no passo seguinte (*receding horizon*, Fig. 24.1).
Deliberadamente **não** usa o substituto PIML como modelo de predição — o
balanço de massa já é barato o bastante para ser avaliado milhares de
vezes sem precisar de substituto.

## `compressor_sim/pso.py` — Otimização por Enxame de Partículas

Implementação padrão (Eqs. 24.3/24.4): peso de inércia decaindo
linearmente de `w_ini` a `w_fim` ao longo das iterações. `otimizar()` é
genérica — recebe qualquer `func_custo(x)`; no app, minimiza o SPC variando
a pressão de setpoint, com a restrição de autonomia mínima imposta por
penalidade (PSO básico não trata restrições nativamente).

## `app.py` — interface Streamlit

Ponto de entrada. Estrutura: `defaults = parametros_default()` primeiro,
depois a barra lateral inteira (todos os `st.slider`/`st.number_input`,
organizados em `st.expander`s por assunto — um por subsistema/algoritmo),
depois `params = {...}` reunindo tudo num único dicionário passado a
`sistema.simular()`, depois as 4 abas (`st.tabs`), cada uma num bloco
`with tab_x:` que executa a cada rerun do Streamlit independente de qual
aba está visualmente selecionada (relevante para testar via `AppTest` — ver
`MANUTENCAO.md`). Seções caras (treino de VAE/PIML) usam
`@st.cache_resource` chaveado pelos parâmetros relevantes.

## `tests/test_simulador.py`

Um bloco por módulo, na mesma ordem deste guia. Convenção: toda função
pública de `compressor_sim/` tem pelo menos um teste de sanidade física
(a grandeza se move na direção fisicamente esperada quando um parâmetro
muda) — não apenas "não lança exceção". Testes de EKF/PIML/VAE fixam
tolerâncias **calibradas numericamente** antes de escrever o `assert`
(rodar o cenário via `python -c`, observar a convergência, só então
escolher a margem) — nunca uma tolerância arbitrária que possa mascarar
regressão real ou, pior, ser frágil por acaso.
