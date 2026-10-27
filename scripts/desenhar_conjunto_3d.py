"""Versão 3D do conjunto compressor + motor, com os pontos de medição.

Gera:
    figuras/fig_18_3_conjunto_3d.{pdf,png}
    compressor2/crates/app/assets/conjunto-3d.png

Reaproveita a convenção 3D de scripts/gen_figuras.py (quads com sombreamento
plano, câmera isométrica). Os pontos A..I, L e DT são projetados para a tela
e anotados com bolha + linha de chamada, para não girar com a cena.

Uso:
    python scripts/desenhar_conjunto_3d.py
"""

from __future__ import annotations

import os
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

NAVY = "#1f3b57"
BLUE = "#2b6cb0"
TEAL = "#2c8f8f"
AMBER = "#b8860b"
ORANGE = "#c05621"
GRAY = "#5b6770"
LGRAY = "#9aa5ad"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})

OUTDIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figuras")
)

# --------------------------------------------------------------- iluminação
_LUZ = np.array([-0.45, -0.60, 0.66])
_LUZ = _LUZ / np.linalg.norm(_LUZ)


def _sombra(normal, cor, amb=0.38):
    lam = abs(np.dot(normal, _LUZ))
    return np.clip(np.array(cor, dtype=float) * (amb + (1 - amb) * lam), 0, 1)


# --------------------------------------------------------------- primitivas
def _caixa(x0, x1, y0, y1, z0, z1, cor, amb=0.38):
    faces = [
        ([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]], (0, 0, -1)),
        ([[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], (0, 0, 1)),
        ([[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], (0, -1, 0)),
        ([[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], (0, 1, 0)),
        ([[x0, y0, z0], [x0, y1, z0], [x0, y1, z1], [x0, y0, z1]], (-1, 0, 0)),
        ([[x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]], (1, 0, 0)),
    ]
    q, c = [], []
    for poly, n in faces:
        q.append(np.array(poly, dtype=float))
        c.append(_sombra(np.array(n, dtype=float), cor, amb))
    return q, c


def _cil(eixo, lo, hi, c1, c2, r, cor, n=28, amb=0.38, tampas=True):
    n = max(n, 72)  # suaviza a curvatura
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    q, c = [], []

    def pt(a, u, v):
        if eixo == "x":
            return (a, u, v)
        if eixo == "y":
            return (v, a, u)
        return (u, v, a)

    def nr(u, v):
        if eixo == "x":
            return (0.0, u, v)
        if eixo == "y":
            return (v, 0.0, u)
        return (u, v, 0.0)

    for j in range(n):
        k = (j + 1) % n
        ua, va = c1 + r * np.cos(ang[j]), c2 + r * np.sin(ang[j])
        ub, vb = c1 + r * np.cos(ang[k]), c2 + r * np.sin(ang[k])
        q.append(np.array([pt(lo, ua, va), pt(lo, ub, vb), pt(hi, ub, vb), pt(hi, ua, va)]))
        c.append(_sombra(np.array(nr(np.cos((ang[j] + ang[k]) / 2),
                                    np.sin((ang[j] + ang[k]) / 2))), cor, amb))
    if tampas:
        for a, s in ((lo, -1.0), (hi, 1.0)):
            centro = np.array(pt(a, c1, c2))
            nv = np.array(nr(0, 0)) + np.array(pt(s, 0, 0)) - np.array(pt(0, 0, 0))
            ct = _sombra(nv, cor, amb + 0.05)
            for j in range(n):
                k = (j + 1) % n
                ua, va = c1 + r * np.cos(ang[j]), c2 + r * np.sin(ang[j])
                ub, vb = c1 + r * np.cos(ang[k]), c2 + r * np.sin(ang[k])
                q.append(np.array([centro, pt(a, ua, va), pt(a, ub, vb)]))
                c.append(ct)
    return q, c


def _frustum(eixo, lo, hi, c1, c2, r_lo, r_hi, cor, n=28, amb=0.38, tampas=True):
    n = max(n, 72)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    q, c = [], []

    def pt(a, u, v):
        if eixo == "x":
            return (a, u, v)
        if eixo == "y":
            return (v, a, u)
        return (u, v, a)

    incl = (r_hi - r_lo) / max(hi - lo, 1e-9)
    for j in range(n):
        k = (j + 1) % n
        ua, va = c1 + r_lo * np.cos(ang[j]), c2 + r_lo * np.sin(ang[j])
        ub, vb = c1 + r_lo * np.cos(ang[k]), c2 + r_lo * np.sin(ang[k])
        uc, vc = c1 + r_hi * np.cos(ang[k]), c2 + r_hi * np.sin(ang[k])
        ud, vd = c1 + r_hi * np.cos(ang[j]), c2 + r_hi * np.sin(ang[j])
        q.append(np.array([pt(lo, ua, va), pt(lo, ub, vb), pt(hi, uc, vc), pt(hi, ud, vd)]))
        na = (np.cos(ang[j]) + np.cos(ang[k])) / 2
        nb = (np.sin(ang[j]) + np.sin(ang[k])) / 2
        if eixo == "x":
            nv = np.array([incl, na, nb])
        elif eixo == "y":
            nv = np.array([nb, incl, na])
        else:
            nv = np.array([na, nb, incl])
        q.append  # noqa
        c.append(_sombra(nv / np.linalg.norm(nv), cor, amb))
    if tampas:
        if r_hi > 1e-6:
            centro = np.array(pt(hi, c1, c2))
            nv = np.array([1.0, 0, 0]) if eixo == "x" else (
                np.array([0, 1.0, 0]) if eixo == "y" else np.array([0, 0, 1.0]))
            ct = _sombra(nv, cor, amb + 0.05)
            for j in range(n):
                k = (j + 1) % n
                q.append(np.array([centro,
                                   pt(hi, c1 + r_hi * np.cos(ang[j]), c2 + r_hi * np.sin(ang[j])),
                                   pt(hi, c1 + r_hi * np.cos(ang[k]), c2 + r_hi * np.sin(ang[k]))]))
                c.append(ct)
        centro = np.array(pt(lo, c1, c2))
        ct = _sombra(np.array([-1.0, 0, 0]), cor, amb + 0.05)
        for j in range(n):
            k = (j + 1) % n
            q.append(np.array([centro,
                               pt(lo, c1 + r_lo * np.cos(ang[j]), c2 + r_lo * np.sin(ang[j])),
                               pt(lo, c1 + r_lo * np.cos(ang[k]), c2 + r_lo * np.sin(ang[k]))]))
            c.append(ct)
    return q, c


def _tubo3d(p0, p1, r, cor, n=10):
    """Cilindro entre dois pontos quaisquer (tubulação)."""
    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    v = p1 - p0
    L = np.linalg.norm(v)
    if L < 1e-9:
        return [], []
    eixo = v / L
    aux = np.array([0, 0, 1.0]) if abs(eixo[2]) < 0.9 else np.array([1.0, 0, 0])
    u = np.cross(eixo, aux)
    u /= np.linalg.norm(u)
    w = np.cross(eixo, u)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    q, c = [], []
    for j in range(n):
        k = (j + 1) % n
        a0 = p0 + r * (np.cos(ang[j]) * u + np.sin(ang[j]) * w)
        a1 = p0 + r * (np.cos(ang[k]) * u + np.sin(ang[k]) * w)
        b0 = p1 + r * (np.cos(ang[j]) * u + np.sin(ang[j]) * w)
        b1 = p1 + r * (np.cos(ang[k]) * u + np.sin(ang[k]) * w)
        q.append(np.array([a0, a1, b1, b0]))
        nv = np.cos((ang[j] + ang[k]) / 2) * u + np.sin((ang[j] + ang[k]) / 2) * w
        c.append(_sombra(nv / np.linalg.norm(nv), cor, 0.45))
    return q, c



def _bbox_conteudo(fig, dpi=90, margem=0.10):
    """Recorta o branco em volta da cena: os eixos 3D ocupam a figura inteira,
    entao o bbox_inches="tight" nao apara nada."""
    import io

    from matplotlib.transforms import Bbox
    from PIL import Image

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor="white")
    buf.seek(0)
    im = Image.open(buf).convert("RGB")
    w, h = im.size
    px = im.load()

    esq, topo, dir_, base = w, h, 0, 0
    for y in range(h):
        achou = False
        for x in range(0, w, 2):
            if px[x, y] != (255, 255, 255):
                achou = True
                if x < esq:
                    esq = x
                if x > dir_:
                    dir_ = x
        if achou:
            if y < topo:
                topo = y
            base = y

    if esq >= dir_ or topo >= base:
        return "tight"

    return Bbox.from_extents(
        max(0.0, esq / dpi - margem),
        max(0.0, (h - base) / dpi - margem),
        min(w / dpi, dir_ / dpi + margem),
        min(h / dpi, (h - topo) / dpi + margem),
    )


# =============================================================== cena
def desenhar():
    fig = plt.figure(figsize=(15.5, 8.8))
    ax = fig.add_axes([0.0, 0.085, 1.0, 1.0], projection="3d")
    ax.set_axis_off()

    Q, C = [], []

    def add(par):
        q, c = par
        Q.extend(q)
        C.extend(c)

    # ---------------------------------------------------------- cores
    SKID = (0.80, 0.83, 0.86)
    MOTOR = (0.22, 0.32, 0.46)
    ALETA = (0.27, 0.38, 0.53)
    CAIXA = (0.62, 0.66, 0.71)
    GB = (0.60, 0.63, 0.68)
    TAMPA = (0.46, 0.50, 0.56)
    CASCO = (0.26, 0.42, 0.60)
    CASCO2 = (0.30, 0.47, 0.65)
    TROCADOR = (0.40, 0.63, 0.57)
    VASO = (0.50, 0.60, 0.73)
    PSA = (0.33, 0.57, 0.57)
    FILTRO = (0.56, 0.61, 0.68)
    OLEO = (0.76, 0.60, 0.25)
    PAINEL = (0.54, 0.57, 0.61)

    # ---------------------------------------------------------- skid
    add(_caixa(0.0, 27.8, -3.2, 3.2, -0.45, 0.0, SKID))
    for xl in (1.0, 8.0, 15.0, 21.0, 27.0):
        add(_caixa(xl, xl + 0.40, -3.0, 3.0, -1.35, -0.45, SKID))

    # ---------------------------------------------------------- MCC / VSD
    add(_caixa(0.3, 1.45, -3.0, -1.9, 0.0, 3.05, PAINEL))
    add(_caixa(0.3, 1.45, -3.05, -2.98, 1.0, 2.3, (0.35, 0.38, 0.42)))

    # ---------------------------------------------------------- motor
    MX0, MX1 = 1.75, 5.05
    ZM = 1.25
    add(_cil("x", MX0, MX1, 0.0, ZM, 0.95, MOTOR, n=34, tampas=False))
    add(_cil("x", MX0, MX0 + 0.07, 0.0, ZM, 0.95, MOTOR, n=34))
    add(_cil("x", MX1 - 0.07, MX1, 0.0, ZM, 0.95, MOTOR, n=34))
    for xa in np.arange(MX0 + 0.30, MX1 - 0.25, 0.28):
        add(_cil("x", xa, xa + 0.09, 0.0, ZM, 1.05, ALETA, n=34, tampas=False))
    add(_caixa(2.3, 3.3, -0.42, 0.42, ZM + 0.95, ZM + 1.45, CAIXA))
    add(_caixa(MX0 + 0.1, MX1 - 0.1, -1.25, -0.95, 0.0, 0.45, (0.34, 0.35, 0.37)))

    # ---------------------------------------------------------- acoplamento
    add(_cil("x", 5.05, 5.40, 0.0, ZM, 0.36, (0.55, 0.57, 0.60), n=24))
    add(_cil("x", 5.14, 5.26, 0.0, ZM, 0.46, TAMPA, n=24))

    # ---------------------------------------------------------- redutor
    add(_caixa(5.40, 13.6, -1.45, 1.45, 0.30, 2.30, GB))
    for ya in (-1.47, 1.39):
        add(_caixa(5.40, 13.6, ya, ya + 0.08, 0.55, 2.05, TAMPA))
    add(_caixa(6.4, 8.2, 1.45, 1.57, 0.85, 1.85, TAMPA))
    for xp in (7.0, 12.2):
        add(_cil("y", -1.50, -1.42, 1.45, xp, 0.58, (0.70, 0.72, 0.76), n=24))
        add(_cil("y", -1.50, -1.42, 1.45, xp, 0.26, (0.44, 0.47, 0.51), n=18))

    # ---------------------------------------------------------- estágios
    def estagio(x0, x1, cor):
        z0, z1 = 2.30, 4.35
        add(_caixa(x0, x1, -1.30, 1.30, z0, z1, cor))
        add(_caixa(x0 + 0.10, x1 - 0.10, -1.38, 1.38, z0 + 0.12, z1 - 0.12, cor))
        for yc in (-0.52, 0.52):
            add(_cil("x", x0 + 0.15, x1 - 0.15, yc, z1 + 0.10, 0.40, TAMPA, n=20))

    estagio(4.55, 8.05, CASCO)
    estagio(10.75, 14.25, CASCO2)

    # ---------------------------------------------------------- trocadores
    def trocador(x0, x1, cor):
        zc, r = 3.25, 0.82
        add(_cil("x", x0, x1, 0.0, zc, r, cor, n=26))
        for xa in (x0 + 0.55, x1 - 0.75):
            add(_caixa(xa, xa + 0.30, -0.50, 0.50, zc - r - 0.45, zc - r + 0.05,
                       (0.54, 0.57, 0.61)))
        add(_cil("z", zc + r, zc + r + 0.34, x0 + 0.62, 0.0, 0.13, (0.28, 0.56, 0.56), n=10))
        add(_cil("z", zc - r - 0.34, zc - r, x1 - 0.58, 0.0, 0.13, (0.28, 0.56, 0.56), n=10))

    trocador(8.35, 10.45, TROCADOR)     # intercooler
    trocador(14.55, 16.65, TROCADOR)    # aftercooler

    # ---------------------------------------------------------- filtro de admissão
    add(_cil("z", 0.30, 3.55, 2.55, -2.35, 0.58, FILTRO, n=24))
    add(_frustum("z", 3.55, 3.95, 2.55, -2.35, 0.58, 0.28, FILTRO, n=24))

    # ---------------------------------------------------------- separador ciclônico
    SX = 17.45
    add(_cil("z", 1.65, 4.05, SX, 0.0, 0.66, VASO, n=24))
    add(_frustum("z", 0.60, 1.65, SX, 0.0, 0.14, 0.66, VASO, n=24))
    add(_cil("z", 0.45, 0.60, SX, 0.0, 0.14, (0.38, 0.52, 0.52), n=10))

    # ---------------------------------------------------------- secador PSA
    for xc in (18.95, 20.15):
        add(_cil("z", 0.35, 5.05, xc, 0.0, 0.64, PSA, n=24))
        for zz in (0.85, 1.85, 3.45, 4.45):
            add(_cil("z", zz, zz + 0.09, xc, 0.0, 0.68, (0.28, 0.47, 0.47), n=24, tampas=False))

    # ---------------------------------------------------------- filtros de linha
    add(_cil("z", 0.65, 3.05, 21.55, 0.0, 0.40, FILTRO, n=20))
    add(_frustum("z", 3.05, 3.32, 21.55, 0.0, 0.40, 0.20, FILTRO, n=20))

    # ---------------------------------------------------------- vaso pulmão
    add(_cil("x", 22.45, 26.15, 0.0, 1.80, 1.20, VASO, n=28))
    for xa in (23.10, 25.45):
        add(_caixa(xa, xa + 0.40, -0.85, 0.85, 0.0, 0.75, (0.54, 0.57, 0.61)))
    add(_cil("z", 2.95, 3.55, 24.30, 0.0, 0.18, (0.44, 0.54, 0.62), n=10))

    # ---------------------------------------------------------- header
    HX = 27.05
    add(_cil("z", 0.60, 4.85, HX, 0.0, 0.19, (0.44, 0.57, 0.71), n=14))
    for zz, yy in ((1.55, 1.15), (2.95, -1.25), (4.15, 0.55)):
        add(_cil("y", 0.0, yy, zz, HX, 0.13, (0.44, 0.57, 0.71), n=10))

    # ---------------------------------------------------------- tubulação de ar
    AR = (0.28, 0.48, 0.73)
    ZA = 3.30
    trechos = [
        ((-2.35, 3.55, 2.55), (-2.35, 2.55, 3.30)),
        ((-2.35, 2.55, 3.30), (4.55, 0.0, 3.30)),
        ((8.05, 0.0, ZA), (8.35, 0.0, ZA)),
        ((10.45, 0.0, ZA), (10.75, 0.0, ZA)),
        ((14.25, 0.0, ZA), (14.55, 0.0, ZA)),
        ((16.65, 0.0, ZA), (17.45, 0.0, ZA)),
        ((17.45, 0.0, ZA), (17.45, 0.0, 2.60)),
        ((17.45, 0.0, 2.15), (18.95, 0.0, 2.15)),
        ((20.15, 0.0, 2.15), (21.55, 0.0, 2.15)),
        ((21.55, 0.0, 2.15), (21.55, 0.0, 2.90)),
        ((21.55, 0.0, 3.05), (22.45, 0.0, 2.60)),
        ((26.15, 0.0, 1.80), (HX, 0.0, 1.80)),
    ]
    for a, b in trechos:
        add(_tubo3d(a, b, 0.20, AR, n=9))

    # ---------------------------------------------------------- console de óleo
    add(_caixa(6.20, 10.10, -2.95, -1.95, 0.0, 0.85, OLEO))
    add(_cil("z", 0.0, 0.85, 7.10, -2.45, 0.22, (0.58, 0.46, 0.19), n=14))
    add(_tubo3d((8.60, -2.45, 0.80), (8.60, -2.45, 2.55), 0.09, (0.70, 0.55, 0.22), n=8))
    add(_tubo3d((8.60, -2.45, 2.55), (8.60, -1.45, 2.55), 0.09, (0.70, 0.55, 0.22), n=8))

    # ---------------------------------------------------------- render
    col = Poly3DCollection(Q, facecolors=C, edgecolors="none", linewidths=0.0)
    col.set_zsort("average")
    ax.add_collection3d(col)

    ax.set_xlim(0, 28.2)
    ax.set_ylim(-3.4, 3.4)
    ax.set_zlim(-1.4, 5.6)
    ax.set_box_aspect((3.9, 0.94, 1.0), zoom=1.12)
    ax.view_init(elev=23, azim=-62)

    # ---------------------------------------------------------- rótulos 2D
    def bolha(letra, p3, desloc):
        x2, y2, _ = proj3d.proj_transform(p3[0], p3[1], p3[2], ax.get_proj())
        px, py = ax.transData.transform((x2, y2))
        fx, fy = ax.transAxes.inverted().transform((px, py))
        ax.annotate(
            letra,
            xy=(fx, fy), xycoords="axes fraction",
            xytext=(fx + desloc[0], fy + desloc[1]), textcoords="axes fraction",
            ha="center", va="center", fontsize=9.5, fontweight="bold",
            color="white", zorder=30,
            bbox=dict(boxstyle="circle,pad=0.26", facecolor=NAVY,
                      edgecolor="white", linewidth=1.3),
            arrowprops=dict(arrowstyle="-", color=NAVY, lw=1.0,
                            shrinkA=7, shrinkB=2),
        )

    PONTOS = [
        ("A", (0.88, -2.45, 2.20), (-0.045, 0.105)),
        ("B", (5.30, -0.95, 1.30), (-0.016, -0.120)),
        ("C", (4.55, 0.0, 3.90), (-0.010, 0.120)),
        ("D", (9.40, 0.0, 4.20), (0.015, 0.135)),
        ("E", (14.25, 0.0, 4.20), (0.045, 0.120)),
        ("F", (15.60, 0.0, 4.20), (0.080, 0.115)),
        ("G", (20.15, 0.0, 5.25), (0.115, 0.090)),
        ("H", (24.30, 0.0, 3.60), (0.100, 0.080)),
        ("I", (27.05, 0.0, 4.95), (0.075, 0.080)),
        ("L", (7.10, -2.45, 0.75), (0.030, -0.075)),
    ]
    for letra, p3, d in PONTOS:
        bolha(letra, p3, d)

    # DT
    ax.annotate(
        "GÊMEO DIGITAL\nİ · ṁ_CO₂ · HI\ncalculado de A…I",
        xy=(0.995, 0.335), xycoords="axes fraction",
        ha="right", va="center", fontsize=8.4, color=NAVY, style="italic",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#eef3f9",
                  edgecolor=NAVY, linewidth=1.2, linestyle=(0, (5, 3))),
        zorder=30,
    )

    # título e legenda
    fig.text(0.028, 0.962,
             "Conjunto compressor de parafuso duplo oil-free — vista 3D com pontos de medição",
             fontsize=13.5, color=NAVY, fontweight="bold", ha="left")
    fig.text(0.028, 0.932,
             "Motor, redutor de dois pinhões, estágios LP/HP, intercooler, aftercooler, "
             "secagem PSA, vaso pulmão e header sobre skid único",
             fontsize=8.4, color=GRAY, ha="left")

    itens = [(BLUE, "ar comprimido"), (TEAL, "água de resfriamento"),
             (AMBER, "óleo"), (ORANGE, "energia")]
    for i, (cor, rot) in enumerate(itens):
        x = 0.028 + i * 0.105
        fig.patches.append(plt.Line2D([x, x + 0.020], [0.906, 0.906],
                                      color=cor, lw=4, solid_capstyle="round",
                                      transform=fig.transFigure))
        fig.text(x + 0.024, 0.906, rot, fontsize=7.4, color=GRAY, va="center")

    # ---------------------------------------------------------- gravação
    os.makedirs(OUTDIR, exist_ok=True)
    bx = _bbox_conteudo(fig)

    pdf = os.path.join(OUTDIR, "fig_18_3_conjunto_3d.pdf")
    png = os.path.join(OUTDIR, "fig_18_3_conjunto_3d.png")
    fig.savefig(pdf, dpi=200, bbox_inches=bx, facecolor="white")
    fig.savefig(png, dpi=360, bbox_inches=bx, facecolor="white")
    print("salvo:", pdf)
    print("salvo:", png)

    app_assets = os.path.normpath(
        os.path.join(OUTDIR, "..", "compressor2", "crates", "app", "assets")
    )
    os.makedirs(app_assets, exist_ok=True)
    web = os.path.join(app_assets, "conjunto-3d.png")
    fig.savefig(web, dpi=170, bbox_inches=bx, facecolor="white")
    print("salvo:", web)
    shutil.copyfile(pdf, os.path.join(app_assets, "conjunto-3d.pdf"))
    print("salvo:", os.path.join(app_assets, "conjunto-3d.pdf"))

    plt.close(fig)


if __name__ == "__main__":
    desenhar()
