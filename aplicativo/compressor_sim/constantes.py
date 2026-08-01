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

# --- Vaso pulmão / rede ---
V_VASO_DEFAULT = 2.0       # m³ — ASSUMIDO
P_LIMITE_REDE = 6.0e5      # Pa abs, pressão mínima de instrumentação — ASSUMIDO
DEMANDA_M3_MIN = 8.0       # m³/min FAD de consumo da rede — ASSUMIDO

# --- PDP alvo ---
PDP_ALVO_C = -40.0         # °C, ISO 8573-1 Classe 2 (:2305)
