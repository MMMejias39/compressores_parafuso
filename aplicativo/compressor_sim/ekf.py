"""Filtro de Kalman Estendido (EKF) — Cap. 21, Eqs. 21.2/21.4/21.7/21.8.

Estado x = [folga_rel, r_f_equiv] — os dois parâmetros de degradação que o
restante do app já trata como ASSUMIDO/medido (Eq. 9.3 para a folga do
estágio LP, Eq. 10.5 para o fouling do intercooler), escolhidos por serem
exatamente os dois "estados ocultos" da Equação 21.2 do livro que têm
contraparte calculável neste simulador: folga_rel desloca ṁ_seco via η_v
(Eq. 9.3), r_f_equiv desloca T_HP,in via UA com fouling (Eq. 10.5). Os
demais estados do vetor x do livro (η_is,LP, η_is,HP, σ_b) não têm
contraparte aqui — motor elétrico a esse nível de detalhe e engrenagem não
são modelados neste app (ver CONTEXTO_app.md).

Medição z = [ṁ_seco medido, T_HP,in medido] — os mesmos dois canais, com
ruído gaussiano simulado.

Os Jacobianos F_k/G_k (Eq. 21.3) são numéricos (diferenças finitas
centradas) sobre a própria cascata `sistema.simular()`, em vez de
derivados analiticamente — tecnicamente equivalente e evita depender de
derivadas fechadas de uma cascata com dezenas de passos.
"""

from __future__ import annotations

import numpy as np

from . import sistema


def _jacobiana_numerica(func, x: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    """Jacobiana por diferenças finitas centradas — Eq. 21.3 (F_k/G_k)."""
    x = np.asarray(x, dtype=float)
    f0 = np.asarray(func(x), dtype=float)
    n, m = len(x), len(f0)
    jac = np.zeros((m, n))
    for j in range(n):
        dx = np.zeros(n)
        dx[j] = eps * max(1.0, abs(x[j]))
        jac[:, j] = (np.asarray(func(x + dx)) - np.asarray(func(x - dx))) / (2 * dx[j])
    return jac


def medicao(x: np.ndarray, params_base: dict) -> np.ndarray:
    """g(x) — ṁ_seco e T_HP,in previstos pela cascata completa para o estado x."""
    folga_rel, r_f_equiv = x
    p = {**params_base,
         "folga_rel": max(float(folga_rel), 0.0),
         "r_f_equiv": max(float(r_f_equiv), 0.0)}
    res = sistema.simular(p)
    m_dot_seco = res["nos"][0]["m_dot"]
    t_hp_in = res["nos"][2]["t_c"]
    return np.array([m_dot_seco, t_hp_in])


def passo_ekf(x_hat: np.ndarray, p_cov: np.ndarray, z: np.ndarray,
             params_base: dict, q_proc: np.ndarray, r_meas: np.ndarray):
    """Um ciclo de predição-correção do EKF — Eq. 21.4.

    Modelo de transição f(x) = x (passeio aleatório): o livro não fecha uma
    dinâmica própria de evolução para δ/R_f, então a predição assume estado
    quase-constante entre ciclos, com a incerteza de processo Q absorvendo
    a deriva lenta esperada. Covariância atualizada pela forma de Joseph
    (Eq. 21.8, numericamente estável); NIS pela Eq. 21.7.
    """
    n = len(x_hat)
    x_pred = np.array(x_hat, dtype=float)  # f(x) = x
    jac_f = _jacobiana_numerica(lambda xx: xx, x_pred)
    p_pred = jac_f @ p_cov @ jac_f.T + q_proc

    g_func = lambda xx: medicao(xx, params_base)
    z_pred = g_func(x_pred)
    jac_g = _jacobiana_numerica(g_func, x_pred)
    s_cov = jac_g @ p_pred @ jac_g.T + r_meas
    k_gain = p_pred @ jac_g.T @ np.linalg.inv(s_cov)

    inovacao = np.asarray(z, dtype=float) - z_pred
    x_new = x_pred + k_gain @ inovacao
    x_new = np.maximum(x_new, 0.0)  # folga/fouling não-negativos

    i_kg = np.eye(n) - k_gain @ jac_g
    p_new = i_kg @ p_pred @ i_kg.T + k_gain @ r_meas @ k_gain.T  # Eq. 21.8

    nis = float(inovacao.T @ np.linalg.inv(s_cov) @ inovacao)  # Eq. 21.7
    return x_new, p_new, inovacao, nis


def simular_ekf(params_base: dict, folga_true: np.ndarray, r_f_true: np.ndarray,
                sigma_m_dot: float, sigma_t_hp: float,
                q_proc_diag: tuple[float, float], x0: tuple[float, float],
                p0_diag: tuple[float, float], seed: int = 42) -> dict:
    """Roda o EKF ao longo de uma série de estados verdadeiros (desconhecidos
    do filtro), gerando medições ruidosas a cada passo e devolvendo as séries
    temporais de estimativa, incerteza (desvio-padrão) e NIS.
    """
    rng = np.random.default_rng(seed)
    n_passos = len(folga_true)
    x_hat = np.array(x0, dtype=float)
    p_cov = np.diag(p0_diag).astype(float)
    q_proc = np.diag(q_proc_diag)
    r_meas = np.diag([sigma_m_dot**2, sigma_t_hp**2])

    x_hist = np.zeros((n_passos, 2))
    std_hist = np.zeros((n_passos, 2))
    nis_hist = np.zeros(n_passos)
    z_hist = np.zeros((n_passos, 2))

    for k in range(n_passos):
        x_true_k = np.array([folga_true[k], r_f_true[k]])
        z_true = medicao(x_true_k, params_base)
        ruido = rng.normal(0.0, [sigma_m_dot, sigma_t_hp])
        z_k = z_true + ruido

        x_hat, p_cov, _, nis = passo_ekf(x_hat, p_cov, z_k, params_base, q_proc, r_meas)

        x_hist[k] = x_hat
        std_hist[k] = np.sqrt(np.maximum(np.diag(p_cov), 0.0))
        nis_hist[k] = nis
        z_hist[k] = z_k

    return {
        "x_hat": x_hist,
        "std": std_hist,
        "nis": nis_hist,
        "z": z_hist,
        "folga_true": np.asarray(folga_true, dtype=float),
        "r_f_true": np.asarray(r_f_true, dtype=float),
    }


__all__ = ["medicao", "passo_ekf", "simular_ekf"]
