//! Subsistemas do trem de ar comprimido: intercooler, separador, PSA, vaso.
//!
//! Equações do livro compressores.tex. Convenções: SI, Pa, K.

use std::f64::consts::PI;
use crate::constantes::{CP_AR, R_AR};

// ── Intercooler / aftercooler (Caps. 10 e 12) ─────────────────────────────────

/// Diferença de temperatura média logarítmica [K] — Eq. 10.2
pub fn lmtd(dt1: f64, dt2: f64) -> f64 {
    if dt1 <= 0.0 || dt2 <= 0.0 { return 0.0; }
    if (dt1 - dt2).abs() < 1e-9 { return dt1; }
    (dt1 - dt2) / (dt1 / dt2).ln()
}

/// UA degradado por fouling [W/K] — forma UA da Eq. 10.5: 1/UA_real = 1/UA_proj + R_f
pub fn ua_com_fouling(ua_projeto: f64, r_f_equiv: f64) -> f64 {
    1.0 / (1.0 / ua_projeto + r_f_equiv)
}

/// Coeficiente global real com incrustação [W/(m²K)] — Eq. 10.5
pub fn u_real(u_clean: f64, r_f: f64) -> f64 {
    1.0 / (1.0 / u_clean + r_f)
}

/// Efetividade do trocador (lado quente = ar comprimido) — Eq. 10.3
pub fn efetividade(t_quente_in: f64, t_quente_out: f64, t_fria_in: f64) -> f64 {
    let span = t_quente_in - t_fria_in;
    if span <= 0.0 { return 0.0; }
    (t_quente_in - t_quente_out) / span
}

/// Efetividade ε-NTU para contracorrente — Eq. 12.4
pub fn eps_ntu_contracorrente(ntu: f64, c_r: f64) -> f64 {
    if (c_r - 1.0).abs() < 1e-9 { return ntu / (1.0 + ntu); }
    let e = (-ntu * (1.0 - c_r)).exp();
    (1.0 - e) / (1.0 - c_r * e)
}

/// Temperatura de saída do lado quente [K] via ε-NTU (aproximação C_r→0) — Eq. 12.4
pub fn saida_trocador(t_quente_in: f64, t_fria_in: f64, ua: f64, c_min: f64) -> f64 {
    let ntu = ua / c_min;
    let eps = 1.0 - (-ntu).exp();
    t_quente_in - eps * (t_quente_in - t_fria_in)
}

/// Taxa de transferência de calor [W] — Eq. 10.1: Q̇ = ṁ·cp·(T_in − T_out)
pub fn calor_trocado(m_dot: f64, cp: f64, t_in: f64, t_out: f64) -> f64 {
    m_dot * cp * (t_in - t_out)
}

// ── Separador de condensado (Cap. 14) ─────────────────────────────────────────

/// Água arrastada para jusante do separador [kg/s] — Eq. 14.4: ṁ_arr = ṁ_cond·(1−η_sep)
pub fn arraste(m_dot_cond: f64, eta_sep: f64) -> f64 {
    m_dot_cond * (1.0 - eta_sep)
}

// ── Secador PSA (Caps. 3 e 15) ────────────────────────────────────────────────

/// Vazão de purga de regeneração [kg/s] — Eq. 15.2: ṁ_purge = ṁ_in·(P_low/P_high)·φ
pub fn purga_psa(m_dot_in: f64, p_low: f64, p_high: f64, phi: f64) -> f64 {
    m_dot_in * (p_low / p_high) * phi
}

/// Eficiência de purga — Eq. 15.9: η_purge = 1 − ṁ_purge/ṁ_total
pub fn eta_purga(m_dot_purge: f64, m_dot_total: f64) -> f64 {
    1.0 - m_dot_purge / m_dot_total
}

/// Potência do aquecedor de regeneração [W] — Eq. 3.3: P = ṁ_purge·cp·ΔT
pub fn potencia_aquecedor(m_dot_purge: f64, delta_t: f64) -> f64 {
    m_dot_purge * CP_AR * delta_t
}

/// Consumo energético específico de secagem [J/kg] — Eq. 15.6
pub fn sec_dry(w_heater: f64, w_drum: f64, m_dot_dry: f64) -> f64 {
    (w_heater + w_drum) / m_dot_dry
}

/// Coeficiente de convecção forçada turbulenta em duto [W/(m²K)] — Eq. 15.15 (Dittus-Boelter)
pub fn coef_conveccao_forcada(m_dot: f64, d_h: f64, mu: f64, k_fluido: f64, pr: f64, aquecendo: bool) -> f64 {
    let re = 4.0 * m_dot / (PI * d_h * mu);
    let n = if aquecendo { 0.4 } else { 0.3 };
    let nu = 0.023 * re.powf(0.8) * pr.powf(n);
    nu * k_fluido / d_h
}

/// Correção da taxa de adsorção pela esfericidade — Eq. 15.18: k_ads = k_ads_ref/ψ_p
pub fn k_ads_por_forma(k_ads_ref: f64, psi_p: f64) -> f64 {
    k_ads_ref / psi_p
}

/// Perda de carga em leito empacotado [Pa] — Eq. 15.17 (Ergun, 1952)
pub fn perda_carga_ergun(
    mu: f64, v_s: f64, rho: f64,
    psi_p: f64, d_p: f64, porosidade: f64, l_leito: f64,
) -> f64 {
    let termo_viscoso = 150.0 * (1.0 - porosidade).powi(2) / porosidade.powi(3)
        * mu * v_s / (psi_p * d_p).powi(2);
    let termo_inercial = 1.75 * (1.0 - porosidade) / porosidade.powi(3)
        * rho * v_s * v_s / (psi_p * d_p);
    (termo_viscoso + termo_inercial) * l_leito
}

/// Índice de saúde do dessecante — Eq. 15.7: HI_des = (ΔP_nom/ΔP_real)·(PDP_target_K/PDP_real_K)
pub fn hi_des(dp_nom: f64, dp_real: f64, pdp_target_c: f64, pdp_real_c: f64) -> f64 {
    let pdp_target_k = pdp_target_c + 273.15;
    let pdp_real_k   = pdp_real_c   + 273.15;
    (dp_nom / dp_real) * (pdp_target_k / pdp_real_k)
}

// ── Vaso pulmão / rede (Caps. 2, 16) ─────────────────────────────────────────

/// Variação de pressão do vaso [Pa/s] — Eq. 16.4: dP/dt = R·T/V·(Σṁ_in − Σṁ_out)
pub fn dp_dt_vaso(v_vaso: f64, t_k: f64, m_dot_in: f64, m_dot_out: f64) -> f64 {
    R_AR * t_k / v_vaso * (m_dot_in - m_dot_out)
}

/// Tempo até atingir a pressão de corte [s] — Eq. 16.5
pub fn autonomia_vaso(v_vaso: f64, p_atual: f64, p_limite: f64, v_dot_demanda: f64, p_atm: f64) -> f64 {
    if v_dot_demanda <= 0.0 { return f64::INFINITY; }
    v_vaso * (p_atual - p_limite) / (v_dot_demanda * p_atm)
}

// ── Testes ────────────────────────────────────────────────────────────────────
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ua_com_fouling_zero() {
        // R_f = 0 → UA_real = UA_projeto
        let ua = ua_com_fouling(4000.0, 0.0);
        assert!((ua - 4000.0).abs() < 1e-6, "ua = {ua}");
    }

    #[test]
    fn test_ua_com_fouling_degradado() {
        // R_f > 0 → UA_real < UA_projeto
        let ua = ua_com_fouling(4000.0, 1e-4);
        assert!(ua < 4000.0, "UA deve diminuir com fouling");
    }

    #[test]
    fn test_perda_carga_ergun_positiva() {
        let dp = perda_carga_ergun(2.6e-5, 0.01, 1.2, 1.0, 0.0015, 0.38, 2.3);
        assert!(dp > 0.0, "ΔP Ergun deve ser positivo, got {dp}");
    }

    #[test]
    fn test_hi_des_saudavel() {
        // leito limpo: DP_nom = DP_real, PDP_real = PDP_target → HI ≈ 1.0
        let hi = hi_des(30_000.0, 30_000.0, -40.0, -40.0);
        assert!((hi - 1.0).abs() < 1e-6, "HI_des saudável = {hi}");
    }

    #[test]
    fn test_autonomia_vaso_sem_demanda() {
        let t = autonomia_vaso(2.0, 8e5, 6e5, 0.0, 1e5);
        assert!(t.is_infinite());
    }
}
