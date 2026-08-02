"""Cascata completa do trem de ar comprimido.

Encadeia: filtro de admissão → estágio LP → intercooler → estágio HP →
aftercooler → separador → secador PSA → vaso pulmão/rede.

Equações do livro compressores.tex (números indicados ao longo do código).
Convenções: SI, pressões absolutas (Pa), temperaturas em K.
"""

from __future__ import annotations

import math

from . import nucleo, subsistemas
from .constantes import (
    CP_AR,
    DELTA_T_REGEN,
    DEMANDA_M3_MIN,
    DP_NOM_PSA,
    ETA_MECANICA,
    ETA_SEPARADOR,
    FAD_DEFAULT_M3_MIN,
    FATOR_PURGA,
    FOLGA_REL_DEFAULT,
    K_FOLGA,
    N_COMPRESSORES_DEFAULT,
    N_POLITROPICO,
    P_ATM,
    PDP_ALVO_C,
    PI_REDE_DEFAULT,
    P_LIMITE_REDE,
    R_AR,
    RF_FOULING_DEFAULT,
    T_AGUA_DEFAULT,
    T_AMB_DEFAULT,
    UA_PROJETO,
    UR_AMB_DEFAULT,
    VI_DEFAULT,
    V_VASO_DEFAULT,
    W_DRUM_PADRAO,
    ZETA_FILTRO,
)

D_DUTO_ADMISSAO = 0.10  # m, diâmetro do duto de admissão — ASSUMIDO


def parametros_default() -> dict:
    """Conjunto default de parâmetros (origem de cada valor: constantes.py)."""
    return {
        "t_amb": T_AMB_DEFAULT,
        "ur_amb": UR_AMB_DEFAULT,
        "p_amb": P_ATM,
        "pi_total": PI_REDE_DEFAULT,
        "fad_m3_min": FAD_DEFAULT_M3_MIN,
        "n_compressores": N_COMPRESSORES_DEFAULT,
        "n": N_POLITROPICO,
        "v_i": VI_DEFAULT,
        "eta_mec": ETA_MECANICA,
        "k_folga": K_FOLGA,
        "folga_rel": FOLGA_REL_DEFAULT,
        "zeta_filtro": ZETA_FILTRO,
        "t_agua": T_AGUA_DEFAULT,
        "ua_projeto": UA_PROJETO,
        "r_f_equiv": RF_FOULING_DEFAULT,
        "eta_sep": ETA_SEPARADOR,
        "fator_purga": FATOR_PURGA,
        "delta_t_regen": DELTA_T_REGEN,
        "v_vaso": V_VASO_DEFAULT,
        "p_limite": P_LIMITE_REDE,
        "demanda_m3_min": DEMANDA_M3_MIN,
        "dp_real_psa": DP_NOM_PSA,   # medido — default = nominal (leito limpo)
        "pdp_real_c": PDP_ALVO_C,    # medido — default = alvo (secador saudável)
    }


def simular(par: dict | None = None) -> dict:
    """Roda a cascata completa e devolve estados, potências e KPIs.

    Parâmetros: dict no formato de `parametros_default()` (ou None = defaults).
    Retorna dict com chaves: `nos`, `potencias`, `kpis`, `avisos`. O trem
    termodinâmico (`nos`, potências por unidade) é calculado para **uma**
    unidade — `n_compressores` unidades idênticas operam em paralelo
    (mesmo ponto de operação cada uma), somando-se apenas nas grandezas de
    planta (`w_total_planta`, `fad_total_m3_min` em `potencias`/`kpis`).
    """
    p = {**parametros_default(), **(par or {})}
    n_comp = max(1, int(round(p["n_compressores"])))
    avisos: list[str] = []

    # --- 0. Admissão ---------------------------------------------------------
    v_dot_fad = p["fad_m3_min"] / 60.0              # m³/s (ar livre)
    rho_amb = nucleo.densidade_ar(p["p_amb"], p["t_amb"])
    eta_v_lp = nucleo.eficiencia_volumetrica(
        p["k_folga"], p["folga_rel"], math.sqrt(p["pi_total"]))
    m_dot = rho_amb * v_dot_fad * eta_v_lp          # kg/s (Eq. 9.3 ajusta vazão)

    area_duto = math.pi * D_DUTO_ADMISSAO**2 / 4.0
    v_duto = v_dot_fad / area_duto
    dp_filtro = nucleo.delta_p_filtro(p["zeta_filtro"], rho_amb, v_duto)  # Eq. 5.4
    p0 = p["p_amb"] - dp_filtro
    w_amb = nucleo.razao_umidade(p["t_amb"], p["p_amb"], p["ur_amb"])     # Eq. 10.6

    # Vazão de AR SECO real entregue por um FAD de ar ÚMIDO — fórmula
    # psicrométrica padrão (ASHRAE): volume específico do ar úmido por kg de
    # ar seco é v = (R_ar·T/P)·(1+1,6078·W). "m_dot" acima segue sendo a
    # base do trabalho de compressão (Eqs. 5.5/5.8/5.9) e fica deliberadamente
    # sem essa correção: com vazão VOLUMÉTRICA fixa (regime de deslocamento
    # positivo), P·V=nRT diz que o número de mols admitidos por ciclo não
    # depende de quais moléculas são — o trabalho de compressão é, portanto,
    # ~invariante à umidade. Quem MUDA com a umidade é quanto ar seco útil sai
    # dessa mesma vazão volumétrica: "m_dot_seco" alimenta tudo que é balanço
    # de massa de verdade (condensado, calor sensível via cp_úmido, purga,
    # tabela de estados) — nunca a cadeia de potência.
    m_dot_seco = m_dot / (1.0 + 1.6078 * w_amb)

    # --- 1. Divisão de estágios (geométrica, intercooler ideal) --------------
    p_rede = p["p_amb"] * p["pi_total"]
    pi_lp = pi_hp = math.sqrt(p["pi_total"] * p["p_amb"] / p0)
    p_inter = p0 * pi_lp                            # saída LP / entrada HP

    # --- 2. Estágio LP --------------------------------------------------------
    v_dot_lp = m_dot * R_AR * p["t_amb"] / p0       # vazão volumétrica na sucção
    w_lp = nucleo.potencia_politropica(             # Eq. 5.5
        p0, v_dot_lp, pi_lp, p["n"], p["eta_mec"])
    perda_vi_lp = nucleo.perda_vi(                  # Eqs. 5.8/5.9
        p0, v_dot_lp * (p0 / p_inter), pi_lp, p["v_i"], p["n"])
    t_lp_out = nucleo.temperatura_descarga(p["t_amb"], pi_lp, p["n"])  # Eq. 11.1

    # --- 3. Intercooler -------------------------------------------------------
    ua = subsistemas.ua_com_fouling(p["ua_projeto"], p["r_f_equiv"])   # Eq. 10.5
    c_ar = m_dot_seco * nucleo.cp_umido(w_amb)                         # Eq. 10.8
    t_hp_in = subsistemas.saida_trocador(t_lp_out, p["t_agua"], ua, c_ar)
    eps_inter = subsistemas.efetividade(t_lp_out, t_hp_in, p["t_agua"])  # Eq. 10.3
    q_inter = subsistemas.calor_trocado(m_dot_seco, c_ar / m_dot_seco, t_lp_out, t_hp_in)
    # condensado no intercooler: sai saturado na pressão intermediária (Eq. 10.6)
    w_sat_inter = nucleo.razao_umidade(t_hp_in, p_inter, 1.0)
    cond_inter = nucleo.condensado(m_dot_seco, w_amb, w_sat_inter)
    w_hp_in = min(w_amb, w_sat_inter)

    # --- 4. Estágio HP --------------------------------------------------------
    v_dot_hp = m_dot * R_AR * t_hp_in / p_inter
    w_hp = nucleo.potencia_politropica(             # Eq. 5.5
        p_inter, v_dot_hp, pi_hp, p["n"], p["eta_mec"])
    perda_vi_hp = nucleo.perda_vi(                  # Eqs. 5.8/5.9
        p_inter, v_dot_hp * (p_inter / p_rede), pi_hp, p["v_i"], p["n"])
    t_hp_out = nucleo.temperatura_descarga(t_hp_in, pi_hp, p["n"])     # Eq. 11.1

    # --- 5. Aftercooler + separador -------------------------------------------
    t_pos_after = subsistemas.saida_trocador(t_hp_out, p["t_agua"], ua, c_ar)
    q_after = subsistemas.calor_trocado(m_dot_seco, CP_AR, t_hp_out, t_pos_after)
    w_sat_after = nucleo.razao_umidade(t_pos_after, p_rede, 1.0)
    cond_after = nucleo.condensado(m_dot_seco, w_hp_in, w_sat_after)   # Eq. 14.3
    agua_arraste = subsistemas.arraste(cond_after, p["eta_sep"])       # Eq. 14.4
    w_pos_sep = min(w_hp_in, w_sat_after) + agua_arraste / m_dot_seco

    # --- 6. Secador PSA --------------------------------------------------------
    m_purge = p["fator_purga"] * m_dot_seco         # fração de 10–18 % (:1971)
    eta_pur = subsistemas.eta_purga(m_purge, m_dot_seco)               # Eq. 15.9
    p_aquecedor = subsistemas.potencia_aquecedor(                      # Eq. 3.3
        m_purge, p["delta_t_regen"])
    m_dot_util = m_dot_seco - m_purge
    # W de saída = saturação no PDP real medido (Eq. 10.6, mesma convenção de
    # w_sat_inter/w_sat_after acima) — não mais W=0 fixo, que era um "ar
    # infinitamente seco" sem base física. Liga o secador à mesma leitura de
    # PDP real usada em HI_des (Eq. 15.7): degradar o PDP medido agora reduz
    # de fato a qualidade do ar entregue à rede, não só o índice de saúde.
    w_pos_secador = nucleo.razao_umidade(p["pdp_real_c"] + 273.15, p_rede, 1.0)
    sec_dry = subsistemas.sec_dry(p_aquecedor, W_DRUM_PADRAO, m_dot_util)  # Eq. 15.6
    hi_des = subsistemas.hi_des(                                      # Eq. 15.7
        DP_NOM_PSA, p["dp_real_psa"], PDP_ALVO_C, p["pdp_real_c"])

    # --- 7. Vaso pulmão / rede -------------------------------------------------
    # m_dot_util é de UMA unidade; o vaso/rede recebe a soma das n_comp
    # unidades em paralelo (ver docstring de simular()).
    demanda_m3_s = p["demanda_m3_min"] / 60.0
    m_dot_demanda = rho_amb * demanda_m3_s
    dp_dt = subsistemas.dp_dt_vaso(                                    # Eq. 16.4
        p["v_vaso"], t_pos_after, m_dot_util * n_comp, m_dot_demanda)
    t_autonomia = subsistemas.autonomia_vaso(                          # Eq. 16.5
        p["v_vaso"], p_rede, p["p_limite"], demanda_m3_s, p["p_amb"])

    # --- 8. Totais e KPIs ------------------------------------------------------
    w_iso = nucleo.potencia_isotermica(             # referência das Eqs. 5.12/5.13
        p["p_amb"], v_dot_fad, p["pi_total"])
    w_total = w_lp + w_hp + perda_vi_lp + perda_vi_hp + p_aquecedor
    eta_global = w_iso / w_total if w_total > 0 else 0.0
    spc_valor = nucleo.spc(w_total, p["fad_m3_min"])                   # Eq. 11.11

    if t_hp_out - 273.15 < 100.0:
        avisos.append("Descarga HP abaixo de 100 °C — atípico (:584).")
    if not 0.0 <= eps_inter <= 1.0:
        avisos.append("Efetividade do intercooler fora de [0,1] — verificar UA/fouling.")

    # "m_dot" na tabela abaixo é "m_dot_seco" (vazão de AR SECO) — invariante
    # ao longo da compressão/resfriamento (convenção padrão de psicrometria:
    # só a água muda de fase, o ar seco não condensa). É por isso que ela não
    # cai nos pontos onde há condensação — quem cai ali é "w" (razão de
    # umidade). Para não parecer que a massa se perde sem explicação (ou
    # pior, que "aumenta"), cada ponto também traz "m_dot_total" =
    # ṁ_seco·(1+w), a vazão real da corrente (ar + vapor d'água ainda não
    # condensado) — essa sim cai em CADA ponto de condensação, e cai de novo
    # (por um motivo diferente: purga, não condensação) no secador PSA.
    # PDP (ponto de orvalho sob pressão) em cada ponto — Eqs. 10.6+10.7
    # combinadas (razão de umidade -> pressão de vapor -> inversão de Buck).
    # É a MESMA leitura que um sensor T_dp reportaria naquele ponto do trem;
    # calculada para os 6 pontos por igual, para nenhum acessório do fluxo
    # ficar sem essa grandeza.
    pdp_admissao_c = nucleo.temp_orvalho_de_w(w_amb, p0)
    pdp_pos_inter_c = nucleo.temp_orvalho_de_w(w_hp_in, p_inter)
    pdp_pos_after_c = nucleo.temp_orvalho_de_w(w_pos_sep, p_rede)
    pdp_pos_secador_c = nucleo.temp_orvalho_de_w(w_pos_secador, p_rede)

    nos = [
        {"nome": "Admissão (pós-filtro)", "p_bar": p0 / 1e5,
         "t_c": p["t_amb"] - 273.15, "m_dot": m_dot_seco, "w": w_amb,
         "m_dot_total": m_dot_seco * (1.0 + w_amb), "pdp_c": pdp_admissao_c},
        {"nome": "Descarga LP", "p_bar": p_inter / 1e5,
         "t_c": t_lp_out - 273.15, "m_dot": m_dot_seco, "w": w_amb,
         "m_dot_total": m_dot_seco * (1.0 + w_amb),
         "pdp_c": nucleo.temp_orvalho_de_w(w_amb, p_inter)},
        {"nome": "Entrada HP (pós-intercooler)", "p_bar": p_inter / 1e5,
         "t_c": t_hp_in - 273.15, "m_dot": m_dot_seco, "w": w_hp_in,
         "m_dot_total": m_dot_seco * (1.0 + w_hp_in), "pdp_c": pdp_pos_inter_c},
        {"nome": "Descarga HP", "p_bar": p_rede / 1e5,
         "t_c": t_hp_out - 273.15, "m_dot": m_dot_seco, "w": w_hp_in,
         "m_dot_total": m_dot_seco * (1.0 + w_hp_in),
         "pdp_c": nucleo.temp_orvalho_de_w(w_hp_in, p_rede)},
        {"nome": "Saída aftercooler", "p_bar": p_rede / 1e5,
         "t_c": t_pos_after - 273.15, "m_dot": m_dot_seco, "w": w_pos_sep,
         "m_dot_total": m_dot_seco * (1.0 + w_pos_sep), "pdp_c": pdp_pos_after_c},
        {"nome": "Rede (pós-secador)", "p_bar": p_rede / 1e5,
         "t_c": t_pos_after - 273.15, "m_dot": m_dot_util, "w": w_pos_secador,
         "m_dot_total": m_dot_util * (1.0 + w_pos_secador),
         "pdp_c": pdp_pos_secador_c},
    ]

    return {
        "nos": nos,
        "potencias": {
            "w_lp": w_lp, "w_hp": w_hp,
            "perda_vi_lp": perda_vi_lp, "perda_vi_hp": perda_vi_hp,
            "aquecedor": p_aquecedor, "w_total": w_total,
            "w_isotermico": w_iso,
            "q_intercooler": q_inter, "q_aftercooler": q_after,
            # --- Planta (n_comp unidades idênticas em paralelo) ---
            "n_compressores": n_comp,
            "w_total_planta": w_total * n_comp,
        },
        "kpis": {
            "spc": spc_valor,
            "eta_global": eta_global,
            "eta_v_lp": eta_v_lp,
            "t_descarga_hp_c": t_hp_out - 273.15,
            "efetividade_intercooler": eps_inter,
            "condensado_total_kg_h": (cond_inter + cond_after) * 3600.0,
            "purga_pct": (1.0 - eta_pur) * 100.0,
            "dp_filtro_mbar": dp_filtro / 100.0,
            "dp_dt_vaso_bar_min": dp_dt * 60.0 / 1e5,
            "autonomia_min": t_autonomia / 60.0,
            "p_intermediaria_bar": p_inter / 1e5,
            "pdp_alvo_c": PDP_ALVO_C,
            "sec_dry_kj_kg": sec_dry / 1000.0,
            "hi_des": hi_des,
            "fad_total_m3_min": p["fad_m3_min"] * n_comp,
            "condensado_total_planta_kg_h":
                (cond_inter + cond_after) * 3600.0 * n_comp,
        },
        "avisos": avisos,
    }


__all__ = ["parametros_default", "simular"]
