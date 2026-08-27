//! Otimização por Enxame de Partículas (PSO) — Cap. 24, Eqs. 24.3/24.4.
//!
//! Peso de inércia decrescente linearmente ao longo das iterações:
//! w_ini (~0,9) → w_fim (~0,4), favorecendo exploração ampla depois concentração.

use rand::prelude::*;
use serde::{Deserialize, Serialize};

/// Resultado da otimização PSO.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResultadoPso {
    pub g_best: Vec<f64>,
    pub g_best_custo: f64,
    pub historico_custo: Vec<f64>,
}

/// Minimiza `func_custo(x)` dentro de [limite_inf, limite_sup].
///
/// - Eq. 24.3: v_new = w·v + c1·r1·(p_best − x) + c2·r2·(g_best − x)
/// - Eq. 24.4: x_new = clip(x + v_new, inf, sup)
pub fn otimizar<F>(
    func_custo: F,
    limite_inf: &[f64],
    limite_sup: &[f64],
    n_particulas: usize,
    n_iter: usize,
    w_ini: f64,
    w_fim: f64,
    c1: f64,
    c2: f64,
    seed: u64,
) -> ResultadoPso
where
    F: Fn(&[f64]) -> f64,
{
    let n_dim = limite_inf.len();
    assert_eq!(n_dim, limite_sup.len(), "limites de dimensões diferentes");
    let mut rng = StdRng::seed_from_u64(seed);

    // Inicializar posições e velocidades
    let mut x: Vec<Vec<f64>> = (0..n_particulas)
        .map(|_| {
            (0..n_dim)
                .map(|d| rng.gen_range(limite_inf[d]..=limite_sup[d]))
                .collect()
        })
        .collect();
    let mut v: Vec<Vec<f64>> = vec![vec![0.0; n_dim]; n_particulas];
    let mut custo: Vec<f64> = x.iter().map(|xi| func_custo(xi)).collect();

    let mut p_best = x.clone();
    let mut p_best_custo = custo.clone();

    let (mut g_best_idx, mut g_best_custo) = p_best_custo
        .iter()
        .enumerate()
        .min_by(|a, b| a.1.partial_cmp(b.1).unwrap())
        .map(|(i, &c)| (i, c))
        .unwrap();
    let mut g_best = p_best[g_best_idx].clone();
    let mut historico = vec![0.0_f64; n_iter];

    for t in 0..n_iter {
        let w = w_ini + (w_fim - w_ini) * t as f64 / (n_iter - 1).max(1) as f64;

        for i in 0..n_particulas {
            for d in 0..n_dim {
                let r1: f64 = rng.gen();
                let r2: f64 = rng.gen();
                // Eq. 24.3
                v[i][d] = w * v[i][d]
                    + c1 * r1 * (p_best[i][d] - x[i][d])
                    + c2 * r2 * (g_best[d]    - x[i][d]);
                // Eq. 24.4
                x[i][d] = (x[i][d] + v[i][d])
                    .max(limite_inf[d])
                    .min(limite_sup[d]);
            }
            custo[i] = func_custo(&x[i]);
            if custo[i] < p_best_custo[i] {
                p_best_custo[i] = custo[i];
                p_best[i] = x[i].clone();
            }
        }

        // Atualizar g_best
        if let Some((idx, &c)) = p_best_custo
            .iter()
            .enumerate()
            .min_by(|a, b| a.1.partial_cmp(b.1).unwrap())
        {
            if c < g_best_custo {
                g_best_custo = c;
                g_best_idx = idx;
                g_best = p_best[g_best_idx].clone();
            }
        }
        historico[t] = g_best_custo;
    }

    ResultadoPso { g_best, g_best_custo, historico_custo: historico }
}

// ── Testes ────────────────────────────────────────────────────────────────────
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pso_minimiza_quadratico() {
        // Minimizar f(x,y) = x² + y² → ótimo em (0,0)
        let res = otimizar(
            |x| x[0] * x[0] + x[1] * x[1],
            &[-5.0, -5.0],
            &[5.0,   5.0],
            30, 100, 0.9, 0.4, 2.0, 2.0, 42,
        );
        assert!(res.g_best_custo < 0.01, "custo = {}", res.g_best_custo);
        assert!((res.g_best[0]).abs() < 0.2);
        assert!((res.g_best[1]).abs() < 0.2);
    }

    #[test]
    fn test_pso_historico_nao_crescente() {
        let res = otimizar(
            |x| x[0] * x[0],
            &[-10.0], &[10.0],
            20, 50, 0.9, 0.4, 2.0, 2.0, 0,
        );
        // g_best é não-crescente
        for w in res.historico_custo.windows(2) {
            assert!(w[0] >= w[1] - 1e-12, "histórico cresceu: {} → {}", w[0], w[1]);
        }
    }
}
