"""Painel de Falhas — cenários de falha isolada sobre a cascata física.

Cruza o catálogo de mecanismos de falha do livro (Tabela 28.2, Cap. 28.3,
56 mecanismos) com os parâmetros ``ASSUMIDO`` já existentes em
``constantes.py``/``sistema.parametros_default()``: dos 56, **dez** têm
hoje, no simulador, um único parâmetro que os representa fielmente — basta
alterá-lo e rodar ``sistema.simular()`` de novo para produzir o cenário de
falha. Os 46 restantes exigiriam física ainda não modelada neste app
(espectro de vibração, correntes por fase, circuito de óleo) e ficam fora
deste catálogo — não é uma limitação escondida, é o escopo real.

Cada cenário roda a cascata duas vezes — parâmetro saudável (valor de
``parametros_default()``) contra parâmetro ``valor_severo`` interpolado por
``severidade`` — e compara um único KPI indicado pelo próprio catálogo.
Não roda o EKF/VAE/PIML sobre o cenário: mostra a física, não testa se o
algoritmo de detecção do livro (coluna ``deteccao_primaria``) de fato o
capturaria — essa é uma extensão natural, não implementada aqui.
"""

from __future__ import annotations

from . import sistema

# Limiares de classificação de status — deliberadamente simples e únicos
# para todos os cenários (ASSUMIDO, não vem do livro): o desvio percentual
# do KPI principal, na direção que piora a condição da máquina, acima de
# 10% vira ALERTA, acima de 25% vira CRÍTICO. Um mecanismo cujo efeito
# físico direto é pequeno mesmo em severidade máxima (ex.: cenário 1,
# folga LP — ver nota no catálogo abaixo) fica em OK por este critério
# simples, o que é o próprio ponto pedagógico: é exatamente por isso que
# o livro recomenda EKF em vez de limiar direto para esses casos.
LIMIAR_ALERTA_PCT = 10.0
LIMIAR_CRITICO_PCT = 25.0

OK = "OK"
ALERTA = "ALERTA"
CRITICO = "CRÍTICO"

CATALOGO_CENARIOS: list[dict] = [
    {
        "id": "folga_lp",
        "nome": "Desgaste de folgas (estágio LP)",
        "capitulo": "Cap. 9",
        "eq_ref": "Eq. 9.3",
        "parametro": "folga_rel",
        "valor_severo": 0.020,  # mesmo limiar crítico do cenário do Cap. 29
        "kpi_path": ("kpis", "eta_v_lp"),
        "direcao_piora": "diminui",
        "deteccao_primaria": "EKF (δ)",
        "descricao": (
            "Erosão progressiva do perfil do rotor aumenta a folga δ/L, "
            "elevando a fuga interna entre câmaras (Eq. 9.3)."
        ),
    },
    {
        "id": "fouling_intercooler",
        "nome": "Fouling (intercooler)",
        "capitulo": "Cap. 10",
        "eq_ref": "Eq. 10.5",
        "parametro": "r_f_equiv",
        "valor_severo": 0.002,
        "kpi_path": ("kpis", "efetividade_intercooler"),
        "direcao_piora": "diminui",
        "deteccao_primaria": "EKF (R_f)",
        "descricao": (
            "Incrustação na superfície de troca do intercooler degrada a "
            "condutância térmica global (UA), reduzindo a efetividade."
        ),
    },
    {
        "id": "filtro_admissao",
        "nome": "Filtro de admissão obstruído",
        "capitulo": "Cap. 5/13",
        "eq_ref": "Eq. 5.4",
        "parametro": "zeta_filtro",
        "valor_severo": 10.0,
        "kpi_path": ("kpis", "dp_filtro_mbar"),
        "direcao_piora": "aumenta",
        "deteccao_primaria": "Limiar direto",
        "descricao": (
            "Acúmulo de partículas/sal no elemento filtrante eleva o "
            "coeficiente de perda de carga ζ na admissão."
        ),
    },
    {
        "id": "exaustor_hood",
        "nome": "Falha do exaustor (invólucro/Hood)",
        "capitulo": "Cap. 2",
        "eq_ref": "Eq. 2.2",
        "parametro": "m_dot_vent",
        "valor_severo": 0.15,
        "kpi_path": ("kpis", "t_hood_c"),
        "direcao_piora": "aumenta",
        "deteccao_primaria": "PIML (ambíguo com outras fontes de calor do invólucro)",
        "descricao": (
            "Filtro do exaustor obstruído, pá danificada ou motor em falha "
            "reduz a vazão de ventilação forçada do invólucro acústico."
        ),
    },
    {
        "id": "arrefecimento_carcaca",
        "nome": "Perda de arrefecimento ativo da carcaça",
        "capitulo": "Cap. 9",
        "eq_ref": "Eq. 9.15",
        "parametro": "cond_arref_carcaca",
        "valor_severo": 5.0,
        "kpi_path": ("kpis", "t_carcaca_c"),
        "direcao_piora": "aumenta",
        "deteccao_primaria": "PIML (ambíguo com falha de invólucro, Cap. 2)",
        "descricao": (
            "Degradação da ventilação/arrefecimento ativo do elemento "
            "compressor reduz a condutância de arrefecimento forçado."
        ),
    },
    {
        "id": "folga_termica_rotor",
        "nome": "Contato/rubbing por folga térmica do rotor",
        "capitulo": "Cap. 9",
        "eq_ref": "Eq. 9.7/9.18/9.19",
        "parametro": "delta_nom_um",
        "valor_severo": 120.0,
        "kpi_path": ("kpis", "folga_residual_um"),
        "direcao_piora": "diminui",
        "deteccao_primaria": "Limiar direto",
        "descricao": (
            "Folga nominal a frio menor que a de projeto (montagem, "
            "desgaste de flange) — em severidade máxima, a dilatação "
            "térmica diferencial consome a folga inteira e cruza para "
            "contato metal-metal (folga residual negativa)."
        ),
    },
    {
        "id": "leito_psa_dp",
        "nome": "Filtro coalescente / leito PSA saturado (ΔP)",
        "capitulo": "Cap. 15",
        "eq_ref": "Eq. 15.7",
        "parametro": "dp_real_psa",
        "valor_severo": 0.90e5,
        "kpi_path": ("kpis", "hi_des"),
        "direcao_piora": "diminui",
        "deteccao_primaria": "Limiar direto (HI_des)",
        "descricao": (
            "Colmatagem progressiva do leito dessecante eleva a perda de "
            "carga real medida acima do valor nominal de projeto."
        ),
    },
    {
        "id": "psa_breakthrough",
        "nome": "Breakthrough (secador PSA)",
        "capitulo": "Cap. 15",
        "eq_ref": "Eq. 15.7",
        "parametro": "pdp_real_c",
        "valor_severo": -10.0,
        "kpi_path": ("kpis", "hi_des"),
        "direcao_piora": "diminui",
        "deteccao_primaria": "VAE (envelhecimento gradual, sem limiar estabelecido)",
        "descricao": (
            "Material dessecante degradado ou saturado deixa passar "
            "umidade — ponto de orvalho de saída sobe em relação ao alvo "
            "de projeto (Classe 2 ISO 8573-1)."
        ),
    },
    {
        "id": "eta_mec_mancais",
        "nome": "Desgaste de mancais/engrenagens (perda de eficiência mecânica)",
        "capitulo": "Cap. 5/6",
        "eq_ref": "Eq. 5.5",
        "parametro": "eta_mec",
        "valor_severo": 0.85,
        "kpi_path": ("kpis", "spc"),
        "direcao_piora": "aumenta",
        "deteccao_primaria": "Limiar direto",
        "descricao": (
            "Atrito crescente em mancais e engrenamentos consome mais "
            "potência sem converter em trabalho de compressão, elevando "
            "o consumo específico."
        ),
    },
    {
        "id": "motor_escorregamento",
        "nome": "Motor degradado (escorregamento elevado)",
        "capitulo": "Cap. 4",
        "eq_ref": "Eq. 4.11",
        "parametro": "s_motor",
        "valor_severo": 0.08,
        "kpi_path": ("kpis", "eta_mot"),
        "direcao_piora": "diminui",
        "deteccao_primaria": "Limiar direto",
        "descricao": (
            "Barras de rotor parcialmente rompidas ou entreferro "
            "desigual aumentam o escorregamento nominal do motor de "
            "indução, elevando a perda Joule do rotor."
        ),
    },
]


def _get(resultado: dict, caminho: tuple[str, str]):
    valor = resultado
    for chave in caminho:
        valor = valor[chave]
    return valor


def _classificar(delta_pct: float, direcao_piora: str) -> str:
    """Classifica o desvio do KPI principal em OK/ALERTA/CRÍTICO.

    `delta_pct` é o desvio percentual assinado (falha - saudável). Convertido
    para "piora" (positivo quando o KPI se moveu na direção que piora a
    condição da máquina) antes de comparar contra os limiares — ver módulo.
    """
    piora_pct = delta_pct if direcao_piora == "aumenta" else -delta_pct
    if piora_pct >= LIMIAR_CRITICO_PCT:
        return CRITICO
    if piora_pct >= LIMIAR_ALERTA_PCT:
        return ALERTA
    return OK


def rodar_cenario(params_base: dict, cenario: dict, severidade: float = 1.0) -> dict:
    """Roda um cenário de falha isolada: saudável vs. `parametro` interpolado
    até `valor_severo` por `severidade` (0 = saudável, 1 = severidade máxima
    do cenário). Todos os demais parâmetros permanecem em `params_base`.
    """
    severidade = max(0.0, min(1.0, float(severidade)))
    valor_saudavel = params_base[cenario["parametro"]]
    valor_falha = valor_saudavel + severidade * (cenario["valor_severo"] - valor_saudavel)

    res_saudavel = sistema.simular(params_base)
    res_falha = sistema.simular({**params_base, cenario["parametro"]: valor_falha})

    kpi_saudavel = _get(res_saudavel, cenario["kpi_path"])
    kpi_falha = _get(res_falha, cenario["kpi_path"])
    delta = kpi_falha - kpi_saudavel
    delta_pct = 100.0 * delta / abs(kpi_saudavel) if kpi_saudavel else 0.0

    status = _classificar(delta_pct, cenario["direcao_piora"])
    # Override físico: folga residual negativa é contato metal-metal real,
    # independente do limiar percentual genérico.
    if cenario["kpi_path"] == ("kpis", "folga_residual_um") and kpi_falha < 0:
        status = CRITICO

    return {
        "id": cenario["id"],
        "nome": cenario["nome"],
        "capitulo": cenario["capitulo"],
        "eq_ref": cenario["eq_ref"],
        "parametro": cenario["parametro"],
        "valor_saudavel": valor_saudavel,
        "valor_falha": valor_falha,
        "kpi_path": cenario["kpi_path"],
        "kpi_saudavel": kpi_saudavel,
        "kpi_falha": kpi_falha,
        "delta_pct": delta_pct,
        "status": status,
        "deteccao_primaria": cenario["deteccao_primaria"],
        "descricao": cenario["descricao"],
    }


def rodar_todos_cenarios(params_base: dict, severidade: float = 1.0) -> list[dict]:
    """Roda `rodar_cenario` para cada entrada de `CATALOGO_CENARIOS`."""
    return [rodar_cenario(params_base, cenario, severidade)
            for cenario in CATALOGO_CENARIOS]
