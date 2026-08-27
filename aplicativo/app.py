"""App Streamlit — Simulador Digital Twin e Treinamento de Falhas com Dados PI.

Desenvolvido para compressores de parafuso industriais em unidades offshore (FPSOs e plataformas).
Baseado nas equações e diretrizes do livro:
"Enciclopédia de Máquinas Rotodinâmicas — Volume II: Gêmeo Digital de Sistemas de Compressão Offshore"

Executar a partir do diretório `aplicativo/`:
    venv/bin/streamlit run app.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from compressor_sim import (
    calib_lm,
    cenarios_falha,
    constantes,
    dinamica,
    ekf,
    frota_supervisorio,
    mpc,
    nucleo,
    parametros_default,
    pi_telemetry,
    piml,
    psa_ciclo,
    pso,
    simular,
    subsistemas,
    treinamento_falhas,
    vae,
)

# Paleta e estilo industrial
NAVY = "#1f3b57"
BLUE = "#2b6cb0"
RED = "#b73a3a"
GREEN = "#2f7a4f"
ORANGE = "#d97706"
GRAY = "#64748b"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.grid": True,
    "grid.color": "#e2e8f0",
    "axes.facecolor": "white",
    "figure.facecolor": "white",
})

st.set_page_config(
    page_title="Gêmeo Digital & Treinamento PI — Compressor Offshore",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS de Identidade Visual Industrial ──────────────────────────────────────
st.markdown("""
<style>
/* Fonte monoespaçada para valores de telemetria */
.mono { font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; font-size: 0.93em; }

/* Badges de alarme ISA 18.2 */
.badge-normal  { background:#166534; color:#dcfce7; padding:2px 8px; border-radius:12px; font-size:0.78em; font-weight:600; }
.badge-alerta  { background:#92400e; color:#fef3c7; padding:2px 8px; border-radius:12px; font-size:0.78em; font-weight:600; }
.badge-trip    { background:#991b1b; color:#fee2e2; padding:2px 8px; border-radius:12px; font-size:0.78em; font-weight:600; }

/* Card de KPI principal */
.kpi-card { background:#f8fafc; border:1px solid #cbd5e1; border-left:4px solid #2563eb; border-radius:8px; padding:12px 16px; margin-bottom:8px; box-shadow:0 1px 3px rgba(0,0,0,0.05); }
.kpi-label { font-size:0.78em; color:#334155; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; }
.kpi-value { font-size:1.6em; font-weight:800; color:#0f172a; line-height:1.1; }
.kpi-delta-ok  { font-size:0.78em; color:#166534; font-weight:600; }
.kpi-delta-warn{ font-size:0.78em; color:#92400e; font-weight:600; }
.kpi-delta-crit{ font-size:0.78em; color:#991b1b; font-weight:600; }

/* Card de frota — urgência */
.fleet-card         { border-radius:10px; padding:14px 18px; margin-bottom:10px; border:2px solid #cbd5e1; background:#ffffff; box-shadow:0 1px 3px rgba(0,0,0,0.05); }
.fleet-card-ok      { border-color:#166534; background:#f0fdf4; }
.fleet-card-warn    { border-color:#d97706; background:#fffbeb; }
.fleet-card-crit    { border-color:#dc2626; background:#fef2f2; }

/* Reforço de contraste em formulários e configurações */
div[data-testid="stExpander"] {
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
    background-color: #ffffff !important;
}
div[data-testid="stExpander"] summary {
    font-weight: 700 !important;
    color: #0f172a !important;
}
label[data-testid="stWidgetLabel"] {
    color: #1e293b !important;
    font-weight: 600 !important;
}

/* Separador de fase do treinamento */
.fase-header { background:linear-gradient(90deg,#1f3b57,#2b6cb0); color:white; padding:8px 16px;
               border-radius:6px; font-weight:700; font-size:1.02em; margin:12px 0 8px 0; }

/* Barra de progresso personalizada */
.progress-bar-outer { background:#e2e8f0; border-radius:6px; height:14px; overflow:hidden; }
.progress-bar-inner { height:100%; border-radius:6px; transition:width 0.3s; }
</style>
""", unsafe_allow_html=True)

# ── Cabeçalho Principal ───────────────────────────────────────────────────────
col_hdr, col_status = st.columns([4, 1])
with col_hdr:
    st.title("🌀 Gêmeo Digital & Treinamento de Falhas")
    st.caption(
        "Simulação Física de Alta Fidelidade · Telemetria OSIsoft PI System · "
        "Arena Operacional de Diagnóstico · **API 619 · ISO 1217 · ISO 8573-1 · ASME VIII**"
    )
with col_status:
    from datetime import datetime as _dt
    st.markdown(f"<div style='text-align:right;color:#64748b;font-size:0.8em;margin-top:18px;'>"
                f"🕐 {_dt.now().strftime('%d/%m/%Y  %H:%M:%S')}<br>"
                f"<b style='color:#166534;'>● Sistema Operacional</b></div>", unsafe_allow_html=True)

defaults = parametros_default()

# ---------------------------------------------------------------------------
# Inicialização de variáveis no session_state
# ---------------------------------------------------------------------------
if "caso_treinamento" not in st.session_state:
    st.session_state["caso_treinamento"] = None
if "resultado_avaliacao" not in st.session_state:
    st.session_state["resultado_avaliacao"] = None
if "historico_treinamento" not in st.session_state:
    st.session_state["historico_treinamento"] = []
if "frota_instancias" not in st.session_state:
    st.session_state["frota_instancias"] = frota_supervisorio.criar_frota_padrao_offshore(n_maquinas=4)
if "telemetria_pi_live" not in st.session_state:
    st.session_state["telemetria_pi_live"] = None

# ---------------------------------------------------------------------------
# Estrutura de Abas do Aplicativo — 5 abas operacionais + Treinamento na sidebar
# ---------------------------------------------------------------------------
(
    tab_frota,
    tab_dashboard,
    tab_diagnostico,
    tab_sistema,
    tab_config,
) = st.tabs([
    "🚢 Supervisório de Frota",
    "📊 Dashboard do Ativo",
    "🔬 Diagnóstico & IA",
    "🛠️ Sistema & Dinâmica",
    "⚙️ Configurações",
])

# Modo Treinamento — controlado via sidebar
if "modo_treinamento" not in st.session_state:
    st.session_state["modo_treinamento"] = False



# ---------------------------------------------------------------------------
# 1. ABA: Configurações & Parâmetros Físicos (Renderizada cedo para alimentar params)
# ---------------------------------------------------------------------------
with tab_config:
    st.subheader("Parâmetros Construtivos, Geométricos e Hiperparâmetros")
    st.caption(
        "Configurações que descrevem a física do equipamento e algoritmos da Parte II. "
        "Para as condições operacionais instantâneas, utilize a barra lateral."
    )

    cfg1, cfg2 = st.columns(2)

    with cfg1:
        with st.expander("Compressor — Geometria e Eficiência (Caps. 3, 5 e 9)", expanded=True):
            fad = st.number_input(
                "Vazão FAD por unidade [m³/min] (ISO 1217)",
                1.0, 100.0, defaults["fad_m3_min"], 0.5
            )
            n_compressores = st.number_input(
                "Compressores em paralelo na planta (N_frota)",
                1, 10, defaults["n_compressores"], 1
            )
            n_pol = st.slider("Índice politrópico n (Eq. 5.5 / Eq. 9.5)", 1.20, 1.40, defaults["n"], 0.01)
            v_i = st.slider("Razão volumétrica interna V_i (Eq. 5.6)", 2.0, 7.0, defaults["v_i"], 0.1)
            eta_mec = st.slider("Eficiência mecânica η_mec", 0.80, 1.00, defaults["eta_mec"], 0.005)

        with st.expander("Carcaça e Rotores — Balanço Térmico e Folgas (Eqs. 9.6, 9.7, 9.16)"):
            m_carcaca = st.number_input("Massa térmica da carcaça M_c [kg]", 50.0, 2000.0, defaults["m_carcaca"], 10.0)
            c_carcaca = st.number_input("Calor específico c_c [J/(kg·K)]", 300.0, 900.0, defaults["c_carcaca"], 10.0)
            cond_ext_carcaca = st.number_input("Condutância de convecção externa [W/K]", 1.0, 200.0, defaults["cond_ext_carcaca"], 1.0)
            cond_arref_carcaca = st.number_input("Condutância do arrefecimento forçado [W/K]", 1.0, 500.0, defaults["cond_arref_carcaca"], 1.0)
            delta_nom_um = st.number_input("Folga nominal a frio δ_nom [μm]", 50.0, 500.0, defaults["delta_nom_um"], 10.0)

        with st.expander("Motor Elétrico e Invólucro Acústico (Hood) (Eqs. 2.1, 2.4, 4.10-4.12)"):
            hood_enclausurado = st.checkbox("Compressor dentro de invólucro acústico (Hood)?", value=defaults["hood_enclausurado"])
            s_motor = st.slider("Escorregamento nominal s (Eq. 4.4)", 0.005, 0.08, defaults["s_motor"], 0.005, format="%.3f")
            p_fixas_motor = st.number_input("Perdas fixas do motor P_fixas [W] (IEC 60034-2-1)", 200.0, 10000.0, defaults["p_fixas_motor"], 100.0)
            m_dot_vent = st.number_input("Vazão de ventilação forçada do exaustor [kg/s]", 0.05, 5.0, defaults["m_dot_vent"], 0.05)
            p_loss_hood_outros = st.number_input("Perdas de VSD + Gearbox no Hood [W]", 0.0, 10000.0, defaults["p_loss_hood_outros"], 100.0)

    with cfg2:
        with st.expander("Tratamento de Ar, Resfriadores e Secador PSA (Caps. 10, 14 e 15)", expanded=True):
            ua = st.number_input("Condutância térmica global de projeto UA [W/K]", 500.0, 20000.0, defaults["ua_projeto"], 100.0)
            eta_sep = st.slider("Eficiência do separador ciclônico η_sep (Eq. 14.4)", 0.80, 1.00, defaults["eta_sep"], 0.01)
            material_psa = st.selectbox("Material dessecante PSA (Tabela 15.1)", list(constantes.MATERIAIS_DESSECANTE.keys()))
            massa_leito_psa = st.number_input("Massa do leito por torre [kg]", 10.0, 5000.0, constantes.MASSA_LEITO_PSA_DEFAULT_KG, 10.0)
            purga_pct = st.slider("Fração de ar de purga PSA [%] (Eq. 15.2)", 5, 25, int(defaults["fator_purga"] * 100))
            eps_recup_psa = st.slider("Efetividade de recuperação de calor residual ε (Eq. 15.10)", 0.0, 1.0, constantes.EPSILON_RECUP_PSA_DEFAULT, 0.05)

        with st.expander("Vaso Pulmão e Rede de Distribuição (Caps. 13 e 16)"):
            v_vaso = st.number_input("Volume do vaso pulmão V_tk [m³]", 0.5, 20.0, defaults["v_vaso"], 0.5)
            p_limite_bar = st.number_input("Pressão mínima crítica da rede P_crit [bar abs]", 3.0, 8.0, defaults["p_limite"] / 1e5, 0.1)
            dp_db_bar = st.slider("Banda morta carga/alívio ΔP_db [bar] (Eq. 13.8)", 0.1, 1.5, dinamica.DP_DB / 1e5, 0.1)

        with st.expander("Hiperparâmetros de Inteligência Artificial (EKF / VAE / PIML / MPC / PSO)"):
            n_passos_ekf = st.slider("Passos de varredura EKF", 20, 500, 60, 10)
            dt_horas_ekf = st.number_input("Intervalo Δt EKF [horas]", 0.1, 24.0, 1.0, 0.1)
            n_amostras_vae = st.slider("Amostras para treino do VAE", 50, 1000, 200, 50)
            n_epocas_vae = st.slider("Épocas de treino do VAE", 10, 100, 30, 5)
            n_amostras_piml = st.slider("Amostras de treino PIML", 50, 500, 100, 25)
            n_epocas_piml = st.slider("Épocas PIML", 10, 100, 30, 5)
            n_particulas_pso = st.slider("Partículas do PSO", 10, 60, 20, 5)
            n_iter_pso = st.slider("Iterações do PSO", 10, 50, 20, 5)


# ---------------------------------------------------------------------------
# Barra Lateral: Seletor de Ativo + Condições Operacionais
# ---------------------------------------------------------------------------
with st.sidebar:
    # Seletor de Ativo Principal
    st.markdown("### 🔧 Ativo em Análise")
    ativos_disponiveis = ["CMP-01", "CMP-02", "CMP-03", "CMP-04"]
    ativo_sel = st.selectbox(
        "Selecionar compressor",
        ativos_disponiveis,
        index=st.session_state.get("ativo_idx", 0),
        label_visibility="collapsed",
    )
    # Atualiza idx se o usuário mudar manualmente no selectbox
    st.session_state["ativo_idx"] = ativos_disponiveis.index(ativo_sel)

    # Status rápido do ativo selecionado
    painel_atual = st.session_state.get("painel_frota")
    if painel_atual:
        ativo_data = next((m for m in painel_atual if m["maquina_id"] == ativo_sel), None)
        if ativo_data:
            hi_v = ativo_data["hi"] * 100
            hi_cor = "#166534" if hi_v >= 85 else ("#92400e" if hi_v >= 60 else "#991b1b")
            st.markdown(
                f"<div style='background:#1e293b;border-radius:8px;padding:8px 12px;margin-bottom:8px;'>"
                f"<span style='color:#94a3b8;font-size:0.75em;'>Health Index</span><br>"
                f"<span style='font-size:1.4em;font-weight:700;color:{hi_cor};'>{hi_v:.1f}%</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Botão Modo Treinamento
    modo_btn_label = "🎓 Sair do Treinamento" if st.session_state["modo_treinamento"] else "🎓 Entrar no Modo Treinamento"
    if st.button(modo_btn_label, use_container_width=True):
        st.session_state["modo_treinamento"] = not st.session_state["modo_treinamento"]
        st.rerun()

    st.markdown("---")
    st.markdown("**⚙️ Ponto de Operação**")
    st.markdown("*Ambiente Offshore (Plataforma/FPSO)*")

    t_amb_c = st.slider("Temperatura Ambiente T_amb [°C]", 5.0, 45.0, 30.0, 0.5)
    ur_amb_pct = st.slider("Umidade Relativa do Ar [%]", 20, 100, 80, 5)
    p_amb_mbar = st.number_input("Pressão Atmosférica [mbar abs]", 950.0, 1050.0, 1013.25, 5.0)

    st.markdown("---")
    st.markdown("**Geração e Compressão**")
    pi_rede = st.slider("Razão de Pressão Global π = P2/P1 (Eq. 5.14)", 5.0, 11.0, 8.0, 0.1)
    f_vsd = st.slider("Frequência de Alimentação VSD [Hz]", 25.0, 70.0, 60.0, 1.0)
    demanda_m3_min = st.slider("Demanda de Ar da Planta [m³/min]", 1.0, float(fad * n_compressores), 8.0, 0.5)
    t_agua_c = st.slider("Temp. Água de Resfriamento T_w,in [°C]", 10.0, 40.0, 25.0, 0.5)

    st.markdown("---")
    st.markdown("**Estado do Gêmeo Digital (Estados Ocultos)**")
    folga_rel_input = st.slider("Folga Relativa LP δ/L [μm/m] (Eq. 9.3)", 0.001, 0.025, 0.002, 0.001, format="%.4f")
    rf_fouling_input = st.slider("Resistência Fouling Intercooler R_f [m²K/W]", 0.0, 0.002, 0.0, 0.0001, format="%.4f")

    zeta_filtro_input = st.slider("Perda de Carga do Filtro ζ (Eq. 5.4)", 1.0, 15.0, 2.5, 0.5)

# Montagem do dicionário de parâmetros completo
params = {
    "t_amb": t_amb_c + 273.15,
    "ur_amb": ur_amb_pct / 100.0,
    "p_amb": p_amb_mbar * 100.0,
    "pi_total": pi_rede,
    "f_vsd": f_vsd,
    "demanda_m3_min": demanda_m3_min,
    "t_agua": t_agua_c + 273.15,
    "folga_rel": folga_rel_input,
    "r_f_equiv": rf_fouling_input,
    "zeta_filtro": zeta_filtro_input,
    "fad_m3_min": fad,
    "n_compressores": n_compressores,
    "n": n_pol,
    "v_i": v_i,
    "eta_mec": eta_mec,
    "m_carcaca": m_carcaca,
    "c_carcaca": c_carcaca,
    "cond_ext_carcaca": cond_ext_carcaca,
    "cond_arref_carcaca": cond_arref_carcaca,
    "delta_nom_um": delta_nom_um,
    "hood_enclausurado": hood_enclausurado,
    "s_motor": s_motor,
    "p_fixas_motor": p_fixas_motor,
    "m_dot_vent": m_dot_vent,
    "p_loss_hood_outros": p_loss_hood_outros,
    "ua_projeto": ua,
    "eta_sep": eta_sep,
    "material_psa": material_psa,
    "massa_leito_psa": massa_leito_psa,
    "fator_purga": purga_pct / 100.0,
    "eps_recup_psa": eps_recup_psa,
    "v_vaso": v_vaso,
    "p_limite": p_limite_bar * 1e5,
}

# Execução da simulação física central
res_sim = simular(params)
snapshot_pi = pi_telemetry.extrair_snapshot_pi(res_sim, params, prefixo="CMP01", adicionar_ruido=True)


# Banner de Modo Treinamento (visível em todas as abas)
if st.session_state["modo_treinamento"]:
    st.markdown(
        "<div style='background:#7c3aed;color:#fff;padding:10px 18px;border-radius:8px;"
        "margin-bottom:12px;font-weight:700;font-size:1em;letter-spacing:0.04em;'>"
        "🎓 MODO TREINAMENTO ATIVO — Os dados abaixo são sintéticos. "
        "Saia pelo botão na barra lateral para retornar ao modo operacional.</div>",
        unsafe_allow_html=True,
    )

# ===========================================================================
# 2. ABA: DASHBOARD DIGITAL TWIN & TELEMETRIA PI
# ===========================================================================
with tab_dashboard:
    _ativos_lista = ["CMP-01", "CMP-02", "CMP-03", "CMP-04"]
    _ativo_nome = _ativos_lista[st.session_state.get("ativo_idx", 0)]
    st.subheader(f"📊 Dashboard — {_ativo_nome}")
    st.caption("Pontos A a I (Tabela 18.1) · Telemetria PI em tempo real · Balanço exergético (Eq. 17.3)")

    # Faixa de alarmes ativos (se houver)
    _alarmes_ativos = [t for t, d in snapshot_pi.items() if d.get("status_alarme") in ("ALARME", "TRIP")]
    if _alarmes_ativos:
        st.markdown(
            f"<div style='background:#991b1b;color:#fff;padding:8px 14px;border-radius:6px;"
            f"margin-bottom:8px;font-weight:700;'>⚠️ {len(_alarmes_ativos)} TAG(S) EM ALARME — "
            f"{', '.join(_alarmes_ativos[:4])}{'...' if len(_alarmes_ativos)>4 else ''}</div>",
            unsafe_allow_html=True,
        )


    # ── Nível 1: 3 KPIs Grandes ──────────────────────────────────────────────
    _w_kw   = res_sim['potencias']['w_total_planta'] / 1000.0
    _spc    = res_sim['kpis']['spc']
    _eta    = res_sim['kpis']['eta_global'] * 100.0
    _exerg  = max(0.0, (res_sim['potencias']['w_total'] - res_sim['potencias']['w_isotermico']) / 1000.0)
    _co2    = _w_kw * 0.40
    _pdp    = res_sim['nos'][5]['pdp_c']

    kp1, kp2, kp3 = st.columns(3)
    kp1.markdown(
        f"<div class='kpi-card'><div class='kpi-label'>⚡ Potência Elétrica Total</div>"
        f"<div class='kpi-value'>{_w_kw:.1f} <span style='font-size:0.55em'>kW</span></div>"
        f"<div class='kpi-delta-ok'>ISO 1217 — Equação 11.11</div></div>", unsafe_allow_html=True)
    kp2.markdown(
        f"<div class='kpi-card'><div class='kpi-label'>📊 Consumo Específico (SPC)</div>"
        f"<div class='kpi-value'>{_spc:.3f} <span style='font-size:0.45em'>kW·m⁻³·min</span></div>"
        f"<div class='kpi-delta-ok'>Norma ISO 1217 — Eq. 11.11</div></div>", unsafe_allow_html=True)
    kp3.markdown(
        f"<div class='kpi-card'><div class='kpi-label'>🎯 Eficiência Global η</div>"
        f"<div class='kpi-value'>{_eta:.1f} <span style='font-size:0.55em'>%</span></div>"
        f"<div class='kpi-delta-ok'>W_isotérmico / W_real — Eq. 5.13</div></div>", unsafe_allow_html=True)

    # ── Nível 2: 4 KPIs Secundários ──────────────────────────────────────────
    ks1, ks2, ks3, ks4 = st.columns(4)
    ks1.metric("🔥 Exergia Destruída İ", f"{_exerg:.1f} kW", help="Irreversibilidade — Eq. 17.3")
    ks2.metric("🌿 Emissão CO₂", f"{_co2:.1f} kg/h", help="Fator 0.40 kg CO₂/kWh — Eq. 17.5")
    _pdp_delta = _pdp - (-40.0)
    _delta_col = "normal" if _pdp_delta < 0 else "inverse"
    ks3.metric("💧 PDP — Ponto de Orvalho", f"{_pdp:.1f} °C",
               delta=f"{_pdp_delta:+.1f} vs Classe 2 (ISO 8573-1)", delta_color=_delta_col)
    _ni_alm = sum(1 for t in snapshot_pi.values() if t["status_alarme"] != "NORMAL")
    ks4.metric("🚨 Alarmes ISA 18.2 Ativos", str(_ni_alm),
               delta="⚠️ Verificar tags" if _ni_alm > 0 else "✅ Todos normais",
               delta_color="inverse" if _ni_alm > 0 else "normal")

    st.divider()

    # ── Perfis Termodinâmicos + Tabela de Nós ────────────────────────────────
    st.markdown("### 🗺️ Perfis Termodinâmicos ao Longo do Trem (Pontos A – I)")
    col_diag, col_nodes = st.columns([1.4, 1.0])

    with col_diag:
        nomes_nos = [n["nome"] for n in res_sim["nos"]]
        p_bar_nos = [n["p_bar"] for n in res_sim["nos"]]
        t_c_nos   = [n["t_c"]   for n in res_sim["nos"]]

        fig_diag, (ax_p, ax_t) = plt.subplots(2, 1, figsize=(8.5, 4.5), sharex=True)

        # Faixa de compressão preenchida
        ax_p.fill_between(range(len(nomes_nos)), p_bar_nos, alpha=0.12, color=BLUE)
        ax_p.plot(range(len(nomes_nos)), p_bar_nos, marker="o", ms=7, color=BLUE, lw=2.5, label="Pressão [bar abs]")
        ax_p.set_ylabel("Pressão [bar abs]")
        ax_p.legend(loc="upper left", fontsize=8)

        ax_t.fill_between(range(len(nomes_nos)), t_c_nos, alpha=0.10, color=RED)
        ax_t.plot(range(len(nomes_nos)), t_c_nos, marker="s", ms=7, color=RED, lw=2.5, label="Temperatura [°C]")
        ax_t.set_ylabel("Temperatura [°C]")
        ax_t.set_xticks(range(len(nomes_nos)))
        ax_t.set_xticklabels(nomes_nos, rotation=28, ha="right", fontsize=8)
        ax_t.legend(loc="upper left", fontsize=8)

        fig_diag.tight_layout()
        st.pyplot(fig_diag)

    with col_nodes:
        st.markdown("**📋 Status dos Nós de Processo**")
        df_nos = pd.DataFrame([
            {
                "Ponto": n["nome"],
                "P [bar]": f"{n['p_bar']:.2f}",
                "T [°C]": f"{n['t_c']:.1f}",
                "ṁ [kg/s]": f"{n['m_dot_total']:.4f}",
                "PDP [°C]": f"{n['pdp_c']:.1f}",
            }
            for n in res_sim["nos"]
        ])
        st.dataframe(df_nos, width="stretch", hide_index=True)

        st.markdown(f"""
        <div style='background:#f0f4f8;border-radius:8px;padding:10px 14px;margin-top:8px;'>
        <b>Circuito de Lubrificação</b><br>
        <span class='mono'>T_ret_óleo:</span> <b>{res_sim['kpis'].get('t_carcaca_c', 0.0)+5:.1f} °C</b><br>
        <span class='mono'>T_carcaça:</span> <b>{res_sim['kpis']['t_carcaca_c']:.1f} °C</b><br>
        <span class='mono'>HI Dessecante:</span> <b>{res_sim['kpis']['hi_des']:.3f}</b>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Tags PI agrupadas por subsistema em expanders ─────────────────────────
    st.markdown("### 🏷️ Telemetria Industrial — Tags PI por Subsistema (OSIsoft PI System)")

    # Agrupar tags por subsistema
    _grupos: dict[str, list] = {}
    for tag_id, tag_item in snapshot_pi.items():
        sub = tag_item["subsistema"]
        _grupos.setdefault(sub, []).append(tag_item)

    # Ícones por subsistema
    _icones = {
        "Painel Elétrico / MCC": "⚡",
        "Transmissão / Eixos": "⚙️",
        "Compressão Estágio LP": "🔵",
        "Intercooler": "❄️",
        "Compressão Estágio HP": "🔴",
        "Aftercooler": "🌊",
        "Secagem PSA": "💨",
        "Filtragem de Linha": "🔲",
        "Vaso de Pressão (Air Receiver)": "🫧",
        "Header / Distribuição": "🔀",
        "Circuito de Lubrificação": "🟡",
        "Gêmeo Digital (Saúde)": "🧠",
    }

    for sub_nome, tags in _grupos.items():
        tem_alarme = any(t["status_alarme"] != "NORMAL" for t in tags)
        icone = _icones.get(sub_nome, "📍")
        label = f"{icone} {sub_nome}  {'⚠️' if tem_alarme else '✅'}"

        with st.expander(label, expanded=tem_alarme):
            rows = []
            for t in tags:
                st_txt = t["status_alarme"]
                if "Trip" in st_txt or "Crítico" in st_txt:
                    badge_html = f"<span class='badge-trip'>🔴 TRIP</span>"
                elif "Alerta" in st_txt:
                    badge_html = f"<span class='badge-alerta'>🟡 ALERTA</span>"
                else:
                    badge_html = f"<span class='badge-normal'>🟢 OK</span>"
                rows.append({
                    "Tag": t["tag"],
                    "Descrição": t["descricao"],
                    "Valor": f"{t['valor']:.4g}",
                    "Unidade": t["unidade"],
                    "Status": st_txt,
                    "Qualidade": t["qualidade"],
                })
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)




# ===========================================================================
# MODO TREINAMENTO — Exibido como painel flutuante quando ativado pela sidebar
# ===========================================================================
if st.session_state["modo_treinamento"]:
    st.markdown("---")
    st.subheader("🎯 Arena de Treinamento de Falhas e Diagnóstico Operacional")
    st.caption(
        "Ambiente de capacitação para engenheiros de confiabilidade e operadores offshore. "
        "Analise os sintomas da telemetria PI, identifique a causa-raiz física e aplique as ações prescritivas normatizadas."
    )

    t_modo, t_estudo = st.tabs(["🕹️ Modo Desafio Cego (Exame)", "📚 Biblioteca Técnica de Mecanismos"])

    with t_modo:
        col_dif, col_btn_novo = st.columns([2, 1])
        dificuldade_sel = col_dif.select_slider(
            "Nível de Dificuldade do Cenário",
            options=["Iniciante", "Intermediario", "Avancado", "Mestre"],
            value="Intermediario",
            help="Iniciante: falhas com sintomas expressivos. Avancado/Mestre: falhas silenciosas e incipientes (desgaste de folgas, fouling leve, EDM) onde apenas a correlação de dados revela a causa-raiz."
        )

        if col_btn_novo.button("🎲 Gerar Novo Caso Cego", type="primary"):
            st.session_state["caso_treinamento"] = treinamento_falhas.gerar_caso_treinamento(
                dificuldade=dificuldade_sel,
                params_base=params,
            )
            st.session_state["resultado_avaliacao"] = None

        caso = st.session_state["caso_treinamento"]

        if caso is not None:
            st.markdown(
                f"<div class='fase-header'>📡 FASE 1 — OBSERVAÇÃO   "
                f"<span style='font-size:0.85em;font-weight:400;'>Cenário: Nível {caso['dificuldade']} "
                f"| Analise a telemetria e identifique os desvios</span></div>",
                unsafe_allow_html=True
            )

            # Exibição dos gráficos temporais do caso cego
            df_pi_caso = caso["df_serie_pi"]

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_c1, ax_c1 = plt.subplots(figsize=(7.5, 3.2))
                ax_c1.plot(df_pi_caso["Passo"], df_pi_caso["CMP01:LP_TDISC"], color=RED, label="CMP01:LP_TDISC [°C]")
                ax_c1.plot(df_pi_caso["Passo"], df_pi_caso["CMP01:HP_TDISC"], color=ORANGE, label="CMP01:HP_TDISC [°C]")
                ax_c1.axvline(15, color=GRAY, ls=":", label="Início da Ocorrência")
                ax_c1.set_xlabel("Tempo [Passos]")
                ax_c1.set_ylabel("Temperatura [°C]")
                ax_c1.legend(fontsize=8)
                ax_c1.set_title("Evolução Térmica dos Estágios", fontsize=10)
                fig_c1.tight_layout()
                st.pyplot(fig_c1)

            with col_g2:
                fig_c2, ax_c2 = plt.subplots(figsize=(7.5, 3.2))
                ax_c2.plot(df_pi_caso["Passo"], df_pi_caso["CMP01:ELE_I"], color=BLUE, label="CMP01:ELE_I [A]")
                ax_c2.plot(df_pi_caso["Passo"], df_pi_caso["CMP01:MEC_VIB_RMS"], color=NAVY, label="CMP01:MEC_VIB_RMS [mm/s]")
                ax_c2.axvline(15, color=GRAY, ls=":", label="Início da Ocorrência")
                ax_c2.set_xlabel("Tempo [Passos]")
                ax_c2.set_ylabel("Corrente / Vibração")
                ax_c2.legend(fontsize=8)
                ax_c2.set_title("Evolução Eletromecânica", fontsize=10)
                fig_c2.tight_layout()
                st.pyplot(fig_c2)

            col_g3, col_g4 = st.columns(2)
            with col_g3:
                fig_c3, ax_c3 = plt.subplots(figsize=(7.5, 3.2))
                ax_c3.plot(df_pi_caso["Passo"], df_pi_caso["CMP01:PSA_TDP"], color=GREEN, label="CMP01:PSA_TDP [°C]")
                ax_c3.axhline(-40.0, color=RED, ls="--", label="Limite Classe 2 (-40°C)")
                ax_c3.axvline(15, color=GRAY, ls=":", label="Início da Ocorrência")
                ax_c3.set_xlabel("Tempo [Passos]")
                ax_c3.set_ylabel("PDP [°C]")
                ax_c3.legend(fontsize=8)
                ax_c3.set_title("Ponto de Orvalho (Secador PSA)", fontsize=10)
                fig_c3.tight_layout()
                st.pyplot(fig_c3)

            with col_g4:
                fig_c4, ax_c4 = plt.subplots(figsize=(7.5, 3.2))
                ax_c4.plot(df_pi_caso["Passo"], df_pi_caso["CMP01:TK_PTK"], color=BLUE, label="CMP01:TK_PTK [bar]")
                ax_c4.plot(df_pi_caso["Passo"], df_pi_caso["CMP01:IC_PINT"], color=NAVY, label="CMP01:IC_PINT [bar]")
                ax_c4.axvline(15, color=GRAY, ls=":", label="Início da Ocorrência")
                ax_c4.set_xlabel("Tempo [Passos]")
                ax_c4.set_ylabel("Pressão [bar]")
                ax_c4.legend(fontsize=8)
                ax_c4.set_title("Pressões de Processo e Vaso Pulmão", fontsize=10)
                fig_c4.tight_layout()
                st.pyplot(fig_c4)

            # Painel com as últimas leituras de telemetria
            with st.expander("🔍 Ver Telemetria Instantânea das Tags PI (Snapshot do Caso)", expanded=False):
                st.dataframe(
                    pd.DataFrame([
                        {
                            "Tag": t_name,
                            "Valor": f"{t_data['valor']:.3g} {t_data['unidade']}",
                            "Status": t_data["status_alarme"],
                            "Subsistema": t_data["subsistema"],
                        }
                        for t_name, t_data in caso["snapshot_final_pi"].items()
                    ]),
                    width="stretch",
                    hide_index=True,
                )

            st.markdown("<div class='fase-header'>📝 FASE 3 — DIAGNÓSTICO   <span style='font-size:0.85em;font-weight:400;'>Preencha o formulário com sua análise técnica</span></div>", unsafe_allow_html=True)

            with st.form("form_diagnostico_treinamento"):
                fc1, fc2 = st.columns(2)
                
                subsistemas_lista = [
                    "Geração / Estágio LP", "Resfriamento Intermediário", "Admissão e Filtragem",
                    "Pacote / Invólucro (Hood)", "Tratamento / Secagem PSA", "Transmissão e Mancais",
                    "Painel Elétrico / Motor", "Painel Elétrico / Mancais", "Armazenamento e Segurança",
                    "Tratamento Primário / Drenagem", "Header / Distribuição"
                ]
                sub_escolhido = fc1.selectbox("1. Qual o Subsistema Afetado?", subsistemas_lista)

                mecanismos_opcoes = {m.id: f"{m.nome} ({m.capitulo})" for m in treinamento_falhas.CATALOGO_FALHAS_TREINAMENTO}
                mec_id_escolhido = fc2.selectbox(
                    "2. Qual a Causa-Raiz / Mecanismo Específico?",
                    options=list(mecanismos_opcoes.keys()),
                    format_func=lambda k: mecanismos_opcoes[k]
                )

                fc3, fc4 = st.columns(2)
                sev_escolhida = fc3.radio(
                    "3. Nível de Severidade Diagnosticado",
                    ["Leve/Incipiente", "Moderada/Alerta", "Severa/Crítica"],
                    horizontal=True
                )

                acoes_disponiveis = [m.acao_prescritiva for m in treinamento_falhas.CATALOGO_FALHAS_TREINAMENTO]
                acao_escolhida = fc4.selectbox("4. Qual a Ação Prescritiva Recomendada?", acoes_disponiveis)

                btn_submeter = st.form_submit_button("🏁 Submeter Avaliação Diagnóstica", type="primary")

            if btn_submeter:
                st.session_state["resultado_avaliacao"] = treinamento_falhas.avaliar_diagnostico_usuario(
                    caso=caso,
                    subsistema_escolhido=sub_escolhido,
                    mecanismo_id_escolhido=mec_id_escolhido,
                    severidade_escolhida=sev_escolhida,
                    acao_escolhida=acao_escolhida,
                )
                # Salva no histórico de tentativas
                st.session_state["historico_treinamento"].append({
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Dificuldade": caso["dificuldade"],
                    "Mecanismo Real": caso["mecanismo_gabarito"].nome,
                    "Mecanismo Indicado": mecanismos_opcoes[mec_id_escolhido],
                    "Score": st.session_state["resultado_avaliacao"]["score_total"],
                    "Status": "Aprovado" if st.session_state["resultado_avaliacao"]["aprovado"] else "Reprovado",
                })

            # Exibição do Parecer da Avaliação
            if st.session_state["resultado_avaliacao"] is not None:
                av = st.session_state["resultado_avaliacao"]
                st.markdown("<div class='fase-header'>🏆 FASE 4 — RESULTADO & GABARITO</div>", unsafe_allow_html=True)

                score = av["score_total"]
                # Barra de progresso visual com cor dinâmica
                score_cor = "#166534" if score >= 70 else ("#92400e" if score >= 50 else "#991b1b")
                st.markdown(f"""
                <div style='margin-bottom:4px;'><b>Pontuação Total: {score:.0f} / 100</b></div>
                <div class='progress-bar-outer'>
                  <div class='progress-bar-inner' style='width:{score}%;background:{score_cor};'></div>
                </div>""", unsafe_allow_html=True)

                sc1, sc2, sc3, sc4 = st.columns(4)
                sc1.metric("Subsistema", f"{av['pts_subsistema']:.0f}/25 pts")
                sc2.metric("Mecanismo", f"{av['pts_mecanismo']:.0f}/45 pts")
                sc3.metric("Severidade", f"{av['pts_severidade']:.0f}/15 pts")
                sc4.metric("Ação Prescritiva", f"{av['pts_acao']:.0f}/15 pts")

                if av["aprovado"]:
                    st.success(f"✅ **{av['classificacao']}**")
                else:
                    st.error(f"❌ **{av['classificacao']}**")

                with st.expander("🔬 Ver Gabarito Completo e Fundamentação Física"):
                    st.markdown(f"**Mecanismo Real**: `{av['gabarito_mecanismo'].nome}` ({av['gabarito_mecanismo'].capitulo} — {av['gabarito_mecanismo'].eq_ref})")
                    st.markdown(f"**Normas Aplicáveis**: `{av['normas']}`")
                    st.markdown(f"**Explicação Técnica**: {av['explicacao_tecnica']}")
                    st.markdown(f"**Ação Recomendada Correta**: {av['acao_esperada']}")
                    st.markdown("**Sintomas Típicos Esperados:**")
                    for s in av["sintomas_chave"]:
                        st.markdown(f"- {s}")

                col_next, _ = st.columns([1, 3])
                if col_next.button("▶️ Próximo Caso", type="primary"):
                    st.session_state["caso_treinamento"] = None
                    st.session_state["resultado_avaliacao"] = None
                    st.rerun()

        else:
            st.info("Clique em **'🎲 Gerar Novo Caso Cego'** acima para iniciar uma rodada de treinamento.")

        # Histórico da Sessão com gráfico de radar de competências
        if st.session_state["historico_treinamento"]:
            st.divider()
            st.markdown("### 📈 Histórico de Desempenho do Operador nesta Sessão")
            df_hist = pd.DataFrame(st.session_state["historico_treinamento"])
            st.dataframe(df_hist, width="stretch", hide_index=True)

            # Mini gráfico de scores ao longo das tentativas
            if len(df_hist) > 1:
                fig_hist, ax_hist = plt.subplots(figsize=(8.0, 2.5))
                cores_hist = [GREEN if s >= 70 else (ORANGE if s >= 50 else RED) for s in df_hist["Score"]]
                ax_hist.bar(range(len(df_hist)), df_hist["Score"], color=cores_hist, width=0.55)
                ax_hist.axhline(70, color=GREEN, ls="--", lw=1.2, label="Aprovação (70 pts)")
                ax_hist.set_xlabel("Tentativa #")
                ax_hist.set_ylabel("Score (pts)")
                ax_hist.set_ylim(0, 105)
                ax_hist.legend(fontsize=8)
                ax_hist.set_title("Evolução de Desempenho nas Tentativas", fontsize=10)
                fig_hist.tight_layout()
                st.pyplot(fig_hist)


    with t_estudo:
        st.markdown("### 📚 Catálogo Completo de Mecanismos de Falha e Diagnóstico")
        st.caption("Consulte os 15+ mecanismos de falha detalhados com suas equações físicas e diretrizes normativas.")

        for mec in treinamento_falhas.CATALOGO_FALHAS_TREINAMENTO:
            with st.expander(f"🔹 {mec.nome} [{mec.subsistema}] — {mec.capitulo} ({mec.eq_ref})"):
                st.markdown(f"**Descrição Física**: {mec.descricao_fisica}")
                st.markdown(f"**Detecção Primária**: `{mec.deteccao_primaria}` | **Dificuldade**: `{mec.dificuldade}`")
                st.markdown(f"**Norma de Referência**: `{mec.norma_referencia}`")
                st.markdown(f"**Ação Prescritiva**: {mec.acao_prescritiva}")
                st.markdown(f"**Equacionamento e Fundamentação**: {mec.explicacao_tecnica}")
                st.markdown("**Sintomas na Telemetria PI:**")
                for sint in mec.sintomas_pi:
                    st.markdown(f"- {sint}")


# ===========================================================================
# 3. ABA: DIAGNÓSTICO & IA — Laboratório + Motores de IA
# ===========================================================================
with tab_diagnostico:
    st.subheader("🔬 Diagnóstico & Inteligência Artificial")
    st.caption("Laboratório de injeção de falhas, classificador m̂_falha e motores de IA do Gêmeo Digital.")

    td1, td2 = st.tabs(["🚨 Laboratório de Falhas & Classificador m̂_falha", "🧠 Motores de IA (EKF · VAE · PIML · MPC · PSO)"])

    with td1:
        st.markdown("#### Laboratório de Injeção de Falhas & Classificador m̂_falha (Eq. 29.2)")
        st.caption(
            "Injete falhas de forma interativa, compare a telemetria real (PI) contra o Gêmeo Digital "
            "e execute a classificação automática de causa-raiz por resíduo mínimo ponderado."
        )

        col_l1, col_l2 = st.columns([1.5, 1.0])

        with col_l1:
            falhas_opcoes = {m.id: f"{m.nome} ({m.subsistema})" for m in treinamento_falhas.CATALOGO_FALHAS_TREINAMENTO}
            falha_lab_id = st.selectbox("Mecanismo a Injetar", list(falhas_opcoes.keys()), format_func=lambda k: falhas_opcoes[k])
            mec_lab = treinamento_falhas.buscar_mecanismo_por_id(falha_lab_id)

            sev_lab_pct = st.slider("Severidade da Falha Injetada [%]", 0, 100, 75, 5)
            sev_lab = sev_lab_pct / 100.0

        with col_l2:
            st.markdown(f"**Mecanismo**: `{mec_lab.nome}`")
            st.markdown(f"**Equação**: `{mec_lab.eq_ref}` | **Capítulo**: `{mec_lab.capitulo}`")
            st.markdown(f"**Parâmetro Físico**: `{mec_lab.parametro}` → valor severo: `{mec_lab.valor_severo}`")
            st.markdown(f"**Norma**: `{mec_lab.norma_referencia}`")

        # Execução da simulação saudável vs falha
        p_saudavel = dict(params)
        p_falha_lab = dict(params)
        val_ini_lab = params.get(mec_lab.parametro, 0.0)
        p_falha_lab[mec_lab.parametro] = val_ini_lab + sev_lab * (mec_lab.valor_severo - val_ini_lab)

        res_saudavel_lab = simular(p_saudavel)
        res_falha_lab = simular(p_falha_lab)

        snap_saudavel_lab = pi_telemetry.extrair_snapshot_pi(res_saudavel_lab, p_saudavel, adicionar_ruido=False)
        snap_falha_lab = pi_telemetry.extrair_snapshot_pi(res_falha_lab, p_falha_lab, adicionar_ruido=True)

        vetor_z_lab = {tag: info["valor"] for tag, info in snap_falha_lab.items()}

        # Classificador Multi-Mecanismo m̂_falha
        ranking_m_falha = treinamento_falhas.classificar_m_falha_minimo_residuo(vetor_z_lab, p_saudavel)

        st.divider()

        # Exibição do Classificador Automático
        st.markdown("### 🤖 Diagnóstico Automático via Gêmeo Digital (Classificador m̂_falha)")
        st.caption("Busca sobre todas as hipóteses m ∈ M por resíduo mínimo normalizado ponderado (Eq. 29.2 do livro).")

        top_m = ranking_m_falha[0]
        top_mec = top_m["mecanismo"]

        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("1º Diagnóstico (Mais Provável)", top_mec.nome, delta=f"{top_m['probabilidade_pct']:.1f}% confiança")
        dc2.metric("Resíduo Ponderado J(m)", f"{top_m['custo_j']:.3f}", help="Menor valor indica melhor ajuste físico")
        dc3.metric("Classificação de Acerto", "✅ EXATO" if top_mec.id == mec_lab.id else "⚠️ DISCREPÂNCIA")

        # Gráfico de Probabilidade dos Top Candidatos
        col_p, col_sh = st.columns(2)
        with col_p:
            top5_candidatos = ranking_m_falha[:5]
            fig_prob, ax_prob = plt.subplots(figsize=(7.0, 3.2))
            nomes_top5 = [item["mecanismo"].nome[:28] + "…" for item in top5_candidatos]
            probs_top5 = [item["probabilidade_pct"] for item in top5_candidatos]
            cores_top5 = [GREEN if item["mecanismo"].id == mec_lab.id else BLUE for item in top5_candidatos]
            bars = ax_prob.barh(nomes_top5[::-1], probs_top5[::-1], color=cores_top5[::-1], height=0.55)
            ax_prob.set_xlabel("Probabilidade [%]")
            ax_prob.set_xlim(0, 100)
            for bar, val in zip(bars, probs_top5[::-1]):
                ax_prob.text(val + 1.5, bar.get_y() + bar.get_height()/2.0, f"{val:.1f}%", va="center", fontsize=8)
            ax_prob.set_title("Top-5 Hipóteses Diagnosticadas", fontsize=10)
            fig_prob.tight_layout()
            st.pyplot(fig_prob)

        with col_sh:
            # Gráfico SHAP de Atribuição de Tags
            st.markdown("**🔬 Explicabilidade — Contribuição das Tags PI (Eq. 25.4)**")
            tags_residuos = top_m["residuos_tags"]
            tags_ordenadas = sorted(tags_residuos.items(), key=lambda x: x[1], reverse=True)[:8]
            fig_shap, ax_shap = plt.subplots(figsize=(7.0, 3.2))
            t_nomes = [t[0] for t in tags_ordenadas]
            t_pesos = [t[1] for t in tags_ordenadas]
            ax_shap.bar(t_nomes, t_pesos, color=ORANGE, width=0.5)
            ax_shap.set_ylabel("Impacto no Resíduo J(m)")
            ax_shap.set_title("Top Tags PI Determinantes", fontsize=10)
            plt.setp(ax_shap.get_xticklabels(), rotation=35, ha="right", fontsize=7)
            fig_shap.tight_layout()
            st.pyplot(fig_shap)

    with td2:
        st.markdown("#### Motores de Inteligência Artificial do Gêmeo Digital (Parte II)")
        st.caption("Execução e validação dos 5 algoritmos fundamentais: EKF, VAE, PIML, MPC e PSO.")

        tg1, tg2, tg3, tg4, tg5 = st.tabs([
            "1. EKF & EKF Aumentado", "2. VAE (Espaço Latente)", "3. PIML (Física Informada)",
            "4. MPC (Controle Preditivo)", "5. PSO (Otimização Global)"
        ])

        with tg1:
            st.markdown("#### Filtro de Kalman Estendido — EKF (Eqs. 21.2–21.8)")
            folga_true_ekf = np.linspace(0.002, 0.009, n_passos_ekf)
            rf_true_ekf = np.zeros(n_passos_ekf)
            res_ekf = ekf.simular_ekf(
                params_base=params,
                folga_true=folga_true_ekf,
                r_f_true=rf_true_ekf,
                sigma_m_dot=1e-4,
                sigma_t_hp=0.05,
                q_proc_diag=(1e-7, 1e-10),
                x0=(0.002, 0.0),
                p0_diag=(1e-6, 1e-10),
                seed=42,
            )

            fig_ekf, (ax_e1, ax_e2) = plt.subplots(1, 2, figsize=(11.0, 3.2))
            eixo_t = np.arange(n_passos_ekf) * dt_horas_ekf / 24.0

            ax_e1.plot(eixo_t, res_ekf["folga_true"] * 1000.0, color=GREEN, label="δ/L real (oculto)")
            ax_e1.plot(eixo_t, res_ekf["x_hat"][:, 0] * 1000.0, color=BLUE, label="δ/L estimado EKF")
            ax_e1.fill_between(
                eixo_t,
                (res_ekf["x_hat"][:, 0] - 2 * res_ekf["std"][:, 0]) * 1000.0,
                (res_ekf["x_hat"][:, 0] + 2 * res_ekf["std"][:, 0]) * 1000.0,
                color=BLUE, alpha=0.2, label="IC 95%"
            )
            ax_e1.set_xlabel("Tempo [dias]")
            ax_e1.set_ylabel("Folga Relativa [μm/m]")
            ax_e1.legend(fontsize=7)
            ax_e1.set_title("Estimação de Folga LP (δ)", fontsize=10)

            ax_e2.plot(eixo_t, res_ekf["nis"], color=NAVY, label="NIS medido")
            ax_e2.axhline(7.0, color=GREEN, ls="--", label="Média esperada (df=7)")
            ax_e2.axhline(14.07, color=RED, ls=":", label="Limiar 95% χ²")
            ax_e2.set_xlabel("Tempo [dias]")
            ax_e2.set_ylabel("NIS (Eq. 21.7)")
            ax_e2.legend(fontsize=7)
            ax_e2.set_title("Auditoria Estatística NIS", fontsize=10)
            fig_ekf.tight_layout()
            st.pyplot(fig_ekf)

        with tg2:
            st.markdown("#### Redução de Dimensionalidade & Detecção de Anomalia via VAE (Cap. 22)")
            @st.cache_resource
            def _obter_vae_treinado(_p, _chave):
                X_tr = vae.gerar_dataset_saudavel(n_amostras_vae, _p, seed=42)
                info = vae.treinar(X_tr, n_epocas=n_epocas_vae, lr=1e-3, beta=0.1)
                X_val = vae.gerar_dataset_saudavel(50, _p, seed=99)
                e_val = vae.erro_reconstrucao(info, X_val)
                limiar = float(np.percentile(e_val, 99.0))
                return info, limiar

            info_vae, limiar_vae = _obter_vae_treinado(params, (round(params["t_amb"], 1), n_amostras_vae, n_epocas_vae))
            feat_atual = vae.extrair_features(res_sim)[None, :]
            e_atual = float(vae.erro_reconstrucao(info_vae, feat_atual)[0])

            vc1, vc2 = st.columns(2)
            vc1.metric("Erro de Reconstrução E_rec Atual", f"{e_atual:.2f}")
            vc2.metric("Limiar de Disparo (Eq. 22.6)", f"{limiar_vae:.2f}")

            if e_atual > limiar_vae:
                st.warning("⚠️ Operação fora do padrão saudável (Anomalia detectada pelo VAE)")
            else:
                st.success("✅ Operação dentro da distribuição de normalidade do VAE")

        with tg3:
            st.markdown("#### Physics-Informed Machine Learning — PIML (Cap. 23)")
            st.caption("Rede neural treinada sob restrições físicas de conservação de energia e balanço térmico.")
            @st.cache_resource
            def _obter_piml_treinado(_p, _chave):
                faixas = {"pi_total": (6.0, 10.0), "t_amb_c": (10.0, 40.0), "folga_rel": (0.001, 0.02), "r_f_equiv": (0.0, 5e-4), "fad_m3_min": (8.0, 12.0)}
                entradas_tr, saidas_tr = piml.gerar_dataset(n_amostras_piml, _p, faixas, seed=0)
                info = piml.treinar(entradas_tr, saidas_tr, faixas, n_epocas=n_epocas_piml, lr=1e-2)
                return info

            info_piml = _obter_piml_treinado(params, (round(params["t_amb"], 1), n_amostras_piml, n_epocas_piml))
            fig_piml, ax_pi = plt.subplots(figsize=(8.5, 2.8))
            ax_pi.plot(info_piml["hist_data"], color=BLUE, label="L_data (Erro de Dados)")
            ax_pi.plot(info_piml["hist_fisica"], color=RED, label="L_physics (Resíduo de Conservação)")
            ax_pi.set_yscale("log")
            ax_pi.set_xlabel("Época")
            ax_pi.set_ylabel("Perda (log)")
            ax_pi.legend(fontsize=8)
            fig_piml.tight_layout()
            st.pyplot(fig_piml)

        with tg4:
            st.markdown("#### Controle Preditivo Baseado em Modelo — MPC (Cap. 24)")
            r_mpc = mpc.simular_mpc(
                horizonte_min=30, dt=1.0, n_horizonte=10,
                m_dot_cap=res_sim["nos"][-1]["m_dot"] * params["n_compressores"],
                v_vaso=params["v_vaso"], t_k=params["t_amb"],
                p_set=params["p_amb"] * params["pi_total"],
                dem_base=0.15, t_ev=(10*60, 20*60), fator_ev=1.3,
                rho=0.1, x_c_min=dinamica.X_C_MIN,
                w_nom=res_sim["potencias"]["w_total_planta"], eta_vsd=dinamica.ETA_VSD
            )
            fig_mpc, ax_mpc = plt.subplots(figsize=(8.5, 2.8))
            ax_mpc.plot(r_mpc["t_min"], r_mpc["p_bar"], color=BLUE, label="MPC (Antecipativo)")
            ax_mpc.axhline(params["p_amb"] * params["pi_total"] / 1e5, color=GREEN, ls=":", label="Referência")
            ax_mpc.set_xlabel("Tempo [min]")
            ax_mpc.set_ylabel("Pressão [bar abs]")
            ax_mpc.legend(fontsize=8)
            fig_mpc.tight_layout()
            st.pyplot(fig_mpc)

        with tg5:
            st.markdown("#### Otimização por Enxame de Partículas — PSO (Cap. 24.2)")
            st.caption("Minimiza o SPC (Consumo Específico) variando a razão de pressão π — Eqs. 24.3 e 24.4.")
            if st.button("🚀 Otimizar Setpoint de Pressão via PSO"):
                def _custo_spc(x):
                    _p = dict(params)
                    _p["pi_total"] = float(x[0])
                    return simular(_p)["kpis"]["spc"]

                r_pso = pso.otimizar(
                    func_custo=_custo_spc,
                    limite_inf=[6.0],
                    limite_sup=[10.0],
                    n_particulas=n_particulas_pso,
                    n_iter=n_iter_pso,
                    seed=42,
                )
                pi_otimo = float(r_pso["g_best"][0])
                spc_otimo = float(r_pso["g_best_custo"])
                st.success(f"✅ Ótimo Global: **π* = {pi_otimo:.2f}** | SPC Mínimo = **{spc_otimo:.4f} kW·m⁻³·min**")

                fig_pso, ax_pso = plt.subplots(figsize=(8.0, 2.5))
                ax_pso.plot(r_pso["historico_custo"], color=BLUE, lw=2)
                ax_pso.set_xlabel("Iteração PSO")
                ax_pso.set_ylabel("SPC (Custo)")
                ax_pso.set_title("Convergência do PSO — g_best por Iteração", fontsize=10)
                fig_pso.tight_layout()
                st.pyplot(fig_pso)




# ===========================================================================
# 4. ABA: FROTA OFFSHORE — Supervisório de Múltiplos Compressores
# ===========================================================================
with tab_frota:
    st.subheader("🚢 Painel Supervisório de Frota Offshore (Seção 26.6)")
    st.caption(
        "Monitoramento integrado de múltiplos compressores em paralelo na plataforma. "
        "Priorização por urgência, Health Index composto (Eq. 26.4), NIS (Eq. 21.7) e RUL bayesiano."
    )

    col_btn_f, col_info_f = st.columns([1, 3])
    if col_btn_f.button("🔄 Executar Ciclo de Varredura da Frota (t_k)", type="primary"):
        st.session_state["painel_frota"] = frota_supervisorio.executar_ciclo_supervisorio_frota(
            st.session_state["frota_instancias"], dt_dias=1.0
        )

    painel_frota = st.session_state.get(
        "painel_frota",
        frota_supervisorio.executar_ciclo_supervisorio_frota(st.session_state["frota_instancias"], dt_dias=0.0)
    )

    # Resumo rápido
    n_crit = sum(1 for m in painel_frota if m["hi"] < 0.60)
    n_alrt = sum(1 for m in painel_frota if 0.60 <= m["hi"] < 0.85)
    n_ok   = sum(1 for m in painel_frota if m["hi"] >= 0.85)
    col_info_f.markdown(
        f"**Visão Geral da Frota** — "
        f"<span style='color:#166534;font-weight:700;'>✅ {n_ok} Normais</span>  "
        f"<span style='color:#92400e;font-weight:700;'>⚠️ {n_alrt} Atenção</span>  "
        f"<span style='color:#991b1b;font-weight:700;'>🔴 {n_crit} Críticos</span>",
        unsafe_allow_html=True
    )

    st.markdown("### 📋 Status dos Ativos (Ordenado por Urgência)")

    for item in painel_frota:
        hi_val = item["hi"]
        # Classe CSS do card baseada no HI
        if hi_val >= 0.85:
            card_class = "fleet-card fleet-card-ok"
            status_emoji = "🟢"
            hi_cor = "#166534"
        elif hi_val >= 0.60:
            card_class = "fleet-card fleet-card-warn"
            status_emoji = "🟡"
            hi_cor = "#92400e"
        else:
            card_class = "fleet-card fleet-card-crit"
            status_emoji = "🔴"
            hi_cor = "#991b1b"

        st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)

        c1, c2, c3, c4, c5, c6 = st.columns([1.8, 1.0, 1.0, 1.2, 1.0, 0.9])
        c1.markdown(
            f"<div style='font-size:1.1em;font-weight:700;'>{status_emoji} {item['nome']}</div>"
            f"<div style='font-size:0.8em;color:#64748b;'>{item['maquina_id']}</div>",
            unsafe_allow_html=True
        )

        # Barra de HI proporcional
        hi_pct = hi_val * 100
        c2.markdown(
            f"<div style='font-size:0.75em;color:#64748b;'>Health Index (HI)</div>"
            f"<div style='font-size:1.3em;font-weight:700;color:{hi_cor};'>{hi_pct:.1f}%</div>"
            f"<div class='progress-bar-outer'><div class='progress-bar-inner' "
            f"style='width:{hi_pct:.0f}%;background:{hi_cor};'></div></div>",
            unsafe_allow_html=True
        )
        c3.metric("NIS (χ²)", f"{item['nis']:.2f}", help=item["nis_status"])
        c4.metric("RUL", f"{item['rul_estimado_dias']:.0f} dias",
                  help=f"IC 95%: [{item['rul_ic_min']:.0f}, {item['rul_ic_max']:.0f}] dias")
        c5.metric("SPC", f"{item['consumo_spc']:.3f}", help="kW·m⁻³·min")

        # Botão Analisar — seleciona o ativo e direciona ao Dashboard
        _btn_key = f"analisar_{item['maquina_id']}"
        if c6.button("🔍 Analisar", key=_btn_key, help=f"Abrir Dashboard de {item['maquina_id']}"):
            _mapa_id = {"CMP-01": 0, "CMP-02": 1, "CMP-03": 2, "CMP-04": 3}
            st.session_state["ativo_idx"] = _mapa_id.get(item["maquina_id"], 0)
            st.toast(f"✅ {item['maquina_id']} selecionado — Acesse a aba 📊 Dashboard do Ativo", icon="🔍")
            st.rerun()


        st.markdown("</div>", unsafe_allow_html=True)

        if item["tem_alarmes"]:
            st.warning(f"⚠️ **{item['maquina_id']}**: {len(item['alarmes'])} tag(s) em alarme ISA 18.2")
            with st.expander(f"Ver alarmes — {item['maquina_id']}"):
                st.dataframe(pd.DataFrame(item["alarmes"]), width="stretch", hide_index=True)


    # Gráficos de Frota
    st.divider()
    st.markdown("### 📊 Análise Comparativa de Desempenho e RUL")
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        fig_f1, ax_f1 = plt.subplots(figsize=(7.0, 3.2))
        ids_maq = [m["maquina_id"] for m in painel_frota]
        his_maq = [m["hi"] * 100 for m in painel_frota]
        cores_maq = [GREEN if h >= 85 else (ORANGE if h >= 60 else RED) for h in his_maq]
        bars_f1 = ax_f1.bar(ids_maq, his_maq, color=cores_maq, width=0.45)
        ax_f1.axhline(85.0, color=GREEN, ls="--", lw=1.0, label="Normal (85%)")
        ax_f1.axhline(60.0, color=ORANGE, ls="--", label="Atenção (60%)")
        ax_f1.axhline(40.0, color=RED, ls=":", label="Crítico (40%)")
        for bar, val in zip(bars_f1, his_maq):
            ax_f1.text(bar.get_x() + bar.get_width()/2, val + 1.5, f"{val:.0f}%", ha="center", fontsize=8)
        ax_f1.set_ylabel("Health Index [%]")
        ax_f1.set_ylim(0, 108)
        ax_f1.legend(fontsize=7)
        ax_f1.set_title("Health Index por Ativo da Frota", fontsize=10)
        fig_f1.tight_layout()
        st.pyplot(fig_f1)

    with col_f2:
        fig_f2, ax_f2 = plt.subplots(figsize=(7.0, 3.2))
        ruls_maq = [m["rul_estimado_dias"] for m in painel_frota]
        err_min = [m["rul_estimado_dias"] - m["rul_ic_min"] for m in painel_frota]
        err_max = [m["rul_ic_max"] - m["rul_estimado_dias"] for m in painel_frota]
        yerr = [err_min, err_max]
        ax_f2.errorbar(ids_maq, ruls_maq, yerr=yerr, fmt="o", ms=8, color=BLUE, ecolor=NAVY, elinewidth=2, capsize=5)
        for xi, yi in zip(ids_maq, ruls_maq):
            ax_f2.text(xi, yi + 3, f"{yi:.0f}d", ha="center", fontsize=8)
        ax_f2.set_ylabel("RUL [dias]")
        ax_f2.set_title("Prognóstico RUL com Incerteza 95% (Eq. 19.10)", fontsize=10)
        fig_f2.tight_layout()
        st.pyplot(fig_f2)



# ===========================================================================
# 5. ABA: SISTEMA & DINÂMICA — Dinâmica Temporal, PSA, Conector PI
# ===========================================================================
with tab_sistema:
    st.subheader("🛠️ Sistema & Dinâmica")
    st.caption("Dinâmica temporal da rede, ciclagem PSA e integração com OSIsoft PI System.")

    ts1, ts2, ts3 = st.tabs(["📈 Dinâmica Temporal", "🌀 Secagem PSA", "📂 Conector PI System"])

    with ts1:
        st.markdown("#### 📈 Visão Transiente de Vasos de Pressão & Trens de Compressão")
        st.caption("Evolução temporal contínua da pressão no vaso P_vaso(t), sucção P_in(t) e descarga P_out(t) frente a perturbações de demanda, monitorando conformidade com a PMTA (ASME VIII) e P_mín.")

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            duracao_min = st.slider("Duração da Simulação (T_sim) [min]", 10, 120, 30, 5)
        with col_d2:
            dt_s = st.selectbox("Passo de Integração (Δt)", [0.1, 0.5, 1.0, 2.0], index=1, format_func=lambda x: f"{x} s ({1/x:.0f} Hz)" if x < 1 else f"{x} s")
        with col_d3:
            modo_controle = st.radio("Modo de Modulação do Compressor", ["VSD (Inversor / Rampa 1ª Ordem)", "Carga / Alívio (Histerese)"], horizontal=True)

        n_passos_calc = int(duracao_min * 60.0 / dt_s)
        st.caption(f"⚙️ **Resolvedor Numérico:** Balanço Diferencial Contínuo dP/dt = (RT/V)·(ṁ_in - ṁ_out) [Euler Explícito] | **N = {n_passos_calc:,} passos** | **Δt = {dt_s}s** | **T_sim = {duracao_min} min**")

        rho_amb = nucleo.densidade_ar(params["p_amb"], params["t_amb"])
        dem_base_kg_s = rho_amb * params["demanda_m3_min"] / 60.0
        m_cap_kg_s = res_sim["nos"][-1]["m_dot"] * params["n_compressores"]
        p_set_pa = params["p_amb"] * params["pi_total"]

        res_trans = dinamica.simular_transiente(
            horizonte_min=duracao_min,
            m_dot_cap=m_cap_kg_s,
            w_nom=res_sim["potencias"]["w_total_planta"],
            v_vaso=params["v_vaso"],
            t_k=params["t_amb"],
            p_set=p_set_pa,
            p_limite=params["p_limite"],
            dem_base=dem_base_kg_s,
            t_ev=(duracao_min * 60 * 0.3, duracao_min * 60 * 0.6),
            fator_ev=1.35,
            modo="VSD" if "VSD" in modo_controle else "CARGA_ALIVIO",
            dp_db=dp_db_bar * 1e5,
            dt=dt_s,
        )

        kpts = res_trans["kpis"]
        asme_ok = kpts["integridade_asme_ok"]
        
        # Cards de Integridade ASME VIII
        tc1, tc2, tc3, tc4, tc5 = st.columns(5)
        tc1.metric("🛡️ Integridade ASME VIII", "✅ NORMAL" if asme_ok else "🚨 ALÍVIO PSV", help="ASME Seção VIII Div. 1")
        tc2.metric("🔴 PMTA Máx. Admissível", f"{kpts['pmta_bar']:.1f} bar", help="Pressão Máxima de Projeto do Vaso")
        tc3.metric("🟠 P_mín Crítica de Rede", f"{kpts['p_min_critica_bar']:.1f} bar", help="Pressão Mínima Operacional")
        tc4.metric("⏱️ Máxima Taxa dP/dt", f"{kpts['dp_dt_max_bar_min']:.2f} bar/min", help="Taxa de variação no vaso")
        tc5.metric("⚡ Energia Consumida", f"{kpts['energia_kwh']:.1f} kWh", help="Consumo no período")

        # Gráfico 1: Pressões de Vaso, Descarga e Sucção
        fig_trans, (ax_tp, ax_tw) = plt.subplots(2, 1, figsize=(10.5, 5.2), sharex=True)
        ax_tp.plot(res_trans["t_min"], res_trans["p_bar"], color=BLUE, lw=2.2, label="P_vaso (Vaso Pulmão) [bar abs]")
        ax_tp.plot(res_trans["t_min"], res_trans["p_out_bar"], color="#8b5cf6", lw=1.5, ls="--", label="P_out (Descarga Compressor) [bar abs]")
        ax_tp.plot(res_trans["t_min"], res_trans["p_in_bar"], color="#06b6d4", lw=1.5, label="P_in (Sucção / Vácuo Admissão) [bar abs]")
        ax_tp.axhline(kpts["pmta_bar"], color=RED, ls="--", lw=1.5, label=f"PMTA Máx. ASME VIII ({kpts['pmta_bar']:.1f} bar)")
        ax_tp.axhline(kpts["p_min_critica_bar"], color=ORANGE, ls=":", lw=1.5, label=f"P_mín Crítica ({kpts['p_min_critica_bar']:.1f} bar)")
        ax_tp.set_ylabel("Pressão [bar abs]", fontweight="bold")
        ax_tp.set_title("1. Perfil Temporal de Pressões e Limites Estruturais de Projeto", fontsize=10, fontweight="bold")
        ax_tp.legend(fontsize=8, loc="upper right")

        # Gráfico 2: Balanço de Vazões Mássicas e Potência
        ax_tw.plot(res_trans["t_min"], res_trans["m_comp"], color=GREEN, lw=1.8, label="ṁ_comp (Vazão Gerada) [kg/s]")
        ax_tw.plot(res_trans["t_min"], res_trans["m_dem"], color=RED, lw=1.8, ls="--", label="ṁ_demanda (Consumo Planta) [kg/s]")
        ax_tw.set_xlabel("Tempo [min]", fontweight="bold")
        ax_tw.set_ylabel("Vazão [kg/s]", color=GREEN, fontweight="bold")
        ax_tw.tick_params(axis='y', labelcolor=GREEN)

        ax_tw2 = ax_tw.twinx()
        ax_tw2.plot(res_trans["t_min"], res_trans["w_kw"], color="#eab308", lw=1.5, ls="-.", label="Potência Elétrica [kW]")
        ax_tw2.set_ylabel("Potência [kW]", color="#b45309", fontweight="bold")
        ax_tw2.tick_params(axis='y', labelcolor="#b45309")
        ax_tw.set_title("2. Balanço Dinâmico de Vazão Mássica e Potência Elétrica [kW]", fontsize=10, fontweight="bold")

        lines_1, labels_1 = ax_tw.get_legend_handles_labels()
        lines_2, labels_2 = ax_tw2.get_legend_handles_labels()
        ax_tw.legend(lines_1 + lines_2, labels_1 + labels_2, fontsize=8, loc="upper right")

        fig_trans.tight_layout()
        st.pyplot(fig_trans)

    with ts2:
        st.markdown("#### 🌀 Sistema de Secagem PSA — Ciclagem e Rodízio de Vasos (Cap. 15)")
        st.caption(
            "Simulação dinâmica de N torres em rodízio contínuo (Adsorção, Regeneração e Resfriamento). "
            "Cinética de adsorção exponencial (Eq. 15.1), recuperação de capacidade (Eq. 15.12), conformidade ISO 8573-1."
        )

        col_pcfg1, col_pcfg2, col_pcfg3 = st.columns(3)
        with col_pcfg1:
            n_vasos_sim = st.slider("Número de Torres em Rodízio (N_vasos)", 2, 6, 2, 1,
                                    help="Mínimo 2 torres para operação PSA alternada.")
            topologia_psa = st.radio("Topologia de Instalação", ["N vasos por compressor", "N vasos para o sistema"],
                                 horizontal=True)
    with col_pcfg2:
        t_ads_sim = st.slider("Duração da Adsorção [min]", 2.0, 180.0, 60.0, 5.0)
        t_regen_sim = st.slider("Duração da Regeneração [min]", 1.0, 90.0, 45.0, 5.0)
    with col_pcfg3:
        t_resf_sim = st.slider("Tempo de Resfriamento [min]", 0.0, 30.0, 10.0, 1.0)
        horiz_psa_min = st.slider("Horizonte de Simulação [min]", 30, 360, 180, 15)

    # Determina vazão de ar que chega ao secador PSA
    m_dot_ar_psa = res_sim["nos"][4]["m_dot"]
    if "sistema" in topologia_psa:
        m_dot_ar_psa *= float(params.get("n_compressores", 1))

    props_m = constantes.MATERIAIS_DESSECANTE[material_psa]
    p_low_psa = float(params.get("p_amb", 101325.0))
    p_high_psa = res_sim["nos"][4]["p_bar"] * 1e5

    sim_psa = psa_ciclo.simular_ciclo_psa(
        horizonte_min=float(horiz_psa_min),
        m_dot_ar=m_dot_ar_psa,
        t_ads_min=float(t_ads_sim),
        t_regen_min=float(t_regen_sim),
        t_resfriamento_min=float(t_resf_sim),
        n_vasos=n_vasos_sim,
        k_ads=float(props_m["k_ads_ref"]),
        p_low=p_low_psa,
        p_high=p_high_psa,
        fator_purga=params["fator_purga"],
        t_entrada_c=res_sim["nos"][4]["t_c"],
        delta_t_regen=constantes.DELTA_T_REGEN,
        pdp_entrada_c=res_sim["nos"][4]["pdp_c"],
        capacidade_trabalho=props_m["capacidade_trabalho"],
        massa_leito_kg=massa_leito_psa,
        dt_min=0.05,
    )

    kpis_psa = sim_psa["kpis"]

    # Alerta se houver janela sem secagem (todas as torres em regeneração/resfriamento)
    if kpis_psa["tempo_sem_secagem_min"] > 0:
        st.error(
            f"🚨 **ALERTA DE PROJETO (Subdimensionamento)**: Existe um intervalo total de "
            f"**{kpis_psa['tempo_sem_secagem_min']:.1f} minutos** sem nenhuma torre em adsorção "
            f"(tempo de regeneração + resfriamento excessivo para o número de torres). O ar passará sem secagem!"
        )
    else:
        st.success(
            f"✅ **Cobertura Contínua Garantida**: Mínimo de **{kpis_psa['n_adsorvendo_min']} torre(s)** "
            f"secando ar ininterruptamente ao longo de todo o ciclo."
        )

    # Cartões de Métricas da Ciclagem
    pk1, pk2, pk3, pk4, pk5 = st.columns(5)
    pk1.metric("Tempo de Ciclo (T_ciclo)", f"{kpis_psa['t_ciclo_min']:.1f} min")
    pk2.metric("Tempo Residência Calc.", f"{kpis_psa['t_res_calc_min']:.1f} min", help="Tempo para saturação total do leito (Eq. 15.6)")
    pk3.metric("Ponto de Orvalho Máx.", f"{kpis_psa['pdp_saida_max_c']:.1f} °C", delta=f"{kpis_psa['pdp_saida_max_c'] - (-40.0):+.1f} vs -40°C")
    pk4.metric("Purga Média", f"{kpis_psa['purga_media_kg_s']*1000:.1f} g/s")
    pk5.metric("Massa Água Retida Máx.", f"{kpis_psa['agua_adsorvida_max_kg']:.2f} kg/torre")

    st.divider()

    # 1. Diagrama de Gantt / Cronograma de Fases das Torres PSA
    st.markdown("### 📊 Cronograma de Rodízio e Estados Operacionais das Torres (Gantt)")
    
    t_psa = sim_psa["t_min"]
    estado_psa = sim_psa["estado"]  # shape (n_vasos, n_pontos)

    fig_gantt, ax_gantt = plt.subplots(figsize=(11.0, max(2.5, 0.7 * n_vasos_sim + 1.2)))
    cores_estado = {
        "Adsorvendo": BLUE,
        "Regenerando": ORANGE,
        "Resfriando": GREEN,
    }

    for i in range(n_vasos_sim):
        y_pos = n_vasos_sim - 1 - i
        for estado_nome, cor in cores_estado.items():
            mask = estado_psa[i] == estado_nome
            if np.any(mask):
                ax_gantt.fill_between(
                    t_psa, y_pos - 0.35, y_pos + 0.35,
                    where=mask, color=cor, alpha=0.85, step="mid"
                )

    # Legenda customizada
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=BLUE, label="Adsorvendo (Em serviço / Secando)"),
        Patch(facecolor=ORANGE, label="Regenerando (Aquecimento + Purga)"),
        Patch(facecolor=GREEN, label="Resfriando (Standby Térmico)"),
    ]
    ax_gantt.legend(handles=legend_elements, loc="upper right", fontsize=8)
    ax_gantt.set_yticks(range(n_vasos_sim))
    ax_gantt.set_yticklabels([f"Torre {n_vasos_sim - i}" for i in range(n_vasos_sim)])
    ax_gantt.set_xlabel("Tempo Decorrido [min]")
    ax_gantt.set_xlim(0, horiz_psa_min)
    ax_gantt.set_title("Rodízio Round-Robin das Torres PSA ao Longo do Tempo", fontsize=10)
    fig_gantt.tight_layout()
    st.pyplot(fig_gantt)

    st.divider()

    # 2. Curvas Dinâmicas de Capacidade e Temperatura dos Leitos
    st.markdown("### 📈 Curvas Dinâmicas de Capacidade e Temperatura dos Leitos")
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        fig_cap, ax_cap = plt.subplots(figsize=(7.5, 3.4))
        for i in range(n_vasos_sim):
            ax_cap.plot(t_psa, sim_psa["q_norm"][i], label=f"Torre {i+1}", lw=1.8)
        ax_cap.axhline(0.2, color=RED, ls=":", label="Limite de Esgotamento (20%)")
        ax_cap.set_xlabel("Tempo [min]")
        ax_cap.set_ylabel("Capacidade Dinâmica Normalizada (q_d / q_eq)")
        ax_cap.set_ylim(0, 1.05)
        ax_cap.legend(fontsize=7, loc="lower right")
        ax_cap.set_title("Evolução da Capacidade Adsortiva (Eq. 15.1 / Eq. 15.12)", fontsize=10)
        fig_cap.tight_layout()
        st.pyplot(fig_cap)

    with col_c2:
        fig_temp_psa, ax_temp_psa = plt.subplots(figsize=(7.5, 3.4))
        for i in range(n_vasos_sim):
            ax_temp_psa.plot(t_psa, sim_psa["temp_c"][i], label=f"Torre {i+1}", lw=1.8)
        ax_temp_psa.set_xlabel("Tempo [min]")
        ax_temp_psa.set_ylabel("Temperatura do Leito [°C]")
        ax_temp_psa.legend(fontsize=7, loc="upper right")
        ax_temp_psa.set_title("Ciclo Térmico de Aquecimento e Resfriamento", fontsize=10)
        fig_temp_psa.tight_layout()
        st.pyplot(fig_temp_psa)

    col_c3, col_c4 = st.columns(2)

    with col_c3:
        fig_pdp, ax_pdp = plt.subplots(figsize=(7.5, 3.4))
        ax_pdp.plot(t_psa, sim_psa["pdp_saida_c"], color=BLUE, lw=2, label="PDP de Saída [°C]")
        ax_pdp.axhline(-40.0, color=RED, ls="--", label="Classe 2 ISO 8573-1 (-40 °C)")
        ax_pdp.axhline(-70.0, color=GREEN, ls=":", label="Classe 1 ISO 8573-1 (-70 °C)")
        ax_pdp.set_xlabel("Tempo [min]")
        ax_pdp.set_ylabel("Ponto de Orvalho sob Pressão [°C]")
        ax_pdp.legend(fontsize=7)
        ax_pdp.set_title("Ponto de Orvalho Combinado Entregue à Rede", fontsize=10)
        fig_pdp.tight_layout()
        st.pyplot(fig_pdp)

    with col_c4:
        fig_pur, ax_pur = plt.subplots(figsize=(7.5, 3.4))
        ax_pur.plot(t_psa, sim_psa["m_purge_kg_s"] * 1000.0, color=ORANGE, lw=2, label="Vazão de Purga [g/s]")
        ax_pur.set_xlabel("Tempo [min]")
        ax_pur.set_ylabel("Vazão de Purga Total [g/s]")
        ax_pur.legend(fontsize=7)
        ax_pur.set_title("Demanda Instantânea de Ar de Purga (Eq. 15.2)", fontsize=10)
        fig_pur.tight_layout()
        st.pyplot(fig_pur)


    with ts3:
        st.markdown("#### 📂 Conector OSIsoft PI System & Gerador de Séries Temporais")
        st.caption(
            "Integração industrial com telemetria PI, visualização de tendências históricas, "
            "geração de datasets com ruído e exportador/importador compatível com PI Vision e PI Web API."
        )

    t_exp, t_imp, t_cat = st.tabs(["📤 Gerador & Exportador PI", "📥 Importador de Telemetria", "📑 Catálogo de Tags"])

    with t_exp:
        st.markdown("#### Gerar Série Temporal Sintética no Padrão PI")
        col_p1, col_p2, col_p3 = st.columns(3)
        passos_pi = col_p1.slider("Número de Passos (Amostras)", 20, 200, 60, 10)
        dt_pi_min = col_p2.number_input("Intervalo Δt [minutos]", 0.5, 60.0, 1.0, 0.5)
        prefixo_pi = col_p3.text_input("Prefixo do Ativo PI", "CMP01")

        df_telemetria = pi_telemetry.gerar_serie_temporal_pi(
            params_base=params,
            n_passos=passos_pi,
            dt_minutos=dt_pi_min,
            prefixo=prefixo_pi,
        )

        st.dataframe(df_telemetria.head(10), width="stretch")

        csv_pi_data = pi_telemetry.exportar_pi_csv(df_telemetria)
        st.download_button(
            label="⬇️ Baixar Telemetria Gerada (.csv padrão OSIsoft PI)",
            data=csv_pi_data,
            file_name=f"telemetria_pi_{prefixo_pi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    with t_imp:
        st.markdown("#### Carregar Arquivo de Telemetria Externa")
        arq_upload = st.file_uploader("Selecione arquivo CSV ou Excel de telemetria", type=["csv", "xlsx"])
        if arq_upload is not None:
            df_up = pi_telemetry.carregar_telemetria_arquivo(arq_upload)
            st.success(f"Arquivo carregado com sucesso: {len(df_up)} registros e {len(df_up.columns)} colunas.")
            st.dataframe(df_up.head(10), width="stretch")

    with t_cat:
        st.markdown("#### Matriz Completa de Tags PI Industriais (Tabela 18.1)")
        cat_tags = pi_telemetry.obter_catalogo_tags_pi(prefixo="CMP01")
        df_cat = pd.DataFrame([
            {
                "Tag": t.tag,
                "Descrição": t.descricao,
                "Ponto": t.ponto,
                "Subsistema": t.subsistema,
                "Unidade": t.unidade,
                "Tipo": t.tipo,
                "Faixa": f"[{t.faixa_min}, {t.faixa_max}]",
                "Alarme L/LL": f"{t.alarme_l}/{t.alarme_ll}" if t.alarme_l else "-",
                "Alarme H/HH": f"{t.alarme_h}/{t.alarme_hh}" if t.alarme_h else "-",
            }
            for t in cat_tags
        ])
        st.dataframe(df_cat, width="stretch", hide_index=True)
