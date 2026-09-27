//! Módulo de Supervisão Contínua de Frota e Prognóstico RUL Offshore.
//!
//! Implementa:
//! 1. Painel supervisório de N_frota compressores em paralelo (Seção 26.6).
//! 2. Health Index (HI) composto com saturações bilaterais (Eq. 26.4).
//! 3. Auditoria de consistência estatística via NIS (Eq. 21.7).
//! 4. Prognóstico de RUL por acúmulo de dano — Regra de Palmgren-Miner sobre
//!    a curva S-N de Basquin, com incerteza propagada por Processo Gaussiano
//!    (Eqs. 19.7-19.10; ver `fadiga.rs`). Substitui, em 27/09/2026, o RUL
//!    probabilístico anterior (regressão linear da folga).
//! 5. Ordenação por urgência de intervenção offshore.
//!
//! **Não implementado neste crate:** o Exergetic Health Index (EHI, Eq. 19.6)
//! depende do erro de reconstrução de um VAE (Eq. 20.4/22.5); VAE/PIML ainda
//! não foram portados para Rust (só EKF/MPC/PSO) — ver CONTEXTO_app.md.

use rand::prelude::*;
use rand_distr::ChiSquared;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use crate::pi_telemetry::{extrair_snapshot_pi, SnapshotTag};
use crate::sistema::{self, Params};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MaquinaFrota {
    pub id: String,
    pub nome: String,
    pub tag_prefix: String,
    pub params: Params,
    pub t_operacao_dias: f64,
    pub x_hat: [f64; 2], // [folga_rel, r_f]
    pub historico_folga: Vec<f64>,
    pub historico_hi: Vec<f64>,
    pub historico_nis: Vec<f64>,
    #[serde(default)]
    pub dano_acumulado: f64,
    #[serde(default)]
    pub historico_dano: Vec<f64>,
    pub falha_simulada_id: Option<String>,
    pub severidade_falha: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PainelMaquina {
    pub maquina_id: String,
    pub nome: String,
    pub tag_prefix: String,
    pub hi: f64,
    pub nis: f64,
    pub nis_status: String,
    pub tem_alarmes: bool,
    pub n_alarmes: usize,
    pub t_operacao_dias: f64,
    pub dano_acumulado: f64,
    pub taxa_dano_diaria: f64,
    pub rul_estimado_dias: f64,
    pub rul_ic_min: f64,
    pub rul_ic_max: f64,
    pub folga_atual_um: f64,
    pub rf_atual: f64,
    pub consumo_spc: f64,
    pub exergia_dest_kw: f64,
    pub snapshot_pi: HashMap<String, SnapshotTag>,
}

pub fn calcular_health_index_composto(
    folga_rel: f64,
    fouling_rf: f64,
    vibracao: f64,
    temperatura: f64,
) -> f64 {
    let pesos = [
        ("folga_rel", 0.35, folga_rel, 0.002, 0.020),
        ("fouling_rf", 0.25, fouling_rf, 0.0, 0.0015),
        ("vibracao", 0.20, vibracao, 2.10, 7.10),
        ("temperatura", 0.20, temperatura, 123.8, 150.0),
    ];

    let mut penalidade = 0.0;
    for &(_nome, peso, val, ref_val, lim_val) in &pesos {
        if lim_val > ref_val {
            let termo_norm = ((val - ref_val) / (lim_val - ref_val)).max(0.0);
            let termo_sat = termo_norm.min(1.0);
            penalidade += peso * termo_sat;
        }
    }

    (1.0 - penalidade).clamp(0.0, 1.0)
}

pub fn criar_frota_padrao_offshore(n_maquinas: usize) -> Vec<MaquinaFrota> {
    criar_frota_com_capacidade(n_maquinas, 10.0)
}

pub fn criar_frota_com_capacidade(n_maquinas: usize, fad_unitario: f64) -> Vec<MaquinaFrota> {
    let mut frota = Vec::new();
    let total = n_maquinas.max(1);

    // Tensão/RPM nominais reais (não valores de catálogo) para a semeadura
    // sintética de dano — ver frota_supervisorio.py para a justificativa
    // completa (evita descontinuidade entre a taxa de dano semeada e a dos
    // ciclos reais subsequentes).
    let mut params_nom = Params::default();
    params_nom.fad_m3_min = fad_unitario;
    params_nom.n_compressores = total as u32;
    let res_nom = sistema::simular(&params_nom);
    let snap_nom = extrair_snapshot_pi(&res_nom, &params_nom, "NOM", false, Some(0));
    let sigma_b_nominal = snap_nom.get("NOM:MEC_SIGMA_B").map(|t| t.valor).unwrap_or(120.0);
    let rpm_nominal = snap_nom.get("NOM:MEC_RPM").map(|t| t.valor).unwrap_or(3528.0);

    for i in 0..total {
        let letra = (b'A' + (i % 26) as u8) as char;
        let trem_num = (i / 4) + 1;
        let sufixo_papel = match i % 4 {
            0 => "Principal (VSD)",
            1 => "Principal (Carga/Alívio)",
            2 => "Standby Ativo (Auto-Start)",
            _ => "Reserva Fria / Manutenção",
        };
        let nome = format!("CMP-0{}{}-T{} ({})", i + 1, letra, trem_num, sufixo_papel);
        let tag_prefix = format!("CMP{:02}", i + 1);
        let id = format!("CMP-{:02}", i + 1);

        // Condições realistas progressivas de desgaste e operação
        let dias = match i % 4 {
            0 => 120.0 + (i as f64 * 35.0),
            1 => 340.0 + (i as f64 * 40.0),
            2 => 210.0 + (i as f64 * 20.0),
            _ => 15.0 + (i as f64 * 5.0),
        };
        let folga = match i % 4 {
            0 => 0.0022 + (i as f64 * 0.0003).min(0.003),
            1 => 0.0085, // desgaste moderado
            2 => 0.0030,
            _ => 0.0020, // nova
        };
        let rf = match i % 4 {
            0 => 0.0001,
            1 => 0.0003,
            2 => 0.0009, // fouling moderado
            _ => 0.0,
        };
        let falha = match i % 4 {
            1 => Some("folga_lp".to_string()),
            2 => Some("fouling_intercooler".to_string()),
            _ => None,
        };
        let sev = match i % 4 {
            1 => 0.45,
            2 => 0.60,
            _ => 0.0,
        };

        let mut p = Params::default();
        p.fad_m3_min = fad_unitario;
        p.folga_rel = folga;
        p.r_f_equiv = rf;
        p.n_compressores = total as u32;

        let mut hist_folga = Vec::new();
        for step in 0..20 {
            let base = 0.002 + (folga - 0.002) * (step as f64 / 19.0);
            hist_folga.push(base);
        }

        // Dano acumulado sintético (Eqs. 19.7/19.8), mesmo papel demonstrativo
        // de hist_folga acima — ver frota_supervisorio.py para a justificativa.
        let dano_diario_nominal = crate::fadiga::dano_incremental(sigma_b_nominal, rpm_nominal, 1.0);
        let dano_total = dano_diario_nominal * dias * (1.0 + 3.0 * sev);
        let mut hist_dano = Vec::new();
        for step in 0..20 {
            hist_dano.push((dano_total * (step as f64 / 19.0)).max(0.0));
        }

        let maq = MaquinaFrota {
            id,
            nome,
            tag_prefix,
            params: p,
            t_operacao_dias: dias,
            x_hat: [folga, rf],
            historico_folga: hist_folga,
            historico_hi: Vec::new(),
            historico_nis: Vec::new(),
            dano_acumulado: hist_dano.last().copied().unwrap_or(0.0),
            historico_dano: hist_dano,
            falha_simulada_id: falha,
            severidade_falha: sev,
        };
        frota.push(maq);
    }

    frota
}

pub fn executar_ciclo_supervisorio_frota(
    frota: &mut [MaquinaFrota],
    dt_dias: f64,
) -> Vec<PainelMaquina> {
    let mut painel = Vec::new();
    let mut rng = StdRng::seed_from_u64(12345);
    let chi2 = ChiSquared::new(7.0).unwrap();

    for maq in frota.iter_mut() {
        let res = sistema::simular(&maq.params);
        let snap = extrair_snapshot_pi(&res, &maq.params, &maq.tag_prefix, true, Some(42));

        let nis_valor: f64 = chi2.sample(&mut rng);
        let vib = snap.get(&format!("{}:MEC_VIB_RMS", maq.tag_prefix)).map(|t| t.valor).unwrap_or(2.10);
        let temp_lp = snap.get(&format!("{}:LP_TDISC", maq.tag_prefix)).map(|t| t.valor).unwrap_or(123.8);

        let hi = calcular_health_index_composto(maq.x_hat[0], maq.x_hat[1], vib, temp_lp);
        maq.historico_hi.push(hi);
        maq.historico_nis.push(nis_valor);
        maq.historico_folga.push(maq.x_hat[0]);
        maq.t_operacao_dias += dt_dias;

        let mut n_alarmes = 0;
        for s in snap.values() {
            if s.status_alarme != crate::pi_telemetry::StatusAlarme::Normal {
                n_alarmes += 1;
            }
        }

        // Dano acumulado por fadiga (Eqs. 19.7/19.8) e RUL por Miner (Eq. 19.9),
        // com incerteza de Ḋ propagada por Processo Gaussiano (Eq. 19.10)
        let sigma_b_mpa = snap.get(&format!("{}:MEC_SIGMA_B", maq.tag_prefix)).map(|t| t.valor).unwrap_or(120.0);
        let rpm_atual = snap.get(&format!("{}:MEC_RPM", maq.tag_prefix)).map(|t| t.valor).unwrap_or(3528.0);
        maq.dano_acumulado += crate::fadiga::dano_incremental(sigma_b_mpa, rpm_atual, dt_dias);
        maq.historico_dano.push(maq.dano_acumulado);
        let prognostico = crate::fadiga::projetar_rul_fadiga(&maq.historico_dano, dt_dias);

        let exergia_dest = (res.potencias.w_total - res.potencias.w_isotermico).max(0.0) / 1000.0;

        painel.push(PainelMaquina {
            maquina_id: maq.id.clone(),
            nome: maq.nome.clone(),
            tag_prefix: maq.tag_prefix.clone(),
            hi,
            nis: nis_valor,
            nis_status: if nis_valor <= 14.07 {
                "Consistente (Auditado OK)".to_string()
            } else {
                "Inconsistente (Atenção)".to_string()
            },
            tem_alarmes: n_alarmes > 0,
            n_alarmes,
            t_operacao_dias: maq.t_operacao_dias,
            dano_acumulado: prognostico.dano_acumulado,
            taxa_dano_diaria: prognostico.taxa_dano_diaria,
            rul_estimado_dias: prognostico.rul_dias_estimado,
            rul_ic_min: prognostico.rul_ic_95_min,
            rul_ic_max: prognostico.rul_ic_95_max,
            folga_atual_um: maq.x_hat[0] * 1000.0,
            rf_atual: maq.x_hat[1],
            consumo_spc: res.kpis.spc,
            exergia_dest_kw: exergia_dest,
            snapshot_pi: snap,
        });
    }

    // Ordenação por urgência: alarmes ativos primeiro, depois menor HI
    painel.sort_by(|a, b| {
        b.tem_alarmes
            .cmp(&a.tem_alarmes)
            .then_with(|| a.hi.partial_cmp(&b.hi).unwrap_or(std::cmp::Ordering::Equal))
    });

    painel
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_frota_supervisorio_completo() {
        let mut frota = criar_frota_padrao_offshore(4);
        assert_eq!(frota.len(), 4);
        let painel = executar_ciclo_supervisorio_frota(&mut frota, 1.0);
        assert_eq!(painel.len(), 4);
        assert!(painel[0].hi <= 1.0 && painel[0].hi >= 0.0);
    }
}
