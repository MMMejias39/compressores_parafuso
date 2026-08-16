"""Controle Preditivo Baseado em Modelo (MPC) — Cap. 24, Eqs. 24.1/24.2.

Horizonte deslizante real sobre o mesmo balanço de massa do vaso/rede já
usado em `dinamica.py` (Eq. 16.4/13.4): a cada passo de tempo, otimiza a
sequência de fração de carga do VSD $x_c(k)$ ao longo de um horizonte $H$
que minimiza o erro de rastreio da pressão de referência mais o esforço
de controle (Eq. 24.1), e aplica só a primeira ação ($u(0)$) antes de
reotimizar no passo seguinte — o princípio de horizonte deslizante
(*receding horizon*) da Figura 24.1 do livro.

Diferente de `dinamica.py` (que só reage à demanda do instante atual via
uma rampa de 1ª ordem, Eq. 13.7), o MPC aqui **antecipa** a demanda
futura conhecida dentro do horizonte — a diferença prática que o
Capítulo 24 atribui ao método, demonstrada lado a lado na UI.

Este app não encadeia o substituto treinado por PIML como modelo de
predição $f(\\cdot)$ do MPC, ao contrário do que o Capítulo 24 recomenda
para sistemas caros de avaliar (CFD, etc.): o balanço de massa do
vaso/rede já é uma expressão algébrica fechada, barata o bastante para
ser avaliada milhares de vezes por execução sem PIML — a mesma
simplificação, pelo motivo oposto, já registrada para o PIML em si (ver
`piml.py`).
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from .constantes import R_AR
from .dinamica import perfil_demanda


def _propagar_pressao(p0: float, x_c_seq: np.ndarray, m_dot_cap: float,
                      dem_seq: np.ndarray, t_k: float, v_vaso: float,
                      dt: float) -> np.ndarray:
    """Simula a pressão do vaso ao longo do horizonte para uma sequência de
    x_c(k) — mesma integração de Euler da Eq. 16.4 já usada em `dinamica.py`.
    """
    p = np.empty(len(x_c_seq) + 1)
    p[0] = p0
    for k, x_c in enumerate(x_c_seq):
        m_in = x_c * m_dot_cap
        p_novo = p[k] + R_AR * t_k / v_vaso * (m_in - dem_seq[k]) * dt
        p[k + 1] = max(p_novo, 0.5e5)
    return p


def _custo_horizonte(x_c_seq: np.ndarray, p0: float, dem_seq: np.ndarray,
                     m_dot_cap: float, t_k: float, v_vaso: float, dt: float,
                     p_ref: float, rho: float, x_c_ant: float) -> float:
    """Eq. 24.1 — erro de rastreio ao quadrado + esforço de controle Δu²."""
    p_traj = _propagar_pressao(p0, x_c_seq, m_dot_cap, dem_seq, t_k, v_vaso, dt)
    erro = np.sum(((p_traj[1:] - p_ref) / p_ref) ** 2)
    du = np.diff(np.concatenate(([x_c_ant], x_c_seq)))
    esforco = rho * np.sum(du ** 2)
    return float(erro + esforco)


def resolver_horizonte(p0: float, dem_seq: np.ndarray, m_dot_cap: float,
                       t_k: float, v_vaso: float, dt: float, p_ref: float,
                       rho: float, x_c_ant: float, x_c_min: float) -> np.ndarray:
    """Resolve a Eq. 24.1 sobre o horizonte de `len(dem_seq)` passos e
    devolve a sequência ótima de x_c(k) — só x_c(0) é de fato aplicado
    pelo laço de horizonte deslizante; o resto é descartado e recalculado
    no próximo passo.
    """
    n_h = len(dem_seq)
    u0 = np.full(n_h, x_c_ant)
    limites = [(x_c_min, 1.0)] * n_h
    resultado = minimize(
        _custo_horizonte, u0,
        args=(p0, dem_seq, m_dot_cap, t_k, v_vaso, dt, p_ref, rho, x_c_ant),
        method="L-BFGS-B", bounds=limites,
        options={"maxiter": 60, "ftol": 1e-10},
    )
    return resultado.x


def simular_mpc(horizonte_min: float, dt: float, n_horizonte: int,
                m_dot_cap: float, v_vaso: float, t_k: float, p_set: float,
                dem_base: float, t_ev: tuple[float, float], fator_ev: float,
                rho: float, x_c_min: float, w_nom: float,
                eta_vsd: float) -> dict:
    """Loop de horizonte deslizante completo — devolve as mesmas séries
    (`t_min`, `p_bar`, `x_c`, `w_kw`, `m_dem`) que `dinamica.simular_transiente`,
    para comparação direta na UI.
    """
    n = int(round(horizonte_min * 60.0 / dt)) + 1
    t = np.linspace(0.0, horizonte_min * 60.0, n)
    dem = perfil_demanda(t, dem_base, t_ev, fator_ev)

    p = p_set
    x_c_ant = min(max(dem[0] / m_dot_cap, x_c_min), 1.0) if m_dot_cap > 0 else 0.0

    p_hist = np.empty(n)
    x_c_hist = np.empty(n)
    w_hist = np.empty(n)

    for i in range(n):
        p_hist[i] = p

        fim = min(i + n_horizonte, n)
        dem_fut = dem[i:fim]
        if len(dem_fut) < n_horizonte:
            preenchimento = np.full(n_horizonte - len(dem_fut), dem_fut[-1])
            dem_fut = np.concatenate([dem_fut, preenchimento])

        x_c_seq = resolver_horizonte(p, dem_fut, m_dot_cap, t_k, v_vaso, dt,
                                     p_set, rho, x_c_ant, x_c_min)
        x_c = float(np.clip(x_c_seq[0], x_c_min, 1.0))
        x_c_hist[i] = x_c
        w_hist[i] = w_nom * x_c / eta_vsd

        if i < n - 1:
            m_in = x_c * m_dot_cap
            p = p + R_AR * t_k / v_vaso * (m_in - dem[i]) * dt
            p = max(p, 0.5e5)
        x_c_ant = x_c

    return {
        "t_min": t / 60.0, "p_bar": p_hist / 1e5, "x_c": x_c_hist,
        "w_kw": w_hist / 1000.0, "m_dem": dem,
    }


__all__ = ["resolver_horizonte", "simular_mpc"]
