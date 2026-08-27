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
    ALPHA_CARCACA,
    ALPHA_ROTOR,
    COND_ARREF_CARCACA_LP,
    COND_EXT_CARCACA_LP,
    COND_ROTOR_W_K,
    CP_AR,
    C_CARCACA_LP,
    DELTA_NOM_UM,
    DELTA_T_REGEN,
    DEMANDA_M3_MIN,
    DP_NOM_PSA,
    D_LINHA_DEFAULT,
    D_P_PARTICULA_M,
    D_VASO_PSA_M,
    EPSILON_RECUP_PSA_DEFAULT,
    ETA_MECANICA,
    ETA_SEPARADOR,
    FAD_DEFAULT_M3_MIN,
    FATOR_PURGA,
    FOLGA_REL_DEFAULT,
    F_D_LINHA_DEFAULT,
    HOOD_ENCLAUSURADO_DEFAULT,
    K_FOLGA,
    L_CARCACA_M,
    L_LEITO_PSA_M,
    L_LINHA_DEFAULT,
    L_ROTOR_M,
    MU_AR_REGEN,
    M_CARCACA_LP,
    M_DOT_VENT_DEFAULT,
    N_COMPRESSORES_DEFAULT,
    N_POLITROPICO,
    PDP_ALVO_C,
    PI_REDE_DEFAULT,
    POROSIDADE_LEITO_PSA,
    PSI_P_ESFERA,
    P_ATM,
    P_FIXAS_MOTOR_DEFAULT,
    P_LIMITE_REDE,
    P_LOSS_HOOD_OUTROS_DEFAULT,
    Q_COND_EIXO_W,
    R_AR,
    RF_FOULING_DEFAULT,
    S_MOTOR_DEFAULT,
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
        "m_carcaca": M_CARCACA_LP,
        "c_carcaca": C_CARCACA_LP,
        "cond_ext_carcaca": COND_EXT_CARCACA_LP,
        "cond_arref_carcaca": COND_ARREF_CARCACA_LP,
        "s_motor": S_MOTOR_DEFAULT,
        "p_fixas_motor": P_FIXAS_MOTOR_DEFAULT,
        "m_dot_vent": M_DOT_VENT_DEFAULT,
        "p_loss_hood_outros": P_LOSS_HOOD_OUTROS_DEFAULT,
        "hood_enclausurado": HOOD_ENCLAUSURADO_DEFAULT,
        "f_d_linha": F_D_LINHA_DEFAULT,
        "l_linha": L_LINHA_DEFAULT,
        "d_linha": D_LINHA_DEFAULT,
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
        "eps_recup_psa": EPSILON_RECUP_PSA_DEFAULT,  # Eq. 15.11
        # --- Rotor: balanço térmico e folga residual (Eqs. 9.7/9.18/9.19) ---
        "cond_rotor": COND_ROTOR_W_K,
        "q_cond_eixo": Q_COND_EIXO_W,
        "delta_nom_um": DELTA_NOM_UM,
        "alpha_rotor": ALPHA_ROTOR,
        "l_rotor": L_ROTOR_M,
        "alpha_carcaca": ALPHA_CARCACA,
        "l_carcaca": L_CARCACA_M,
        # --- Secador PSA: forma da partícula e geometria do leito (Eq. 15.17) ---
        "psi_p": PSI_P_ESFERA,
        "d_p_particula": D_P_PARTICULA_M,
        "porosidade_leito": POROSIDADE_LEITO_PSA,
        "l_leito_psa": L_LEITO_PSA_M,
        "d_vaso_psa": D_VASO_PSA_M,
        "mu_ar_psa": MU_AR_REGEN,
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

    # --- 2b. Calor interno da carcaça do estágio LP (Eq. 9.14) ---------------
    # T_c em si só é calculado mais adiante (passo 8b), depois que a
    # temperatura de referência (T_amb a céu aberto, ou T_hood se
    # enclausurado) estiver definida.
    q_int_lp = nucleo.q_int_carcaca(w_lp, p["eta_mec"])

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

    # --- 4b. Perda de carga na tubulação interestágios (Eq. 5.15) ------------
    # Diagnóstico: reporta a correção de pressão que o restante da cascata
    # (que trata p_inter como um único valor comum a LP/intercooler/HP,
    # simplificação já registrada no livro) ainda não aplica. Um trecho
    # representativo (LP→HP), não os 3 trechos separados do livro.
    v_dot_lp_out = m_dot * R_AR * t_lp_out / p_inter
    area_linha = math.pi * p["d_linha"]**2 / 4.0
    v_linha = v_dot_lp_out / area_linha
    rho_linha = nucleo.densidade_ar(p_inter, t_lp_out)
    dp_linha = nucleo.delta_p_linha(                                   # Eq. 5.15
        p["f_d_linha"], p["l_linha"], p["d_linha"], rho_linha, v_linha)
    p_hp_suc_efetiva = p_inter - dp_linha

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
    p_aquecedor_nominal = subsistemas.potencia_aquecedor(               # Eq. 3.3
        m_purge, p["delta_t_regen"])
    m_dot_util = m_dot_seco - m_purge
    # W de saída = saturação no PDP real medido (Eq. 10.6, mesma convenção de
    # w_sat_inter/w_sat_after acima) — não mais W=0 fixo, que era um "ar
    # infinitamente seco" sem base física. Liga o secador à mesma leitura de
    # PDP real usada em HI_des (Eq. 15.7): degradar o PDP medido agora reduz
    # de fato a qualidade do ar entregue à rede, não só o índice de saúde.
    w_pos_secador = nucleo.razao_umidade(p["pdp_real_c"] + 273.15, p_rede, 1.0)

    # --- 6b. Perda de carga do leito via Ergun (Eq. 15.17, 16/08/2026) —
    # substitui o antigo DP_NOM_PSA fixo (ASSUMIDO) por um valor calculado a
    # partir da geometria do vaso/partícula e da vazão real, incluindo o
    # efeito da esfericidade ψ_p (pellets vs. esferas, Eq. 15.18 para
    # k_ads análogo). Como dp_real_psa (medido) continua com default =
    # DP_NOM_PSA (constante antiga), HI_des deixa de ser exatamente 1,0 por
    # construção no caso saudável — o desvio revela se a geometria
    # configurada bate com a suposição original de 0,30 bar, em vez de
    # esconder essa checagem.
    rho_ar_leito = nucleo.densidade_ar(p_rede, t_pos_after)
    area_vaso_psa = math.pi * p["d_vaso_psa"] ** 2 / 4.0
    v_s_psa = m_dot_util / (rho_ar_leito * area_vaso_psa)
    dp_nom_psa_calc = subsistemas.perda_carga_ergun(                  # Eq. 15.17
        p["mu_ar_psa"], v_s_psa, rho_ar_leito, p["psi_p"],
        p["d_p_particula"], p["porosidade_leito"], p["l_leito_psa"])
    hi_des = subsistemas.hi_des(                                      # Eq. 15.7
        dp_nom_psa_calc, p["dp_real_psa"], PDP_ALVO_C, p["pdp_real_c"])

    # --- 7. Vaso pulmão / rede -------------------------------------------------
    # m_dot_util é de UMA unidade; o vaso/rede recebe a soma das n_comp
    # unidades em paralelo (ver docstring de simular()).
    demanda_m3_s = p["demanda_m3_min"] / 60.0
    m_dot_demanda = rho_amb * demanda_m3_s
    dp_dt = subsistemas.dp_dt_vaso(                                    # Eq. 16.4
        p["v_vaso"], t_pos_after, m_dot_util * n_comp, m_dot_demanda)
    t_autonomia = subsistemas.autonomia_vaso(                          # Eq. 16.5
        p["v_vaso"], p_rede, p["p_limite"], demanda_m3_s, p["p_amb"])

    # --- 8a. Motor (Eqs. 4.10-4.12), invólucro/Hood (Eqs. 2.1/2.4) e -----------
    #         fechamento da carcaça do estágio LP (Eq. 9.6/9.16) ---------------
    # p_eixo_mot é a potência mecânica de eixo (compressão + perdas V_i),
    # sem o aquecedor de regeneração — que é carga elétrica resistiva, não
    # potência mecânica entregue pelo motor.
    p_eixo_mot = w_lp + w_hp + perda_vi_lp + perda_vi_hp
    p_ag = nucleo.potencia_entreferro(p_eixo_mot, p["s_motor"])        # Eq. 4.12 invertida
    p_perdas_mot = nucleo.perdas_motor(p["s_motor"], p_ag, p["p_fixas_motor"])  # Eq. 4.11
    eta_mot = nucleo.eficiencia_motor(p_eixo_mot, p_ag, p["p_fixas_motor"])     # Eq. 4.12

    # Q_casco = Q_int em regime permanente (identidade que fecha a
    # circularidade entre Eq. 2.1 e Eq. 9.6 — ver CONTEXTO.md).
    q_gerado_hood = nucleo.calor_gerado_hood(                          # Eq. 2.1
        p_perdas_mot, p["p_loss_hood_outros"], q_int_lp)
    t_hood = nucleo.temperatura_hood_regime(                           # Eq. 2.4
        q_gerado_hood, p["m_dot_vent"], CP_AR, p["t_amb"])

    # --- 8b. Aproveitamento de calor rejeitado na regeneração (Eqs. 15.10/
    # 15.11, 16/08/2026 — descritas no livro desde antes desta sessão, nunca
    # implementadas no app até agora). Q_disp soma as correntes que o app já
    # calcula (aftercooler + hood); Q_óleo (Cap. 12) fica de fora por não
    # haver um circuito de óleo modelado aqui — omissão explícita, não W=0
    # escondido. O calor recuperado reduz a potência ELÉTRICA do aquecedor
    # resistivo na mesma proporção, sem mudar ΔT_regen (o processo de
    # regeneração continua atingindo a mesma temperatura-alvo — só uma
    # fração dela vem de graça em vez de vir do aquecedor).
    q_disp = q_after + q_gerado_hood                                    # Eq. 15.10
    p_aquecedor = max(                                                   # Eq. 15.11
        0.0, p_aquecedor_nominal - p["eps_recup_psa"] * q_disp)
    sec_dry = subsistemas.sec_dry(p_aquecedor, W_DRUM_PADRAO, m_dot_util)  # Eq. 15.6

    # --- 9. Totais e KPIs (após a correção do aquecedor acima) -----------------
    w_iso = nucleo.potencia_isotermica(             # referência das Eqs. 5.12/5.13
        p["p_amb"], v_dot_fad, p["pi_total"])
    w_total = w_lp + w_hp + perda_vi_lp + perda_vi_hp + p_aquecedor
    eta_global = w_iso / w_total if w_total > 0 else 0.0
    spc_valor = nucleo.spc(w_total, p["fad_m3_min"])                   # Eq. 11.11

    t_ref_carcaca = t_hood if p["hood_enclausurado"] else p["t_amb"]
    t_carcaca = nucleo.temperatura_carcaca_regime(                     # Eq. 9.16
        q_int_lp, p["cond_ext_carcaca"], p["cond_arref_carcaca"], t_ref_carcaca)
    tau_carcaca = nucleo.constante_tempo_carcaca(
        p["m_carcaca"], p["c_carcaca"], p["cond_ext_carcaca"], p["cond_arref_carcaca"])

    # --- 8c. Temperatura do rotor e folga residual térmica (Eqs. 9.7/9.18/
    # 9.19, 16/08/2026) — fecha a metade da Eq. 9.7 que a Eq. 9.16 (T_c)
    # sozinha não cobria. T_gas_med é a média entre sucção e descarga do
    # estágio LP (mesma aproximação do livro, na ausência de perfil de
    # temperatura interno medido). ΔT_r e ΔT_c são tomados acima de T_amb —
    # a referência em que δ_nom foi especificada (máquina fria/parada).
    t_gas_med_lp = (p["t_amb"] + t_lp_out) / 2.0
    t_rotor = nucleo.temperatura_rotor_regime(                        # Eq. 9.19
        t_gas_med_lp, p["q_cond_eixo"], p["cond_rotor"])
    delta_t_rotor = t_rotor - p["t_amb"]
    delta_t_carcaca_termica = t_carcaca - p["t_amb"]
    folga_residual_um = nucleo.folga_residual_termica(                 # Eq. 9.7
        p["delta_nom_um"], p["alpha_rotor"], p["l_rotor"], delta_t_rotor,
        p["alpha_carcaca"], p["l_carcaca"], delta_t_carcaca_termica)

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
    pdp_amb_c = nucleo.temp_orvalho_de_w(w_amb, p["p_amb"])
    pdp_admissao_c = nucleo.temp_orvalho_de_w(w_amb, p0)
    pdp_pos_inter_c = nucleo.temp_orvalho_de_w(w_hp_in, p_inter)
    pdp_pos_after_c = nucleo.temp_orvalho_de_w(w_pos_sep, p_rede)
    pdp_pos_secador_c = nucleo.temp_orvalho_de_w(w_pos_secador, p_rede)

    nos = [
        {"nome": "A: Atmosfera (Ambiente)", "p_bar": p["p_amb"] / 1e5,
         "t_c": p["t_amb"] - 273.15, "m_dot": m_dot_seco, "w": w_amb,
         "m_dot_total": m_dot_seco * (1.0 + w_amb), "pdp_c": pdp_amb_c},
        {"nome": "B: Sucção LP (Pós-Filtro)", "p_bar": p0 / 1e5,
         "t_c": p["t_amb"] - 273.15, "m_dot": m_dot_seco, "w": w_amb,
         "m_dot_total": m_dot_seco * (1.0 + w_amb), "pdp_c": pdp_admissao_c},
        {"nome": "C: Descarga LP", "p_bar": p_inter / 1e5,
         "t_c": t_lp_out - 273.15, "m_dot": m_dot_seco, "w": w_amb,
         "m_dot_total": m_dot_seco * (1.0 + w_amb),
         "pdp_c": nucleo.temp_orvalho_de_w(w_amb, p_inter)},
        {"nome": "D: Entrada HP (Pós-Interc.)", "p_bar": p_inter / 1e5,
         "t_c": t_hp_in - 273.15, "m_dot": m_dot_seco, "w": w_hp_in,
         "m_dot_total": m_dot_seco * (1.0 + w_hp_in), "pdp_c": pdp_pos_inter_c},
        {"nome": "E: Descarga HP", "p_bar": p_rede / 1e5,
         "t_c": t_hp_out - 273.15, "m_dot": m_dot_seco, "w": w_hp_in,
         "m_dot_total": m_dot_seco * (1.0 + w_hp_in),
         "pdp_c": nucleo.temp_orvalho_de_w(w_hp_in, p_rede)},
        {"nome": "F: Saída Aftercooler", "p_bar": p_rede / 1e5,
         "t_c": t_pos_after - 273.15, "m_dot": m_dot_seco, "w": w_pos_sep,
         "m_dot_total": m_dot_seco * (1.0 + w_pos_sep), "pdp_c": pdp_pos_after_c},
        {"nome": "G: Rede (Pós-Secador)", "p_bar": p_rede / 1e5,
         "t_c": t_pos_after - 273.15, "m_dot": m_dot_util, "w": w_pos_secador,
         "m_dot_total": m_dot_util * (1.0 + w_pos_secador),
         "pdp_c": pdp_pos_secador_c},
    ]

    return {
        "nos": nos,
        "potencias": {
            "w_lp": w_lp, "w_hp": w_hp,
            "perda_vi_lp": perda_vi_lp, "perda_vi_hp": perda_vi_hp,
            "aquecedor": p_aquecedor, "aquecedor_nominal": p_aquecedor_nominal,
            "m_dot_util": m_dot_util,
            "q_disp_regen": q_disp, "w_total": w_total,
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
            "q_int_carcaca_w": q_int_lp,
            "t_carcaca_c": t_carcaca - 273.15,
            "delta_t_carcaca_c": t_carcaca - t_ref_carcaca,
            "tau_carcaca_min": tau_carcaca / 60.0,
            "t_ref_carcaca_c": t_ref_carcaca - 273.15,
            "t_rotor_c": t_rotor - 273.15,
            "delta_t_rotor_c": delta_t_rotor,
            "folga_residual_um": folga_residual_um,
            "dp_nom_psa_calc_bar": dp_nom_psa_calc / 1e5,
            "eta_mot": eta_mot,
            "p_ag_w": p_ag,
            "p_perdas_mot_w": p_perdas_mot,
            "q_gerado_hood_w": q_gerado_hood,
            "t_hood_c": t_hood - 273.15,
            "dp_linha_mbar": dp_linha / 100.0,
            "p_hp_suc_efetiva_bar": p_hp_suc_efetiva / 1e5,
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
