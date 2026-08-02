"""Ciclo de chaveamento das torres do secador PSA (Cap. 15).

Generaliza o princípio de alternância de duas torres da Figura 15.1 para N
torres em rodízio (round-robin): a cada instante, exatamente 1 torre
regenera enquanto as demais N-1 adsorvem, com o papel rotacionando
ciclicamente e igualmente espaçado no tempo. A capacidade de adsorção
durante a fase ativa segue a Eq. 15.1 do livro; a recuperação durante a
regeneração é modelada como um retorno linear a q_eq — é uma simplificação
de modelagem (não uma equação do livro, o Capítulo 15 não fecha a cinética
de dessorção), marcada como tal.

Convenções: tempo em minutos nas equações de adsorção (mesma base
adimensional t_ads/t_res da Eq. 15.1/Figura 15.2 do livro), vazões em kg/s.
"""

from __future__ import annotations

import numpy as np


def simular_ciclo_psa(
    horizonte_min: float,
    m_dot_ar: float,
    t_ciclo_min: float,
    n_vasos: int,
    k_ads: float,
    t_res_min: float,
    p_low: float,
    p_high: float,
    fator_purga: float,
    dt_min: float = 0.1,
) -> dict:
    """Simula o rodízio de N torres PSA e devolve séries temporais + KPIs.

    m_dot_ar: vazão de ar a secar [kg/s] — de UM compressor ou da PLANTA
    inteira, conforme a topologia escolhida ("por compressor" vs.
    "por sistema", ver app.py). Eq. 15.2 usa essa vazão para a purga.
    """
    n_vasos = max(2, int(round(n_vasos)))
    n = int(round(horizonte_min / dt_min)) + 1
    t = np.linspace(0.0, horizonte_min, n)

    t_regen = t_ciclo_min / n_vasos
    t_ads_max = t_ciclo_min - t_regen
    q_no_inicio_regen = np.exp(-k_ads * t_ads_max / t_res_min)

    # Índice de slot global (determinístico, computado uma única vez) — evita a
    # ambiguidade de ponto flutuante de avaliar a fronteira independentemente
    # para cada torre, o que já produziu instantes com 0 ou 2 torres
    # "regenerando" simultaneamente por arredondamento.
    slot = np.floor(t / t_regen).astype(np.int64)
    torre_regenerando = slot % n_vasos

    q_norm = np.empty((n_vasos, n))
    estado = np.empty((n_vasos, n), dtype=object)

    for i in range(n_vasos):
        is_regen = torre_regenerando == i
        estado[i, is_regen] = "Regenerando"
        estado[i, ~is_regen] = "Adsorvendo"

        # --- Regeneração: recuperação linear até q_eq (simplificação) ---
        t_regen_decorrido = t - slot * t_regen
        frac_regen = np.clip(t_regen_decorrido / t_regen, 0.0, 1.0)
        q_norm[i, is_regen] = (
            q_no_inicio_regen + (1.0 - q_no_inicio_regen) * frac_regen[is_regen]
        )

        # --- Adsorção: Eq. 15.1 — q_d/q_eq = exp(-k_ads * t_ads/t_res) ---
        # tempo decorrido desde o fim da última regeneração DESTA torre
        slot_i = slot - ((slot - i) % n_vasos)
        t_ads_decorrido = t - (slot_i + 1) * t_regen
        q_norm[i, ~is_regen] = np.exp(
            -k_ads * t_ads_decorrido[~is_regen] / t_res_min
        )

    # --- Purga de regeneração (Eq. 15.2), ativa enquanto houver torre regenerando ---
    n_regenerando = np.sum(estado == "Regenerando", axis=0)
    m_purge = np.where(
        n_regenerando > 0, m_dot_ar * (p_low / p_high) * fator_purga, 0.0
    )

    n_trocas = 0
    for i in range(n_vasos):
        transicoes = np.diff((estado[i] == "Regenerando").astype(int))
        n_trocas += int(np.sum(transicoes == 1))

    adsorvendo_0 = estado[0] == "Adsorvendo"
    q_min = float(q_norm[0, adsorvendo_0].min()) if np.any(adsorvendo_0) else 1.0

    return {
        "t_min": t,
        "q_norm": q_norm,
        "estado": estado,
        "m_purge_kg_s": m_purge,
        "kpis": {
            "n_trocas": n_trocas,
            "q_min": q_min,
            "purga_media_kg_s": float(np.mean(m_purge)),
            "t_ads_max_min": t_ads_max,
            "t_regen_min": t_regen,
        },
    }


__all__ = ["simular_ciclo_psa"]
