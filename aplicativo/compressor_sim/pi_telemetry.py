"""Módulo de Telemetria e Integração com o OSIsoft PI System.

Implementa o mapeamento de tags industriais, gerador de dados em tempo real,
emulador de séries temporais com ruído de instrumentação, detecção de qualidade
de sinal (Good/Bad/Substituted) e exportador/importador no formato OSIsoft PI.

Baseado na Tabela 18.1 (Matriz completa de variáveis e instrumentação) e no
Capítulo 17 (Modelagem Digital Twin: IA, Exergia e Sustentabilidade) do livro
"Gêmeo Digital de Sistemas de Compressão Offshore".
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from . import constantes, nucleo, sistema


@dataclass
class TagPI:
    """Metadados de uma tag industrial do PI System."""
    tag: str
    descricao: str
    ponto: str
    subsistema: str
    unidade: str
    tag_livro: str
    tipo: str  # 'Analog', 'Digital', 'Calculated'
    valor_nom: float
    faixa_min: float
    faixa_max: float
    alarme_l: Optional[float] = None
    alarme_ll: Optional[float] = None
    alarme_h: Optional[float] = None
    alarme_hh: Optional[float] = None
    funcao: str = ""


# Definição do catálogo completo de Tags PI baseado na Tabela 18.1 do livro
CATALOGO_TAGS_PI_PADRAO: List[Dict[str, Any]] = [
    # Ponto A: MCC / Painel Elétrico
    {
        "tag_sufixo": "ELE_VL",
        "descricao": "Tensão de Linha de Alimentação do Motor",
        "ponto": "A",
        "subsistema": "Painel Elétrico / MCC",
        "unidade": "V",
        "tag_livro": "V_L",
        "tipo": "Analog",
        "valor_nom": 4160.0,
        "faixa_min": 3500.0,
        "faixa_max": 4800.0,
        "alarme_l": 3950.0,
        "alarme_ll": 3740.0,
        "alarme_h": 4370.0,
        "alarme_hh": 4580.0,
        "funcao": "Alimentação elétrica do motor trifásico",
    },
    {
        "tag_sufixo": "ELE_I",
        "descricao": "Corrente de Linha do Motor Principal",
        "ponto": "A",
        "subsistema": "Painel Elétrico / MCC",
        "unidade": "A",
        "tag_livro": "I",
        "tipo": "Analog",
        "valor_nom": 42.0,
        "faixa_min": 0.0,
        "faixa_max": 80.0,
        "alarme_h": 50.0,
        "alarme_hh": 55.0,
        "funcao": "Carga elétrica do motor (Eq. 4.1)",
    },
    {
        "tag_sufixo": "ELE_FREQ",
        "descricao": "Frequência de Alimentação do VSD",
        "ponto": "A",
        "subsistema": "Painel Elétrico / MCC",
        "unidade": "Hz",
        "tag_livro": "f",
        "tipo": "Analog",
        "valor_nom": 60.0,
        "faixa_min": 20.0,
        "faixa_max": 75.0,
        "alarme_l": 25.0,
        "alarme_h": 65.0,
        "funcao": "Comando de velocidade angular do inversor VSD",
    },
    {
        "tag_sufixo": "ELE_COSPHI",
        "descricao": "Fator de Potência Elétrica",
        "ponto": "A",
        "subsistema": "Painel Elétrico / MCC",
        "unidade": "-",
        "tag_livro": "cos φ",
        "tipo": "Analog",
        "valor_nom": 0.88,
        "faixa_min": 0.50,
        "faixa_max": 1.00,
        "alarme_l": 0.80,
        "funcao": "Eficiência da conversão eletromecânica",
    },
    {
        "tag_sufixo": "ELE_VU",
        "descricao": "Desbalanço de Tensão entre Fases (NEMA MG1)",
        "ponto": "A",
        "subsistema": "Painel Elétrico / MCC",
        "unidade": "%",
        "tag_livro": "VU",
        "tipo": "Calculated",
        "valor_nom": 0.4,
        "faixa_min": 0.0,
        "faixa_max": 5.0,
        "alarme_h": 1.0,
        "alarme_hh": 2.0,
        "funcao": "Assimetria de alimentação (Eq. 4.8)",
    },
    {
        "tag_sufixo": "ELE_IU",
        "descricao": "Desbalanço de Corrente entre Fases (NEMA MG1)",
        "ponto": "A",
        "subsistema": "Painel Elétrico / MCC",
        "unidade": "%",
        "tag_livro": "IU",
        "tipo": "Calculated",
        "valor_nom": 1.2,
        "faixa_min": 0.0,
        "faixa_max": 15.0,
        "alarme_h": 5.0,
        "alarme_hh": 8.0,
        "funcao": "Detecção de curto entre espiras / assimetria (Eq. 4.8)",
    },

    # Ponto B: Trem de Transmissão e Gearbox
    {
        "tag_sufixo": "MEC_RPM",
        "descricao": "Rotação Medida do Motor de Acionamento",
        "ponto": "B",
        "subsistema": "Transmissão / Eixos",
        "unidade": "RPM",
        "tag_livro": "N_mot",
        "tipo": "Analog",
        "valor_nom": 3528.0,
        "faixa_min": 1000.0,
        "faixa_max": 4000.0,
        "alarme_h": 3800.0,
        "funcao": "Cinemática e rotação síncrona/escorregamento (Eq. 4.4)",
    },
    {
        "tag_sufixo": "MEC_TORQ",
        "descricao": "Torque Estimado no Eixo Principal",
        "ponto": "B",
        "subsistema": "Transmissão / Eixos",
        "unidade": "N·m",
        "tag_livro": "τ",
        "tipo": "Calculated",
        "valor_nom": 530.0,
        "faixa_min": 100.0,
        "faixa_max": 1200.0,
        "alarme_h": 750.0,
        "alarme_hh": 850.0,
        "funcao": "Momento torsor transmitido à gearbox (Eq. 6.8)",
    },
    {
        "tag_sufixo": "MEC_VIB_RMS",
        "descricao": "Severidade Vibratória Global",
        "ponto": "B",
        "subsistema": "Transmissão / Eixos",
        "unidade": "mm/s",
        "tag_livro": "v_rms",
        "tipo": "Analog",
        "valor_nom": 2.10,
        "faixa_min": 0.0,
        "faixa_max": 20.0,
        "alarme_h": 4.5,
        "alarme_hh": 7.1,
        "funcao": "Vibração global de banda larga (API 619 / OEM)",
    },
    {
        "tag_sufixo": "MEC_SIGMA_B",
        "descricao": "Tensão de Flexão na Raiz do Dente",
        "ponto": "B",
        "subsistema": "Transmissão / Eixos",
        "unidade": "MPa",
        "tag_livro": "σ_b",
        "tipo": "Calculated",
        "valor_nom": 120.0,
        "faixa_min": 0.0,
        "faixa_max": 400.0,
        "alarme_h": 250.0,
        "alarme_hh": 300.0,
        "funcao": "Modelo de Lewis e integridade mecânica (Eq. 8.7)",
    },

    # Ponto C: Estágio de Baixa Pressão (LP)
    {
        "tag_sufixo": "LP_PSUC",
        "descricao": "Pressão de Sucção do Estágio LP",
        "ponto": "C",
        "subsistema": "Compressão Estágio LP",
        "unidade": "bar",
        "tag_livro": "P_s,lp",
        "tipo": "Analog",
        "valor_nom": 1.013,
        "faixa_min": 0.80,
        "faixa_max": 1.20,
        "alarme_l": 0.95,
        "alarme_ll": 0.90,
        "funcao": "Pressão de admissão atmosférica pós-filtro (Eq. 5.4)",
    },
    {
        "tag_sufixo": "LP_TDISC",
        "descricao": "Temperatura de Descarga do Estágio LP",
        "ponto": "C",
        "subsistema": "Compressão Estágio LP",
        "unidade": "°C",
        "tag_livro": "T_d,lp",
        "tipo": "Analog",
        "valor_nom": 123.8,
        "faixa_min": 20.0,
        "faixa_max": 180.0,
        "alarme_h": 140.0,
        "alarme_hh": 150.0,
        "funcao": "Calor de compressão do 1º estágio politrópico (Eq. 9.5)",
    },
    {
        "tag_sufixo": "LP_CLEARANCE",
        "descricao": "Folga Relativa Estimada LP (Soft-Sensor EKF)",
        "ponto": "C",
        "subsistema": "Compressão Estágio LP",
        "unidade": "μm/m",
        "tag_livro": "δ_lp/L",
        "tipo": "Calculated",
        "valor_nom": 2.0,
        "faixa_min": 1.0,
        "faixa_max": 25.0,
        "alarme_h": 10.0,
        "alarme_hh": 20.0,
        "funcao": "Desgaste de perfil dos rotores helicoidais (Eq. 9.3)",
    },

    # Ponto D: Intercooler
    {
        "tag_sufixo": "IC_TW_IN",
        "descricao": "Temperatura de Entrada da Água de Resfriamento",
        "ponto": "D",
        "subsistema": "Intercooler",
        "unidade": "°C",
        "tag_livro": "T_w,in",
        "tipo": "Analog",
        "valor_nom": 25.0,
        "faixa_min": 10.0,
        "faixa_max": 45.0,
        "alarme_h": 32.0,
        "alarme_hh": 36.0,
        "funcao": "Temperatura da utilidade de água marinha / offloading",
    },
    {
        "tag_sufixo": "IC_PINT",
        "descricao": "Pressão Interestágio (Descarga LP / Sucção HP)",
        "ponto": "D",
        "subsistema": "Intercooler",
        "unidade": "bar",
        "tag_livro": "P_int",
        "tipo": "Analog",
        "valor_nom": 2.83,
        "faixa_min": 1.5,
        "faixa_max": 4.5,
        "alarme_l": 2.3,
        "alarme_h": 3.4,
        "funcao": "Alocação ótima de carga interestágios (Eq. 5.14)",
    },
    {
        "tag_sufixo": "IC_DP",
        "descricao": "Perda de Carga no Intercooler",
        "ponto": "D",
        "subsistema": "Intercooler",
        "unidade": "mbar",
        "tag_livro": "ΔP_ic",
        "tipo": "Analog",
        "valor_nom": 60.0,
        "faixa_min": 0.0,
        "faixa_max": 300.0,
        "alarme_h": 120.0,
        "alarme_hh": 180.0,
        "funcao": "Restrição ao escoamento e acúmulo de sujeira",
    },
    {
        "tag_sufixo": "IC_MCOND",
        "descricao": "Vazão Mássica de Condensado Separado",
        "ponto": "D",
        "subsistema": "Intercooler",
        "unidade": "kg/h",
        "tag_livro": "ṁ_c",
        "tipo": "Calculated",
        "valor_nom": 4.5,
        "faixa_min": 0.0,
        "faixa_max": 25.0,
        "funcao": "Taxa de extração psicrométrica de umidade (Eq. 10.6)",
    },

    # Ponto E: Estágio de Alta Pressão (HP)
    {
        "tag_sufixo": "HP_PDISC",
        "descricao": "Pressão de Descarga do Estágio HP",
        "ponto": "E",
        "subsistema": "Compressão Estágio HP",
        "unidade": "bar",
        "tag_livro": "P_d,hp",
        "tipo": "Analog",
        "valor_nom": 8.0,
        "faixa_min": 4.0,
        "faixa_max": 12.0,
        "alarme_l": 6.5,
        "alarme_h": 9.5,
        "alarme_hh": 10.5,
        "funcao": "Pressão final de geração do trem (Eq. 11.1)",
    },
    {
        "tag_sufixo": "HP_TDISC",
        "descricao": "Temperatura de Descarga do Estágio HP",
        "ponto": "E",
        "subsistema": "Compressão Estágio HP",
        "unidade": "°C",
        "tag_livro": "T_d,hp",
        "tipo": "Analog",
        "valor_nom": 138.5,
        "faixa_min": 50.0,
        "faixa_max": 200.0,
        "alarme_h": 160.0,
        "alarme_hh": 175.0,
        "funcao": "Temperatura crítica do 2º estágio (Eq. 11.1)",
    },
    {
        "tag_sufixo": "HP_AXIAL",
        "descricao": "Posição Axial do Rotor HP (Sonda de Proximidade)",
        "ponto": "E",
        "subsistema": "Compressão Estágio HP",
        "unidade": "μm",
        "tag_livro": "δ_ax",
        "tipo": "Analog",
        "valor_nom": 15.0,
        "faixa_min": -50.0,
        "faixa_max": 100.0,
        "alarme_h": 40.0,
        "alarme_hh": 60.0,
        "funcao": "Desgaste precoce do mancal de escora (Eq. 11.5)",
    },

    # Ponto F: Aftercooler & Tratamento Primário
    {
        "tag_sufixo": "AC_TAC_OUT",
        "descricao": "Temperatura de Saída do Aftercooler",
        "ponto": "F",
        "subsistema": "Aftercooler",
        "unidade": "°C",
        "tag_livro": "T_ac,out",
        "tipo": "Analog",
        "valor_nom": 28.5,
        "faixa_min": 15.0,
        "faixa_max": 65.0,
        "alarme_h": 38.0,
        "alarme_hh": 45.0,
        "funcao": "Temperatura pré-secagem e proteção do leito PSA (Eq. 14.1)",
    },

    # Ponto G: Secador por Adsorção PSA
    {
        "tag_sufixo": "PSA_TDP",
        "descricao": "Ponto de Orvalho sob Pressão (PDP) na Saída",
        "ponto": "G",
        "subsistema": "Secagem PSA",
        "unidade": "°C",
        "tag_livro": "T_dp",
        "tipo": "Analog",
        "valor_nom": -42.0,
        "faixa_min": -70.0,
        "faixa_max": 20.0,
        "alarme_h": -40.0,  # Classe 2 ISO 8573-1
        "alarme_hh": -20.0,  # Perda severa de secagem
        "funcao": "Qualidade do ar e proteção de instrumentação pneumática",
    },
    {
        "tag_sufixo": "PSA_MPURGE",
        "descricao": "Vazão de Purga de Regeneração do PSA",
        "ponto": "G",
        "subsistema": "Secagem PSA",
        "unidade": "kg/s",
        "tag_livro": "ṁ_p",
        "tipo": "Calculated",
        "valor_nom": 0.032,
        "faixa_min": 0.0,
        "faixa_max": 0.15,
        "funcao": "Ar consumido na regeneração térmica/pressão (Eq. 15.2)",
    },
    {
        "tag_sufixo": "FLT_DP",
        "descricao": "Perda de Carga nos Filtros Coalescentes",
        "ponto": "G",
        "subsistema": "Filtragem de Linha",
        "unidade": "mbar",
        "tag_livro": "ΔP_filt",
        "tipo": "Analog",
        "valor_nom": 120.0,
        "faixa_min": 20.0,
        "faixa_max": 800.0,
        "alarme_h": 350.0,
        "alarme_hh": 500.0,
        "funcao": "Saturação de óleo/partículas no elemento filtrante (Eq. 14.5)",
    },

    # Ponto H: Vaso Pulmão de Armazenamento
    {
        "tag_sufixo": "TK_PTK",
        "descricao": "Pressão de Armazenamento no Vaso Pulmão",
        "ponto": "H",
        "subsistema": "Vaso de Pressão (Air Receiver)",
        "unidade": "bar",
        "tag_livro": "P_tk",
        "tipo": "Analog",
        "valor_nom": 7.85,
        "faixa_min": 0.0,
        "faixa_max": 12.0,
        "alarme_l": 6.8,   # P_L
        "alarme_ll": 6.0,  # P_LL
        "alarme_hh": 10.0, # ASME VIII PSV setpoint
        "funcao": "Buffer de energia e estabilização de rede (Eq. 3.5)",
    },
    {
        "tag_sufixo": "TK_LTK",
        "descricao": "Nível de Condensado no Vaso Pulmão",
        "ponto": "H",
        "subsistema": "Vaso de Pressão (Air Receiver)",
        "unidade": "%",
        "tag_livro": "L_tk",
        "tipo": "Analog",
        "valor_nom": 5.0,
        "faixa_min": 0.0,
        "faixa_max": 100.0,
        "alarme_h": 25.0,
        "alarme_hh": 50.0,
        "funcao": "Acúmulo de líquido e integridade do dreno de fundo",
    },

    # Ponto I: Header de Distribuição e Consumidores
    {
        "tag_sufixo": "HDR_MTOT",
        "descricao": "Vazão Mássica Total de Demanda da Planta",
        "ponto": "I",
        "subsistema": "Header / Distribuição",
        "unidade": "kg/s",
        "tag_livro": "ṁ_tot",
        "tipo": "Analog",
        "valor_nom": 0.185,
        "faixa_min": 0.0,
        "faixa_max": 0.60,
        "funcao": "Consumo total de ar da unidade offshore (Eq. 16.1)",
    },
    {
        "tag_sufixo": "HDR_STAT",
        "descricao": "Status dos Ramais de Distribuição (Emerg/Proc/Serv)",
        "ponto": "I",
        "subsistema": "Header / Distribuição",
        "unidade": "bin",
        "tag_livro": "δ_i",
        "tipo": "Digital",
        "valor_nom": 1.0,
        "faixa_min": 0.0,
        "faixa_max": 1.0,
        "funcao": "Lógica de corte escalonado de utilidades (Eq. 16.1)",
    },

    # Circuito de Óleo e Gestão Térmica (Cap. 7 e 12)
    {
        "tag_sufixo": "OIL_TT_RET",
        "descricao": "Temperatura de Retorno de Óleo dos Mancais",
        "ponto": "B/D",
        "subsistema": "Circuito de Lubrificação",
        "unidade": "°C",
        "tag_livro": "T_óleo,ret",
        "tipo": "Analog",
        "valor_nom": 65.0,
        "faixa_min": 25.0,
        "faixa_max": 100.0,
        "alarme_h": 78.0,
        "alarme_hh": 85.0,
        "funcao": "Calor removido dos mancais e gearbox (Eq. 12.1)",
    },
    {
        "tag_sufixo": "OIL_PT_SUP",
        "descricao": "Pressão de Suprimento de Óleo aos Mancais",
        "ponto": "B/D",
        "subsistema": "Circuito de Lubrificação",
        "unidade": "bar",
        "tag_livro": "P_sup,óleo",
        "tipo": "Analog",
        "valor_nom": 2.2,
        "faixa_min": 0.5,
        "faixa_max": 5.0,
        "alarme_l": 1.5,
        "alarme_ll": 1.2,
        "funcao": "Pressão de óleo após desaerador (Eq. 12.2)",
    },
    {
        "tag_sufixo": "OIL_DP_SEP",
        "descricao": "Perda de Carga no Deaerador de Óleo",
        "ponto": "B/D",
        "subsistema": "Circuito de Lubrificação",
        "unidade": "mbar",
        "tag_livro": "ΔP_sep",
        "tipo": "Analog",
        "valor_nom": 150.0,
        "faixa_min": 20.0,
        "faixa_max": 800.0,
        "alarme_h": 400.0,
        "alarme_hh": 600.0,
        "funcao": "Saturação do elemento desaerador de lubrificante",
    },

    # Indicadores do Gêmeo Digital (Cap. 17 e 26)
    {
        "tag_sufixo": "DT_EXERGY_DEST",
        "descricao": "Taxa de Destruição de Exergia Total",
        "ponto": "DT",
        "subsistema": "Gêmeo Digital (Exergia)",
        "unidade": "kW",
        "tag_livro": "İ_total",
        "tipo": "Calculated",
        "valor_nom": 32.5,
        "faixa_min": 10.0,
        "faixa_max": 80.0,
        "alarme_h": 45.0,
        "funcao": "Perda de potencial de trabalho / irreversibilidade (Eq. 17.3)",
    },
    {
        "tag_sufixo": "DT_CO2_RATE",
        "descricao": "Taxa Instantânea de Emissão de CO2",
        "ponto": "DT",
        "subsistema": "Gêmeo Digital (Sustentabilidade)",
        "unidade": "kg/h",
        "tag_livro": "ṁ_CO2",
        "tipo": "Calculated",
        "valor_nom": 48.0,
        "faixa_min": 15.0,
        "faixa_max": 120.0,
        "funcao": "Pegada de carbono associada ao consumo elétrico (Eq. 17.5)",
    },
    {
        "tag_sufixo": "DT_HEALTH_INDEX",
        "descricao": "Health Index Composto da Máquina (HI)",
        "ponto": "DT",
        "subsistema": "Gêmeo Digital (Saúde)",
        "unidade": "-",
        "tag_livro": "HI",
        "tipo": "Calculated",
        "valor_nom": 0.98,
        "faixa_min": 0.0,
        "faixa_max": 1.0,
        "alarme_l": 0.70,
        "alarme_ll": 0.40,
        "funcao": "Índice sintético de saúde operacional (Eq. 26.4)",
    },
]


def obter_catalogo_tags_pi(prefixo: str = "CMP01") -> List[TagPI]:
    """Retorna a lista de objetos TagPI com o prefixo da unidade configurado."""
    catalogo = []
    for item in CATALOGO_TAGS_PI_PADRAO:
        tag_nome = f"{prefixo}:{item['tag_sufixo']}"
        tag_obj = TagPI(
            tag=tag_nome,
            descricao=item["descricao"],
            ponto=item["ponto"],
            subsistema=item["subsistema"],
            unidade=item["unidade"],
            tag_livro=item["tag_livro"],
            tipo=item["tipo"],
            valor_nom=item["valor_nom"],
            faixa_min=item["faixa_min"],
            faixa_max=item["faixa_max"],
            alarme_l=item.get("alarme_l"),
            alarme_ll=item.get("alarme_ll"),
            alarme_h=item.get("alarme_h"),
            alarme_hh=item.get("alarme_hh"),
            funcao=item.get("funcao", ""),
        )
        catalogo.append(tag_obj)
    return catalogo


def extrair_snapshot_pi(
    resultado_sim: dict,
    params: dict,
    prefixo: str = "CMP01",
    adicionar_ruido: bool = False,
    rng: Optional[np.random.Generator] = None,
) -> Dict[str, Dict[str, Any]]:
    """Mapeia os resultados da cascata física `sistema.simular()` em um snapshot de Tags PI.

    Retorna um dicionário indexado pelo nome da tag com valor, unidade, qualidade, status de alarme.
    """
    if rng is None:
        rng = np.random.default_rng()

    kpis = resultado_sim["kpis"]
    pot = resultado_sim["potencias"]
    nos = resultado_sim["nos"]
    
    # Extração de variáveis base
    v_l = 4160.0
    freq_vsd = float(params.get("f_vsd", 60.0))
    p_elec_kw = pot["w_total_planta"] / 1000.0 if "w_total_planta" in pot else (pot["w_total"] / 1000.0)
    i_motor = (p_elec_kw * 1000.0) / (np.sqrt(3) * v_l * 0.88) if v_l > 0 else 0.0
    
    s_mot = float(params.get("s_motor", 0.02))
    rpm_motor = (120.0 * freq_vsd / 2.0) * (1.0 - s_mot)
    omega_motor = 2.0 * np.pi * rpm_motor / 60.0
    w_eixo = pot["w_lp"] + pot["w_hp"] + pot.get("perda_vi_lp", 0.0) + pot.get("perda_vi_hp", 0.0)
    torque_eixo = w_eixo / omega_motor if omega_motor > 0 else 0.0
    
    # Vibração básica proporcional à carga e folga
    folga_rel = float(params.get("folga_rel", 0.002))
    vib_base = 2.10 * (1.0 + 8.0 * max(0.0, folga_rel - 0.002)) * (rpm_motor / 3528.0)
    
    # Tensão no dente
    sigma_b = 120.0 * (torque_eixo / 530.0) if torque_eixo > 0 else 120.0
    
    # Ponto LP e HP
    p_suc_lp = nos[0]["p_bar"]
    t_disc_lp = nos[1]["t_c"]
    p_int = nos[1]["p_bar"]
    t_w_in = float(params.get("t_agua", 298.15)) - 273.15
    dp_ic = (nos[1]["p_bar"] - nos[2]["p_bar"]) * 1000.0  # mbar
    m_cond_ic = kpis["condensado_total_kg_h"] * 0.5
    
    p_disc_hp = nos[3]["p_bar"]
    t_disc_hp = nos[3]["t_c"]
    t_ac_out = nos[4]["t_c"]
    
    # Secagem e Vaso
    t_dp = nos[5].get("pdp_c", kpis.get("pdp_alvo_c", -40.0))
    m_purge = nos[-1]["m_dot"] * float(params.get("fator_purga", 0.15))
    dp_filt = kpis["dp_filtro_mbar"]
    p_tk = nos[-1]["p_bar"]
    
    # Óleo e Invólucro
    t_hood = kpis["t_hood_c"]
    t_oil_ret = 65.0 + 0.3 * (t_hood - 30.0) + 5.0 * (1.0 - float(params.get("eta_mec", 0.96)) / 0.96)
    p_oil_sup = 2.2 - 0.001 * float(params.get("dp_real_psa", 0.0) / 1000.0)
    dp_oil_sep = 150.0 + 100.0 * (t_oil_ret - 65.0) / 20.0
    
    # Indicadores do Gêmeo
    exergy_dest_kw = max(0.0, (pot["w_total"] - pot["w_isotermico"]) / 1000.0)
    co2_rate = p_elec_kw * 0.40  # kg CO2 / h (fator 0.40 kg/kWh)
    
    # Mapeamento interno
    leituras_raw: Dict[str, float] = {
        "ELE_VL": v_l,
        "ELE_I": i_motor,
        "ELE_FREQ": freq_vsd,
        "ELE_COSPHI": 0.88,
        "ELE_VU": 0.4,
        "ELE_IU": 1.2,
        "MEC_RPM": rpm_motor,
        "MEC_TORQ": torque_eixo,
        "MEC_VIB_RMS": vib_base,
        "MEC_SIGMA_B": sigma_b,
        "LP_PSUC": p_suc_lp,
        "LP_TDISC": t_disc_lp,
        "LP_CLEARANCE": folga_rel * 1000.0,
        "IC_TW_IN": t_w_in,
        "IC_PINT": p_int,
        "IC_DP": max(10.0, dp_ic),
        "IC_MCOND": m_cond_ic,
        "HP_PDISC": p_disc_hp,
        "HP_TDISC": t_disc_hp,
        "HP_AXIAL": 15.0 + 20.0 * max(0.0, (1.0 - float(params.get("eta_mec", 0.96)) / 0.96)),
        "AC_TAC_OUT": t_ac_out,
        "PSA_TDP": t_dp,
        "PSA_MPURGE": m_purge,
        "FLT_DP": dp_filt,
        "TK_PTK": p_tk,
        "TK_LTK": 5.0,
        "HDR_MTOT": nos[-1]["m_dot"] * float(params.get("n_compressores", 1)),
        "HDR_STAT": 1.0,
        "OIL_TT_RET": t_oil_ret,
        "OIL_PT_SUP": p_oil_sup,
        "OIL_DP_SEP": dp_oil_sep,
        "DT_EXERGY_DEST": exergy_dest_kw,
        "DT_CO2_RATE": co2_rate,
        "DT_HEALTH_INDEX": 0.98,
    }

    # Ruído por desvio padrão típico relativo
    ruidos_rel: Dict[str, float] = {
        "ELE_VL": 0.003, "ELE_I": 0.01, "ELE_FREQ": 0.001, "ELE_COSPHI": 0.005,
        "ELE_VU": 0.05, "ELE_IU": 0.05, "MEC_RPM": 0.002, "MEC_TORQ": 0.015,
        "MEC_VIB_RMS": 0.03, "MEC_SIGMA_B": 0.02, "LP_PSUC": 0.005, "LP_TDISC": 0.008,
        "LP_CLEARANCE": 0.02, "IC_TW_IN": 0.01, "IC_PINT": 0.008, "IC_DP": 0.04,
        "IC_MCOND": 0.05, "HP_PDISC": 0.006, "HP_TDISC": 0.008, "HP_AXIAL": 0.03,
        "AC_TAC_OUT": 0.01, "PSA_TDP": 0.02, "PSA_MPURGE": 0.02, "FLT_DP": 0.03,
        "TK_PTK": 0.005, "TK_LTK": 0.05, "HDR_MTOT": 0.015, "HDR_STAT": 0.0,
        "OIL_TT_RET": 0.01, "OIL_PT_SUP": 0.015, "OIL_DP_SEP": 0.03,
        "DT_EXERGY_DEST": 0.01, "DT_CO2_RATE": 0.01, "DT_HEALTH_INDEX": 0.005
    }

    snapshot: Dict[str, Dict[str, Any]] = {}
    catalogo = obter_catalogo_tags_pi(prefixo)
    timestamp_agora = datetime.now()

    for item in catalogo:
        sufixo = item.tag.split(":", 1)[1] if ":" in item.tag else item.tag
        val_base = leituras_raw.get(sufixo, item.valor_nom)
        
        if adicionar_ruido and sufixo in ruidos_rel and ruidos_rel[sufixo] > 0:
            sigma = abs(val_base) * ruidos_rel[sufixo]
            val = float(val_base + rng.normal(0.0, max(1e-5, sigma)))
        else:
            val = float(val_base)

        # Verificação de status de alarme ISA
        status_alarme = "NORMAL"
        if item.alarme_hh is not None and val >= item.alarme_hh:
            status_alarme = "HH (Trip/Crítico)"
        elif item.alarme_ll is not None and val <= item.alarme_ll:
            status_alarme = "LL (Trip/Crítico)"
        elif item.alarme_h is not None and val >= item.alarme_h:
            status_alarme = "H (Alerta Alto)"
        elif item.alarme_l is not None and val <= item.alarme_l:
            status_alarme = "L (Alerta Baixo)"

        snapshot[item.tag] = {
            "tag": item.tag,
            "descricao": item.descricao,
            "ponto": item.ponto,
            "subsistema": item.subsistema,
            "unidade": item.unidade,
            "valor": val,
            "qualidade": "Good",
            "status_alarme": status_alarme,
            "timestamp": timestamp_agora,
            "tag_livro": item.tag_livro,
            "tipo": item.tipo,
        }

    return snapshot


def gerar_serie_temporal_pi(
    params_base: dict,
    n_passos: int = 60,
    dt_minutos: float = 1.0,
    falha_injetada: Optional[dict] = None,
    passo_inicio_falha: int = 20,
    severidade_final: float = 1.0,
    tipo_evolucao: str = "rampa",  # 'rampa', 'degrau', 'senoidal'
    seed: int = 42,
    prefixo: str = "CMP01",
) -> pd.DataFrame:
    """Gera uma série temporal realista de telemetria do PI System.

    Permite simular operação saudável ou injeção controlada de falhas
    com dinâmica temporal e ruído estatístico.
    """
    rng = np.random.default_rng(seed)
    inicio_tempo = datetime.now() - timedelta(minutes=n_passos * dt_minutos)
    
    registros = []

    for k in range(n_passos):
        t_k = inicio_tempo + timedelta(minutes=k * dt_minutos)
        
        # Determina severidade da falha neste instante
        sev_k = 0.0
        if falha_injetada is not None and k >= passo_inicio_falha:
            if tipo_evolucao == "degrau":
                sev_k = severidade_final
            elif tipo_evolucao == "senoidal":
                fase = (k - passo_inicio_falha) / max(1, n_passos - passo_inicio_falha)
                sev_k = severidade_final * np.sin(np.pi * fase)
            else:  # rampa gradual
                frac = (k - passo_inicio_falha) / max(1, n_passos - passo_inicio_falha)
                sev_k = severidade_final * frac

        # Modifica os parâmetros operacionais se houver falha ativa
        params_k = dict(params_base)
        if falha_injetada is not None and sev_k > 0:
            param_nome = falha_injetada["parametro"]
            val_ini = params_base.get(param_nome, 0.0)
            val_sev = falha_injetada["valor_severo"]
            params_k[param_nome] = val_ini + sev_k * (val_sev - val_ini)

        # Flutuação ambiental diária suave (±1.5 °C)
        t_amb_base = float(params_k.get("t_amb", 303.15))
        delta_amb = 1.5 * np.sin(2.0 * np.pi * k / max(1, n_passos))
        params_k["t_amb"] = t_amb_base + delta_amb

        # Executa a simulação física neste passo
        res_k = sistema.simular(params_k)
        snap_k = extrair_snapshot_pi(
            res_k, params_k, prefixo=prefixo, adicionar_ruido=True, rng=rng
        )

        linha: Dict[str, Any] = {
            "Timestamp": t_k,
            "Passo": k,
            "Severidade_Falha_Pct": sev_k * 100.0,
            "Falha_Ativa": falha_injetada["id"] if (falha_injetada and sev_k > 0) else "NENHUMA",
        }

        for tag_nome, tag_info in snap_k.items():
            linha[tag_nome] = tag_info["valor"]
            linha[f"{tag_nome}_Quality"] = tag_info["qualidade"]
            linha[f"{tag_nome}_Alarm"] = tag_info["status_alarme"]

        registros.append(linha)

    df_resultado = pd.DataFrame(registros)
    return df_resultado


def exportar_pi_csv(df: pd.DataFrame) -> str:
    """Converte o DataFrame gerado para o formato padrão CSV de exportação OSIsoft PI."""
    return df.to_csv(index=False)


def carregar_telemetria_arquivo(arquivo_ou_buffer) -> pd.DataFrame:
    """Importa arquivo CSV ou Excel de telemetria externa, higienizando colunas e timestamps."""
    if hasattr(arquivo_ou_buffer, "name") and arquivo_ou_buffer.name.lower().endswith(".xlsx"):
        df = pd.read_excel(arquivo_ou_buffer)
    else:
        df = pd.read_csv(arquivo_ou_buffer)

    # Identificação da coluna de tempo
    cols_lower = {str(c).lower().strip(): c for c in df.columns}
    for t_col in ["timestamp", "data_hora", "time", "date_time", "datahora"]:
        if t_col in cols_lower:
            df["Timestamp"] = pd.to_datetime(df[cols_lower[t_col]], errors="coerce")
            break

    return df
