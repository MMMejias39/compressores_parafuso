"""Testes unitários dos módulos de Telemetria PI, Treinamento de Falhas e Supervisão de Frota."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compressor_sim import (
    frota_supervisorio,
    parametros_default,
    pi_telemetry,
    sistema,
    treinamento_falhas,
)


def test_catalogo_tags_pi():
    tags = pi_telemetry.obter_catalogo_tags_pi(prefixo="CMP01")
    assert len(tags) >= 25
    tag_names = [t.tag for t in tags]
    assert "CMP01:LP_PSUC" in tag_names
    assert "CMP01:HP_PDISC" in tag_names
    assert "CMP01:PSA_TDP" in tag_names
    assert "CMP01:ELE_I" in tag_names
    assert "CMP01:DT_EXERGY_DEST" in tag_names


def test_extrair_snapshot_pi():
    params = parametros_default()
    res = sistema.simular(params)
    snapshot = pi_telemetry.extrair_snapshot_pi(res, params, prefixo="CMP01", adicionar_ruido=False)
    
    assert isinstance(snapshot, dict)
    assert "CMP01:LP_TDISC" in snapshot
    assert snapshot["CMP01:LP_TDISC"]["valor"] > 50.0  # Temperatura em °C plausível
    assert snapshot["CMP01:PSA_TDP"]["valor"] < -20.0   # Ponto de orvalho negativo
    assert snapshot["CMP01:TK_PTK"]["valor"] > 5.0      # Pressão em bar


def test_gerar_serie_temporal_pi():
    params = parametros_default()
    df_serie = pi_telemetry.gerar_serie_temporal_pi(
        params_base=params,
        n_passos=10,
        dt_minutos=1.0,
        falha_injetada=None,
        seed=123,
    )
    assert isinstance(df_serie, pd.DataFrame)
    assert len(df_serie) == 10
    assert "CMP01:LP_PSUC" in df_serie.columns
    assert "Timestamp" in df_serie.columns
    assert "CMP01:LP_PSUC_Quality" in df_serie.columns


def test_gerar_serie_temporal_com_falha():
    params = parametros_default()
    falha = {
        "id": "folga_lp",
        "parametro": "folga_rel",
        "valor_severo": 0.020,
    }
    df_serie = pi_telemetry.gerar_serie_temporal_pi(
        params_base=params,
        n_passos=20,
        dt_minutos=1.0,
        falha_injetada=falha,
        passo_inicio_falha=10,
        severidade_final=1.0,
        seed=42,
    )
    assert len(df_serie) == 20
    assert df_serie["Falha_Ativa"].iloc[5] == "NENHUMA"
    assert df_serie["Falha_Ativa"].iloc[15] == "folga_lp"


def test_catalogo_falhas_treinamento():
    falhas = treinamento_falhas.CATALOGO_FALHAS_TREINAMENTO
    assert len(falhas) >= 10
    ids = [f.id for f in falhas]
    assert "folga_lp" in ids
    assert "fouling_intercooler" in ids
    assert "filtro_admissao" in ids
    assert "psa_breakthrough" in ids
    assert "psv_travada_fechada" in ids


def test_classificador_m_falha_minimo_residuo():
    params = parametros_default()
    # Injeta falha de folga LP
    p_falha = dict(params)
    p_falha["folga_rel"] = 0.015
    res = sistema.simular(p_falha)
    snap = pi_telemetry.extrair_snapshot_pi(res, p_falha, adicionar_ruido=False)
    vetor_z = {tag: info["valor"] for tag, info in snap.items()}

    ranking = treinamento_falhas.classificar_m_falha_minimo_residuo(vetor_z, params)
    assert len(ranking) > 0
    # O primeiro classificado deve ser o mecanismo de folga LP
    melhor_hipotese = ranking[0]["mecanismo"]
    assert melhor_hipotese.id == "folga_lp"
    assert ranking[0]["probabilidade_pct"] > 30.0


def test_gerar_e_avaliar_caso_treinamento():
    params = parametros_default()
    caso = treinamento_falhas.gerar_caso_treinamento(
        dificuldade="Intermediario",
        params_base=params,
        mecanismo_especifico_id="fouling_intercooler",
        seed=999,
    )
    assert caso["mecanismo_gabarito"].id == "fouling_intercooler"
    assert isinstance(caso["df_serie_pi"], pd.DataFrame)

    # Avaliação com resposta correta
    gabarito = caso["mecanismo_gabarito"]
    sev_str = "Severa/Crítica" if caso["severidade"] >= 0.70 else "Moderada/Alerta"
    avaliacao = treinamento_falhas.avaliar_diagnostico_usuario(
        caso=caso,
        subsistema_escolhido=gabarito.subsistema,
        mecanismo_id_escolhido=gabarito.id,
        severidade_escolhida=sev_str,
        acao_escolhida=gabarito.acao_prescritiva,
    )
    assert avaliacao["score_total"] >= 80.0
    assert avaliacao["aprovado"] is True


def test_frota_supervisorio():
    frota = frota_supervisorio.criar_frota_padrao_offshore(n_maquinas=4)
    assert len(frota) == 4
    
    painel = frota_supervisorio.executar_ciclo_supervisorio_frota(frota, dt_dias=1.0)
    assert len(painel) == 4
    for item in painel:
        assert 0.0 <= item["hi"] <= 1.0
        assert 0.0 <= item["ehi"] <= 1.0
        assert item["e_rec_vae"] >= 0.0
        assert item["rul_estimado_dias"] > 0.0
        assert item["rul_ic_min"] <= item["rul_estimado_dias"] <= item["rul_ic_max"]
        assert item["dano_acumulado"] >= 0.0
        assert "CMP0" in item["tag_prefix"]


def test_health_index_composto():
    # Saudável
    res_saudavel = {"folga_rel": 0.002, "fouling_rf": 0.0, "vibracao": 2.10, "temperatura": 123.8}
    hi_ok = frota_supervisorio.calcular_health_index_composto(res_saudavel)
    assert hi_ok > 0.95

    # Degradado
    res_ruim = {"folga_rel": 0.018, "fouling_rf": 0.0012, "vibracao": 6.5, "temperatura": 145.0}
    hi_ruim = frota_supervisorio.calcular_health_index_composto(res_ruim)
    assert hi_ruim < 0.40
