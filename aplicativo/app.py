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
  planta);
- "Gêmeo Digital (EKF/PSO)": os 5 algoritmos da Parte II — EKF, VAE, PIML,
  MPC, PSO — incluindo os dois caminhos de identificação por problema
  inverso (EKF com estado aumentado, Cap. 28; PIML, Cap. 23.8);
- "Configurações": geometria de equipamento e hiperparâmetros de
  algoritmo que não mudam de uma sessão de análise para a outra — as
  condições de operação do momento continuam na barra lateral;
- "Dados Medidos": upload de referência (.xlsx/.csv) com a instrumentação
  real de uma planta, comparada contra a Tabela 18.1 do livro. Só
  documentação — não altera a simulação.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # mesmo backend do scripts/gen_figuras.py

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from compressor_sim import (
    calib_lm,
    constantes,
    dinamica,
    ekf,
    mpc,
    nucleo,
    parametros_default,
    piml,
    psa_ciclo,
    pso,
    simular,
    subsistemas,
    vae,
)

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
# Abas — criadas cedo: a aba "Configurações" precisa renderizar (e atribuir
# suas variáveis) antes do dict `params` ser montado, porque alimenta parte
# dele. Os corpos de tab_est/tab_din/tab_psa/tab_gd continuam mais abaixo,
# depois de `res = simular(params)` estar pronto.
# ---------------------------------------------------------------------------
tab_est, tab_din, tab_psa, tab_gd, tab_config, tab_dados = st.tabs([
    "⚙️ Operação estática", "📈 Dinâmica temporal", "🌀 Secagem PSA",
    "🧠 Gêmeo Digital (EKF/PSO)", "🎛️ Configurações", "📂 Dados Medidos",
])

# ---------------------------------------------------------------------------
# Aba "Configurações" — geometria de equipamento e hiperparâmetros de
# algoritmo: valores que descrevem esta máquina ou este experimento, não a
# condição de operação do momento (essa fica na barra lateral).
# ---------------------------------------------------------------------------
with tab_config:
    st.caption(
        "Parâmetros que normalmente não mudam de uma sessão de análise "
        "para a outra — geometria/constantes de equipamento e "
        "hiperparâmetros dos algoritmos da Parte II. Para temperatura "
        "ambiente, pressão de rede, demanda e outras condições do momento, "
        "use a barra lateral."
    )

    cfg1, cfg2 = st.columns(2)

    with cfg1:
        with st.expander("Compressor — geometria e eficiência", expanded=True):
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

        with st.expander("Resfriamento, vaso e rede — equipamento"):
            ua = st.number_input("UA de projeto [W/K] (assumido)", 500.0, 20000.0,
                                 defaults["ua_projeto"], 100.0)
            eta_sep = st.slider("Eficiência do separador η_sep (Eq. 14.4)",
                                0.80, 1.00, defaults["eta_sep"], 0.01)
            purga_pct = st.slider("Purga do secador PSA [%] (:1971)", 5, 25,
                                  int(defaults["fator_purga"] * 100))
            v_vaso = st.number_input("Volume do vaso [m³] (assumido)", 0.5, 20.0,
                                     defaults["v_vaso"], 0.5)
            p_limite_bar = st.number_input("Pressão mínima da rede [bar abs]",
                                           3.0, 8.0,
                                           defaults["p_limite"] / 1e5, 0.1)

        with st.expander("Dinâmica temporal — sintonia (aba 2)"):
            tau_vsd = st.slider(
                "Constante de tempo de rampa do VSD τ [s] (assumido)",
                1.0, 30.0, dinamica.TAU_VSD, 1.0)
            dp_db_bar = st.slider("Banda carga/alívio ΔP_db [bar]", 0.1, 1.5,
                                  dinamica.DP_DB / 1e5, 0.1)

        with st.expander("Secagem PSA — topologia e sintonia (aba 3)"):
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
            material_psa = st.selectbox(
                "Material dessecante (Tabela 15.2)",
                list(constantes.MATERIAIS_DESSECANTE.keys()),
                index=list(constantes.MATERIAIS_DESSECANTE.keys()).index(
                    constantes.MATERIAL_PSA_DEFAULT),
                help="Densidade e capacidade de trabalho (kg água/kg leito, "
                     "baixa UR) de cada material — mesma Tabela 15.2 do "
                     "livro (16/08/2026), faixas típicas de literatura/"
                     "fabricante, ASSUMIDAS (ver constantes.py). Peneira "
                     "molecular alcança PDP mais baixo; alumina ativada é o "
                     "padrão de mercado para ar comprimido; sílica gel é "
                     "fraca em baixa UR, raramente usada sozinha para "
                     "-40 °C.")
            _props_material = constantes.MATERIAIS_DESSECANTE[material_psa]
            t_ads_psa = st.slider(
                "Duração da adsorção por torre [min] (assumido)",
                2.0, 240.0, 60.0, 1.0,
                help="Estenda junto com regeneração/resfriamento abaixo para "
                     "um ciclo proporcional — regeneração térmica real "
                     "costuma levar dezenas de minutos, não os poucos "
                     "minutos de um ciclo PSA a frio por oscilação de "
                     "pressão.")
            t_regen_psa = st.slider(
                "Duração da regeneração por torre [min] (assumido)",
                1.0, 90.0, float(_props_material["t_regen_ref_min"]), 1.0,
                help=f"Valor de referência de {material_psa} preenchido "
                     "automaticamente — ajuste livremente. Só o valor da "
                     "Alumina Ativada (45 min) vem de experiência de campo "
                     "relatada pelo autor (16/08/2026); os outros dois "
                     "materiais reaproveitam o mesmo número por analogia, "
                     "sem fonte própria (ver constantes.py).")
            t_resfriamento_psa = st.slider(
                "Resfriamento pós-regeneração [min] (assumido)",
                0.0, 20.0, float(_props_material["t_resfriamento_ref_min"]), 1.0,
                help="Tempo em que a torre já regenerou mas ainda está quente "
                     "demais para voltar a adsorver com eficiência — sem essa "
                     "fase o rodízio simularia uma troca instantânea entre "
                     "regeneração e adsorção que não existe fisicamente. "
                     "Faixa 5-15 min relatada pelo autor para Alumina "
                     "Ativada (16/08/2026); outros materiais por analogia.")
            massa_leito_psa = st.number_input(
                "Massa do leito por torre [kg] (assumido)",
                1.0, 5000.0, constantes.MASSA_LEITO_PSA_DEFAULT_KG, 10.0,
                help=f"{material_psa}: densidade aparente "
                     f"≈{_props_material['densidade_kg_m3']:.0f} kg/m³, "
                     f"capacidade de trabalho ≈"
                     f"{_props_material['capacidade_trabalho']*100:.0f}% "
                     "(kg água/kg leito, baixa UR) — usados para converter a "
                     "capacidade normalizada em massa real de água "
                     "adsorvida (aba Secagem PSA) e, via balanço de massa "
                     "de água (Eq. 15.14), no tempo de residência de "
                     "projeto do leito — mais massa esgota mais devagar e "
                     "sustenta o PDP por mais tempo.")
            k_ads_psa = st.slider(
                "Constante de taxa de adsorção k_ads (Eq. 15.1, Fig. 15.2)",
                0.3, 4.0, float(_props_material["k_ads_ref"]), 0.1,
                help=f"Valor de referência do material selecionado "
                     f"({material_psa}) preenchido automaticamente — ajuste "
                     "livremente se tiver um valor de ensaio próprio. "
                     "**Não verificado contra literatura/ensaio** — só uma "
                     "ordenação relativa plausível entre os 3 materiais "
                     "(ver constantes.py).")
            eps_recup_psa = st.slider(
                "Efetividade do trocador de recuperação de calor ε (Eq. 15.11)",
                0.0, 1.0, constantes.EPSILON_RECUP_PSA_DEFAULT, 0.05,
                help="Fração do calor residual disponível (aftercooler + "
                     "hood, Eq. 15.10 — óleo não modelado neste app) "
                     "efetivamente recuperada para pré-aquecer o ar de "
                     "regeneração, reduzindo a potência elétrica do "
                     "aquecedor resistivo (Eq. 3.3) na mesma proporção. "
                     "ε=0 desliga a recuperação (aquecedor 100% elétrico).")
            forma_particula_psa = st.radio(
                "Forma da partícula do dessecante (Eqs. 15.17/15.18)",
                ["Esfera", "Pellet extrudado"],
                help="Esfericidade ψ_p = 1,0 (esfera) ou ψ_p ≈ 0,8 (pellet, "
                     "ASSUMIDO — meio da faixa 0,7-0,9 citada no livro). "
                     "Afeta a perda de carga do leito (Eq. 15.17, equação "
                     "de Ergun) e a cinética de adsorção k_ads (Eq. 15.18) "
                     "em direções opostas: pellets têm mais área externa "
                     "por volume — adsorvem mais rápido, mas também "
                     "impõem mais perda de carga para a mesma vazão.")
            psi_p_psa = (constantes.PSI_P_ESFERA if forma_particula_psa == "Esfera"
                        else constantes.PSI_P_PELLET)
            m_dot_reg_psa = st.slider(
                "Vazão do soprador booster de regeneração [kg/s] (assumido)",
                0.005, 0.50, constantes.M_DOT_REG_DEFAULT_KG_S, 0.005,
                help="Vazão de ar forçada pelo soprador booster através do "
                     "aquecedor de regeneração — fecha o coeficiente de "
                     "convecção h (Eq. 15.15, Dittus-Boelter) e, por "
                     "ε-NTU (Eq. 15.16), a temperatura real que o ar "
                     "atinge ao sair do aquecedor, substituindo o antigo "
                     "ΔT_regen assumido. Sem soprador suficiente, h cai "
                     "para a faixa de convecção natural e o mesmo "
                     "aquecedor de potência fixa entrega bem menos ΔT do "
                     "que o projeto pressupõe — mas vazão maior não eleva "
                     "essa temperatura de saída (na verdade cai "
                     "levemente), o ganho real é na potência térmica "
                     "total entregue ao leito.")

    with cfg2:
        with st.expander("Gêmeo Digital — EKF (aba 4, Eqs. 21.2-21.8)", expanded=True):
            st.caption(
                "Cenário: folga do estágio LP (δ/L) e fouling do intercooler "
                "(R_f) evoluem de um valor inicial a um final ao longo do "
                "horizonte — o EKF nunca vê esses valores, só as medições "
                "ruidosas de ṁ_seco e T_HP,in, e tenta reconstruí-los.")
            n_passos_ekf = st.slider("Horizonte do EKF [passos]", 20, 2000, 60, 10,
                                     help="Cada passo é um ciclo de varredura — o "
                                          "intervalo real entre eles é o "
                                          "\"Δt entre medições\" abaixo. Mecanismos "
                                          "de falha reais (folga, incrustação) se "
                                          "desenvolvem em semanas, não minutos — "
                                          "aumente este valor junto com o Δt para "
                                          "acompanhar um horizonte de dias.")
            dt_horas_ekf = st.number_input(
                "Δt entre medições [horas] (assumido)", 0.1, 24.0, 1.0, 0.1,
                help="Intervalo real de tempo entre dois passos do EKF — só "
                     "converte o eixo dos gráficos abaixo para dias, não afeta "
                     "o cálculo do filtro (Q/R já são por-passo, não por-hora).")
            folga_ini_ekf = st.number_input(
                "δ/L verdadeira — início (assumido)", 0.0005, 0.02, 0.002, 0.0005,
                format="%.4f")
            folga_fim_ekf = st.number_input(
                "δ/L verdadeira — fim (assumido)", 0.0005, 0.02, 0.009, 0.0005,
                format="%.4f")
            r_f_ini_ekf = st.number_input(
                "R_f verdadeiro — início (assumido)", 0.0, 1e-3, 0.0, 1e-5,
                format="%.5f")
            r_f_fim_ekf = st.number_input(
                "R_f verdadeiro — fim (assumido)", 0.0, 1e-3, 0.0, 1e-5,
                format="%.5f")
            sigma_m_dot_ekf = st.number_input(
                "Ruído do sensor de vazão σ [kg/s] (assumido)",
                1e-5, 5e-3, 1e-4, 1e-5, format="%.5f")
            sigma_t_hp_ekf = st.number_input(
                "Ruído do sensor de T_HP,in σ [°C] (assumido)",
                0.01, 2.0, 0.05, 0.01)
            q_folga_ekf = st.number_input(
                "Ruído de processo Q — δ/L (assumido)",
                1e-9, 1e-5, 1e-7, 1e-9, format="%.1e")
            q_rf_ekf = st.number_input(
                "Ruído de processo Q — R_f (assumido)",
                1e-12, 1e-7, 1e-10, 1e-12, format="%.1e")

        with st.expander("Gêmeo Digital — EKF com Estado Aumentado (aba 4, Cap. 28, Eqs. 28.1/28.2)"):
            st.caption(
                "Estado x_aug = [δ/L, R_f, K] — o coeficiente de vazamento K "
                "(Eq. 9.3), fixo em todo o resto do app, passa a ser também "
                "estimado. Cenário próprio (independente do EKF acima, mesmo "
                "padrão de escopo isolado já usado no PSO/MPC): janela de "
                "calibração com δ/L conhecida e constante, K partindo de uma "
                "crença deliberadamente errada; depois, K \"congela\" (Q "
                "pequeno) e δ/L volta a acompanhar deriva, como no EKF de 2 "
                "estados.")
            n_cal_aum = st.slider("Passos na janela de calibração", 15, 50, 30, 5)
            n_op_aum = st.slider("Passos após a calibração", 15, 2000, 40, 10,
                                 help="Mesmo Δt entre medições do EKF de 2 "
                                      "estados acima — aumente para acompanhar "
                                      "deriva de K/δ/L por vários dias após a "
                                      "calibração.")
            folga_cal_aum = st.number_input(
                "δ/L conhecida na janela de calibração (assumido)",
                0.002, 0.02, 0.010, 0.001, format="%.4f",
                help="O efeito de K na Eq. 9.3 escala com δ/L — folgas muito "
                     "baixas (ex. 0,002, condição de máquina nova) tornam K "
                     "quase inobservável frente ao ruído de medição típico; "
                     "este valor mais alto dá um sinal mais forte para a "
                     "calibração convergir.")
            folga_fim_aum = st.number_input(
                "δ/L verdadeira ao fim da operação (assumido)",
                folga_cal_aum, 0.03, 0.018, 0.001, format="%.4f")
            k_inicial_aum = st.number_input(
                "Crença inicial de K (assumido, != K real do app)",
                0.005, 0.15, 0.03, 0.005, format="%.3f",
                help=f"K real usado no restante do app: {defaults['k_folga']:.3f} "
                     "(Eq. 9.3) — mantido diferente aqui para que a convergência "
                     "mostrada seja identificação de verdade.")
            sigma_m_dot_aum = st.number_input(
                "Ruído do sensor de vazão σ [kg/s] — janela de calibração (assumido)",
                1e-6, 5e-4, 3e-5, 1e-6, format="%.1e",
                help="Precisão de instrumentação de bancada/comissionamento, "
                     "mais fina que o sensor de campo do EKF acima — o sinal de "
                     "K na Eq. 9.3 é pequeno mesmo com δ/L elevada, e precisa "
                     "de um ruído de medição proporcionalmente baixo para ser "
                     "identificável em poucas dezenas de ciclos.")

        with st.expander("Gêmeo Digital — PSO (aba 4, Eqs. 24.3/24.4)"):
            st.caption(
                "Otimiza a pressão de setpoint da rede (π) para minimizar o "
                "SPC (Eq. 11.11), sujeito a manter a autonomia do vaso acima "
                "de um mínimo requerido.")
            autonomia_min_pso = st.slider(
                "Autonomia mínima exigida [min] (restrição)", 0.0, 30.0, 1.0, 0.5,
                help="Com os defaults de vaso/demanda, a autonomia real fica "
                     "abaixo de ~1,5 min em toda a faixa de π pesquisada — uma "
                     "restrição alta (ex. 5 min) é inatingível em qualquer "
                     "ponto, e o PSO corretamente converge para a borda "
                     "superior da busca (menor penalidade possível, não um "
                     "mínimo interno) já na 1ª iteração, produzindo um "
                     "gráfico de convergência sem variação visível. O default "
                     "de 1 min já cruza a curva de autonomia dentro da faixa "
                     "de π, dando um ótimo interno de verdade para observar.")
            n_particulas_pso = st.slider("Número de partículas", 10, 60, 25, 5)
            n_iter_pso = st.slider("Número de iterações", 10, 100, 40, 5)
            w_ini_pso = st.slider("Peso de inércia inicial w_ini", 0.5, 1.0, 0.9, 0.05)
            w_fim_pso = st.slider("Peso de inércia final w_fim", 0.1, 0.6, 0.4, 0.05)
            c1_pso = st.slider("Coeficiente cognitivo c1", 0.5, 3.0, 2.0, 0.1)
            c2_pso = st.slider("Coeficiente social c2", 0.5, 3.0, 2.0, 0.1)

        with st.expander("Gêmeo Digital — VAE (aba 4, Eqs. 20.4, 22.1-22.7)"):
            st.caption(
                "Treinado sobre amostras sintéticas saudáveis (comissionamento, "
                "δ/L entre 0,0018-0,0022) — não existe dado real de planta "
                "neste projeto.")
            n_amostras_vae = st.slider("Amostras de treino (assumido)", 200, 1000, 500, 50,
                                       key="n_amostras_vae")
            n_epocas_vae = st.slider("Épocas de treino", 100, 500, 300, 50, key="n_epocas_vae")
            folga_cenario_vae = st.number_input(
                "δ/L do cenário de teste (assumido)", 0.0005, 0.03, 0.015, 0.001,
                format="%.4f",
                help="Valor bem fora da faixa saudável de treino dispara a "
                     "anomalia por padrão; reduza para ver o limite de detecção.")

        with st.expander("Gêmeo Digital — PIML (aba 4, Eqs. 23.1-23.4)"):
            st.caption(
                "Substituto treinado para [T_LP,out, T_HP,in, ṁ_seco, "
                "Q̇_intercooler] a partir de [π, T_amb, δ/L, R_f, FAD], com "
                "resíduo físico do balanço de energia do intercooler "
                "(Eq. 10.1) avaliado em pontos de colocação sem rótulo.")
            n_amostras_piml = st.slider("Amostras de treino (assumido)", 200, 800, 400, 50,
                                        key="n_amostras_piml")
            n_epocas_piml = st.slider("Épocas de treino", 100, 500, 300, 50, key="n_epocas_piml")

        with st.expander("Gêmeo Digital — PIML, Problema Inverso (aba 4, Cap. 23.8, Eq. 23.5)"):
            st.caption(
                "Em vez do balanço de energia do intercooler (Eq. 23.2), o "
                "resíduo físico aqui é a Equação 9.3 (balanço mássico), com o "
                "coeficiente de vazamento K tratado como incógnita Ξ — "
                "otimizada junto aos pesos da rede, não fixa em `params_base` "
                "como no restante do app.")
            n_amostras_piml_inv = st.slider("Amostras de treino (assumido)", 200, 800, 400, 50,
                                            key="n_amostras_piml_inv")
            n_epocas_piml_inv = st.slider("Épocas de treino", 100, 500, 300, 50,
                                          key="n_epocas_piml_inv")
            xi_inicial_piml = st.number_input(
                "Crença inicial de Ξ (assumido, != K real)",
                0.005, 0.15, 0.02, 0.005, format="%.3f",
                help=f"K real usado no restante do app: {defaults['k_folga']:.3f} "
                     "(Eq. 9.3) — mantido diferente aqui para que a "
                     "convergência mostrada seja identificação de verdade.")

        with st.expander("Gêmeo Digital — Calibração LM (aba 4, Cap. 28.1)"):
            st.caption(
                "Terceiro caminho para o mesmo K: mínimos quadrados não "
                "lineares em lote (scipy, Levenberg-Marquardt), sem filtro "
                "nem rede neural.")
            n_amostras_lm = st.slider("Amostras de calibração (assumido)", 20, 200, 60, 10)
            k_inicial_lm = st.number_input(
                "Crença inicial de K (assumido, != K real)",
                0.005, 0.15, 0.10, 0.005, format="%.3f", key="k_inicial_lm",
                help=f"K real usado no restante do app: {defaults['k_folga']:.3f} "
                     "(Eq. 9.3) — mantido diferente aqui para que a "
                     "convergência mostrada seja identificação de verdade.")
            sigma_m_dot_lm = st.number_input(
                "Ruído do sensor de vazão σ [kg/s] (assumido)",
                1e-5, 5e-3, 1e-4, 1e-5, format="%.5f", key="sigma_m_dot_lm")
            sigma_t_hp_lm = st.number_input(
                "Ruído do sensor de T_HP,in σ [°C] (assumido)",
                0.01, 2.0, 0.05, 0.01, key="sigma_t_hp_lm")

        with st.expander("Gêmeo Digital — MPC (aba 4, Eqs. 24.1/24.2)"):
            st.caption(
                "Compara o MPC (antecipa a demanda futura conhecida) contra o "
                "controle reativo já usado na aba \"Dinâmica temporal\" "
                "(só responde à demanda do instante atual).")
            demanda_base_mpc = st.slider(
                "Demanda base para o teste [m³/min] (assumido)", 1.0, 8.0, 5.0, 0.5,
                help="Mantida deliberadamente com folga em relação à capacidade "
                     "instalada — com demanda muito perto do limite, qualquer "
                     "controlador (MPC ou reativo) satura igualmente, e a "
                     "comparação deixa de mostrar diferença.")
            fator_ev_mpc = st.slider("Fator do pico de demanda", 1.1, 2.0, 1.4, 0.1)
            horizonte_mpc = st.slider("Horizonte de simulação [min]", 5, 20, 10, 1)
            dt_mpc = st.slider("Passo de tempo Δt [s] (assumido)", 2.0, 10.0, 5.0, 1.0)
            n_horizonte_mpc = st.slider("Horizonte de predição H [passos]", 6, 24, 12, 2)
            rho_mpc = st.number_input(
                "Peso do esforço de controle ρ (Eq. 24.1)", 0.0, 1.0, 0.05, 0.01,
                format="%.2f")

# ---------------------------------------------------------------------------
# Barra lateral — condições de operação (ajustadas com frequência)
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

    with st.expander("Compressor — ponto de operação", expanded=True):
        pi_total = st.slider("Pressão de rede [bar abs]", 5.0, 12.0,
                             defaults["pi_total"], 0.1)
        folga_rel = st.number_input("Folga relativa δ/L (Eq. 9.3)", 0.0, 0.02,
                                    defaults["folga_rel"], 0.001,
                                    format="%.3f")

    with st.expander("Resfriamento e secagem — estado medido/atual"):
        t_agua_c = st.slider("Água de resfriamento [°C]", 5.0, 40.0,
                             defaults["t_agua"] - 273.15, 0.5)
        r_f = st.number_input("Fouling R_f equivalente (Eq. 10.5)", 0.0, 1e-3,
                              defaults["r_f_equiv"], 1e-5, format="%.5f")

    with st.expander("Vaso pulmão e rede — demanda"):
        demanda = st.number_input("Demanda da rede [m³/min] (assumido)",
                                  0.0, 100.0, defaults["demanda_m3_min"], 0.5)

    with st.expander("Dinâmica temporal (aba 2)"):
        horizonte = st.slider("Horizonte de simulação [min]", 5, 60, 15)
        modo = st.selectbox("Modo de controle (Cap. 13)",
                            ["VSD", "Carga/Alívio"])
        evento = st.checkbox("Evento de pico de demanda", value=True)
        fator_ev = st.slider("Fator do pico (×demanda)", 1.2, 3.0, 2.0, 0.1)

    with st.expander("Secagem PSA — leitura atual (aba 3)"):
        horizonte_psa = st.slider(
            "Horizonte de simulação PSA [min]", 10, 7200, 240, 10,
            help="Até 7200 min (5 dias) — ciclos de regeneração térmica "
                 "real (dezenas de minutos) precisam de um horizonte bem "
                 "maior que os poucos minutos de um ciclo PSA a frio para "
                 "mostrar várias trocas de torre.")
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
    "psi_p": psi_p_psa,
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
    "eps_recup_psa": eps_recup_psa,
}

res = simular(params)
k = res["kpis"]
pw = res["potencias"]

for aviso in res["avisos"]:
    st.warning(aviso)

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
        "aba Configurações) e da própria carcaça; T_hood (Eq. 2.4) fecha a "
        "temperatura de regime do ar confinado a partir da vazão de "
        "ventilação forçada."
    )

    st.subheader("Carcaça do estágio LP — balanço térmico (Eq. 9.6)")
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Q̇_int conduzido à carcaça", f"{k['q_int_carcaca_w']:.0f} W")
    h2.metric("T_referência (Eq. 9.16)",
             f"{k['t_ref_carcaca_c']:.1f} °C",
             help="T_hood se enclausurado (Eq. 2.4), T_amb se a céu aberto — "
                  "ver caixa de seleção na aba Configurações.")
    h3.metric("T_carcaça (regime permanente)", f"{k['t_carcaca_c']:.1f} °C")
    h4.metric("Constante de tempo τ_c", f"{k['tau_carcaca_min']:.0f} min")
    st.caption(
        "Regime permanente da Eq. 9.6 (dT_c/dt = 0): Q_int (proxy — perda "
        "mecânica do estágio LP, W_LP·(1−η_mec)) se equilibra com Q_ext + "
        "Q_arref, modelados como condutâncias lineares (Newton) para a "
        "temperatura de referência acima. τ_c indica quão rápido a "
        "carcaça responde a uma mudança de carga — não é um transiente "
        "calculado ao longo do tempo nesta aba (só o valor de regime), "
        "diferente da rampa do VSD na aba \"Dinâmica temporal\"."
    )

    st.subheader("Temperatura do rotor e folga residual térmica (Eqs. 9.7/9.18/9.19)")
    r1, r2, r3 = st.columns(3)
    r1.metric("T_rotor (regime permanente)", f"{k['t_rotor_c']:.1f} °C")
    r2.metric("ΔT_rotor acima de T_amb", f"{k['delta_t_rotor_c']:.1f} K")
    r3.metric("Folga residual térmica δ_real", f"{k['folga_residual_um']:.0f} µm",
             help="Eq. 9.7 — δ_nom menos a dilatação térmica diferencial "
                  "rotor/carcaça. δ_real ≤ 0 sinaliza risco de contato "
                  "metálico (rubbing). Diagnóstico separado da folga "
                  "relativa δ/L da aba Configurações (usada diretamente na "
                  "eficiência volumétrica, Eq. 9.3): esta aqui é a mesma "
                  "grandeza física vista por uma lente térmica diferente, "
                  "não uma substituição — o EKF (aba 4) continua estimando "
                  "δ/L a partir de medições indiretas, sem depender deste "
                  "cálculo.")
    st.caption(
        "16/08/2026 — fecha a lacuna que a Eq. 9.6 sozinha (T_c) não "
        "cobria: T_rotor (Eq. 9.19) usa a mesma forma de regime permanente "
        "da carcaça, mas limitada por CIMA pela temperatura média do gás "
        "(T_gas,med = média entre sucção e descarga do estágio LP), não "
        "por baixo pela ambiente — o rotor perde calor por condução pelo "
        "eixo, não ganha calor do ambiente. cond_rotor (h_r·A_r) e "
        "Q̇_cond,eixo são parâmetros ASSUMIDOS (constantes.py), assim como "
        "δ_nom e os coeficientes de dilatação térmica α_rotor/α_carcaça."
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
            "Aquecedor sem recuperação (nominal, Eq. 3.3) [kW]":
                round(pw["aquecedor_nominal"] / 1000, 2),
            "Calor disponível p/ recuperação, Eq. 15.10 [kW]":
                round(pw["q_disp_regen"] / 1000, 2),
            "Q̇ intercooler [kW]": round(pw["q_intercooler"] / 1000, 2),
            "Q̇ aftercooler [kW]": round(pw["q_aftercooler"] / 1000, 2),
            "W isotérmico (referência) [kW]":
                round(pw["w_isotermico"] / 1000, 2),
        })
        economia_aquecedor_pct = (
            (1.0 - pw["aquecedor"] / pw["aquecedor_nominal"]) * 100.0
            if pw["aquecedor_nominal"] > 0 else 0.0)
        st.caption(
            f"Aproveitamento de calor rejeitado na regeneração (Eqs. 15.10/"
            f"15.11, 16/08/2026) — Q_disp soma aftercooler + hood (Q_óleo "
            "não modelado neste app); reduz **{:.0f}%** da potência "
            "elétrica nominal do aquecedor resistivo, sem mudar o ΔT de "
            "regeneração alvo (mesmo processo térmico, parte do calor vem "
            "de graça em vez do aquecedor). ε ajustável na aba "
            "Configurações → Secagem PSA.".format(economia_aquecedor_pct)
        )

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

    st.subheader("Pressão e temperatura em cada ponto do trem, ao longo do tempo")
    x_c_ativo = din["x_c"] > 0.02  # abaixo disso, compressor tratado como parado
    cores_pontos = plt.cm.tab10(np.linspace(0, 1, len(res["nos"])))
    figP, (axP, axT) = plt.subplots(1, 2, figsize=(12.6, 3.6))
    for idx, no in enumerate(res["nos"]):
        p_serie = np.where(x_c_ativo, no["p_bar"], np.nan)
        t_serie = np.where(x_c_ativo, no["t_c"], np.nan)
        axP.plot(din["t_min"], p_serie, color=cores_pontos[idx], lw=1.4,
                 label=no["nome"])
        axT.plot(din["t_min"], t_serie, color=cores_pontos[idx], lw=1.4,
                 label=no["nome"])
    axP.set_xlabel("Tempo [min]")
    axP.set_ylabel("Pressão [bar abs]")
    axT.set_xlabel("Tempo [min]")
    axT.set_ylabel("Temperatura [°C]")
    axP.legend(fontsize=6.5, ncol=2, loc="center left")
    figP.tight_layout()
    st.pyplot(figP)
    st.caption(
        "Linhas constantes enquanto o compressor está ativo — neste "
        "modelo, P e T de cada ponto do trem dependem só do ponto de "
        "operação fixo (pressão de rede, temperaturas ambiente/água), não "
        "da vazão instantânea: um compressor de deslocamento positivo a "
        "razão de pressão fixa entrega o mesmo perfil P/T em qualquer "
        "fração de carga do VSD, só a vazão mássica muda (gráfico "
        "\"Vazão mássica\" acima). O que de fato varia aqui é **quando** "
        "cada ponto está ativo: no modo Carga/Alívio, as linhas somem "
        "durante os intervalos de alívio (compressor parado, sem fluxo) — "
        "o padrão liga/desliga é o sinal relevante, não a forma da curva. "
        "Para ver P/T variando de verdade, seria preciso um cenário onde "
        "a própria pressão de rede (setpoint) ou as temperaturas de "
        "referência mudassem no tempo — não modelado nesta aba."
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

    # --- Soprador booster: fecha h (Dittus-Boelter, Eq. 15.15) e T_reg,in
    # (ε-NTU, Eq. 15.16) a partir da vazão do booster, substituindo o
    # antigo delta_t_regen assumido por um valor calculado. Forma da
    # partícula (Eq. 15.18) corrige k_ads antes de entrar no ciclo.
    # 16/08/2026.
    t_upstream_regen_c = res["nos"][4]["t_c"]
    h_aquecedor = subsistemas.coef_conveccao_forcada(
        m_dot_reg_psa, constantes.D_H_AQUECEDOR_M, constantes.MU_AR_REGEN,
        constantes.K_AR_REGEN, constantes.PR_AR, aquecendo=True)
    ua_aquecedor = h_aquecedor * constantes.A_AQUECEDOR_M2
    t_reg_in_c = subsistemas.saida_trocador(
        t_upstream_regen_c, constantes.T_ELEM_MAX_C, ua_aquecedor,
        m_dot_reg_psa * constantes.CP_AR)
    delta_t_regen_calc = t_reg_in_c - t_upstream_regen_c
    k_ads_efetivo = subsistemas.k_ads_por_forma(k_ads_psa, psi_p_psa)  # Eq. 15.18

    # --- Potência do soprador booster (Eq. 15.6, SEC_dry): perda de carga
    # do leito na vazão de regeneração (Ergun, Eq. 15.17) vezes vazão
    # volumétrica, sobre a eficiência do soprador.
    rho_ar_regen = nucleo.densidade_ar(p_high_psa, t_upstream_regen_c + 273.15)
    area_vaso_psa = np.pi * params["d_vaso_psa"] ** 2 / 4.0
    v_s_regen = m_dot_reg_psa / (rho_ar_regen * area_vaso_psa)
    dp_leito_regen = subsistemas.perda_carga_ergun(
        params["mu_ar_psa"], v_s_regen, rho_ar_regen, psi_p_psa,
        params["d_p_particula"], params["porosidade_leito"],
        params["l_leito_psa"])
    w_booster = (m_dot_reg_psa / rho_ar_regen) * dp_leito_regen / constantes.ETA_SOPRADOR_BOOSTER
    sec_dry_com_booster_kj_kg = subsistemas.sec_dry(
        res["potencias"]["aquecedor"] + w_booster, 0.0,
        res["potencias"]["m_dot_util"]) / 1000.0

    r_psa = psa_ciclo.simular_ciclo_psa(
        horizonte_min=horizonte_psa,
        m_dot_ar=m_dot_psa,
        t_ads_min=t_ads_psa,
        t_regen_min=t_regen_psa,
        t_resfriamento_min=t_resfriamento_psa,
        n_vasos=n_vasos_psa,
        k_ads=k_ads_efetivo,
        p_low=p_low_psa,
        p_high=p_high_psa,
        fator_purga=params["fator_purga"],
        t_entrada_c=res["nos"][4]["t_c"],
        delta_t_regen=delta_t_regen_calc,
        pdp_entrada_c=res["nos"][4]["pdp_c"],
        capacidade_trabalho=_props_material["capacidade_trabalho"],
        massa_leito_kg=massa_leito_psa,
    )
    kp = r_psa["kpis"]

    st.caption(
        f"Soprador booster ({m_dot_reg_psa:.3f} kg/s, {forma_particula_psa.lower()} "
        f"ψ_p={psi_p_psa:.2f}): h={h_aquecedor:.0f} W/(m²K) (Eq. 15.15) → "
        f"T_reg,in={t_reg_in_c:.1f} °C, ΔT_regen calculado={delta_t_regen_calc:.1f} K "
        f"(Eq. 15.16, substitui o antigo valor assumido) — k_ads efetivo "
        f"{k_ads_efetivo:.2f} (Eq. 15.18) — potência do booster "
        f"≈{w_booster:.0f} W (Eq. 15.17, Ergun) — SEC_dry com booster "
        f"≈{sec_dry_com_booster_kj_kg:.1f} kJ/kg (vs. "
        f"{k['sec_dry_kj_kg']:.1f} kJ/kg sem, no card abaixo)."
    )

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

    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("Trocas no horizonte", f"{kp['n_trocas']}")
    d2.metric("Capacidade mín. do leito (fim da adsorção)",
             f"{kp['q_min'] * 100:.1f}% de q_eq")
    d3.metric("Purga de regeneração (Eq. 15.2)",
             f"{kp['purga_media_kg_s'] * 3600:.1f} kg/h")
    d4.metric("Torres adsorvendo simultaneamente (mín.)",
             f"{kp['n_adsorvendo_min']}")
    d5.metric("Tempo de residência de projeto (Eq. 15.14)",
             f"{kp['t_res_calc_min']:.1f} min",
             help="Derivado da massa/capacidade do leito e da carga de "
                  "umidade do ar de entrada (16/08/2026) — não é mais um "
                  "valor independente. Aumentar a massa do leito (aba "
                  "Configurações) aumenta este valor e, com ele, quanto "
                  "tempo o PDP fica sustentado perto do alvo.")

    st.subheader("Indicadores Globais de Performance (Cap. 15)")
    e1, e2, e3 = st.columns(3)
    e1.metric("SEC_dry (Eq. 15.6)", f"{k['sec_dry_kj_kg']:.1f} kJ/kg",
             help="Só a parcela do aquecedor de regeneração — este app não "
                  "modela o secador de tambor rotativo (HOC) do Cap. 15, "
                  "então Ẇ_drum é sempre 0 aqui.")
    e2.metric("HI_des (Eq. 15.7)", f"{k['hi_des']:.2f}",
             help=f"1,0 = leito saudável (ΔP real, na barra lateral, igual "
                  f"ao ΔP nominal calculado por Ergun — Eq. 15.17, "
                  f"{k['dp_nom_psa_calc_bar']*1000:.0f} mbar na geometria/"
                  "vazão/forma de partícula atuais, 16/08/2026 — substitui "
                  "o antigo valor fixo de 300 mbar). Cai conforme ΔP real e "
                  "PDP real se afastam do nominal/alvo.")
    e3.metric("η_purge (Eq. 15.9)", f"{k['purga_pct']:.1f} %")
    if k["hi_des"] < 0.7:
        st.warning(
            f"HI_des = {k['hi_des']:.2f} — dessecante degradado (ΔP real "
            "ou PDP real distantes do nominal/alvo definidos na barra "
            "lateral). Ver Tabela 15.1 (Matriz de Diagnóstico de Falhas)."
        )

    st.subheader("Capacidade de adsorção e temperatura do leito por torre (Eq. 15.1)")
    fig8, ax8 = plt.subplots(figsize=(9.0, 3.6))
    cores_torres = plt.cm.tab10(np.linspace(0, 1, n_vasos_psa))
    for i in range(n_vasos_psa):
        ax8.plot(r_psa["t_min"], r_psa["q_norm"][i], color=cores_torres[i],
                 label=f"Torre {i + 1}", lw=1.6)
    ax8.set_xlabel("Tempo [min]")
    ax8.set_ylabel(r"$q_d \, / \, q_{eq}$")
    ax8.set_ylim(-0.05, 1.05)
    ax8b = ax8.twinx()
    for i in range(n_vasos_psa):
        ax8b.plot(r_psa["t_min"], r_psa["temp_c"][i], color=cores_torres[i],
                  ls="--", lw=1.0, alpha=0.6)
    ax8b.set_ylabel("Temperatura do leito [°C] (tracejado)")
    ax8b.grid(False)
    ax8.legend(fontsize=8, ncol=min(n_vasos_psa, 4), loc="lower left")
    fig8.tight_layout()
    st.pyplot(fig8)
    st.caption(
        "Linha cheia: capacidade normalizada, recuperação exponencial de "
        "1ª ordem na regeneração (Eq. 15.12 do livro, 16/08/2026 — eixo "
        "esquerdo). Linha tracejada: temperatura do leito (eixo direito) "
        "— sobe durante a regeneração (aquecedor, ΔT_regen) e desce no "
        "resfriamento, mesma forma exponencial por analogia física, não "
        "por uma equação própria do livro (que fecha a cinética de "
        "capacidade, não a dinâmica térmica do leito). Pressão de "
        f"entrada/saída do secador é constante no horizonte simulado: "
        f"{p_high_psa / 1e5:.2f} bar abs (alta) e {p_low_psa / 1e5:.2f} "
        "bar abs (purga, à pressão ambiente)."
    )

    st.subheader(f"Água adsorvida por torre [kg] — {material_psa}")
    fig_agua, ax_agua = plt.subplots(figsize=(9.0, 3.0))
    for i in range(n_vasos_psa):
        ax_agua.plot(r_psa["t_min"], r_psa["agua_adsorvida_kg"][i],
                    color=cores_torres[i], lw=1.6, label=f"Torre {i + 1}")
    ax_agua.axhline(_props_material["capacidade_trabalho"] * massa_leito_psa,
                    color=RED, ls=":",
                    label="Capacidade máx. (leito saturado)")
    ax_agua.set_xlabel("Tempo [min]")
    ax_agua.set_ylabel("Água adsorvida [kg]")
    ax_agua.legend(fontsize=8, ncol=min(n_vasos_psa + 1, 5), loc="upper right")
    fig_agua.tight_layout()
    st.pyplot(fig_agua)
    st.caption(
        f"Massa real de água retida no leito (Eq. 15.13 do livro, "
        "16/08/2026 — alternativa ao balanço mássico rigoroso da Eq. 15.3, "
        "útil sem sensor contínuo de W_out), não só a fração normalizada "
        f"do gráfico acima: (1 − capacidade normalizada) × capacidade de "
        f"trabalho ({_props_material['capacidade_trabalho']*100:.0f}% para "
        f"{material_psa}, Tabela 15.2) × massa do leito "
        f"({massa_leito_psa:.0f} kg/torre, aba Configurações). Zera ao fim "
        "de cada regeneração (água expulsa pelo ar de purga quente) e "
        "cresce de novo ao longo da adsorção seguinte."
    )

    st.subheader("Ponto de orvalho na saída do secador ao longo do tempo")
    fig_pdp, ax_pdp = plt.subplots(figsize=(9.0, 3.0))
    ax_pdp.plot(r_psa["t_min"], r_psa["pdp_saida_c"], color=NAVY, lw=1.6,
               label="PDP de saída (estimado)")
    ax_pdp.axhline(defaults["pdp_real_c"], color=GREEN, ls=":",
                   label=f"Alvo ISO 8573-1 Classe 2 ({defaults['pdp_real_c']:.0f} °C)")
    ax_pdp.set_xlabel("Tempo [min]")
    ax_pdp.set_ylabel("PDP de saída [°C]")
    ax_pdp.legend(fontsize=8, loc="upper right")
    fig_pdp.tight_layout()
    st.pyplot(fig_pdp)
    st.caption(
        "Simplificação de modelagem, não uma equação do livro (o Cap. 15 "
        "só fecha o KPI estático HI_des, Eq. 15.7 — não uma série temporal "
        "de PDP): a cada instante, a torre relevante é a que está "
        "adsorvendo com a menor capacidade normalizada restante — "
        "interpolação linear entre o PDP alvo (leito \"novo\") e o PDP de "
        "entrada do secador (nenhuma remoção, o mesmo limite de um "
        "*breakthrough* total ou de um intervalo sem nenhuma torre "
        "disponível). Serrilhado esperado: cada troca de torre reinicia a "
        "curva de degradação daquele leito. Pico máximo neste horizonte: "
        f"{kp['pdp_saida_max_c']:.1f} °C."
    )

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

# ===========================================================================
# Aba 4 — Gêmeo Digital (EKF/PSO)
# ===========================================================================
with tab_gd:
    st.subheader("Estimação de Estado via EKF (Eqs. 21.2, 21.4, 21.7, 21.8)")
    st.caption(
        "Estado x = [δ/L, R_f] — os dois únicos estados do vetor da Eq. 21.2 "
        "com contraparte calculável neste app (δ/L via Eq. 9.3, R_f via "
        "Eq. 10.5). Medição z = [ṁ_seco, T_HP,in], com ruído gaussiano "
        "simulado. O filtro parte sempre de uma crença de comissionamento "
        "(δ/L=0,002, R_f=0 — \"como novo\"), independente dos valores "
        "verdadeiros configurados na aba Configurações, para que a convergência "
        "abaixo seja estimação de verdade, não o filtro \"sabendo\" a resposta."
    )

    folga_true_ekf = np.linspace(folga_ini_ekf, folga_fim_ekf, n_passos_ekf)
    r_f_true_ekf = np.linspace(r_f_ini_ekf, r_f_fim_ekf, n_passos_ekf)
    r_ekf = ekf.simular_ekf(
        params_base=params,
        folga_true=folga_true_ekf,
        r_f_true=r_f_true_ekf,
        sigma_m_dot=sigma_m_dot_ekf,
        sigma_t_hp=sigma_t_hp_ekf,
        q_proc_diag=(q_folga_ekf, q_rf_ekf),
        x0=(0.002, 0.0),
        p0_diag=(1e-4, 1e-6),
    )
    passos_ekf = np.arange(n_passos_ekf)
    t_dias_ekf = passos_ekf * dt_horas_ekf / 24.0

    f1, f2 = st.columns(2)
    with f1:
        figekf1, axekf1 = plt.subplots(figsize=(6.2, 3.4))
        axekf1.plot(t_dias_ekf, r_ekf["folga_true"], color=GREEN, ls="--",
                    label="δ/L verdadeira")
        axekf1.plot(t_dias_ekf, r_ekf["x_hat"][:, 0], color=BLUE,
                    label="δ/L estimada (EKF)")
        banda_inf = r_ekf["x_hat"][:, 0] - r_ekf["std"][:, 0]
        banda_sup = r_ekf["x_hat"][:, 0] + r_ekf["std"][:, 0]
        axekf1.fill_between(t_dias_ekf, banda_inf, banda_sup, color=BLUE,
                            alpha=0.2, label="±1σ (P_k|k)")
        axekf1.set_xlabel("Tempo [dias]")
        axekf1.set_ylabel("δ/L")
        axekf1.legend(fontsize=8)
        figekf1.tight_layout()
        st.pyplot(figekf1)

    with f2:
        figekf2, axekf2 = plt.subplots(figsize=(6.2, 3.4))
        axekf2.plot(t_dias_ekf, r_ekf["r_f_true"], color=GREEN, ls="--",
                    label="R_f verdadeiro")
        axekf2.plot(t_dias_ekf, r_ekf["x_hat"][:, 1], color=BLUE,
                    label="R_f estimado (EKF)")
        banda_inf_rf = r_ekf["x_hat"][:, 1] - r_ekf["std"][:, 1]
        banda_sup_rf = r_ekf["x_hat"][:, 1] + r_ekf["std"][:, 1]
        axekf2.fill_between(t_dias_ekf, banda_inf_rf, banda_sup_rf, color=BLUE,
                            alpha=0.2, label="±1σ (P_k|k)")
        axekf2.set_xlabel("Tempo [dias]")
        axekf2.set_ylabel("R_f [m²K/W]")
        axekf2.legend(fontsize=8)
        figekf2.tight_layout()
        st.pyplot(figekf2)

    st.caption(
        f"Horizonte total simulado: {n_passos_ekf} passos × "
        f"{dt_horas_ekf:.1f} h/passo ≈ **{t_dias_ekf[-1]:.1f} dias** — a "
        "mesma escala de tempo (semanas) usada no cenário do Capítulo 29 "
        "para desgaste gradual de folga."
    )

    g1, g2, g3 = st.columns(3)
    g1.metric("δ/L estimada (final)", f"{r_ekf['x_hat'][-1, 0]:.4f}",
             help=f"Verdadeira: {r_ekf['folga_true'][-1]:.4f}")
    g2.metric("R_f estimado (final)", f"{r_ekf['x_hat'][-1, 1]:.5f}",
             help=f"Verdadeiro: {r_ekf['r_f_true'][-1]:.5f}")
    g3.metric("NIS médio (Eq. 21.7)", f"{np.mean(r_ekf['nis']):.2f}",
             help="Esperado em torno de n_z=2 (duas medições) se o filtro "
                  "estiver bem calibrado — muito acima indica modelo/Q "
                  "subestimados, muito abaixo indica filtro conservador "
                  "demais.")

    figekf3, axekf3 = plt.subplots(figsize=(9.0, 2.4))
    axekf3.plot(t_dias_ekf, r_ekf["nis"], color=NAVY, lw=1.2)
    axekf3.axhline(2.0, color=RED, ls=":", label="n_z = 2 (esperado)")
    axekf3.set_xlabel("Tempo [dias]")
    axekf3.set_ylabel("NIS")
    axekf3.legend(fontsize=8)
    figekf3.tight_layout()
    st.pyplot(figekf3)
    st.caption(
        "NIS (Normalized Innovation Squared, Eq. 21.7) audita o próprio "
        "filtro sem conhecer o estado verdadeiro — é a estatística que um "
        "Gêmeo Digital real usaria para saber se pode confiar na "
        "estimativa acima. Mesma leitura operacional do Capítulo 21: NIS "
        "consistentemente alto sinaliza Q subestimada ou modelo defasado; "
        "consistentemente baixo, filtro excessivamente conservador."
    )

    st.divider()
    st.subheader("EKF com Estado Aumentado — Calibração de K (Cap. 28, Eqs. 28.1/28.2)")
    st.caption(
        "Problema inverso resolvido online: o coeficiente de vazamento K "
        "(Eq. 9.3), fixo em todo o resto deste app, entra no próprio vetor "
        "de estado do EKF. Na janela de calibração (fundo cinza), δ/L é "
        "tratada como conhecida (Q quase nulo) para que K convirja; depois, "
        "K \"congela\" (Q pequeno) e δ/L volta a acompanhar deriva livre."
    )

    folga_true_aum = np.concatenate([
        np.full(n_cal_aum, folga_cal_aum),
        np.linspace(folga_cal_aum, folga_fim_aum, n_op_aum),
    ])
    n_total_aum = n_cal_aum + n_op_aum
    r_f_true_aum = np.zeros(n_total_aum)
    k_true_aum = np.full(n_total_aum, defaults["k_folga"])
    r_aum = ekf.simular_ekf_aumentado(
        params_base=params,
        folga_true=folga_true_aum,
        r_f_true=r_f_true_aum,
        k_true=k_true_aum,
        sigma_m_dot=sigma_m_dot_aum,
        sigma_t_hp=sigma_t_hp_ekf,
        q_proc_calibracao=(1e-10, 1e-10, 1e-5),
        q_proc_operacao=(1e-6, 1e-10, 1e-11),
        x0=(folga_cal_aum, 0.0, k_inicial_aum),
        p0_diag=(1e-10, 1e-6, 1e-3),
        n_passos_calibracao=n_cal_aum,
    )
    passos_aum = np.arange(n_total_aum)
    t_dias_aum = passos_aum * dt_horas_ekf / 24.0
    fim_cal_dias = n_cal_aum * dt_horas_ekf / 24.0

    a1, a2 = st.columns(2)
    with a1:
        figaum1, axaum1 = plt.subplots(figsize=(6.2, 3.4))
        axaum1.axvspan(0, fim_cal_dias, color="#dddddd", alpha=0.5, label="Janela de calibração")
        axaum1.axhline(defaults["k_folga"], color=GREEN, ls="--", label="K real")
        axaum1.plot(t_dias_aum, r_aum["x_hat"][:, 2], color=BLUE, label="K estimado (EKF)")
        banda_k = r_aum["std"][:, 2]
        axaum1.fill_between(t_dias_aum, r_aum["x_hat"][:, 2] - banda_k,
                            r_aum["x_hat"][:, 2] + banda_k, color=BLUE, alpha=0.2)
        axaum1.set_xlabel("Tempo [dias]")
        axaum1.set_ylabel("K (Eq. 9.3)")
        axaum1.legend(fontsize=8)
        figaum1.tight_layout()
        st.pyplot(figaum1)

    with a2:
        figaum2, axaum2 = plt.subplots(figsize=(6.2, 3.4))
        axaum2.axvspan(0, fim_cal_dias, color="#dddddd", alpha=0.5)
        axaum2.plot(t_dias_aum, r_aum["folga_true"], color=GREEN, ls="--", label="δ/L verdadeira")
        axaum2.plot(t_dias_aum, r_aum["x_hat"][:, 0], color=BLUE, label="δ/L estimada")
        axaum2.set_xlabel("Tempo [dias]")
        axaum2.set_ylabel("δ/L")
        axaum2.legend(fontsize=8)
        figaum2.tight_layout()
        st.pyplot(figaum2)

    st.caption(
        f"Δt entre medições: {dt_horas_ekf:.1f} h (mesmo valor do EKF de 2 "
        f"estados acima) — janela de calibração de {fim_cal_dias:.1f} dias, "
        f"operação acompanhada por mais {t_dias_aum[-1] - fim_cal_dias:.1f} "
        "dias depois."
    )

    b1, b2, b3 = st.columns(3)
    b1.metric("K estimado (fim da calibração)", f"{r_aum['x_hat'][n_cal_aum - 1, 2]:.4f}",
             help=f"K real: {defaults['k_folga']:.4f} — crença inicial: {k_inicial_aum:.4f}")
    b2.metric("K estimado (fim da operação)", f"{r_aum['x_hat'][-1, 2]:.4f}",
             help="Deve continuar perto do valor calibrado, mesmo com δ/L "
                  "variando livremente depois.")
    b3.metric("δ/L estimada (fim)", f"{r_aum['x_hat'][-1, 0]:.4f}",
             help=f"Verdadeira: {r_aum['folga_true'][-1]:.4f}")
    st.caption(
        "Tabela 28.1 do livro (Seção 28.2): antes desta calibração, K estava "
        "na categoria (iv) — desconhecido/valor de catálogo. Depois, passa "
        "para a categoria (iii) — calibrável na janela saudável — com a "
        "proveniência explícita registrada, em vez de herdado implicitamente."
    )

    st.divider()
    st.subheader("Otimização de Setpoint via PSO (Eqs. 24.3/24.4)")
    st.caption(
        "Minimiza o SPC (Eq. 11.11) variando a pressão de setpoint da rede "
        "π, sujeito a manter a autonomia do vaso (Eq. 16.5) acima do "
        "mínimo definido na aba Configurações — restrição imposta por "
        "penalidade, já que o PSO básico não trata restrições nativamente."
    )

    if st.button("🔄 Rodar PSO"):
        def _custo_pso(x: np.ndarray) -> float:
            pi_cand = float(x[0])
            r_cand = simular({**params, "pi_total": pi_cand})
            spc_cand = r_cand["kpis"]["spc"]
            autonomia_cand = r_cand["kpis"]["autonomia_min"]
            penalidade = 0.0
            if np.isfinite(autonomia_cand) and autonomia_cand < autonomia_min_pso:
                penalidade = 1e3 * (autonomia_min_pso - autonomia_cand)
            return spc_cand + penalidade

        st.session_state["r_pso"] = pso.otimizar(
            _custo_pso, limite_inf=[5.0], limite_sup=[12.0],
            n_particulas=n_particulas_pso, n_iter=n_iter_pso,
            w_ini=w_ini_pso, w_fim=w_fim_pso, c1=c1_pso, c2=c2_pso)

    if "r_pso" in st.session_state:
        r_pso = st.session_state["r_pso"]
        pi_otimo = float(r_pso["g_best"][0])
        res_otimo = simular({**params, "pi_total": pi_otimo})

        p1, p2, p3 = st.columns(3)
        p1.metric("π ótimo encontrado", f"{pi_otimo:.2f} bar abs")
        p2.metric("SPC no ótimo", f"{res_otimo['kpis']['spc']:.2f} kW·min/m³",
                 help=f"SPC no π atual da barra lateral: {k['spc']:.2f} "
                      "kW·min/m³")
        p3.metric("Autonomia no ótimo",
                 f"{res_otimo['kpis']['autonomia_min']:.1f} min"
                 if np.isfinite(res_otimo["kpis"]["autonomia_min"])
                 else "∞ (sem demanda)")

        figpso, axpso = plt.subplots(figsize=(9.0, 2.8))
        axpso.plot(r_pso["historico_custo"], color=BLUE, lw=1.6)
        axpso.set_xlabel("Iteração")
        axpso.set_ylabel("Custo de g_best (SPC + penalidade)")
        figpso.tight_layout()
        st.pyplot(figpso)
        st.caption(
            "Convergência do enxame: o custo de g_best nunca piora entre "
            "iterações (Eqs. 24.3/24.4 só atualizam g_best quando a nova "
            "posição é melhor). Sem restrição de autonomia ativa, o "
            "mínimo tende à menor pressão pesquisada — SPC cresce com π "
            "pela mesma \"regra dos 7 %/bar\" já discutida no Capítulo de "
            "Trem de Potência; é a restrição de autonomia mínima que "
            "impede o otimizador de simplesmente zerar o setpoint."
        )
    else:
        st.info("Clique em \"Rodar PSO\" para otimizar — não roda "
                "automaticamente a cada mudança de slider, por ser mais "
                "custoso que o resto do app.")

    st.divider()
    st.subheader("Detecção de Anomalia via VAE (Eqs. 20.4, 22.1-22.7)")
    st.caption(
        "Autoencoder variacional treinado sobre pontos de operação "
        "saudáveis sintéticos (não há dado real de planta neste "
        "projeto). O erro de reconstrução E_rec funciona como sensor "
        "virtual de anomalia — o limiar de disparo (Eq. 22.6) é "
        "calibrado estatisticamente sobre um conjunto de validação "
        "saudável, não escolhido à mão."
    )

    @st.cache_resource(show_spinner="Treinando VAE...")
    def _treinar_vae_cache(_params_base, chave, n_amostras, n_epocas):
        ds_treino = vae.gerar_dataset_saudavel(n_amostras, _params_base, seed=0)
        ds_val = vae.gerar_dataset_saudavel(max(80, n_amostras // 3), _params_base, seed=1)
        info_treinado = vae.treinar(ds_treino, n_epocas=n_epocas)
        limiar_calibrado = vae.calibrar_limiar(info_treinado, ds_val, n_desvios=3.0)
        e_val_calc = vae.erro_reconstrucao(info_treinado, ds_val)
        return info_treinado, limiar_calibrado, e_val_calc

    chave_vae = (round(params["t_amb"], 1), round(params["pi_total"], 2),
                round(params["fad_m3_min"], 2), n_amostras_vae, n_epocas_vae)
    info_vae, limiar_vae, e_val_vae = _treinar_vae_cache(
        params, chave_vae, n_amostras_vae, n_epocas_vae)

    feat_saudavel = vae.extrair_features(res)[None, :]
    e_saudavel = float(vae.erro_reconstrucao(info_vae, feat_saudavel)[0])
    p_cenario_vae = {**params, "folga_rel": folga_cenario_vae}
    feat_cenario = vae.extrair_features(simular(p_cenario_vae))[None, :]
    e_cenario = float(vae.erro_reconstrucao(info_vae, feat_cenario)[0])

    v1, v2, v3 = st.columns(3)
    v1.metric("E_rec — ponto de operação atual", f"{e_saudavel:.2f}")
    v2.metric(f"E_rec — cenário δ/L={folga_cenario_vae:.4f}", f"{e_cenario:.2f}",
             delta=f"{e_cenario - limiar_vae:+.2f} vs. limiar")
    v3.metric("Limiar de disparo (Eq. 22.6)", f"{limiar_vae:.2f}")
    if e_cenario > limiar_vae:
        st.warning(f"Cenário de teste classificado como **anômalo** — "
                   f"E_rec ({e_cenario:.2f}) > limiar ({limiar_vae:.2f}).")
    else:
        st.success(f"Cenário de teste dentro do esperado — "
                   f"E_rec ({e_cenario:.2f}) ≤ limiar ({limiar_vae:.2f}).")

    figvae, (axv1, axv2) = plt.subplots(1, 2, figsize=(12.4, 3.2))
    axv1.plot(info_vae["historico_loss"], color=BLUE)
    axv1.set_xlabel("Época")
    axv1.set_ylabel("Perda (ELBO)")
    axv1.set_title("Convergência do treino", fontsize=10)

    axv2.hist(e_val_vae, bins=20, color=BLUE, alpha=0.6,
             label="E_rec (validação saudável)")
    axv2.axvline(limiar_vae, color=RED, ls="--", label="limiar")
    axv2.axvline(e_cenario, color=GREEN, ls="-", label="cenário de teste")
    axv2.set_xlabel("E_rec")
    axv2.set_ylabel("Contagem")
    axv2.legend(fontsize=7)
    axv2.set_title("Distribuição saudável vs. cenário", fontsize=10)
    figvae.tight_layout()
    st.pyplot(figvae)
    st.caption(
        "Nenhuma das 12 variáveis de entrada precisa isoladamente cruzar "
        "um limiar próprio para o VAE sinalizar — é a combinação "
        "conjunta que se afasta da distribuição aprendida na operação "
        "saudável (a mesma lógica do achado que motivou o Capítulo 28 "
        "do livro)."
    )

    st.divider()
    st.subheader("Modelo Substituto PIML (Eqs. 23.1-23.4)")
    st.caption(
        "Rede treinada para prever T_LP,out, T_HP,in, ṁ_seco e "
        "Q̇_intercooler a partir do ponto de operação, com um resíduo "
        "físico (balanço de energia do intercooler, Eq. 10.1) penalizado "
        "em pontos de colocação sem rótulo — inclusive fora da faixa "
        "rotulada de treino."
    )

    _FAIXAS_PIML_APP = {
        "pi_total": (6.0, 10.0), "t_amb_c": (10.0, 40.0),
        "folga_rel": (0.001, 0.02), "r_f_equiv": (0.0, 5e-4),
        "fad_m3_min": (8.0, 12.0),
    }

    @st.cache_resource(show_spinner="Treinando o substituto PIML...")
    def _treinar_piml_cache(_params_base, chave, n_amostras, n_epocas):
        entradas_tr, saidas_tr = piml.gerar_dataset(
            n_amostras, _params_base, _FAIXAS_PIML_APP, seed=0)
        info_treinado = piml.treinar(entradas_tr, saidas_tr, _FAIXAS_PIML_APP,
                                     n_epocas=n_epocas, lr=1e-2)
        entradas_tst, saidas_tst = piml.gerar_dataset(
            max(20, n_amostras // 10), _params_base, _FAIXAS_PIML_APP, seed=99)
        return info_treinado, entradas_tst, saidas_tst

    chave_piml = (round(params["t_amb"], 1), n_amostras_piml, n_epocas_piml)
    info_piml, entradas_teste_piml, saidas_teste_piml = _treinar_piml_cache(
        params, chave_piml, n_amostras_piml, n_epocas_piml)

    pred_piml = piml.prever(info_piml, entradas_teste_piml)
    erro_piml = np.abs(pred_piml - saidas_teste_piml).mean(axis=0)
    residuo_piml = piml.residuo_fisico_real(info_piml, entradas_teste_piml)

    pi1, pi2, pi3 = st.columns(3)
    pi1.metric("Erro médio T_LP,out", f"{erro_piml[0]:.2f} °C")
    pi2.metric("Erro médio ṁ_seco", f"{erro_piml[2] * 1000:.2f} g/s")
    pi3.metric("Resíduo físico médio |F|", f"{np.abs(residuo_piml).mean():.1f} W",
              help="O livro é explícito (Cap. 23, \"Limitações e "
                   "Cautelas\") que essa penalização é fraca, não uma "
                   "garantia — o resíduo deve ser medido, não presumido "
                   "nulo.")

    figpiml, (axp1, axp2) = plt.subplots(1, 2, figsize=(12.4, 3.2))
    axp1.plot(info_piml["hist_data"], color=BLUE, label="L_data")
    axp1.plot(info_piml["hist_fisica"], color=RED, label="L_physics")
    axp1.set_yscale("log")
    axp1.set_xlabel("Época")
    axp1.set_ylabel("Perda (escala log)")
    axp1.legend(fontsize=8)
    axp1.set_title("Convergência das duas perdas", fontsize=10)

    axp2.plot(info_piml["hist_lambda"], color=NAVY)
    axp2.set_xlabel("Época")
    axp2.set_ylabel("λ")
    axp2.set_title("Balanceamento adaptativo de λ (Eq. 23.4)", fontsize=10)
    figpiml.tight_layout()
    st.pyplot(figpiml)
    st.caption(
        "λ parte de 0,1 e se ajusta pela razão entre as magnitudes dos "
        "gradientes de L_data e L_physics — sem essa normalização, o "
        "resíduo físico (medido em watts, ordens de grandeza acima do "
        "erro de dados já padronizado) satura a rede logo no 1º passo de "
        "treino (ver CONTEXTO_app.md para o diagnóstico completo)."
    )

    st.divider()
    st.subheader("PIML — Identificação por Problema Inverso (Cap. 23.8, Eq. 23.5)")
    st.caption(
        "Em vez do resíduo de energia do intercooler acima, aqui o resíduo "
        "físico é a Equação 9.3 (balanço mássico), e o coeficiente de "
        "vazamento Ξ é otimizado junto aos pesos da rede — não fixo em "
        "`params_base`. Mesmo mecanismo de identificação da Seção 28.1 do "
        "livro (EKF aumentado), por um caminho offline: um treino em lote "
        "sobre dados dispersos, em vez de um ciclo sequencial online."
    )

    @st.cache_resource(show_spinner="Identificando Ξ via problema inverso...")
    def _treinar_piml_inv_cache(_params_base, chave, n_amostras, n_epocas, xi0):
        entradas_tr, saidas_tr = piml.gerar_dataset(
            n_amostras, _params_base, _FAIXAS_PIML_APP, seed=0)
        return piml.treinar_com_identificacao(
            entradas_tr, saidas_tr, _FAIXAS_PIML_APP, params_base=_params_base,
            xi_inicial=xi0, n_epocas=n_epocas, lr=1e-2)

    chave_piml_inv = (round(params["t_amb"], 1), n_amostras_piml_inv,
                      n_epocas_piml_inv, xi_inicial_piml)
    info_piml_inv = _treinar_piml_inv_cache(
        params, chave_piml_inv, n_amostras_piml_inv, n_epocas_piml_inv, xi_inicial_piml)

    pv1, pv2, pv3 = st.columns(3)
    pv1.metric("Ξ estimado", f"{info_piml_inv['xi_estimado']:.4f}",
              help=f"K real usado no restante do app: {defaults['k_folga']:.4f}")
    pv2.metric("Crença inicial de Ξ", f"{xi_inicial_piml:.4f}")
    pv3.metric("Erro |Ξ_estimado − K_real|",
              f"{abs(info_piml_inv['xi_estimado'] - defaults['k_folga']):.4f}")

    figpimlinv, axpi = plt.subplots(figsize=(9.0, 2.8))
    axpi.axhline(defaults["k_folga"], color=GREEN, ls="--", label="K real")
    axpi.axhline(xi_inicial_piml, color="#999999", ls=":", label="Ξ inicial")
    axpi.plot(info_piml_inv["hist_xi"], color=BLUE, label="Ξ (durante o treino)")
    axpi.set_xlabel("Época")
    axpi.set_ylabel("Ξ")
    axpi.legend(fontsize=8)
    figpimlinv.tight_layout()
    st.pyplot(figpimlinv)
    st.caption(
        "O efeito de K/Ξ na Equação 9.3 é pequeno frente às demais "
        "variações do ponto de operação — identificação por problema "
        "inverso é um problema mais mal-condicionado que o EKF sequencial "
        "acima, e a estimativa converge para perto do valor real, mas com "
        "ruído residual maior. Reduzir o ruído sintético de rotulagem ou "
        "aumentar a faixa de δ/L amostrada (barra lateral) melhora a "
        "identificação, pelo mesmo motivo do slider de δ/L de calibração "
        "do EKF aumentado acima."
    )

    st.divider()
    st.subheader("Calibração em Lote via Levenberg-Marquardt (Cap. 28.1, scipy)")
    st.caption(
        "Terceiro caminho para o mesmo K — sem filtro, sem rede neural: "
        "mínimos quadrados não lineares em lote (`scipy.optimize."
        "least_squares(method='lm')`), direto contra o modelo físico "
        "`sistema.simular()`, pelos mesmos dois canais do EKF aumentado "
        "(ṁ_seco, T_HP,in). Viável aqui porque a incógnita é só K — 1 "
        "parâmetro; inviável para o PIML acima, cujas incógnitas são os "
        "pesos da rede inteira, não 1 escalar."
    )

    @st.cache_resource(show_spinner="Calibrando K via Levenberg-Marquardt...")
    def _calibrar_lm_cache(_params_base, chave, n_amostras, k0, sigma_m, sigma_t):
        entradas_lm, saidas4_lm = piml.gerar_dataset(
            n_amostras, _params_base, _FAIXAS_PIML_APP, seed=7)
        saidas2_lm = saidas4_lm[:, [2, 1]]  # [m_dot_seco, t_hp_in]
        rng_lm = np.random.default_rng(11)
        ruido_lm = np.stack([
            rng_lm.normal(0.0, sigma_m, size=len(saidas2_lm)),
            rng_lm.normal(0.0, sigma_t, size=len(saidas2_lm)),
        ], axis=1)
        return calib_lm.calibrar_k_lm(
            entradas_lm, saidas2_lm + ruido_lm, _params_base, k_inicial=k0)

    chave_lm = (round(params["t_amb"], 1), n_amostras_lm, k_inicial_lm,
               sigma_m_dot_lm, sigma_t_hp_lm)
    info_lm = _calibrar_lm_cache(
        params, chave_lm, n_amostras_lm, k_inicial_lm, sigma_m_dot_lm, sigma_t_hp_lm)

    lm1, lm2, lm3, lm4 = st.columns(4)
    lm1.metric("K estimado", f"{info_lm['k_estimado']:.4f}",
              help=f"K real usado no restante do app: {defaults['k_folga']:.4f}")
    lm2.metric("Erro |K_estimado − K_real|",
              f"{abs(info_lm['k_estimado'] - defaults['k_folga']):.4f}")
    lm3.metric("Avaliações do modelo físico", info_lm["n_avaliacoes"])
    lm4.metric("Convergiu?", "Sim" if info_lm["sucesso"] else "Não")
    st.caption(
        f"scipy: \"{info_lm['mensagem']}\" — compare o número de avaliações "
        "acima contra épocas × amostras dos dois treinos PIML mais acima: "
        "para 1 parâmetro só, LM converge em poucas dezenas de avaliações "
        "do modelo físico, ordens de grandeza mais barato que treinar uma "
        "rede — o preço é não escalar: o mesmo método não serve para "
        "calibrar os pesos de uma rede neural."
    )

    st.divider()
    st.subheader("MPC vs. Controle Reativo (Eqs. 24.1/24.2)")

    rho_amb_gd = nucleo.densidade_ar(params["p_amb"], params["t_amb"])
    dem_base_mpc = rho_amb_gd * demanda_base_mpc / 60.0
    m_dot_cap_gd = res["nos"][-1]["m_dot"] * pw["n_compressores"]
    p_set_mpc = params["p_amb"] * params["pi_total"]
    hor_s_mpc = horizonte_mpc * 60.0
    t_ev_mpc = (0.4 * hor_s_mpc, 0.65 * hor_s_mpc)

    r_mpc = mpc.simular_mpc(
        horizonte_min=horizonte_mpc, dt=dt_mpc, n_horizonte=n_horizonte_mpc,
        m_dot_cap=m_dot_cap_gd, v_vaso=params["v_vaso"], t_k=params["t_amb"],
        p_set=p_set_mpc, dem_base=dem_base_mpc, t_ev=t_ev_mpc,
        fator_ev=fator_ev_mpc, rho=rho_mpc, x_c_min=dinamica.X_C_MIN,
        w_nom=pw["w_total_planta"], eta_vsd=dinamica.ETA_VSD)
    r_reativo_mpc = dinamica.simular_transiente(
        horizonte_min=horizonte_mpc, m_dot_cap=m_dot_cap_gd,
        w_nom=pw["w_total_planta"], v_vaso=params["v_vaso"],
        t_k=params["t_amb"], p_set=p_set_mpc, p_limite=params["p_limite"],
        dem_base=dem_base_mpc, t_ev=t_ev_mpc, fator_ev=fator_ev_mpc,
        modo="VSD", dp_db=0.5e5)

    p_ref_bar_mpc = p_set_mpc / 1e5
    desvio_mpc = float(np.mean(np.abs(r_mpc["p_bar"] - p_ref_bar_mpc)))
    desvio_reativo = float(np.mean(np.abs(r_reativo_mpc["p_bar"] - p_ref_bar_mpc)))

    mm1, mm2, mm3 = st.columns(3)
    mm1.metric("Desvio médio — MPC", f"{desvio_mpc * 1000:.1f} mbar")
    mm2.metric("Desvio médio — reativo (VSD)", f"{desvio_reativo * 1000:.1f} mbar")
    melhora_mpc = (1.0 - desvio_mpc / desvio_reativo) * 100.0 if desvio_reativo > 0 else 0.0
    mm3.metric("Melhora do MPC", f"{melhora_mpc:.0f} %")

    figmpc, axmpc = plt.subplots(figsize=(9.0, 3.4))
    axmpc.plot(r_mpc["t_min"], r_mpc["p_bar"], color=BLUE, label="MPC (antecipa)")
    axmpc.plot(r_reativo_mpc["t_min"], r_reativo_mpc["p_bar"], color=RED, ls="--",
              label="Reativo (rampa 1ª ordem)")
    axmpc.axhline(p_ref_bar_mpc, color=GREEN, ls=":", label="Referência")
    axmpc.set_xlabel("Tempo [min]")
    axmpc.set_ylabel("Pressão da rede [bar abs]")
    axmpc.legend(fontsize=8)
    figmpc.tight_layout()
    st.pyplot(figmpc)
    st.caption(
        "Mesmo evento de demanda, dois controladores: o reativo (mesmo da "
        "aba \"Dinâmica temporal\") só responde à demanda do instante "
        "atual; o MPC otimiza a sequência de x_c ao longo do horizonte H "
        "com a demanda futura conhecida (Eq. 24.1) e por isso antecipa o "
        "evento em vez de correr atrás dele. Demanda base mantida com "
        "folga (aba Configurações) — perto da capacidade máxima, qualquer "
        "controlador satura igualmente e a comparação perde sentido."
    )

# ===========================================================================
# Aba "Dados Medidos" — inventário de instrumentação real da planta
# ===========================================================================
with tab_dados:
    st.subheader("Inventário de instrumentação medida")
    st.caption(
        "Envie a planilha de instrumentação da sua instalação — pontos "
        "efetivamente medidos em campo — para comparar contra a matriz de "
        "referência do livro (Tabela 18.1): mostra quais dos 9 pontos "
        "padrão (A-I) já têm sensor físico nesta planta e quais dependem "
        "de inferência por modelo (soft-sensor). Este upload é só "
        "referência/documentação — não altera a simulação nas outras abas."
    )

    _REFERENCIA_TAB18_1 = [
        {"Ponto": "A", "Localização": "MCC / Relé", "Variável": "Tensão de Linha", "Tag": "V_L", "Unidade": "V"},
        {"Ponto": "A", "Localização": "MCC / Relé", "Variável": "Corrente de Fase", "Tag": "I", "Unidade": "A"},
        {"Ponto": "A", "Localização": "MCC / Relé", "Variável": "Frequência", "Tag": "f", "Unidade": "Hz"},
        {"Ponto": "A", "Localização": "MCC / Relé", "Variável": "Fator de Potência", "Tag": "cos φ", "Unidade": "-"},
        {"Ponto": "B", "Localização": "Transmissão", "Variável": "Velocidade Angular", "Tag": "ω", "Unidade": "rad/s"},
        {"Ponto": "B", "Localização": "Transmissão", "Variável": "Torque no Eixo", "Tag": "τ", "Unidade": "N·m"},
        {"Ponto": "B", "Localização": "Transmissão", "Variável": "Vibração Global", "Tag": "v_rms", "Unidade": "mm/s"},
        {"Ponto": "B", "Localização": "Transmissão", "Variável": "Tensão no Dente", "Tag": "σ_b", "Unidade": "MPa"},
        {"Ponto": "C", "Localização": "Estágio LP", "Variável": "Pressão Sucção", "Tag": "P_s,lp", "Unidade": "bar"},
        {"Ponto": "C", "Localização": "Estágio LP", "Variável": "Temp. Descarga", "Tag": "T_d,lp", "Unidade": "°C"},
        {"Ponto": "C", "Localização": "Estágio LP", "Variável": "Folga Interna", "Tag": "δ_lp", "Unidade": "μm"},
        {"Ponto": "D", "Localização": "Intercooler", "Variável": "Temp. Água In", "Tag": "T_w,in", "Unidade": "°C"},
        {"Ponto": "D", "Localização": "Intercooler", "Variável": "Delta Pressão", "Tag": "ΔP_ic", "Unidade": "bar"},
        {"Ponto": "D", "Localização": "Intercooler", "Variável": "Vazão Condensado", "Tag": "ṁ_c", "Unidade": "kg/h"},
        {"Ponto": "E", "Localização": "Estágio HP", "Variável": "Pressão Descarga", "Tag": "P_d,hp", "Unidade": "bar"},
        {"Ponto": "E", "Localização": "Estágio HP", "Variável": "Temp. Descarga", "Tag": "T_d,hp", "Unidade": "°C"},
        {"Ponto": "E", "Localização": "Estágio HP", "Variável": "Folga Interna", "Tag": "δ_hp", "Unidade": "μm"},
        {"Ponto": "E", "Localização": "Estágio HP", "Variável": "Posição Axial", "Tag": "δ_ax", "Unidade": "μm"},
        {"Ponto": "F", "Localização": "Aftercooler", "Variável": "Temp. Saída", "Tag": "T_ac,out", "Unidade": "°C"},
        {"Ponto": "G", "Localização": "Secador PSA", "Variável": "Ponto de Orvalho", "Tag": "T_dp", "Unidade": "°C"},
        {"Ponto": "G", "Localização": "Secador PSA", "Variável": "Vazão de Purga", "Tag": "ṁ_p", "Unidade": "kg/s"},
        {"Ponto": "H", "Localização": "Vaso Pulmão", "Variável": "Pressão Vaso", "Tag": "P_tk", "Unidade": "bar"},
        {"Ponto": "H", "Localização": "Vaso Pulmão", "Variável": "Nível Condensado", "Tag": "L_tk", "Unidade": "%"},
        {"Ponto": "I", "Localização": "Header", "Variável": "Vazão de Demanda", "Tag": "ṁ_tot", "Unidade": "kg/s"},
        {"Ponto": "I", "Localização": "Header", "Variável": "Status Ramal", "Tag": "δ_i", "Unidade": "bin"},
    ]

    with st.expander("Matriz de referência do livro — Tabela 18.1 (9 pontos, A-I)"):
        st.dataframe(_REFERENCIA_TAB18_1, width="stretch", hide_index=True)

    _exemplo_path = Path(__file__).parent / "exemplos" / "instrumentacao_exemplo.csv"
    if _exemplo_path.exists():
        st.download_button(
            "⬇️ Baixar exemplo (.csv, os 9 pontos da Tabela 18.1)",
            data=_exemplo_path.read_bytes(),
            file_name="instrumentacao_exemplo.csv",
            mime="text/csv",
            help="Mesmo arquivo em aplicativo/exemplos/ — baixe, apague as "
                 "linhas que não se aplicam à sua planta e reenvie abaixo "
                 "para ver a comparação de cobertura.")

    arquivo_medidas = st.file_uploader(
        "Planilha de instrumentação desta planta (.xlsx ou .csv)",
        type=["xlsx", "csv"],
        help="Colunas esperadas: Ponto, Localização, Variável, Tag, Unidade "
             "(Função é opcional) — mesmo layout da Tabela 18.1 do livro.")

    if arquivo_medidas is not None:
        df_medidas = None
        try:
            if arquivo_medidas.name.lower().endswith(".csv"):
                df_medidas = pd.read_csv(arquivo_medidas)
            else:
                df_medidas = pd.read_excel(arquivo_medidas)
        except Exception as e:
            st.error(f"Não foi possível ler o arquivo: {e}")

        if df_medidas is not None:
            st.subheader(f"{len(df_medidas)} variáveis carregadas")
            st.dataframe(df_medidas, width="stretch", hide_index=True)

            colunas_norm = {str(c).strip().lower(): c for c in df_medidas.columns}
            col_ponto = colunas_norm.get("ponto")
            if col_ponto is not None:
                pontos_cobertos = {
                    str(p).strip().upper() for p in df_medidas[col_ponto].dropna()}
                pontos_ref = "ABCDEFGHI"
                faltando = [p for p in pontos_ref if p not in pontos_cobertos]

                cob1, cob2 = st.columns(2)
                cob1.metric("Pontos cobertos",
                           f"{len(set(pontos_ref) & pontos_cobertos)}/9")
                cob2.metric("Pontos sem sensor nesta planilha", len(faltando))

                if faltando:
                    st.warning(
                        "Sem cobertura nesta planilha: " + ", ".join(faltando) +
                        " — o Gêmeo Digital depende de inferência por modelo "
                        "(soft-sensor) nesses pontos, não de leitura direta "
                        "(mesma lógica de lacunas de observabilidade da "
                        "Tabela 18.1 do livro).")
                else:
                    st.success(
                        "Todos os 9 pontos de referência (A-I) têm ao menos "
                        "uma variável coberta nesta planilha.")
            else:
                st.info(
                    "Coluna \"Ponto\" não encontrada — mostrando a planilha "
                    "como enviada, sem comparação de cobertura contra a "
                    "Tabela 18.1.")
