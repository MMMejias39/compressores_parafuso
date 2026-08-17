"""Núcleo termodinâmico: estágios de compressão e psicrometria.

Todas as equações referem-se ao livro compressores.tex (número da equação
indicado em cada docstring/comment). Convenções: SI, pressões absolutas (Pa),
temperaturas em K nas equações termodinâmicas.
"""

from __future__ import annotations

import math

from .constantes import CP_AR, GAMMA, R_AR


# ---------------------------------------------------------------------------
# Estágios de compressão
# ---------------------------------------------------------------------------

def delta_p_filtro(zeta: float, rho: float, v: float) -> float:
    """Perda de carga do filtro de admissão [Pa].

    Eq. 5.4 — ΔP_filt = ζ · ρ·v²/2
    """
    return zeta * rho * v**2 / 2.0


def razao_pressao_interna(v_i: float, n: float) -> float:
    """Razão de pressão interna ideal do estágio.

    Eqs. 5.6/5.7 — π_i = V_i^n  (V_i fixo pela geometria do rotor)
    """
    return v_i**n


def potencia_politropica(p_in: float, v_dot_in: float, pi: float,
                         n: float, eta_mec: float) -> float:
    """Potência de compressão de um estágio [W].

    Eq. 5.5 — W = n/(n−1) · P_in · V̇_in · [π^((n−1)/n) − 1] / η_mec
    """
    return (n / (n - 1.0)) * p_in * v_dot_in * (pi**((n - 1.0) / n) - 1.0) / eta_mec


def perda_vi(p1: float, v_dot2: float, pi_operante: float,
             v_i: float, n: float) -> float:
    """Perda por descasamento entre π operante e π_i interna [W] (curva em "V").

    Eqs. 5.8/5.9 — ΔW = V̇2 · |P2 − P1·π_i|
      π > π_i : subcompressão (ΔW_sub = V̇2·(P2 − P_i))
      π < π_i : sobrecompressão (ΔW_sobre = V̇2·(P_i − P2))
    """
    p_i = p1 * razao_pressao_interna(v_i, n)
    p2 = p1 * pi_operante
    return v_dot2 * abs(p2 - p_i)


def temperatura_descarga(t_in: float, pi: float, n: float) -> float:
    """Temperatura de descarga do estágio [K].

    Eq. 11.1 (também Eq. 10.10) — T_out = T_in · π^((n−1)/n)
    """
    return t_in * pi**((n - 1.0) / n)


def eficiencia_volumetrica(k: float, folga_rel: float, pi: float) -> float:
    """Eficiência volumétrica com folga residual δ.

    Eq. 9.3 — η_v = 1 − K·(δ/L)·√(P2/P1)
    """
    return 1.0 - k * folga_rel * math.sqrt(pi)


def potencia_entreferro(p_eixo: float, s: float) -> float:
    """Potência de entreferro do motor [W] — Eq. 4.12 invertida.

    P_ag = P_eixo/(1-s). Simplificação: em vez do circuito equivalente
    completo (Eqs. 4.4/4.5, que exigiriam parâmetros de placa não
    disponíveis neste app), P_ag é obtido diretamente da potência mecânica
    de eixo já calculada pelo restante da cascata.
    """
    return p_eixo / (1.0 - s)


def perdas_motor(s: float, p_ag: float, p_fixas: float) -> float:
    """Perdas totais do motor [W].

    Eq. 4.11 — P_perdas,mot = s·P_ag + P_fixas (Joule do rotor variável
    com a carga via s; estator+núcleo+atrito/ventilação+suplementares
    agregados em P_fixas, de ensaio — método segregado IEC 60034-2-1).
    """
    return s * p_ag + p_fixas


def eficiencia_motor(p_eixo: float, p_ag: float, p_fixas: float) -> float:
    """Eficiência do motor [adimensional] — Eq. 4.12."""
    p_eletrica = p_ag + p_fixas
    return p_eixo / p_eletrica if p_eletrica > 0.0 else 0.0


def calor_gerado_hood(p_perdas_mot: float, p_loss_outros: float, q_casco: float) -> float:
    """Calor total gerado dentro do invólucro (hood) [W] — Eq. 2.1.

    Q_gerado = perdas do motor + perdas de VSD/gearbox (não decompostas
    neste app, ver P_LOSS_HOOD_OUTROS_DEFAULT) + Q_casco (convecção da
    carcaça do estágio LP).
    """
    return p_perdas_mot + p_loss_outros + q_casco


def temperatura_hood_regime(q_gerado: float, m_dot_vent: float, cp: float,
                            t_amb: float) -> float:
    """Temperatura de regime permanente do ar interno do invólucro [K].

    Eq. 2.4 — T_hood = T_amb + Q_gerado/(m_vent·cp), sob mistura completa
    do ar confinado (T_hood ≡ T_exaustão, a leitura de saída do exaustor).
    """
    if m_dot_vent <= 0.0:
        return t_amb
    return t_amb + q_gerado / (m_dot_vent * cp)


def delta_p_linha(f_d: float, l_linha: float, d_linha: float, rho: float,
                  v: float) -> float:
    """Perda de carga distribuída na tubulação interestágios [Pa].

    Eq. 5.15 — Darcy-Weisbach: ΔP_linha = f_D·(L/D)·ρv²/2.
    """
    return f_d * (l_linha / d_linha) * rho * v**2 / 2.0


def potencia_isotermica(p1: float, v_dot1: float, pi: float) -> float:
    """Potência isotérmica ideal de referência [W].

    Usada nas Eqs. 5.12/5.13 (η_global). O livro não fecha a fórmula do
    isotérmico; adota-se a forma clássica W_iso = P1·V̇1·ln(π).
    """
    return p1 * v_dot1 * math.log(pi)


def q_int_carcaca(w_estagio: float, eta_mec: float) -> float:
    """Calor gerado internamente e conduzido à carcaça [W] — proxy de Q_int (Eq. 9.6).

    Simplificação de modelagem: o livro não fecha como calcular Q_int a partir
    de outras grandezas do capítulo. Adota-se a própria perda mecânica já
    embutida na Eq. 5.5 via η_mec — potência que não realiza trabalho de
    compressão e fica como calor dentro da máquina — como a parcela
    conduzida à carcaça: Q_int = W·(1 − η_mec).
    """
    return w_estagio * (1.0 - eta_mec)


def temperatura_carcaca_regime(q_int: float, cond_ext: float, cond_arref: float,
                               t_amb: float) -> float:
    """Temperatura de carcaça em regime permanente (dT_c/dt = 0) [K].

    Eq. 9.6 — M_c·c_c·dT_c/dt = Q_int − Q_ext − Q_arref. Q_ext e Q_arref são
    modelados pela lei de Newton do resfriamento, lineares em (T_c − T_amb):
    Q_ext = cond_ext·(T_c−T_amb) [convecção natural carcaça-ambiente],
    Q_arref = cond_arref·(T_c−T_amb) [arrefecimento ativo/ventilação forçada
    do invólucro]. Em regime permanente, Q_int = (cond_ext+cond_arref)·(T_c−T_amb).
    """
    cond_total = cond_ext + cond_arref
    if cond_total <= 0.0:
        return t_amb
    return t_amb + q_int / cond_total


def constante_tempo_carcaca(m_c: float, c_c: float, cond_ext: float,
                            cond_arref: float) -> float:
    """Constante de tempo térmica da carcaça [s].

    τ_c = M_c·c_c / (cond_ext + cond_arref) — decorre de linearizar a
    Eq. 9.6 (Q_ext/Q_arref lineares em T_c) como sistema de 1ª ordem.
    """
    cond_total = cond_ext + cond_arref
    return (m_c * c_c) / cond_total if cond_total > 0.0 else float("inf")


def temperatura_carcaca(t_c0: float, t_amb: float, q_int: float, cond_ext: float,
                        cond_arref: float, m_c: float, c_c: float, t: float) -> float:
    """Evolução temporal T_c(t) [K] — solução analítica da Eq. 9.6 linearizada.

    Com Q_ext/Q_arref lineares em (T_c−T_amb), a Eq. 9.6 vira um sistema de
    1ª ordem com solução fechada: T_c(t) = T_c,ss + (T_c0−T_c,ss)·exp(−t/τ_c),
    mesma forma já usada para a rampa do VSD em `dinamica.py`.
    """
    t_ss = temperatura_carcaca_regime(q_int, cond_ext, cond_arref, t_amb)
    tau_c = constante_tempo_carcaca(m_c, c_c, cond_ext, cond_arref)
    if not math.isfinite(tau_c):
        return t_amb
    return t_ss + (t_c0 - t_ss) * math.exp(-t / tau_c)


def temperatura_rotor_regime(t_gas_med: float, q_cond_eixo: float,
                             cond_rotor: float) -> float:
    """Temperatura do rotor em regime permanente (dT_r/dt = 0) [K].

    Eq. 9.19 — T_r = T_gas,med − Q̇_cond,eixo/(h_r·A_r). `cond_rotor` é o
    produto h_r·A_r (Eq. 9.18) já fechado, mesma convenção lumped de
    cond_ext/cond_arref para a carcaça — parâmetro de calibração da
    máquina, não valor de catálogo universal. Diferente de
    `temperatura_carcaca_regime` (que SOBE acima de T_amb pelo calor
    interno gerado), aqui T_r é limitada por CIMA por T_gas_med e cai
    conforme mais calor é conduzido para fora pelo eixo.
    """
    if cond_rotor <= 0.0:
        return t_gas_med
    return t_gas_med - q_cond_eixo / cond_rotor


def folga_residual_termica(delta_nom_um: float, alpha_r: float, l_r: float,
                           delta_t_r: float, alpha_c: float, l_c: float,
                           delta_t_c: float) -> float:
    """Folga residual por dilatação térmica diferencial [µm].

    Eq. 9.7 — δ_real = δ_nom − (α_r·L_r·ΔT_r − α_c·L_c·ΔT_c). ΔT_r e ΔT_c
    são os aumentos de temperatura do rotor e da carcaça acima da
    referência de folga nominal (T_amb, condição de máquina fria/parada
    em que δ_nom foi especificada). α em 1/K, L em m — o termo entre
    parênteses converte para µm (fator 1e6) para ficar na mesma unidade
    de δ_nom. δ_real ≤ 0 sinaliza risco de contato metálico (rubbing).
    """
    return delta_nom_um - (alpha_r * l_r * delta_t_r - alpha_c * l_c * delta_t_c) * 1.0e6


def spc(w_total: float, fad_m3_min: float) -> float:
    """Consumo específico de energia [kW·min/m³].

    Eq. 11.11 — SPC = (W_LP + W_HP) / V̇_free_air
    """
    return (w_total / 1000.0) / fad_m3_min


# ---------------------------------------------------------------------------
# Psicrometria (Cap. 10)
# ---------------------------------------------------------------------------

def p_sat(t_k: float) -> float:
    """Pressão de saturação do vapor d'água [Pa] — fórmula de Buck.

    Eq. 10.7 — P_sat(T) = 0,61121·exp[(18,678 − T/234,5)·T/(257,14+T)]  [kPa]
    Válida para 0–80 °C; T aqui entra em K e é convertida para °C.
    """
    t_c = t_k - 273.15
    return 0.61121e3 * math.exp((18.678 - t_c / 234.5) * (t_c / (257.14 + t_c)))


def razao_umidade(t_k: float, p: float, ur: float) -> float:
    """Razão de umidade [kg água / kg ar seco].

    Eq. 10.6 — W = 0,622 · φ·P_sat(T) / (P − φ·P_sat(T))
    """
    pv = ur * p_sat(t_k)
    pv = min(pv, 0.99 * p)  # evita singularidade na saturação a baixa P
    return 0.622 * pv / (p - pv)


def pressao_vapor(w: float, p: float) -> float:
    """Pressão parcial de vapor d'água [Pa] — inversa da Eq. 10.6.

    p_v = W·P / (0,622 + W)
    """
    return w * p / (0.622 + w)


def ur_de_w(w: float, t_k: float, p: float) -> float:
    """Umidade relativa a partir da razão de umidade (inversa da Eq. 10.6)."""
    return pressao_vapor(w, p) / p_sat(t_k)


def temp_orvalho_c(p_vapor: float) -> float:
    """Temperatura de ponto de orvalho sob pressão [°C] — inversa numérica
    da Eq. 10.7 (fórmula de Buck).

    Não há forma fechada simples para inverter a Eq. 10.7 com os três
    parâmetros do livro (ao contrário da forma "Magnus" de 2 parâmetros,
    mais comum); em vez de introduzir uma fórmula aproximada não citada no
    livro, a inversão é feita por bisseção sobre a própria `p_sat()` — que
    é monótona crescente em T, garantindo convergência.
    """
    if p_vapor <= 0.0:
        return -90.0  # ar sem vapor d'água — piso convencional, sem PDP físico definido
    lo_k, hi_k = 183.15, 363.15  # -90 °C a 90 °C, faixa ampla o suficiente
    for _ in range(60):
        mid_k = (lo_k + hi_k) / 2.0
        if p_sat(mid_k) < p_vapor:
            lo_k = mid_k
        else:
            hi_k = mid_k
    return (lo_k + hi_k) / 2.0 - 273.15


def temp_orvalho_de_w(w: float, p: float) -> float:
    """Temperatura de ponto de orvalho sob pressão [°C] a partir da razão
    de umidade W e da pressão local P — encadeia `pressao_vapor()` e
    `temp_orvalho_c()`. Usada para reportar o PDP em cada ponto de estado
    do trem (Eq. 10.6 + Eq. 10.7 combinadas)."""
    return temp_orvalho_c(pressao_vapor(w, p))


def condensado(m_dot_ar: float, w_in: float, w_out: float) -> float:
    """Vazão mássica de condensado [kg/s].

    Eq. 10.6 (intercooler) / Eq. 14.3 (aftercooler) — ṁ_cond = ṁ_ar·(W_in − W_out)
    """
    return m_dot_ar * max(w_in - w_out, 0.0)


def cp_umido(w: float) -> float:
    """cp do ar úmido [J/(kg·K)].

    Eq. 10.8 — cp_úmido ≈ 1005 + W·1860
    """
    return CP_AR + w * 1860.0


def densidade_ar(p: float, t_k: float) -> float:
    """Densidade do ar seco [kg/m³] — gás ideal (convenção do livro)."""
    return p / (R_AR * t_k)


__all__ = [
    "GAMMA",
    "R_AR",
    "delta_p_filtro",
    "razao_pressao_interna",
    "potencia_politropica",
    "perda_vi",
    "temperatura_descarga",
    "eficiencia_volumetrica",
    "q_int_carcaca",
    "temperatura_carcaca_regime",
    "constante_tempo_carcaca",
    "temperatura_carcaca",
    "temperatura_rotor_regime",
    "folga_residual_termica",
    "potencia_entreferro",
    "perdas_motor",
    "eficiencia_motor",
    "calor_gerado_hood",
    "temperatura_hood_regime",
    "delta_p_linha",
    "potencia_isotermica",
    "spc",
    "p_sat",
    "razao_umidade",
    "pressao_vapor",
    "ur_de_w",
    "temp_orvalho_c",
    "temp_orvalho_de_w",
    "condensado",
    "cp_umido",
    "densidade_ar",
]
