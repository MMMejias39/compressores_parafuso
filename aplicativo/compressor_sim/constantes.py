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

# --- Rotor — balanço térmico e folga residual (Eqs. 9.7/9.18/9.19, 16/08/2026) ---
COND_ROTOR_W_K = 15.0     # W/K, h_r·A_r lumped (convecção gás-rotor) — ASSUMIDO,
                           # menor que a condutância da carcaça (área molhada do
                           # rotor é bem menor que a área externa da carcaça)
Q_COND_EIXO_W = 50.0       # W, calor conduzido pelo eixo para os mancais — ASSUMIDO
DELTA_NOM_UM = 250.0       # µm, folga nominal a frio (referência de T_amb) — ASSUMIDO. Calibrado
                           # para ficar acima da dilatação diferencial típica no ponto de operação
                           # default do app (~140 µm) com alguma margem — 100 µm (primeira tentativa)
                           # dava δ_real negativo por construção, sinalizando risco de contato numa
                           # máquina "saudável" default (achado em verificação visual, 16/08/2026).
                           # Não calibrado para bater com folga_rel=δ/L (Eq. 9.3, config. separada) —
                           # os "L" das duas equações não são a mesma grandeza física (ver docstring
                           # de folga_residual_termica).
ALPHA_ROTOR = 12.0e-6      # 1/K, coef. de dilatação térmica linear do aço do rotor — ASSUMIDO (material)
ALPHA_CARCACA = 10.0e-6    # 1/K, coef. de dilatação térmica linear do ferro fundido — ASSUMIDO (material,
                           # mesma família de C_CARCACA_LP)
L_ROTOR_M = 1.0            # m, comprimento característico do rotor — ASSUMIDO
L_CARCACA_M = 1.0          # m, comprimento característico da carcaça — ASSUMIDO

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

# --- Materiais dessecantes (16/08/2026) — o livro (Eq. 15.1) não fecha massa
# nem material do leito, só a capacidade normalizada q_d/q_eq. Densidade
# aparente e capacidade de TRABALHO (não a capacidade estática máxima de
# folha de dados — a de trabalho é medida em baixa UR, o regime real de um
# secador de ar comprimido já pré-secado por aftercooler+separador, e é
# sempre menor que a capacidade estática) são faixas típicas de literatura/
# fabricante, ASSUMIDAS por não haver ensaio específico deste projeto:
# ScienceDirect "Activated Alumina" (densidade 600-800 kg/m³, capacidade
# 7-12% em baixa UR) e guias de peneira molecular 13X (capacidade dinâmica
# >25% em alta UR, PDP alcançável até -73°C — por isso é o material típico
# para a Classe 2/-40°C do livro; sílica gel é fraca em baixa UR, raramente
# usada sozinha para esse PDP). k_ads_ref é só um ponto de partida razoável
# para o slider já existente (Eq. 15.1) — o usuário pode ajustar livremente.
MATERIAIS_DESSECANTE = {
    "Alumina Ativada": {
        "densidade_kg_m3": 750.0,       # ASSUMIDO — meio da faixa 600-800 kg/m³
        "capacidade_trabalho": 0.10,    # ASSUMIDO — kg água / kg seco, baixa UR
        "k_ads_ref": 1.5,               # ASSUMIDO — NÃO verificado contra
                                         # literatura/ensaio, só uma ordenação
                                         # relativa plausível entre os 3
                                         # materiais (ver CONTEXTO_app.md,
                                         # pendência levantada pelo autor
                                         # 16/08/2026 — dinâmica de adsorção
                                         # dos materiais ainda não equacionada
                                         # de fato)
        "t_regen_ref_min": 45.0,        # fonte: experiência de campo do autor
                                         # (16/08/2026) — não é valor de
                                         # literatura
        "t_resfriamento_ref_min": 10.0, # idem, meio da faixa 5-15 min citada
                                         # pelo autor
    },
    "Sílica Gel": {
        "densidade_kg_m3": 700.0,       # ASSUMIDO
        "capacidade_trabalho": 0.08,    # ASSUMIDO — desempenho fraco em baixa UR
        "k_ads_ref": 1.2,               # ASSUMIDO — não verificado (idem acima)
        "t_regen_ref_min": 45.0,        # ASSUMIDO por analogia à alumina — sem
                                         # fonte própria, ao contrário do valor
                                         # de alumina acima
        "t_resfriamento_ref_min": 10.0, # ASSUMIDO por analogia
    },
    "Peneira Molecular 13X": {
        "densidade_kg_m3": 720.0,       # ASSUMIDO
        "capacidade_trabalho": 0.18,    # ASSUMIDO — melhor em baixa UR/PDP baixo
        "k_ads_ref": 1.8,               # ASSUMIDO — não verificado (idem acima)
        "t_regen_ref_min": 45.0,        # ASSUMIDO por analogia à alumina — sem
                                         # fonte própria
        "t_resfriamento_ref_min": 10.0, # ASSUMIDO por analogia
    },
}
MATERIAL_PSA_DEFAULT = "Alumina Ativada"
MASSA_LEITO_PSA_DEFAULT_KG = 200.0  # kg por torre — ASSUMIDO (ordem de grandeza
                                     # de leito industrial de médio porte)

# --- Forma da partícula: pellets vs. esferas (Eqs. 15.17/15.18, 16/08/2026) ---
# A esfericidade não é específica de material no livro (ψ_p é tratado como
# parâmetro geométrico independente, não uma propriedade de catálogo por
# material) — por isso entra como uma escolha própria na UI, não dentro de
# MATERIAIS_DESSECANTE.
PSI_P_ESFERA = 1.0        # esfericidade de referência (esfera perfeita)
PSI_P_PELLET = 0.8        # ASSUMIDO — meio da faixa 0,7-0,9 citada no livro
                           # para pellets extrudados
D_P_PARTICULA_M = 0.0015  # m, diâmetro de partícula equivalente em volume — ASSUMIDO (1,5 mm,
                           # extremidade fina da faixa típica de dessecante industrial)
POROSIDADE_LEITO_PSA = 0.38  # fração de vazios do leito — ASSUMIDO (típico de leito
                              # empacotado de partículas quase-esféricas)
L_LEITO_PSA_M = 2.3       # m, altura do leito por torre — ASSUMIDO
D_VASO_PSA_M = 0.30       # m, diâmetro interno do vaso — ASSUMIDO. Os quatro valores acima
                           # (D_P/POROSIDADE/L/D_VASO) foram calibrados em conjunto para que a
                           # Eq. 15.17 (Ergun), no ponto de operação default do app, reproduza a
                           # mesma ordem de grandeza do antigo DP_NOM_PSA fixo (~300 mbar) — sem
                           # essa calibração, geometria "razoável" isolada (ex.: vaso de 0,5 m,
                           # leito de 1 m) dava ΔP ~6 mbar, 50× menor, disparando HI_des≈0,02 e um
                           # alarme falso de "dessecante degradado" logo na carga inicial do app
                           # (achado em verificação visual, 16/08/2026). Mesmo calibrados, ainda
                           # não batem exatamente com DP_NOM_PSA — o antigo valor também era só
                           # ASSUMIDO, nunca derivado de geometria — e o pequeno desvio residual é
                           # esperado, não um bug.

# --- Soprador booster e aquecedor de regeneração (Eqs. 15.15/15.16, 16/08/2026) ---
D_H_AQUECEDOR_M = 0.05     # m, diâmetro hidráulico do duto/banco de resistências — ASSUMIDO
A_AQUECEDOR_M2 = 2.0       # m², área de troca do elemento resistivo — ASSUMIDO
T_ELEM_MAX_C = 250.0       # °C, temperatura máxima do elemento (limite termostático) — ASSUMIDO
M_DOT_REG_DEFAULT_KG_S = 0.05  # kg/s, vazão de ar de regeneração imposta pelo booster — ASSUMIDO,
                                # bem menor que a vazão principal de processo (FAD_DEFAULT_M3_MIN)
ETA_SOPRADOR_BOOSTER = 0.65    # eficiência do soprador booster — ASSUMIDO (centrífugo típico)
MU_AR_REGEN = 2.6e-5       # Pa·s, viscosidade dinâmica do ar ~150 °C (regeneração) — ASSUMIDO
K_AR_REGEN = 0.035         # W/(m·K), condutividade térmica do ar ~150 °C — ASSUMIDO
PR_AR = 0.7                # número de Prandtl do ar — valor padrão de literatura
EPSILON_RECUP_PSA_DEFAULT = 0.5  # efetividade do trocador de recuperação de
                                  # calor da regeneração (Eq. 15.11) — ASSUMIDO,
                                  # meio de uma faixa típica de trocador
                                  # ar-ar/ar-líquido compacto (0,3-0,7)
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
