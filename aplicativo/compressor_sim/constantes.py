"""Constantes físicas e valores default do simulador.

Origem dos defaults: livro "Gêmeo Digital de Sistemas de Compressão Offshore"
(compressores.tex). Onde o livro não fornece valor numérico, o default é
marcado como ASSUMIDO.
"""

# --- Propriedades do ar (Nomenclatura do livro; Eq. 10.8 usa cp = 1005) ---
R_AR = 287.0          # J/(kg·K) — constante específica do ar
CP_AR = 1005.0        # J/(kg·K) — Eq. 10.8
GAMMA = 1.4           # cp/cv — Nomenclatura (:178)

# --- Condições de referência ---
P_ATM = 101325.0      # Pa
T_AMB_DEFAULT = 303.15  # K (30 °C, ambiente offshore típico) — ASSUMIDO
UR_AMB_DEFAULT = 0.80   # umidade relativa 80 % (salinidade/umidade offshore) — ASSUMIDO

# --- Compressão (defaults do livro) ---
N_POLITROPICO = 1.35   # exemplo trabalhado da Eq. 13.9 (:1746)
VI_DEFAULT = 2.2       # casada com π = √8 ≈ 2,83 por estágio (Eq. 5.7, n=1,35);
                       # a figura 5.1 usa V_i = 4,0 para ILUSTRAR o descasamento
PI_REDE_DEFAULT = 8.0  # razão de pressão total, faixa 7–10 bar (:483)
ETA_ISENTROPICA = 0.75  # ASSUMIDO (típico parafuso injetado)
ETA_MECANICA = 0.96    # ASSUMIDO (mancais + engrenagens)
K_FOLGA = 0.05         # coeficiente K da Eq. 9.3 — ASSUMIDO
FOLGA_REL_DEFAULT = 0.002  # δ/L — ASSUMIDO (máquina nova)
ZETA_FILTRO = 2.5      # ζ do filtro de admissão (Eq. 5.4) — ASSUMIDO

# --- Carcaça do estágio LP — balanço térmico (Eq. 9.6) ---
M_CARCACA_LP = 300.0        # kg, massa térmica da carcaça do elemento LP — ASSUMIDO
C_CARCACA_LP = 460.0        # J/(kg·K), calor específico típico do ferro fundido — ASSUMIDO (material)
COND_EXT_CARCACA_LP = 10.0  # W/K, condutância de convecção natural carcaça-ambiente (h_ext·A_ext) — ASSUMIDO
COND_ARREF_CARCACA_LP = 20.0  # W/K, condutância do arrefecimento ativo/ventilação forçada do invólucro — ASSUMIDO

# --- Motor elétrico (Eqs. 4.10-4.12) — fechamento simplificado das perdas ---
S_MOTOR_DEFAULT = 0.02          # escorregamento nominal — ASSUMIDO (motor de indução típico)
P_FIXAS_MOTOR_DEFAULT = 1500.0  # W, perdas fixas de ensaio (estator+núcleo+atrito/vent.+suplementares,
                                 # método segregado IEC 60034-2-1) — ASSUMIDO

# --- Invólucro/Hood (Eqs. 2.1/2.4) — balanço térmico do gabinete ---
M_DOT_VENT_DEFAULT = 0.5             # kg/s, vazão de ventilação forçada do exaustor do hood — ASSUMIDO
P_LOSS_HOOD_OUTROS_DEFAULT = 2000.0  # W, perdas de VSD+gearbox não decompostas neste app (Eqs. 4.3/5.2
                                      # não implementadas) — lumped, ASSUMIDO
HOOD_ENCLAUSURADO_DEFAULT = True     # motor+gearbox+estágios dentro do mesmo invólucro acústico — ASSUMIDO

# --- Tubulação interestágios (Eq. 5.15) ---
F_D_LINHA_DEFAULT = 0.02  # fator de atrito de Darcy — ASSUMIDO (turbulento, tubo comercial)
L_LINHA_DEFAULT = 3.0     # m, comprimento do trecho LP→intercooler→HP — ASSUMIDO
D_LINHA_DEFAULT = 0.10    # m, diâmetro interno do trecho (mesma ordem de grandeza do
                           # duto de admissão D_DUTO_ADMISSAO) — ASSUMIDO

# --- Vazão (não consta no livro — ASSUMIDO) ---
FAD_DEFAULT_M3_MIN = 10.0  # m³/min de ar livre (FAD) por unidade
N_COMPRESSORES_DEFAULT = 1  # unidades idênticas operando em paralelo — ASSUMIDO

# --- Intercooler / aftercooler ---
T_AGUA_DEFAULT = 298.15    # K (25 °C) — ASSUMIDO
UA_PROJETO = 4000.0        # W/K — ASSUMIDO
RF_FOULING_DEFAULT = 0.0   # m²K/W (Eq. 10.5) — limpo
ETA_SEPARADOR = 0.98       # Eq. 14.4 — ASSUMIDO (separador ciclone típico)

# --- Secador PSA ---
FATOR_PURGA = 0.15         # 10–18 % da produção, PSA a frio (:1971)
DELTA_T_REGEN = 80.0       # K, aquecedor de regeneração (Eq. 3.3) — ASSUMIDO
K_ADS_DEFAULT = 1.5        # constante de taxa de adsorção (Eq. 15.1) — meio da faixa
                           # ilustrativa do livro (0,5 a 3,0, Figura 15.2) — ASSUMIDO
T_RES_PSA_DEFAULT_MIN = 4.0  # tempo de residência de projeto do leito [min] — ASSUMIDO
T_ADS_PSA_DEFAULT_MIN = 6.0    # duração da fase de adsorção por torre [min] — ASSUMIDO
T_REGEN_PSA_DEFAULT_MIN = 4.0  # duração da fase de regeneração por torre [min] — ASSUMIDO
T_RESFRIAMENTO_PSA_DEFAULT_MIN = 2.0  # duração do resfriamento pós-regeneração
                                       # [min] — ASSUMIDO; com os defaults acima e
                                       # N_VASOS_PSA_DEFAULT=2, t_ads = t_regen +
                                       # t_resfriamento exatamente, dando cobertura
                                       # contínua sem gap (ver docstring do módulo)
N_VASOS_PSA_DEFAULT = 2     # torres em rodízio — ASSUMIDO (mínimo do princípio PSA)
DP_NOM_PSA = 0.30e5         # Pa, perda de carga nominal de projeto do leito (Eq. 15.7) — ASSUMIDO
W_DRUM_PADRAO = 0.0         # W, potência do motor do tambor rotativo (Eq. 15.6) — este app
                             # modela só o secador PSA a frio, não o HOC de tambor rotativo
                             # do Cap. 15, logo essa parcela é sempre 0 aqui

# --- Vaso pulmão / rede ---
V_VASO_DEFAULT = 2.0       # m³ — ASSUMIDO
P_LIMITE_REDE = 6.0e5      # Pa abs, pressão mínima de instrumentação — ASSUMIDO
DEMANDA_M3_MIN = 8.0       # m³/min FAD de consumo da rede — ASSUMIDO

# --- PDP alvo ---
PDP_ALVO_C = -40.0         # °C, ISO 8573-1 Classe 2 (:2305)
