"""Testes unitários do módulo de fadiga (RUL por Regra de Palmgren-Miner + EHI, Eqs. 19.6-19.10)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compressor_sim import fadiga


def test_parametros_basquin_positivos():
    C, b_f = fadiga.parametros_basquin()
    assert C > 0.0
    assert b_f > 0.0


def test_dano_incremental_cresce_com_tensao():
    # Eq. 19.8: N_i(sigma) cai com sigma maior -> dano por ciclo sobe
    d_baixo = fadiga.dano_incremental(sigma_b_mpa=120.0, rpm=3528.0, dt_dias=1.0)
    d_alto = fadiga.dano_incremental(sigma_b_mpa=250.0, rpm=3528.0, dt_dias=1.0)
    assert 0.0 < d_baixo < d_alto


def test_dano_incremental_zero_sem_rotacao():
    assert fadiga.dano_incremental(sigma_b_mpa=120.0, rpm=0.0, dt_dias=1.0) == 0.0


def test_dano_incremental_no_limite_admissivel():
    # No limite admissível (== SIGMA_B_ADM_MPA, referência de N_REF_ENDURANCE
    # ciclos), o dano por dia deve ser pequeno mas não nulo.
    from compressor_sim import constantes as c
    d = fadiga.dano_incremental(sigma_b_mpa=c.SIGMA_B_ADM_MPA, rpm=3528.0, dt_dias=1.0)
    assert d > 0.0


def test_taxa_dano_gp_media_positiva_para_dano_crescente():
    t_obs = [0.0, 5.0, 10.0, 15.0, 20.0]
    taxas = [0.001, 0.0012, 0.0011, 0.0013, 0.0012]
    media, var = fadiga.taxa_dano_gp(t_obs, taxas, t_estrela_dias=20.0)
    assert media > 0.0
    assert var >= 0.0


def test_projetar_rul_fadiga_decresce_com_dano():
    hist_baixo = list(__import__("numpy").linspace(0.0, 0.05, 20))
    hist_alto = list(__import__("numpy").linspace(0.0, 0.60, 20))
    r_baixo = fadiga.projetar_rul_fadiga(hist_baixo, dt_dias=1.0)
    r_alto = fadiga.projetar_rul_fadiga(hist_alto, dt_dias=1.0)
    assert r_alto["dano_acumulado"] > r_baixo["dano_acumulado"]
    assert r_alto["rul_dias_estimado"] < r_baixo["rul_dias_estimado"]
    assert r_baixo["rul_ic_95_min"] <= r_baixo["rul_dias_estimado"] <= r_baixo["rul_ic_95_max"]


def test_projetar_rul_fadiga_historico_curto():
    r = fadiga.projetar_rul_fadiga([0.0, 0.01], dt_dias=1.0)
    assert r["confiabilidade"].startswith("Baixa")
    assert r["rul_dias_estimado"] > 0.0


def test_calcular_ehi_bounds():
    # E_rec = 0 (reconstrução perfeita): EHI == razão de eficiência exergética
    assert abs(fadiga.calcular_ehi(0.85, 0.0) - 0.85) < 1e-9
    # E_rec > 0 desconta o índice
    ehi_com_erro = fadiga.calcular_ehi(0.85, 2.0)
    assert 0.0 < ehi_com_erro < 0.85
    # razão fora de [0,1] é grampeada
    assert fadiga.calcular_ehi(1.5, 0.0) <= 1.0
