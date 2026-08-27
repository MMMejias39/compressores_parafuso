//! Ciclo de chaveamento das torres do secador PSA (Cap. 15).
//!
//! Generaliza a alternância para N torres em rodízio com 3 fases:
//! 1. Adsorvendo (Eq. 15.1)
//! 2. Regenerando (Eq. 15.12)
//! 3. Resfriando

use serde::{Deserialize, Serialize};
use crate::constantes::PDP_ALVO_C;
use crate::nucleo;

pub const TAXA_1A_ORDEM: f64 = 4.0;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KpisPsaCiclo {
    pub n_trocas: usize,
    pub q_min: f64,
    pub purga_media_kg_s: f64,
    pub t_ciclo_min: f64,
    pub n_adsorvendo_min: usize,
    pub tempo_sem_secagem_min: f64,
    pub pdp_saida_max_c: f64,
    pub agua_adsorvida_max_kg: f64,
    pub t_res_calc_min: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResultadoPsaCiclo {
    pub t_min: Vec<f64>,
    pub q_norm: Vec<Vec<f64>>,       // [n_vasos][n_passos]
    pub estado: Vec<Vec<String>>,    // [n_vasos][n_passos]
    pub temp_c: Vec<Vec<f64>>,       // [n_vasos][n_passos]
    pub m_purge_kg_s: Vec<f64>,
    pub n_adsorvendo: Vec<usize>,
    pub pdp_saida_c: Vec<f64>,
    pub agua_adsorvida_kg: Vec<Vec<f64>>,
    pub kpis: KpisPsaCiclo,
}

pub fn simular_ciclo_psa(
    horizonte_min: f64,
    m_dot_ar: f64,
    t_ads_min: f64,
    t_regen_min: f64,
    t_resfriamento_min: f64,
    n_vasos: usize,
    k_ads: f64,
    p_low: f64,
    p_high: f64,
    fator_purga: f64,
    t_entrada_c: f64,
    delta_t_regen: f64,
    pdp_entrada_c: f64,
    capacidade_trabalho: f64,
    massa_leito_kg: f64,
    dt_min: f64,
) -> ResultadoPsaCiclo {
    let n_vasos = n_vasos.max(2);
    let t_ciclo = t_ads_min + t_regen_min + t_resfriamento_min;
    let n = (horizonte_min / dt_min).round() as usize + 1;
    let t: Vec<f64> = (0..n).map(|i| i as f64 * dt_min).collect();

    let w_in = nucleo::razao_umidade(pdp_entrada_c + 273.15, p_high, 1.0);
    let taxa_agua_kg_min = m_dot_ar * w_in * 60.0;
    let capacidade_leito_kg = massa_leito_kg * capacidade_trabalho;
    let t_res_min = capacidade_leito_kg / taxa_agua_kg_min.max(1e-12);

    let q_no_inicio_regen = (-k_ads * t_ads_min / t_res_min).exp();

    let mut q_norm = vec![vec![0.0_f64; n]; n_vasos];
    let mut estado = vec![vec![String::new(); n]; n_vasos];
    let mut temp_c = vec![vec![0.0_f64; n]; n_vasos];
    let mut agua_adsorvida_kg = vec![vec![0.0_f64; n]; n_vasos];

    for i in 0..n_vasos {
        let offset = i as f64 * t_ciclo / n_vasos as f64;
        for j in 0..n {
            let tj = t[j];
            let fase = (tj - offset).rem_euclid(t_ciclo);

            if fase < t_ads_min {
                estado[i][j] = "Adsorvendo".to_string();
                let q = (-k_ads * fase / t_res_min).exp();
                q_norm[i][j] = q;
                temp_c[i][j] = t_entrada_c;
            } else if fase < t_ads_min + t_regen_min {
                estado[i][j] = "Regenerando".to_string();
                let frac_regen = (fase - t_ads_min) / t_regen_min;
                let q = 1.0 - (1.0 - q_no_inicio_regen) * (-TAXA_1A_ORDEM * frac_regen).exp();
                q_norm[i][j] = q;
                temp_c[i][j] = t_entrada_c + delta_t_regen * (1.0 - (-TAXA_1A_ORDEM * frac_regen).exp());
            } else {
                estado[i][j] = "Resfriando".to_string();
                q_norm[i][j] = 1.0;
                let frac_resf = if t_resfriamento_min > 0.0 {
                    ((fase - t_ads_min - t_regen_min) / t_resfriamento_min).clamp(0.0, 1.0)
                } else {
                    1.0
                };
                temp_c[i][j] = t_entrada_c + delta_t_regen * (-TAXA_1A_ORDEM * frac_resf).exp();
            }
            agua_adsorvida_kg[i][j] = (1.0 - q_norm[i][j]) * capacidade_trabalho * massa_leito_kg;
        }
    }

    let mut n_adsorvendo = vec![0_usize; n];
    let mut n_regen = vec![0_usize; n];
    for j in 0..n {
        for i in 0..n_vasos {
            if estado[i][j] == "Adsorvendo" {
                n_adsorvendo[j] += 1;
            } else if estado[i][j] == "Regenerando" {
                n_regen[j] += 1;
            }
        }
    }

    let m_purge_kg_s: Vec<f64> = (0..n)
        .map(|j| m_dot_ar * (p_low / p_high) * fator_purga * n_regen[j] as f64)
        .collect();

    let mut n_trocas = 0;
    for i in 0..n_vasos {
        for j in 0..n - 1 {
            if estado[i][j] != "Regenerando" && estado[i][j + 1] == "Regenerando" {
                n_trocas += 1;
            }
        }
    }

    let q_min = (0..n)
        .filter(|&j| estado[0][j] == "Adsorvendo")
        .map(|j| q_norm[0][j])
        .fold(1.0_f64, f64::min);

    let tempo_sem_secagem_min = n_adsorvendo.iter().filter(|&&count| count == 0).count() as f64 * dt_min;

    let mut pdp_saida_c = vec![0.0_f64; n];
    for j in 0..n {
        let mut min_q = f64::INFINITY;
        let mut has_adsorvendo = false;
        for i in 0..n_vasos {
            if estado[i][j] == "Adsorvendo" {
                has_adsorvendo = true;
                if q_norm[i][j] < min_q {
                    min_q = q_norm[i][j];
                }
            }
        }
        let q_rel = if has_adsorvendo { min_q } else { 0.0 };
        pdp_saida_c[j] = PDP_ALVO_C + (pdp_entrada_c - PDP_ALVO_C) * (1.0 - q_rel);
    }

    let purga_media_kg_s = m_purge_kg_s.iter().sum::<f64>() / m_purge_kg_s.len() as f64;
    let n_adsorvendo_min = *n_adsorvendo.iter().min().unwrap_or(&0);
    let pdp_saida_max_c = pdp_saida_c.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let agua_adsorvida_max_kg = agua_adsorvida_kg
        .iter()
        .flat_map(|v| v.iter())
        .cloned()
        .fold(f64::NEG_INFINITY, f64::max);

    ResultadoPsaCiclo {
        t_min: t,
        q_norm,
        estado,
        temp_c,
        m_purge_kg_s,
        n_adsorvendo,
        pdp_saida_c,
        agua_adsorvida_kg,
        kpis: KpisPsaCiclo {
            n_trocas,
            q_min,
            purga_media_kg_s,
            t_ciclo_min: t_ciclo,
            n_adsorvendo_min,
            tempo_sem_secagem_min,
            pdp_saida_max_c,
            agua_adsorvida_max_kg,
            t_res_calc_min: t_res_min,
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_psa_ciclo_executa() {
        let res = simular_ciclo_psa(
            15.0, 0.2, 6.0, 4.0, 2.0, 2, 1.5, 1.0e5, 8.0e5, 0.15,
            30.0, 80.0, 15.0, 0.10, 200.0, 0.1,
        );
        assert_eq!(res.estado.len(), 2);
        assert!(res.kpis.t_ciclo_min == 12.0);
        assert!(res.kpis.pdp_saida_max_c <= 15.0);
    }
}
