//! Fadiga do dente de engrenagem por acúmulo de dano — Cap. 19, Eqs. 19.6-19.10.
//!
//! Espelha `aplicativo/compressor_sim/fadiga.py`. Substitui, em 27/09/2026, o
//! RUL probabilístico anterior (regressão linear da folga estimada) pela
//! Regra de Palmgren-Miner sobre a curva S-N de Basquin, com incerteza da
//! taxa de acúmulo de dano propagada por Processo Gaussiano.
//!
//! Cada ciclo diário do supervisório de frota é tratado como um único nível
//! de tensão constante (sem histórico de carga vibratória de alta frequência
//! que justificasse contagem por rainflow) — número de ciclos de carga no
//! período é aproximado pelo número de rotações do eixo no período.
//!
//! O EHI (Eq. 19.6) não está implementado neste crate: depende do erro de
//! reconstrução de um VAE (Eq. 20.4/22.5), e a Parte II em Rust cobre hoje
//! só EKF/MPC/PSO — VAE/PIML seguem só no app Python (ver CONTEXTO_app.md).

use crate::constantes as c;

/// Ajusta (C, b_f) da Eq. 19.8 a partir dos dois pontos de referência
/// ASSUMIDOS em `constantes.rs`.
pub fn parametros_basquin() -> (f64, f64) {
    let sigma1 = c::SIGMA_REF_BAIXO_CICLO_MPA;
    let n1 = c::N_REF_BAIXO_CICLO;
    let sigma2 = c::SIGMA_B_ADM_MPA;
    let n2 = c::N_REF_ENDURANCE;
    let b_f = (n2 / n1).ln() / (sigma1 / sigma2).ln();
    let cc = n1 * sigma1.powf(b_f);
    (cc, b_f)
}

/// Incremento de dano ΔD no período (Eqs. 19.7/19.8), tratando `sigma_b_mpa`
/// como um único nível de tensão constante durante `dt_dias`.
pub fn dano_incremental(sigma_b_mpa: f64, rpm: f64, dt_dias: f64) -> f64 {
    let (cc, b_f) = parametros_basquin();
    let sigma = sigma_b_mpa.max(1.0);
    let n_i = rpm.max(0.0) * 60.0 * 24.0 * dt_dias.max(0.0);
    let n_falha = cc * sigma.powf(-b_f);
    if n_falha > 0.0 { n_i / n_falha } else { 0.0 }
}

fn kernel_gp(a: f64, b: f64, sigma_f: f64, ell: f64) -> f64 {
    let d = a - b;
    sigma_f * sigma_f * (-(d * d) / (2.0 * ell * ell)).exp()
}

/// Resolve o sistema linear K x = b por eliminação gaussiana com pivotamento
/// parcial — matrizes pequenas (poucas dezenas de pontos históricos), não
/// vale a pena trazer uma dependência de álgebra linear só para isto.
fn resolver_linear(mat: &[Vec<f64>], rhs: &[f64]) -> Vec<f64> {
    let n = rhs.len();
    let mut a: Vec<Vec<f64>> = mat.iter().map(|row| row.clone()).collect();
    let mut b = rhs.to_vec();

    for k in 0..n {
        let mut piv = k;
        for i in (k + 1)..n {
            if a[i][k].abs() > a[piv][k].abs() {
                piv = i;
            }
        }
        a.swap(k, piv);
        b.swap(k, piv);

        let pivo = a[k][k];
        if pivo.abs() < 1e-14 {
            continue;
        }
        for i in (k + 1)..n {
            let fator = a[i][k] / pivo;
            for j in k..n {
                a[i][j] -= fator * a[k][j];
            }
            b[i] -= fator * b[k];
        }
    }

    let mut x = vec![0.0; n];
    for i in (0..n).rev() {
        let mut soma = b[i];
        for j in (i + 1)..n {
            soma -= a[i][j] * x[j];
        }
        x[i] = if a[i][i].abs() > 1e-14 { soma / a[i][i] } else { 0.0 };
    }
    x
}

/// Média e variância preditivas de Ḋ(t*) por regressão de Processo
/// Gaussiano (Eq. 19.10) sobre o histórico de taxas de dano observadas.
pub fn taxa_dano_gp(
    t_obs_dias: &[f64],
    taxas_obs: &[f64],
    t_estrela_dias: f64,
    sigma_f: f64,
    ell: f64,
    sigma_n: f64,
) -> (f64, f64) {
    let n = t_obs_dias.len();
    if n == 0 {
        return (1e-6, sigma_f * sigma_f);
    }

    let mut k_mat = vec![vec![0.0; n]; n];
    for i in 0..n {
        for j in 0..n {
            k_mat[i][j] = kernel_gp(t_obs_dias[i], t_obs_dias[j], sigma_f, ell);
        }
        k_mat[i][i] += sigma_n * sigma_n;
    }

    let k_star: Vec<f64> = t_obs_dias
        .iter()
        .map(|&t| kernel_gp(t, t_estrela_dias, sigma_f, ell))
        .collect();

    let alpha = resolver_linear(&k_mat, taxas_obs);
    let media: f64 = k_star.iter().zip(alpha.iter()).map(|(a, b)| a * b).sum();

    let v = resolver_linear(&k_mat, &k_star);
    let k_ss = kernel_gp(t_estrela_dias, t_estrela_dias, sigma_f, ell);
    let variancia = (k_ss - k_star.iter().zip(v.iter()).map(|(a, b)| a * b).sum::<f64>()).max(0.0);

    (media, variancia)
}

pub struct PrognosticoRul {
    pub rul_dias_estimado: f64,
    pub rul_ic_95_min: f64,
    pub rul_ic_95_max: f64,
    pub taxa_dano_diaria: f64,
    pub dano_acumulado: f64,
    pub confiabilidade: String,
}

/// RUL por acúmulo de dano (Eq. 19.9), com IC 95% propagado da variância de
/// Ḋ estimada por Processo Gaussiano (Eq. 19.10).
pub fn projetar_rul_fadiga(historico_dano: &[f64], dt_dias: f64) -> PrognosticoRul {
    let n = historico_dano.len();
    if n < 3 {
        return PrognosticoRul {
            rul_dias_estimado: 180.0,
            rul_ic_95_min: 120.0,
            rul_ic_95_max: 240.0,
            taxa_dano_diaria: 1e-4,
            dano_acumulado: historico_dano.last().copied().unwrap_or(0.0),
            confiabilidade: "Baixa (poucos pontos históricos)".to_string(),
        };
    }

    // Eixo de tempo por índice, não `dt_dias` do parâmetro — ver fadiga.py
    // para a justificativa (chamada de "espiar" o painel com dt_dias=0.0).
    let t: Vec<f64> = (0..n).map(|i| i as f64).collect();
    let taxas_obs: Vec<f64> = (1..n)
        .map(|i| historico_dano[i] - historico_dano[i - 1])
        .collect();
    let t_obs_taxas: Vec<f64> = t[1..].to_vec();

    let t_estrela = t[n - 1];
    let (mut media_taxa, var_taxa) = taxa_dano_gp(
        &t_obs_taxas, &taxas_obs, t_estrela,
        c::GP_SIGMA_F, c::GP_ELL_DIAS, c::GP_SIGMA_N,
    );
    media_taxa = media_taxa.max(1e-7);

    let dano_atual = historico_dano[n - 1];
    let dano_restante = (1.0 - dano_atual).max(0.0);
    let rul_central = dano_restante / media_taxa;

    let desvio = var_taxa.sqrt();
    // Piso relativo, não 1e-7 absoluto — ver fadiga.py para a justificativa
    // (sigma_b elevado a b_f~8 na Eq. 19.8 amplifica ruído pequeno).
    let taxa_min = (0.1 * media_taxa).max(media_taxa - 1.96 * desvio);
    let taxa_max = media_taxa + 1.96 * desvio;

    let rul_min = if taxa_max > 0.0 { dano_restante / taxa_max } else { rul_central };
    let rul_max = if taxa_min > 0.0 { dano_restante / taxa_min } else { rul_central };

    // Teto de exibição/decisão (constantes::RUL_TETO_DIAS) — ver fadiga.py.
    let teto = c::RUL_TETO_DIAS;
    let rul_central = rul_central.min(teto);
    let rul_min = rul_min.min(teto);
    let rul_max = rul_max.min(teto);

    PrognosticoRul {
        rul_dias_estimado: rul_central,
        rul_ic_95_min: rul_min.max(0.0),
        rul_ic_95_max: rul_max.max(rul_central),
        taxa_dano_diaria: media_taxa,
        dano_acumulado: dano_atual,
        confiabilidade: if n >= 15 { "Alta".to_string() } else { "Média".to_string() },
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parametros_basquin_positivos() {
        let (cc, b_f) = parametros_basquin();
        assert!(cc > 0.0);
        assert!(b_f > 0.0);
    }

    #[test]
    fn test_dano_incremental_cresce_com_tensao() {
        let d_baixo = dano_incremental(120.0, 3528.0, 1.0);
        let d_alto = dano_incremental(250.0, 3528.0, 1.0);
        assert!(d_baixo > 0.0);
        assert!(d_alto > d_baixo);
    }

    #[test]
    fn test_dano_incremental_zero_sem_rotacao() {
        assert_eq!(dano_incremental(120.0, 0.0, 1.0), 0.0);
    }

    #[test]
    fn test_projetar_rul_fadiga_decresce_com_dano() {
        let hist_baixo: Vec<f64> = (0..20).map(|i| 0.05 * i as f64 / 19.0).collect();
        let hist_alto: Vec<f64> = (0..20).map(|i| 0.60 * i as f64 / 19.0).collect();
        let r_baixo = projetar_rul_fadiga(&hist_baixo, 1.0);
        let r_alto = projetar_rul_fadiga(&hist_alto, 1.0);
        assert!(r_alto.dano_acumulado > r_baixo.dano_acumulado);
        assert!(r_alto.rul_dias_estimado < r_baixo.rul_dias_estimado);
        assert!(r_baixo.rul_ic_95_min <= r_baixo.rul_dias_estimado);
        assert!(r_baixo.rul_dias_estimado <= r_baixo.rul_ic_95_max);
        // Piso relativo do RUL: IC max não deve explodir muito além de 10x o central
        assert!(r_baixo.rul_ic_95_max <= r_baixo.rul_dias_estimado * 10.0 + 1.0);
    }

    #[test]
    fn test_projetar_rul_fadiga_historico_curto() {
        let r = projetar_rul_fadiga(&[0.0, 0.01], 1.0);
        assert!(r.confiabilidade.starts_with("Baixa"));
        assert!(r.rul_dias_estimado > 0.0);
    }
}
