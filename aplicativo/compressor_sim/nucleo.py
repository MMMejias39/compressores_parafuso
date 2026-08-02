"""Núcleo termodinâmico: estágios de compressão e psicrometria.

Todas as equações referem-se ao livro compressores.tex (número da equação
indicado em cada docstring/comment). Convenções: SI, pressões absolutas (Pa),
temperaturas em K nas equações termodinâmicas.
"""

from __future__ import annotations

import math

from .constantes import CP_AR, GAMMA, R_AR


# ---------------------------------------------------------------------------
# Estágios de compressão
# ---------------------------------------------------------------------------

def delta_p_filtro(zeta: float, rho: float, v: float) -> float:
    """Perda de carga do filtro de admissão [Pa].

    Eq. 5.4 — ΔP_filt = ζ · ρ·v²/2
    """
    return zeta * rho * v**2 / 2.0


def razao_pressao_interna(v_i: float, n: float) -> float:
    """Razão de pressão interna ideal do estágio.

    Eqs. 5.6/5.7 — π_i = V_i^n  (V_i fixo pela geometria do rotor)
    """
    return v_i**n


def potencia_politropica(p_in: float, v_dot_in: float, pi: float,
                         n: float, eta_mec: float) -> float:
    """Potência de compressão de um estágio [W].

    Eq. 5.5 — W = n/(n−1) · P_in · V̇_in · [π^((n−1)/n) − 1] / η_mec
    """
    return (n / (n - 1.0)) * p_in * v_dot_in * (pi**((n - 1.0) / n) - 1.0) / eta_mec


def perda_vi(p1: float, v_dot2: float, pi_operante: float,
             v_i: float, n: float) -> float:
    """Perda por descasamento entre π operante e π_i interna [W] (curva em "V").

    Eqs. 5.8/5.9 — ΔW = V̇2 · |P2 − P1·π_i|
      π > π_i : subcompressão (ΔW_sub = V̇2·(P2 − P_i))
      π < π_i : sobrecompressão (ΔW_sobre = V̇2·(P_i − P2))
    """
    p_i = p1 * razao_pressao_interna(v_i, n)
    p2 = p1 * pi_operante
    return v_dot2 * abs(p2 - p_i)


def temperatura_descarga(t_in: float, pi: float, n: float) -> float:
    """Temperatura de descarga do estágio [K].

    Eq. 11.1 (também Eq. 10.10) — T_out = T_in · π^((n−1)/n)
    """
    return t_in * pi**((n - 1.0) / n)


def eficiencia_volumetrica(k: float, folga_rel: float, pi: float) -> float:
    """Eficiência volumétrica com folga residual δ.

    Eq. 9.3 — η_v = 1 − K·(δ/L)·√(P2/P1)
    """
    return 1.0 - k * folga_rel * math.sqrt(pi)


def potencia_isotermica(p1: float, v_dot1: float, pi: float) -> float:
    """Potência isotérmica ideal de referência [W].

    Usada nas Eqs. 5.12/5.13 (η_global). O livro não fecha a fórmula do
    isotérmico; adota-se a forma clássica W_iso = P1·V̇1·ln(π).
    """
    return p1 * v_dot1 * math.log(pi)


def spc(w_total: float, fad_m3_min: float) -> float:
    """Consumo específico de energia [kW·min/m³].

    Eq. 11.11 — SPC = (W_LP + W_HP) / V̇_free_air
    """
    return (w_total / 1000.0) / fad_m3_min


# ---------------------------------------------------------------------------
# Psicrometria (Cap. 10)
# ---------------------------------------------------------------------------

def p_sat(t_k: float) -> float:
    """Pressão de saturação do vapor d'água [Pa] — fórmula de Buck.

    Eq. 10.7 — P_sat(T) = 0,61121·exp[(18,678 − T/234,5)·T/(257,14+T)]  [kPa]
    Válida para 0–80 °C; T aqui entra em K e é convertida para °C.
    """
    t_c = t_k - 273.15
    return 0.61121e3 * math.exp((18.678 - t_c / 234.5) * (t_c / (257.14 + t_c)))


def razao_umidade(t_k: float, p: float, ur: float) -> float:
    """Razão de umidade [kg água / kg ar seco].

    Eq. 10.6 — W = 0,622 · φ·P_sat(T) / (P − φ·P_sat(T))
    """
    pv = ur * p_sat(t_k)
    pv = min(pv, 0.99 * p)  # evita singularidade na saturação a baixa P
    return 0.622 * pv / (p - pv)


def pressao_vapor(w: float, p: float) -> float:
    """Pressão parcial de vapor d'água [Pa] — inversa da Eq. 10.6.

    p_v = W·P / (0,622 + W)
    """
    return w * p / (0.622 + w)


def ur_de_w(w: float, t_k: float, p: float) -> float:
    """Umidade relativa a partir da razão de umidade (inversa da Eq. 10.6)."""
    return pressao_vapor(w, p) / p_sat(t_k)


def temp_orvalho_c(p_vapor: float) -> float:
    """Temperatura de ponto de orvalho sob pressão [°C] — inversa numérica
    da Eq. 10.7 (fórmula de Buck).

    Não há forma fechada simples para inverter a Eq. 10.7 com os três
    parâmetros do livro (ao contrário da forma "Magnus" de 2 parâmetros,
    mais comum); em vez de introduzir uma fórmula aproximada não citada no
    livro, a inversão é feita por bisseção sobre a própria `p_sat()` — que
    é monótona crescente em T, garantindo convergência.
    """
    if p_vapor <= 0.0:
        return -90.0  # ar sem vapor d'água — piso convencional, sem PDP físico definido
    lo_k, hi_k = 183.15, 363.15  # -90 °C a 90 °C, faixa ampla o suficiente
    for _ in range(60):
        mid_k = (lo_k + hi_k) / 2.0
        if p_sat(mid_k) < p_vapor:
            lo_k = mid_k
        else:
            hi_k = mid_k
    return (lo_k + hi_k) / 2.0 - 273.15


def temp_orvalho_de_w(w: float, p: float) -> float:
    """Temperatura de ponto de orvalho sob pressão [°C] a partir da razão
    de umidade W e da pressão local P — encadeia `pressao_vapor()` e
    `temp_orvalho_c()`. Usada para reportar o PDP em cada ponto de estado
    do trem (Eq. 10.6 + Eq. 10.7 combinadas)."""
    return temp_orvalho_c(pressao_vapor(w, p))


def condensado(m_dot_ar: float, w_in: float, w_out: float) -> float:
    """Vazão mássica de condensado [kg/s].

    Eq. 10.6 (intercooler) / Eq. 14.3 (aftercooler) — ṁ_cond = ṁ_ar·(W_in − W_out)
    """
    return m_dot_ar * max(w_in - w_out, 0.0)


def cp_umido(w: float) -> float:
    """cp do ar úmido [J/(kg·K)].

    Eq. 10.8 — cp_úmido ≈ 1005 + W·1860
    """
    return CP_AR + w * 1860.0


def densidade_ar(p: float, t_k: float) -> float:
    """Densidade do ar seco [kg/m³] — gás ideal (convenção do livro)."""
    return p / (R_AR * t_k)


__all__ = [
    "GAMMA",
    "R_AR",
    "delta_p_filtro",
    "razao_pressao_interna",
    "potencia_politropica",
    "perda_vi",
    "temperatura_descarga",
    "eficiencia_volumetrica",
    "potencia_isotermica",
    "spc",
    "p_sat",
    "razao_umidade",
    "pressao_vapor",
    "ur_de_w",
    "temp_orvalho_c",
    "temp_orvalho_de_w",
    "condensado",
    "cp_umido",
    "densidade_ar",
]
