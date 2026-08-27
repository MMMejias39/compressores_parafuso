//! Cascata completa do trem de ar comprimido.
//!
//! Encadeia: filtro → LP → intercooler → HP → aftercooler → separador → PSA → pulmão.
//! Convenções: SI, pressões absolutas (Pa), temperaturas em K.

use std::f64::consts::PI as PI_F64;
use serde::{Deserialize, Serialize};
use crate::{constantes::*, nucleo, subsistemas};

/// Parâmetros operacionais e físicos do sistema.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Params {
    pub t_amb: f64,
    pub ur_amb: f64,
    pub p_amb: f64,
    pub pi_total: f64,
    pub fad_m3_min: f64,
    pub n_compressores: u32,
    pub n: f64,              // expoente politrópico
    pub v_i: f64,
    pub eta_mec: f64,
    pub k_folga: f64,
    pub folga_rel: f64,
    pub m_carcaca: f64,
    pub c_carcaca: f64,
    pub cond_ext_carcaca: f64,
    pub cond_arref_carcaca: f64,
    pub s_motor: f64,
    pub p_fixas_motor: f64,
    pub m_dot_vent: f64,
    pub p_loss_hood_outros: f64,
    pub hood_enclausurado: bool,
    pub f_d_linha: f64,
    pub l_linha: f64,
    pub d_linha: f64,
    pub zeta_filtro: f64,
    pub t_agua: f64,
    pub ua_projeto: f64,
    pub r_f_equiv: f64,
    pub eta_sep: f64,
    pub fator_purga: f64,
    pub delta_t_regen: f64,
    pub v_vaso: f64,
    pub p_limite: f64,
    pub demanda_m3_min: f64,
    pub dp_real_psa: f64,
    pub pdp_real_c: f64,
    pub eps_recup_psa: f64,
    pub cond_rotor: f64,
    pub q_cond_eixo: f64,
    pub delta_nom_um: f64,
    pub alpha_rotor: f64,
    pub l_rotor: f64,
    pub alpha_carcaca: f64,
    pub l_carcaca: f64,
    pub psi_p: f64,
    pub d_p_particula: f64,
    pub porosidade_leito: f64,
    pub l_leito_psa: f64,
    pub d_vaso_psa: f64,
    pub mu_ar_psa: f64,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            t_amb: T_AMB_DEFAULT,
            ur_amb: UR_AMB_DEFAULT,
            p_amb: P_ATM,
            pi_total: PI_REDE_DEFAULT,
            fad_m3_min: FAD_DEFAULT_M3_MIN,
            n_compressores: N_COMPRESSORES_DEFAULT,
            n: N_POLITROPICO,
            v_i: VI_DEFAULT,
            eta_mec: ETA_MECANICA,
            k_folga: K_FOLGA,
            folga_rel: FOLGA_REL_DEFAULT,
            m_carcaca: M_CARCACA_LP,
            c_carcaca: C_CARCACA_LP,
            cond_ext_carcaca: COND_EXT_CARCACA_LP,
            cond_arref_carcaca: COND_ARREF_CARCACA_LP,
            s_motor: S_MOTOR_DEFAULT,
            p_fixas_motor: P_FIXAS_MOTOR_DEFAULT,
            m_dot_vent: M_DOT_VENT_DEFAULT,
            p_loss_hood_outros: P_LOSS_HOOD_OUTROS_DEFAULT,
            hood_enclausurado: HOOD_ENCLAUSURADO_DEFAULT,
            f_d_linha: F_D_LINHA_DEFAULT,
            l_linha: L_LINHA_DEFAULT,
            d_linha: D_LINHA_DEFAULT,
            zeta_filtro: ZETA_FILTRO,
            t_agua: T_AGUA_DEFAULT,
            ua_projeto: UA_PROJETO,
            r_f_equiv: RF_FOULING_DEFAULT,
            eta_sep: ETA_SEPARADOR,
            fator_purga: FATOR_PURGA,
            delta_t_regen: DELTA_T_REGEN,
            v_vaso: V_VASO_DEFAULT,
            p_limite: P_LIMITE_REDE,
            demanda_m3_min: DEMANDA_M3_MIN,
            dp_real_psa: DP_NOM_PSA,
            pdp_real_c: PDP_ALVO_C,
            eps_recup_psa: EPSILON_RECUP_PSA_DEFAULT,
            cond_rotor: COND_ROTOR_W_K,
            q_cond_eixo: Q_COND_EIXO_W,
            delta_nom_um: DELTA_NOM_UM,
            alpha_rotor: ALPHA_ROTOR,
            l_rotor: L_ROTOR_M,
            alpha_carcaca: ALPHA_CARCACA,
            l_carcaca: L_CARCACA_M,
            psi_p: PSI_P_ESFERA,
            d_p_particula: D_P_PARTICULA_M,
            porosidade_leito: POROSIDADE_LEITO_PSA,
            l_leito_psa: L_LEITO_PSA_M,
            d_vaso_psa: D_VASO_PSA_M,
            mu_ar_psa: MU_AR_REGEN,
        }
    }
}

/// Estado termodinâmico em um nó do trem.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct No {
    pub nome: String,
    pub p_bar: f64,
    pub t_c: f64,
    pub m_dot: f64,    // kg/s ar seco
    pub w: f64,        // razão de umidade
    pub m_dot_total: f64,
    pub pdp_c: f64,
}

/// Balanço de potências do sistema.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Potencias {
    pub w_lp: f64,
    pub w_hp: f64,
    pub perda_vi_lp: f64,
    pub perda_vi_hp: f64,
    pub aquecedor: f64,
    pub aquecedor_nominal: f64,
    pub m_dot_util: f64,
    pub q_disp_regen: f64,
    pub w_total: f64,
    pub w_isotermico: f64,
    pub q_intercooler: f64,
    pub q_aftercooler: f64,
    pub n_compressores: u32,
    pub w_total_planta: f64,
}

/// KPIs e grandezas derivadas.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Kpis {
    pub spc: f64,
    pub eta_global: f64,
    pub eta_v_lp: f64,
    pub t_descarga_hp_c: f64,
    pub q_int_carcaca_w: f64,
    pub t_carcaca_c: f64,
    pub delta_t_carcaca_c: f64,
    pub tau_carcaca_min: f64,
    pub t_ref_carcaca_c: f64,
    pub t_rotor_c: f64,
    pub delta_t_rotor_c: f64,
    pub folga_residual_um: f64,
    pub dp_nom_psa_calc_bar: f64,
    pub eta_mot: f64,
    pub p_ag_w: f64,
    pub p_perdas_mot_w: f64,
    pub q_gerado_hood_w: f64,
    pub t_hood_c: f64,
    pub dp_linha_mbar: f64,
    pub p_hp_suc_efetiva_bar: f64,
    pub efetividade_intercooler: f64,
    pub condensado_total_kg_h: f64,
    pub purga_pct: f64,
    pub dp_filtro_mbar: f64,
    pub dp_dt_vaso_bar_min: f64,
    pub autonomia_min: f64,
    pub p_intermediaria_bar: f64,
    pub pdp_alvo_c: f64,
    pub sec_dry_kj_kg: f64,
    pub hi_des: f64,
    pub fad_total_m3_min: f64,
    pub condensado_total_planta_kg_h: f64,
}

/// Resultado completo da simulação.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResultadoSistema {
    pub nos: Vec<No>,
    pub potencias: Potencias,
    pub kpis: Kpis,
    pub avisos: Vec<String>,
}

/// Roda a cascata completa e devolve todos os estados, potências e KPIs.
///
/// O trem termodinâmico é calculado para **uma** unidade; `n_compressores`
/// unidades idênticas em paralelo são somadas apenas nas grandezas de planta.
pub fn simular(par: &Params) -> ResultadoSistema {
    let p = par;
    let n_comp = p.n_compressores.max(1) as f64;
    let mut avisos: Vec<String> = Vec::new();

    // --- 0. Admissão ----------------------------------------------------------
    let v_dot_fad = p.fad_m3_min / 60.0; // m³/s
    let rho_amb = nucleo::densidade_ar(p.p_amb, p.t_amb);
    let eta_v_lp = nucleo::eficiencia_volumetrica(p.k_folga, p.folga_rel, (p.pi_total).sqrt());
    let m_dot = rho_amb * v_dot_fad * eta_v_lp;

    let area_duto = PI_F64 * D_DUTO_ADMISSAO * D_DUTO_ADMISSAO / 4.0;
    let v_duto = v_dot_fad / area_duto;
    let dp_filtro = nucleo::delta_p_filtro(p.zeta_filtro, rho_amb, v_duto);
    let p0 = p.p_amb - dp_filtro;
    let w_amb = nucleo::razao_umidade(p.t_amb, p.p_amb, p.ur_amb);
    let m_dot_seco = m_dot / (1.0 + 1.6078 * w_amb);

    // --- 1. Divisão de estágios (geométrica, intercooler ideal) ---------------
    let p_rede = p.p_amb * p.pi_total;
    let pi_lp = (p.pi_total * p.p_amb / p0).sqrt();
    let pi_hp = pi_lp;
    let p_inter = p0 * pi_lp;

    // --- 2. Estágio LP --------------------------------------------------------
    let v_dot_lp = m_dot * R_AR * p.t_amb / p0;
    let w_lp = nucleo::potencia_politropica(p0, v_dot_lp, pi_lp, p.n, p.eta_mec);
    let perda_vi_lp = nucleo::perda_vi(p0, v_dot_lp * (p0 / p_inter), pi_lp, p.v_i, p.n);
    let t_lp_out = nucleo::temperatura_descarga(p.t_amb, pi_lp, p.n);
    let q_int_lp = nucleo::q_int_carcaca(w_lp, p.eta_mec);

    // --- 3. Intercooler -------------------------------------------------------
    let ua = subsistemas::ua_com_fouling(p.ua_projeto, p.r_f_equiv);
    let c_ar = m_dot_seco * nucleo::cp_umido(w_amb);
    let t_hp_in = subsistemas::saida_trocador(t_lp_out, p.t_agua, ua, c_ar);
    let eps_inter = subsistemas::efetividade(t_lp_out, t_hp_in, p.t_agua);
    let q_inter = subsistemas::calor_trocado(m_dot_seco, c_ar / m_dot_seco, t_lp_out, t_hp_in);
    let w_sat_inter = nucleo::razao_umidade(t_hp_in, p_inter, 1.0);
    let cond_inter = nucleo::condensado(m_dot_seco, w_amb, w_sat_inter);
    let w_hp_in = w_amb.min(w_sat_inter);

    // --- 4. Estágio HP --------------------------------------------------------
    let v_dot_hp = m_dot * R_AR * t_hp_in / p_inter;
    let w_hp = nucleo::potencia_politropica(p_inter, v_dot_hp, pi_hp, p.n, p.eta_mec);
    let perda_vi_hp = nucleo::perda_vi(p_inter, v_dot_hp * (p_inter / p_rede), pi_hp, p.v_i, p.n);
    let t_hp_out = nucleo::temperatura_descarga(t_hp_in, pi_hp, p.n);

    // --- 4b. Perda de carga na linha LP→HP ------------------------------------
    let v_dot_lp_out = m_dot * R_AR * t_lp_out / p_inter;
    let area_linha = PI_F64 * p.d_linha * p.d_linha / 4.0;
    let v_linha = v_dot_lp_out / area_linha;
    let rho_linha = nucleo::densidade_ar(p_inter, t_lp_out);
    let dp_linha = nucleo::delta_p_linha(p.f_d_linha, p.l_linha, p.d_linha, rho_linha, v_linha);
    let p_hp_suc_efetiva = p_inter - dp_linha;

    // --- 5. Aftercooler + separador -------------------------------------------
    let t_pos_after = subsistemas::saida_trocador(t_hp_out, p.t_agua, ua, c_ar);
    let q_after = subsistemas::calor_trocado(m_dot_seco, CP_AR, t_hp_out, t_pos_after);
    let w_sat_after = nucleo::razao_umidade(t_pos_after, p_rede, 1.0);
    let cond_after = nucleo::condensado(m_dot_seco, w_hp_in, w_sat_after);
    let agua_arraste = subsistemas::arraste(cond_after, p.eta_sep);
    let w_pos_sep = w_hp_in.min(w_sat_after) + agua_arraste / m_dot_seco;

    // --- 6. Secador PSA -------------------------------------------------------
    let m_purge = p.fator_purga * m_dot_seco;
    let eta_pur = subsistemas::eta_purga(m_purge, m_dot_seco);
    let p_aquecedor_nominal = subsistemas::potencia_aquecedor(m_purge, p.delta_t_regen);
    let m_dot_util = m_dot_seco - m_purge;
    let w_pos_secador = nucleo::razao_umidade(p.pdp_real_c + 273.15, p_rede, 1.0);

    // --- 6b. Perda de carga Ergun (Eq. 15.17) ---------------------------------
    let rho_ar_leito = nucleo::densidade_ar(p_rede, t_pos_after);
    let area_vaso_psa = PI_F64 * p.d_vaso_psa * p.d_vaso_psa / 4.0;
    let v_s_psa = m_dot_util / (rho_ar_leito * area_vaso_psa);
    let dp_nom_psa_calc = subsistemas::perda_carga_ergun(
        p.mu_ar_psa, v_s_psa, rho_ar_leito,
        p.psi_p, p.d_p_particula, p.porosidade_leito, p.l_leito_psa,
    );
    let hi_des_val = subsistemas::hi_des(dp_nom_psa_calc, p.dp_real_psa, PDP_ALVO_C, p.pdp_real_c);

    // --- 7. Vaso pulmão / rede ------------------------------------------------
    let demanda_m3_s = p.demanda_m3_min / 60.0;
    let m_dot_demanda = rho_amb * demanda_m3_s;
    let dp_dt = subsistemas::dp_dt_vaso(p.v_vaso, t_pos_after, m_dot_util * n_comp, m_dot_demanda);
    let t_autonomia = subsistemas::autonomia_vaso(p.v_vaso, p_rede, p.p_limite, demanda_m3_s, p.p_amb);

    // --- 8a. Motor, Hood, Carcaça LP -----------------------------------------
    let p_eixo_mot = w_lp + w_hp + perda_vi_lp + perda_vi_hp;
    let p_ag = nucleo::potencia_entreferro(p_eixo_mot, p.s_motor);
    let p_perdas_mot = nucleo::perdas_motor(p.s_motor, p_ag, p.p_fixas_motor);
    let eta_mot = nucleo::eficiencia_motor(p_eixo_mot, p_ag, p.p_fixas_motor);
    let q_gerado_hood = nucleo::calor_gerado_hood(p_perdas_mot, p.p_loss_hood_outros, q_int_lp);
    let t_hood = nucleo::temperatura_hood_regime(q_gerado_hood, p.m_dot_vent, CP_AR, p.t_amb);

    // --- 8b. Recuperação de calor na regeneração (Eqs. 15.10/15.11) ----------
    let q_disp = q_after + q_gerado_hood;
    let p_aquecedor = (p_aquecedor_nominal - p.eps_recup_psa * q_disp).max(0.0);
    let sec_dry_val = subsistemas::sec_dry(p_aquecedor, W_DRUM_PADRAO, m_dot_util);

    // --- 8c. Temperatura do rotor e folga residual térmica --------------------
    let t_ref_carcaca = if p.hood_enclausurado { t_hood } else { p.t_amb };
    let t_carcaca = nucleo::temperatura_carcaca_regime(
        q_int_lp, p.cond_ext_carcaca, p.cond_arref_carcaca, t_ref_carcaca,
    );
    let tau_carcaca = nucleo::constante_tempo_carcaca(
        p.m_carcaca, p.c_carcaca, p.cond_ext_carcaca, p.cond_arref_carcaca,
    );
    let t_gas_med_lp = (p.t_amb + t_lp_out) / 2.0;
    let t_rotor = nucleo::temperatura_rotor_regime(t_gas_med_lp, p.q_cond_eixo, p.cond_rotor);
    let delta_t_rotor = t_rotor - p.t_amb;
    let delta_t_carcaca_termica = t_carcaca - p.t_amb;
    let folga_residual_um = nucleo::folga_residual_termica(
        p.delta_nom_um, p.alpha_rotor, p.l_rotor, delta_t_rotor,
        p.alpha_carcaca, p.l_carcaca, delta_t_carcaca_termica,
    );

    // --- 9. Totais e KPIs ----------------------------------------------------
    let w_iso = nucleo::potencia_isotermica(p.p_amb, v_dot_fad, p.pi_total);
    let w_total = w_lp + w_hp + perda_vi_lp + perda_vi_hp + p_aquecedor;
    let eta_global = if w_total > 0.0 { w_iso / w_total } else { 0.0 };
    let spc_valor = nucleo::spc(w_total, p.fad_m3_min);

    if t_hp_out - 273.15 < 100.0 {
        avisos.push("Descarga HP abaixo de 100 °C — atípico.".to_string());
    }
    if !(0.0..=1.0).contains(&eps_inter) {
        avisos.push("Efetividade do intercooler fora de [0,1] — verificar UA/fouling.".to_string());
    }

    // PDP em cada nó
    let pdp_amb_c           = nucleo::temp_orvalho_de_w(w_amb, p.p_amb);
    let pdp_admissao_c      = nucleo::temp_orvalho_de_w(w_amb, p0);
    let pdp_pos_inter_c     = nucleo::temp_orvalho_de_w(w_hp_in, p_inter);
    let pdp_pos_after_c     = nucleo::temp_orvalho_de_w(w_pos_sep, p_rede);
    let pdp_pos_secador_c   = nucleo::temp_orvalho_de_w(w_pos_secador, p_rede);

    let nos = vec![
        No { nome: "A: Atmosfera (Ambiente)".to_string(),     p_bar: p.p_amb / 1e5, t_c: p.t_amb - 273.15, m_dot: m_dot_seco, w: w_amb,         m_dot_total: m_dot_seco * (1.0 + w_amb),        pdp_c: pdp_amb_c },
        No { nome: "B: Sucção LP (Pós-Filtro)".to_string(),   p_bar: p0 / 1e5,      t_c: p.t_amb - 273.15, m_dot: m_dot_seco, w: w_amb,         m_dot_total: m_dot_seco * (1.0 + w_amb),        pdp_c: pdp_admissao_c },
        No { nome: "C: Descarga LP".to_string(),              p_bar: p_inter / 1e5, t_c: t_lp_out - 273.15, m_dot: m_dot_seco, w: w_amb,       m_dot_total: m_dot_seco * (1.0 + w_amb),        pdp_c: nucleo::temp_orvalho_de_w(w_amb, p_inter) },
        No { nome: "D: Entrada HP (Pós-Interc.)".to_string(), p_bar: p_inter / 1e5, t_c: t_hp_in - 273.15,  m_dot: m_dot_seco, w: w_hp_in,    m_dot_total: m_dot_seco * (1.0 + w_hp_in),     pdp_c: pdp_pos_inter_c },
        No { nome: "E: Descarga HP".to_string(),              p_bar: p_rede / 1e5,  t_c: t_hp_out - 273.15, m_dot: m_dot_seco, w: w_hp_in,    m_dot_total: m_dot_seco * (1.0 + w_hp_in),     pdp_c: nucleo::temp_orvalho_de_w(w_hp_in, p_rede) },
        No { nome: "F: Saída Aftercooler".to_string(),        p_bar: p_rede / 1e5,  t_c: t_pos_after - 273.15, m_dot: m_dot_seco, w: w_pos_sep, m_dot_total: m_dot_seco * (1.0 + w_pos_sep), pdp_c: pdp_pos_after_c },
        No { nome: "G: Rede (Pós-Secador)".to_string(),       p_bar: p_rede / 1e5,  t_c: t_pos_after - 273.15, m_dot: m_dot_util, w: w_pos_secador, m_dot_total: m_dot_util * (1.0 + w_pos_secador), pdp_c: pdp_pos_secador_c },
    ];

    ResultadoSistema {
        nos,
        potencias: Potencias {
            w_lp, w_hp, perda_vi_lp, perda_vi_hp,
            aquecedor: p_aquecedor,
            aquecedor_nominal: p_aquecedor_nominal,
            m_dot_util,
            q_disp_regen: q_disp,
            w_total, w_isotermico: w_iso,
            q_intercooler: q_inter, q_aftercooler: q_after,
            n_compressores: p.n_compressores,
            w_total_planta: w_total * n_comp,
        },
        kpis: Kpis {
            spc: spc_valor, eta_global, eta_v_lp,
            t_descarga_hp_c: t_hp_out - 273.15,
            q_int_carcaca_w: q_int_lp,
            t_carcaca_c: t_carcaca - 273.15,
            delta_t_carcaca_c: t_carcaca - t_ref_carcaca,
            tau_carcaca_min: tau_carcaca / 60.0,
            t_ref_carcaca_c: t_ref_carcaca - 273.15,
            t_rotor_c: t_rotor - 273.15,
            delta_t_rotor_c: delta_t_rotor,
            folga_residual_um,
            dp_nom_psa_calc_bar: dp_nom_psa_calc / 1e5,
            eta_mot, p_ag_w: p_ag, p_perdas_mot_w: p_perdas_mot,
            q_gerado_hood_w: q_gerado_hood,
            t_hood_c: t_hood - 273.15,
            dp_linha_mbar: dp_linha / 100.0,
            p_hp_suc_efetiva_bar: p_hp_suc_efetiva / 1e5,
            efetividade_intercooler: eps_inter,
            condensado_total_kg_h: (cond_inter + cond_after) * 3600.0,
            purga_pct: (1.0 - eta_pur) * 100.0,
            dp_filtro_mbar: dp_filtro / 100.0,
            dp_dt_vaso_bar_min: dp_dt * 60.0 / 1e5,
            autonomia_min: t_autonomia / 60.0,
            p_intermediaria_bar: p_inter / 1e5,
            pdp_alvo_c: PDP_ALVO_C,
            sec_dry_kj_kg: sec_dry_val / 1000.0,
            hi_des: hi_des_val,
            fad_total_m3_min: p.fad_m3_min * n_comp,
            condensado_total_planta_kg_h: (cond_inter + cond_after) * 3600.0 * n_comp,
        },
        avisos,
    }
}

// ── Testes ────────────────────────────────────────────────────────────────────
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simular_defaults_sem_panic() {
        let res = simular(&Params::default());
        assert_eq!(res.nos.len(), 7);
        assert!(res.kpis.spc > 0.0, "SPC deve ser positivo");
        assert!(res.kpis.eta_global > 0.0, "η_global deve ser positivo");
        assert!(res.kpis.t_descarga_hp_c > 100.0, "T_HP,out deve ser > 100 °C");
    }

    #[test]
    fn test_simular_potencia_positiva() {
        let res = simular(&Params::default());
        assert!(res.potencias.w_total > 0.0);
        assert!(res.potencias.w_lp > 0.0);
        assert!(res.potencias.w_hp > 0.0);
    }

    #[test]
    fn test_simular_hi_des_range() {
        let res = simular(&Params::default());
        // HI_des saudável deve ser próximo de 1.0 (pode variar por geometria calibrada)
        assert!(res.kpis.hi_des > 0.0, "HI_des deve ser positivo");
    }

    #[test]
    fn test_simular_nos_pressao_crescente() {
        let res = simular(&Params::default());
        // Ponto A (Atmosfera) > Ponto B (Sucção pós-filtro com vácuo)
        assert!(res.nos[0].p_bar > res.nos[1].p_bar, "Pós-filtro deve estar sub-atmosférico devido a delta_p_filtro");
        // Ponto B < Descarga LP (Ponto C) < Descarga HP (Ponto E)
        assert!(res.nos[1].p_bar < res.nos[2].p_bar);
        assert!(res.nos[2].p_bar < res.nos[4].p_bar);
    }
}
