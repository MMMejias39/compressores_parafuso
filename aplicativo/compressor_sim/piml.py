"""Physics-Informed Machine Learning (PIML) — Cap. 23, Eqs. 23.1-23.4.

Rede neural (PyTorch) treinada para prever quatro grandezas do trem —
[T_LP,out, T_HP,in, ṁ_seco, Q̇_intercooler] — a partir do ponto de
operação [π, T_amb, δ/L, R_f, FAD]. A perda híbrida (Eq. 23.3) soma:

- **Erro de dados** ($L_{\\text{data}}$): MSE contra `sistema.simular()`
  em pontos rotulados.
- **Resíduo físico** ($L_{\\text{physics}}$): violação do balanço de
  energia do intercooler — a forma algébrica em regime permanente da
  Equação 10.1 deste documento, $\\dot Q = \\dot m_{\\text{seco}} \\cdot
  c_p \\cdot (T_{LP,out} - T_{HP,in})$ — avaliada em **pontos de
  colocação sem rótulo** (Eq. 23.1/23.2): coordenadas de entrada
  sorteadas, inclusive fora da faixa de treino, onde a rede nunca viu um
  valor medido mas ainda assim precisa respeitar a conservação de
  energia entre suas próprias quatro saídas.

Peso $\\lambda$ balanceado adaptativamente pela magnitude relativa dos
gradientes (Eq. 23.4), não fixado à mão.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import nn

from .constantes import CP_AR, R_AR
from . import sistema
from .torch_device import obter_device

NOMES_ENTRADA = ["pi_total", "t_amb_c", "folga_rel", "r_f_equiv", "fad_m3_min"]
NOMES_SAIDA = ["t_lp_out_c", "t_hp_in_c", "m_dot_seco", "q_intercooler_w"]


def _amostrar_entradas(n: int, faixas: dict, rng: np.random.Generator) -> np.ndarray:
    cols = []
    for nome in NOMES_ENTRADA:
        lo, hi = faixas[nome]
        cols.append(rng.uniform(lo, hi, size=n))
    return np.stack(cols, axis=1).astype(np.float32)


def _rotular(entradas: np.ndarray, params_base: dict) -> np.ndarray:
    """Roda `sistema.simular()` para cada linha de entrada e extrai os 4 alvos."""
    saidas = np.zeros((len(entradas), 4), dtype=np.float32)
    for i, (pi_total, t_amb_c, folga_rel, r_f_equiv, fad) in enumerate(entradas):
        p = {**params_base, "pi_total": float(pi_total),
             "t_amb": float(t_amb_c) + 273.15, "folga_rel": max(float(folga_rel), 0.0),
             "r_f_equiv": max(float(r_f_equiv), 0.0), "fad_m3_min": float(fad)}
        res = sistema.simular(p)
        saidas[i] = [res["nos"][1]["t_c"], res["nos"][2]["t_c"],
                    res["nos"][0]["m_dot"], res["potencias"]["q_intercooler"]]
    return saidas


def gerar_dataset(n_amostras: int, params_base: dict, faixas: dict,
                  seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Gera `n_amostras` pares (entrada, saída rotulada por `simular()`)."""
    rng = np.random.default_rng(seed)
    entradas = _amostrar_entradas(n_amostras, faixas, rng)
    saidas = _rotular(entradas, params_base)
    return entradas, saidas


class SubstitutoPIML(nn.Module):
    """MLP simples: 5 entradas -> 2 camadas ocultas -> 4 saídas."""

    def __init__(self, dim_oculta: int = 48):
        super().__init__()
        self.rede = nn.Sequential(
            nn.Linear(len(NOMES_ENTRADA), dim_oculta), nn.Tanh(),
            nn.Linear(dim_oculta, dim_oculta), nn.Tanh(),
            nn.Linear(dim_oculta, len(NOMES_SAIDA)),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.rede(x)


def _residuo_fisico(saida_pred: torch.Tensor) -> torch.Tensor:
    """F = Q̇_pred − ṁ_seco_pred·c_p·(T_LP,out_pred − T_HP,in_pred) — Eq. 23.2,
    forma algébrica em regime permanente da Eq. 10.1 (balanço de energia do
    intercooler), avaliada sobre as próprias saídas da rede.
    """
    t_lp_out, t_hp_in, m_dot_seco, q_pred = saida_pred.unbind(dim=1)
    q_balanco = m_dot_seco * CP_AR * (t_lp_out - t_hp_in)
    return q_pred - q_balanco


def treinar(entradas: np.ndarray, saidas: np.ndarray, faixas_colocacao: dict,
           n_epocas: int = 300, lr: float = 5e-3, n_colocacao: int = 256,
           kappa: float = 0.1, lambda_inicial: float = 0.1,
           seed: int = 0) -> dict:
    """Treina o substituto pela perda híbrida (Eq. 23.3), com $\\lambda$
    balanceado adaptativamente pela Eq. 23.4. Entradas/saídas são
    padronizadas antes do treino.

    O resíduo físico (Eq. 23.2) é medido em watts — ordens de grandeza
    acima do erro de dados já padronizado (adimensional, O(1)). Sem
    reescalar, o primeiro passo de otimização é dominado por um
    gradiente gigante do termo físico antes que o balanceamento
    adaptativo de $\\lambda$ tenha qualquer chance de agir, saturando a
    rede (unidades `tanh` presas em ±1) de forma irrecuperável — a razão
    pela qual `perda_fisica` é dividida pela própria escala
    (`desvio_y` de $\\dot Q$) antes de entrar na perda: não muda a
    física exigida ($\\mathcal{F}=0$ continua $\\mathcal{F}=0$), só evita
    o choque numérico do primeiro passo. `residuo_fisico_real()` segue
    reportando o resíduo em watts, sem essa normalização, para uso como
    métrica de aceitação.
    """
    torch.manual_seed(seed)
    device = obter_device()
    rng = np.random.default_rng(seed + 1)

    media_x, desvio_x = entradas.mean(axis=0), entradas.std(axis=0) + 1e-8
    media_y, desvio_y = saidas.mean(axis=0), saidas.std(axis=0) + 1e-8
    escala_residuo = float(desvio_y[NOMES_SAIDA.index("q_intercooler_w")])
    x_norm = torch.tensor((entradas - media_x) / desvio_x, dtype=torch.float32, device=device)
    y_norm = torch.tensor((saidas - media_y) / desvio_y, dtype=torch.float32, device=device)
    desvio_y_t = torch.tensor(desvio_y, dtype=torch.float32, device=device)
    media_y_t = torch.tensor(media_y, dtype=torch.float32, device=device)

    modelo = SubstitutoPIML().to(device)
    otimizador = torch.optim.Adam(modelo.parameters(), lr=lr)
    params_treinaveis = list(modelo.parameters())

    lam = lambda_inicial
    hist_data, hist_fisica, hist_lambda = (np.zeros(n_epocas) for _ in range(3))

    for epoca in range(n_epocas):
        otimizador.zero_grad()
        pred_dados = modelo(x_norm)
        perda_dados = torch.mean((pred_dados - y_norm) ** 2)  # L_data

        entradas_coloc = _amostrar_entradas(n_colocacao, faixas_colocacao, rng)
        x_coloc = torch.tensor((entradas_coloc - media_x) / desvio_x, dtype=torch.float32, device=device)
        pred_coloc_norm = modelo(x_coloc)
        # desfaz a padronização das SAÍDAS para avaliar o resíduo físico em
        # unidades reais (K, kg/s, W) — a padronização por si só violaria
        # a Eq. 10.1, que soma grandezas com unidades físicas concretas
        pred_coloc = pred_coloc_norm * desvio_y_t + media_y_t
        residuo = _residuo_fisico(pred_coloc) / escala_residuo
        perda_fisica = torch.mean(residuo ** 2)  # L_physics

        perda_total = perda_dados + lam * perda_fisica  # Eq. 23.3
        perda_total.backward()
        otimizador.step()

        # balanceamento adaptativo de lambda — Eq. 23.4
        if epoca % 5 == 0:
            otimizador.zero_grad()
            pred_dados2 = modelo(x_norm)
            perda_dados2 = torch.mean((pred_dados2 - y_norm) ** 2)
            grad_dados = torch.autograd.grad(perda_dados2, params_treinaveis,
                                             retain_graph=True, allow_unused=True)
            mag_dados = np.mean([g.abs().mean().item() for g in grad_dados if g is not None])

            entradas_coloc2 = _amostrar_entradas(n_colocacao, faixas_colocacao, rng)
            x_coloc2 = torch.tensor((entradas_coloc2 - media_x) / desvio_x, dtype=torch.float32, device=device)
            pred_coloc2 = modelo(x_coloc2) * desvio_y_t + media_y_t
            perda_fisica2 = torch.mean((_residuo_fisico(pred_coloc2) / escala_residuo) ** 2)
            grad_fisica = torch.autograd.grad(perda_fisica2, params_treinaveis,
                                              retain_graph=False, allow_unused=True)
            mag_fisica = np.mean([g.abs().mean().item() for g in grad_fisica if g is not None])

            razao = mag_dados / max(mag_fisica, 1e-12)
            lam = (1.0 - kappa) * lam + kappa * razao

        hist_data[epoca] = float(perda_dados.item())
        hist_fisica[epoca] = float(perda_fisica.item())
        hist_lambda[epoca] = lam

    modelo.eval()
    return {
        "modelo": modelo, "media_x": media_x, "desvio_x": desvio_x,
        "media_y": media_y, "desvio_y": desvio_y,
        "hist_data": hist_data, "hist_fisica": hist_fisica, "hist_lambda": hist_lambda,
        "device": device,
    }


def prever(modelo_info: dict, entradas: np.ndarray) -> np.ndarray:
    """Avalia o substituto treinado sobre novas entradas, em unidades reais."""
    modelo = modelo_info["modelo"]
    device = modelo_info.get("device", obter_device())
    x_norm = (entradas - modelo_info["media_x"]) / modelo_info["desvio_x"]
    x_tensor = torch.tensor(x_norm, dtype=torch.float32, device=device)
    modelo.eval()
    with torch.no_grad():
        y_norm = modelo(x_tensor).cpu().numpy()
    return y_norm * modelo_info["desvio_y"] + modelo_info["media_y"]


def residuo_fisico_real(modelo_info: dict, entradas: np.ndarray) -> np.ndarray:
    """Resíduo físico (Eq. 23.2) em unidades reais [W], para reportar como
    métrica de aceitação do modelo — o livro é explícito (Seção
    "Limitações e Cautelas" do Cap. 23) que essa penalização é fraca, e o
    resíduo deve ser medido, não presumido desprezível.
    """
    pred = prever(modelo_info, entradas)
    t_lp_out, t_hp_in, m_dot_seco, q_pred = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
    q_balanco = m_dot_seco * CP_AR * (t_lp_out - t_hp_in)
    return q_pred - q_balanco


def _residuo_inverso(pred_coloc: torch.Tensor, entradas_coloc: np.ndarray,
                     xi: torch.Tensor, params_base: dict,
                     device: torch.device | None = None) -> torch.Tensor:
    """F(ŷ; Ξ) = ṁ_seco_pred − ṁ_seco,eq93(Ξ) — Eq. 23.5 (Seção 23.8), forma
    do problema inverso sobre a Equação 9.3: em vez de K fixo em
    `params_base` (como em `_rotular`, que gerou os dados rotulados), ele é
    a incógnita Ξ, otimizada junto aos pesos da rede.

    `entradas_coloc` são os pontos de colocação em unidades reais (mesma
    convenção de `treinar()`), na ordem de `NOMES_ENTRADA`. A razão de
    umidade `w_amb` (Eq. 10.6) é recalculada ponto a ponto com a própria
    `nucleo.razao_umidade()` — fora do grafo do PyTorch, pois depende só de
    `t_amb`/`ur_amb`/`p_amb`, não de Ξ nem dos pesos da rede — porque
    `sistema.py` corrige `m_dot` por `(1+1,6078·w_amb)` para chegar em
    `m_dot_seco` (a mesma grandeza que a rede prevê); ignorar essa correção
    introduziria um viés sistemático de alguns % que o ajuste de Ξ tentaria
    compensar incorretamente, dominando o termo real de Ξ na Eq. 9.3 (cujo
    efeito, em folgas típicas, é da ordem de décimos de %).
    """
    device = device if device is not None else pred_coloc.device
    pi_total = torch.tensor(entradas_coloc[:, NOMES_ENTRADA.index("pi_total")], dtype=torch.float32, device=device)
    t_amb_c = entradas_coloc[:, NOMES_ENTRADA.index("t_amb_c")]
    t_amb_k = torch.tensor(t_amb_c, dtype=torch.float32, device=device) + 273.15
    folga_rel = torch.tensor(entradas_coloc[:, NOMES_ENTRADA.index("folga_rel")], dtype=torch.float32, device=device)
    fad = torch.tensor(entradas_coloc[:, NOMES_ENTRADA.index("fad_m3_min")], dtype=torch.float32, device=device)

    w_amb = np.array([sistema.nucleo.razao_umidade(t_c + 273.15, params_base["p_amb"], params_base["ur_amb"])
                      for t_c in t_amb_c])
    w_amb_t = torch.tensor(w_amb, dtype=torch.float32, device=device)

    rho_amb = params_base["p_amb"] / (R_AR * t_amb_k)
    v_dot_fad = fad / 60.0
    # nucleo.eficiencia_volumetrica(k, folga_rel, pi) é chamada em sistema.py
    # com pi=sqrt(pi_total) (razão do estágio, Eq. 5.7) e aplica sqrt(pi) de
    # novo internamente (Eq. 9.3, √(P2/P1)) — equivalente a pi_total**0.25.
    eta_v = 1.0 - xi * folga_rel * pi_total**0.25
    m_dot_seco_eq93 = (rho_amb * v_dot_fad * eta_v) / (1.0 + 1.6078 * w_amb_t)

    m_dot_pred = pred_coloc[:, NOMES_SAIDA.index("m_dot_seco")]
    return m_dot_pred - m_dot_seco_eq93


def treinar_com_identificacao(entradas: np.ndarray, saidas: np.ndarray, faixas_colocacao: dict,
                              params_base: dict, xi_inicial: float,
                              n_epocas: int = 300, lr: float = 5e-3, n_colocacao: int = 256,
                              kappa: float = 0.1, lambda_inicial: float = 0.1,
                              seed: int = 0) -> dict:
    """Identificação de parâmetro por problema inverso (Eq. 23.5, Seção 23.8):
    treina o substituto PIML e, simultaneamente, otimiza Ξ — o coeficiente de
    vazamento K da Equação 9.3 — como incógnita, a partir do resíduo de
    `_residuo_inverso`. Mesma perda híbrida e mesmo balanceamento adaptativo
    de λ (Eq. 23.4) de `treinar()`, mas o resíduo físico é o da Eq. 9.3
    (mássico) em vez do balanço de energia do intercooler (Eq. 23.2) — o
    ponto da Seção 23.8 é que o mecanismo é genérico, não específico de um
    único resíduo.

    `xi_inicial` é a crença de partida para Ξ — deliberadamente diferente do
    K real usado para rotular os dados (`params_base["k_folga"]` dentro de
    `gerar_dataset`), para que a convergência mostrada seja identificação de
    verdade, mesmo espírito do EKF em `simular_ekf`/`simular_ekf_aumentado`.
    """
    torch.manual_seed(seed)
    device = obter_device()
    rng = np.random.default_rng(seed + 1)

    media_x, desvio_x = entradas.mean(axis=0), entradas.std(axis=0) + 1e-8
    media_y, desvio_y = saidas.mean(axis=0), saidas.std(axis=0) + 1e-8
    escala_residuo = float(desvio_y[NOMES_SAIDA.index("m_dot_seco")])
    x_norm = torch.tensor((entradas - media_x) / desvio_x, dtype=torch.float32, device=device)
    y_norm = torch.tensor((saidas - media_y) / desvio_y, dtype=torch.float32, device=device)
    desvio_y_t = torch.tensor(desvio_y, dtype=torch.float32, device=device)
    media_y_t = torch.tensor(media_y, dtype=torch.float32, device=device)

    modelo = SubstitutoPIML().to(device)
    xi = torch.nn.Parameter(torch.tensor(float(xi_inicial), dtype=torch.float32, device=device))
    otimizador = torch.optim.Adam(list(modelo.parameters()) + [xi], lr=lr)
    params_treinaveis = list(modelo.parameters())  # balanceamento de λ só sobre pesos da rede

    lam = lambda_inicial
    hist_data, hist_fisica, hist_lambda, hist_xi = (np.zeros(n_epocas) for _ in range(4))

    for epoca in range(n_epocas):
        otimizador.zero_grad()
        pred_dados = modelo(x_norm)
        perda_dados = torch.mean((pred_dados - y_norm) ** 2)  # L_data

        entradas_coloc = _amostrar_entradas(n_colocacao, faixas_colocacao, rng)
        x_coloc = torch.tensor((entradas_coloc - media_x) / desvio_x, dtype=torch.float32, device=device)
        pred_coloc_norm = modelo(x_coloc)
        pred_coloc = pred_coloc_norm * desvio_y_t + media_y_t
        residuo = _residuo_inverso(pred_coloc, entradas_coloc, xi, params_base, device) / escala_residuo
        perda_fisica = torch.mean(residuo ** 2)  # L_physics(θ, Ξ) — Eq. 23.5

        perda_total = perda_dados + lam * perda_fisica
        perda_total.backward()
        otimizador.step()

        if epoca % 5 == 0:
            otimizador.zero_grad()
            pred_dados2 = modelo(x_norm)
            perda_dados2 = torch.mean((pred_dados2 - y_norm) ** 2)
            grad_dados = torch.autograd.grad(perda_dados2, params_treinaveis,
                                             retain_graph=True, allow_unused=True)
            mag_dados = np.mean([g.abs().mean().item() for g in grad_dados if g is not None])

            entradas_coloc2 = _amostrar_entradas(n_colocacao, faixas_colocacao, rng)
            x_coloc2 = torch.tensor((entradas_coloc2 - media_x) / desvio_x, dtype=torch.float32, device=device)
            pred_coloc2 = modelo(x_coloc2) * desvio_y_t + media_y_t
            residuo2 = _residuo_inverso(pred_coloc2, entradas_coloc2, xi, params_base, device) / escala_residuo
            perda_fisica2 = torch.mean(residuo2 ** 2)
            grad_fisica = torch.autograd.grad(perda_fisica2, params_treinaveis,
                                              retain_graph=False, allow_unused=True)
            mag_fisica = np.mean([g.abs().mean().item() for g in grad_fisica if g is not None])

            razao = mag_dados / max(mag_fisica, 1e-12)
            lam = (1.0 - kappa) * lam + kappa * razao

        hist_data[epoca] = float(perda_dados.item())
        hist_fisica[epoca] = float(perda_fisica.item())
        hist_lambda[epoca] = lam
        hist_xi[epoca] = float(xi.item())

    modelo.eval()
    return {
        "modelo": modelo, "media_x": media_x, "desvio_x": desvio_x,
        "media_y": media_y, "desvio_y": desvio_y,
        "hist_data": hist_data, "hist_fisica": hist_fisica, "hist_lambda": hist_lambda,
        "hist_xi": hist_xi, "xi_estimado": float(xi.item()), "device": device,
    }


__all__ = [
    "NOMES_ENTRADA", "NOMES_SAIDA", "gerar_dataset", "SubstitutoPIML",
    "treinar", "prever", "residuo_fisico_real",
    "treinar_com_identificacao",
]
