"""Autoencoder Variacional (VAE) — Cap. 22, Eqs. 22.1-22.7; erro de
reconstrução também citado como Eq. 20.4.

Aprende a "assinatura" estatística da operação saudável do compressor a
partir de amostras sintéticas geradas pelo próprio simulador (não existe
dado real de planta neste projeto) e usa o erro de reconstrução como
sensor virtual de anomalia (Eq. 22.5/20.4), com o limiar de disparo
calibrado estatisticamente sobre um conjunto de validação saudável
(Eq. 22.6) — não um valor arbitrário.

Vetor de entrada (16 grandezas, não as 28 do livro — este simulador não
tem 28 saídas independentes; ver `extrair_features()` para a lista
exata): pressão e temperatura nos 6 pontos de estado da cascata, mais
cinco KPIs (η_v, η_global, SPC, efetividade do intercooler, ΔP/Δt do
vaso).
"""

from __future__ import annotations

import numpy as np
import torch
from torch import nn

from . import sistema
from .torch_device import obter_device

NOMES_FEATURES = [
    "t_admissao", "m_dot_seco", "t_desc_lp", "t_ent_hp", "t_desc_hp",
    "p_rede", "eta_v_lp", "eta_global", "spc", "efetividade_intercooler",
    "condensado_total_kg_h", "t_carcaca_c",
]


def extrair_features(res: dict) -> np.ndarray:
    """Vetor de 12 grandezas a partir do resultado de `sistema.simular()`.

    Deliberadamente **não** inclui todas as pressões/temperaturas da
    cascata: neste modelo, a maioria delas depende só do ponto de operação
    fixo (pressão de rede, temperaturas de referência) e não se move nem
    um pouco com δ/L ou R_f (mesmo achado já registrado para a aba
    "Dinâmica temporal" — ver CONTEXTO_app.md). As duas grandezas que
    realmente carregam sinal de degradação são `m_dot_seco` (via η_v,
    Eq. 9.3) e, mais fracamente, `efetividade_intercooler`/`t_ent_hp`
    (via fouling, Eq. 10.5) — incluídas explicitamente aqui em vez de
    diluídas entre uma dúzia de pressões constantes.
    """
    nos = res["nos"]
    k = res["kpis"]
    vals = [
        nos[1]["t_c"], nos[1]["m_dot"], nos[2]["t_c"], nos[3]["t_c"],
        nos[4]["t_c"], nos[6]["p_bar"], k["eta_v_lp"], k["eta_global"],
        k["spc"], k["efetividade_intercooler"], k["condensado_total_kg_h"],
        k["t_carcaca_c"],
    ]
    return np.array(vals, dtype=np.float32)


def gerar_dataset_saudavel(n_amostras: int, params_base: dict,
                           faixa_folga: tuple[float, float] = (0.0018, 0.0022),
                           faixa_r_f: tuple[float, float] = (0.0, 1e-5),
                           sigma_ruido_rel: float = 0.0003,
                           seed: int = 0) -> np.ndarray:
    """Amostras sintéticas de operação saudável — pequenas variações em
    torno do ponto de operação de referência, dentro de faixas de
    degradação "como novo" (δ/L e R_f — comissionamento, tolerância
    apertada), mais ruído de medição simulado após a extração das
    features. Não é dado de planta real. `sigma_ruido_rel` é
    deliberadamente baixo (~0,03 % da leitura, sensores de boa
    qualidade) porque o sinal físico de degradação em `m_dot_seco` já é
    da ordem de poucos décimos percentuais — ruído maior o encobriria
    por construção, não por realismo de sensor.
    """
    rng = np.random.default_rng(seed)
    linhas = []
    for _ in range(n_amostras):
        p = dict(params_base)
        p["t_amb"] = params_base["t_amb"] + rng.normal(0.0, 1.5)
        p["ur_amb"] = float(np.clip(params_base["ur_amb"] + rng.normal(0.0, 0.03), 0.1, 1.0))
        p["pi_total"] = params_base["pi_total"] + rng.normal(0.0, 0.15)
        p["fad_m3_min"] = params_base["fad_m3_min"] + rng.normal(0.0, 0.2)
        p["folga_rel"] = float(rng.uniform(*faixa_folga))
        p["r_f_equiv"] = float(rng.uniform(*faixa_r_f))
        res = sistema.simular(p)
        feat = extrair_features(res)
        feat += rng.normal(0.0, sigma_ruido_rel * np.abs(feat) + 1e-6).astype(np.float32)
        linhas.append(feat)
    return np.stack(linhas)


class VAE(nn.Module):
    """Encoder-decoder com gargalo probabilístico — Eq. 22.1 (reparametrização)."""

    def __init__(self, dim_entrada: int, dim_latente: int = 3, dim_oculta: int = 32):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(dim_entrada, dim_oculta), nn.Tanh(),
            nn.Linear(dim_oculta, dim_oculta), nn.Tanh(),
        )
        self.mu = nn.Linear(dim_oculta, dim_latente)
        self.logvar = nn.Linear(dim_oculta, dim_latente)
        self.decoder = nn.Sequential(
            nn.Linear(dim_latente, dim_oculta), nn.Tanh(),
            nn.Linear(dim_oculta, dim_oculta), nn.Tanh(),
            nn.Linear(dim_oculta, dim_entrada),
        )

    def forward(self, x: torch.Tensor):
        h = self.encoder(x)
        mu, logvar = self.mu(h), self.logvar(h)
        eps = torch.randn_like(mu)
        ell = mu + torch.exp(0.5 * logvar) * eps  # Eq. 22.1 (ℓ = μ + σ·ε)
        x_hat = self.decoder(ell)
        return x_hat, mu, logvar


def treinar(dataset: np.ndarray, dim_latente: int = 3, dim_oculta: int = 32,
           beta: float = 0.05, n_epocas: int = 400, lr: float = 5e-3,
           seed: int = 0) -> dict:
    """Treina o VAE pela perda do ELBO invertido (Eq. 22.2/22.3): erro de
    reconstrução + β·divergência KL. Padroniza o dataset (média/desvio) e
    devolve o modelo treinado junto com os parâmetros de padronização.
    """
    torch.manual_seed(seed)
    device = obter_device()
    media = dataset.mean(axis=0)
    desvio = dataset.std(axis=0) + 1e-8
    x_norm = (dataset - media) / desvio
    x_tensor = torch.tensor(x_norm, dtype=torch.float32, device=device)

    modelo = VAE(dim_entrada=dataset.shape[1], dim_latente=dim_latente,
                dim_oculta=dim_oculta).to(device)
    otimizador = torch.optim.Adam(modelo.parameters(), lr=lr)

    historico_loss = np.zeros(n_epocas)
    for epoca in range(n_epocas):
        otimizador.zero_grad()
        x_hat, mu, logvar = modelo(x_tensor)
        perda_reconstrucao = torch.mean((x_tensor - x_hat) ** 2)
        perda_kl = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
        perda = perda_reconstrucao + beta * perda_kl  # Eq. 22.3
        perda.backward()
        otimizador.step()
        historico_loss[epoca] = float(perda.item())

    modelo.eval()
    return {
        "modelo": modelo, "media": media, "desvio": desvio,
        "historico_loss": historico_loss, "device": device,
    }


def erro_reconstrucao(modelo_info: dict, amostras: np.ndarray) -> np.ndarray:
    """E_rec por amostra (Eq. 20.4/22.5) — soma do erro quadrático
    normalizado pela variância de cada variável, no espaço padronizado.
    """
    modelo = modelo_info["modelo"]
    media, desvio = modelo_info["media"], modelo_info["desvio"]
    device = modelo_info.get("device", obter_device())
    x_norm = (amostras - media) / desvio
    x_tensor = torch.tensor(x_norm, dtype=torch.float32, device=device)
    modelo.eval()
    with torch.no_grad():
        x_hat, _, _ = modelo(x_tensor)
        erro2 = (x_tensor - x_hat) ** 2  # já normalizado por desvio-padrão (Eq. 20.4)
        e_rec = erro2.sum(dim=1)
    return e_rec.cpu().numpy()


def calibrar_limiar(modelo_info: dict, dataset_validacao: np.ndarray,
                    n_desvios: float = 3.0) -> float:
    """Limiar de disparo (Eq. 22.6) calibrado estatisticamente: média + n
    desvios-padrão do erro de reconstrução sobre um conjunto de validação
    saudável — não um valor arbitrário.
    """
    e_rec_val = erro_reconstrucao(modelo_info, dataset_validacao)
    return float(e_rec_val.mean() + n_desvios * e_rec_val.std())


__all__ = [
    "NOMES_FEATURES", "extrair_features", "gerar_dataset_saudavel", "VAE",
    "treinar", "erro_reconstrucao", "calibrar_limiar",
]
