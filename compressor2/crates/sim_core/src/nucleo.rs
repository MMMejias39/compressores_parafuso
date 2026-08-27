//! Núcleo termodinâmico: estágios de compressão e psicrometria.
//!
//! Todas as equações referem-se ao livro compressores.tex.
//! Convenções: SI, pressões absolutas (Pa), temperaturas em K.

use crate::constantes::{CP_AR, R_AR};

// ── Estágios de compressão ────────────────────────────────────────────────────

/// Perda de carga do filtro de admissão [Pa] — Eq. 5.4: ΔP = ζ·ρ·v²/2
pub fn delta_p_filtro(zeta: f64, rho: f64, v: f64) -> f64 {
    zeta * rho * v * v / 2.0
}

/// Razão de pressão interna ideal do estágio — Eqs. 5.6/5.7: π_i = V_i^n
pub fn razao_pressao_interna(v_i: f64, n: f64) -> f64 {
    v_i.powf(n)
}

/// Potência de compressão de um estágio [W] — Eq. 5.5:
/// W = n/(n−1) · P_in · V̇_in · [π^((n−1)/n) − 1] / η_mec
pub fn potencia_politropica(p_in: f64, v_dot_in: f64, pi: f64, n: f64, eta_mec: f64) -> f64 {
    (n / (n - 1.0)) * p_in * v_dot_in * (pi.powf((n - 1.0) / n) - 1.0) / eta_mec
}

/// Perda por descasamento π_operante vs. π_i interna [W] — Eqs. 5.8/5.9
pub fn perda_vi(p1: f64, v_dot2: f64, pi_operante: f64, v_i: f64, n: f64) -> f64 {
    let p_i = p1 * razao_pressao_interna(v_i, n);
    let p2 = p1 * pi_operante;
    v_dot2 * (p2 - p_i).abs()
}

/// Temperatura de descarga do estágio [K] — Eq. 11.1: T_out = T_in · π^((n−1)/n)
pub fn temperatura_descarga(t_in: f64, pi: f64, n: f64) -> f64 {
    t_in * pi.powf((n - 1.0) / n)
}

/// Eficiência volumétrica — Eq. 9.3: η_v = 1 − K·(δ/L)·√(P2/P1)
pub fn eficiencia_volumetrica(k: f64, folga_rel: f64, pi: f64) -> f64 {
    1.0 - k * folga_rel * pi.sqrt()
}

/// Potência de entreferro do motor [W] — Eq. 4.12 invertida: P_ag = P_eixo/(1−s)
pub fn potencia_entreferro(p_eixo: f64, s: f64) -> f64 {
    p_eixo / (1.0 - s)
}

/// Perdas totais do motor [W] — Eq. 4.11: P_perdas = s·P_ag + P_fixas
pub fn perdas_motor(s: f64, p_ag: f64, p_fixas: f64) -> f64 {
    s * p_ag + p_fixas
}

/// Eficiência do motor [adim.] — Eq. 4.12
pub fn eficiencia_motor(p_eixo: f64, p_ag: f64, p_fixas: f64) -> f64 {
    let p_eletrica = p_ag + p_fixas;
    if p_eletrica > 0.0 { p_eixo / p_eletrica } else { 0.0 }
}

/// Calor total gerado dentro do hood [W] — Eq. 2.1
pub fn calor_gerado_hood(p_perdas_mot: f64, p_loss_outros: f64, q_casco: f64) -> f64 {
    p_perdas_mot + p_loss_outros + q_casco
}

/// Temperatura de regime do hood [K] — Eq. 2.4: T_hood = T_amb + Q/(ṁ_vent·cp)
pub fn temperatura_hood_regime(q_gerado: f64, m_dot_vent: f64, cp: f64, t_amb: f64) -> f64 {
    if m_dot_vent <= 0.0 { return t_amb; }
    t_amb + q_gerado / (m_dot_vent * cp)
}

/// Perda de carga distribuída na tubulação [Pa] — Eq. 5.15 (Darcy-Weisbach)
pub fn delta_p_linha(f_d: f64, l_linha: f64, d_linha: f64, rho: f64, v: f64) -> f64 {
    f_d * (l_linha / d_linha) * rho * v * v / 2.0
}

/// Potência isotérmica ideal de referência [W] — Eqs. 5.12/5.13
pub fn potencia_isotermica(p1: f64, v_dot1: f64, pi: f64) -> f64 {
    p1 * v_dot1 * pi.ln()
}

/// Calor gerado internamente e conduzido à carcaça [W] — proxy Eq. 9.6
pub fn q_int_carcaca(w_estagio: f64, eta_mec: f64) -> f64 {
    w_estagio * (1.0 - eta_mec)
}

/// Temperatura de carcaça em regime permanente [K] — Eq. 9.6 (regime): T_ss = T_amb + Q_int/cond_total
pub fn temperatura_carcaca_regime(q_int: f64, cond_ext: f64, cond_arref: f64, t_amb: f64) -> f64 {
    let cond_total = cond_ext + cond_arref;
    if cond_total <= 0.0 { return t_amb; }
    t_amb + q_int / cond_total
}

/// Constante de tempo térmica da carcaça [s] — τ_c = M_c·c_c / cond_total
pub fn constante_tempo_carcaca(m_c: f64, c_c: f64, cond_ext: f64, cond_arref: f64) -> f64 {
    let cond_total = cond_ext + cond_arref;
    if cond_total > 0.0 { (m_c * c_c) / cond_total } else { f64::INFINITY }
}

/// Evolução temporal T_c(t) [K] — solução analítica Eq. 9.6:
/// T_c(t) = T_c,ss + (T_c0 − T_c,ss)·exp(−t/τ_c)
pub fn temperatura_carcaca(
    t_c0: f64, t_amb: f64, q_int: f64,
    cond_ext: f64, cond_arref: f64, m_c: f64, c_c: f64, t: f64,
) -> f64 {
    let t_ss = temperatura_carcaca_regime(q_int, cond_ext, cond_arref, t_amb);
    let tau_c = constante_tempo_carcaca(m_c, c_c, cond_ext, cond_arref);
    if !tau_c.is_finite() { return t_amb; }
    t_ss + (t_c0 - t_ss) * (-t / tau_c).exp()
}

/// Temperatura do rotor em regime permanente [K] — Eq. 9.19: T_r = T_gas,med − Q̇_cond/(h_r·A_r)
pub fn temperatura_rotor_regime(t_gas_med: f64, q_cond_eixo: f64, cond_rotor: f64) -> f64 {
    if cond_rotor <= 0.0 { return t_gas_med; }
    t_gas_med - q_cond_eixo / cond_rotor
}

/// Folga residual por dilatação térmica diferencial [µm] — Eq. 9.7
pub fn folga_residual_termica(
    delta_nom_um: f64,
    alpha_r: f64, l_r: f64, delta_t_r: f64,
    alpha_c: f64, l_c: f64, delta_t_c: f64,
) -> f64 {
    delta_nom_um - (alpha_r * l_r * delta_t_r - alpha_c * l_c * delta_t_c) * 1.0e6
}

/// Consumo específico de energia [kW·min/m³] — Eq. 11.11
pub fn spc(w_total: f64, fad_m3_min: f64) -> f64 {
    (w_total / 1000.0) / fad_m3_min
}

// ── Psicrometria (Cap. 10) ────────────────────────────────────────────────────

/// Pressão de saturação do vapor d'água [Pa] — Eq. 10.7 (fórmula de Buck).
/// Válida para 0–80 °C; t_k em K.
pub fn p_sat(t_k: f64) -> f64 {
    let t_c = t_k - 273.15;
    0.61121e3 * ((18.678 - t_c / 234.5) * (t_c / (257.14 + t_c))).exp()
}

/// Razão de umidade [kg água / kg ar seco] — Eq. 10.6:
/// W = 0,622 · φ·P_sat(T) / (P − φ·P_sat(T))
pub fn razao_umidade(t_k: f64, p: f64, ur: f64) -> f64 {
    let pv = (ur * p_sat(t_k)).min(0.99 * p);
    0.622 * pv / (p - pv)
}

/// Pressão parcial de vapor d'água [Pa] — inversa da Eq. 10.6
pub fn pressao_vapor(w: f64, p: f64) -> f64 {
    w * p / (0.622 + w)
}

/// Umidade relativa a partir da razão de umidade
pub fn ur_de_w(w: f64, t_k: f64, p: f64) -> f64 {
    pressao_vapor(w, p) / p_sat(t_k)
}

/// Temperatura de ponto de orvalho [°C] — inversão numérica (bisseção) da Eq. 10.7
pub fn temp_orvalho_c(p_vapor: f64) -> f64 {
    if p_vapor <= 0.0 { return -90.0; }
    let (mut lo_k, mut hi_k) = (183.15_f64, 363.15_f64); // −90 °C a 90 °C
    for _ in 0..60 {
        let mid_k = (lo_k + hi_k) / 2.0;
        if p_sat(mid_k) < p_vapor { lo_k = mid_k; } else { hi_k = mid_k; }
    }
    (lo_k + hi_k) / 2.0 - 273.15
}

/// PDP [°C] a partir da razão de umidade W e pressão P
pub fn temp_orvalho_de_w(w: f64, p: f64) -> f64 {
    temp_orvalho_c(pressao_vapor(w, p))
}

/// Vazão mássica de condensado [kg/s] — Eq. 10.6/14.3
pub fn condensado(m_dot_ar: f64, w_in: f64, w_out: f64) -> f64 {
    m_dot_ar * (w_in - w_out).max(0.0)
}

/// cp do ar úmido [J/(kg·K)] — Eq. 10.8: cp_úmido ≈ 1005 + W·1860
pub fn cp_umido(w: f64) -> f64 {
    CP_AR + w * 1860.0
}

/// Densidade do ar seco [kg/m³] — gás ideal
pub fn densidade_ar(p: f64, t_k: f64) -> f64 {
    p / (R_AR * t_k)
}

// ── Testes unitários ──────────────────────────────────────────────────────────
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_p_sat_25c() {
        // Python: p_sat(298.15) ≈ 3169 Pa
        let ps = p_sat(298.15);
        assert!((ps - 3169.0).abs() < 10.0, "p_sat(25°C) = {ps}");
    }

    #[test]
    fn test_temperatura_descarga() {
        // T_out = 303.15 * 2.83^((1.35-1)/1.35) ≈ 380 K
        let t = temperatura_descarga(303.15, 2.83, 1.35);
        assert!(t > 370.0 && t < 400.0, "T_descarga = {t}");
    }

    #[test]
    fn test_eficiencia_volumetrica() {
        // η_v = 1 - 0.05 * 0.002 * sqrt(8) ≈ 0.9997
        let eta = eficiencia_volumetrica(0.05, 0.002, 8.0);
        assert!((eta - 0.9997).abs() < 0.001, "η_v = {eta}");
    }

    #[test]
    fn test_spc_dimensional() {
        // kW·min/m³ — só verifica unidade positiva
        let s = spc(50_000.0, 10.0);
        assert!(s > 0.0);
    }

    #[test]
    fn test_temp_orvalho_c_roundtrip() {
        // p_sat(15 °C) → orvalho deve voltar ~15 °C
        let pv = p_sat(288.15);
        let tdp = temp_orvalho_c(pv);
        assert!((tdp - 15.0).abs() < 0.05, "tdp = {tdp}");
    }
}
