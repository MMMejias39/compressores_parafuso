//! Módulo de Treinamento Operacional, Diagnóstico de Falhas e Classificador Multi-Mecanismo.
//!
//! Implementa:
//! 1. Catálogo completo de mecanismos de falha (Tabela 28.2).
//! 2. Classificação de causa-raiz por resíduo mínimo ponderado m̂_falha (Eq. 29.2).
//! 3. Gerador de desafios para a Arena de Treinamento.
//! 4. Motor de pontuação e parecer técnico-normativo (API 619, ISO 1217, ISO 8573-1, ASME VIII).

use rand::prelude::*;
use serde::{Deserialize, Serialize};
use crate::sistema::{self, Params, ResultadoSistema};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MecanismoFalha {
    pub id: String,
    pub nome: String,
    pub capitulo: String,
    pub eq_ref: String,
    pub subsistema: String,
    pub parametro: String,
    pub valor_severo: f64,
    pub kpi_chave: String,
    pub direcao_piora: String,
    pub deteccao_primaria: String,
    pub dificuldade: String, // "Iniciante", "Intermediario", "Avancado", "Mestre"
    pub descricao_fisica: String,
    pub sintomas_pi: Vec<String>,
    pub norma_referencia: String,
    pub acao_prescritiva: String,
    pub explicacao_tecnica: String,
}

pub fn catalogo_falhas() -> Vec<MecanismoFalha> {
    vec![
        MecanismoFalha {
            id: "folga_lp".to_string(),
            nome: "Desgaste de Folgas nos Rotores (Estágio LP)".to_string(),
            capitulo: "Capítulo 9".to_string(),
            eq_ref: "Eq. 9.3 / Eq. 9.4".to_string(),
            subsistema: "Geração / Estágio LP".to_string(),
            parametro: "folga_rel".to_string(),
            valor_severo: 0.020,
            kpi_chave: "eta_v_lp".to_string(),
            direcao_piora: "diminui".to_string(),
            deteccao_primaria: "EKF (δ)".to_string(),
            dificuldade: "Avancado".to_string(),
            descricao_fisica: "Erosão e desgaste abrasivo aumentam as folgas radiais e de flanco (δ/L), elevando a recirculação interna de ar comprimido para a sucção.".to_string(),
            sintomas_pi: vec![
                "Elevação suave da temperatura de descarga LP (CMP01:LP_TDISC)".to_string(),
                "Aumento gradual da corrente do motor (CMP01:ELE_I)".to_string(),
                "Discreta elevação na componente de passagem de lóbulos (CMP01:MEC_VIB_RMS)".to_string(),
                "Queda sutil na eficiência volumétrica estimada pelo EKF".to_string(),
            ],
            norma_referencia: "API 619 / ISO 1217:2009 Amd 1".to_string(),
            acao_prescritiva: "Monitorar taxa de deriva do EKF; se RUL_δ < 6 semanas, programar recondicionamento ou troca do elemento LP.".to_string(),
            explicacao_tecnica: "O desgaste de folga reduz a eficiência volumétrica conforme η_v = 1 - K(δ/L)√(P2/P1) (Eq. 9.3). O ar recirculado aquece a admissão por pre-heating (Eq. 9.4).".to_string(),
        },
        MecanismoFalha {
            id: "fouling_intercooler".to_string(),
            nome: "Incrustação Térmica (Fouling) no Intercooler".to_string(),
            capitulo: "Capítulo 10".to_string(),
            eq_ref: "Eq. 10.5 / Eq. 10.3".to_string(),
            subsistema: "Resfriamento Intermediário".to_string(),
            parametro: "r_f_equiv".to_string(),
            valor_severo: 0.002,
            kpi_chave: "efetividade_intercooler".to_string(),
            direcao_piora: "diminui".to_string(),
            deteccao_primaria: "EKF (R_f)".to_string(),
            dificuldade: "Intermediario".to_string(),
            descricao_fisica: "Depósito biológico, calcário ou óxido nos tubos do trocador casco-tubo aumenta a resistência térmica Rf, reduzindo o coeficiente global U.".to_string(),
            sintomas_pi: vec![
                "Aumento progressivo da temperatura de sucção do 2º estágio".to_string(),
                "Redução da efetividade térmica ε".to_string(),
                "Aumento no consumo de potência específica (SPC) do estágio HP".to_string(),
                "Temperatura da água de entrada estável, descartando distúrbio externo".to_string(),
            ],
            norma_referencia: "TEMA / API 619".to_string(),
            acao_prescritiva: "Disparar ordem de limpeza química/mecânica do feixe tubular do intercooler.".to_string(),
            explicacao_tecnica: "A incrustação adiciona resistência térmica em série 1/U_real = 1/U_clean + R_f (Eq. 10.5). Como a temperatura da água é normal, a queda de efetividade térmica é interna ao trocador.".to_string(),
        },
        MecanismoFalha {
            id: "offloading_termico".to_string(),
            nome: "Sobrecarga Térmica Externa de Água (Offloading)".to_string(),
            capitulo: "Capítulo 10".to_string(),
            eq_ref: "Eq. 10.4".to_string(),
            subsistema: "Resfriamento Intermediário".to_string(),
            parametro: "t_agua".to_string(),
            valor_severo: 313.15,
            kpi_chave: "w_hp_kw".to_string(),
            direcao_piora: "aumenta".to_string(),
            deteccao_primaria: "PIML / Limiar Direto".to_string(),
            dificuldade: "Intermediario".to_string(),
            descricao_fisica: "Demanda excessiva de outros consumidores da plataforma eleva a temperatura de suprimento da água de resfriamento (T_w,in).".to_string(),
            sintomas_pi: vec![
                "Elevação na tag CMP01:IC_TW_IN acima de 35 °C".to_string(),
                "Elevação de T_d,hp sem alteração na resistência térmica R_f".to_string(),
                "Efetividade do trocador ε permanece constante".to_string(),
            ],
            norma_referencia: "ISO 10440-1".to_string(),
            acao_prescritiva: "Emitir alerta de sobrecarga na rede externa de resfriamento; reajustar vazão das bombas de serviço.".to_string(),
            explicacao_tecnica: "No distúrbio de offloading a efetividade térmica permanece constante, enquanto T_w,in e W_HP aumentam (Eq. 10.4).".to_string(),
        },
        MecanismoFalha {
            id: "filtro_admissao".to_string(),
            nome: "Obstrução / Colmatagem do Filtro de Admissão".to_string(),
            capitulo: "Capítulo 5 e 13".to_string(),
            eq_ref: "Eq. 5.4".to_string(),
            subsistema: "Admissão e Filtragem".to_string(),
            parametro: "zeta_filtro".to_string(),
            valor_severo: 10.0,
            kpi_chave: "dp_filtro_mbar".to_string(),
            direcao_piora: "aumenta".to_string(),
            deteccao_primaria: "Limiar direto".to_string(),
            dificuldade: "Iniciante".to_string(),
            descricao_fisica: "Acúmulo de partículas salinas e névoa marítima satura o meio poroso filtrante, aumentando o coeficiente de perda de carga ζ.".to_string(),
            sintomas_pi: vec![
                "Aumento expressivo na perda de carga (CMP01:FLT_DP)".to_string(),
                "Queda na pressão absoluta de sucção (CMP01:LP_PSUC < 0.95 bar)".to_string(),
                "Redução da vazão mássica total entregue".to_string(),
            ],
            norma_referencia: "ISO 8573-1 / API 619".to_string(),
            acao_prescritiva: "Substituição imediata dos elementos filtrantes de admissão de ar.".to_string(),
            explicacao_tecnica: "A perda de carga segue ΔP_filt = ζ · (ρ v² / 2) (Eq. 5.4). A restrição na sucção diminui a densidade do ar admitido.".to_string(),
        },
        MecanismoFalha {
            id: "exaustor_hood".to_string(),
            nome: "Falha do Exaustor do Invólucro Acústico (Canopy/Hood)".to_string(),
            capitulo: "Capítulo 2".to_string(),
            eq_ref: "Eq. 2.1 / Eq. 2.4".to_string(),
            subsistema: "Pacote / Invólucro (Hood)".to_string(),
            parametro: "m_dot_vent".to_string(),
            valor_severo: 0.10,
            kpi_chave: "t_hood_c".to_string(),
            direcao_piora: "aumenta".to_string(),
            deteccao_primaria: "PIML / Limiar Térmico".to_string(),
            dificuldade: "Intermediario".to_string(),
            descricao_fisica: "Queima do motor do exaustor ou venezianas travadas reduzem a vazão de ventilação forçada ṁ_vent, confinando o calor gerado.".to_string(),
            sintomas_pi: vec![
                "Elevação rápida da temperatura interna do invólucro (T_hood > 55 °C)".to_string(),
                "Superaquecimento do motor elétrico e módulos VSD".to_string(),
                "Aumento na temperatura da carcaça do compressor (T_c)".to_string(),
            ],
            norma_referencia: "IEC 60079 / ISO 2151".to_string(),
            acao_prescritiva: "Verificar alimentação do exaustor e desobstruir venezianas acústicas.".to_string(),
            explicacao_tecnica: "O balanço térmico impõe T_hood = T_amb + Q̇_gerado / (ṁ_vent · c_p) (Eq. 2.4).".to_string(),
        },
        MecanismoFalha {
            id: "psa_breakthrough".to_string(),
            nome: "Saturação do Leito Dessecante / Breakthrough PSA".to_string(),
            capitulo: "Capítulo 15".to_string(),
            eq_ref: "Eq. 15.1 / Eq. 15.7".to_string(),
            subsistema: "Tratamento / Secagem PSA".to_string(),
            parametro: "pdp_real_c".to_string(),
            valor_severo: -10.0,
            kpi_chave: "hi_des".to_string(),
            direcao_piora: "diminui".to_string(),
            deteccao_primaria: "Limiar PDP".to_string(),
            dificuldade: "Avancado".to_string(),
            descricao_fisica: "Perda de capacidade adsortiva por envelhecimento ou contaminação por óleo, permitindo passagem de umidade.".to_string(),
            sintomas_pi: vec![
                "Elevação do Ponto de Orvalho sob Pressão (CMP01:PSA_TDP) acima de -40 °C".to_string(),
                "Deterioração do índice HI_des (Eq. 15.14)".to_string(),
                "Pressões e temperaturas mecânicas da máquina normais".to_string(),
            ],
            norma_referencia: "ISO 8573-1 Classe 2 (-40 °C PDP)".to_string(),
            acao_prescritiva: "Antecipar tempo de ciclo de regeneração; planejar substituição do dessecante.".to_string(),
            explicacao_tecnica: "A capacidade dinâmica decai exponencialmente q_d = q_eq exp(-k_ads t_ads/t_res) (Eq. 15.1).".to_string(),
        },
        MecanismoFalha {
            id: "desgaste_mancais".to_string(),
            nome: "Desgaste e Perda de Eficiência Mecânica (Mancais/Gearbox)".to_string(),
            capitulo: "Capítulo 5 e 8".to_string(),
            eq_ref: "Eq. 5.5 / Eq. 8.4".to_string(),
            subsistema: "Transmissão e Mancais".to_string(),
            parametro: "eta_mec".to_string(),
            valor_severo: 0.85,
            kpi_chave: "spc".to_string(),
            direcao_piora: "aumenta".to_string(),
            deteccao_primaria: "Resíduo r_mec".to_string(),
            dificuldade: "Intermediario".to_string(),
            descricao_fisica: "Degradação do filme lubrificante e micro-pitting aumentam o atrito parasita e as perdas mecânicas.".to_string(),
            sintomas_pi: vec![
                "Aumento do Consumo de Potência Específica SPC".to_string(),
                "Elevação da temperatura de retorno de óleo (CMP01:OIL_TT_RET)".to_string(),
                "Aumento da corrente elétrica (CMP01:ELE_I)".to_string(),
                "Aumento da severidade vibratória (CMP01:MEC_VIB_RMS)".to_string(),
            ],
            norma_referencia: "API 619 / ISO 281".to_string(),
            acao_prescritiva: "Coletar amostra de óleo para análise (TAN, ISO 4406); inspecionar folga dos mancais.".to_string(),
            explicacao_tecnica: "A redução de η_mec desvia o torque real do torque teórico, gerando resíduo positivo r_mec > 0 (Eq. 6.6).".to_string(),
        },
        MecanismoFalha {
            id: "leito_psa_colmatado".to_string(),
            nome: "Colmatagem / Queda Excessiva de Pressão no Secador PSA".to_string(),
            capitulo: "Capítulo 15".to_string(),
            eq_ref: "Eq. 15.17 / Eq. 15.7".to_string(),
            subsistema: "Tratamento / Secagem PSA".to_string(),
            parametro: "dp_real_psa".to_string(),
            valor_severo: 1.2e5,
            kpi_chave: "dp_psa_bar".to_string(),
            direcao_piora: "aumenta".to_string(),
            deteccao_primaria: "Limiar direto (HI_des)".to_string(),
            dificuldade: "Iniciante".to_string(),
            descricao_fisica: "Compactação ou poeira de dessecante causam restrição severa ao fluxo segundo a equação de Ergun.".to_string(),
            sintomas_pi: vec![
                "Queda acentuada na pressão de entrega à rede".to_string(),
                "Diferencial de pressão no secador muito acima do nominal".to_string(),
                "Degradação drástica do índice HI_des".to_string(),
            ],
            norma_referencia: "ASME VIII Div 1 / ISO 8573-1".to_string(),
            acao_prescritiva: "Despressurizar e descarregar a torre; tamisar dessecante e substituir cargas pulverizadas.".to_string(),
            explicacao_tecnica: "A perda de carga no leito empacotado obedece à equação de Ergun (Eq. 15.17).".to_string(),
        },
    ]
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CasoCego {
    pub mecanismo_id: String,
    pub mecanismo_nome: String,
    pub severidade: f64,
    pub nivel_dificuldade: String,
    pub params_com_falha: Params,
    pub resultado_com_falha: ResultadoSistema,
}

pub fn gerar_caso_cego(nivel: &str, seed: u64) -> CasoCego {
    let catalogo = catalogo_falhas();
    let mut rng = StdRng::seed_from_u64(seed);

    let candidatos: Vec<&MecanismoFalha> = match nivel {
        "Iniciante" => catalogo.iter().filter(|m| m.dificuldade == "Iniciante").collect(),
        "Intermediario" => catalogo.iter().filter(|m| m.dificuldade == "Iniciante" || m.dificuldade == "Intermediario").collect(),
        "Avancado" => catalogo.iter().filter(|m| m.dificuldade != "Mestre").collect(),
        _ => catalogo.iter().collect(),
    };

    let mec = if !candidatos.is_empty() {
        candidatos[rng.gen_range(0..candidatos.len())]
    } else {
        &catalogo[0]
    };

    let severidade = rng.gen_range(0.35..=0.85);
    let mut params = Params::default();

    match mec.id.as_str() {
        "folga_lp" => {
            params.folga_rel = 0.002 + (mec.valor_severo - 0.002) * severidade;
        }
        "fouling_intercooler" => {
            params.r_f_equiv = mec.valor_severo * severidade;
        }
        "offloading_termico" => {
            params.t_agua = 298.15 + (mec.valor_severo - 298.15) * severidade;
        }
        "filtro_admissao" => {
            params.zeta_filtro = 2.5 + (mec.valor_severo - 2.5) * severidade;
        }
        "exaustor_hood" => {
            params.m_dot_vent = (0.5 - (0.5 - mec.valor_severo) * severidade).max(0.05);
        }
        "psa_breakthrough" => {
            params.pdp_real_c = -40.0 + (mec.valor_severo - (-40.0)) * severidade;
        }
        "desgaste_mancais" => {
            params.eta_mec = 0.96 - (0.96 - mec.valor_severo) * severidade;
        }
        "leito_psa_colmatado" => {
            params.dp_real_psa = 0.30e5 + (mec.valor_severo - 0.30e5) * severidade;
        }
        _ => {}
    }

    let resultado = sistema::simular(&params);

    CasoCego {
        mecanismo_id: mec.id.clone(),
        mecanismo_nome: mec.nome.clone(),
        severidade,
        nivel_dificuldade: nivel.to_string(),
        params_com_falha: params,
        resultado_com_falha: resultado,
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AvaliacaoResposta {
    pub mecanismo_correto: bool,
    pub severidade_correta: bool,
    pub subsistema_correto: bool,
    pub pontuacao: u32,
    pub parecer_tecnico: String,
    pub explicacao_tecnica: String,
}

pub fn avaliar_resposta(
    caso: &CasoCego,
    resposta_mecanismo_id: &str,
    resposta_severidade: f64,
    resposta_subsistema: &str,
) -> AvaliacaoResposta {
    let catalogo = catalogo_falhas();
    let mec_real = catalogo.iter().find(|m| m.id == caso.mecanismo_id);

    let mec_correto = caso.mecanismo_id == resposta_mecanismo_id;
    let sev_diff = (caso.severidade - resposta_severidade).abs();
    let sev_correta = sev_diff <= 0.20;

    let sub_real = mec_real.map(|m| m.subsistema.as_str()).unwrap_or("");
    let sub_correto = sub_real.eq_ignore_ascii_case(resposta_subsistema) || mec_correto;

    let mut pts = 0;
    if mec_correto { pts += 50; }
    if sev_correta { pts += 25; }
    if sub_correto { pts += 25; }

    let parecer = if pts >= 90 {
        "Diagnóstico EXCELENTE: Identificação exata da causa-raiz e da severidade operacional.".to_string()
    } else if pts >= 60 {
        "Diagnóstico BOM: Subsistema correto, mas com imprecisão na severidade ou no mecanismo exato.".to_string()
    } else {
        "Diagnóstico INADEQUADO: Mecanismo não condizente com os sintomas de telemetria observados.".to_string()
    };

    let explicacao = mec_real
        .map(|m| format!("{} (Norma: {} - Ação: {})", m.explicacao_tecnica, m.norma_referencia, m.acao_prescritiva))
        .unwrap_or_default();

    AvaliacaoResposta {
        mecanismo_correto: mec_correto,
        severidade_correta: sev_correta,
        subsistema_correto: sub_correto,
        pontuacao: pts,
        parecer_tecnico: parecer,
        explicacao_tecnica: explicacao,
    }
}

pub fn classificar_falha(
    params_base: &Params,
    res_obs: &ResultadoSistema,
) -> Vec<(String, f64)> {
    let catalogo = catalogo_falhas();
    let mut scores = Vec::new();

    let obs_tdisc_lp = if res_obs.nos.len() > 1 { res_obs.nos[1].t_c } else { 120.0 };
    let obs_tdisc_hp = res_obs.kpis.t_descarga_hp_c;
    let obs_dp_filtro = res_obs.kpis.dp_filtro_mbar;
    let obs_hi_des = res_obs.kpis.hi_des;
    let obs_spc = res_obs.kpis.spc;

    for mec in &catalogo {
        let mut p_test = params_base.clone();
        match mec.id.as_str() {
            "folga_lp" => p_test.folga_rel = 0.010,
            "fouling_intercooler" => p_test.r_f_equiv = 0.001,
            "offloading_termico" => p_test.t_agua = 308.15,
            "filtro_admissao" => p_test.zeta_filtro = 6.0,
            "exaustor_hood" => p_test.m_dot_vent = 0.2,
            "psa_breakthrough" => p_test.pdp_real_c = -20.0,
            "desgaste_mancais" => p_test.eta_mec = 0.90,
            "leito_psa_colmatado" => p_test.dp_real_psa = 0.8e5,
            _ => {}
        }
        let res_test = sistema::simular(&p_test);

        let t_lp_diff = (obs_tdisc_lp - res_test.nos[1].t_c).abs() / 20.0;
        let t_hp_diff = (obs_tdisc_hp - res_test.kpis.t_descarga_hp_c).abs() / 20.0;
        let dp_f_diff = (obs_dp_filtro - res_test.kpis.dp_filtro_mbar).abs() / 50.0;
        let hi_diff = (obs_hi_des - res_test.kpis.hi_des).abs() / 0.5;
        let spc_diff = (obs_spc - res_test.kpis.spc).abs() / 1.0;

        let residuo_ponderado = t_lp_diff + t_hp_diff + dp_f_diff + hi_diff + spc_diff;
        let prob = (-residuo_ponderado).exp();
        scores.push((mec.id.clone(), prob));
    }

    let sum_prob: f64 = scores.iter().map(|s| s.1).sum();
    for s in &mut scores {
        s.1 = if sum_prob > 0.0 { s.1 / sum_prob } else { 0.0 };
    }
    scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
    scores
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_treinamento_gerar_e_avaliar() {
        let caso = gerar_caso_cego("Iniciante", 42);
        assert!(!caso.mecanismo_id.is_empty());

        let aval = avaliar_resposta(&caso, &caso.mecanismo_id, caso.severidade, "subsistema_teste");
        assert!(aval.mecanismo_correto);
        assert!(aval.severidade_correta);
        assert!(aval.pontuacao >= 75);
    }

    #[test]
    fn test_classificador_multi_mecanismo() {
        let base = Params::default();
        let mut falha = base.clone();
        falha.folga_rel = 0.012;
        let res = sistema::simular(&falha);

        let ranking = classificar_falha(&base, &res);
        assert!(!ranking.is_empty());
        assert!(ranking[0].1 > 0.0);
    }
}
