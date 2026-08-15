"""App Streamlit — Simulador de Sistema de Ar Comprimido (compressor de parafuso).

Baseado nas equações do livro "Gêmeo Digital de Sistemas de Compressão
Offshore" (compressores.tex). Executar a partir do diretório `aplicativo/`:

    venv/bin/streamlit run app.py

Abas:
- "Operação estática": ponto de operação do trem completo (cascata steady-state);
- "Dinâmica temporal": transiente de pressão da rede com controle VSD ou
  carga/alívio (Eqs. 13.4, 13.7, 13.8, 16.4);
- "Secagem PSA": rodízio de N torres PSA (Eq. 15.1) com topologia
  configurável (N vasos por compressor ou N vasos compartilhados pela
  planta).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # mesmo backend do scripts/gen_figuras.py

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from compressor_sim import dinamica, nucleo, parametros_default, psa_ciclo, simular

# Paleta e estilo herdados de scripts/gen_figuras.py
NAVY = "#1f3b57"
BLUE = "#2b6cb0"
RED = "#b73a3a"
GREEN = "#2f7a4f"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.grid": True,
    "grid.color": "#dddddd",
    "axes.facecolor": "white",
    "figure.facecolor": "white",
})

st.set_page_config(page_title="Simulador de Compressor de Parafuso",
                   page_icon="🌀", layout="wide")

st.title("Simulador de Sistema de Ar Comprimido — Compressor de Parafuso")
st.caption(
    "Trem completo: filtro → LP → intercooler → HP → aftercooler → separador → "
    "secador PSA → vaso pulmão. Equações do livro *Gêmeo Digital de Sistemas de "
    "Compressão Offshore* (compressores.tex)."
)

defaults = parametros_default()

# ---------------------------------------------------------------------------
# Barra lateral — entradas
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Condições de operação")

    with st.expander("Ambiente", expanded=True):
        t_amb_c = st.slider("Temperatura ambiente [°C]", 0.0, 45.0,
                            defaults["t_amb"] - 273.15, 0.5)
        ur_amb = st.slider("Umidade relativa [%]", 10, 100,
                           int(defaults["ur_amb"] * 100)) / 100.0
        p_amb_bar = st.number_input("Pressão atmosférica [bar abs]", 0.9, 1.1,
                                    defaults["p_amb"] / 1e5, 0.005)

    with st.expander("Compressor (estágios LP/HP)", expanded=True):
        pi_total = st.slider("Pressão de rede [bar abs]", 5.0, 12.0,
                             defaults["pi_total"], 0.1)
        fad = st.number_input(
            "Vazão FAD por unidade [m³/min] (assumido — não consta no livro)",
            1.0, 100.0, defaults["fad_m3_min"], 0.5)
        n_compressores = st.number_input(
            "Compressores idênticos em paralelo (assumido)",
            1, 10, defaults["n_compressores"], 1)
        n_pol = st.slider("Índice politrópico n (Eq. 5.5)", 1.20, 1.40,
                          defaults["n"], 0.01)
        v_i = st.slider("Razão volumétrica interna V_i (Eq. 5.6)", 2.0, 7.0,
                        defaults["v_i"], 0.1)
        eta_mec = st.slider("Eficiência mecânica η_mec", 0.90, 1.00,
                            defaults["eta_mec"], 0.005)
        folga_rel = st.number_input("Folga relativa δ/L (Eq. 9.3)", 0.0, 0.02,
                                    defaults["folga_rel"], 0.001,
                                    format="%.3f")

    with st.expander("Carcaça do estágio LP — balanço térmico (Eq. 9.6)"):
        m_carcaca = st.number_input(
            "Massa térmica da carcaça M_c [kg] (assumido)",
            50.0, 2000.0, defaults["m_carcaca"], 10.0)
        c_carcaca = st.number_input(
            "Calor específico c_c [J/(kg·K)] (assumido — ferro fundido típico)",
            300.0, 900.0, defaults["c_carcaca"], 10.0)
        cond_ext_carcaca = st.number_input(
            "Condutância de convecção externa carcaça-ambiente [W/K] (assumido)",
            1.0, 200.0, defaults["cond_ext_carcaca"], 1.0)
        cond_arref_carcaca = st.number_input(
            "Condutância do arrefecimento ativo/ventilação forçada [W/K] (assumido)",
            1.0, 500.0, defaults["cond_arref_carcaca"], 1.0)

    with st.expander("Motor e invólucro (Hood) — Eqs. 4.10-4.12, 2.1, 2.4"):
        hood_enclausurado = st.checkbox(
            "Compressor dentro de invólucro acústico (Hood)?",
            value=defaults["hood_enclausurado"],
            help="Se marcado, a carcaça do estágio LP (Eq. 9.6) referencia "
                 "T_hood (Eq. 2.4) em vez da temperatura ambiente externa — "
                 "arranjo comum offshore, às vezes com o trem inteiro (motor "
                 "a saída do 2º estágio) no mesmo invólucro por restrição "
                 "de ruído.")
        s_motor = st.slider("Escorregamento do motor s (assumido)",
                            0.005, 0.05, defaults["s_motor"], 0.005,
                            format="%.3f")
        p_fixas_motor = st.number_input(
            "Perdas fixas do motor P_fixas [W] (assumido — ensaio a vazio)",
            200.0, 10000.0, defaults["p_fixas_motor"], 100.0)
        m_dot_vent = st.number_input(
            "Vazão de ventilação forçada do exaustor [kg/s] (assumido)",
            0.05, 5.0, defaults["m_dot_vent"], 0.05)
        p_loss_hood_outros = st.number_input(
            "Perdas de VSD+gearbox no invólucro [W] (assumido — Eqs. 4.3/5.2 "
            "não decompostas neste app)",
            0.0, 10000.0, defaults["p_loss_hood_outros"], 100.0)

    with st.expander("Tubulação interestágios (Eq. 5.15)"):
        f_d_linha = st.number_input(
            "Fator de atrito de Darcy f_D (assumido)",
            0.005, 0.08, defaults["f_d_linha"], 0.005, format="%.3f")
        l_linha = st.number_input(
            "Comprimento do trecho LP→HP [m] (assumido)",
            0.5, 30.0, defaults["l_linha"], 0.5)
        d_linha = st.number_input(
            "Diâmetro interno da linha [m] (assumido)",
            0.02, 0.30, defaults["d_linha"], 0.01)

    with st.expander("Resfriamento e tratamento"):
        t_agua_c = st.slider("Água de resfriamento [°C]", 5.0, 40.0,
                             defaults["t_agua"] - 273.15, 0.5)
        ua = st.number_input("UA de projeto [W/K] (assumido)", 500.0, 20000.0,
                             defaults["ua_projeto"], 100.0)
        r_f = st.number_input("Fouling R_f equivalente (Eq. 10.5)", 0.0, 1e-3,
                              defaults["r_f_equiv"], 1e-5, format="%.5f")
        eta_sep = st.slider("Eficiência do separador η_sep (Eq. 14.4)",
                            0.80, 1.00, defaults["eta_sep"], 0.01)
        purga_pct = st.slider("Purga do secador PSA [%] (:1971)", 5, 25,
                              int(defaults["fator_purga"] * 100))

    with st.expander("Vaso pulmão e rede"):
        v_vaso = st.number_input("Volume do vaso [m³] (assumido)", 0.5, 20.0,
                                 defaults["v_vaso"], 0.5)
        demanda = st.number_input("Demanda da rede [m³/min] (assumido)",
                                  0.0, 100.0, defaults["demanda_m3_min"], 0.5)
        p_limite_bar = st.number_input("Pressão mínima da rede [bar abs]",
                                       3.0, 8.0,
                                       defaults["p_limite"] / 1e5, 0.1)

    with st.expander("Dinâmica temporal (aba 2)"):
        horizonte = st.slider("Horizonte de simulação [min]", 5, 60, 15)
        modo = st.selectbox("Modo de controle (Cap. 13)",
                            ["VSD", "Carga/Alívio"])
        tau_vsd = st.slider(
            "Constante de tempo de rampa do VSD τ [s] (assumido)",
            1.0, 30.0, dinamica.TAU_VSD, 1.0)
        dp_db_bar = st.slider("Banda carga/alívio ΔP_db [bar]", 0.1, 1.5,
                              dinamica.DP_DB / 1e5, 0.1)
        evento = st.checkbox("Evento de pico de demanda", value=True)
        fator_ev = st.slider("Fator do pico (×demanda)", 1.2, 3.0, 2.0, 0.1)

    with st.expander("Secagem PSA — ciclo de torres (aba 3)"):
        topologia_psa = st.radio(
            "Topologia do secador PSA",
            ["N vasos por compressor", "N vasos para o sistema"],
            help="Por compressor: cada uma das unidades em paralelo tem seu "
                 "próprio secador dedicado (rodízio idêntico em cada uma). "
                 "Para o sistema: um único banco de N torres compartilhado, "
                 "dimensionado para a vazão total da planta.")
        n_vasos_psa = st.number_input(
            "Torres em rodízio N (assumido — mínimo do princípio PSA)",
            2, 6, 2, 1)
        t_ads_psa = st.slider(
            "Duração da adsorção por torre [min] (assumido)",
            2.0, 20.0, 6.0, 0.5)
        t_regen_psa = st.slider(
            "Duração da regeneração por torre [min] (assumido)",
            1.0, 15.0, 4.0, 0.5)
        t_resfriamento_psa = st.slider(
            "Resfriamento pós-regeneração [min] (assumido)",
            0.0, 10.0, 2.0, 0.5,
            help="Tempo em que a torre já regenerou mas ainda está quente "
                 "demais para voltar a adsorver com eficiência — sem essa "
                 "fase o rodízio simularia uma troca instantânea entre "
                 "regeneração e adsorção que não existe fisicamente.")
        k_ads_psa = st.slider(
            "Constante de taxa de adsorção k_ads (Eq. 15.1, Fig. 15.2)",
            0.3, 4.0, 1.5, 0.1)
        t_res_psa = st.slider(
            "Tempo de residência de projeto do leito [min] (assumido)",
            1.0, 15.0, 4.0, 0.5)
        horizonte_psa = st.slider("Horizonte de simulação PSA [min]", 10, 120, 30)
        st.caption("Saúde do dessecante (Eq. 15.7) — valores medidos/simulados:")
        dp_real_psa_mbar = st.slider(
            "ΔP real do leito [mbar] (medido)", 15.0, 90.0,
            defaults["dp_real_psa"] / 100.0, 1.0)
        pdp_real_psa_c = st.slider(
            "PDP real [°C] (medido)", -45.0, 10.0,
            float(defaults["pdp_real_c"]), 1.0)

params = {
    **defaults,
    "t_amb": t_amb_c + 273.15,
    "ur_amb": ur_amb,
    "p_amb": p_amb_bar * 1e5,
    "pi_total": pi_total,
    "fad_m3_min": fad,
    "n_compressores": n_compressores,
    "n": n_pol,
    "v_i": v_i,
    "eta_mec": eta_mec,
    "folga_rel": folga_rel,
    "m_carcaca": m_carcaca,
    "c_carcaca": c_carcaca,
    "cond_ext_carcaca": cond_ext_carcaca,
    "cond_arref_carcaca": cond_arref_carcaca,
    "hood_enclausurado": hood_enclausurado,
    "s_motor": s_motor,
    "p_fixas_motor": p_fixas_motor,
    "m_dot_vent": m_dot_vent,
    "p_loss_hood_outros": p_loss_hood_outros,
    "f_d_linha": f_d_linha,
    "l_linha": l_linha,
    "d_linha": d_linha,
    "t_agua": t_agua_c + 273.15,
    "ua_projeto": ua,
    "r_f_equiv": r_f,
    "eta_sep": eta_sep,
    "fator_purga": purga_pct / 100.0,
    "v_vaso": v_vaso,
    "demanda_m3_min": demanda,
    "p_limite": p_limite_bar * 1e5,
    "dp_real_psa": dp_real_psa_mbar * 100.0,
    "pdp_real_c": pdp_real_psa_c,
}

res = simular(params)
k = res["kpis"]
pw = res["potencias"]

for aviso in res["avisos"]:
    st.warning(aviso)

tab_est, tab_din, tab_psa = st.tabs(
    ["⚙️ Operação estática", "📈 Dinâmica temporal", "🌀 Secagem PSA"])

# ===========================================================================
# Aba 1 — Operação estática
# ===========================================================================
with tab_est:
    st.subheader("Indicadores principais (por unidade)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Potência por unidade", f"{pw['w_total'] / 1000:.1f} kW")
    c2.metric("SPC (Eq. 11.11)", f"{k['spc']:.2f} kW·min/m³")
    c3.metric("η global (Eqs. 5.12/5.13)", f"{k['eta_global'] * 100:.1f} %")
    c4.metric("Descarga HP", f"{k['t_descarga_hp_c']:.0f} °C")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Condensado (1 unidade)", f"{k['condensado_total_kg_h']:.1f} kg/h")
    c6.metric("Purga do secador", f"{k['purga_pct']:.0f} %")
    c7.metric("P intermediária", f"{k['p_intermediaria_bar']:.2f} bar abs")
    c8.metric("Autonomia do vaso",
              f"{k['autonomia_min']:.1f} min" if np.isfinite(k["autonomia_min"])
              else "∞ (sem demanda)")

    st.subheader(f"Planta — {pw['n_compressores']} compressor"
                 f"{'es' if pw['n_compressores'] != 1 else ''} em paralelo")
    p1, p2, p3 = st.columns(3)
    p1.metric("Potência total da planta", f"{pw['w_total_planta'] / 1000:.1f} kW")
    p2.metric("Capacidade total instalada (FAD)",
             f"{k['fad_total_m3_min']:.1f} m³/min")
    p3.metric("Condensado total da planta",
             f"{k['condensado_total_planta_kg_h']:.1f} kg/h")

    st.subheader("Pontos de estado ao longo do trem (uma unidade representativa)")
    st.dataframe(
        [{"Ponto": no["nome"], "P [bar abs]": round(no["p_bar"], 3),
          "T [°C]": round(no["t_c"], 1),
          "PDP [°C]": round(no["pdp_c"], 2),
          "ṁ ar seco [kg/s]": round(no["m_dot"], 4),
          "ṁ total (ar+água) [kg/s]": round(no["m_dot_total"], 4),
          "W [kg/kg]": round(no["w"], 6)} for no in res["nos"]],
        width="stretch", hide_index=True,
    )
    st.caption(
        "PDP (ponto de orvalho sob pressão, Eqs. 10.6+10.7) é a mesma "
        "leitura que um sensor T_dp reportaria em cada ponto — sobe com a "
        "compressão (mesmo W, mais concentrado sob maior pressão) e cai de "
        "volta à própria temperatura nos pontos saturados pelos "
        "trocadores (intercooler, aftercooler). ṁ ar seco é invariante à "
        "condensação (convenção padrão de psicrometria — só a água muda de "
        "fase); ṁ total é quem realmente cai a cada ponto de condensação e "
        "de novo, por outro motivo (purga), no secador PSA. Estes valores "
        "valem igualmente para cada um dos "
        f"{pw['n_compressores']} compressores em paralelo — todos operam "
        "no mesmo ponto por serem modelados como idênticos (ver "
        "\"Planta\" acima)."
    )

    g1, g2 = st.columns(2)

    with g1:
        st.subheader("Perfil de pressão, temperatura e ponto de orvalho no trem")
        nomes = [no["nome"].replace(" (pós-intercooler)", "\n(pós-intercooler)")
                 .replace(" (pós-filtro)", "\n(pós-filtro)")
                 .replace(" (pós-secador)", "\n(pós-secador)")
                 for no in res["nos"]]
        x = np.arange(len(nomes))
        press = [no["p_bar"] for no in res["nos"]]
        temps = [no["t_c"] for no in res["nos"]]
        pdps = [no["pdp_c"] for no in res["nos"]]

        fig, ax1 = plt.subplots(figsize=(6.2, 3.6))
        ax1.plot(x, press, "o-", color=BLUE, label="Pressão [bar abs]")
        ax1.set_ylabel("Pressão [bar abs]", color=BLUE)
        ax1.tick_params(axis="y", labelcolor=BLUE)
        ax2 = ax1.twinx()
        ax2.plot(x, temps, "s--", color=RED, label="Temperatura [°C]")
        ax2.plot(x, pdps, "^:", color=GREEN, label="PDP [°C]")
        ax2.set_ylabel("Temperatura / PDP [°C]", color=RED)
        ax2.tick_params(axis="y", labelcolor=RED)
        ax2.grid(False)
        linhas = ax1.get_lines() + ax2.get_lines()
        ax2.legend(linhas, [l.get_label() for l in linhas],
                  fontsize=7, loc="upper right")
        ax1.set_xticks(x)
        ax1.set_xticklabels(nomes, fontsize=7, rotation=20, ha="right")
        fig.tight_layout()
        st.pyplot(fig)
        st.caption(
            "A distância vertical entre a linha de Temperatura (vermelha) "
            "e a de PDP (verde) é a margem até o ar começar a condensar "
            "naquele ponto — onde as duas se tocam, o ar está saturado "
            "(100% UR), como acontece por construção logo após o "
            "intercooler e o aftercooler."
        )

    with g2:
        st.subheader("Curva em “V” — perdas V_i (Eqs. 5.8/5.9)")
        p0 = params["p_amb"]
        v_dot = params["fad_m3_min"] / 60.0
        pi_i = nucleo.razao_pressao_interna(params["v_i"], params["n"])
        pi_arr = np.linspace(0.5 * pi_i, 1.8 * pi_i, 200)
        perdas = [nucleo.perda_vi(p0, v_dot / pi, pi, params["v_i"], params["n"])
                  / 1000.0 for pi in pi_arr]
        pi_op = np.sqrt(params["pi_total"])
        perda_op = nucleo.perda_vi(p0, v_dot / pi_op, pi_op, params["v_i"],
                                   params["n"]) / 1000.0

        fig2, ax = plt.subplots(figsize=(6.2, 3.6))
        ax.plot(pi_arr, perdas, color=NAVY, label="Perda V_i (estágio)")
        ax.axvline(pi_i, color=GREEN, ls=":", label=f"π_i = {pi_i:.2f}")
        ax.plot([pi_op], [perda_op], "o", color=RED,
                label=f"Ponto operante (π = {pi_op:.2f})")
        ax.set_xlabel("Razão de pressão operante π do estágio")
        ax.set_ylabel("Perda [kW]")
        ax.legend(fontsize=8)
        fig2.tight_layout()
        st.pyplot(fig2)

    st.subheader("Sensibilidade — potência × pressão de setpoint (Eq. 13.9)")
    pi_range = np.arange(5.0, 12.01, 0.25)
    potencias = []
    for pi_r in pi_range:
        r = simular({**params, "pi_total": float(pi_r)})
        potencias.append(r["potencias"]["w_total"] / 1000.0)

    fig3, ax3 = plt.subplots(figsize=(6.2, 3.2))
    ax3.plot(pi_range, potencias, color=BLUE)
    w_ref = pw["w_total"] / 1000.0
    ax3.plot([pi_total], [w_ref], "o", color=RED, label="Ponto operante")
    ax3.set_xlabel("Pressão de rede [bar abs]")
    ax3.set_ylabel("Potência por unidade [kW]")
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    st.pyplot(fig3)
    delta_1bar = (np.interp(pi_total + 1.0, pi_range, potencias) - w_ref)
    st.caption(
        f"Reduzir o setpoint em 1 bar economiza ≈ {delta_1bar:.1f} kW "
        f"({delta_1bar / w_ref * 100:.1f} % da potência atual) — cf. “regra "
        f"dos 7 %/bar” (:1746)."
    )

    st.subheader("Motor (Eqs. 4.10-4.12) e invólucro/Hood (Eqs. 2.1, 2.4)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("η_mot", f"{k['eta_mot'] * 100:.1f} %")
    m2.metric("Perdas do motor", f"{k['p_perdas_mot_w']:.0f} W")
    m3.metric("Q̇_gerado no invólucro", f"{k['q_gerado_hood_w']:.0f} W")
    m4.metric("T_hood (regime permanente)", f"{k['t_hood_c']:.1f} °C")
    st.caption(
        "η_mot fecha via Eq. 4.12, com P_ag (Eq. 4.10) obtido da potência "
        "de eixo já calculada pela cascata — simplificação que evita "
        "reconstruir o circuito equivalente completo (Eqs. 4.4/4.5), sem "
        "parâmetros de placa neste app. Q̇_gerado (Eq. 2.1) soma as perdas "
        "do motor, do VSD+gearbox (não decompostas aqui — ver ASSUMIDO na "
        "barra lateral) e da própria carcaça; T_hood (Eq. 2.4) fecha a "
        "temperatura de regime do ar confinado a partir da vazão de "
        "ventilação forçada."
    )

    st.subheader("Carcaça do estágio LP — balanço térmico (Eq. 9.6)")
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Q̇_int conduzido à carcaça", f"{k['q_int_carcaca_w']:.0f} W")
    h2.metric("T_referência (Eq. 9.16)",
             f"{k['t_ref_carcaca_c']:.1f} °C",
             help="T_hood se enclausurado (Eq. 2.4), T_amb se a céu aberto — "
                  "ver caixa de seleção na barra lateral.")
    h3.metric("T_carcaça (regime permanente)", f"{k['t_carcaca_c']:.1f} °C")
    h4.metric("Constante de tempo τ_c", f"{k['tau_carcaca_min']:.0f} min")
    st.caption(
        "Regime permanente da Eq. 9.6 (dT_c/dt = 0): Q_int (proxy — perda "
        "mecânica do estágio LP, W_LP·(1−η_mec)) se equilibra com Q_ext + "
        "Q_arref, modelados como condutâncias lineares (Newton) para a "
        "temperatura de referência acima. τ_c indica quão rápido a "
        "carcaça responde a uma mudança de carga — não é um transiente "
        "calculado ao longo do tempo nesta aba (só o valor de regime), "
        "diferente da rampa do VSD na aba \"Dinâmica temporal\". A Eq. 9.7 "
        "(folga residual por dilatação térmica) não está implementada — "
        "exigiria um modelo à parte para a temperatura do rotor, não "
        "fechado pelo livro."
    )

    st.subheader("Tubulação interestágios (Eq. 5.15)")
    l1, l2 = st.columns(2)
    l1.metric("ΔP_linha (LP→HP)", f"{k['dp_linha_mbar']:.2f} mbar")
    l2.metric("P sucção HP efetiva", f"{k['p_hp_suc_efetiva_bar']:.3f} bar abs",
             help="P_intermediária menos ΔP_linha — diagnóstico; o restante "
                  "da cascata ainda usa P_intermediária como sucção do "
                  "estágio HP (simplificação já registrada no livro).")
    st.caption(
        "Correção de pressão por atrito distribuído na linha (Darcy-"
        "Weisbach), separada da perda localizada do filtro/silenciador "
        "(Eq. 5.4). Pequena em linha nova e bem dimensionada — tende a "
        "crescer com corrosão/incrustação interna ao longo da vida da "
        "instalação (f_D sobe), e vale acompanhar como sintoma."
    )

    with st.expander("Balanço de potência e calor"):
        st.write({
            "W_LP [kW]": round(pw["w_lp"] / 1000, 2),
            "W_HP [kW]": round(pw["w_hp"] / 1000, 2),
            "Perda V_i LP [kW]": round(pw["perda_vi_lp"] / 1000, 2),
            "Perda V_i HP [kW]": round(pw["perda_vi_hp"] / 1000, 2),
            "Aquecedor de regeneração [kW]": round(pw["aquecedor"] / 1000, 2),
            "Q̇ intercooler [kW]": round(pw["q_intercooler"] / 1000, 2),
            "Q̇ aftercooler [kW]": round(pw["q_aftercooler"] / 1000, 2),
            "W isotérmico (referência) [kW]":
                round(pw["w_isotermico"] / 1000, 2),
        })

# ===========================================================================
# Aba 2 — Dinâmica temporal
# ===========================================================================
with tab_din:
    # capacidade pós-secador da PLANTA (soma das n_compressores unidades) [kg/s]
    m_dot_cap = res["nos"][-1]["m_dot"] * pw["n_compressores"]
    rho_amb = nucleo.densidade_ar(params["p_amb"], params["t_amb"])
    dem_base = rho_amb * demanda / 60.0          # kg/s
    hor_s = horizonte * 60.0
    t_ev = (0.40 * hor_s, 0.65 * hor_s) if evento else (float("inf"),) * 2

    din = dinamica.simular_transiente(
        horizonte_min=horizonte,
        m_dot_cap=m_dot_cap,
        w_nom=pw["w_total_planta"],
        v_vaso=params["v_vaso"],
        t_k=params["t_amb"],
        p_set=params["p_amb"] * params["pi_total"],
        p_limite=params["p_limite"],
        dem_base=dem_base,
        t_ev=t_ev,
        fator_ev=fator_ev,
        modo=modo,
        dp_db=dp_db_bar * 1e5,
        tau_vsd=tau_vsd,
    )
    kd = din["kpis"]

    st.subheader(f"Transiente da rede — controle {kd['modo']}")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Energia no horizonte", f"{kd['energia_kwh']:.1f} kWh")
    d2.metric("Pressão mín./máx.",
              f"{kd['p_min_bar']:.2f} / {kd['p_max_bar']:.2f} bar")
    d3.metric("Tempo abaixo do limite", f"{kd['t_abaixo_limite_min']:.1f} min")
    if modo == "Carga/Alívio":
        d4.metric("Ciclos carga/alívio", f"{kd['n_ciclos']} "
                  f"(teórico: {kd['f_ciclo_teorica_min']:.1f}/min, Eq. 13.8)")
    else:
        d4.metric("Ciclos carga/alívio", "— (VSD)")

    if kd["t_abaixo_limite_min"] > 0:
        st.error("A rede ficou abaixo da pressão mínima de instrumentação — "
                 "capacidade insuficiente durante o evento.")

    e1, e2 = st.columns(2)

    with e1:
        fig4, ax4 = plt.subplots(figsize=(6.2, 3.4))
        ax4.plot(din["t_min"], din["p_bar"], color=NAVY, label="P da rede")
        p_set_bar = params["pi_total"] * params["p_amb"] / 1e5
        if modo == "Carga/Alívio":
            ax4.axhline(p_set_bar + dp_db_bar / 2, color=GREEN, ls=":",
                        label="Banda carga/alívio")
            ax4.axhline(p_set_bar - dp_db_bar / 2, color=GREEN, ls=":")
        else:
            ax4.axhline(p_set_bar, color=GREEN, ls=":", label="Setpoint")
        ax4.axhline(params["p_limite"] / 1e5, color=RED, ls="--",
                    label="P mínima da rede")
        ax4.set_xlabel("Tempo [min]")
        ax4.set_ylabel("Pressão [bar abs]")
        ax4.legend(fontsize=8)
        fig4.tight_layout()
        st.pyplot(fig4)

        fig6, ax6 = plt.subplots(figsize=(6.2, 3.0))
        ax6.plot(din["t_min"], din["w_kw"], color=BLUE)
        ax6.set_xlabel("Tempo [min]")
        ax6.set_ylabel("Potência [kW]")
        ax6.set_title("Potência instantânea (Eq. 13.7)", fontsize=10)
        fig6.tight_layout()
        st.pyplot(fig6)

    with e2:
        fig5, ax5 = plt.subplots(figsize=(6.2, 3.4))
        ax5.plot(din["t_min"], din["m_comp"], color=BLUE,
                 label="ṁ compressor (pós-secador)")
        ax5.plot(din["t_min"], din["m_dem"], color=RED, ls="--",
                 label="ṁ demanda")
        ax5.set_xlabel("Tempo [min]")
        ax5.set_ylabel("Vazão mássica [kg/s]")
        ax5.legend(fontsize=8)
        fig5.tight_layout()
        st.pyplot(fig5)

        fig7, ax7 = plt.subplots(figsize=(6.2, 3.0))
        energia_t = np.concatenate(
            [[0.0], np.cumsum(np.diff(din["t_min"]) *
                              (din["w_kw"][1:] + din["w_kw"][:-1]) / 2.0 / 60.0)])
        ax7.plot(din["t_min"], energia_t, color=GREEN)
        ax7.set_xlabel("Tempo [min]")
        ax7.set_ylabel("Energia acumulada [kWh]")
        fig7.tight_layout()
        st.pyplot(fig7)

    if evento:
        st.caption(
            f"Evento de pico: demanda ×{fator_ev:.1f} entre "
            f"{0.40 * horizonte:.0f} min e {0.65 * horizonte:.0f} min. "
            "Balanço de massa no vaso: Eq. 16.4; modulação de potência: "
            "Eq. 13.7; ciclagem teórica: Eq. 13.8."
        )

# ===========================================================================
# Aba 3 — Secagem PSA (ciclo de torres)
# ===========================================================================
with tab_psa:
    m_dot_unidade = res["nos"][-1]["m_dot"]  # vazão pós-secador de UMA unidade
    if topologia_psa == "N vasos por compressor":
        m_dot_psa = m_dot_unidade
        legenda_topologia = (
            f"cada um dos {pw['n_compressores']} compressores tem seu próprio "
            f"secador dedicado de {n_vasos_psa} torres — o gráfico abaixo é "
            f"idêntico em todas as unidades (mesmo ponto de operação)."
        )
    else:
        m_dot_psa = m_dot_unidade * pw["n_compressores"]
        legenda_topologia = (
            f"um único banco de {n_vasos_psa} torres compartilhado, "
            f"dimensionado para a vazão total da planta "
            f"({pw['n_compressores']} compressores somados)."
        )

    p_low_psa = params["p_amb"]
    p_high_psa = params["p_amb"] * params["pi_total"]

    r_psa = psa_ciclo.simular_ciclo_psa(
        horizonte_min=horizonte_psa,
        m_dot_ar=m_dot_psa,
        t_ads_min=t_ads_psa,
        t_regen_min=t_regen_psa,
        t_resfriamento_min=t_resfriamento_psa,
        n_vasos=n_vasos_psa,
        k_ads=k_ads_psa,
        t_res_min=t_res_psa,
        p_low=p_low_psa,
        p_high=p_high_psa,
        fator_purga=params["fator_purga"],
    )
    kp = r_psa["kpis"]

    st.subheader(f"Rodízio de {n_vasos_psa} torres — {topologia_psa.lower()}")
    st.caption(
        f"Topologia escolhida: {legenda_topologia} Ciclo por torre: "
        f"{kp['t_ciclo_min']:.1f} min (adsorção + regeneração + resfriamento)."
    )

    if kp["tempo_sem_secagem_min"] > 0:
        st.error(
            f"Cobertura de secagem **interrompida** por "
            f"{kp['tempo_sem_secagem_min']:.1f} min no horizonte simulado — "
            f"em alguns instantes nenhuma das {n_vasos_psa} torres está "
            "disponível para adsorver (todas regenerando/resfriando ao "
            "mesmo tempo). Ar não tratado passaria direto. Aumente N de "
            "torres, reduza o resfriamento/regeneração, ou aumente a "
            "duração da adsorção."
        )
    if kp["q_min"] < 0.05:
        st.warning(
            f"Capacidade mínima do leito caiu para {kp['q_min']*100:.1f}% de "
            "q_eq ao fim da adsorção — próximo do esgotamento (risco de "
            "*breakthrough*, ver Tabela 15.1). Considere ciclo mais curto ou "
            "mais torres em rodízio."
        )

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Trocas no horizonte", f"{kp['n_trocas']}")
    d2.metric("Capacidade mín. do leito (fim da adsorção)",
             f"{kp['q_min'] * 100:.1f}% de q_eq")
    d3.metric("Purga de regeneração (Eq. 15.2)",
             f"{kp['purga_media_kg_s'] * 3600:.1f} kg/h")
    d4.metric("Torres adsorvendo simultaneamente (mín.)",
             f"{kp['n_adsorvendo_min']}")

    st.subheader("Indicadores Globais de Performance (Cap. 15)")
    e1, e2, e3 = st.columns(3)
    e1.metric("SEC_dry (Eq. 15.6)", f"{k['sec_dry_kj_kg']:.1f} kJ/kg",
             help="Só a parcela do aquecedor de regeneração — este app não "
                  "modela o secador de tambor rotativo (HOC) do Cap. 15, "
                  "então Ẇ_drum é sempre 0 aqui.")
    e2.metric("HI_des (Eq. 15.7)", f"{k['hi_des']:.2f}",
             help="1,0 = leito saudável (ΔP e PDP medidos, na barra lateral, "
                  "iguais ao nominal/alvo). Cai conforme ΔP real e PDP real "
                  "se afastam desses valores.")
    e3.metric("η_purge (Eq. 15.9)", f"{k['purga_pct']:.1f} %")
    if k["hi_des"] < 0.7:
        st.warning(
            f"HI_des = {k['hi_des']:.2f} — dessecante degradado (ΔP real "
            "ou PDP real distantes do nominal/alvo definidos na barra "
            "lateral). Ver Tabela 15.1 (Matriz de Diagnóstico de Falhas)."
        )

    st.subheader("Capacidade de adsorção normalizada por torre (Eq. 15.1)")
    fig8, ax8 = plt.subplots(figsize=(9.0, 3.4))
    cores_torres = plt.cm.tab10(np.linspace(0, 1, n_vasos_psa))
    for i in range(n_vasos_psa):
        ax8.plot(r_psa["t_min"], r_psa["q_norm"][i], color=cores_torres[i],
                 label=f"Torre {i + 1}", lw=1.6)
    ax8.set_xlabel("Tempo [min]")
    ax8.set_ylabel(r"$q_d \, / \, q_{eq}$")
    ax8.set_ylim(-0.05, 1.05)
    ax8.legend(fontsize=8, ncol=min(n_vasos_psa, 4))
    fig8.tight_layout()
    st.pyplot(fig8)

    st.subheader("Chaveamento entre torres")
    # 0 = Adsorvendo, 1 = Regenerando, 2 = Resfriando
    mapa_estado = {"Adsorvendo": 0, "Regenerando": 1, "Resfriando": 2}
    estado_num = np.vectorize(mapa_estado.get)(r_psa["estado"]).astype(float)
    cmap_estado = matplotlib.colors.ListedColormap([BLUE, RED, "#d9a441"])
    fig9, ax9 = plt.subplots(figsize=(9.0, 0.9 + 0.5 * n_vasos_psa))
    ax9.imshow(
        estado_num, aspect="auto", cmap=cmap_estado, vmin=-0.5, vmax=2.5,
        extent=[r_psa["t_min"][0], r_psa["t_min"][-1], n_vasos_psa - 0.5, -0.5],
    )
    ax9.set_yticks(range(n_vasos_psa))
    ax9.set_yticklabels([f"Torre {i + 1}" for i in range(n_vasos_psa)])
    ax9.set_xlabel("Tempo [min]")
    ax9.set_title("Azul = adsorvendo · Vermelho = regenerando · "
                  "Laranja = resfriando (fora de serviço)", fontsize=9)
    fig9.tight_layout()
    st.pyplot(fig9)

    st.subheader("Vazão de purga de regeneração (Eq. 15.2)")
    fig10, ax10 = plt.subplots(figsize=(9.0, 2.6))
    ax10.plot(r_psa["t_min"], r_psa["m_purge_kg_s"] * 3600.0, color=RED, lw=1.6)
    ax10.set_xlabel("Tempo [min]")
    ax10.set_ylabel("Purga [kg/h]")
    fig10.tight_layout()
    st.pyplot(fig10)
    st.caption(
        "Com rodízio contínuo (sempre exatamente 1 torre regenerando), a "
        "purga é aproximadamente constante — uma queda para zero ou um pico "
        "acima desse patamar sinalizaria falha de chaveamento (ver "
        "Tabela 15.1)."
    )
