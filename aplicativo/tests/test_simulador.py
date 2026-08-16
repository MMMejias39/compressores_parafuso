"""Testes de sanidade do simulador.

Rodar a partir do diretório `aplicativo/`:

    venv/bin/pytest tests/
"""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compressor_sim import (
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


# --- Núcleo ----------------------------------------------------------------

def test_razao_pressao_interna():
    # π_i = V_i^n com V_i = 4,0 e n = 1,35 (figura 5.1 / Eq. 13.9)
    assert nucleo.razao_pressao_interna(4.0, 1.35) == pytest.approx(4.0**1.35)


def test_minimo_curva_v_em_pi_i():
    p1, v_dot2, v_i, n = 1e5, 0.15, 4.0, 1.35
    pi_i = nucleo.razao_pressao_interna(v_i, n)
    perda_min = nucleo.perda_vi(p1, v_dot2, pi_i, v_i, n)
    assert perda_min == pytest.approx(0.0, abs=1e-6)
    for pi in (0.7 * pi_i, 1.3 * pi_i):
        assert nucleo.perda_vi(p1, v_dot2, pi, v_i, n) > perda_min


def test_potencia_cresce_com_pi():
    p1, v_dot, n, eta = 1e5, 0.15, 1.35, 0.96
    w = [nucleo.potencia_politropica(p1, v_dot, pi, n, eta)
         for pi in (2.0, 3.0, 4.0)]
    assert w[0] < w[1] < w[2]


def test_temperatura_descarga_coerente():
    # T_out = T_in·π^((n-1)/n) — Eq. 11.1
    assert nucleo.temperatura_descarga(300.0, 2.83, 1.35) == pytest.approx(
        300.0 * 2.83 ** (0.35 / 1.35))


def test_q_int_carcaca_proporcional_a_perda_mecanica():
    # Q_int = W·(1 − η_mec) — proxy da perda mecânica conduzida à carcaça (Eq. 9.6)
    assert nucleo.q_int_carcaca(1000.0, 0.96) == pytest.approx(40.0)
    assert nucleo.q_int_carcaca(1000.0, 1.0) == pytest.approx(0.0)


def test_temperatura_carcaca_regime_sem_calor_fica_no_ambiente():
    t_amb = 303.15
    assert nucleo.temperatura_carcaca_regime(0.0, 10.0, 20.0, t_amb) == pytest.approx(t_amb)


def test_temperatura_carcaca_regime_cresce_com_q_int_e_cai_com_condutancia():
    t_amb = 303.15
    t_baixo = nucleo.temperatura_carcaca_regime(500.0, 10.0, 20.0, t_amb)
    t_alto = nucleo.temperatura_carcaca_regime(1500.0, 10.0, 20.0, t_amb)
    assert t_alto > t_baixo > t_amb
    # mais condutância (melhor arrefecimento) -> carcaça mais fria para o mesmo Q_int
    t_mais_arrefecida = nucleo.temperatura_carcaca_regime(500.0, 10.0, 60.0, t_amb)
    assert t_mais_arrefecida < t_baixo


def test_temperatura_carcaca_transiente_converge_para_regime():
    t_amb, q_int, cond_ext, cond_arref = 303.15, 800.0, 10.0, 20.0
    t_ss = nucleo.temperatura_carcaca_regime(q_int, cond_ext, cond_arref, t_amb)
    tau = nucleo.constante_tempo_carcaca(300.0, 460.0, cond_ext, cond_arref)
    # em t=0, T_c(t) = T_c0 (condição inicial), não o regime
    t0 = nucleo.temperatura_carcaca(t_amb, t_amb, q_int, cond_ext, cond_arref,
                                    300.0, 460.0, 0.0)
    assert t0 == pytest.approx(t_amb)
    # em t >> τ, converge para o regime permanente
    t_longo = nucleo.temperatura_carcaca(t_amb, t_amb, q_int, cond_ext, cond_arref,
                                         300.0, 460.0, 20.0 * tau)
    assert t_longo == pytest.approx(t_ss, abs=1e-3)


def test_potencia_entreferro_e_perdas_motor():
    # Eq. 4.12 invertida: P_ag = P_eixo/(1-s)
    p_ag = nucleo.potencia_entreferro(1000.0, 0.02)
    assert p_ag == pytest.approx(1000.0 / 0.98)
    # Eq. 4.11: perdas = s·P_ag + P_fixas
    perdas = nucleo.perdas_motor(0.02, p_ag, 100.0)
    assert perdas == pytest.approx(0.02 * p_ag + 100.0)
    # Eq. 4.12: eta_mot = P_eixo/(P_ag+P_fixas); consistência: perdas = P_eletrica - P_eixo
    eta = nucleo.eficiencia_motor(1000.0, p_ag, 100.0)
    p_eletrica = p_ag + 100.0
    assert eta == pytest.approx(1000.0 / p_eletrica)
    assert perdas == pytest.approx(p_eletrica - 1000.0, abs=1e-6)


def test_temperatura_hood_regime_sem_ventilacao_fica_no_ambiente():
    assert nucleo.temperatura_hood_regime(1000.0, 0.0, 1005.0, 303.15) == pytest.approx(303.15)


def test_temperatura_hood_regime_cresce_com_calor_gerado():
    t_amb = 303.15
    t_baixo = nucleo.temperatura_hood_regime(2000.0, 0.5, 1005.0, t_amb)
    t_alto = nucleo.temperatura_hood_regime(6000.0, 0.5, 1005.0, t_amb)
    assert t_alto > t_baixo > t_amb


def test_delta_p_linha_cresce_com_atrito_e_comprimento():
    dp1 = nucleo.delta_p_linha(0.02, 3.0, 0.10, 2.5, 10.0)
    dp2 = nucleo.delta_p_linha(0.04, 3.0, 0.10, 2.5, 10.0)  # mais atrito
    dp3 = nucleo.delta_p_linha(0.02, 6.0, 0.10, 2.5, 10.0)  # linha mais longa
    assert dp2 > dp1 > 0.0
    assert dp3 > dp1


def test_psicrometria():
    # P_sat a 25 °C ≈ 3,17 kPa (Buck, Eq. 10.7)
    assert nucleo.p_sat(298.15) == pytest.approx(3169, rel=0.02)
    # Ar saturado: W > 0; ar seco: W = 0
    assert nucleo.razao_umidade(303.15, 101325.0, 1.0) > 0.0
    assert nucleo.razao_umidade(303.15, 101325.0, 0.0) == 0.0
    # condensado nunca negativo (Eqs. 10.6/14.3)
    assert nucleo.condensado(1.0, 0.010, 0.020) == 0.0


@pytest.mark.parametrize("t_c", [-40.0, -20.0, 0.0, 10.0, 25.0, 40.0])
def test_temp_orvalho_inverte_p_sat_exatamente(t_c):
    # temp_orvalho_c(p_sat(T)) deve recuperar o próprio T — inversa numérica
    # da Eq. 10.7 (bisseção), sem fórmula aproximada não citada no livro
    pv = nucleo.p_sat(t_c + 273.15)
    assert nucleo.temp_orvalho_c(pv) == pytest.approx(t_c, abs=1e-3)


def test_temp_orvalho_de_w_igual_a_t_quando_saturado():
    # ar saturado (UR=100%) tem, por definição, PDP igual à própria temperatura
    t_k, p = 298.15, 8e5
    w_sat = nucleo.razao_umidade(t_k, p, 1.0)
    assert nucleo.temp_orvalho_de_w(w_sat, p) == pytest.approx(t_k - 273.15, abs=1e-2)


def test_temp_orvalho_sobe_com_pressao_a_w_constante():
    # comprimir sem remover água concentra o vapor -> PDP sobe (fenômeno
    # básico de ar comprimido, é por isso que ele condensa ao esfriar depois)
    w = 0.02
    pdp_baixa_p = nucleo.temp_orvalho_de_w(w, 1e5)
    pdp_alta_p = nucleo.temp_orvalho_de_w(w, 8e5)
    assert pdp_alta_p > pdp_baixa_p


# --- Subsistemas -------------------------------------------------------------

def test_lmtd_maior_ou_igual_media_para_contracorrente():
    # LMTD ≤ média aritmética das diferenças extremas (propriedade da média log)
    dt1, dt2 = 40.0, 20.0
    lm = subsistemas.lmtd(dt1, dt2)
    assert dt2 < lm < dt1
    assert lm <= (dt1 + dt2) / 2.0 + 1e-9


def test_eps_ntu_limites():
    for ntu, c_r in [(0.0, 0.5), (1.0, 0.3), (5.0, 0.9)]:
        eps = subsistemas.eps_ntu_contracorrente(ntu, c_r)
        assert 0.0 <= eps <= 1.0
    assert subsistemas.eps_ntu_contracorrente(0.0, 0.5) == 0.0


def test_fouling_degrada_ua():
    ua_limpo = subsistemas.ua_com_fouling(4000.0, 0.0)
    ua_sujo = subsistemas.ua_com_fouling(4000.0, 1e-4)
    assert ua_sujo < ua_limpo


def test_purga_entre_10_e_18_pct_default():
    par = parametros_default()
    assert 0.10 <= par["fator_purga"] <= 0.18  # :1971


def test_sec_dry_soma_aquecedor_e_tambor():
    assert subsistemas.sec_dry(1000.0, 0.0, 0.5) == pytest.approx(2000.0)
    assert subsistemas.sec_dry(1000.0, 500.0, 0.5) == pytest.approx(3000.0)


def test_hi_des_unitario_no_nominal():
    # ΔP e PDP reais iguais ao nominal/alvo => leito saudável, HI_des = 1
    assert subsistemas.hi_des(0.3e5, 0.3e5, -40.0, -40.0) == pytest.approx(1.0)


def test_hi_des_cai_com_degradacao():
    saudavel = subsistemas.hi_des(0.3e5, 0.3e5, -40.0, -40.0)
    dp_alto = subsistemas.hi_des(0.3e5, 0.6e5, -40.0, -40.0)
    pdp_pior = subsistemas.hi_des(0.3e5, 0.3e5, -40.0, -20.0)
    assert dp_alto < saudavel
    assert pdp_pior < saudavel  # PDP mais alto (pior) deve reduzir o índice, não aumentar


def test_autonomia_positiva_e_infinita_sem_demanda():
    t = subsistemas.autonomia_vaso(2.0, 8e5, 6e5, 0.1, 1e5)
    assert t == pytest.approx(40.0)  # Eq. 16.5: 2·(8e5-6e5)/(0.1·1e5)
    assert subsistemas.autonomia_vaso(2.0, 8e5, 6e5, 0.0, 1e5) == math.inf


# --- Cascata completa ----------------------------------------------------------

def test_potencia_quase_invariante_a_umidade_mas_ar_seco_cai():
    # deslocamento positivo: vazão volumétrica fixa -> P·V=nRT diz que o
    # trabalho de compressão não depende de quais moléculas são admitidas.
    # Quem cai com a umidade é o ar seco ÚTIL entregue pela mesma vazão.
    seco = simular({"ur_amb": 0.10})
    umido = simular({"ur_amb": 0.95})
    assert umido["potencias"]["w_total"] == pytest.approx(
        seco["potencias"]["w_total"], rel=0.01)
    assert umido["nos"][0]["m_dot"] < seco["nos"][0]["m_dot"]
    assert umido["kpis"]["condensado_total_kg_h"] > seco["kpis"]["condensado_total_kg_h"]


def test_simular_defaults_plausivel():
    res = simular()
    k, pw = res["kpis"], res["potencias"]
    assert pw["w_total"] > 0.0
    assert 0.0 < k["eta_global"] < 1.0
    assert k["t_descarga_hp_c"] > 100.0           # descarga HP > 100 °C (:584)
    assert 4.0 <= k["spc"] <= 12.0                # faixa plausível kW·min/m³
                                                  # (modelo de eixo, sem motor/VSD)
    assert 0.0 <= k["efetividade_intercooler"] <= 1.0
    assert k["condensado_total_kg_h"] >= 0.0
    assert k["autonomia_min"] > 0.0
    assert len(res["nos"]) == 6
    for no in res["nos"]:
        assert "pdp_c" in no and "m_dot_total" in no


def test_simular_expoe_carcaca_lp_eq_9_6():
    res = simular()
    k = res["kpis"]
    t_amb_c = parametros_default()["t_amb"] - 273.15
    assert k["q_int_carcaca_w"] > 0.0
    assert k["t_carcaca_c"] > t_amb_c        # carcaça mais quente que o ambiente
    assert k["delta_t_carcaca_c"] > 0.0
    assert k["tau_carcaca_min"] > 0.0
    # menos eficiência mecânica -> mais calor gerado -> carcaça mais quente
    res_pior = simular({"eta_mec": 0.90})
    assert res_pior["kpis"]["t_carcaca_c"] > k["t_carcaca_c"]


def test_simular_hood_enclausurado_eleva_temperatura_da_carcaca():
    # Com hood, T_hood > T_amb (Eq. 2.4) e a carcaça referencia T_hood
    # (Eq. 9.16 emendada) — logo T_c enclausurado > T_c a céu aberto.
    res_hood = simular({"hood_enclausurado": True})
    res_aberto = simular({"hood_enclausurado": False})
    assert res_hood["kpis"]["t_ref_carcaca_c"] > res_aberto["kpis"]["t_ref_carcaca_c"]
    assert res_hood["kpis"]["t_carcaca_c"] > res_aberto["kpis"]["t_carcaca_c"]
    # a céu aberto, a referência é exatamente T_amb
    t_amb_c = parametros_default()["t_amb"] - 273.15
    assert res_aberto["kpis"]["t_ref_carcaca_c"] == pytest.approx(t_amb_c)


def test_simular_expoe_motor_e_hood():
    res = simular()
    k = res["kpis"]
    assert 0.0 < k["eta_mot"] < 1.0
    assert k["p_ag_w"] > 0.0
    assert k["p_perdas_mot_w"] > 0.0
    assert k["q_gerado_hood_w"] > k["q_int_carcaca_w"]  # inclui motor+outros, não só a carcaça
    assert k["t_hood_c"] > parametros_default()["t_amb"] - 273.15


def test_simular_dp_linha_reduz_pressao_efetiva_de_sucao_hp():
    res = simular()
    k = res["kpis"]
    assert k["dp_linha_mbar"] > 0.0
    assert k["p_hp_suc_efetiva_bar"] < k["p_intermediaria_bar"]


def test_pdp_secador_bate_com_pdp_real_medido():
    # o secador agora entrega ar saturado no PDP "medido" (pdp_real_c) em
    # vez do antigo W=0 fixo (ar infinitamente seco, sem base física)
    res = simular({"pdp_real_c": -30.0})
    assert res["nos"][-1]["pdp_c"] == pytest.approx(-30.0, abs=0.05)
    assert res["nos"][-1]["w"] > 0.0


def test_pdp_sobe_ao_longo_da_compressao_sem_condensar():
    # Admissão -> Descarga LP: mesma W (ainda não condensou), mas a pressão
    # subiu -> PDP tem que subir também
    res = simular()
    admissao, descarga_lp = res["nos"][0], res["nos"][1]
    assert admissao["w"] == pytest.approx(descarga_lp["w"])
    assert descarga_lp["pdp_c"] > admissao["pdp_c"]


def test_n_compressores_escala_totais_sem_afetar_por_unidade():
    r1 = simular({"n_compressores": 1})
    r3 = simular({"n_compressores": 3})
    # grandezas de planta escalam linearmente com n_compressores
    assert r3["potencias"]["w_total_planta"] == pytest.approx(
        3 * r1["potencias"]["w_total_planta"])
    assert r3["kpis"]["fad_total_m3_min"] == pytest.approx(
        3 * r1["kpis"]["fad_total_m3_min"])
    # grandezas por unidade (intensivas) não mudam com n_compressores
    assert r3["potencias"]["w_total"] == pytest.approx(r1["potencias"]["w_total"])
    assert r3["kpis"]["spc"] == pytest.approx(r1["kpis"]["spc"])
    assert r3["nos"][-1]["m_dot"] == pytest.approx(r1["nos"][-1]["m_dot"])


def test_potencia_total_aumenta_com_pressao():
    w8 = simular({"pi_total": 8.0})["potencias"]["w_total"]
    w9 = simular({"pi_total": 9.0})["potencias"]["w_total"]
    assert w9 > w8
    # regra dos ~7 %/bar com n entre 1,3 e 1,4 (:1746) — faixa tolerante
    assert (w9 - w8) / w8 == pytest.approx(0.07, abs=0.03)


# --- Ciclo de torres PSA (3 fases: adsorção, regeneração, resfriamento) ----

@pytest.mark.parametrize("n_vasos", [2, 3, 4])
def test_psa_cobertura_continua_quando_bem_dimensionado(n_vasos):
    # t_ads = t_regen + t_resfriamento -> handoff exato entre torres, sem gap
    r = psa_ciclo.simular_ciclo_psa(
        horizonte_min=30, m_dot_ar=0.5, t_ads_min=6.0, t_regen_min=4.0,
        t_resfriamento_min=2.0, n_vasos=n_vasos, k_ads=1.5, t_res_min=4.0,
        p_low=1.05e5, p_high=8.4e5, fator_purga=0.15,
        t_entrada_c=25.0, delta_t_regen=80.0)
    assert r["kpis"]["tempo_sem_secagem_min"] == pytest.approx(0.0)
    assert r["kpis"]["n_adsorvendo_min"] >= 1


def test_psa_gap_quando_resfriamento_nao_cabe_no_rodizio():
    # N=2 com regen+resfriamento (7 min) > adsorção (3 min): pelas contas do
    # rodízio, sobra um intervalo sem nenhuma torre disponível para secar —
    # exatamente o problema físico que motivou a fase de resfriamento.
    r = psa_ciclo.simular_ciclo_psa(
        horizonte_min=10, m_dot_ar=0.5, t_ads_min=3.0, t_regen_min=4.0,
        t_resfriamento_min=3.0, n_vasos=2, k_ads=1.5, t_res_min=4.0,
        p_low=1.05e5, p_high=8.4e5, fator_purga=0.15,
        t_entrada_c=25.0, delta_t_regen=80.0)
    assert r["kpis"]["tempo_sem_secagem_min"] > 0.0
    assert r["kpis"]["n_adsorvendo_min"] == 0


def test_psa_capacidade_decai_regenera_e_mantem_no_resfriamento():
    r = psa_ciclo.simular_ciclo_psa(
        horizonte_min=12, m_dot_ar=0.5, t_ads_min=6.0, t_regen_min=4.0,
        t_resfriamento_min=2.0, n_vasos=2, k_ads=1.5, t_res_min=4.0,
        p_low=1.05e5, p_high=8.4e5, fator_purga=0.15,
        t_entrada_c=25.0, delta_t_regen=80.0)
    torre0 = r["q_norm"][0]
    t = r["t_min"]
    # adsorvendo em [0, 6): capacidade cai monotonicamente
    fase_ads = torre0[t < 6.0]
    assert np.all(np.diff(fase_ads) <= 1e-9)
    # regenerando em [6, 10): capacidade recupera monotonicamente até ~1
    fase_regen = torre0[(t >= 6.0) & (t < 10.0)]
    assert np.all(np.diff(fase_regen) >= -1e-9)
    assert fase_regen[-1] == pytest.approx(1.0, abs=0.03)
    # resfriando em [10, 12): capacidade permanece em 1 (já restaurada)
    fase_resfriamento = torre0[t >= 10.0]
    assert np.all(fase_resfriamento == pytest.approx(1.0))


def test_psa_purga_so_durante_regeneracao_e_escala_com_torres_simultaneas():
    r = psa_ciclo.simular_ciclo_psa(
        horizonte_min=12, m_dot_ar=0.5, t_ads_min=6.0, t_regen_min=4.0,
        t_resfriamento_min=2.0, n_vasos=2, k_ads=1.5, t_res_min=4.0,
        p_low=1.05e5, p_high=8.4e5, fator_purga=0.15,
        t_entrada_c=25.0, delta_t_regen=80.0)
    n_regenerando = np.sum(r["estado"] == "Regenerando", axis=0)
    esperado_por_torre = 0.5 * (1.05e5 / 8.4e5) * 0.15
    # purga é zero quando ninguém regenera, e escala com quantas regeneram
    assert np.allclose(r["m_purge_kg_s"], n_regenerando * esperado_por_torre)
    assert (r["m_purge_kg_s"][n_regenerando == 0] == 0.0).all()


def test_psa_temperatura_do_leito_sobe_na_regeneracao_e_desce_no_resfriamento():
    r = psa_ciclo.simular_ciclo_psa(
        horizonte_min=12, m_dot_ar=0.5, t_ads_min=6.0, t_regen_min=4.0,
        t_resfriamento_min=2.0, n_vasos=2, k_ads=1.5, t_res_min=4.0,
        p_low=1.05e5, p_high=8.4e5, fator_purga=0.15,
        t_entrada_c=25.0, delta_t_regen=80.0)
    torre0 = r["temp_c"][0]
    t = r["t_min"]
    # adsorvendo em [0, 6): leito na temperatura de entrada
    assert np.allclose(torre0[t < 6.0], 25.0)
    # regenerando em [6, 10): temperatura sobe monotonicamente até T_entrada+ΔT
    fase_regen = torre0[(t >= 6.0) & (t < 10.0)]
    assert np.all(np.diff(fase_regen) >= -1e-9)
    assert fase_regen[-1] == pytest.approx(105.0, abs=1.0)
    # resfriando em [10, 12): temperatura desce monotonicamente de volta
    fase_resfriamento = torre0[t >= 10.0]
    assert np.all(np.diff(fase_resfriamento) <= 1e-9)
    assert fase_resfriamento[-1] < fase_resfriamento[0]


def test_umidade_nao_aumenta_ao_longo_do_tratamento():
    res = simular()
    ws = [no["w"] for no in res["nos"]]
    assert ws[2] <= ws[1] + 1e-9   # intercooler condensa
    assert ws[4] <= ws[3] + 1e-3   # aftercooler + separador (arraste pequeno)


# --- Dinâmica temporal ---------------------------------------------------------

def test_vsd_pressao_reage_a_evento_de_demanda():
    # x_c segue o alvo por rampa de 1ª ordem (tau_vsd) — um degrau de demanda
    # deve, portanto, produzir uma queda de pressão visível antes da recuperação,
    # não uma reta (regressão: x_c instantâneo fazia dP/dt = 0 o tempo todo).
    res = simular()
    m_cap = res["nos"][-1]["m_dot"]
    w_nom = res["potencias"]["w_total"]
    d = dinamica.simular_transiente(
        horizonte_min=15, m_dot_cap=m_cap, w_nom=w_nom, v_vaso=2.0, t_k=303.15,
        p_set=8e5, p_limite=6e5, dem_base=0.08, t_ev=(360.0, 585.0),
        fator_ev=2.0, modo="VSD", dp_db=0.5e5)
    assert d["kpis"]["p_max_bar"] - d["kpis"]["p_min_bar"] > 0.05


def test_vsd_pressao_constante_sem_evento():
    res = simular()
    m_cap = res["nos"][-1]["m_dot"]
    w_nom = res["potencias"]["w_total"]
    d = dinamica.simular_transiente(
        horizonte_min=15, m_dot_cap=m_cap, w_nom=w_nom, v_vaso=2.0, t_k=303.15,
        p_set=8e5, p_limite=6e5, dem_base=0.08,
        t_ev=(math.inf, math.inf), fator_ev=2.0, modo="VSD", dp_db=0.5e5)
    assert d["kpis"]["p_max_bar"] == pytest.approx(d["kpis"]["p_min_bar"], abs=1e-9)


# --- EKF (Eqs. 21.2/21.4/21.7/21.8) --------------------------------------------

def test_ekf_medicao_responde_a_folga_e_fouling():
    p = parametros_default()
    z_base = ekf.medicao(np.array([0.002, 0.0]), p)
    z_folga_alta = ekf.medicao(np.array([0.015, 0.0]), p)
    z_fouling_alto = ekf.medicao(np.array([0.002, 5e-4]), p)
    # mais folga -> menos eficiência volumétrica -> menos vazão de ar seco
    assert z_folga_alta[0] < z_base[0]
    # mais fouling -> UA cai -> intercooler resfria menos -> T_HP,in maior
    assert z_fouling_alto[1] > z_base[1]


def test_ekf_converge_para_estado_constante_com_ruido_baixo():
    p = parametros_default()
    n_passos = 40
    folga_true = np.full(n_passos, 0.010)
    r_f_true = np.zeros(n_passos)
    r = ekf.simular_ekf(
        p, folga_true, r_f_true, sigma_m_dot=1e-4, sigma_t_hp=0.05,
        q_proc_diag=(1e-8, 1e-10), x0=(0.002, 0.0), p0_diag=(1e-4, 1e-6))
    # com ruído baixo e estado verdadeiro constante, a estimativa final deve
    # convergir para perto do valor real de folga
    assert r["x_hat"][-1, 0] == pytest.approx(0.010, abs=0.001)
    # a incerteza (desvio-padrão) deve cair ao longo dos ciclos de correção
    assert r["std"][-1, 0] < r["std"][0, 0]


def test_ekf_acompanha_deriva_lenta():
    p = parametros_default()
    n_passos = 60
    folga_true = np.linspace(0.002, 0.009, n_passos)  # mesma deriva do Cap. 28
    r_f_true = np.zeros(n_passos)
    r = ekf.simular_ekf(
        p, folga_true, r_f_true, sigma_m_dot=1e-4, sigma_t_hp=0.05,
        q_proc_diag=(1e-7, 1e-10), x0=(0.002, 0.0), p0_diag=(1e-4, 1e-6))
    # a estimativa final deve acompanhar a deriva (com algum atraso esperado
    # do filtro), não ficar presa perto do valor inicial de 0,002
    assert r["x_hat"][-1, 0] > 0.006


def test_ekf_nis_proximo_dos_graus_de_liberdade_quando_bem_calibrado():
    # com Q e R usados na geração dos dados == Q e R do filtro, o NIS médio
    # deve orbitar em torno de n_z=2 (2 medições) — Eq. 21.7
    p = parametros_default()
    n_passos = 80
    folga_true = np.full(n_passos, 0.002)
    r_f_true = np.zeros(n_passos)
    r = ekf.simular_ekf(
        p, folga_true, r_f_true, sigma_m_dot=2e-4, sigma_t_hp=0.1,
        q_proc_diag=(1e-9, 1e-11), x0=(0.002, 0.0), p0_diag=(1e-6, 1e-8),
        seed=7)
    nis_medio = float(np.mean(r["nis"][10:]))  # descarta transiente inicial
    assert 0.3 < nis_medio < 8.0  # faixa larga e tolerante em torno de n_z=2


# --- PSO (Eqs. 24.3/24.4) -------------------------------------------------------

def test_pso_minimiza_funcao_quadratica_simples():
    custo = lambda x: (x[0] - 3.0) ** 2 + (x[1] + 1.5) ** 2
    r = pso.otimizar(custo, limite_inf=[-10.0, -10.0], limite_sup=[10.0, 10.0],
                     n_particulas=25, n_iter=50, seed=1)
    assert r["g_best"][0] == pytest.approx(3.0, abs=0.05)
    assert r["g_best"][1] == pytest.approx(-1.5, abs=0.05)
    assert r["g_best_custo"] < 1e-2


def test_pso_historico_de_custo_nao_aumenta():
    custo = lambda x: (x[0] - 1.0) ** 2
    r = pso.otimizar(custo, limite_inf=[-5.0], limite_sup=[5.0],
                     n_particulas=15, n_iter=30, seed=2)
    hist = r["historico_custo"]
    assert np.all(np.diff(hist) <= 1e-12)  # g_best só melhora ou empata


def test_pso_minimiza_spc_sem_restricao_vai_para_pressao_minima():
    # sem restrição de autonomia, SPC cresce com a pressão de rede (regra dos
    # ~7%/bar) -> o mínimo irrestrito deve ficar no limite inferior da busca
    def custo(x):
        return simular({"pi_total": float(x[0])})["kpis"]["spc"]

    r = pso.otimizar(custo, limite_inf=[5.0], limite_sup=[12.0],
                     n_particulas=12, n_iter=25, seed=3)
    assert r["g_best"][0] == pytest.approx(5.0, abs=0.1)


# --- VAE (Eqs. 20.4, 22.1-22.7) -------------------------------------------------

def test_vae_extrai_features_tamanho_correto():
    res = simular()
    feat = vae.extrair_features(res)
    assert feat.shape == (len(vae.NOMES_FEATURES),)
    assert np.all(np.isfinite(feat))


def test_vae_gerar_dataset_forma_correta():
    p = parametros_default()
    ds = vae.gerar_dataset_saudavel(50, p, seed=0)
    assert ds.shape == (50, len(vae.NOMES_FEATURES))
    assert np.all(np.isfinite(ds))


def test_vae_treino_reduz_perda():
    p = parametros_default()
    ds = vae.gerar_dataset_saudavel(200, p, seed=0)
    info = vae.treinar(ds, n_epocas=150)
    assert info["historico_loss"][-1] < info["historico_loss"][0]


def test_vae_detecta_anomalia_clara_fora_do_limiar():
    p = parametros_default()
    ds_treino = vae.gerar_dataset_saudavel(400, p, seed=0)
    ds_val = vae.gerar_dataset_saudavel(150, p, seed=1)
    info = vae.treinar(ds_treino, n_epocas=300)
    limiar = vae.calibrar_limiar(info, ds_val, n_desvios=3.0)

    # ponto de operação saudável (referência) não deve disparar
    feat_saudavel = vae.extrair_features(simular(p))[None, :]
    e_saudavel = vae.erro_reconstrucao(info, feat_saudavel)
    assert e_saudavel[0] < limiar

    # folga bem fora da faixa de comissionamento (0,0018-0,0022) deve disparar
    p_deg = {**p, "folga_rel": 0.02}
    feat_deg = vae.extrair_features(simular(p_deg))[None, :]
    e_deg = vae.erro_reconstrucao(info, feat_deg)
    assert e_deg[0] > limiar


# --- PIML (Eqs. 23.1-23.4) -------------------------------------------------------

_FAIXAS_PIML_TESTE = {
    "pi_total": (6.0, 10.0), "t_amb_c": (10.0, 40.0),
    "folga_rel": (0.001, 0.02), "r_f_equiv": (0.0, 5e-4),
    "fad_m3_min": (8.0, 12.0),
}


def test_piml_gerar_dataset_forma_correta():
    p = parametros_default()
    entradas, saidas = piml.gerar_dataset(30, p, _FAIXAS_PIML_TESTE, seed=0)
    assert entradas.shape == (30, len(piml.NOMES_ENTRADA))
    assert saidas.shape == (30, len(piml.NOMES_SAIDA))
    assert np.all(np.isfinite(entradas)) and np.all(np.isfinite(saidas))


def test_piml_treino_reduz_ambas_as_perdas():
    p = parametros_default()
    entradas, saidas = piml.gerar_dataset(300, p, _FAIXAS_PIML_TESTE, seed=0)
    info = piml.treinar(entradas, saidas, _FAIXAS_PIML_TESTE, n_epocas=200, lr=1e-2)
    assert info["hist_data"][-1] < info["hist_data"][0]
    assert info["hist_fisica"][-1] < info["hist_fisica"][0]


def test_piml_preve_proximo_do_simulador_real():
    p = parametros_default()
    entradas, saidas = piml.gerar_dataset(400, p, _FAIXAS_PIML_TESTE, seed=0)
    info = piml.treinar(entradas, saidas, _FAIXAS_PIML_TESTE, n_epocas=300, lr=1e-2)

    entradas_teste, saidas_teste = piml.gerar_dataset(20, p, _FAIXAS_PIML_TESTE, seed=99)
    pred = piml.prever(info, entradas_teste)
    # T_HP,in praticamente não varia (intercooler efetivo) -> erro deve ser mínimo;
    # T_LP,out e ṁ_seco têm faixa maior, tolerância proporcionalmente maior
    assert np.abs(pred[:, 1] - saidas_teste[:, 1]).mean() < 0.5   # °C
    assert np.abs(pred[:, 2] - saidas_teste[:, 2]).mean() < 0.01  # kg/s


def test_piml_residuo_fisico_pequeno_apos_treino():
    p = parametros_default()
    entradas, saidas = piml.gerar_dataset(400, p, _FAIXAS_PIML_TESTE, seed=0)
    info = piml.treinar(entradas, saidas, _FAIXAS_PIML_TESTE, n_epocas=300, lr=1e-2)

    entradas_coloc, _ = piml.gerar_dataset(50, p, _FAIXAS_PIML_TESTE, seed=123)
    residuo = piml.residuo_fisico_real(info, entradas_coloc)
    q_medio = np.abs(saidas[:, 3]).mean()
    # resíduo médio bem abaixo da escala típica de Q̇ — o livro é explícito que a
    # penalização física é fraca (não nula), então a tolerância aqui é generosa
    assert np.abs(residuo).mean() < 0.05 * q_medio


# --- MPC (Eqs. 24.1/24.2) --------------------------------------------------------

def test_mpc_x_c_respeita_limites():
    params = parametros_default()
    res = simular(params)
    pw = res["potencias"]
    m_dot_cap = res["nos"][-1]["m_dot"] * pw["n_compressores"]
    rho_amb = nucleo.densidade_ar(params["p_amb"], params["t_amb"])
    dem_base = rho_amb * 5.0 / 60.0
    r = mpc.simular_mpc(
        horizonte_min=6.0, dt=5.0, n_horizonte=10, m_dot_cap=m_dot_cap,
        v_vaso=params["v_vaso"], t_k=params["t_amb"],
        p_set=params["p_amb"] * params["pi_total"], dem_base=dem_base,
        t_ev=(90.0, 180.0), fator_ev=1.4, rho=0.05, x_c_min=0.3,
        w_nom=pw["w_total_planta"], eta_vsd=0.95)
    assert np.all(r["x_c"] >= 0.3 - 1e-9)
    assert np.all(r["x_c"] <= 1.0 + 1e-9)


def test_mpc_rastreia_referencia_melhor_que_controle_reativo():
    # cenário com margem de capacidade (evento moderado, não satura o vaso)
    # -- o MPC antecipa a demanda futura conhecida; o controle reativo de
    # dinamica.py só responde à demanda do instante atual via rampa de 1ª
    # ordem (Eq. 13.7) -- o MPC deve rastrear a pressão de referência com
    # erro médio menor.
    params = parametros_default()
    res = simular(params)
    pw = res["potencias"]
    m_dot_cap = res["nos"][-1]["m_dot"] * pw["n_compressores"]
    rho_amb = nucleo.densidade_ar(params["p_amb"], params["t_amb"])
    dem_base = rho_amb * 5.0 / 60.0
    p_set = params["p_amb"] * params["pi_total"]
    horizonte_min, t_ev, fator_ev = 10.0, (240.0, 390.0), 1.4

    r_mpc = mpc.simular_mpc(
        horizonte_min=horizonte_min, dt=5.0, n_horizonte=12,
        m_dot_cap=m_dot_cap, v_vaso=params["v_vaso"], t_k=params["t_amb"],
        p_set=p_set, dem_base=dem_base, t_ev=t_ev, fator_ev=fator_ev,
        rho=0.05, x_c_min=0.3, w_nom=pw["w_total_planta"], eta_vsd=0.95)
    r_reativo = dinamica.simular_transiente(
        horizonte_min=horizonte_min, m_dot_cap=m_dot_cap,
        w_nom=pw["w_total_planta"], v_vaso=params["v_vaso"],
        t_k=params["t_amb"], p_set=p_set, p_limite=params["p_limite"],
        dem_base=dem_base, t_ev=t_ev, fator_ev=fator_ev, modo="VSD",
        dp_db=0.5e5)

    p_ref_bar = p_set / 1e5
    desvio_mpc = np.mean(np.abs(r_mpc["p_bar"] - p_ref_bar))
    desvio_reativo = np.mean(np.abs(r_reativo["p_bar"] - p_ref_bar))
    assert desvio_mpc < desvio_reativo
