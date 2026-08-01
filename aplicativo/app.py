"""App Streamlit — Simulador de Sistema de Ar Comprimido (compressor de parafuso).

Baseado nas equações do livro "Gêmeo Digital de Sistemas de Compressão
Offshore" (compressores.tex). Executar a partir do diretório `aplicativo/`:

    venv/bin/streamlit run app.py

Abas:
- "Operação estática": ponto de operação do trem completo (cascata steady-state);
- "Dinâmica temporal": transiente de pressão da rede com controle VSD ou
  carga/alívio (Eqs. 13.4, 13.7, 13.8, 16.4).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # mesmo backend do scripts/gen_figuras.py

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from compressor_sim import dinamica, nucleo, parametros_default, simular

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
    "t_agua": t_agua_c + 273.15,
    "ua_projeto": ua,
    "r_f_equiv": r_f,
    "eta_sep": eta_sep,
    "fator_purga": purga_pct / 100.0,
    "v_vaso": v_vaso,
    "demanda_m3_min": demanda,
    "p_limite": p_limite_bar * 1e5,
}

res = simular(params)
k = res["kpis"]
pw = res["potencias"]

for aviso in res["avisos"]:
    st.warning(aviso)

tab_est, tab_din = st.tabs(["⚙️ Operação estática", "📈 Dinâmica temporal"])

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
          "T [°C]": round(no["t_c"], 1), "ṁ [kg/s]": round(no["m_dot"], 4),
          "W [kg/kg]": round(no["w"], 6)} for no in res["nos"]],
        width="stretch", hide_index=True,
    )

    g1, g2 = st.columns(2)

    with g1:
        st.subheader("Perfil de pressão e temperatura no trem")
        nomes = [no["nome"].replace(" (pós-intercooler)", "\n(pós-intercooler)")
                 .replace(" (pós-filtro)", "\n(pós-filtro)")
                 .replace(" (pós-secador)", "\n(pós-secador)")
                 for no in res["nos"]]
        x = np.arange(len(nomes))
        press = [no["p_bar"] for no in res["nos"]]
        temps = [no["t_c"] for no in res["nos"]]

        fig, ax1 = plt.subplots(figsize=(6.2, 3.6))
        ax1.plot(x, press, "o-", color=BLUE, label="Pressão [bar abs]")
        ax1.set_ylabel("Pressão [bar abs]", color=BLUE)
        ax1.tick_params(axis="y", labelcolor=BLUE)
        ax2 = ax1.twinx()
        ax2.plot(x, temps, "s--", color=RED, label="Temperatura [°C]")
        ax2.set_ylabel("Temperatura [°C]", color=RED)
        ax2.tick_params(axis="y", labelcolor=RED)
        ax2.grid(False)
        ax1.set_xticks(x)
        ax1.set_xticklabels(nomes, fontsize=7, rotation=20, ha="right")
        fig.tight_layout()
        st.pyplot(fig)

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
