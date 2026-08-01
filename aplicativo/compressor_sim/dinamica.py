"""Simulação dinâmica (domínio do tempo) da rede de ar comprimido.

Integra o balanço de massa do vaso pulmão/rede (Eq. 16.4 / Eq. 13.4) com os
modos de controle do Cap. 13:

- VSD: modulação contínua, Ẇ(x_c) ≈ Ẇ_nom·x_c/η_vsd (Eq. 13.7), com x_c
  perseguindo o alvo de regime permanente por uma rampa de 1ª ordem (τ_vsd,
  ASSUMIDO) em vez de saltar instantaneamente;
- Carga/Alívio: histerese em banda ΔP_db, Ẇ = Ẇ_nom·[x_c + (1−x_c)·k_ul]
  (Eq. 13.7), frequência de ciclagem teórica da Eq. 13.8.

Convenções: SI, pressões absolutas (Pa), tempo em segundos.
"""

from __future__ import annotations

import math

import numpy as np

from .constantes import R_AR

# --- Defaults de controle (Cap. 13) ---
K_UL = 0.25          # fração de Ẇ_nom em alívio (unload) — Eq. 13.7, ASSUMIDO
DP_DB = 0.5e5        # Pa, banda de histerese carga/alívio — ASSUMIDO (típico 0,5 bar)
ETA_VSD = 0.95       # eficiência do inversor em carga parcial — ASSUMIDO
X_C_MIN = 0.30       # velocidade mínima do VSD (fração) — ASSUMIDO
TAU_VSD = 5.0        # s, constante de tempo de rampa do VSD — ASSUMIDO (resposta do
                     # inversor/motor a um degrau de demanda; a Eq. 13.7 define x_c
                     # só em regime permanente, não a dinâmica de resposta)


def perfil_demanda(t: np.ndarray, base: float, t_ev: tuple[float, float],
                   fator_ev: float) -> np.ndarray:
    """Perfil de demanda [kg/s]: valor base com um evento de pico em degrau.

    base: demanda base [kg/s]; t_ev: (início, fim) do evento [s];
    fator_ev: multiplicador da demanda durante o evento.
    """
    dem = np.full_like(t, base, dtype=float)
    mask = (t >= t_ev[0]) & (t < t_ev[1])
    dem[mask] *= fator_ev
    return dem


def simular_transiente(
    horizonte_min: float,
    m_dot_cap: float,
    w_nom: float,
    v_vaso: float,
    t_k: float,
    p_set: float,
    p_limite: float,
    dem_base: float,
    t_ev: tuple[float, float] = (math.inf, math.inf),
    fator_ev: float = 2.0,
    modo: str = "VSD",
    dp_db: float = DP_DB,
    k_ul: float = K_UL,
    eta_vsd: float = ETA_VSD,
    x_c_min: float = X_C_MIN,
    tau_vsd: float = TAU_VSD,
    dt: float = 0.5,
) -> dict:
    """Integra P(t) da rede e devolve séries temporais e KPIs.

    m_dot_cap: capacidade máxima do compressor [kg/s] (saída pós-secador);
    w_nom: potência total em carga plena [W] (saída de `sistema.simular`);
    p_set: pressão de setpoint da rede [Pa abs];
    modo: "VSD" ou "Carga/Alívio".
    """
    n = int(horizonte_min * 60.0 / dt) + 1
    t = np.linspace(0.0, horizonte_min * 60.0, n)
    dem = perfil_demanda(t, dem_base, t_ev, fator_ev)

    p_arr = np.empty(n)
    m_comp = np.empty(n)
    x_c_arr = np.empty(n)
    w_arr = np.empty(n)

    p = p_set
    carregado = True  # estado da máquina no modo Carga/Alívio
    # x_c parte já no valor de regime permanente da demanda inicial (Eq. 13.7)
    x_c = min(max(dem[0] / m_dot_cap, x_c_min), 1.0) if m_dot_cap > 0 else 0.0

    for i in range(n):
        if modo == "VSD":
            # Eq. 13.7 define x_c = V̇_demanda/V̇_nom só em regime permanente;
            # a resposta do inversor a um degrau de demanda não é instantânea,
            # por isso x_c persegue o alvo como uma rampa de 1ª ordem (τ_vsd,
            # ASSUMIDO) em vez de saltar direto — sem isso dP/dt seria sempre
            # ~0 e a pressão da rede nunca se moveria neste modo.
            x_c_alvo = min(max(dem[i] / m_dot_cap, x_c_min), 1.0) if m_dot_cap > 0 else 0.0
            x_c += (x_c_alvo - x_c) * min(dt / tau_vsd, 1.0)
            m_in = x_c * m_dot_cap
            w = w_nom * x_c / eta_vsd
        else:
            # Carga/Alívio — histerese em torno de p_set com banda dp_db
            if carregado and p >= p_set + dp_db / 2.0:
                carregado = False
            elif not carregado and p <= p_set - dp_db / 2.0:
                carregado = True
            x_c = 1.0 if carregado else 0.0
            m_in = m_dot_cap if carregado else 0.0
            w = w_nom * (x_c + (1.0 - x_c) * k_ul)  # Eq. 13.7

        p_arr[i], m_comp[i], x_c_arr[i], w_arr[i] = p, m_in, x_c, w
        # Eq. 16.4 / 13.4 — dP/dt = R·T/V · (ṁ_in − ṁ_out)
        if i < n - 1:
            p += R_AR * t_k / v_vaso * (m_in - dem[i]) * dt
            p = max(p, 0.5e5)  # limite físico inferior

    energia_kwh = float(np.trapezoid(w_arr, t) / 3.6e6)
    if modo != "VSD":
        # número de ciclos carga→alívio ao longo da simulação
        n_ciclos = int(np.sum(np.diff(x_c_arr < 0.5) == 1))
        # Eq. 13.8 — frequência de ciclagem teórica na demanda média
        dem_media = float(np.mean(dem))
        if 0.0 < dem_media < m_dot_cap:
            f_ciclo = (R_AR * t_k * dem_media * (m_dot_cap - dem_media)
                       / (v_vaso * dp_db * m_dot_cap))
        else:
            f_ciclo = 0.0
    else:
        n_ciclos = 0
        f_ciclo = 0.0

    return {
        "t_min": t / 60.0,
        "p_bar": p_arr / 1e5,
        "m_comp": m_comp,
        "m_dem": dem,
        "x_c": x_c_arr,
        "w_kw": w_arr / 1000.0,
        "kpis": {
            "energia_kwh": energia_kwh,
            "n_ciclos": n_ciclos,
            "f_ciclo_teorica_min": f_ciclo * 60.0,
            "t_abaixo_limite_min": float(np.sum(p_arr < p_limite) * dt / 60.0),
            "p_min_bar": float(p_arr.min() / 1e5),
            "p_max_bar": float(p_arr.max() / 1e5),
            "modo": modo,
        },
    }


__all__ = [
    "K_UL",
    "DP_DB",
    "ETA_VSD",
    "X_C_MIN",
    "TAU_VSD",
    "perfil_demanda",
    "simular_transiente",
]
