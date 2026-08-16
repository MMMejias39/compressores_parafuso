"""Calibração em lote de K via Levenberg-Marquardt — alternativa clássica.

Terceiro caminho de identificação do coeficiente de vazamento K (Eq. 9.3),
ao lado do EKF com estado aumentado (`ekf.py`, online/recursivo, Cap. 28)
e do PIML (`piml.py`, offline, junto ao treino de uma rede substituta,
Cap. 23.8). Aqui não há filtro nem rede neural: é ajuste de mínimos
quadrados não lineares em lote, direto contra o modelo físico
`sistema.simular()`, pelos mesmos dois canais medidos do EKF aumentado
(ṁ_seco e T_HP,in — `ekf.medicao_aumentada`), para que os três caminhos
sejam comparáveis entre si.

Levenberg-Marquardt (Gauss-Newton amortecido) é o método clássico de
calibração em lote quando o vetor de incógnitas é pequeno — aqui, 1
elemento (K) — e existe um modelo direto barato de avaliar. É inviável
para o PIML porque lá as incógnitas são os milhares de pesos da rede
neural mais Ξ: formar (ou aproximar) a Hessiana Gauss-Newton J^T J para
esse tamanho de vetor de parâmetros não é prático, e por isso o PIML usa
gradiente estocástico (Adam) em vez de LM. Aqui, com 1 parâmetro só, LM
converge em poucas avaliações e sem precisar de nenhuma rede.
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

    entradas: matriz (N, 5) — [pi_total, t_amb_c, folga_rel, r_f_equiv, fad],
    mesma convenção de `piml.NOMES_ENTRADA` (reaproveitar `piml.gerar_dataset`
    para produzi-las, extraindo ṁ_seco/T_HP,in das 4 saídas rotuladas).
    saidas: matriz (N, 2) — [ṁ_seco, T_HP,in] medidos (ruidosos).
    k_inicial: crença inicial de K, deliberadamente diferente do K real
    usado para rotular `saidas`, para que a convergência devolvida seja
    identificação de verdade, não o otimizador "sabendo" a resposta.
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


__all__ = ["calibrar_k_lm"]
