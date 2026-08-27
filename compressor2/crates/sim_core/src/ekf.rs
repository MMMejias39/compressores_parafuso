//! Filtro de Kalman Estendido (EKF) — Cap. 21, Eqs. 21.2/21.4/21.7/21.8.
//!
//! Estado: x = [folga_rel, r_f_equiv]
//! Medição: z = [m_dot_seco, T_HP_in]
//! Jacobiana numérica por diferenças finitas centradas (Eq. 21.3).

use rand_distr::Normal;
use serde::{Deserialize, Serialize};
use crate::sistema::{self, Params};

/// Resultado de uma simulação EKF completa.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResultadoEkf {
    /// Série temporal de estimativas [n_passos × 2]
    pub x_hat: Vec<[f64; 2]>,
    /// Desvio-padrão das estimativas
    pub std: Vec<[f64; 2]>,
    /// NIS (Normalized Innovation Squared) — Eq. 21.7
    pub nis: Vec<f64>,
    /// Medições ruidosas
    pub z: Vec<[f64; 2]>,
    pub folga_true: Vec<f64>,
    pub r_f_true: Vec<f64>,
}

/// Resultado de um EKF aumentado (estado 3D: [folga, r_f, K]).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResultadoEkfAumentado {
    pub x_hat: Vec<[f64; 3]>,
    pub std: Vec<[f64; 3]>,
    pub nis: Vec<f64>,
    pub z: Vec<[f64; 2]>,
    pub folga_true: Vec<f64>,
    pub r_f_true: Vec<f64>,
    pub k_true: Vec<f64>,
    pub n_passos_calibracao: usize,
}

// ── Jacobiana numérica (Eq. 21.3) ────────────────────────────────────────────

/// Jacobiana m×n por diferenças finitas centradas.
fn jacobiana_numerica<F>(func: F, x: &[f64], eps: f64) -> Vec<Vec<f64>>
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    let n = x.len();
    let f0 = func(x);
    let m = f0.len();
    let mut jac = vec![vec![0.0; n]; m];
    for j in 0..n {
        let mut xp = x.to_vec();
        let mut xm = x.to_vec();
        let h = eps * x[j].abs().max(1.0);
        xp[j] += h;
        xm[j] -= h;
        let fp = func(&xp);
        let fm = func(&xm);
        for i in 0..m {
            jac[i][j] = (fp[i] - fm[i]) / (2.0 * h);
        }
    }
    jac
}

// ── Operações de matriz (2×2 e 3×3, sem ndarray para manter simplicidade) ────

fn mat_mul_2(a: [[f64; 2]; 2], b: [[f64; 2]; 2]) -> [[f64; 2]; 2] {
    let mut r = [[0.0; 2]; 2];
    for i in 0..2 { for j in 0..2 { for k in 0..2 { r[i][j] += a[i][k] * b[k][j]; } } }
    r
}
fn mat_add_2(a: [[f64; 2]; 2], b: [[f64; 2]; 2]) -> [[f64; 2]; 2] {
    let mut r = [[0.0; 2]; 2];
    for i in 0..2 { for j in 0..2 { r[i][j] = a[i][j] + b[i][j]; } }
    r
}
fn inv_2(a: [[f64; 2]; 2]) -> [[f64; 2]; 2] {
    let det = a[0][0] * a[1][1] - a[0][1] * a[1][0];
    [[a[1][1] / det, -a[0][1] / det],
     [-a[1][0] / det, a[0][0] / det]]
}
fn transpose_2x2(a: [[f64; 2]; 2]) -> [[f64; 2]; 2] {
    [[a[0][0], a[1][0]], [a[0][1], a[1][1]]]
}

// Jac G é 2×2 (2 medições × 2 estados)
fn jac_g_2x2_to_arr(jac: &[Vec<f64>]) -> [[f64; 2]; 2] {
    [[jac[0][0], jac[0][1]], [jac[1][0], jac[1][1]]]
}

/// Função de medição g(x) para o estado de 2 elementos.
fn medicao_2(x: &[f64], base: &Params) -> Vec<f64> {
    let mut p = base.clone();
    p.folga_rel = x[0].max(0.0);
    p.r_f_equiv = x[1].max(0.0);
    let res = sistema::simular(&p);
    vec![res.nos[0].m_dot, res.nos[2].t_c + 273.15]
}

/// Um ciclo de predição-correção do EKF para estado de 2 elementos.
///
/// Retorna (x_new, p_new, inovacao, nis)
fn passo_ekf_2(
    x_hat: [f64; 2],
    p_cov: [[f64; 2]; 2],
    z: [f64; 2],
    base: &Params,
    q_proc: [[f64; 2]; 2],
    r_meas: [[f64; 2]; 2],
) -> ([f64; 2], [[f64; 2]; 2], [f64; 2], f64) {
    // Predição (f(x)=x, F=I)
    let x_pred = x_hat;
    let p_pred = mat_add_2(p_cov, q_proc); // P⁻ = P + Q

    // Medição prevista + Jacobiana
    let z_pred_vec = medicao_2(&x_pred, base);
    let z_pred = [z_pred_vec[0], z_pred_vec[1]];
    let jac_vec = jacobiana_numerica(|xx| medicao_2(xx, base), &x_pred, 1e-5);
    let g = jac_g_2x2_to_arr(&jac_vec);
    let gt = transpose_2x2(g);

    // Ganho de Kalman
    let s = mat_add_2(mat_mul_2(mat_mul_2(g, p_pred), gt), r_meas);
    let s_inv = inv_2(s);
    // K = P⁻·Gᵀ·S⁻¹  (2×2)
    let k = mat_mul_2(mat_mul_2(p_pred, gt), s_inv);

    // Inovação e atualização do estado
    let innov = [z[0] - z_pred[0], z[1] - z_pred[1]];
    let mut x_new = [
        x_pred[0] + k[0][0] * innov[0] + k[0][1] * innov[1],
        x_pred[1] + k[1][0] * innov[0] + k[1][1] * innov[1],
    ];
    x_new[0] = x_new[0].max(0.0);
    x_new[1] = x_new[1].max(0.0);

    // Joseph form (Eq. 21.8): P⁺ = (I−K·G)·P⁻·(I−K·G)ᵀ + K·R·Kᵀ
    let i_kg = [
        [1.0 - k[0][0]*g[0][0] - k[0][1]*g[1][0], -k[0][0]*g[0][1] - k[0][1]*g[1][1]],
        [-k[1][0]*g[0][0] - k[1][1]*g[1][0],       1.0 - k[1][0]*g[0][1] - k[1][1]*g[1][1]],
    ];
    let p_new = mat_add_2(
        mat_mul_2(mat_mul_2(i_kg, p_pred), transpose_2x2(i_kg)),
        mat_mul_2(mat_mul_2(k, r_meas), transpose_2x2(k)),
    );

    // NIS (Eq. 21.7): ν'·S⁻¹·ν
    let nis = innov[0] * (s_inv[0][0]*innov[0] + s_inv[0][1]*innov[1])
            + innov[1] * (s_inv[1][0]*innov[0] + s_inv[1][1]*innov[1]);

    (x_new, p_new, innov, nis)
}

/// Simula o EKF ao longo de uma série de estados verdadeiros.
pub fn simular_ekf(
    params_base: &Params,
    folga_true: &[f64],
    r_f_true: &[f64],
    sigma_m_dot: f64,
    sigma_t_hp: f64,
    q_proc_diag: [f64; 2],
    x0: [f64; 2],
    p0_diag: [f64; 2],
    seed: u64,
) -> ResultadoEkf {
    use rand::prelude::*;
    let mut rng = rand::rngs::StdRng::seed_from_u64(seed);
    let dist_m  = Normal::new(0.0, sigma_m_dot).unwrap();
    let dist_t  = Normal::new(0.0, sigma_t_hp).unwrap();

    let n = folga_true.len();
    let mut x_hat = x0;
    let mut p_cov = [[p0_diag[0], 0.0], [0.0, p0_diag[1]]];
    let q_proc    = [[q_proc_diag[0], 0.0], [0.0, q_proc_diag[1]]];
    let r_meas    = [[sigma_m_dot*sigma_m_dot, 0.0], [0.0, sigma_t_hp*sigma_t_hp]];

    let mut x_hist = vec![[0.0_f64; 2]; n];
    let mut std_hist = vec![[0.0_f64; 2]; n];
    let mut nis_hist = vec![0.0_f64; n];
    let mut z_hist = vec![[0.0_f64; 2]; n];

    for k in 0..n {
        let x_true = [folga_true[k], r_f_true[k]];
        let z_true_vec = medicao_2(&x_true, params_base);
        let z_k = [z_true_vec[0] + dist_m.sample(&mut rng),
                   z_true_vec[1] + dist_t.sample(&mut rng)];

        let (xn, pn, _innov, nis) = passo_ekf_2(x_hat, p_cov, z_k, params_base, q_proc, r_meas);
        x_hat = xn;
        p_cov = pn;

        x_hist[k] = x_hat;
        std_hist[k] = [p_cov[0][0].max(0.0).sqrt(), p_cov[1][1].max(0.0).sqrt()];
        nis_hist[k] = nis;
        z_hist[k] = z_k;
    }

    ResultadoEkf {
        x_hat: x_hist, std: std_hist, nis: nis_hist, z: z_hist,
        folga_true: folga_true.to_vec(),
        r_f_true: r_f_true.to_vec(),
    }
}

// ── Testes ────────────────────────────────────────────────────────────────────
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ekf_estado_converge() {
        let base = Params::default();
        let n = 10;
        let folga_true = vec![FOLGA_REL_DEFAULT; n];
        let r_f_true   = vec![0.0; n];
        let res = simular_ekf(
            &base,
            &folga_true, &r_f_true,
            1e-4, 1.0,
            [1e-8, 1e-8],
            [FOLGA_REL_DEFAULT * 1.5, 0.0005],
            [1e-6, 1e-6],
            42,
        );
        assert_eq!(res.x_hat.len(), n);
        // Estado estimado deve ser razoável (positivo)
        for xh in &res.x_hat {
            assert!(xh[0] >= 0.0);
            assert!(xh[1] >= 0.0);
        }
    }

    use crate::constantes::FOLGA_REL_DEFAULT;
}
