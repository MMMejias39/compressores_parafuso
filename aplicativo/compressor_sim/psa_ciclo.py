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

from .constantes import PDP_ALVO_C


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
    t_entrada_c: float,
    delta_t_regen: float,
    pdp_entrada_c: float,
    dt_min: float = 0.05,
) -> dict:
    """Simula o rodízio de N torres PSA (3 fases) e devolve séries + KPIs.

    m_dot_ar: vazão de ar a secar [kg/s] — de UM compressor ou da PLANTA
    inteira, conforme a topologia escolhida ("por compressor" vs.
    "por sistema", ver app.py). Eq. 15.2 usa essa vazão para a purga.
    t_entrada_c: temperatura do ar na entrada do secador [°C] — mesma leitura
    da "Saída aftercooler" da cascata estática (Cap. 14). delta_t_regen: salto
    de temperatura do aquecedor de regeneração (Eq. 3.3), mesmo parâmetro já
    usado para dimensionar sua potência. pdp_entrada_c: ponto de orvalho do
    ar que chega ao secador [°C] — mesma leitura de "Saída aftercooler"
    (`pdp_c`) da cascata estática, usada como o pior caso de PDP de saída
    (ver `pdp_saida_c` abaixo).
    """
    n_vasos = max(2, int(round(n_vasos)))
    t_ciclo = t_ads_min + t_regen_min + t_resfriamento_min
    n = int(round(horizonte_min / dt_min)) + 1
    t = np.linspace(0.0, horizonte_min, n)

    q_no_inicio_regen = np.exp(-k_ads * t_ads_min / t_res_min)

    q_norm = np.empty((n_vasos, n))
    estado = np.empty((n_vasos, n), dtype=object)
    temp_c = np.empty((n_vasos, n))

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

        # --- Temperatura do leito por fase (simplificação de modelagem, a
        # mesma família da recuperação linear de capacidade acima — o Cap. 15
        # não fecha a dinâmica térmica do leito): sobe linearmente durante a
        # regeneração (aquecedor, Eq. 3.3) e desce linearmente durante o
        # resfriamento, formando um perfil triangular por ciclo. Adsorvendo,
        # o leito está na temperatura do ar de entrada.
        temp_c[i, adsorvendo] = t_entrada_c
        temp_c[i, regenerando] = t_entrada_c + delta_t_regen * frac_regen
        if t_resfriamento_min > 0.0:
            frac_resf = (fase[resfriando] - t_ads_min - t_regen_min) / t_resfriamento_min
            frac_resf = np.clip(frac_resf, 0.0, 1.0)
        else:
            frac_resf = 1.0
        temp_c[i, resfriando] = t_entrada_c + delta_t_regen * (1.0 - frac_resf)

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

    # --- Ponto de orvalho na saída, ao longo do tempo (simplificação de
    # modelagem — o Cap. 15 não fecha uma relação entre carga do leito e
    # PDP de saída, só o KPI estático HI_des da Eq. 15.7, alimentado por um
    # PDP "medido" manual). A cada instante, a torre relevante é a que está
    # ADSORVENDO com a MENOR capacidade normalizada restante (a mais
    # próxima do breakthrough) — com N torres em paralelo, é ela que
    # domina a qualidade do ar combinado. Interpolação linear entre o PDP
    # alvo (leito "novo", q_norm=1, ISO 8573-1 Classe 2) e o PDP de entrada
    # (nenhuma remoção, q_norm->0 — o mesmo que aconteceria num
    # breakthrough total). Quando nenhuma torre está adsorvendo
    # (`tempo_sem_secagem_min` > 0), o ar passa sem secagem nenhuma —
    # mesmo limite (q_relevante = 0).
    adsorvendo_mask = estado == "Adsorvendo"
    q_norm_adsorvendo = np.where(adsorvendo_mask, q_norm, np.inf)
    q_relevante = np.min(q_norm_adsorvendo, axis=0)
    q_relevante[~np.any(adsorvendo_mask, axis=0)] = 0.0
    pdp_saida_c = PDP_ALVO_C + (pdp_entrada_c - PDP_ALVO_C) * (1.0 - q_relevante)

    return {
        "t_min": t,
        "q_norm": q_norm,
        "estado": estado,
        "temp_c": temp_c,
        "m_purge_kg_s": m_purge,
        "n_adsorvendo": n_adsorvendo,
        "pdp_saida_c": pdp_saida_c,
        "kpis": {
            "n_trocas": n_trocas,
            "q_min": q_min,
            "purga_media_kg_s": float(np.mean(m_purge)),
            "t_ciclo_min": t_ciclo,
            "n_adsorvendo_min": int(n_adsorvendo.min()),
            "tempo_sem_secagem_min": tempo_sem_secagem_min,
            "pdp_saida_max_c": float(np.max(pdp_saida_c)),
        },
    }


__all__ = ["simular_ciclo_psa"]
