//! Controle Preditivo Baseado em Modelo (MPC) — Cap. 24, Eqs. 24.1/24.2.
//!
//! Horizonte deslizante sobre o balanço de massa do vaso/rede (Eq. 16.4/13.4).

use serde::{Deserialize, Serialize};
use crate::constantes::R_AR;
use crate::dinamica::perfil_demanda;

fn propagar_pressao(
    p0: f64,
    x_c_seq: &[f64],
    m_dot_cap: f64,
    dem_seq: &[f64],
    t_k: f64,
    v_vaso: f64,
    dt: f64,
) -> Vec<f64> {
    let mut p = Vec::with_capacity(x_c_seq.len() + 1);
    p.push(p0);
    for k in 0..x_c_seq.len() {
        let m_in = x_c_seq[k] * m_dot_cap;
        let p_novo = p[k] + R_AR * t_k / v_vaso * (m_in - dem_seq[k]) * dt;
        p.push(p_novo.max(0.5e5));
    }
    p
}

fn custo_horizonte(
    x_c_seq: &[f64],
    p0: f64,
    dem_seq: &[f64],
    m_dot_cap: f64,
    t_k: f64,
    v_vaso: f64,
    dt: f64,
    p_ref: f64,
    rho: f64,
    x_c_ant: f64,
) -> f64 {
    let p_traj = propagar_pressao(p0, x_c_seq, m_dot_cap, dem_seq, t_k, v_vaso, dt);
    let mut erro = 0.0;
    for i in 1..p_traj.len() {
        let diff = (p_traj[i] - p_ref) / p_ref;
        erro += diff * diff;
    }

    let mut esforco = 0.0;
    let mut prev_u = x_c_ant;
    for &u in x_c_seq {
        let du = u - prev_u;
        esforco += du * du;
        prev_u = u;
    }

    erro + rho * esforco
}

pub fn resolver_horizonte(
    p0: f64,
    dem_seq: &[f64],
    m_dot_cap: f64,
    t_k: f64,
    v_vaso: f64,
    dt: f64,
    p_ref: f64,
    rho: f64,
    x_c_ant: f64,
    x_c_min: f64,
) -> Vec<f64> {
    let n_h = dem_seq.len();
    let mut u = vec![x_c_ant; n_h];

    // Otimização via gradiente projetado com passo adaptativo
    let lr = 0.05;
    let eps = 1e-4;
    for _iter in 0..50 {
        let c0 = custo_horizonte(&u, p0, dem_seq, m_dot_cap, t_k, v_vaso, dt, p_ref, rho, x_c_ant);
        let mut grad = vec![0.0; n_h];
        for j in 0..n_h {
            let old = u[j];
            u[j] = (old + eps).min(1.0);
            let c_plus = custo_horizonte(&u, p0, dem_seq, m_dot_cap, t_k, v_vaso, dt, p_ref, rho, x_c_ant);
            grad[j] = (c_plus - c0) / (u[j] - old).max(1e-9);
            u[j] = old;
        }

        for j in 0..n_h {
            u[j] = (u[j] - lr * grad[j]).clamp(x_c_min, 1.0);
        }
    }

    u
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResultadoMpc {
    pub t_min: Vec<f64>,
    pub p_bar: Vec<f64>,
    pub x_c: Vec<f64>,
    pub w_kw: Vec<f64>,
    pub m_dem: Vec<f64>,
}

pub fn simular_mpc(
    horizonte_min: f64,
    dt: f64,
    n_horizonte: usize,
    m_dot_cap: f64,
    v_vaso: f64,
    t_k: f64,
    p_set: f64,
    dem_base: f64,
    t_ev: (f64, f64),
    fator_ev: f64,
    rho: f64,
    x_c_min: f64,
    w_nom: f64,
    eta_vsd: f64,
) -> ResultadoMpc {
    let n = (horizonte_min * 60.0 / dt).round() as usize + 1;
    let t: Vec<f64> = (0..n).map(|i| i as f64 * dt).collect();
    let dem = perfil_demanda(&t, dem_base, t_ev, fator_ev);

    let mut p = p_set;
    let mut x_c_ant = if m_dot_cap > 0.0 {
        (dem[0] / m_dot_cap).clamp(x_c_min, 1.0)
    } else {
        0.0
    };

    let mut p_hist = vec![0.0; n];
    let mut x_c_hist = vec![0.0; n];
    let mut w_hist = vec![0.0; n];

    for i in 0..n {
        p_hist[i] = p;
        let fim = (i + n_horizonte).min(n);
        let mut dem_fut = dem[i..fim].to_vec();
        while dem_fut.len() < n_horizonte {
            dem_fut.push(*dem_fut.last().unwrap_or(&dem_base));
        }

        let x_c_seq = resolver_horizonte(
            p, &dem_fut, m_dot_cap, t_k, v_vaso, dt, p_set, rho, x_c_ant, x_c_min,
        );
        let x_c = x_c_seq[0].clamp(x_c_min, 1.0);
        x_c_hist[i] = x_c;
        w_hist[i] = w_nom * x_c / eta_vsd;

        if i < n - 1 {
            let m_in = x_c * m_dot_cap;
            p = (p + R_AR * t_k / v_vaso * (m_in - dem[i]) * dt).max(0.5e5);
        }
        x_c_ant = x_c;
    }

    ResultadoMpc {
        t_min: t.iter().map(|&s| s / 60.0).collect(),
        p_bar: p_hist.iter().map(|&pa| pa / 1e5).collect(),
        x_c: x_c_hist,
        w_kw: w_hist.iter().map(|&w| w / 1000.0).collect(),
        m_dem: dem,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mpc_executa() {
        let res = simular_mpc(
            2.0, 1.0, 5, 0.2, 2.0, 303.15, 8.0e5,
            0.15, (30.0, 60.0), 1.5, 0.1, 0.3, 50000.0, 0.95,
        );
        assert!(!res.t_min.is_empty());
        assert_eq!(res.t_min.len(), res.p_bar.len());
    }
}
