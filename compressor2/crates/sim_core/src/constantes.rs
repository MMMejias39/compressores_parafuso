//! Constantes físicas e valores default do simulador.
//!
//! Origem: livro "Gêmeo Digital de Sistemas de Compressão Offshore"
//! (compressores.tex). Valores ASSUMIDO não têm respaldo direto no livro.

use std::collections::HashMap;

// ── Propriedades do ar ────────────────────────────────────────────────────────
pub const R_AR: f64 = 287.0;           // J/(kg·K)
pub const CP_AR: f64 = 1005.0;         // J/(kg·K) — Eq. 10.8
pub const GAMMA: f64 = 1.4;            // cp/cv

// ── Condições de referência ───────────────────────────────────────────────────
pub const P_ATM: f64 = 101_325.0;      // Pa
pub const T_AMB_DEFAULT: f64 = 303.15; // K (30 °C) — ASSUMIDO
pub const UR_AMB_DEFAULT: f64 = 0.80;  // 80 % — ASSUMIDO

// ── Compressão ────────────────────────────────────────────────────────────────
pub const N_POLITROPICO: f64 = 1.35;   // Eq. 13.9
pub const VI_DEFAULT: f64 = 2.2;       // Eq. 5.7
pub const PI_REDE_DEFAULT: f64 = 8.0;  // razão de pressão total
pub const ETA_ISENTROPICA: f64 = 0.75; // ASSUMIDO
pub const ETA_MECANICA: f64 = 0.96;    // ASSUMIDO
pub const K_FOLGA: f64 = 0.05;         // Eq. 9.3 — ASSUMIDO
pub const FOLGA_REL_DEFAULT: f64 = 0.002; // δ/L — ASSUMIDO
pub const ZETA_FILTRO: f64 = 2.5;      // ASSUMIDO

// ── Carcaça LP — balanço térmico (Eq. 9.6) ───────────────────────────────────
pub const M_CARCACA_LP: f64 = 300.0;        // kg — ASSUMIDO
pub const C_CARCACA_LP: f64 = 460.0;        // J/(kg·K) — ASSUMIDO
pub const COND_EXT_CARCACA_LP: f64 = 10.0;  // W/K — ASSUMIDO
pub const COND_ARREF_CARCACA_LP: f64 = 20.0; // W/K — ASSUMIDO

// ── Rotor — balanço térmico e folga residual (Eqs. 9.7/9.18/9.19) ────────────
pub const COND_ROTOR_W_K: f64 = 15.0;     // W/K — ASSUMIDO
pub const Q_COND_EIXO_W: f64 = 50.0;      // W — ASSUMIDO
pub const DELTA_NOM_UM: f64 = 250.0;      // µm — ASSUMIDO
pub const ALPHA_ROTOR: f64 = 12.0e-6;     // 1/K — ASSUMIDO (aço)
pub const ALPHA_CARCACA: f64 = 10.0e-6;   // 1/K — ASSUMIDO (ferro fundido)
pub const L_ROTOR_M: f64 = 1.0;           // m — ASSUMIDO
pub const L_CARCACA_M: f64 = 1.0;         // m — ASSUMIDO

// ── Motor elétrico (Eqs. 4.10-4.12) ──────────────────────────────────────────
pub const S_MOTOR_DEFAULT: f64 = 0.02;         // ASSUMIDO
pub const P_FIXAS_MOTOR_DEFAULT: f64 = 1500.0; // W — ASSUMIDO

// ── Invólucro / Hood (Eqs. 2.1/2.4) ──────────────────────────────────────────
pub const M_DOT_VENT_DEFAULT: f64 = 0.5;          // kg/s — ASSUMIDO
pub const P_LOSS_HOOD_OUTROS_DEFAULT: f64 = 2000.0; // W — ASSUMIDO
pub const HOOD_ENCLAUSURADO_DEFAULT: bool = true;

// ── Tubulação interestágios (Eq. 5.15) ───────────────────────────────────────
pub const F_D_LINHA_DEFAULT: f64 = 0.02; // Darcy — ASSUMIDO
pub const L_LINHA_DEFAULT: f64 = 3.0;   // m — ASSUMIDO
pub const D_LINHA_DEFAULT: f64 = 0.10;  // m — ASSUMIDO

// ── Vazão / frota ─────────────────────────────────────────────────────────────
pub const FAD_DEFAULT_M3_MIN: f64 = 10.0;
pub const N_COMPRESSORES_DEFAULT: u32 = 1;

// ── Intercooler / aftercooler ─────────────────────────────────────────────────
pub const T_AGUA_DEFAULT: f64 = 298.15; // K (25 °C) — ASSUMIDO
pub const UA_PROJETO: f64 = 4000.0;     // W/K — ASSUMIDO
pub const RF_FOULING_DEFAULT: f64 = 0.0; // m²K/W (limpo)
pub const ETA_SEPARADOR: f64 = 0.98;    // Eq. 14.4 — ASSUMIDO

// ── Secador PSA ───────────────────────────────────────────────────────────────
pub const FATOR_PURGA: f64 = 0.15;
pub const DELTA_T_REGEN: f64 = 80.0;       // K — ASSUMIDO
pub const K_ADS_DEFAULT: f64 = 1.5;        // Eq. 15.1 — ASSUMIDO
pub const T_RES_PSA_DEFAULT_MIN: f64 = 4.0;
pub const T_ADS_PSA_DEFAULT_MIN: f64 = 6.0;
pub const T_REGEN_PSA_DEFAULT_MIN: f64 = 4.0;
pub const T_RESFRIAMENTO_PSA_DEFAULT_MIN: f64 = 2.0;
pub const N_VASOS_PSA_DEFAULT: u32 = 2;
pub const MATERIAL_PSA_DEFAULT: &str = "Alumina Ativada";
pub const MASSA_LEITO_PSA_DEFAULT_KG: f64 = 200.0; // kg/torre — ASSUMIDO

// ── Forma da partícula PSA ────────────────────────────────────────────────────
pub const PSI_P_ESFERA: f64 = 1.0;
pub const PSI_P_PELLET: f64 = 0.8;          // ASSUMIDO
pub const D_P_PARTICULA_M: f64 = 0.0015;    // m — ASSUMIDO
pub const POROSIDADE_LEITO_PSA: f64 = 0.38; // ASSUMIDO
pub const L_LEITO_PSA_M: f64 = 2.3;         // m — ASSUMIDO (calibrado vs. ΔP ~300 mbar)
pub const D_VASO_PSA_M: f64 = 0.30;         // m — ASSUMIDO

// ── Soprador booster / aquecedor ──────────────────────────────────────────────
pub const D_H_AQUECEDOR_M: f64 = 0.05;          // m — ASSUMIDO
pub const A_AQUECEDOR_M2: f64 = 2.0;            // m² — ASSUMIDO
pub const T_ELEM_MAX_C: f64 = 250.0;            // °C — ASSUMIDO
pub const M_DOT_REG_DEFAULT_KG_S: f64 = 0.05;   // kg/s — ASSUMIDO
pub const ETA_SOPRADOR_BOOSTER: f64 = 0.65;     // ASSUMIDO
pub const MU_AR_REGEN: f64 = 2.6e-5;            // Pa·s ~150 °C — ASSUMIDO
pub const K_AR_REGEN: f64 = 0.035;              // W/(m·K) ~150 °C — ASSUMIDO
pub const PR_AR: f64 = 0.7;                     // Prandtl
pub const EPSILON_RECUP_PSA_DEFAULT: f64 = 0.5; // ASSUMIDO
pub const DP_NOM_PSA: f64 = 0.30e5;             // Pa — ASSUMIDO
pub const W_DRUM_PADRAO: f64 = 0.0;             // W (sem tambor rotativo)

// ── Vaso pulmão / rede ────────────────────────────────────────────────────────
pub const V_VASO_DEFAULT: f64 = 2.0;    // m³ — ASSUMIDO
pub const P_LIMITE_REDE: f64 = 6.0e5;  // Pa abs — ASSUMIDO
pub const DEMANDA_M3_MIN: f64 = 8.0;   // m³/min FAD — ASSUMIDO

// ── PDP alvo ─────────────────────────────────────────────────────────────────
pub const PDP_ALVO_C: f64 = -40.0; // °C (ISO 8573-1 Classe 2)

// ── Duto de admissão ─────────────────────────────────────────────────────────
pub const D_DUTO_ADMISSAO: f64 = 0.10; // m — ASSUMIDO

// ── Fadiga do dente de engrenagem: Regra de Palmgren-Miner (Eqs. 19.7-19.9,
// 27/09/2026) ─────────────────────────────────────────────────────────────────
// Espelha aplicativo/compressor_sim/constantes.py — mesma justificativa: o
// livro descreve a curva S-N de Basquin (sigma^b_f * N = C) e cita a AGMA
// 2001, mas não fixa C/b_f para um material específico; ambos ASSUMIDOS a
// partir de dois pontos típicos de fadiga em flexão de dente cementado/
// temperado (aço-liga, grau AGMA 1-2). SIGMA_B_ADM_MPA reaproveita o limiar
// HH já definido para a tag MEC_SIGMA_B (pi_telemetry.rs).
pub const SIGMA_B_ADM_MPA: f64 = 300.0;          // MPa — sigma_adm (Eq. 24.2)
pub const N_REF_ENDURANCE: f64 = 1.0e7;          // ciclos — ASSUMIDO
pub const SIGMA_REF_BAIXO_CICLO_MPA: f64 = 700.0; // MPa — ASSUMIDO
pub const N_REF_BAIXO_CICLO: f64 = 1.0e4;        // ciclos — ASSUMIDO

// ── Processo Gaussiano da taxa de dano (Eq. 19.10, 27/09/2026) ────────────────
pub const GP_SIGMA_F: f64 = 0.02;   // desvio padrão do processo — ASSUMIDO
pub const GP_ELL_DIAS: f64 = 30.0;  // dias, comprimento de escala — ASSUMIDO
pub const GP_SIGMA_N: f64 = 0.002;  // desvio padrão do ruído de medição — ASSUMIDO

// 30 anos — teto de exibição/decisão do RUL por fadiga (ver fadiga.py)
pub const RUL_TETO_DIAS: f64 = 10_950.0;

// ── Materiais dessecantes ─────────────────────────────────────────────────────

/// Propriedades de um material dessecante para secador PSA.
#[derive(Debug, Clone)]
pub struct MaterialDessecante {
    pub densidade_kg_m3: f64,
    pub capacidade_trabalho: f64, // kg água / kg seco, baixa UR
    pub k_ads_ref: f64,
    pub t_regen_ref_min: f64,
    pub t_resfriamento_ref_min: f64,
}

/// Retorna o mapa de materiais dessecantes disponíveis.
pub fn materiais_dessecante() -> HashMap<&'static str, MaterialDessecante> {
    let mut m = HashMap::new();
    m.insert("Alumina Ativada", MaterialDessecante {
        densidade_kg_m3: 750.0,
        capacidade_trabalho: 0.10,
        k_ads_ref: 1.5,
        t_regen_ref_min: 45.0,
        t_resfriamento_ref_min: 10.0,
    });
    m.insert("Sílica Gel", MaterialDessecante {
        densidade_kg_m3: 700.0,
        capacidade_trabalho: 0.08,
        k_ads_ref: 1.2,
        t_regen_ref_min: 45.0,
        t_resfriamento_ref_min: 10.0,
    });
    m.insert("Peneira Molecular 13X", MaterialDessecante {
        densidade_kg_m3: 720.0,
        capacidade_trabalho: 0.18,
        k_ads_ref: 1.8,
        t_regen_ref_min: 45.0,
        t_resfriamento_ref_min: 10.0,
    });
    m
}
