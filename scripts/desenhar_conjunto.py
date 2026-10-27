"""Desenho do conjunto compressor de parafuso + motor, com os pontos de medição.

Gera figuras/fig_18_2_conjunto_pontos.{pdf,png}

O desenho é uma elevação esquemática do pacote (skid) na ordem física do
processo, com o trem de acionamento (MCC/VSD -> motor -> redutor -> estágios)
abaixo. Cada ponto de medição do catálogo PI (A..I, lubrificação e gêmeo
digital) é ancorado no equipamento onde a instrumentação realmente atua.

Uso:
    python scripts/desenhar_conjunto.py
"""

from __future__ import annotations

import os
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle, Wedge

# ---------------------------------------------------------------- paleta
NAVY = "#1f3b57"
BLUE = "#2b6cb0"
RED = "#b73a3a"
GREEN = "#2f7a4f"
GRAY = "#5b6770"
LGRAY = "#9aa5ad"
TEAL = "#2c8f8f"
AMBER = "#b8860b"
ORANGE = "#c05621"

FILL = "#eaf1f8"
FILL2 = "#f5f8fb"
FILLW = "#e6f2f2"
FILLO = "#fdf4e4"
FILLM = "#eef0f2"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})

OUTDIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figuras")
)


# ================================================================ primitivas
def tubo(ax, pts, cor=BLUE, lw=3.4, z=3, tracejado=False):
    """Tubulação com contorno escuro (leitura sobre fundo claro)."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    estilo = (0, (4, 2.5)) if tracejado else "solid"
    ax.plot(xs, ys, color=NAVY, lw=lw + 2.4, solid_capstyle="round",
            solid_joinstyle="round", zorder=z, linestyle=estilo)
    ax.plot(xs, ys, color=cor, lw=lw, solid_capstyle="round",
            solid_joinstyle="round", zorder=z + 1, linestyle=estilo)


def seta(ax, x, y, sentido="dir", cor=NAVY, s=0.30, z=6):
    if sentido == "dir":
        p = [(x - s, y - s * 0.75), (x + s, y), (x - s, y + s * 0.75)]
    elif sentido == "esq":
        p = [(x + s, y - s * 0.75), (x - s, y), (x + s, y + s * 0.75)]
    elif sentido == "cima":
        p = [(x - s * 0.75, y - s), (x, y + s), (x + s * 0.75, y - s)]
    else:
        p = [(x - s * 0.75, y + s), (x, y - s), (x + s * 0.75, y + s)]
    ax.add_patch(Polygon(p, closed=True, facecolor=cor, edgecolor="none", zorder=z))


def vaso_horizontal(ax, x0, x1, yc, r, fill=FILL, borda=NAVY, tampas=True):
    ax.add_patch(Rectangle((x0, yc - r), x1 - x0, 2 * r, facecolor=fill,
                           edgecolor=borda, lw=1.4, zorder=4))
    if tampas:
        ax.add_patch(Ellipse((x0, yc), 0.68 * r, 2 * r, facecolor=fill,
                             edgecolor=borda, lw=1.4, zorder=4))
        ax.add_patch(Ellipse((x1, yc), 0.68 * r, 2 * r, facecolor=fill,
                             edgecolor=borda, lw=1.4, zorder=4))


def vaso_vertical(ax, xc, y0, y1, r, fill=FILL, borda=NAVY):
    ax.add_patch(Rectangle((xc - r, y0), 2 * r, y1 - y0, facecolor=fill,
                           edgecolor=borda, lw=1.4, zorder=4))
    ax.add_patch(Ellipse((xc, y0), 2 * r, 0.5 * r, facecolor=fill,
                         edgecolor=borda, lw=1.4, zorder=4))
    ax.add_patch(Ellipse((xc, y1), 2 * r, 0.5 * r, facecolor=fill,
                         edgecolor=borda, lw=1.4, zorder=4))


def caixa(ax, x0, y0, w, h, fill=FILL, borda=NAVY, lw=1.4, raio=0.12, z=4):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h,
                                boxstyle=f"round,pad=0,rounding_size={raio}",
                                facecolor=fill, edgecolor=borda, lw=lw, zorder=z))


def parafuso(ax, x0, x1, y0, y1):
    """Carcaça de compressor de parafuso com os dois rotores à mostra."""
    caixa(ax, x0, y0, x1 - x0, y1 - y0, fill=FILL, borda=NAVY, lw=1.6, raio=0.22)
    xc = (x0 + x1) / 2
    yc = (y0 + y1) / 2
    r = min((y1 - y0) * 0.26, (x1 - x0) * 0.16)
    for dx, lobs in ((-r * 1.05, 4), (r * 1.05, 6)):
        ax.add_patch(Circle((xc + dx, yc), r, facecolor="white", edgecolor=BLUE,
                            lw=1.1, zorder=6))
        for a in np.linspace(0, 2 * np.pi, lobs, endpoint=False):
            ax.plot([xc + dx, xc + dx + r * 0.78 * np.cos(a)],
                    [yc, yc + r * 0.78 * np.sin(a)],
                    color=BLUE, lw=1.0, zorder=7)


def motor(ax, x0, x1, y0, y1):
    caixa(ax, x0, y0, x1 - x0, y1 - y0, fill=FILLM, borda=NAVY, lw=1.5, raio=0.30)
    n = 7
    for i in range(n):
        x = x0 + (x1 - x0) * (0.16 + 0.68 * i / (n - 1))
        ax.plot([x, x], [y0 + 0.16, y1 - 0.16], color=LGRAY, lw=0.9, zorder=5)
    ax.add_patch(Rectangle((x0 + 0.18, y1), 0.42, 0.22, facecolor=FILLM,
                           edgecolor=NAVY, lw=1.1, zorder=5))


def filtro_vertical(ax, xc, y0, y1, r):
    vaso_vertical(ax, xc, y0, y1, r, fill=FILL2)
    for yy in (y0 + 0.26, y1 - 0.26):
        ax.plot([xc - r, xc + r], [yy, yy], color=LGRAY, lw=0.9, zorder=5)


def torre_psa(ax, xc, y0, y1, r):
    vaso_vertical(ax, xc, y0, y1, r, fill=FILLW)
    for f in (0.18, 0.32, 0.68, 0.82):
        yy = y0 + (y1 - y0) * f
        ax.plot([xc - r, xc + r], [yy, yy], color=TEAL, lw=0.8, alpha=0.75, zorder=5)
    ax.add_patch(Rectangle((xc - r * 0.72, y0 + 0.30), r * 1.44, (y1 - y0) * 0.28,
                           facecolor="#d8ecec", edgecolor="none", zorder=4.5))


def trocador(ax, x0, x1, yc, r, cor_tubo=TEAL, fill=FILLW):
    vaso_horizontal(ax, x0, x1, yc, r, fill=fill)
    y_in = yc + r * 0.45
    y_out = yc - r * 0.45
    for yy in np.linspace(y_out, y_in, 5):
        ax.plot([x0 + 0.10, x1 - 0.10], [yy, yy], color=cor_tubo, lw=0.8,
                alpha=0.8, zorder=5)
    ax.plot([x0 + 0.5, x0 + 0.5], [yc - r, yc - r - 0.42], color=cor_tubo, lw=2.0, zorder=5)
    ax.plot([x1 - 0.5, x1 - 0.5], [yc + r, yc + r + 0.42], color=cor_tubo, lw=2.0, zorder=5)


def valvula(ax, x, y, s=0.17, cor=GRAY):
    ax.add_patch(Polygon([(x - s, y - s), (x - s, y + s), (x, y)],
                         closed=True, facecolor="white", edgecolor=cor, lw=1.2, zorder=7))
    ax.add_patch(Polygon([(x + s, y - s), (x + s, y + s), (x, y)],
                         closed=True, facecolor="white", edgecolor=cor, lw=1.2, zorder=7))


def texto(ax, x, y, s, size=8, cor=NAVY, peso="normal", ha="center", va="center",
          z=9, rot=0, caixa_branca=False, style="normal"):
    kw = dict(fontsize=size, color=cor, fontweight=peso, ha=ha, va=va,
              zorder=z, rotation=rot, style=style)
    if caixa_branca:
        kw["bbox"] = dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="none", alpha=0.92)
    ax.text(x, y, s, **kw)


# ================================================================ figura
def desenhar():
    fig = plt.figure(figsize=(16, 10.4))
    ax = fig.add_axes([0.012, 0.335, 0.976, 0.655])
    ax.set_xlim(0, 34)
    ax.set_ylim(0.6, 14.8)
    ax.axis("off")

    # ------------------------------------------------------------ skid
    y_skid = 1.55
    ax.add_patch(Rectangle((0.20, y_skid), 30.6, 0.34, facecolor="#dde3e9",
                           edgecolor=NAVY, lw=1.2, zorder=2))
    for xl in (0.9, 8.0, 16.4, 24.0, 30.3):
        ax.add_patch(Rectangle((xl, y_skid - 0.55), 0.34, 0.55, facecolor="#dde3e9",
                               edgecolor=NAVY, lw=1.0, zorder=2))
    texto(ax, 1.40, 1.18, "SKID ESTRUTURAL / BASE COMUM", 7.0, GRAY,
          peso="bold", ha="left")
    texto(ax, 0.35, 0.78, "Conjunto montado e testado em fábrica (FAT): compressor, motor, "
          "redutor, trocadores, secador e vaso numa única bancada.", 7.2, GRAY,
          ha="left", style="italic")

    # ------------------------------------------------------------ linha de ar
    Y = 9.25

    # Filtro de admissão
    fx = 2.55
    filtro_vertical(ax, fx, 10.05, 12.55, 0.62)
    ax.add_patch(Wedge((fx, 12.72), 0.62, 0, 180, width=0.16, facecolor=FILL2,
                       edgecolor=NAVY, lw=1.2, zorder=5))
    texto(ax, fx, 11.30, "F-01", 7.6, NAVY, peso="bold")
    texto(ax, fx, 10.78, "filtro de\nadmissão", 6.5, GRAY)
    tubo(ax, [(fx + 0.62, 10.30), (4.05, 10.30), (4.05, Y)], BLUE)

    # Estágio LP
    parafuso(ax, 4.05, 7.05, 7.85, 10.65)
    texto(ax, 5.55, 8.90, "C-01", 8.0, NAVY, peso="bold", caixa_branca=True)
    texto(ax, 5.55, 8.38, "estágio LP\n(parafuso duplo)", 6.5, GRAY, caixa_branca=True)

    # Intercooler
    trocador(ax, 7.75, 10.35, Y, 0.80)
    texto(ax, 9.05, Y + 0.10, "E-01 · intercooler", 7.0, NAVY, peso="bold", caixa_branca=True)
    texto(ax, 9.05, Y - 0.30, "ar × água", 6.2, GRAY, caixa_branca=True)

    # Estágio HP
    parafuso(ax, 10.75, 13.75, 7.85, 10.65)
    texto(ax, 12.25, 8.90, "C-02", 8.0, NAVY, peso="bold", caixa_branca=True)
    texto(ax, 12.25, 8.38, "estágio HP\n(parafuso duplo)", 6.5, GRAY, caixa_branca=True)

    # Aftercooler
    trocador(ax, 14.45, 17.05, Y, 0.80)
    texto(ax, 15.75, Y + 0.10, "E-02 · aftercooler", 7.0, NAVY, peso="bold", caixa_branca=True)
    texto(ax, 15.75, Y - 0.30, "ar × água", 6.2, GRAY, caixa_branca=True)

    # Separador ciclônico
    sx = 18.05
    ax.add_patch(Rectangle((sx - 0.62, 9.05), 1.24, 1.75, facecolor=FILL2,
                           edgecolor=NAVY, lw=1.4, zorder=4))
    ax.add_patch(Polygon([(sx - 0.62, 9.05), (sx + 0.62, 9.05), (sx, 7.75)],
                         closed=True, facecolor=FILL2, edgecolor=NAVY, lw=1.4, zorder=4))
    ax.plot([sx - 0.30, sx + 0.30], [7.88, 7.88], color=NAVY, lw=1.2, zorder=5)
    ax.plot([sx, sx], [7.88, 7.45], color=TEAL, lw=2.0, zorder=5)
    ax.add_patch(Polygon([(sx - 0.13, 7.62), (sx + 0.13, 7.62), (sx, 7.38)],
                         closed=True, facecolor=TEAL, edgecolor="none", zorder=6))
    texto(ax, sx, 10.00, "V-01", 7.4, NAVY, peso="bold", caixa_branca=True)
    texto(ax, sx, 9.52, "separador\nciclônico", 6.2, GRAY, caixa_branca=True)
    texto(ax, sx - 0.30, 7.42, "condensado", 5.9, TEAL, ha="right")

    # Secador PSA
    xs1, xs2 = 19.85, 21.65
    for xc, nome in ((xs1, "A"), (xs2, "B")):
        torre_psa(ax, xc, 7.85, 10.95, 0.52)
        texto(ax, xc, 9.40, nome, 7.4, TEAL, peso="bold", caixa_branca=True)
    texto(ax, 19.40, 7.46, "D-01 · secador PSA (2 torres)", 6.8, NAVY,
          peso="bold", ha="left")
    texto(ax, 19.40, 7.12, "adsorção com regeneração alternada", 6.0, GRAY, ha="left")

    # Filtros de linha
    filtro_vertical(ax, 23.25, 8.55, 10.05, 0.40)
    texto(ax, 23.25, 10.42, "F-02/F-03", 7.0, NAVY, peso="bold")
    texto(ax, 23.25, 8.14, "filtros de\nlinha", 6.3, GRAY)

    # Vaso pulmão
    vaso_horizontal(ax, 24.15, 27.75, Y - 0.15, 1.15, fill=FILL)
    for xl in (24.75, 27.15):
        ax.add_patch(Rectangle((xl - 0.16, Y - 0.15 - 1.15 - 0.30), 0.32, 0.32,
                               facecolor="#dde3e9", edgecolor=NAVY, lw=1.0, zorder=5))
    texto(ax, 25.95, 9.55, "V-02 · vaso pulmão", 7.0, NAVY, peso="bold", caixa_branca=True)
    texto(ax, 25.95, 9.05, "amortecimento de rede", 6.2, GRAY, caixa_branca=True)

    # Header de distribuição
    hx = 28.85
    ax.add_patch(Rectangle((hx - 0.16, 6.55), 0.32, 5.30, facecolor=FILL,
                           edgecolor=NAVY, lw=1.3, zorder=4))
    for yy in (7.35, 9.20, 11.05):
        ax.plot([hx + 0.16, hx + 0.95], [yy, yy], color=NAVY, lw=3.0, zorder=3)
        ax.plot([hx + 0.16, hx + 0.95], [yy, yy], color=BLUE, lw=1.6, zorder=4)
        seta(ax, hx + 1.12, yy, "dir", NAVY, 0.17)
    texto(ax, hx, 12.20, "header", 6.9, NAVY, peso="bold")
    texto(ax, hx, 6.24, "para a rede", 6.0, GRAY)

    # ------------------------------------------------------------ linha de ar: trechos
    trechos = [
        [(7.05, Y), (7.75, Y)],
        [(10.35, Y), (10.75, Y)],
        [(13.75, Y), (14.45, Y)],
        [(17.05, Y), (17.43, Y)],
        [(18.67, Y), (19.33, Y)],
        [(22.17, Y), (22.85, Y)],
        [(23.65, Y), (24.15, Y)],
        [(27.75, Y), (28.69, Y)],
    ]
    for t in trechos:
        tubo(ax, t, BLUE)
    for xa in (7.40, 10.55, 14.10, 22.50, 23.95, 28.20):
        seta(ax, xa, Y, "dir", NAVY, 0.22)

    # PSA: manifold de entrada/saída
    tubo(ax, [(18.67, Y), (18.67, 8.55), (19.33, 8.55)], BLUE, lw=2.6)
    tubo(ax, [(19.33, 8.55), (19.33, Y)], BLUE, lw=2.6)
    tubo(ax, [(20.37, 8.30), (21.13, 8.30)], BLUE, lw=2.6)
    tubo(ax, [(22.17, Y), (22.17, 8.30), (21.13, 8.30)], BLUE, lw=2.6)
    for xc in (xs1, xs2):
        tubo(ax, [(xc, 7.85), (xc, 8.30)], BLUE, lw=2.2)
    for xv in (19.45, 22.05):
        valvula(ax, xv, Y + 0.02, 0.13)

    # ------------------------------------------------------------ água de resfriamento
    y_agua = 11.55
    tubo(ax, [(7.20, y_agua), (16.90, y_agua)], TEAL, lw=2.4)
    tubo(ax, [(8.25, y_agua), (8.25, Y + 0.80 + 0.42)], TEAL, lw=1.9)
    tubo(ax, [(16.55, y_agua), (16.55, Y + 0.80 + 0.42)], TEAL, lw=1.9)
    tubo(ax, [(8.25, Y - 0.80 - 0.42), (8.25, 7.15), (15.85, 7.15)], TEAL, lw=1.9)
    tubo(ax, [(15.85, 7.15), (15.85, Y - 0.80 - 0.42)], TEAL, lw=1.9)
    texto(ax, 7.10, y_agua + 0.34, "água de resfriamento", 6.5, TEAL, ha="left", peso="bold")
    texto(ax, 8.40, 6.88, "retorno de água", 6.3, TEAL, ha="left")
    seta(ax, 12.6, y_agua, "dir", TEAL, 0.18)
    seta(ax, 11.0, 7.15, "esq", TEAL, 0.18)

    # ------------------------------------------------------------ trem de acionamento
    # MCC / VSD
    caixa(ax, 0.35, 2.75, 1.30, 3.85, fill="#f2f4f6", borda=NAVY, lw=1.4, raio=0.08)
    for i in range(3):
        ax.plot([0.55, 1.45], [3.05 + i * 0.30, 3.05 + i * 0.30], color=LGRAY, lw=1.0, zorder=5)
    ax.add_patch(Circle((1.00, 4.55), 0.20, facecolor="white", edgecolor=ORANGE, lw=1.4, zorder=6))
    ax.plot([0.92, 1.08], [4.55, 4.55], color=ORANGE, lw=1.2, zorder=7)
    texto(ax, 1.00, 6.85, "MCC / VSD", 7.2, NAVY, peso="bold")
    texto(ax, 1.00, 5.62, "painel\nelétrico", 6.2, GRAY)

    tubo(ax, [(1.65, 4.55), (2.05, 4.55)], ORANGE, lw=2.2, tracejado=True)

    # Motor
    motor(ax, 2.05, 5.15, 3.25, 5.05)
    texto(ax, 3.60, 3.02, "M-01 · motor elétrico (VSD)", 7.0, NAVY, peso="bold")
    ax.plot([5.15, 5.55], [4.15, 4.15], color=NAVY, lw=3.2, zorder=5)

    # Acoplamento
    ax.add_patch(Rectangle((5.55, 3.95), 0.32, 0.40, facecolor="white",
                           edgecolor=NAVY, lw=1.2, zorder=6))

    # Redutor
    caixa(ax, 5.87, 3.15, 7.55, 2.20, fill=FILLM, borda=NAVY, lw=1.6, raio=0.18)
    texto(ax, 9.65, 3.50, "G-01 · redutor de engrenagens (2 pinhões)", 7.0, NAVY,
          peso="bold", caixa_branca=True)
    for xp in (6.55, 12.15):
        ax.add_patch(Circle((xp, 4.20), 0.42, facecolor="white", edgecolor=BLUE, lw=1.2, zorder=6))
        for ang in np.linspace(0, 2 * np.pi, 10, endpoint=False):
            ax.plot([xp, xp + 0.38 * np.cos(ang)], [4.20, 4.20 + 0.38 * np.sin(ang)],
                    color=BLUE, lw=0.7, zorder=7)

    # eixos verticais até os estágios
    for xp in (6.55, 12.15):
        tubo(ax, [(xp, 5.35), (xp, 7.85)], GRAY, lw=2.0, tracejado=True)
    texto(ax, 6.55, 6.30, "eixo LP", 5.9, GRAY, rot=90, caixa_branca=True)
    texto(ax, 12.15, 6.30, "eixo HP", 5.9, GRAY, rot=90, caixa_branca=True)

    # ------------------------------------------------------------ console de óleo
    caixa(ax, 6.15, 1.95, 4.30, 1.00, fill=FILLO, borda=AMBER, lw=1.3, raio=0.10)
    texto(ax, 8.30, 2.78, "óleo: bomba · filtro · resfriador", 5.9, AMBER, peso="bold")
    ax.add_patch(Circle((6.75, 2.30), 0.20, facecolor="white", edgecolor=AMBER, lw=1.2, zorder=6))
    ax.plot([6.75, 6.93], [2.30, 2.30], color=AMBER, lw=1.0, zorder=7)
    ax.add_patch(Rectangle((7.42, 2.10), 0.66, 0.40, facecolor="white",
                           edgecolor=AMBER, lw=1.1, zorder=6))
    ax.add_patch(Rectangle((8.52, 2.10), 0.50, 0.40, facecolor="white",
                           edgecolor=AMBER, lw=1.1, zorder=6))
    tubo(ax, [(6.55, 3.15), (6.55, 2.30), (6.55, 2.30)], AMBER, lw=1.6)
    tubo(ax, [(9.20, 2.30), (10.65, 2.30), (10.65, 3.15)], AMBER, lw=1.6)

    # ------------------------------------------------------------ gêmeo digital
    dt_x0, dt_y0, dt_w, dt_h = 30.70, 11.95, 3.20, 2.40
    ax.add_patch(FancyBboxPatch((dt_x0, dt_y0), dt_w, dt_h,
                                boxstyle="round,pad=0,rounding_size=0.16",
                                facecolor="#eef3f9", edgecolor=NAVY, lw=1.3,
                                linestyle=(0, (5, 3)), zorder=4))
    texto(ax, dt_x0 + dt_w / 2, dt_y0 + dt_h - 0.30, "GÊMEO DIGITAL", 7.6, NAVY, peso="bold")
    linhas_dt = [
        "İ_total — exergia destruída",
        "ṁ_CO₂ — emissão de carbono",
        "HI — health index da máquina",
    ]
    for i, s in enumerate(linhas_dt):
        texto(ax, dt_x0 + 0.18, dt_y0 + dt_h - 0.78 - i * 0.42, s, 6.0, GRAY, ha="left")
    texto(ax, dt_x0 + dt_w / 2, dt_y0 + 0.26, "calculado a partir de A…I", 5.9, GRAY,
          style="italic")

    # ============================================================ pontos de medição
    def ponto(letra, xtxt, ytxt, xalvo, yalvo, grandezas, abaixo=False):
        ax.annotate("", xy=(xalvo, yalvo), xytext=(xtxt, ytxt),
                    arrowprops=dict(arrowstyle="-", color=NAVY, lw=1.0,
                                    shrinkA=9, shrinkB=1), zorder=8)
        ax.add_patch(Circle((xtxt, ytxt), 0.38, facecolor=NAVY, edgecolor="white",
                            lw=1.4, zorder=9))
        texto(ax, xtxt, ytxt, letra, 9.0, "white", peso="bold", z=10)
        if grandezas:
            dy = -0.58 if abaixo else 0.58
            texto(ax, xtxt, ytxt + dy, grandezas, 6.1, GRAY, z=10,
                  va="top" if abaixo else "bottom")

    ponto("A", 1.00, 7.82, 1.00, 6.68, "V · I · f · cos φ · VU · IU")
    ponto("C", 5.55, 12.32, 5.55, 10.65, "P_s · T_d · δ_LP")
    ponto("D", 9.95, 12.50, 9.95, 10.05, "T_w,in · P_int · ΔP_ic · ṁ_c")
    ponto("E", 12.25, 12.32, 12.25, 10.65, "P_d · T_d · δ_axial")
    ponto("F", 15.75, 12.50, 15.75, 10.05, "T_ac,out")
    ponto("G", 20.75, 12.35, 20.75, 11.00, "T_dp · ṁ_purga · ΔP_filtro")
    ponto("H", 25.95, 11.80, 25.95, 10.30, "P_tk · L_tk")
    ponto("I", 28.85, 12.85, 28.85, 11.87, "ṁ_tot")
    # B — acoplamento/redutor (linha de chamada vertical, sem cruzar o motor)
    ponto("B", 5.71, 6.55, 5.71, 4.40, "N · τ · v_rms · σ_b")
    # L — console de óleo
    ponto("L", 11.55, 2.30, 10.65, 2.30, "T_óleo · P_óleo")

    # ------------------------------------------------------------ título
    texto(ax, 0.30, 14.38,
          "Conjunto compressor de parafuso duplo oil-free — onde a instrumentação aponta",
          12.0, NAVY, peso="bold", ha="left")
    texto(ax, 0.30, 13.92,
          "Dois estágios com intercooler, aftercooler, secagem PSA e vaso pulmão · "
          "pontos A–I conforme Tabela 18.1", 7.8, GRAY, ha="left")

    # legenda de cores
    itens = [(BLUE, "ar comprimido"), (TEAL, "água de resfriamento"),
             (AMBER, "óleo de lubrificação"), (ORANGE, "energia elétrica")]
    lx, ly = 19.1, 14.35
    for i, (cor, rot) in enumerate(itens):
        xx = lx + (i % 2) * 5.3
        yy = ly - (i // 2) * 0.44
        ax.plot([xx, xx + 0.50], [yy, yy], color=cor, lw=3.2, solid_capstyle="round", zorder=6)
        texto(ax, xx + 0.62, yy, rot, 6.4, GRAY, ha="left")

    # ============================================================ tabela
    axt = fig.add_axes([0.012, 0.010, 0.976, 0.300])
    axt.set_xlim(0, 34)
    axt.set_ylim(0, 11)
    axt.axis("off")

    col_x = [0.15, 1.35, 6.45, 12.30, 21.30, 28.60]
    cabecalho = ["Ponto", "Local no conjunto", "Equipamento", "Grandezas medidas",
                 "Tags PI (prefixo CMP01:)", "Un."]

    linhas = [
        ("A", "Painel elétrico / MCC-VSD", "MCC-01", "tensão, corrente, frequência, cos φ, desbalanços",
         "ELE_VL, ELE_I, ELE_FREQ, ELE_COSPHI, ELE_VU, ELE_IU", "V, A, Hz, -, %, %"),
        ("B", "Acoplamento e redutor", "G-01", "rotação, torque, vibração global, tensão no dente",
         "MEC_RPM, MEC_TORQ, MEC_VIB_RMS, MEC_SIGMA_B", "RPM, N·m, mm/s, MPa"),
        ("C", "Sucção e descarga do estágio LP", "C-01", "pressão de sucção, temperatura de descarga, folga dos rotores",
         "LP_PSUC, LP_TDISC, LP_CLEARANCE", "bar, °C, μm/m"),
        ("D", "Intercooler (ar × água)", "E-01", "água de entrada, pressão interestágio, perda de carga, condensado",
         "IC_TW_IN, IC_PINT, IC_DP, IC_MCOND", "°C, bar, mbar, kg/h"),
        ("E", "Descarga do estágio HP", "C-02", "pressão final, temperatura de descarga, posição axial do rotor",
         "HP_PDISC, HP_TDISC, HP_AXIAL", "bar, °C, μm"),
        ("F", "Saída do aftercooler", "E-02", "temperatura de saída do ar",
         "AC_TAC_OUT", "°C"),
        ("G", "Secador PSA e filtros de linha", "D-01 / F-02", "ponto de orvalho, vazão de purga, perda de carga",
         "PSA_TDP, PSA_MPURGE, FLT_DP", "°C, kg/s, mbar"),
        ("H", "Vaso pulmão", "V-02", "pressão e nível de condensado",
         "TK_PTK, TK_LTK", "bar, %"),
        ("I", "Header de distribuição", "HDR-01", "vazão total demandada pela planta",
         "HDR_MTOT", "kg/s"),
        ("L", "Console de óleo (mancais e redutor)", "L-01", "temperatura de retorno e pressão de suprimento",
         "OIL_TT_RET, OIL_PT_SUP", "°C, bar"),
        ("DT", "Gêmeo digital (não é sensor)", "—", "exergia destruída, emissão de CO₂, health index",
         "DT_EXERGY_DEST, DT_CO2_RATE, DT_HEALTH_INDEX", "kW, kg/h, -"),
    ]

    y_topo = 10.25
    y_lin = 0.72
    axt.add_patch(Rectangle((0.10, y_topo - 0.55), 33.8, 0.62, facecolor=NAVY,
                            edgecolor="none", zorder=2))
    for i, c in enumerate(cabecalho):
        axt.text(col_x[i], y_topo - 0.24, c, fontsize=6.6, color="white",
                 fontweight="bold", ha="left", va="center", zorder=3)

    for j, (pto, local, equip, grand, tags, un) in enumerate(linhas):
        y = y_topo - 0.55 - (j + 1) * y_lin
        if j % 2 == 0:
            axt.add_patch(Rectangle((0.10, y - 0.36), 33.8, y_lin, facecolor="#f4f7fa",
                                    edgecolor="none", zorder=1))
        axt.add_patch(Circle((col_x[0] + 0.34, y - 0.02), 0.21, facecolor=NAVY,
                             edgecolor="none", zorder=3))
        axt.text(col_x[0] + 0.34, y - 0.02, pto, fontsize=6.0, color="white",
                 fontweight="bold", ha="center", va="center", zorder=4)
        axt.text(col_x[1], y - 0.02, local, fontsize=6.3, color="#1a1a1a", ha="left", va="center")
        axt.text(col_x[2], y - 0.02, equip, fontsize=6.3, color=GRAY, ha="left", va="center")
        axt.text(col_x[3], y - 0.02, grand, fontsize=6.0, color="#1a1a1a", ha="left", va="center")
        axt.text(col_x[4], y - 0.02, tags, fontsize=5.6, color=BLUE, ha="left", va="center",
                 family="DejaVu Sans Mono")
        axt.text(col_x[5], y - 0.02, un, fontsize=5.6, color=GRAY, ha="left", va="center")

    axt.plot([0.10, 33.9], [y_topo - 0.55 - len(linhas) * y_lin - 0.30] * 2,
             color=LGRAY, lw=0.8)
    axt.text(0.15, 0.28,
             "Cada bolha marca o local físico da instrumentação; as tags seguem o catálogo OSIsoft PI do "
             "gêmeo digital. A e B são grandezas de máquina, C–G de processo e H–I de rede.",
             fontsize=6.0, color=GRAY, style="italic", ha="left", va="center")

    os.makedirs(OUTDIR, exist_ok=True)
    base = "fig_18_2_conjunto_pontos"

    pdf_path = os.path.join(OUTDIR, f"{base}.pdf")
    fig.savefig(pdf_path, dpi=200, bbox_inches="tight", facecolor="white")
    print("salvo:", pdf_path)
    svg_path = os.path.join(OUTDIR, f"{base}.svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor="white")
    print("salvo:", svg_path)

    png_path = os.path.join(OUTDIR, f"{base}.png")
    fig.savefig(png_path, dpi=400, bbox_inches="tight", facecolor="white")
    print("salvo:", png_path)

    # versoes embutidas no aplicativo web (compressor2/crates/app/assets)
    app_assets = os.path.normpath(
        os.path.join(OUTDIR, "..", "compressor2", "crates", "app", "assets")
    )
    os.makedirs(app_assets, exist_ok=True)
    web_png = os.path.join(app_assets, "conjunto-pontos.png")
    fig.savefig(web_png, dpi=150, bbox_inches="tight", facecolor="white")
    print("salvo:", web_png)
    web_pdf = os.path.join(app_assets, "conjunto-pontos.pdf")
    shutil.copyfile(pdf_path, web_pdf)
    print("salvo:", web_pdf)

    plt.close(fig)


if __name__ == "__main__":
    desenhar()
