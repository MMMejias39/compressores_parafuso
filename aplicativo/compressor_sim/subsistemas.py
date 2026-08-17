"""Subsistemas do trem de ar comprimido: intercooler, separador, secador PSA,
vaso pulmão e rede.

Equações do livro compressores.tex (números indicados por função).
Convenções: SI, pressões absolutas (Pa), temperaturas em K.
"""

from __future__ import annotations

import math

from .constantes import CP_AR, R_AR


# ---------------------------------------------------------------------------
# Intercooler / aftercooler (Caps. 10 e 12)
# ---------------------------------------------------------------------------

def lmtd(dt1: float, dt2: float) -> float:
    """Diferença de temperatura média logarítmica [K].

    Eq. 10.2 — ΔT_lm = (ΔT1 − ΔT2) / ln(ΔT1/ΔT2)
    """
    if dt1 <= 0 or dt2 <= 0:
        return 0.0
    if abs(dt1 - dt2) < 1e-9:
        return dt1
    return (dt1 - dt2) / math.log(dt1 / dt2)


def u_real(u_clean: float, r_f: float, area: float = 1.0) -> float:
    """Coeficiente global real com incrustação [W/(m²K)].

    Eq. 10.5 — 1/U_real = 1/U_clean + R_f
    (R_f em m²K/W; para a forma UA, usar ua_com_fouling abaixo)
    """
    return 1.0 / (1.0 / u_clean + r_f)


def ua_com_fouling(ua_projeto: float, r_f_equiv: float) -> float:
    """UA degradado por fouling [W/K] — forma UA da Eq. 10.5.

    1/UA_real = 1/UA_projeto + R_f_equiv
    """
    return 1.0 / (1.0 / ua_projeto + r_f_equiv)


def efetividade(t_quente_in: float, t_quente_out: float, t_fria_in: float) -> float:
    """Efetividade do trocador (lado quente = ar comprimido).

    Eq. 10.3 — ε = (T_LP,out − T_HP,in) / (T_LP,out − T_w,in)
    """
    span = t_quente_in - t_fria_in
    if span <= 0:
        return 0.0
    return (t_quente_in - t_quente_out) / span


def eps_ntu_contracorrente(ntu: float, c_r: float) -> float:
    """Efetividade ε-NTU para contracorrente.

    Eq. 12.4 — ε = [1 − exp(−NTU·(1−C_r))] / [1 − C_r·exp(−NTU·(1−C_r))]
    """
    if abs(c_r - 1.0) < 1e-9:
        return ntu / (1.0 + ntu)
    e = math.exp(-ntu * (1.0 - c_r))
    return (1.0 - e) / (1.0 - c_r * e)


def saida_trocador(t_quente_in: float, t_fria_in: float,
                   ua: float, c_min: float) -> float:
    """Temperatura de saída do lado quente [K] via ε-NTU (Eq. 12.4).

    Aproximação C_r → 0 (vazão de água grande frente ao ar), caso comum em
    intercooler com água de mar: ε ≈ 1 − exp(−NTU).
    """
    ntu = ua / c_min
    eps = 1.0 - math.exp(-ntu)
    return t_quente_in - eps * (t_quente_in - t_fria_in)


def calor_trocado(m_dot: float, cp: float, t_in: float, t_out: float) -> float:
    """Taxa de transferência de calor [W].

    Eq. 10.1 — Q̇ = ṁ·cp·(T_entra − T_sai)
    """
    return m_dot * cp * (t_in - t_out)


# ---------------------------------------------------------------------------
# Separador de condensado (Cap. 14)
# ---------------------------------------------------------------------------

def arraste(m_dot_cond: float, eta_sep: float) -> float:
    """Água arrastada para jusante do separador [kg/s].

    Eq. 14.4 — ṁ_arraste = ṁ_cond·(1 − η_sep)
    """
    return m_dot_cond * (1.0 - eta_sep)


# ---------------------------------------------------------------------------
# Secador PSA (Caps. 3 e 15)
# ---------------------------------------------------------------------------

def purga_psa(m_dot_in: float, p_low: float, p_high: float, phi: float) -> float:
    """Vazão de purga de regeneração [kg/s].

    Eq. 15.2 — ṁ_purge = ṁ_in · (P_low/P_high) · φ
    φ = fator de histerese; na prática 10–18 % da produção (PSA a frio, :1971).
    """
    return m_dot_in * (p_low / p_high) * phi


def eta_purga(m_dot_purge: float, m_dot_total: float) -> float:
    """Eficiência de purga.

    Eq. 15.9 — η_purge = 1 − ṁ_purge/ṁ_total
    """
    return 1.0 - m_dot_purge / m_dot_total


def potencia_aquecedor(m_dot_purge: float, delta_t: float, cp: float = CP_AR) -> float:
    """Potência do aquecedor de regeneração [W].

    Eq. 3.3 — P_term = ṁ_purge·cp·ΔT
    """
    return m_dot_purge * cp * delta_t


def sec_dry(w_heater: float, w_drum: float, m_dot_dry: float) -> float:
    """Consumo energético específico de secagem [J/kg de ar seco].

    Eq. 15.6 — SEC_dry = (Ẇ_heater + Ẇ_drum)/ṁ_dry
    Este app modela só o secador PSA a frio (não o HOC de tambor rotativo),
    então w_drum é sempre 0 nas chamadas internas — o parâmetro fica
    explícito para não esconder essa limitação de escopo.
    """
    return (w_heater + w_drum) / m_dot_dry


def coef_conveccao_forcada(m_dot: float, d_h: float, mu: float, k_fluido: float,
                           pr: float, aquecendo: bool = True) -> float:
    """Coeficiente de convecção forçada turbulenta em duto [W/(m²K)].

    Eq. 15.15 (Dittus-Boelter) — Re = 4ṁ/(π·D_h·μ); Nu = 0,023·Re^0,8·Pr^n
    (n=0,4 aquecendo o fluido, n=0,3 resfriando); h = Nu·k_fluido/D_h.
    """
    re = 4.0 * m_dot / (math.pi * d_h * mu)
    n = 0.4 if aquecendo else 0.3
    nu = 0.023 * re ** 0.8 * pr ** n
    return nu * k_fluido / d_h


def k_ads_por_forma(k_ads_ref: float, psi_p: float) -> float:
    """Correção da taxa de adsorção pela esfericidade da partícula.

    Eq. 15.18 — k_ads = k_ads_ref/ψ_p (ψ_p,ref = 1, esfera de referência).
    A área externa específica a_v = 6/(ψ_p·d_p) cresce para esfericidade
    menor (pellet tem mais área externa por volume que a esfera de mesmo
    volume equivalente), acelerando a cinética de adsorção.
    """
    return k_ads_ref / psi_p


def perda_carga_ergun(mu: float, v_s: float, rho: float, psi_p: float,
                      d_p: float, porosidade: float, l_leito: float) -> float:
    """Perda de carga em leito empacotado [Pa].

    Eq. 15.17 (Ergun, 1952) — soma o termo viscoso/laminar (Blake-Kozeny)
    e o termo inercial/turbulento (Burke-Plummer). ψ_p é a esfericidade
    da partícula (1,0 para esfera perfeita, < 1 para pellet extrudado —
    eleva ΔP em ambos os termos para a mesma vazão e o mesmo material).
    v_s é a velocidade superficial do ar (vazão volumétrica / área da
    seção do vaso).
    """
    termo_viscoso = (150.0 * (1.0 - porosidade) ** 2 / porosidade ** 3
                      * mu * v_s / (psi_p * d_p) ** 2)
    termo_inercial = (1.75 * (1.0 - porosidade) / porosidade ** 3
                       * rho * v_s ** 2 / (psi_p * d_p))
    return (termo_viscoso + termo_inercial) * l_leito


def hi_des(dp_nom: float, dp_real: float, pdp_target_c: float, pdp_real_c: float) -> float:
    """Índice de saúde do dessecante.

    Eq. 15.7 — HI_des = (ΔP_nom/ΔP_real) · (PDP_target/PDP_real)

    O PDP entra em **Kelvin**, não Celsius, nesta razão: usando °C com sinal
    diretamente, um PDP_real mais alto (pior, secagem menos eficaz) geraria
    HI_des > 1 — o oposto do que o índice pretende sinalizar. Mesma classe
    de armadilha de unidade das Equações 9.8/11.6 do livro (fator de
    conversão faltando); corrigida aqui na implementação, não no `.tex`.
    """
    pdp_target_k = pdp_target_c + 273.15
    pdp_real_k = pdp_real_c + 273.15
    return (dp_nom / dp_real) * (pdp_target_k / pdp_real_k)


# ---------------------------------------------------------------------------
# Vaso pulmão / rede (Caps. 2, 16)
# ---------------------------------------------------------------------------

def dp_dt_vaso(v_vaso: float, t_k: float, m_dot_in: float, m_dot_out: float) -> float:
    """Variação de pressão do vaso [Pa/s].

    Eq. 16.4 (também Eqs. 3.5/18.5) — dP/dt = R·T/V · (Σṁ_in − Σṁ_out)
    """
    return R_AR * t_k / v_vaso * (m_dot_in - m_dot_out)


def autonomia_vaso(v_vaso: float, p_atual: float, p_limite: float,
                   v_dot_demanda: float, p_atm: float) -> float:
    """Tempo até atingir a pressão de corte [s].

    Eq. 16.5 — t_to_cut = V·(P_atual − P_limite) / (V̇_demanda·P_atm)
    """
    if v_dot_demanda <= 0:
        return math.inf
    return v_vaso * (p_atual - p_limite) / (v_dot_demanda * p_atm)


__all__ = [
    "lmtd",
    "u_real",
    "ua_com_fouling",
    "efetividade",
    "eps_ntu_contracorrente",
    "saida_trocador",
    "calor_trocado",
    "arraste",
    "purga_psa",
    "eta_purga",
    "potencia_aquecedor",
    "coef_conveccao_forcada",
    "k_ads_por_forma",
    "perda_carga_ergun",
    "sec_dry",
    "hi_des",
    "dp_dt_vaso",
    "autonomia_vaso",
]
