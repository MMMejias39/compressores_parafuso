//! Simulação dinâmica (domínio do tempo) da rede de ar comprimido.
//!
//! Integra o balanço de massa do vaso pulmão/rede (Eq. 16.4/13.4) com os
//! modos de controle do Cap. 13: VSD (modulação contínua) e Carga/Alívio (histerese).

use serde::{Deserialize, Serialize};
use crate::constantes::R_AR;

// ── Defaults de controle (Cap. 13) ────────────────────────────────────────────
pub const K_UL: f64 = 0.25;    // fração de Ẇ_nom em alívio — ASSUMIDO
pub const DP_DB: f64 = 0.5e5;  // Pa, banda de histerese — ASSUMIDO (0,5 bar)
pub const ETA_VSD: f64 = 0.95; // eficiência do inversor — ASSUMIDO
pub const X_C_MIN: f64 = 0.30; // velocidade mínima VSD — ASSUMIDO
pub const TAU_VSD: f64 = 5.0;  // s, constante de tempo de rampa — ASSUMIDO

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KpisTransiente {
    pub energia_kwh: f64,
    pub n_ciclos: usize,
    pub f_ciclo_teorica_min: f64,
    pub t_abaixo_limite_min: f64,
    pub t_acima_pmta_min: f64,
    pub p_min_bar: f64,
    pub p_max_bar: f64,
    pub pmta_bar: f64,
    pub p_min_critica_bar: f64,
    pub dp_dt_max_bar_min: f64,
    pub modo: String,
    pub integridade_asme_ok: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResultadoTransiente {
    pub t_min: Vec<f64>,
    pub p_bar: Vec<f64>,        // Pressão no vaso P_vaso(t) [bar abs]
    pub p_in_bar: Vec<f64>,     // Pressão de entrada no compressor P_in(t) [bar abs]
    pub p_out_bar: Vec<f64>,    // Pressão de descarga do compressor P_out(t) [bar abs]
    pub m_comp: Vec<f64>,       // Vazão gerada pelo compressor [kg/s]
    pub m_dem: Vec<f64>,        // Vazão demandada pela planta [kg/s]
    pub x_c: Vec<f64>,          // Fração de carga / modulação VSD
    pub w_kw: Vec<f64>,         // Potência elétrica total [kW]
    pub status_vaso: Vec<String>,
    pub kpis: KpisTransiente,
}

/// Perfil de demanda escalonado: valor base com um evento de pico em degrau.
pub fn perfil_demanda(t: &[f64], base: f64, t_ev: (f64, f64), fator_ev: f64) -> Vec<f64> {
    t.iter()
        .map(|&ti| if ti >= t_ev.0 && ti < t_ev.1 { base * fator_ev } else { base })
        .collect()
}

/// Integra P(t) da rede e do vaso pulmão e calcula o acoplamento com compressores.
///
/// Monitora os limites de PMTA (ASME VIII) e Pressão Mínima de Trabalho.
pub fn simular_transiente(
    horizonte_min: f64,
    m_dot_cap: f64,
    w_nom: f64,
    v_vaso: f64,
    t_k: f64,
    p_set: f64,
    p_limite: f64,
    dem_base: f64,
    t_ev: (f64, f64),
    fator_ev: f64,
    modo: &str,
    dp_db: f64,
    k_ul: f64,
    eta_vsd: f64,
    x_c_min: f64,
    tau_vsd: f64,
    dt: f64,
) -> ResultadoTransiente {
    let pmta_pa = p_set * 1.25; // PMTA padrão 25% acima de P_set (ASME VIII)
    let p_min_pa = p_limite;

    let n = (horizonte_min * 60.0 / dt) as usize + 1;
    let t: Vec<f64> = (0..n).map(|i| i as f64 * dt).collect();
    let dem = perfil_demanda(&t, dem_base, t_ev, fator_ev);

    let mut p_arr = vec![0.0_f64; n];
    let mut p_in_arr = vec![0.0_f64; n];
    let mut p_out_arr = vec![0.0_f64; n];
    let mut m_comp_arr = vec![0.0_f64; n];
    let mut x_c_arr = vec![0.0_f64; n];
    let mut w_arr = vec![0.0_f64; n];
    let mut status_arr = Vec::with_capacity(n);

    let mut p = p_set;
    let mut carregado = true;
    let mut x_c = if m_dot_cap > 0.0 {
        (dem[0] / m_dot_cap).max(x_c_min).min(1.0)
    } else { 0.0 };

    let p_amb_base = 101325.0;
    let mut dp_dt_max = 0.0_f64;

    for i in 0..n {
        let (m_in, w) = if modo == "VSD" {
            let x_c_alvo = if m_dot_cap > 0.0 {
                (dem[i] / m_dot_cap).max(x_c_min).min(1.0)
            } else { 0.0 };
            x_c += (x_c_alvo - x_c) * (dt / tau_vsd).min(1.0);
            let m_in = x_c * m_dot_cap;
            let w = w_nom * x_c / eta_vsd;
            (m_in, w)
        } else {
            // Carga/Alívio — histerese em torno de p_set com banda dp_db
            if carregado && p >= p_set + dp_db / 2.0 { carregado = false; }
            else if !carregado && p <= p_set - dp_db / 2.0 { carregado = true; }
            x_c = if carregado { 1.0 } else { 0.0 };
            let m_in = if carregado { m_dot_cap } else { 0.0 };
            let w = w_nom * (x_c + (1.0 - x_c) * k_ul); // Eq. 13.7
            (m_in, w)
        };

        // Perda de carga de admissão (vácuo na sucção dependente da vazão)
        let dp_admissao = 2500.0 * (x_c * x_c); // Pa
        let p_in_comp = p_amb_base - dp_admissao;
        
        // Descarga do compressor precisa vencer a contrapressão do vaso + perda dos trocadores
        let dp_pos = 0.3e5; // 0.3 bar perdas em aftercooler/secador
        let p_out_comp = p + dp_pos;

        let st = if p >= pmta_pa {
            "🚨 ALÍVIO / PSV ABERTA (PMTA Excedida)".to_string()
        } else if p < p_min_pa {
            "⚠️ SUBPRESSÃO CRÍTICA (Abaixo de P_min)".to_string()
        } else if x_c > 0.8 {
            "⚡ CARGA PLENA (Vaso em Enchimento)".to_string()
        } else if x_c < 0.2 {
            "💤 ALÍVIO / DESCARREGADO".to_string()
        } else {
            "✅ OPERAÇÃO ESTÁVEL".to_string()
        };

        p_arr[i] = p;
        p_in_arr[i] = p_in_comp;
        p_out_arr[i] = p_out_comp;
        m_comp_arr[i] = m_in;
        x_c_arr[i] = x_c;
        w_arr[i] = w;
        status_arr.push(st);

        // Eq. 16.4 — dP/dt = R·T/V · (ṁ_in − ṁ_out)
        if i < n - 1 {
            let dp_dt = R_AR * t_k / v_vaso * (m_in - dem[i]);
            let dp_dt_abs_min = (dp_dt.abs() * 60.0) / 1e5; // bar/min
            if dp_dt_abs_min > dp_dt_max { dp_dt_max = dp_dt_abs_min; }
            p += dp_dt * dt;
            p = p.max(0.5e5);
        }
    }

    // Energia por trapézio
    let energia_kwh = t.windows(2)
        .zip(w_arr.windows(2))
        .map(|(ts, ws)| (ws[0] + ws[1]) / 2.0 * (ts[1] - ts[0]))
        .sum::<f64>() / 3.6e6;

    let (n_ciclos, f_ciclo_teorica_min) = if modo != "VSD" {
        let n_c = x_c_arr.windows(2)
            .filter(|w| w[0] >= 0.5 && w[1] < 0.5)
            .count();
        let dem_media = dem.iter().sum::<f64>() / dem.len() as f64;
        let f_c = if dem_media > 0.0 && dem_media < m_dot_cap {
            R_AR * t_k * dem_media * (m_dot_cap - dem_media)
                / (v_vaso * dp_db * m_dot_cap) * 60.0
        } else { 0.0 };
        (n_c, f_c)
    } else { (0, 0.0) };

    let t_abaixo_limite_min = p_arr.iter()
        .filter(|&&pi| pi < p_min_pa)
        .count() as f64 * dt / 60.0;

    let t_acima_pmta_min = p_arr.iter()
        .filter(|&&pi| pi > pmta_pa)
        .count() as f64 * dt / 60.0;

    let p_min_calc = p_arr.iter().cloned().fold(f64::INFINITY, f64::min) / 1e5;
    let p_max_calc = p_arr.iter().cloned().fold(f64::NEG_INFINITY, f64::max) / 1e5;

    ResultadoTransiente {
        t_min: t.iter().map(|&ti| ti / 60.0).collect(),
        p_bar: p_arr.iter().map(|&pi| pi / 1e5).collect(),
        p_in_bar: p_in_arr.iter().map(|&pi| pi / 1e5).collect(),
        p_out_bar: p_out_arr.iter().map(|&pi| pi / 1e5).collect(),
        m_comp: m_comp_arr,
        m_dem: dem,
        x_c: x_c_arr,
        w_kw: w_arr.iter().map(|&wi| wi / 1000.0).collect(),
        status_vaso: status_arr,
        kpis: KpisTransiente {
            energia_kwh,
            n_ciclos,
            f_ciclo_teorica_min,
            t_abaixo_limite_min,
            t_acima_pmta_min,
            p_min_bar: p_min_calc,
            p_max_bar: p_max_calc,
            pmta_bar: pmta_pa / 1e5,
            p_min_critica_bar: p_min_pa / 1e5,
            dp_dt_max_bar_min: dp_dt_max,
            modo: modo.to_string(),
            integridade_asme_ok: t_acima_pmta_min == 0.0,
        },
    }
}

// ── Testes ────────────────────────────────────────────────────────────────────
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_transiente_vsd_executa() {
        let r = simular_transiente(
            5.0, 0.2, 50_000.0, 2.0, 303.15,
            8e5, 6e5, 0.15,
            (f64::INFINITY, f64::INFINITY), 1.5,
            "VSD", DP_DB, K_UL, ETA_VSD, X_C_MIN, TAU_VSD, 0.5,
        );
        assert!(!r.p_bar.is_empty());
        assert!(r.kpis.p_max_bar > 0.0);
    }

    #[test]
    fn test_transiente_carga_alívio_executa() {
        let r = simular_transiente(
            5.0, 0.2, 50_000.0, 2.0, 303.15,
            8e5, 6e5, 0.15,
            (f64::INFINITY, f64::INFINITY), 1.5,
            "Carga/Alívio", DP_DB, K_UL, ETA_VSD, X_C_MIN, TAU_VSD, 0.5,
        );
        assert!(!r.p_bar.is_empty());
    }
}
