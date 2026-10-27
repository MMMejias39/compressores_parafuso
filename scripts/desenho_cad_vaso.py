"""Desenho de engenharia do vaso pulmão V-02 a partir de sólido B-rep.

Gera:
    figuras/fig_16_2_vaso_v02_cad.{pdf,png}
    figuras/vaso_v02.step

O modelo é construído com build123d (kernel OpenCascade) a partir das
dimensões do projeto (V ≈ 2,0 m³, PMTA 10 bar) e o desenho é gerado por
projeção ortográfica com remoção de linhas ocultas — não é ilustração.

Uso:
    python scripts/desenho_cad_vaso.py
"""

from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch

from build123d import (
    Align, Axis, Box, BuildPart, Cylinder, Location, Locations, Mode,
    Pos, Rot, export_step,
)

NAVY = "#1f3b57"
BLUE = "#2b6cb0"
GRAY = "#5b6770"
LGRAY = "#9aa5ad"

OUTDIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figuras")
)

# ---------------------------------------------------------------- geometria
D_CASCO = 1200.0     # diâmetro interno do casco [mm]
L_CASCO = 1800.0     # comprimento do trecho cilíndrico [mm]
T = 16.0             # espessura de parede [mm]
NOZUL = {"entrada": (80.0, 480.0), "saida": (100.0, 0.0), "dreno": (50.0, 0.0)}


def construir() -> object:
    """Vaso horizontal com tampos elípticos 2:1, selas e bocais."""
    r_int = D_CASCO / 2
    r_ext = r_int + T
    comp = L_CASCO + 2 * 0.5 * r_int  # comprimento total com tampos 2:1

    with BuildPart() as v:
        # casco cilíndrico (eixo X)
        Cylinder(radius=r_ext, height=L_CASCO,
                 rotation=(0, 90, 0), align=(Align.CENTER, Align.CENTER, Align.CENTER))
        # tampos elípticos 2:1 (semiesferas achatadas)
        for s in (-1, 1):
            with Locations((s * L_CASCO / 2, 0, 0)):
                from build123d import Sphere
                sp = Sphere(radius=r_ext)
                # achata em X pela metade -> elipsoide 2:1 aproximado
                sp = sp.scale((0.5, 1.0, 1.0))
                v.part = v.part.fuse(sp) if v.part else sp
        # bocais
        with BuildPart() as bocais:
            with Locations((0, 0, r_ext - 5)):
                Cylinder(radius=NOZUL["entrada"][0] / 2, height=120,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations((-300, 0, -r_ext + 5)):
                Cylinder(radius=NOZUL["dreno"][0] / 2, height=120,
                         align=(Align.CENTER, Align.CENTER, Align.MAX))
            with Locations((350, 0, r_ext - 5)):
                Cylinder(radius=NOZUL["saida"][0] / 2, height=140,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
        v.part = v.part.fuse(bocais.part)
        # selas de apoio
        for s in (-1, 1):
            sela = Pos(s * (L_CASCO / 2 - 250), 0, -r_ext - 40) * Box(300, 900, 320)
            v.part = v.part.fuse(sela)
    return v.part, comp


def arestas_2d(parte, origem, up):
    """Projeta o sólido e devolve arestas visíveis/ocultas em 2D."""
    try:
        vis, hid = parte.project_to_viewport(origem, viewport_up=up)
    except Exception:
        vis, hid = [], []
    def para_2d(arestas):
        saida = []
        for e in arestas:
            try:
                pts = [e.position_at(t) for t in np.linspace(0, 1, 24)]
                saida.append(np.array([[p.X, p.Y] for p in pts]))
            except Exception:
                continue
        return saida
    return para_2d(vis), para_2d(hid)


def desenhar():
    parte, comp = construir()
    os.makedirs(OUTDIR, exist_ok=True)
    step = os.path.join(OUTDIR, "vaso_v02.step")
    export_step(parte, step)
    print("salvo:", step)

    modelo = parte.bounding_box()
    print("bounding box:", modelo)

    v_front = arestas_2d(parte, (0, -4000, 0), (0, 0, 1))
    v_topo = arestas_2d(parte, (0, 0, 4000), (0, 1, 0))

    fig = plt.figure(figsize=(13.5, 9.4))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_aspect("equal")
    ax.axis("off")

    x0, x1 = modelo.min.X, modelo.max.X
    z0, z1 = modelo.min.Z, modelo.max.Z
    y0, y1 = modelo.min.Y, modelo.max.Y
    altura_topo = y1 - y0

    # 1o diedro: planta abaixo da elevacao, alinhada em X
    dy_topo = z0 - 480 - altura_topo

    def plotar(arestas, dy=0, estilo="-", cor=NAVY, lw=1.1):
        for a in arestas:
            ax.plot(a[:, 0], a[:, 1] + dy, linestyle=estilo, color=cor, lw=lw,
                    solid_capstyle="round")

    plotar(v_front[0], 0, "-", NAVY, 1.5)
    plotar(v_front[1], 0, (0, (6, 3)), LGRAY, 0.8)
    plotar(v_topo[0], dy_topo, "-", NAVY, 1.5)
    plotar(v_topo[1], dy_topo, (0, (6, 3)), LGRAY, 0.8)

    # ---- cotas
    def cota_h(xa, xb, y, texto):
        ax.add_patch(FancyArrowPatch((xa, y), (xb, y), arrowstyle="<|-|>",
                                     mutation_scale=10, color=BLUE, lw=0.9))
        for xx in (xa, xb):
            ax.plot([xx, xx], [y - 60, y + 60], color=BLUE, lw=0.7)
        ax.text((xa + xb) / 2, y + 45, texto, ha="center", va="bottom",
                fontsize=9, color=BLUE, fontweight="bold")

    def cota_v(za, zb, x, texto):
        ax.add_patch(FancyArrowPatch((x, za), (x, zb), arrowstyle="<|-|>",
                                     mutation_scale=10, color=BLUE, lw=0.9))
        for zz in (za, zb):
            ax.plot([x - 60, x + 60], [zz, zz], color=BLUE, lw=0.7)
        ax.text(x - 70, (za + zb) / 2, texto, ha="right", va="center",
                fontsize=9, color=BLUE, rotation=90, fontweight="bold")

    cota_h(x0, x1, z1 + 320, f"{comp:.0f} (comprimento total)")
    cota_v(y0, y1, x0 - 420, f"Ø{D_CASCO + 2 * T:.0f}")

    x_sela = L_CASCO / 2 - 250
    cota_h(-x_sela, x_sela, z0 - 260, f"{2 * x_sela:.0f} (entre selas)")

    # ---- titulos e rotulos
    ax.text(0, z1 + 1250,
            "Vaso pulmão V-02 — desenho gerado a partir de sólido B-rep",
            fontsize=14, color=NAVY, fontweight="bold", ha="center")
    ax.text(0, z1 + 950,
            "Cotas em mm · projeção ortográfica 1º diedro com remoção de linhas ocultas "
            "(OpenCascade via build123d)",
            fontsize=8.4, color=GRAY, ha="center")

    ax.text(x1 + 300, (z0 + z1) / 2, "VISTA FRONTAL\n(elevação)", fontsize=8.2,
            color=GRAY, ha="left", va="center")
    ax.text(x1 + 300, dy_topo + (y0 + y1) / 2, "VISTA SUPERIOR\n(planta)", fontsize=8.2,
            color=GRAY, ha="left", va="center")

    # ---- bloco de titulo (ABNT simplificado)
    yb = dy_topo + y0 - 760
    ax.add_patch(plt.Rectangle((x0, yb), 3300, 560, fill=False, edgecolor=NAVY, lw=1.1))
    ax.plot([x0 + 2150, x0 + 2150], [yb, yb + 560], color=NAVY, lw=1.1)
    ax.plot([x0, x0 + 3300], [yb + 330, yb + 330], color=NAVY, lw=0.7)
    ax.text(x0 + 70, yb + 440, "VASO PULMÃO V-02", fontsize=10, color=NAVY,
            fontweight="bold", va="center")
    ax.text(x0 + 70, yb + 240, "Gêmeo Digital · Compressores Parafuso Offshore", fontsize=7.4,
            color=GRAY, va="center")
    ax.text(x0 + 70, yb + 110, f"Ø{D_CASCO} × {comp:.0f} · e = {T:.0f} mm · PMTA 10 bar · ASME VIII Div. 1",
            fontsize=6.9, color=GRAY, va="center")
    ax.text(x0 + 2220, yb + 440, "ESC. 1:20", fontsize=9.5, color=NAVY, va="center",
            fontweight="bold")
    ax.text(x0 + 2220, yb + 240, "FIG. 16.2", fontsize=9.5, color=NAVY, va="center")
    ax.text(x0 + 2220, yb + 110, "ABNT NBR 10067", fontsize=7.4, color=GRAY, va="center")

    ax.set_xlim(x0 - 900, x1 + 1900)
    ax.set_ylim(yb - 320, z1 + 1450)
    for ext in ("pdf", "png"):
        caminho = os.path.join(OUTDIR, f"fig_16_2_vaso_v02_cad.{ext}")
        fig.savefig(caminho, dpi=400 if ext == "png" else 200,
                    bbox_inches="tight", facecolor="white")
        print("salvo:", caminho)
    svg = os.path.join(OUTDIR, "fig_16_2_vaso_v02_cad.svg")
    fig.savefig(svg, bbox_inches="tight", facecolor="white")
    print("salvo:", svg)

    plt.close(fig)


if __name__ == "__main__":
    desenhar()
