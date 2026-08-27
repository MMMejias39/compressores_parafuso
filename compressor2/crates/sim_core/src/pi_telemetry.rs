//! Módulo de Telemetria e Integração com o OSIsoft PI System.
//!
//! Mapeamento de 26+ tags industriais (Tabela 18.1, Pontos A–I),
//! geração de snapshot, alarmes ISA 18.2 e exportador CSV.

use rand::prelude::*;
use rand_distr::Normal;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use crate::sistema::{Params, ResultadoSistema};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum QualidadeSinal {
    Good,
    Bad,
    Substituted,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum StatusAlarme {
    Normal,
    AlertaLow,
    AlertaHigh,
    TripLL,
    TripHH,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TagPI {
    pub tag: String,
    pub sufixo: String,
    pub descricao: String,
    pub ponto: String,
    pub subsistema: String,
    pub unidade: String,
    pub tag_livro: String,
    pub tipo: String, // "Analog", "Digital", "Calculated"
    pub valor_nom: f64,
    pub faixa_min: f64,
    pub faixa_max: f64,
    pub alarme_l: Option<f64>,
    pub alarme_ll: Option<f64>,
    pub alarme_h: Option<f64>,
    pub alarme_hh: Option<f64>,
    pub funcao: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotTag {
    pub tag: String,
    pub sufixo: String,
    pub descricao: String,
    pub ponto: String,
    pub subsistema: String,
    pub unidade: String,
    pub valor: f64,
    pub valor_engenharia: f64,
    pub qualidade: QualidadeSinal,
    pub status_alarme: StatusAlarme,
    pub status_alarme_str: String,
    pub timestamp: String,
}

pub fn obter_catalogo_tags_pi(prefixo: &str) -> Vec<TagPI> {
    let raw = vec![
        // Ponto A: MCC / Elétrico
        ("ELE_VL", "Tensão de Linha do Motor", "A", "Painel Elétrico / MCC", "V", "V_L", "Analog", 4160.0, 3500.0, 4800.0, Some(3950.0), Some(3740.0), Some(4370.0), Some(4580.0), "Alimentação do motor"),
        ("ELE_I", "Corrente de Linha do Motor", "A", "Painel Elétrico / MCC", "A", "I", "Analog", 42.0, 0.0, 80.0, None, None, Some(50.0), Some(55.0), "Carga elétrica do motor (Eq. 4.1)"),
        ("ELE_FREQ", "Frequência do VSD", "A", "Painel Elétrico / MCC", "Hz", "f", "Analog", 60.0, 20.0, 75.0, Some(25.0), None, Some(65.0), None, "Comando angular do VSD"),
        ("ELE_COSPHI", "Fator de Potência", "A", "Painel Elétrico / MCC", "-", "cos φ", "Analog", 0.88, 0.50, 1.00, Some(0.80), None, None, None, "Eficiência da conversão"),
        ("ELE_VU", "Desbalanço de Tensão", "A", "Painel Elétrico / MCC", "%", "VU", "Calculated", 0.4, 0.0, 5.0, None, None, Some(1.0), Some(2.0), "Assimetria de alimentação (Eq. 4.8)"),
        ("ELE_IU", "Desbalanço de Corrente", "A", "Painel Elétrico / MCC", "%", "IU", "Calculated", 1.2, 0.0, 15.0, None, None, Some(5.0), Some(8.0), "Detecção de curto (Eq. 4.8)"),

        // Ponto B: Transmissão / Eixos
        ("MEC_RPM", "Rotação do Motor", "B", "Transmissão / Eixos", "RPM", "N_mot", "Analog", 3528.0, 1000.0, 4000.0, None, None, Some(3800.0), None, "Cinemática do eixo (Eq. 4.4)"),
        ("MEC_TORQ", "Torque no Eixo", "B", "Transmissão / Eixos", "N·m", "τ", "Calculated", 530.0, 100.0, 1200.0, None, None, Some(750.0), Some(850.0), "Momento torsor (Eq. 6.8)"),
        ("MEC_VIB_RMS", "Severidade Vibratória", "B", "Transmissão / Eixos", "mm/s", "v_rms", "Analog", 2.10, 0.0, 20.0, None, None, Some(4.5), Some(7.1), "Vibração global (API 619)"),
        ("MEC_SIGMA_B", "Tensão Flexão Dente", "B", "Transmissão / Eixos", "MPa", "σ_b", "Calculated", 120.0, 0.0, 400.0, None, None, Some(250.0), Some(300.0), "Modelo de Lewis (Eq. 8.7)"),

        // Ponto C: Estágio LP
        ("LP_PSUC", "Pressão Sucção LP", "C", "Compressão Estágio LP", "bar", "P_s,lp", "Analog", 1.013, 0.80, 1.20, Some(0.95), Some(0.90), None, None, "Admissão pós-filtro (Eq. 5.4)"),
        ("LP_TDISC", "Temperatura Descarga LP", "C", "Compressão Estágio LP", "°C", "T_d,lp", "Analog", 123.8, 20.0, 180.0, None, None, Some(140.0), Some(150.0), "Compressão 1º estágio (Eq. 9.5)"),
        ("LP_CLEARANCE", "Folga Relativa LP", "C", "Compressão Estágio LP", "μm/m", "δ_lp/L", "Calculated", 2.0, 1.0, 25.0, None, None, Some(10.0), Some(20.0), "Desgaste de rotores (Eq. 9.3)"),

        // Ponto D: Intercooler
        ("IC_TW_IN", "Temp Água Entrada", "D", "Intercooler", "°C", "T_w,in", "Analog", 25.0, 10.0, 45.0, None, None, Some(32.0), Some(36.0), "Utilidade de água marinha"),
        ("IC_PINT", "Pressão Interestágio", "D", "Intercooler", "bar", "P_int", "Analog", 2.83, 1.5, 4.5, Some(2.3), None, Some(3.4), None, "Alocação de carga (Eq. 5.14)"),
        ("IC_DP", "Perda Carga Intercooler", "D", "Intercooler", "mbar", "ΔP_ic", "Analog", 60.0, 0.0, 300.0, None, None, Some(120.0), Some(180.0), "Restrição e sujeira"),
        ("IC_MCOND", "Condensado Separado IC", "D", "Intercooler", "kg/h", "ṁ_c", "Calculated", 4.5, 0.0, 25.0, None, None, None, None, "Extração psicrométrica (Eq. 10.6)"),

        // Ponto E: Estágio HP
        ("HP_PDISC", "Pressão Descarga HP", "E", "Compressão Estágio HP", "bar", "P_d,hp", "Analog", 8.0, 4.0, 12.0, Some(6.5), None, Some(9.5), Some(10.5), "Pressão final (Eq. 11.1)"),
        ("HP_TDISC", "Temperatura Descarga HP", "E", "Compressão Estágio HP", "°C", "T_d,hp", "Analog", 138.5, 50.0, 200.0, None, None, Some(160.0), Some(175.0), "Temp crítica 2º est. (Eq. 11.1)"),
        ("HP_AXIAL", "Posição Axial Rotor HP", "E", "Compressão Estágio HP", "μm", "δ_ax", "Analog", 15.0, -50.0, 100.0, None, None, Some(40.0), Some(60.0), "Desgaste mancal escora (Eq. 11.5)"),

        // Ponto F: Aftercooler
        ("AC_TAC_OUT", "Temp Saída Aftercooler", "F", "Aftercooler", "°C", "T_ac,out", "Analog", 28.5, 15.0, 65.0, None, None, Some(38.0), Some(45.0), "Pré-secagem PSA (Eq. 14.1)"),

        // Ponto G: Secador PSA
        ("PSA_TDP", "Ponto de Orvalho Saída", "G", "Secagem PSA", "°C", "T_dp", "Analog", -42.0, -70.0, 20.0, None, None, Some(-40.0), Some(-20.0), "Qualidade do ar (ISO 8573-1)"),
        ("PSA_MPURGE", "Vazão Purga PSA", "G", "Secagem PSA", "kg/s", "ṁ_p", "Calculated", 0.032, 0.0, 0.15, None, None, None, None, "Purga regeneração (Eq. 15.2)"),
        ("FLT_DP", "Perda Carga Filtros", "G", "Filtragem de Linha", "mbar", "ΔP_filt", "Analog", 120.0, 20.0, 800.0, None, None, Some(350.0), Some(500.0), "Saturação elemento (Eq. 14.5)"),

        // Ponto H: Vaso Pulmão
        ("TK_PTK", "Pressão Vaso Pulmão", "H", "Vaso de Pressão", "bar", "P_tk", "Analog", 7.85, 0.0, 12.0, Some(6.8), Some(6.0), None, Some(10.0), "Buffer de rede (Eq. 3.5)"),
        ("TK_LTK", "Nível Condensado Vaso", "H", "Vaso de Pressão", "%", "L_tk", "Analog", 5.0, 0.0, 100.0, None, None, Some(25.0), Some(50.0), "Acúmulo de líquido no vaso"),

        // Ponto I & DT
        ("HDR_MTOT", "Vazão Demanda Total", "I", "Header / Distribuição", "kg/s", "ṁ_tot", "Analog", 0.185, 0.0, 0.60, None, None, None, None, "Consumo offshore (Eq. 16.1)"),
        ("OIL_TT_RET", "Temp Retorno Óleo", "B/D", "Circuito de Lubrificação", "°C", "T_óleo,ret", "Analog", 65.0, 25.0, 100.0, None, None, Some(78.0), Some(85.0), "Calor mancais (Eq. 12.1)"),
        ("OIL_PT_SUP", "Pressão Suprimento Óleo", "B/D", "Circuito de Lubrificação", "bar", "P_sup,óleo", "Analog", 2.2, 0.5, 5.0, Some(1.5), Some(1.2), None, None, "Pressão de óleo (Eq. 12.2)"),
        ("DT_EXERGY_DEST", "Destruição Exergia Total", "DT", "Gêmeo Digital (Exergia)", "kW", "İ_total", "Calculated", 32.5, 10.0, 80.0, None, None, Some(45.0), None, "Irreversibilidade (Eq. 17.3)"),
        ("DT_CO2_RATE", "Taxa Emissão CO2", "DT", "Gêmeo Digital (Sustentabilidade)", "kg/h", "ṁ_CO2", "Calculated", 48.0, 15.0, 120.0, None, None, None, None, "Pegada carbono (Eq. 17.5)"),
        ("DT_HEALTH_INDEX", "Health Index Máquina", "DT", "Gêmeo Digital (Saúde)", "-", "HI", "Calculated", 0.98, 0.0, 1.0, Some(0.70), Some(0.40), None, None, "Saúde operacional (Eq. 26.4)"),
    ];

    raw.into_iter()
        .map(|(suf, desc, pto, sub, uni, livro, tip, vnom, fmin, fmax, al_l, al_ll, al_h, al_hh, func)| {
            TagPI {
                tag: format!("{}:{}", prefixo, suf),
                sufixo: suf.to_string(),
                descricao: desc.to_string(),
                ponto: pto.to_string(),
                subsistema: sub.to_string(),
                unidade: uni.to_string(),
                tag_livro: livro.to_string(),
                tipo: tip.to_string(),
                valor_nom: vnom,
                faixa_min: fmin,
                faixa_max: fmax,
                alarme_l: al_l,
                alarme_ll: al_ll,
                alarme_h: al_h,
                alarme_hh: al_hh,
                funcao: func.to_string(),
            }
        })
        .collect()
}

pub fn avaliar_alarme(valor: f64, tag: &TagPI) -> StatusAlarme {
    if let Some(ll) = tag.alarme_ll {
        if valor <= ll {
            return StatusAlarme::TripLL;
        }
    }
    if let Some(hh) = tag.alarme_hh {
        if valor >= hh {
            return StatusAlarme::TripHH;
        }
    }
    if let Some(l) = tag.alarme_l {
        if valor <= l {
            return StatusAlarme::AlertaLow;
        }
    }
    if let Some(h) = tag.alarme_h {
        if valor >= h {
            return StatusAlarme::AlertaHigh;
        }
    }
    StatusAlarme::Normal
}

pub fn extrair_snapshot_pi(
    res: &ResultadoSistema,
    params: &Params,
    prefixo: &str,
    adicionar_ruido: bool,
    seed: Option<u64>,
) -> HashMap<String, SnapshotTag> {
    let catalogo = obter_catalogo_tags_pi(prefixo);
    let mut rng = StdRng::seed_from_u64(seed.unwrap_or(42));
    let mut mapa = HashMap::new();

    let p_elec_total = res.potencias.w_total;
    let cos_phi = 0.88;
    let v_linha = 4160.0;
    let corrente = if p_elec_total > 0.0 {
        p_elec_total / (3.0_f64.sqrt() * v_linha * cos_phi)
    } else {
        0.0
    };
    let exergia_dest = (res.potencias.w_total - res.potencias.w_isotermico).max(0.0) / 1000.0;
    let co2_rate = (res.potencias.w_total / 1000.0) * 0.45; // 0.45 kg/kWh

    let p_suc_lp = if !res.nos.is_empty() { res.nos[0].p_bar } else { 1.013 };
    let t_disc_lp = if res.nos.len() > 1 { res.nos[1].t_c } else { 120.0 };
    let p_int = if res.nos.len() > 2 { res.nos[2].p_bar } else { 2.83 };
    let p_disc_hp = if res.nos.len() > 3 { res.nos[3].p_bar } else { 8.0 };
    let t_disc_hp = res.kpis.t_descarga_hp_c;
    let t_ac_out = if res.nos.len() > 4 { res.nos[4].t_c } else { 28.0 };
    let t_dp_out = if res.nos.len() > 5 { res.nos[5].pdp_c } else { -42.0 };
    let m_purge = res.potencias.m_dot_util * params.fator_purga;

    for tag_def in catalogo {
        let valor_puro = match tag_def.sufixo.as_str() {
            "ELE_VL" => v_linha,
            "ELE_I" => corrente,
            "ELE_FREQ" => 60.0,
            "ELE_COSPHI" => cos_phi,
            "ELE_VU" => 0.4,
            "ELE_IU" => 1.2,
            "MEC_RPM" => 3528.0,
            "MEC_TORQ" => if corrente > 0.0 { 530.0 * (corrente / 42.0) } else { 0.0 },
            "MEC_VIB_RMS" => 2.10 * (1.0 + params.folga_rel * 10.0),
            "MEC_SIGMA_B" => 120.0,
            "LP_PSUC" => p_suc_lp,
            "LP_TDISC" => t_disc_lp,
            "LP_CLEARANCE" => params.folga_rel * 1000.0,
            "IC_TW_IN" => params.t_agua - 273.15,
            "IC_PINT" => p_int,
            "IC_DP" => 60.0 * (1.0 + params.r_f_equiv * 5000.0),
            "IC_MCOND" => res.kpis.condensado_total_kg_h * 0.4,
            "HP_PDISC" => p_disc_hp,
            "HP_TDISC" => t_disc_hp,
            "HP_AXIAL" => 15.0 + params.folga_rel * 500.0,
            "AC_TAC_OUT" => t_ac_out,
            "PSA_TDP" => t_dp_out,
            "PSA_MPURGE" => m_purge,
            "FLT_DP" => 120.0,
            "TK_PTK" => p_disc_hp * 0.98,
            "TK_LTK" => 5.0,
            "HDR_MTOT" => params.demanda_m3_min * 1.2 / 60.0,
            "OIL_TT_RET" => 65.0 + (t_disc_lp - 120.0).max(0.0) * 0.1,
            "OIL_PT_SUP" => 2.2,
            "OIL_DP_SEP" => 150.0,
            "DT_EXERGY_DEST" => exergia_dest,
            "DT_CO2_RATE" => co2_rate,
            "DT_HEALTH_INDEX" => res.kpis.hi_des.clamp(0.0, 1.0),
            _ => tag_def.valor_nom,
        };

        let valor_final = if adicionar_ruido {
            let sigma = (tag_def.valor_nom.abs() * 0.005).max(1e-4);
            let dist = Normal::new(0.0, sigma).unwrap();
            (valor_puro + dist.sample(&mut rng)).clamp(tag_def.faixa_min, tag_def.faixa_max)
        } else {
            valor_puro.clamp(tag_def.faixa_min, tag_def.faixa_max)
        };

        let status_alarme = avaliar_alarme(valor_final, &tag_def);
        let status_str = match status_alarme {
            StatusAlarme::Normal => "Normal".to_string(),
            StatusAlarme::AlertaLow => "Alerta (L)".to_string(),
            StatusAlarme::AlertaHigh => "Alerta (H)".to_string(),
            StatusAlarme::TripLL => "Trip (LL)".to_string(),
            StatusAlarme::TripHH => "Trip (HH)".to_string(),
        };

        let snap = SnapshotTag {
            tag: tag_def.tag.clone(),
            sufixo: tag_def.sufixo.clone(),
            descricao: tag_def.descricao.clone(),
            ponto: tag_def.ponto.clone(),
            subsistema: tag_def.subsistema.clone(),
            unidade: tag_def.unidade.clone(),
            valor: valor_final,
            valor_engenharia: valor_final,
            qualidade: QualidadeSinal::Good,
            status_alarme,
            status_alarme_str: status_str,
            timestamp: chrono::Utc::now().to_rfc3339(),
        };

        mapa.insert(tag_def.tag, snap);
    }

    mapa
}

pub fn exportar_csv(snapshot: &HashMap<String, SnapshotTag>) -> Result<String, Box<dyn std::error::Error>> {
    let mut wtr = csv::Writer::from_writer(vec![]);
    wtr.write_record(&["Tag", "Descricao", "Ponto", "Subsistema", "Valor", "Unidade", "Qualidade", "Alarme", "Timestamp"])?;

    let mut lista: Vec<&SnapshotTag> = snapshot.values().collect();
    lista.sort_by(|a, b| a.tag.cmp(&b.tag));

    for item in lista {
        wtr.write_record(&[
            &item.tag,
            &item.descricao,
            &item.ponto,
            &item.subsistema,
            &format!("{:.3}", item.valor),
            &item.unidade,
            &format!("{:?}", item.qualidade),
            &item.status_alarme_str,
            &item.timestamp,
        ])?;
    }

    let bytes = wtr.into_inner()?;
    Ok(String::from_utf8(bytes)?)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_catalogo_e_snapshot() {
        let params = Params::default();
        let res = crate::sistema::simular(&params);
        let snap = extrair_snapshot_pi(&res, &params, "CMP01", true, Some(42));
        assert!(snap.len() >= 26);
        assert!(snap.contains_key("CMP01:LP_TDISC"));

        let csv_str = exportar_csv(&snap).unwrap();
        assert!(csv_str.contains("CMP01:LP_TDISC"));
    }
}
