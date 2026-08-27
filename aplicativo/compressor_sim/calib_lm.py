"""Calibração em lote de parâmetros de engenharia via Levenberg-Marquardt.

Resolve o problema inverso clássico de mínimos quadrados não lineares:
ajustar parâmetros de engenharia que não são constantes universais fixas
(como coeficiente de vazamento K_folga, rendimento mecânico eta_mec, perda
de carga no filtro zeta, coeficientes UA dos trocadores de calor) a partir
de medições de planta (ex: telemetria OSIsoft PI).

Suporta calibração escalar univariada (K_folga) e calibração multivariada
simultânea de múltiplos parâmetros de engenharia livres.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares

from . import sistema


def _medicao_lm(k_val: float, entrada_row: np.ndarray, params_base: dict) -> np.ndarray:
    """g(K) no ponto de operação de uma linha — mesmos 2 canais de
    `ekf.medicao_aumentada`: ṁ_seco e T_HP,in."""
    pi_total, t_amb_c, folga_rel, r_f_equiv, fad = entrada_row
    p = {**params_base,
         "pi_total": float(pi_total), "t_amb": float(t_amb_c) + 273.15,
         "folga_rel": max(float(folga_rel), 0.0),
         "r_f_equiv": max(float(r_f_equiv), 0.0),
         "fad_m3_min": float(fad), "k_folga": max(float(k_val), 0.0)}
    res = sistema.simular(p)
    m_dot_seco = res["nos"][0]["m_dot"]
    t_hp_in = res["nos"][2]["t_c"]
    return np.array([m_dot_seco, t_hp_in])


def _residuo_lm(k_arr: np.ndarray, entradas: np.ndarray, saidas: np.ndarray,
                params_base: dict, escala: np.ndarray) -> np.ndarray:
    k_val = k_arr[0]
    preds = np.array([_medicao_lm(k_val, row, params_base) for row in entradas])
    return ((preds - saidas) / escala).ravel()


def calibrar_k_lm(entradas: np.ndarray, saidas: np.ndarray, params_base: dict,
                  k_inicial: float) -> dict:
    """Calibra K em lote via `scipy.optimize.least_squares(method="lm")`.

    entradas: matriz (N, 5) — [pi_total, t_amb_c, folga_rel, r_f_equiv, fad]
    saidas: matriz (N, 2) — [ṁ_seco, T_HP,in] medidos
    k_inicial: estimativa inicial de K
    """
    escala = np.abs(saidas).mean(axis=0)
    escala[escala == 0] = 1.0
    resultado = least_squares(
        _residuo_lm, x0=[k_inicial], args=(entradas, saidas, params_base, escala),
        method="lm")
    return {
        "k_estimado": float(resultado.x[0]),
        "sucesso": bool(resultado.success),
        "n_avaliacoes": int(resultado.nfev),
        "custo_final": float(resultado.cost),
        "mensagem": str(resultado.message),
    }


def _medicao_multi_lm(theta: np.ndarray, nomes_theta: list[str],
                      entrada_row: np.ndarray, params_base: dict,
                      canais_saida: list[str]) -> np.ndarray:
    """Avalia o modelo completo sistema.simular() para o vetor de parâmetros theta."""
    pi_total, t_amb_c, folga_rel, r_f_equiv, fad = entrada_row
    p = {**params_base,
         "pi_total": float(pi_total), "t_amb": float(t_amb_c) + 273.15,
         "folga_rel": max(float(folga_rel), 0.0),
         "r_f_equiv": max(float(r_f_equiv), 0.0),
         "fad_m3_min": float(fad)}
    
    # Aplica os parâmetros livres identificáveis
    for nome, val in zip(nomes_theta, theta):
        p[nome] = max(float(val), 1e-6)

    res = sistema.simular(p)
    
    # Extrai os canais solicitados
    saidas = []
    for canal in canais_saida:
        if canal == "m_dot_seco":
            saidas.append(res["nos"][0]["m_dot"])
        elif canal == "t_hp_in":
            saidas.append(res["nos"][2]["t_c"])
        elif canal == "t_lp_out":
            saidas.append(res["nos"][1]["t_c"])
        elif canal == "t_hp_out":
            saidas.append(res["nos"][3]["t_c"])
        elif canal == "w_total":
            saidas.append(res["potencias"]["w_total"] / 1000.0)
        elif canal == "p_suc_lp":
            saidas.append(res["nos"][0]["p_bar"])
        else:
            saidas.append(0.0)
    return np.array(saidas, dtype=float)


def _residuo_multi_lm(theta: np.ndarray, nomes_theta: list[str],
                      entradas: np.ndarray, saidas: np.ndarray,
                      params_base: dict, escala: np.ndarray,
                      canais_saida: list[str]) -> np.ndarray:
    preds = np.array([
        _medicao_multi_lm(theta, nomes_theta, row, params_base, canais_saida)
        for row in entradas
    ])
    return ((preds - saidas) / escala).ravel()


def calibrar_parametros_multivariavel_lm(
    entradas: np.ndarray,
    saidas: np.ndarray,
    params_base: dict,
    theta_iniciais: dict[str, float],
    canais_saida: list[str] | None = None,
) -> dict:
    """Calibração multivariada de múltiplos parâmetros livres de engenharia via Levenberg-Marquardt.

    Permite ajustar simultaneamente:
    - `k_folga`: Coeficiente de vazamento interno nas folgas
    - `eta_mec`: Rendimento mecânico da carcaça e engrenagens
    - `zeta_filtro`: Coeficiente de perda no filtro de sucção
    - `ua_inter_ref`: Capacitância térmica do intercooler
    - `ua_after_ref`: Capacitância térmica do aftercooler

    Retorna o dicionário de parâmetros calibrados, incertezas e resíduo final.
    """
    if canais_saida is None:
        canais_saida = ["m_dot_seco", "t_hp_in", "t_lp_out", "w_total"]

    nomes_theta = list(theta_iniciais.keys())
    x0 = np.array([theta_iniciais[k] for k in nomes_theta], dtype=float)

    escala = np.abs(saidas).mean(axis=0)
    escala[escala == 0] = 1.0

    resultado = least_squares(
        _residuo_multi_lm,
        x0=x0,
        args=(nomes_theta, entradas, saidas, params_base, escala, canais_saida),
        method="lm",
    )

    params_calibrados = {
        nome: float(resultado.x[i]) for i, nome in enumerate(nomes_theta)
    }

    # Matriz de covariância assintótica dos parâmetros
    try:
        j_mat = resultado.jac
        n_obs = len(resultado.fun)
        n_params = len(x0)
        s_sq = 2.0 * resultado.cost / max(n_obs - n_params, 1)
        cov_matrix = np.linalg.pinv(j_mat.T @ j_mat) * s_sq
        std_errors = {
            nome: float(np.sqrt(max(cov_matrix[i, i], 0.0)))
            for i, nome in enumerate(nomes_theta)
        }
    except Exception:
        std_errors = {nome: 0.0 for nome in nomes_theta}

    return {
        "params_calibrados": params_calibrados,
        "desvios_padrao": std_errors,
        "sucesso": bool(resultado.success),
        "n_avaliacoes": int(resultado.nfev),
        "custo_final": float(resultado.cost),
        "mensagem": str(resultado.message),
    }


__all__ = ["calibrar_k_lm", "calibrar_parametros_multivariavel_lm"]

