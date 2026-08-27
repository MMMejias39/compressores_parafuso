"""Gerador de figuras do Volume I (teorias.tex).

Mesmo estilo visual do gen_figuras.py (Volume II): paleta, fontes e dpi
identicos, para que os dois volumes tenham aparencia uniforme.

Convencao de nomes: fig_v1_c<cap>_<n>_<desc>.pdf  (prefixo fig_v1_ separa do
Volume II, que usa fig_<cap>_<n>_<desc>.pdf).

Saida: figuras/
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figuras")
OUTDIR = os.path.normpath(OUTDIR)
os.makedirs(OUTDIR, exist_ok=True)

# ---- Estilo global (identico ao gen_figuras.py do Volume II) ----
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#1a1a1a",
    "axes.grid": True,
    "grid.color": "#dddddd",
    "grid.linewidth": 0.6,
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})

NAVY = "#1f3b57"
BLUE = "#2b6cb0"
RED = "#b73a3a"
GREEN = "#2f7a4f"
GRAY = "#666666"
LGRAY = "#999999"
ORANGE = "#c05621"
PURPLE = "#6b46a0"


def save(fig, name):
    path = os.path.join(OUTDIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("saved", path)


# =====================================================================
# FIG V1-C8.1 - Resposta em frequencia do oscilador de 1 GDL
# Fator de amplificacao e fase vs. razao de frequencias r = w/wn
# =====================================================================
def fig_v1_c8_1_resposta_freq():
    r = np.linspace(0.0, 3.0, 600)
    zetas = [0.05, 0.10, 0.20, 0.50, 0.707, 1.00]
    cores = [RED, ORANGE, BLUE, GREEN, PURPLE, GRAY]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.4, 6.2), sharex=True)

    for z, c in zip(zetas, cores):
        H = 1.0 / np.sqrt((1.0 - r**2)**2 + (2.0 * z * r)**2)
        phi = np.degrees(np.arctan2(2.0 * z * r, 1.0 - r**2))
        ax1.plot(r, H, color=c, lw=1.6,
                 label=rf"$\zeta = {z:g}$")
        ax2.plot(r, phi, color=c, lw=1.6)

    ax1.set_ylabel(r"$|X|\,k/F_0$  (fator de amplificação)")
    ax1.set_yscale("log")
    ax1.set_ylim(0.08, 25)
    ax1.axvline(1.0, color=LGRAY, lw=1.0, ls=(0, (5, 3)))
    ax1.annotate("ressonância\n" r"$r = 1$", xy=(1.0, 12), xytext=(1.28, 13),
                 fontsize=8.5, color=GRAY,
                 arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.0))
    ax1.legend(fontsize=8.5, loc="upper right", framealpha=0.95)

    ax2.set_xlabel(r"razão de frequências  $r = \omega/\omega_n$")
    ax2.set_ylabel(r"defasagem  $\phi$  [°]")
    ax2.set_yticks([0, 45, 90, 135, 180])
    ax2.set_ylim(0, 180)
    ax2.axvline(1.0, color=LGRAY, lw=1.0, ls=(0, (5, 3)))
    ax2.axhline(90, color=LGRAY, lw=0.8, ls=":")

    fig.align_ylabels()
    save(fig, "fig_v1_c8_1_resposta_freq.pdf")


# =====================================================================
# FIG V1-C8.2 - Rotor de Jeffcott: resposta ao desbalanceamento
# Amplitude normalizada (m X / m_u e) e fase vs. rotacao normalizada
# =====================================================================
def fig_v1_c8_2_jeffcott():
    r = np.linspace(0.0, 3.0, 900)
    zetas = [0.10, 0.30]
    cores = [RED, BLUE]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.4, 6.2), sharex=True)

    for z, c in zip(zetas, cores):
        # resposta a desbalanceamento: X = (m_u e / m) r^2 / sqrt((1-r^2)^2+(2 z r)^2)
        Xn = r**2 / np.sqrt((1.0 - r**2)**2 + (2.0 * z * r)**2)
        phi = np.degrees(np.arctan2(2.0 * z * r, 1.0 - r**2))
        ax1.plot(r, Xn, color=c, lw=1.7, label=rf"$\zeta = {z:g}$")
        ax2.plot(r, phi, color=c, lw=1.7)

    ax1.set_ylabel(r"amplitude normalizada  $\dfrac{m\,X}{m_u\,e}$")
    ax1.set_ylim(0, 6)
    ax1.axvline(1.0, color=LGRAY, lw=1.0, ls=(0, (5, 3)))
    ax1.axhline(1.0, color=LGRAY, lw=0.8, ls=":")
    ax1.annotate("velocidade crítica\n" r"$\omega = \omega_{cr}$",
                 xy=(1.0, 5.0), xytext=(1.35, 4.6), fontsize=8.5, color=GRAY,
                 arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.0))
    ax1.annotate(r"$X \to m_u e / m$" + "\n(autocentramento)",
                 xy=(2.6, 1.06), xytext=(1.85, 2.2), fontsize=8.5, color=GRAY,
                 arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.0))
    ax1.legend(fontsize=8.5, loc="upper left", framealpha=0.95)

    ax2.set_xlabel(r"rotação normalizada  $\omega/\omega_{cr}$")
    ax2.set_ylabel(r"defasagem  $\phi$  [°]")
    ax2.set_yticks([0, 45, 90, 135, 180])
    ax2.set_ylim(0, 180)
    ax2.axvline(1.0, color=LGRAY, lw=1.0, ls=(0, (5, 3)))
    ax2.axhline(90, color=LGRAY, lw=0.8, ls=":")
    ax2.annotate("inversão de fase\nna crítica", xy=(1.0, 90),
                 xytext=(1.3, 60), fontsize=8.5, color=GRAY,
                 arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.0))

    fig.align_ylabels()
    save(fig, "fig_v1_c8_2_jeffcott.pdf")


# =====================================================================
# FIG V1-C8.3 - Curva S-N (Basquin) esquematica em log-log
# =====================================================================
def fig_v1_c8_3_curva_sn():
    bf = 0.10  # expoente de Basquin esquematico (ordem tipica de acos)
    # Ancoras esquematicas: sigma_a = 0.9 S_ut em N=1; joelho em N=1e6
    N_knee = 1.0e6
    s_ut_rel = 1.0           # tensao normalizada por S_ut
    s_a_1 = 0.9 * s_ut_rel   # em N = 1 ciclo
    s_e = s_a_1 * N_knee**(-bf)  # limite de resistencia a fadiga (joelho)

    N1 = np.logspace(0, np.log10(N_knee), 400)
    sig1 = s_a_1 * N1**(-bf)
    N2 = np.logspace(np.log10(N_knee), 8, 100)
    sig2 = np.full_like(N2, s_e)

    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.loglog(N1, sig1, color=NAVY, lw=2.0, label="regime de vida finita (Basquin)")
    ax.loglog(N2, sig2, color=GREEN, lw=2.0,
              label="limite de resistência (vida infinita)")

    ax.axvline(1.0e3, color=LGRAY, lw=0.8, ls=":")
    ax.annotate("baixo ciclo\n(deformação plástica)", xy=(2.0e1, 0.58),
                fontsize=8.5, color=GRAY, ha="center")
    ax.annotate("alto ciclo\n(elástico, Basquin)", xy=(4.0e4, 0.58),
                fontsize=8.5, color=GRAY, ha="center")
    ax.annotate(r"joelho  $N \approx 10^6$", xy=(N_knee, s_e),
                xytext=(4.0e6, 0.36), fontsize=8.5, color=GRAY,
                arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.0))

    # ilustracao da regra de Miner: um ponto de operacao (n_i ciclos a sigma_i)
    ax.loglog([1.0e4], [0.42], marker="o", ms=6, color=RED, zorder=5)
    ax.annotate(r"$(n_i, \sigma_i)$: dano $n_i/N_i$",
                xy=(1.0e4, 0.42), xytext=(1.6e3, 0.30), fontsize=8.5,
                color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))

    ax.set_xlabel(r"vida  $N_f$  [ciclos]")
    ax.set_ylabel(r"amplitude de tensão  $\sigma_a$  (normalizada)")
    ax.set_ylim(0.17, 1.0)
    ax.legend(fontsize=8.5, loc="lower left", framealpha=0.95)
    save(fig, "fig_v1_c8_3_curva_sn.pdf")


if __name__ == "__main__":
    fig_v1_c8_1_resposta_freq()
    fig_v1_c8_2_jeffcott()
    fig_v1_c8_3_curva_sn()
