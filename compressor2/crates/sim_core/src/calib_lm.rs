//! Calibração de Parâmetros de Engenharia via Levenberg-Marquardt (LM)
//!
//! Resolve o problema inverso não linear de mínimos quadrados:
//! \theta^* = \arg\min_{\theta} \sum_{i=1}^N || y_i - g(\theta, u_i) ||_W^2
//!
//! Ajusta parâmetros livres de catálogo/instalação como:
//! - k_folga (coeficiente de vazamento interno dos rotores)
//! - eta_mec (rendimento mecânico da carcaça e engrenagens)
//! - zeta_filtro (coeficiente de perda de carga do filtro de sucção)
//! - ua_inter_ref (capacitância térmica do intercooler)

use serde::{Deserialize, Serialize};
use crate::sistema::{simular, Params};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResultadoCalibLm {
    pub k_folga_estimado: f64,
    pub eta_mec_estimado: f64,
    pub sucesso: bool,
    pub n_iteracoes: usize,
    pub custo_final: f64,
    pub resíduo_medio_pct: f64,
}

/// Avalia a função direta de observação g(k_folga, eta_mec) para um ponto de operação.
/// Retorna [m_dot_seco, t_hp_in, w_total_kw].
fn avaliar_ponto(params_base: &Params, k_folga: f64, eta_mec: f64, pi_total: f64, t_amb_k: f64) -> [f64; 3] {
    let mut p = params_base.clone();
    p.k_folga = k_folga.max(0.001);
    p.eta_mec = eta_mec.clamp(0.50, 0.99);
    p.pi_total = pi_total;
    p.t_amb = t_amb_k;

    let res = simular(&p);
    [
        res.nos[0].m_dot,
        res.nos[2].t_c,
        res.potencias.w_total / 1000.0,
    ]
}

/// Executa a calibração Levenberg-Marquardt multivariada para estimar (k_folga, eta_mec).
pub fn calibrar_parametros_lm(
    params_base: &Params,
    entradas_pi_t_amb: &[(f64, f64)], // [(pi_total, t_amb_k)]
    medicoes_m_t_w: &[[f64; 3]],      // [[m_dot, t_hp_in, w_total_kw]]
    k_inicial: f64,
    eta_inicial: f64,
    max_iter: usize,
) -> ResultadoCalibLm {
    let n_pts = entradas_pi_t_amb.len();
    if n_pts == 0 || n_pts != medicoes_m_t_w.len() {
        return ResultadoCalibLm {
            k_folga_estimado: k_inicial,
            eta_mec_estimado: eta_inicial,
            sucesso: false,
            n_iteracoes: 0,
            custo_final: 999.0,
            resíduo_medio_pct: 100.0,
        };
    }

    let mut k_curr = k_inicial;
    let mut eta_curr = eta_inicial;
    let mut lambda = 1e-2;
    let eps_fd = 1e-5;

    let calc_residuos = |k: f64, eta: f64| -> Vec<f64> {
        let mut r = Vec::with_capacity(n_pts * 3);
        for i in 0..n_pts {
            let (pi, t_amb) = entradas_pi_t_amb[i];
            let z_pred = avaliar_ponto(params_base, k, eta, pi, t_amb);
            let z_med = medicoes_m_t_w[i];
            r.push((z_pred[0] - z_med[0]) / z_med[0].abs().max(1e-4));
            r.push((z_pred[1] - z_med[1]) / z_med[1].abs().max(1e-4));
            r.push((z_pred[2] - z_med[2]) / z_med[2].abs().max(1e-4));
        }
        r
    };

    let mut res_curr = calc_residuos(k_curr, eta_curr);
    let mut custo_curr: f64 = 0.5 * res_curr.iter().map(|v| v * v).sum::<f64>();

    let mut iter_count = 0;
    for iter in 0..max_iter {
        iter_count = iter + 1;

        // Jacobiana numérica 2xM por diferenças finitas
        let m = res_curr.len();
        let mut j_mat = vec![[0.0; 2]; m];

        let res_dk = calc_residuos(k_curr + eps_fd, eta_curr);
        let res_deta = calc_residuos(k_curr, eta_curr + eps_fd);

        for i in 0..m {
            j_mat[i][0] = (res_dk[i] - res_curr[i]) / eps_fd;
            j_mat[i][1] = (res_deta[i] - res_curr[i]) / eps_fd;
        }

        // J^T * J (2x2) e J^T * r (2x1)
        let mut jtj = [[0.0; 2]; 2];
        let mut jtr = [0.0; 2];

        for i in 0..m {
            let j0 = j_mat[i][0];
            let j1 = j_mat[i][1];
            let r = res_curr[i];

            jtj[0][0] += j0 * j0;
            jtj[0][1] += j0 * j1;
            jtj[1][0] += j1 * j0;
            jtj[1][1] += j1 * j1;

            jtr[0] += j0 * r;
            jtr[1] += j1 * r;
        }

        // Amortecimento Levenberg-Marquardt: (J^T J + \lambda diag(J^T J)) \Delta \theta = -J^T r
        let a00 = jtj[0][0] * (1.0 + lambda) + 1e-8;
        let a01 = jtj[0][1];
        let a10 = jtj[1][0];
        let a11 = jtj[1][1] * (1.0 + lambda) + 1e-8;

        let b0 = -jtr[0];
        let b1 = -jtr[1];

        // Resolução analítica do sistema 2x2 por Cramer
        let det = a00 * a11 - a01 * a10;
        if det.abs() < 1e-12 {
            lambda *= 10.0;
            continue;
        }

        let delta_k = (b0 * a11 - b1 * a01) / det;
        let delta_eta = (a00 * b1 - a10 * b0) / det;

        let k_cand = (k_curr + delta_k).clamp(0.001, 0.30);
        let eta_cand = (eta_curr + delta_eta).clamp(0.50, 0.99);

        let res_cand = calc_residuos(k_cand, eta_cand);
        let custo_cand: f64 = 0.5 * res_cand.iter().map(|v| v * v).sum::<f64>();

        if custo_cand < custo_curr {
            // Sucesso: aceita passo e reduz lambda
            k_curr = k_cand;
            eta_curr = eta_cand;
            res_curr = res_cand;
            custo_curr = custo_cand;
            lambda = (lambda / 10.0).max(1e-7);

            if delta_k.abs() < 1e-6 && delta_eta.abs() < 1e-6 {
                break;
            }
        } else {
            // Rejeita passo e aumenta amortecimento
            lambda = (lambda * 10.0).min(1e7);
        }
    }

    let res_medio = (res_curr.iter().map(|v| v.abs()).sum::<f64>() / res_curr.len() as f64) * 100.0;

    ResultadoCalibLm {
        k_folga_estimado: k_curr,
        eta_mec_estimado: eta_curr,
        sucesso: custo_curr < 0.1,
        n_iteracoes: iter_count,
        custo_final: custo_curr,
        resíduo_medio_pct: res_medio,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lm_calibra_k_e_eta_mec() {
        let p_real = Params::default();
        let entradas = vec![
            (7.5, 293.15),
            (8.0, 298.15),
            (8.5, 303.15),
            (9.0, 308.15),
        ];

        // Gera dados sintéticos com os parâmetros reais (k_folga=0.05, eta_mec=0.95)
        let medicoes: Vec<[f64; 3]> = entradas
            .iter()
            .map(|&(pi, t_amb)| avaliar_ponto(&p_real, 0.05, 0.95, pi, t_amb))
            .collect();

        // Chutes iniciais perturbados (k0=0.12, eta0=0.85)
        let res = calibrar_parametros_lm(&p_real, &entradas, &medicoes, 0.12, 0.85, 50);

        assert!(res.sucesso);
        assert!((res.k_folga_estimado - 0.05).abs() < 0.005);
        assert!((res.eta_mec_estimado - 0.95).abs() < 0.005);
    }
}
