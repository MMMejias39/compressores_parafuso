"""Ilustracao conceitual da capa do Volume I.

Gera figuras/fig_capa_vol1.pdf, a imagem que ocupa o espaco reservado na capa
de teorias.tex (mesmo lugar e mesma largura que o render do rotor ocupa na capa
do Volume II).

O motivo escolhido e a tese do proprio volume, enunciada na Eq. (1.1): um unico
balanco sobre uma fronteira, especializado em cinco grandezas. A caixa
isometrica e o volume de controle; as setas atravessam a fronteira; o circulo
interno e a geracao. Os cinco nomes abaixo sao as especializacoes que os
capitulos desenvolvem.

Rodar com o venv de scripts:
    scripts/venv/bin/python scripts/gen_capa_vol1.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Polygon, Circle

OUTDIR = "/home/mejias/Documentos/Compressores/figuras"
os.makedirs(OUTDIR, exist_ok=True)

# Mesmo estilo global de scripts/gen_figuras.py
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})

NAVY = "#1f3b57"
BLUE = "#2b6cb0"
GRAY = "#666666"
LGRAY = "#999999"

# Tons das tres faces visiveis do volume de controle (topo mais claro)
FACE_TOP = "#e8eef5"
FACE_FRONT = "#d3e0ec"
FACE_SIDE = "#bcd0e2"


def iso(x, y, z):
    """Projecao isometrica de um ponto (x, y, z) no plano da figura."""
    ax_ = (x - y) * np.cos(np.pi / 6)
    ay_ = (x + y) * np.sin(np.pi / 6) + z
    return ax_, ay_


def face(ax, pts, color, z):
    ax.add_patch(Polygon([iso(*p) for p in pts], closed=True,
                         facecolor=color, edgecolor=NAVY,
                         linewidth=1.4, zorder=z))


def seta(ax, p0, p1, color, lw=2.0, z=6):
    ax.add_patch(FancyArrowPatch(iso(*p0), iso(*p1),
                                 arrowstyle="-|>", mutation_scale=16,
                                 linewidth=lw, color=color,
                                 shrinkA=0, shrinkB=0, zorder=z))


def gen_capa():
    fig, ax = plt.subplots(figsize=(6.0, 6.6))
    ax.set_aspect("equal")
    ax.axis("off")

    L = 2.0  # aresta do volume de controle

    # --- Volume de controle: tres faces visiveis, do fundo para a frente ---
    face(ax, [(0, 0, L), (L, 0, L), (L, L, L), (0, L, L)], FACE_TOP, 3)   # topo
    face(ax, [(L, 0, 0), (L, L, 0), (L, L, L), (L, 0, L)], FACE_SIDE, 4)  # lateral
    face(ax, [(0, 0, 0), (L, 0, 0), (L, 0, L), (0, 0, L)], FACE_FRONT, 5) # frente

    # Arestas ocultas, tracejadas: a fronteira e imaginaria, nao uma parede
    for p0, p1 in [((0, L, 0), (L, L, 0)),
                   ((0, L, 0), (0, 0, 0)),
                   ((0, L, 0), (0, L, L))]:
        (x0, y0), (x1, y1) = iso(*p0), iso(*p1)
        ax.plot([x0, x1], [y0, y1], linestyle=(0, (3, 3)),
                color=LGRAY, linewidth=1.0, zorder=2)

    # --- Geracao interna ---
    cx, cy = iso(L / 2, L / 2, L / 2)
    ax.add_patch(Circle((cx, cy), 0.30, facecolor="white",
                        edgecolor=BLUE, linewidth=1.6, zorder=7))
    ax.text(cx, cy, r"$\dot{\mathcal{B}}_{ger}$", ha="center", va="center",
            fontsize=11, color=BLUE, zorder=8)

    # --- Fluxos que atravessam a fronteira ---
    # Entrada: tres setas na face frontal
    for j, y in enumerate((0.55, 1.00, 1.45)):
        seta(ax, (-1.55, 0.0, y), (-0.06, 0.0, y), NAVY,
             lw=2.2 if j == 1 else 1.6)
    # Saida: tres setas na face lateral
    for j, y in enumerate((0.55, 1.00, 1.45)):
        seta(ax, (L, L + 0.06, y), (L, L + 1.55, y), NAVY,
             lw=2.2 if j == 1 else 1.6)

    xe, ye = iso(-1.62, 0.0, 1.00)
    ax.text(xe, ye + 0.42, r"$\dot{\mathcal{B}}_{ent}$", ha="center",
            va="bottom", fontsize=12, color=NAVY)
    xs, ys = iso(L, L + 1.62, 1.00)
    ax.text(xs, ys + 0.42, r"$\dot{\mathcal{B}}_{sai}$", ha="center",
            va="bottom", fontsize=12, color=NAVY)

    # Acumulo, sobre a face do topo
    xt, yt = iso(L / 2, L / 2, L)
    ax.text(xt, yt + 0.34, r"$\dfrac{d\mathcal{B}}{dt}$", ha="center",
            va="bottom", fontsize=13, color=NAVY)

    # --- As cinco especializacoes ---
    base = -2.55
    ax.plot([-3.05, 3.05], [base + 0.62, base + 0.62],
            color=NAVY, linewidth=0.8)
    nomes = ["MASSA", "QUANTIDADE DE MOVIMENTO", "ENERGIA", "ENTROPIA", "CARGA"]
    ax.text(0, base + 0.18, "   ·   ".join(nomes), ha="center", va="center",
            fontsize=7.4, color=GRAY)
    ax.plot([-3.05, 3.05], [base - 0.20, base - 0.20],
            color=NAVY, linewidth=0.8)

    ax.set_xlim(-3.3, 3.3)
    ax.set_ylim(base - 0.6, 4.5)

    path = os.path.join(OUTDIR, "fig_capa_vol1.pdf")
    fig.savefig(path, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("saved", path)


if __name__ == "__main__":
    gen_capa()
