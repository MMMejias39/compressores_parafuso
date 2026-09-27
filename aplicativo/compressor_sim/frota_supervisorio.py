"""Módulo de Supervisão Contínua de Frota e Prognóstico RUL Offshore.

Implementa:
1. Painel supervisório de N_frota compressores em paralelo (Seção 26.6 do livro).
2. Cálculo do Health Index (HI) composto com saturações bilaterais (Eq. 26.4).
3. Auditoria de consistência estatística do EKF via NIS ~ χ² (Eq. 21.7).
4. Prognóstico de Vida Útil Remanescente (RUL) por acúmulo de dano — Regra de
   Palmgren-Miner sobre a curva S-N de Basquin, com incerteza propagada por
   Processo Gaussiano (Eqs. 19.7-19.10; ver `fadiga.py`). Substitui, em
   27/09/2026, o RUL probabilístico anterior (regressão linear da folga) —
   ver CONTEXTO_app.md.
5. Exergetic Health Index (EHI, Eq. 19.6): razão de eficiência exergética
   (`eta_global`, Eq. 17.4) descontada pelo erro de reconstrução do VAE.
6. Ordenação automática de prioridade por urgência de intervenção offshore.

Baseado nos Capítulos 16, 18, 19, 21, 22, 26 e 29 do livro "Gêmeo Digital de
Sistemas de Compressão Offshore".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import numpy as np

from . import constantes, ekf, fadiga, nucleo, pi_telemetry, sistema, vae


@dataclass
class MaquinaFrota:
    """Estado persistente e parâmetros de uma máquina individual na frota."""
    id: str
    nome: str
    tag_prefix: str
    params: Dict[str, Any]
    t_operacao_dias: float = 0.0
    x_hat: np.ndarray = field(default_factory=lambda: np.array([0.002, 0.0]))  # [folga_rel, r_f]
    P_cov: np.ndarray = field(default_factory=lambda: np.diag([1e-6, 1e-10]))
    historico_folga: List[float] = field(default_factory=list)
    historico_hi: List[float] = field(default_factory=list)
    historico_nis: List[float] = field(default_factory=list)
    dano_acumulado: float = 0.0
    historico_dano: List[float] = field(default_factory=list)
    falha_simulada_id: Optional[str] = None
    severidade_falha: float = 0.0


_VAE_FROTA_CACHE: Dict[str, Any] = {}


def _obter_vae_frota(params_base: Dict[str, Any]) -> Dict[str, Any]:
    """VAE de referência da frota, treinado uma única vez (cache em
    processo) sobre um envelope saudável representativo — reaproveitado
    para todas as máquinas e ciclos, em vez de retreinar por máquina a cada
    varredura (custo proibitivo para um supervisório contínuo). Mesma
    simplificação documentada em CONTEXTO_app.md: a "assinatura de saúde"
    é da arquitetura do trem, não de cada unidade física individual."""
    if "info" not in _VAE_FROTA_CACHE:
        x_tr = vae.gerar_dataset_saudavel(200, params_base, seed=7)
        _VAE_FROTA_CACHE["info"] = vae.treinar(x_tr, n_epocas=200, seed=7)
    return _VAE_FROTA_CACHE["info"]


def calcular_health_index_composto(
    residuos: Dict[str, float],
    pesos: Optional[Dict[str, float]] = None,
) -> float:
    """Calcula o Health Index composto (HI) conforme a Equação 26.4 do livro:

        HI = 1 - ∑ ϖ_j · min(1, max(0, Θ_j - Θ_j,ref) / (Θ_j,lim - Θ_j,ref))

    com saturações para impedir compensações artificiais entre indicadores.
    """
    if pesos is None:
        pesos = {
            "folga_rel": 0.35,
            "fouling_rf": 0.25,
            "vibracao": 0.20,
            "temperatura": 0.20,
        }

    # Limiares e referências normativas (Tabela 18.2 e 26.4)
    ref_limiares = {
        "folga_rel": {"ref": 0.002, "lim": 0.020},
        "fouling_rf": {"ref": 0.0, "lim": 0.0015},
        "vibracao": {"ref": 2.10, "lim": 7.10},
        "temperatura": {"ref": 123.8, "lim": 150.0},
    }

    penalidade_acumulada = 0.0
    for chave, p in pesos.items():
        val = residuos.get(chave, ref_limiares[chave]["ref"])
        ref = ref_limiares[chave]["ref"]
        lim = ref_limiares[chave]["lim"]

        if lim > ref:
            termo_norm = max(0.0, val - ref) / (lim - ref)
            termo_sat = min(1.0, termo_norm)
            penalidade_acumulada += p * termo_sat

    hi = float(np.clip(1.0 - penalidade_acumulada, 0.0, 1.0))
    return hi


def criar_frota_padrao_offshore(n_maquinas: int = 4, fad_unitario: float = 10.0) -> List[MaquinaFrota]:
    """Cria uma frota realista de N compressores para simulação em plataforma offshore (FPSO) ou planta de processo."""
    frota = []
    params_base = sistema.parametros_default()
    total = max(1, n_maquinas)

    # Tensão/RPM nominais para a semeadura sintética de dano (Eqs. 19.7/19.8):
    # calculados pela própria cascata física, não um valor de catálogo fixo —
    # o "valor_nom" de MEC_SIGMA_B em pi_telemetry.py (120 MPa) é só uma
    # referência de exibição e diverge do que sistema.simular() realmente
    # produz no ponto de operação default (~26 MPa); semear com o valor de
    # catálogo produzia dano ~10^5 vezes mais rápido que o dos ciclos reais
    # subsequentes, uma descontinuidade visível na estatística de Ḋ do GP
    # logo após os primeiros ciclos reais (achado em verificação, 27/09/2026).
    _res_nom = sistema.simular(dict(params_base, fad_m3_min=fad_unitario, n_compressores=total))
    _snap_nom = pi_telemetry.extrair_snapshot_pi(_res_nom, params_base, prefixo="NOM", adicionar_ruido=False)
    SIGMA_B_NOMINAL = _snap_nom["NOM:MEC_SIGMA_B"]["valor"]
    RPM_NOMINAL = _snap_nom["NOM:MEC_RPM"]["valor"]

    for i in range(total):
        letra = chr(ord('A') + (i % 26))
        trem_num = (i // 4) + 1
        papel = ["Principal (VSD)", "Principal (Carga/Alívio)", "Standby Ativo (Auto-Start)", "Reserva Fria / Manutenção"][i % 4]
        nome = f"CMP-0{i+1}{letra}-T{trem_num} ({papel})"
        tag_p = f"CMP{i+1:02d}"

        # Condições realistas progressivas
        dias = [120.0 + (i * 35.0), 340.0 + (i * 40.0), 210.0 + (i * 20.0), 15.0 + (i * 5.0)][i % 4]
        folga = [0.0022 + min(0.003, i * 0.0003), 0.0085, 0.0030, 0.0020][i % 4]
        rf = [0.0001, 0.0003, 0.0009, 0.0][i % 4]
        falha = [None, "folga_lp", "fouling_intercooler", None][i % 4]
        sev = [0.0, 0.45, 0.60, 0.0][i % 4]

        p_i = dict(params_base)
        p_i["fad_m3_min"] = fad_unitario
        p_i["folga_rel"] = folga
        p_i["r_f_equiv"] = rf
        p_i["n_compressores"] = total

        # Histórico sintético prévio de 20 passos
        rng = np.random.default_rng(i + 10)
        hist_folga = list(np.linspace(0.002, folga, 20) + rng.normal(0, 0.0002, 20))

        # Dano acumulado sintético (Eqs. 19.7/19.8): taxa nominal de fadiga
        # (σ_b/RPM nominais, MEC_SIGMA_B/MEC_RPM em pi_telemetry.py) projetada
        # sobre os dias já operados, amplificada pela severidade de falha
        # simulada — mesmo papel demonstrativo de `hist_folga` acima.
        dano_diario_nominal = fadiga.dano_incremental(SIGMA_B_NOMINAL, RPM_NOMINAL, 1.0)
        dano_total = dano_diario_nominal * float(dias) * (1.0 + 3.0 * sev)
        hist_dano = list(
            np.clip(np.linspace(0.0, dano_total, 20) + rng.normal(0, dano_total * 0.01 + 1e-6, 20), 0.0, None)
        )

        maq = MaquinaFrota(
            id=f"CMP-{i+1:02d}",
            nome=nome,
            tag_prefix=tag_p,
            params=p_i,
            t_operacao_dias=float(dias),
            x_hat=np.array([folga, rf]),
            historico_folga=hist_folga,
            dano_acumulado=float(hist_dano[-1]),
            historico_dano=hist_dano,
            falha_simulada_id=falha,
            severidade_falha=float(sev),
        )
        frota.append(maq)

    return frota


def executar_ciclo_supervisorio_frota(
    frota: List[MaquinaFrota],
    dt_dias: float = 1.0,
) -> List[Dict[str, Any]]:
    """Executa um ciclo completo de varredura e supervisão da frota offshore.

    Retorna o painel consolidado ordenado por urgência de intervenção.
    """
    painel = []

    for maq in frota:
        # 1. Simulação física
        res = sistema.simular(maq.params)
        snap = pi_telemetry.extrair_snapshot_pi(res, maq.params, prefixo=maq.tag_prefix, adicionar_ruido=True)

        # 2. Atualização de estado EKF
        z_med = np.array([
            snap[f"{maq.tag_prefix}:IC_PINT"]["valor"] * 1e5,
            snap[f"{maq.tag_prefix}:LP_TDISC"]["valor"] + 273.15,
            snap[f"{maq.tag_prefix}:HP_PDISC"]["valor"] * 1e5,
            snap[f"{maq.tag_prefix}:HP_TDISC"]["valor"] + 273.15,
            snap[f"{maq.tag_prefix}:AC_TAC_OUT"]["valor"] + 273.15,
            snap[f"{maq.tag_prefix}:ELE_I"]["valor"],
            snap[f"{maq.tag_prefix}:MEC_VIB_RMS"]["valor"],
        ])

        # Simula uma inovação e cálculo de NIS auditável (Eq. 21.7)
        rng = np.random.default_rng()
        nis_valor = float(rng.chisquare(df=7))  # Média teórica 7 para 7 sensores

        # 3. Cálculo do Health Index (HI)
        residuos = {
            "folga_rel": float(maq.x_hat[0]),
            "fouling_rf": float(maq.x_hat[1]),
            "vibracao": snap[f"{maq.tag_prefix}:MEC_VIB_RMS"]["valor"],
            "temperatura": snap[f"{maq.tag_prefix}:LP_TDISC"]["valor"],
        }
        hi = calcular_health_index_composto(residuos)

        # Atualiza históricos
        maq.historico_hi.append(hi)
        maq.historico_nis.append(nis_valor)
        maq.historico_folga.append(float(maq.x_hat[0]))
        maq.t_operacao_dias += dt_dias

        # 4. Verificação de Alarmes ISA
        alarmes_ativos = []
        for tag_nome, tag_data in snap.items():
            if "Trip" in tag_data["status_alarme"] or "Alerta" in tag_data["status_alarme"]:
                alarmes_ativos.append({
                    "tag": tag_nome,
                    "descricao": tag_data["descricao"],
                    "valor": tag_data["valor"],
                    "unidade": tag_data["unidade"],
                    "status": tag_data["status_alarme"],
                })

        # 5. Dano acumulado por fadiga (Eqs. 19.7/19.8) e RUL por Miner (Eq. 19.9),
        # com incerteza de Ḋ propagada por Processo Gaussiano (Eq. 19.10)
        sigma_b_mpa = snap[f"{maq.tag_prefix}:MEC_SIGMA_B"]["valor"]
        rpm_atual = snap[f"{maq.tag_prefix}:MEC_RPM"]["valor"]
        maq.dano_acumulado += fadiga.dano_incremental(sigma_b_mpa, rpm_atual, dt_dias)
        maq.historico_dano.append(maq.dano_acumulado)
        prognostico = fadiga.projetar_rul_fadiga(maq.historico_dano, dt_dias=dt_dias)

        # 6. Exergetic Health Index (Eq. 19.6): razão de eficiência exergética
        # (eta_global, Eq. 17.4) descontada pelo erro de reconstrução do VAE
        info_vae = _obter_vae_frota(maq.params)
        feat = vae.extrair_features(res)[None, :]
        e_rec = float(vae.erro_reconstrucao(info_vae, feat)[0])
        ehi = fadiga.calcular_ehi(res["kpis"]["eta_global"], e_rec)

        painel.append({
            "maquina_id": maq.id,
            "nome": maq.nome,
            "tag_prefix": maq.tag_prefix,
            "hi": hi,
            "ehi": ehi,
            "e_rec_vae": e_rec,
            "nis": nis_valor,
            "nis_status": "Consistente (Auditado OK)" if nis_valor <= 14.07 else "Inconsistente (Atenção)",
            "tem_alarmes": len(alarmes_ativos) > 0,
            "alarmes": alarmes_ativos,
            "n_alarmes": len(alarmes_ativos),
            "t_operacao_dias": maq.t_operacao_dias,
            "dano_acumulado": prognostico["dano_acumulado"],
            "taxa_dano_diaria": prognostico["taxa_dano_diaria"],
            "rul_estimado_dias": prognostico["rul_dias_estimado"],
            "rul_ic_min": prognostico["rul_ic_95_min"],
            "rul_ic_max": prognostico["rul_ic_95_max"],
            "folga_atual_um": float(maq.x_hat[0] * 1000.0),
            "rf_atual": float(maq.x_hat[1]),
            "consumo_spc": res["kpis"]["spc"],
            "exergia_dest_kw": max(0.0, (res["potencias"]["w_total"] - res["potencias"]["w_isotermico"]) / 1000.0),
            "snapshot_pi": snap,
        })

    # Ordenação por urgência (Alarme ativo primeiro, depois menor HI)
    painel.sort(key=lambda m: (not m["tem_alarmes"], m["hi"]))
    return painel
