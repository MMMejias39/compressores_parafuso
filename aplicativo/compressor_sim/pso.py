"""Otimização por Enxame de Partículas (PSO) — Cap. 24, Eqs. 24.3/24.4.

Implementação padrão, com peso de inércia decaindo linearmente ao longo
das iterações — mesma prática recomendada no livro (Seção "Sintonia dos
coeficientes e critério de parada" do Cap. 24): iniciar alto (~0,9),
favorecendo varredura ampla, e decair até um valor baixo (~0,4),
concentrando o enxame em torno da melhor região encontrada.
"""

from __future__ import annotations

import numpy as np


def otimizar(func_custo, limite_inf, limite_sup, n_particulas: int = 30,
            n_iter: int = 60, w_ini: float = 0.9, w_fim: float = 0.4,
            c1: float = 2.0, c2: float = 2.0, seed: int = 42) -> dict:
    """Minimiza `func_custo(x)` dentro de [limite_inf, limite_sup].

    Eq. 24.3 atualiza a velocidade de cada partícula (termo de inércia +
    puxão cognitivo p_best + puxão social g_best); Eq. 24.4 aplica o
    deslocamento. Devolve a melhor posição/custo encontrados e o histórico
    de g_best por iteração, para o gráfico de convergência.
    """
    rng = np.random.default_rng(seed)
    limite_inf = np.atleast_1d(np.asarray(limite_inf, dtype=float))
    limite_sup = np.atleast_1d(np.asarray(limite_sup, dtype=float))
    n_dim = len(limite_inf)

    x = rng.uniform(limite_inf, limite_sup, size=(n_particulas, n_dim))
    v = np.zeros_like(x)
    custo = np.array([func_custo(xi) for xi in x])

    p_best = x.copy()
    p_best_custo = custo.copy()
    g_best_idx = int(np.argmin(p_best_custo))
    g_best = p_best[g_best_idx].copy()
    g_best_custo = float(p_best_custo[g_best_idx])

    historico = np.zeros(n_iter)
    for t in range(n_iter):
        w = w_ini + (w_fim - w_ini) * t / max(n_iter - 1, 1)
        r1 = rng.uniform(size=(n_particulas, n_dim))
        r2 = rng.uniform(size=(n_particulas, n_dim))
        v = w * v + c1 * r1 * (p_best - x) + c2 * r2 * (g_best - x)  # Eq. 24.3
        x = np.clip(x + v, limite_inf, limite_sup)                  # Eq. 24.4

        custo = np.array([func_custo(xi) for xi in x])
        melhorou = custo < p_best_custo
        p_best[melhorou] = x[melhorou]
        p_best_custo[melhorou] = custo[melhorou]

        idx = int(np.argmin(p_best_custo))
        if p_best_custo[idx] < g_best_custo:
            g_best_custo = float(p_best_custo[idx])
            g_best = p_best[idx].copy()

        historico[t] = g_best_custo

    return {
        "g_best": g_best,
        "g_best_custo": g_best_custo,
        "historico_custo": historico,
    }


__all__ = ["otimizar"]
