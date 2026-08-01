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
    "dp_dt_vaso",
    "autonomia_vaso",
]
