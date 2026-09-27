"""Fadiga do dente de engrenagem por acúmulo de dano — Cap. 19, Eqs. 19.6-19.10.

Substitui o RUL probabilístico anterior (regressão linear da folga estimada
pelo EKF) pelo modelo fisicamente fundamentado do livro: Regra de
Palmgren-Miner sobre a curva S-N de Basquin do dente de engrenagem, com
propagação de incerteza por Processo Gaussiano sobre a taxa de acúmulo de
dano — ver CONTEXTO.md/CONTEXTO_app.md, "RUL por Miner + EHI" (27/09/2026).

Fonte do sinal de tensão: `MEC_SIGMA_B` (pi_telemetry.py), já calculada a
partir do torque de eixo pelo modelo de Lewis (Eq. 8.7). Cada ciclo diário
do supervisório de frota é tratado como um único nível de tensão constante
(o app não simula um histórico de carga vibratória de alta frequência para
justificar contagem por rainflow) — número de ciclos de carga no período é
aproximado pelo número de rotações do eixo (uma solicitação de flexão por
rotação, mesma convenção de projeto de engrenagens).

C e b_f da curva de Basquin (Eq. 19.8) são ASSUMIDOS — ver constantes.py,
"Fadiga do dente de engrenagem", para a justificativa e os dois pontos de
referência usados no ajuste.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from . import constantes as c


def parametros_basquin() -> tuple[float, float]:
    """Ajusta (C, b_f) da Eq. 19.8 (sigma^b_f * N = C) a partir dos dois pontos
    de referência ASSUMIDOS em constantes.py (baixo ciclo e limite de resistência)."""
    sigma1, n1 = c.SIGMA_REF_BAIXO_CICLO_MPA, c.N_REF_BAIXO_CICLO
    sigma2, n2 = c.SIGMA_B_ADM_MPA, c.N_REF_ENDURANCE
    b_f = np.log(n2 / n1) / np.log(sigma1 / sigma2)
    C = n1 * sigma1 ** b_f
    return float(C), float(b_f)


def dano_incremental(sigma_b_mpa: float, rpm: float, dt_dias: float) -> float:
    """Incremento de dano ΔD no período (Eqs. 19.7/19.8), tratando sigma_b como
    um único nível de tensão constante durante dt_dias."""
    C, b_f = parametros_basquin()
    sigma = max(1.0, float(sigma_b_mpa))  # MPa, evita base não positiva na potência
    n_i = max(0.0, float(rpm)) * 60.0 * 24.0 * max(0.0, float(dt_dias))  # ciclos no período
    n_falha = C * sigma ** (-b_f)  # Eq. 19.8: N_i(sigma_i)
    return float(n_i / n_falha) if n_falha > 0 else 0.0


def _kernel_gp(a: np.ndarray, b: np.ndarray, sigma_f: float, ell: float) -> np.ndarray:
    """Kernel exponencial quadrático da Eq. 19.10."""
    diff = a[:, None] - b[None, :]
    return sigma_f ** 2 * np.exp(-(diff ** 2) / (2.0 * ell ** 2))


def taxa_dano_gp(
    t_obs_dias: List[float],
    taxas_obs: List[float],
    t_estrela_dias: float,
    sigma_f: float = c.GP_SIGMA_F,
    ell: float = c.GP_ELL_DIAS,
    sigma_n: float = c.GP_SIGMA_N,
) -> tuple[float, float]:
    """Média e variância preditivas de Ḋ(t*) por regressão de Processo
    Gaussiano (Eq. 19.10) sobre o histórico de taxas de dano observadas."""
    t = np.asarray(t_obs_dias, dtype=float)
    d = np.asarray(taxas_obs, dtype=float)
    n = len(t)
    if n == 0:
        return 1e-6, (sigma_f ** 2)

    K = _kernel_gp(t, t, sigma_f, ell) + (sigma_n ** 2) * np.eye(n)
    t_star = np.array([t_estrela_dias])
    k_star = _kernel_gp(t, t_star, sigma_f, ell).ravel()  # (n,)

    alpha = np.linalg.solve(K, d)
    media = float(k_star @ alpha)

    v = np.linalg.solve(K, k_star)
    k_ss = float(_kernel_gp(t_star, t_star, sigma_f, ell)[0, 0])
    variancia = max(0.0, k_ss - float(k_star @ v))

    return media, variancia


def projetar_rul_fadiga(
    historico_dano: List[float],
    dt_dias: float = 1.0,
) -> Dict[str, float | str]:
    """RUL por acúmulo de dano (Eq. 19.9), com IC 95% propagado da variância
    de Ḋ estimada por Processo Gaussiano (Eq. 19.10).

    `dt_dias` não entra no eixo de tempo da regressão (ver comentário interno)
    — mantido no sinal só por simetria com `dano_incremental()`/os outros
    chamadores; hoje é vestigial aqui."""
    if len(historico_dano) < 3:
        return {
            "rul_dias_estimado": 180.0,
            "rul_ic_95_min": 120.0,
            "rul_ic_95_max": 240.0,
            "taxa_dano_diaria": 1e-4,
            "dano_acumulado": float(historico_dano[-1]) if historico_dano else 0.0,
            "confiabilidade": "Baixa (poucos pontos históricos)",
        }

    D = np.asarray(historico_dano, dtype=float)
    n = len(D)
    # Eixo de tempo por índice (cada ponto do histórico = um passo nominal),
    # não `dt_dias` do parâmetro: o app chama esta função também com
    # dt_dias=0.0 para "espiar" o painel sem avançar o tempo (achado em
    # verificação visual, 27/09/2026) — usar esse dt para reconstruir o eixo
    # inteiro dividiria por zero e/ou colapsaria todo o histórico em t=0.
    t = np.arange(n, dtype=float)

    # Taxas observadas por diferença finita entre passos consecutivos de D(t)
    # (já "por passo": o passo nominal é a própria unidade do eixo t acima)
    taxas_obs = np.diff(D)
    t_obs_taxas = t[1:]

    t_estrela = float(t[-1])
    media_taxa, var_taxa = taxa_dano_gp(list(t_obs_taxas), list(taxas_obs), t_estrela)
    media_taxa = max(1e-7, media_taxa)

    dano_atual = float(D[-1])
    dano_restante = max(0.0, 1.0 - dano_atual)

    rul_central = dano_restante / media_taxa

    desvio = float(np.sqrt(var_taxa))
    # Piso relativo (não 1e-7 absoluto): sigma_b entra na Eq. 19.8 elevado a
    # b_f~8, então um desvio-padrão pequeno em termos absolutos já é grande
    # o bastante para levar taxa_min perto de zero e explodir rul_ic_95_max
    # (achado em verificação, 27/09/2026) — a taxa real de uma máquina em
    # operação contínua não deveria ser modelada como podendo colapsar a
    # zero, então o piso é uma fração da própria média estimada.
    taxa_min = max(0.1 * media_taxa, media_taxa - 1.96 * desvio)
    taxa_max = media_taxa + 1.96 * desvio

    rul_min = dano_restante / taxa_max if taxa_max > 0 else rul_central
    rul_max = dano_restante / taxa_min if taxa_min > 0 else rul_central

    # Teto de exibição/decisão (constantes.py, RUL_TETO_DIAS): operação bem
    # abaixo do limite de resistência projeta RUL de milhões de dias,
    # tecnicamente correto (Eq. 19.9) mas sem utilidade operacional.
    teto = c.RUL_TETO_DIAS
    rul_central = min(rul_central, teto)
    rul_min = min(rul_min, teto)
    rul_max = min(rul_max, teto)

    return {
        "rul_dias_estimado": float(rul_central),
        "rul_ic_95_min": float(max(0.0, rul_min)),
        "rul_ic_95_max": float(max(rul_central, rul_max)),
        "taxa_dano_diaria": float(media_taxa),
        "dano_acumulado": dano_atual,
        "confiabilidade": "Alta" if n >= 15 else "Média",
    }


def calcular_ehi(razao_reversivel: float, e_rec: float) -> float:
    """Exergetic Health Index (Eq. 19.6): razão de eficiência exergética
    (Ẇ_min,rev/Ẇ_real, aqui `eta_global` já calculado em sistema.py — mesma
    noção de eficiência exergética da Eq. 17.4) descontada exponencialmente
    pelo erro de reconstrução do VAE."""
    razao = float(np.clip(razao_reversivel, 0.0, 1.0))
    return float(razao * np.exp(-max(0.0, float(e_rec))))


__all__ = [
    "parametros_basquin",
    "dano_incremental",
    "taxa_dano_gp",
    "projetar_rul_fadiga",
    "calcular_ehi",
]
