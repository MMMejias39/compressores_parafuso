"""Módulo de Treinamento Operacional, Diagnóstico de Falhas e Classificador Multi-Mecanismo.

Implementa:
1. Catálogo expandido de mecanismos de falha do compressor de parafuso offshore (Tabela 28.2).
2. Algoritmo de classificação de causa-raiz por resíduo mínimo ponderado m̂_falha (Eq. 29.2).
3. Atribuição de importância de variáveis e explicabilidade tipo SHAP (Eq. 25.4).
4. Gerador de desafios para a Arena de Treinamento de Operadores e Engenheiros.
5. Motor de pontuação e emissão de parecer técnico-normativo (API 619, ISO 1217, ISO 8573-1, ASME VIII).

Baseado nos Capítulos 28 e 29 do livro "Gêmeo Digital de Sistemas de Compressão Offshore".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from . import constantes, nucleo, pi_telemetry, sistema


@dataclass
class MecanismoFalhaInfo:
    id: str
    nome: str
    capitulo: str
    eq_ref: str
    subsistema: str
    parametro: str
    valor_severo: float
    kpi_chave: str
    direcao_piora: str
    deteccao_primaria: str
    dificuldade: str  # 'Iniciante', 'Intermediario', 'Avancado', 'Mestre'
    descricao_fisica: str
    sintomas_pi: List[str]
    norma_referencia: str
    acao_prescritiva: str
    explicacao_tecnica: str


# Catálogo completo de mecanismos de falha detalhados para simulação e treinamento
CATALOGO_FALHAS_TREINAMENTO: List[MecanismoFalhaInfo] = [
    MecanismoFalhaInfo(
        id="folga_lp",
        nome="Desgaste de Folgas nos Rotores (Estágio LP)",
        capitulo="Capítulo 9",
        eq_ref="Eq. 9.3 / Eq. 9.4",
        subsistema="Geração / Estágio LP",
        parametro="folga_rel",
        valor_severo=0.020,
        kpi_chave="eta_v_lp",
        direcao_piora="diminui",
        deteccao_primaria="EKF (δ)",
        dificuldade="Avancado",
        descricao_fisica="Erosão e desgaste abrasivo aumentam as folgas radiais e de flanco (δ/L), elevando a recirculação interna de ar comprimido para a sucção.",
        sintomas_pi=[
            "Elevação suave da temperatura de descarga LP (CMP01:LP_TDISC) por pré-aquecimento de sucção",
            "Aumento gradual da corrente do motor (CMP01:ELE_I)",
            "Discreta elevação na componente de passagem de lóbulos (CMP01:MEC_VIB_RMS)",
            "Queda sutil na eficiência volumétrica estimada pelo EKF",
        ],
        norma_referencia="API 619 / ISO 1217:2009 Amd 1",
        acao_prescritiva="Monitorar taxa de deriva do EKF; se RUL_δ < 6 semanas, programar recondicionamento ou troca do elemento compressor LP.",
        explicacao_tecnica="O desgaste de folga reduz a eficiência volumétrica conforme η_v = 1 - K(δ/L)√(P2/P1) (Eq. 9.3). O ar quente recirculado aquece a admissão por pre-heating (Eq. 9.4). Os sintomas individuais são sub-liminares nas primeiras semanas, sendo detectáveis apenas pela fusão de estados via EKF."
    ),
    MecanismoFalhaInfo(
        id="fouling_intercooler",
        nome="Incrustação Térmica (Fouling) no Intercooler",
        capitulo="Capítulo 10",
        eq_ref="Eq. 10.5 / Eq. 10.3",
        subsistema="Resfriamento Intermediário",
        parametro="r_f_equiv",
        valor_severo=0.002,
        kpi_chave="efetividade_intercooler",
        direcao_piora="diminui",
        deteccao_primaria="EKF (R_f)",
        dificuldade="Intermediario",
        descricao_fisica="Depósito biológico, calcário ou óxido nos tubos do trocador casco-tubo aumenta a resistência térmica Rf, reduzindo o coeficiente global U.",
        sintomas_pi=[
            "Aumento progressivo da temperatura de sucção do 2º estágio (CMP01:IC_PINT / CMP01:HP_TDISC)",
            "Redução da efetividade térmica ε (CMP01:AC_TAC_OUT normal, mas T_HP,in alta)",
            "Aumento no consumo de potência específica (SPC) do estágio HP",
            "Temperatura da água de entrada (CMP01:IC_TW_IN) estável, descartando distúrbio externo",
        ],
        norma_referencia="TEMA / API 619",
        acao_prescritiva="Disparar ordem de limpeza química/mecânica do feixe tubular do intercooler.",
        explicacao_tecnica="A incrustação adiciona resistência térmica em série 1/U_real = 1/U_clean + R_f (Eq. 10.5). Como a temperatura da água permanece normal, a queda de efetividade térmica é estritamente interna ao trocador, penalizando o trabalho de compressão do estágio HP (Eq. 10.4)."
    ),
    MecanismoFalhaInfo(
        id="offloading_termico",
        nome="Sobrecarga Térmica Externa de Água (Offloading)",
        capitulo="Capítulo 10",
        eq_ref="Eq. 10.4",
        subsistema="Resfriamento Intermediário",
        parametro="t_agua",
        valor_severo=313.15,  # 40 °C
        kpi_chave="w_hp_kw",
        direcao_piora="aumenta",
        deteccao_primaria="PIML / Limiar Direto",
        dificuldade="Intermediario",
        descricao_fisica="Demanda excessiva de outros consumidores da plataforma eleva a temperatura de suprimento da água de resfriamento (T_w,in).",
        sintomas_pi=[
            "Elevação na tag CMP01:IC_TW_IN acima de 35 °C",
            "Elevação de T_d,hp sem alteração na resistência térmica R_f",
            "Efetividade do trocador ε permanece constante",
            "Aumento na potência do estágio HP (Eq. 10.4)",
        ],
        norma_referencia="ISO 10440-1",
        acao_prescritiva="Emitir alerta de sobrecarga na rede externa de resfriamento; reajustar vazão das bombas de água de serviço.",
        explicacao_tecnica="Diferente do fouling interno, no distúrbio de offloading a efetividade térmica ε = (T_LP,out - T_HP,in)/(T_LP,out - T_w,in) permanece constante, enquanto T_w,in e W_HP aumentam (Eq. 10.4). O PIML classifica o evento como 'External Thermal Disturbance'."
    ),
    MecanismoFalhaInfo(
        id="filtro_admissao",
        nome="Obstrução / Colmatagem do Filtro de Admissão",
        capitulo="Capítulo 5 e 13",
        eq_ref="Eq. 5.4",
        subsistema="Admissão e Filtragem",
        parametro="zeta_filtro",
        valor_severo=10.0,
        kpi_chave="dp_filtro_mbar",
        direcao_piora="aumenta",
        deteccao_primaria="Limiar direto",
        dificuldade="Iniciante",
        descricao_fisica="Acúmulo de partículas salinas e névoa marítima satura o meio poroso filtrante, aumentando o coeficiente de perda de carga ζ.",
        sintomas_pi=[
            "Aumento expressivo na perda de carga (CMP01:FLT_DP / ΔP_filtro)",
            "Queda na pressão absoluta de sucção (CMP01:LP_PSUC < 0.95 bar)",
            "Redução da vazão mássica total entregue",
            "Aumento da taxa de compressão efetiva global",
        ],
        norma_referencia="ISO 8573-1 / API 619",
        acao_prescritiva="Substituição imediata dos elementos filtrantes de admissão de ar.",
        explicacao_tecnica="A perda de carga segue ΔP_filt = ζ · (ρ v² / 2) (Eq. 5.4). A restrição na sucção diminui a densidade do ar admitido, reduzindo o FAD e forçando o compressor a operar com maior razão de pressão global."
    ),
    MecanismoFalhaInfo(
        id="exaustor_hood",
        nome="Falha do Exaustor do Invólucro Acústico (Canopy/Hood)",
        capitulo="Capítulo 2",
        eq_ref="Eq. 2.1 / Eq. 2.2 / Eq. 2.4",
        subsistema="Pacote / Invólucro (Hood)",
        parametro="m_dot_vent",
        valor_severo=0.10,
        kpi_chave="t_hood_c",
        direcao_piora="aumenta",
        deteccao_primaria="PIML / Limiar Térmico",
        dificuldade="Intermediario",
        descricao_fisica="Queima do motor do exaustor ou venezianas travadas reduzem a vazão de ar de ventilação forçada ṁ_vent, confinando o calor gerado.",
        sintomas_pi=[
            "Elevação rápida da temperatura interna do invólucro (T_hood > 55 °C)",
            "Superaquecimento do motor elétrico e dos módulos VSD",
            "Aumento na temperatura da carcaça do compressor (T_c)",
            "Consumo de potência total inalterado",
        ],
        norma_referencia="IEC 60079 (Zonas Classificadas) / ISO 2151",
        acao_prescritiva="Verificar alimentação elétrica do exaustor e desobstruir venezianas acústicas.",
        explicacao_tecnica="O balanço térmico do invólucro em regime permanente impõe T_hood = T_amb + Q̇_gerado / (ṁ_vent · c_p) (Eq. 2.4). Com a queda de ṁ_vent, a capacidade de remoção térmica colapsa, provocando risco de derating no VSD e degradação acelerada do isolamento do motor (Eq. 4.7)."
    ),
    MecanismoFalhaInfo(
        id="psa_breakthrough",
        nome="Saturação do Leito Dessecante / Breakthrough PSA",
        capitulo="Capítulo 15",
        eq_ref="Eq. 15.1 / Eq. 15.7",
        subsistema="Tratamento / Secagem PSA",
        parametro="pdp_real_c",
        valor_severo=-10.0,
        kpi_chave="hi_des",
        direcao_piora="diminui",
        deteccao_primaria="VAE (Anomalia Gradual) / Limiar PDP",
        dificuldade="Avancado",
        descricao_fisica="Perda de capacidade adsortiva por envelhecimento, contaminação por óleo ou tempo excessivo de ciclo, permitindo passagem de umidade.",
        sintomas_pi=[
            "Elevação do Ponto de Orvalho sob Pressão (CMP01:PSA_TDP) acima de -40 °C",
            "Deterioração do índice HI_des (Eq. 15.14)",
            "Aumento do erro de reconstrução do VAE (E_rec > 4.0)",
            "Pressões e temperaturas mecânicas da máquina normais",
        ],
        norma_referencia="ISO 8573-1 Classe 2 (-40 °C PDP)",
        acao_prescritiva="Antecipar tempo de ciclo de regeneração; planejar substituição do material dessecante (Alumina/Peneira Molecular).",
        explicacao_tecnica="A capacidade dinâmica decai exponencialmente q_d = q_eq exp(-k_ads t_ads/t_res) (Eq. 15.1). Quando o leito atinge saturação prematura (breakthrough), o vapor d'água não é adsorvido, violando os limites da ISO 8573-1 Classe 2 e ameaçando a instrumentação pneumática."
    ),
    MecanismoFalhaInfo(
        id="desgaste_mancais",
        nome="Desgaste e Perda de Eficiência Mecânica na Gearbox/Mancais",
        capitulo="Capítulo 5, 6 e 8",
        eq_ref="Eq. 5.5 / Eq. 8.4",
        subsistema="Transmissão e Mancais",
        parametro="eta_mec",
        valor_severo=0.85,
        kpi_chave="spc",
        direcao_piora="aumenta",
        deteccao_primaria="Limiar Direto / Resíduo r_mec",
        dificuldade="Intermediario",
        descricao_fisica="Degradação do filme lubrificante e micro-pitting nas engrenagens e pistas de rolamento aumentam o atrito parasita e as perdas mecânicas.",
        sintomas_pi=[
            "Aumento do Consumo de Potência Específica SPC (CMP01:DT_EXERGY_DEST)",
            "Elevação da temperatura de retorno de óleo (CMP01:OIL_TT_RET)",
            "Aumento da corrente elétrica (CMP01:ELE_I) para a mesma vazão e pressão",
            "Aumento da severidade vibratória (CMP01:MEC_VIB_RMS)",
        ],
        norma_referencia="API 619 / ISO 281",
        acao_prescritiva="Coletar amostra de óleo para análise físico-química (TAN, Partículas ISO 4406); inspecionar folga e alinhamento dos mancais.",
        explicacao_tecnica="O atrito nos mancais dissipa calor conforme P_fric,brg ∝ μ ω² R³ L / e_filme (Eq. 7.4). A redução de η_mec desvia o torque real do torque de referência teórico (Eq. 6.8), gerando resíduo positivo r_mec > 0 (Eq. 6.6)."
    ),
    MecanismoFalhaInfo(
        id="motor_degradado",
        nome="Degradação Eletromagnética do Motor (Escorregamento Alto)",
        capitulo="Capítulo 4",
        eq_ref="Eq. 4.4 / Eq. 4.11 / Eq. 4.12",
        subsistema="Painel Elétrico / Motor",
        parametro="s_motor",
        valor_severo=0.07,
        kpi_chave="eta_mot",
        direcao_piora="diminui",
        deteccao_primaria="Limiar direto / MCSA",
        dificuldade="Avancado",
        descricao_fisica="Trincas em barras de gaiola do rotor de indução ou sobreaquecimento dos enrolamentos aumentam o escorregamento s e a perda Joule no rotor.",
        sintomas_pi=[
            "Queda na rotação medida do motor (CMP01:MEC_RPM) para a mesma frequência do VSD",
            "Aumento da corrente de fase (CMP01:ELE_I)",
            "Queda no rendimento elétrico η_mot (Eq. 4.12)",
            "Elevação na temperatura dos enrolamentos do estator",
        ],
        norma_referencia="IEC 60034-2-1 / IEEE 112",
        acao_prescritiva="Realizar teste de assinatura de corrente MCSA (busca por bandas laterais f_sideband, Eq. 4.6); inspecionar rotor.",
        explicacao_tecnica="A perda Joule no rotor é s · P_ag (Eq. 4.11). Quando barras quebram, a resistência equivalente do rotor aumenta, elevando o escorregamento s = (n_s - N_mot)/n_s (Eq. 4.4) e reduzindo a eficiência eletromecânica η_mot(s,T) (Eq. 4.12)."
    ),
    MecanismoFalhaInfo(
        id="desbalanco_fases",
        nome="Desbalanço de Tensão/Corrente Trifásica (NEMA MG1)",
        capitulo="Capítulo 4",
        eq_ref="Eq. 4.8",
        subsistema="Painel Elétrico / Motor",
        parametro="iu_desbalanco",
        valor_severo=10.0,
        kpi_chave="iu_pct",
        direcao_piora="aumenta",
        deteccao_primaria="Limiar direto (NEMA MG1)",
        dificuldade="Iniciante",
        descricao_fisica="Assimetria na rede de alimentação ou conexão frouxa provoca correntes de sequência negativa e sobreaquecimento localizado.",
        sintomas_pi=[
            "Tag CMP01:ELE_IU ultrapassando 5.0%",
            "Espalhamento entre temperaturas de fases ΔT_fases elevado",
            "Corrente média parece aceitável, mas uma fase sobrecarrega",
        ],
        norma_referencia="NEMA MG1 Parte 14",
        acao_prescritiva="Verificar conexões e aperto dos barramentos no MCC; balancear cargas da rede da plataforma.",
        explicacao_tecnica="Mesmo um pequeno desbalanço de tensão VU gera um desbalanço de corrente desproporcionalmente elevado IU = 100 · max|I_i - I_med| / I_med (Eq. 4.8) devido à baixa impedância de sequência negativa da máquina de indução."
    ),
    MecanismoFalhaInfo(
        id="edm_corrente_eixo",
        nome="Descargas Eletrostáticas em Rolamentos por VSD (EDM)",
        capitulo="Capítulo 4",
        eq_ref="Eq. 4.13",
        subsistema="Painel Elétrico / Mancais",
        parametro="v_shaft_v",
        valor_severo=35.0,
        kpi_chave="v_shaft",
        direcao_piora="aumenta",
        deteccao_primaria="VAE / Sonda de Aterramento",
        dificuldade="Mestre",
        descricao_fisica="Chaveamento PWM de alta frequência induz tensão de modo comum no eixo que rompe a rigidez dielétrica do filme de óleo, causando craterização (fluting).",
        sintomas_pi=[
            "Picos de corrente transitória no aterramento de eixo",
            "Aumento de vibração em altas frequências na pista do rolamento (BPFO/BPFI)",
            "Ocorre principalmente em baixas rotações (filme de óleo mais fino)",
        ],
        norma_referencia="IEEE Trans. Ind. Appl. / API 684",
        acao_prescritiva="Inspecionar e substituir o anel de aterramento de eixo (shaft grounding ring); verificar isolamento do rolamento NDE.",
        explicacao_tecnica="O acoplamento capacitivo estator-rotor divide a tensão conforme V_shaft = [C_sr / (C_sr + C_rg + C_bearing)] · V_modo_comum (Eq. 4.13). A descarga ocorre quando V_shaft ≥ E_dielétrico · e_filme(T,ω)."
    ),
    MecanismoFalhaInfo(
        id="leito_psa_colmatado",
        nome="Colmatagem / Queda Excessiva de Pressão no Secador PSA",
        capitulo="Capítulo 15",
        eq_ref="Eq. 15.16 / Eq. 15.14",
        subsistema="Tratamento / Secagem PSA",
        parametro="dp_real_psa",
        valor_severo=1.2e5,  # 1.2 bar
        kpi_chave="dp_psa_bar",
        direcao_piora="aumenta",
        deteccao_primaria="Limiar direto (HI_des)",
        dificuldade="Iniciante",
        descricao_fisica="Compactação, poeira de dessecante ou pulverização do leito causam restrição severa ao fluxo de ar comprimido segundo a equação de Ergun.",
        sintomas_pi=[
            "Queda acentuada na pressão de entrega à rede",
            "Diferencial de pressão no secador muito acima do nominal (CMP01:FLT_DP)",
            "Aumento da taxa de compressão exigida nos compressores",
        ],
        norma_referencia="ASME VIII Div 1 / ISO 8573-1",
        acao_prescritiva="Despressurizar e descarregar a torre saturada; tamisar o dessecante e substituir cargas pulverizadas.",
        explicacao_tecnica="A perda de carga no leito empacotado obedece à equação de Ergun (Eq. 15.16). Quando a porosidade ε_leito diminui e finos acumulam-se, a perda cresce com os termos viscoso e inercial, degradando o índice HI_des (Eq. 15.14)."
    ),
    MecanismoFalhaInfo(
        id="psv_travada_aberta",
        nome="Válvula de Segurança (PSV) com Vazamento / Disparo Prematuro",
        capitulo="Capítulo 14 e 16",
        eq_ref="Eq. 14.6 / Tabela 16.1",
        subsistema="Armazenamento e Segurança",
        parametro="perda_psv_kg_s",
        valor_severo=0.08,
        kpi_chave="spc",
        direcao_piora="aumenta",
        deteccao_primaria="Limiar Direto / Balanço de Massa",
        dificuldade="Intermediario",
        descricao_fisica="Fadiga da mola de calibração ou assentamento com sujeira mantém a PSV parcialmente aberta, aliviando ar de processo para a atmosfera.",
        sintomas_pi=[
            "Taxa de pressurização dP_tk/dt reduzida na fase de carga",
            "Aumento sustentado do consumo de energia específico SPC",
            "Incapacidade de manter a pressão de corte nos horários de pico",
            "Ruído sônico contínuo na tubulação de alívio atmosférico",
        ],
        norma_referencia="ASME Seção VIII Div. 1 / API 520",
        acao_prescritiva="Isolar ramal de teste da PSV; recalibrar ou substituir a mola da válvula de segurança.",
        explicacao_tecnica="O escoamento em orifício crítico descarrega ar em regime sônico (choked flow, Eq. 14.6): ṁ_perda = Cd A_dreno √(γ ρ P) [2/(γ+1)]^((γ+1)/(γ-1)), desperdiçando energia pura sem produzir trabalho útil."
    ),
    MecanismoFalhaInfo(
        id="psv_travada_fechada",
        nome="Válvula de Segurança (PSV) Travada Fechada (Risco Crítico)",
        capitulo="Capítulo 3 e 16",
        eq_ref="Tabela 16.1 / Tabela 18.2",
        subsistema="Armazenamento e Segurança",
        parametro="psv_stuck_closed",
        valor_severo=1.0,
        kpi_chave="p_tk_bar",
        direcao_piora="aumenta",
        deteccao_primaria="Limiar de Pressão Máxima (HH)",
        dificuldade="Mestre",
        descricao_fisica="Incrustação salina, corrosão da haste ou assento colado impedem a abertura mecânica da PSV em caso de sobrepressão.",
        sintomas_pi=[
            "Pressão do vaso (CMP01:TK_PTK) excede P_set (> 10 bar) sem abertura de alívio",
            "Disparo imediato de alarme HH no supervisório",
            "Exige trip de emergência (ESD) imediato para integridade do vaso",
        ],
        norma_referencia="ASME Seção VIII Div. 1",
        acao_prescritiva="PARADA DE EMERGÊNCIA IMEDIATA DA UNIDADE (ESD) para evitar sobrepressão catastrófica do vaso pulmão.",
        explicacao_tecnica="A PSV é a última barreira física de segurança do vaso de pressão. Seu travamento fechado anula a proteção contra sobrepressão, exigindo interrupção emergencial de todo o trem de geração."
    ),
    MecanismoFalhaInfo(
        id="dreno_fechado_calco",
        nome="Dreno Automático de Condensado Entupido (Risco de Calço)",
        capitulo="Capítulo 10 e 14",
        eq_ref="Eq. 10.10 / Eq. 11.9",
        subsistema="Tratamento Primário / Drenagem",
        parametro="dreno_obstruido",
        valor_severo=1.0,
        kpi_chave="m_cond_retida",
        direcao_piora="aumenta",
        deteccao_primaria="Vibração HF / Emissão Acústica",
        dificuldade="Avancado",
        descricao_fisica="Válvula de dreno emperrada fechada acumula líquido no separador ciclônico, provocando arraste de condensado para a sucção do 2º estágio.",
        sintomas_pi=[
            "Oscilação anormal na perda de carga do intercooler (CMP01:IC_DP)",
            "Picos transitórios de torque e corrente (Δτ, Eq. 11.9)",
            "Emissões acústicas e vibração de alta frequência no estágio HP",
            "Nível de líquido no vaso (CMP01:TK_LTK) subindo continuamente",
        ],
        norma_referencia="API 619",
        acao_prescritiva="Forçar purga manual imediata do separador; inspecionar e desobstruir válvula de dreno automático.",
        explicacao_tecnica="O arraste de água líquida incompressível para os rotores do estágio HP gera impacto mecânico instantâneo Δτ = I (dω/dt) + τ_impacto (Eq. 11.9), com risco severo de cisalhamento de chavetas e quebra de dentes de sincronismo."
    ),
    MecanismoFalhaInfo(
        id="vazamento_critico_header",
        nome="Vazamento Crítico / Ruptura no Header de Distribuição",
        capitulo="Capítulo 16",
        eq_ref="Eq. 16.4 / Eq. 16.5",
        subsistema="Header / Distribuição",
        parametro="taxa_vazamento_ext",
        valor_severo=0.15,
        kpi_chave="dp_dt_tank",
        direcao_piora="diminui",
        deteccao_primaria="Gradiente dP/dt Negativo",
        dificuldade="Intermediario",
        descricao_fisica="Ruptura de mangueira de utilidade ou conexões no coletor principal provoca despressurização acelerada da rede da plataforma.",
        sintomas_pi=[
            "Gradiente dP/dt no vaso pulmão fortemente negativo mesmo em plena carga",
            "Vazão de demanda medida (CMP01:HDR_MTOT) muito superior à produção",
            "Disparo do nível P_LL de corte de serviços (δ_serv = 0)",
            "Tempo de autonomia t_to_cut (Eq. 16.5) em rápida redução",
        ],
        norma_referencia="API 618 / Lógica Escalonada ISA",
        acao_prescritiva="Executar corte automático de serviços (δ_serv=0); se a queda persistir, isolar linha de processo (δ_proc=0) para salvar ar de instrumentos.",
        explicacao_tecnica="A taxa de pressão no vaso pulmão dP/dt = (R T / V_tk) · (∑ṁ_in - ∑ṁ_out) (Eq. 16.4) torna-se negativa. A lógica escalonada (Cap. 16.3) atua fechando sequencialmente Serviços (Nível 2) e Processo (Nível 3) para preservar a Emergência."
    ),
]


def buscar_mecanismo_por_id(mecanismo_id: str) -> Optional[MecanismoFalhaInfo]:
    """Localiza as informações detalhadas de um mecanismo pelo seu ID."""
    for m in CATALOGO_FALHAS_TREINAMENTO:
        if m.id == mecanismo_id:
            return m
    return None


def classificar_m_falha_minimo_residuo(
    vetor_z_medido: Dict[str, float],
    params_base: dict,
    catalogo_candidatos: Optional[List[MecanismoFalhaInfo]] = None,
    desvios_padrao: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """Implementa a busca por resíduo mínimo ponderado m̂_falha (Eq. 29.2 do livro).

    Calcula para cada mecanismo candidato m ∈ M a distância normalizada:
        J(m) = 1/n_z ∑ [(z_j - ẑ_j^(m)) / σ_j]²

    Retorna a lista ordenada dos mecanismos do mais provável para o menos provável,
    com probabilidades normalizadas e contribuição individual de cada tag (SHAP).
    """
    if catalogo_candidatos is None:
        catalogo_candidatos = CATALOGO_FALHAS_TREINAMENTO

    # Desvios padrão padrão para normalização
    sigmas_default: Dict[str, float] = {
        "LP_PSUC": 0.01, "LP_TDISC": 1.5, "LP_CLEARANCE": 0.5,
        "IC_TW_IN": 0.8, "IC_PINT": 0.05, "IC_DP": 5.0, "IC_MCOND": 0.5,
        "HP_PDISC": 0.08, "HP_TDISC": 1.8, "HP_AXIAL": 2.0,
        "AC_TAC_OUT": 1.0, "PSA_TDP": 2.0, "PSA_MPURGE": 0.005, "FLT_DP": 8.0,
        "TK_PTK": 0.05, "TK_LTK": 2.0, "HDR_MTOT": 0.01,
        "ELE_VL": 20.0, "ELE_I": 0.8, "ELE_FREQ": 0.2, "MEC_RPM": 15.0,
        "MEC_TORQ": 10.0, "MEC_VIB_RMS": 0.2, "OIL_TT_RET": 1.2, "OIL_PT_SUP": 0.05,
    }
    if desvios_padrao is not None:
        sigmas_default.update(desvios_padrao)

    # 1. Simulação nominal saudável
    res_saudavel = sistema.simular(params_base)
    snap_saudavel = pi_telemetry.extrair_snapshot_pi(res_saudavel, params_base, adicionar_ruido=False)
    
    resultados_candidatos = []

    # 2. Avaliação de cada hipótese m no catálogo
    for mec in catalogo_candidatos:
        # Simula a hipótese com a falha injetada
        p_hipotese = dict(params_base)
        if mec.parametro in p_hipotese:
            p_hipotese[mec.parametro] = mec.valor_severo
        elif mec.parametro == "t_agua":
            p_hipotese["t_agua"] = mec.valor_severo
        elif mec.parametro == "pdp_real_c":
            p_hipotese["pdp_real_c"] = mec.valor_severo
        elif mec.parametro == "dp_real_psa":
            p_hipotese["dp_real_psa"] = mec.valor_severo

        res_hipotese = sistema.simular(p_hipotese)
        snap_hipotese = pi_telemetry.extrair_snapshot_pi(res_hipotese, p_hipotese, adicionar_ruido=False)

        residuos_tags: Dict[str, float] = {}
        soma_res_quad = 0.0
        n_z = 0

        for tag_nome, val_med in vetor_z_medido.items():
            sufixo = tag_nome.split(":", 1)[1] if ":" in tag_nome else tag_nome
            sigma_j = sigmas_default.get(sufixo, 1.0)

            # Valor previsto pela hipótese
            val_pred = None
            for t_k, t_v in snap_hipotese.items():
                if t_k.endswith(sufixo):
                    val_pred = t_v["valor"]
                    break
            
            if val_pred is not None:
                termo = ((val_med - val_pred) / sigma_j) ** 2
                residuos_tags[sufixo] = termo
                soma_res_quad += termo
                n_z += 1

        custo_j = soma_res_quad / max(1, n_z)
        resultados_candidatos.append({
            "mecanismo": mec,
            "custo_j": float(custo_j),
            "residuos_tags": residuos_tags,
        })

    # Ordena pelo menor resíduo J(m)
    resultados_candidatos.sort(key=lambda x: x["custo_j"])

    # Conversão dos custos J em probabilidades (Softmax sobre -J/temperatura)
    custos = np.array([r["custo_j"] for r in resultados_candidatos])
    min_c = np.min(custos)
    temp = 2.0  # Temperatura de dispersão
    logits = - (custos - min_c) / temp
    probs = np.exp(logits) / np.sum(np.exp(logits))

    for idx, item in enumerate(resultados_candidatos):
        item["probabilidade_pct"] = float(probs[idx] * 100.0)

    return resultados_candidatos


def gerar_caso_treinamento(
    dificuldade: str = "Intermediario",
    params_base: Optional[dict] = None,
    mecanismo_especifico_id: Optional[str] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Gera um cenário de teste para treinamento de operadores/engenheiros.

    Pode gerar caso com falha ou caso com operação normal e distúrbio.
    """
    if params_base is None:
        params_base = sistema.parametros_default()
    rng = np.random.default_rng(seed)

    if mecanismo_especifico_id:
        mecanismo = buscar_mecanismo_por_id(mecanismo_especifico_id)
        if mecanismo is None:
            mecanismo = rng.choice(CATALOGO_FALHAS_TREINAMENTO)
    else:
        # Filtra pelo nível de dificuldade
        candidatos = [m for m in CATALOGO_FALHAS_TREINAMENTO
                      if dificuldade == "Todos" or m.dificuldade == dificuldade]
        if not candidatos:
            candidatos = CATALOGO_FALHAS_TREINAMENTO
        mecanismo = rng.choice(candidatos)

    # Severidade proporcional à dificuldade
    sev_map = {
        "Iniciante": float(rng.uniform(0.80, 1.00)),
        "Intermediario": float(rng.uniform(0.50, 0.80)),
        "Avancado": float(rng.uniform(0.30, 0.55)),
        "Mestre": float(rng.uniform(0.25, 0.45)),
    }
    severidade = sev_map.get(dificuldade, 0.70)

    # Gera série temporal de 40 passos com a falha iniciando no passo 15
    df_serie = pi_telemetry.gerar_serie_temporal_pi(
        params_base=params_base,
        n_passos=40,
        dt_minutos=2.0,
        falha_injetada={
            "id": mecanismo.id,
            "parametro": mecanismo.parametro,
            "valor_severo": mecanismo.valor_severo,
        },
        passo_inicio_falha=15,
        severidade_final=severidade,
        tipo_evolucao="rampa",
        seed=int(rng.integers(1, 10000)),
    )

    # Extrai o snapshot final para diagnóstico pontual
    p_final = dict(params_base)
    val_ini = params_base.get(mecanismo.parametro, 0.0)
    p_final[mecanismo.parametro] = val_ini + severidade * (mecanismo.valor_severo - val_ini)
    res_final = sistema.simular(p_final)
    snap_final = pi_telemetry.extrair_snapshot_pi(res_final, p_final, adicionar_ruido=True, rng=rng)

    vetor_z = {tag: info["valor"] for tag, info in snap_final.items()}
    diagnostico_ia = classificar_m_falha_minimo_residuo(vetor_z, params_base)

    caso = {
        "mecanismo_gabarito": mecanismo,
        "severidade": severidade,
        "dificuldade": dificuldade,
        "df_serie_pi": df_serie,
        "snapshot_final_pi": snap_final,
        "vetor_z_medido": vetor_z,
        "diagnostico_ia": diagnostico_ia,
    }
    return caso


def avaliar_diagnostico_usuario(
    caso: Dict[str, Any],
    subsistema_escolhido: str,
    mecanismo_id_escolhido: str,
    severidade_escolhida: str,  # 'Leve/Incipiente', 'Moderada/Alerta', 'Severa/Crítica'
    acao_escolhida: str,
) -> Dict[str, Any]:
    """Avalia as respostas submetidas pelo usuário no modo de treinamento.

    Retorna a pontuação obtida (Score 0-100), acertos por categoria e feedback detalhado.
    """
    gabarito: MecanismoFalhaInfo = caso["mecanismo_gabarito"]
    sev_real = caso["severidade"]

    # 1. Pontuação de Subsistema (25 pts)
    acertou_subsistema = (subsistema_escolhido == gabarito.subsistema)
    pts_sub = 25.0 if acertou_subsistema else 0.0

    # 2. Pontuação de Mecanismo / Causa-Raiz (45 pts)
    acertou_mecanismo = (mecanismo_id_escolhido == gabarito.id)
    pts_mec = 45.0 if acertou_mecanismo else 0.0

    # 3. Pontuação de Severidade (15 pts)
    if sev_real >= 0.70:
        sev_esperada = "Severa/Crítica"
    elif sev_real >= 0.40:
        sev_esperada = "Moderada/Alerta"
    else:
        sev_esperada = "Leve/Incipiente"
    
    acertou_severidade = (severidade_escolhida == sev_esperada)
    pts_sev = 15.0 if acertou_severidade else 0.0

    # 4. Pontuação da Ação Prescritiva (15 pts)
    # Compara afinidade com a ação do gabarito
    acertou_acao = (acao_escolhida.strip() == gabarito.acao_prescritiva.strip())
    pts_acao = 15.0 if acertou_acao else 0.0

    score_total = pts_sub + pts_mec + pts_sev + pts_acao

    if score_total >= 90:
        classificacao = "⭐⭐⭐ EXCELENTE (Especialista Offshore)"
        status_aprovado = True
    elif score_total >= 70:
        classificacao = "⭐⭐ APROVADO (Operador Qualificado)"
        status_aprovado = True
    else:
        classificacao = "⚠️ NECESSITA REVISÃO TÉCNICA"
        status_aprovado = False

    return {
        "score_total": score_total,
        "classificacao": classificacao,
        "aprovado": status_aprovado,
        "pts_subsistema": pts_sub,
        "pts_mecanismo": pts_mec,
        "pts_severidade": pts_sev,
        "pts_acao": pts_acao,
        "gabarito_mecanismo": gabarito,
        "severidade_esperada": sev_esperada,
        "acao_esperada": gabarito.acao_prescritiva,
        "explicacao_tecnica": gabarito.explicacao_tecnica,
        "normas": gabarito.norma_referencia,
        "sintomas_chave": gabarito.sintomas_pi,
    }
