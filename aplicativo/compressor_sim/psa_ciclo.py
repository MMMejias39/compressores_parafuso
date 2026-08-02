"""Ciclo de chaveamento das torres do secador PSA (Cap. 15).

Generaliza o princípio de alternância de duas torres da Figura 15.1 para N
torres em rodízio (round-robin), com **três fases** por torre — não duas:

1. **Adsorvendo**: capacidade decai pela Eq. 15.1 do livro.
2. **Regenerando**: leito é aquecido/purgado; capacidade recupera até q_eq —
   modelada como retorno linear, uma simplificação de modelagem (não uma
   equação do livro, o Capítulo 15 não fecha a cinética de dessorção).
3. **Resfriando**: a capacidade já foi quimicamente restaurada ao fim da
   regeneração, mas o leito ainda está quente — a adsorção é pouco eficaz
   até esfriar, então a torre fica fora de serviço por mais um tempo
   (`t_resfriamento_min`, ASSUMIDO) antes de voltar à fila de adsorção.
   Sem essa fase, o rodízio simula uma troca instantânea entre regeneração
   e adsorção que não existe fisicamente.

Diferente da primeira versão deste módulo, `t_ads_min` e `t_regen_min` são
parâmetros **independentes** (não mais derivados de `t_ciclo/n_vasos`) — o
que significa que a cobertura contínua (sempre pelo menos 1 torre
adsorvendo) deixa de ser garantida por construção. Isso é proposital: com
N torres pequeno e tempo de regeneração+resfriamento longo relativo ao
tempo de adsorção, pode haver um intervalo em que **nenhuma** torre está
disponível para secar — exatamente o cenário que motivou a fase de
resfriamento, e uma limitação real de projetos de PSA subdimensionados
(poucas torres para o tempo de ciclo). O módulo não esconde isso: calcula
e reporta `n_adsorvendo_min` e `tempo_sem_secagem_min`, e o app avisa o
usuário se esse tempo for maior que zero.

Convenções: tempo em minutos nas equações de adsorção (mesma base
adimensional t_ads/t_res da Eq. 15.1/Figura 15.2 do livro), vazões em kg/s.
"""

from __future__ import annotations

import numpy as np


def simular_ciclo_psa(
    horizonte_min: float,
    m_dot_ar: float,
    t_ads_min: float,
    t_regen_min: float,
    t_resfriamento_min: float,
    n_vasos: int,
    k_ads: float,
    t_res_min: float,
    p_low: float,
    p_high: float,
    fator_purga: float,
    dt_min: float = 0.05,
) -> dict:
    """Simula o rodízio de N torres PSA (3 fases) e devolve séries + KPIs.

    m_dot_ar: vazão de ar a secar [kg/s] — de UM compressor ou da PLANTA
    inteira, conforme a topologia escolhida ("por compressor" vs.
    "por sistema", ver app.py). Eq. 15.2 usa essa vazão para a purga.
    """
    n_vasos = max(2, int(round(n_vasos)))
    t_ciclo = t_ads_min + t_regen_min + t_resfriamento_min
    n = int(round(horizonte_min / dt_min)) + 1
    t = np.linspace(0.0, horizonte_min, n)

    q_no_inicio_regen = np.exp(-k_ads * t_ads_min / t_res_min)

    q_norm = np.empty((n_vasos, n))
    estado = np.empty((n_vasos, n), dtype=object)

    for i in range(n_vasos):
        offset = i * t_ciclo / n_vasos
        fase = (t - offset) % t_ciclo

        adsorvendo = fase < t_ads_min
        regenerando = (fase >= t_ads_min) & (fase < t_ads_min + t_regen_min)
        resfriando = fase >= t_ads_min + t_regen_min

        estado[i, adsorvendo] = "Adsorvendo"
        estado[i, regenerando] = "Regenerando"
        estado[i, resfriando] = "Resfriando"

        # --- Adsorção: Eq. 15.1 — q_d/q_eq = exp(-k_ads * t_ads/t_res) ---
        q_norm[i, adsorvendo] = np.exp(-k_ads * fase[adsorvendo] / t_res_min)

        # --- Regeneração: recuperação linear até q_eq (simplificação) ---
        frac_regen = (fase[regenerando] - t_ads_min) / t_regen_min
        q_norm[i, regenerando] = (
            q_no_inicio_regen + (1.0 - q_no_inicio_regen) * frac_regen
        )

        # --- Resfriamento: capacidade já restaurada, torre fora de serviço ---
        q_norm[i, resfriando] = 1.0

    n_adsorvendo = np.sum(estado == "Adsorvendo", axis=0)
    n_regenerando_arr = np.sum(estado == "Regenerando", axis=0)

    # Eq. 15.2 — cada torre regenerando simultaneamente puxa sua própria purga
    m_purge = m_dot_ar * (p_low / p_high) * fator_purga * n_regenerando_arr

    n_trocas = 0
    for i in range(n_vasos):
        transicoes = np.diff((estado[i] == "Regenerando").astype(int))
        n_trocas += int(np.sum(transicoes == 1))

    adsorvendo_0 = estado[0] == "Adsorvendo"
    q_min = float(q_norm[0, adsorvendo_0].min()) if np.any(adsorvendo_0) else 1.0

    tempo_sem_secagem_min = float(np.sum(n_adsorvendo == 0)) * dt_min

    return {
        "t_min": t,
        "q_norm": q_norm,
        "estado": estado,
        "m_purge_kg_s": m_purge,
        "n_adsorvendo": n_adsorvendo,
        "kpis": {
            "n_trocas": n_trocas,
            "q_min": q_min,
            "purga_media_kg_s": float(np.mean(m_purge)),
            "t_ciclo_min": t_ciclo,
            "n_adsorvendo_min": int(n_adsorvendo.min()),
            "tempo_sem_secagem_min": tempo_sem_secagem_min,
        },
    }


__all__ = ["simular_ciclo_psa"]
