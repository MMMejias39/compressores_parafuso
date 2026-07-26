import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, FancyBboxPatch, Wedge
import os

OUTDIR = "/home/mejias/Documentos/Compressores/figuras"
os.makedirs(OUTDIR, exist_ok=True)

# ---- Estilo global (limpo, apropriado para documento tecnico impresso) ----
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

def save(fig, name):
    path = os.path.join(OUTDIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("saved", path)

# =====================================================================
# FIG 2.1 - Esquema dos rotores helicoidais (macho 4 lobulos / femea 6)
# =====================================================================
def fig_rotores():
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.set_aspect("equal")
    ax.axis("off")

    def lobed_circle(center, R, n_lobes, lobe_depth, phase=0.0, **kw):
        theta = np.linspace(0, 2*np.pi, 800)
        r = R + lobe_depth * np.cos(n_lobes * theta + phase)
        x = center[0] + r * np.cos(theta)
        y = center[1] + r * np.sin(theta)
        ax.fill(x, y, **kw)
        return x, y

    # Rotor macho (4 lobulos), a esquerda -- centros aproximados para meshing visual
    lobed_circle((-1.42, 0), 1.05, 4, 0.34, phase=0.0,
                 facecolor="#dbe7f2", edgecolor=NAVY, linewidth=1.8, zorder=4)
    # Rotor femea (6 cavidades), a direita, engrenado (leve sobreposicao)
    lobed_circle((1.42, 0), 1.05, 6, 0.24, phase=np.pi/6,
                 facecolor="#f2e3d5", edgecolor="#8a5a2b", linewidth=1.8, zorder=3, alpha=0.92)

    # Carcaca (contorno tracejado em 8)
    for cx, sgn in [(-1.42, -1), (1.42, 1)]:
        circ = Circle((cx, 0), 1.42, fill=False, ls=(0, (5, 3)), lw=1.1, edgecolor=GRAY, zorder=1)
        ax.add_patch(circ)

    ax.annotate("Rotor macho\n(4 lóbulos)", xy=(-1.42, -1.72), ha="center", fontsize=9.5, color=NAVY, fontweight="bold")
    ax.annotate("Rotor fêmea\n(6 cavidades)", xy=(1.42, -1.72), ha="center", fontsize=9.5, color="#8a5a2b", fontweight="bold")

    ax.annotate("", xy=(-0.95, 1.35), xytext=(-0.20, 1.35),
                arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.4))
    ax.annotate(r"$\omega_{mot}$", xy=(-0.58, 1.52), ha="center", fontsize=9, color=NAVY)

    ax.annotate("", xy=(0.95, 1.35), xytext=(0.20, 1.35),
                arrowprops=dict(arrowstyle="<-", color="#8a5a2b", lw=1.4))

    ax.annotate("Linha de\nengrenamento", xy=(0, -0.25), xytext=(0, -1.15),
                ha="center", fontsize=8.3, color=GRAY,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8, ls=":"))

    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-2.3, 2.1)
    save(fig, "fig_2_1_rotores.pdf")

# =====================================================================
# FIG 2.2 - Diagrama de blocos da arquitetura do sistema
# =====================================================================
def fig_arquitetura():
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.axis("off")

    w, h = 2.35, 1.5
    gap = 0.30
    x0 = 0.2
    boxes = [
        (x0 + 0*(w+gap), "Geração", "Compressor de\nparafuso + VSD"),
        (x0 + 1*(w+gap), "Tratamento", "Aftercooler +\nseparador + PSA"),
        (x0 + 2*(w+gap), "Armazenamento", "Vaso pulmão\n(header)"),
        (x0 + 3*(w+gap), "Gestão", "Gêmeo Digital\n(EKF/VAE/PIML)"),
    ]
    y_bottom = 1.1
    for x, title, sub in boxes:
        box = FancyBboxPatch((x, y_bottom), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                              facecolor="#eaf1f8", edgecolor=NAVY, linewidth=1.6)
        ax.add_patch(box)
        title_fs = 10.2 if len(title) <= 10 else 8.8
        ax.text(x + w/2, y_bottom + h - 0.34, title, ha="center", va="center",
                fontsize=title_fs, fontweight="bold", color=NAVY)
        ax.text(x + w/2, y_bottom + 0.55, sub, ha="center", va="center", fontsize=8.3, color="#333333")

    for i in range(3):
        x_prev_right = boxes[i][0] + w
        x_next_left = boxes[i+1][0]
        ax.annotate("", xy=(x_next_left, y_bottom + h/2), xytext=(x_prev_right, y_bottom + h/2),
                    arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.6))

    x_first_c = boxes[0][0] + w/2
    x_last_c = boxes[-1][0] + w/2
    ax.annotate("", xy=(x_first_c, y_bottom - 0.05), xytext=(x_last_c, y_bottom - 0.05),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.3, ls="--",
                                 connectionstyle="arc3,rad=-0.16"))
    ax.text((x_first_c + x_last_c)/2, y_bottom - 1.0, "realimentação de dados e ações de controle",
            ha="center", fontsize=8.3, color=RED, style="italic")

    ax.set_xlim(-0.15, boxes[-1][0] + w + 0.15)
    ax.set_ylim(y_bottom - 1.3, y_bottom + h + 0.35)
    ax.set_aspect("equal")

    save(fig, "fig_2_2_arquitetura.pdf")

# =====================================================================
# FIG 5.1 - Perdas por Sub/Sobrecompressao (V_i)  Eq 5.8 / 5.9
# =====================================================================
def fig_vi_perdas():
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    P1 = 1.0
    Vi = 4.0
    n = 1.30
    pi_i = Vi**n
    pi_range = np.linspace(pi_i*0.55, pi_i*1.55, 400)
    P2 = pi_range * P1
    Pi_internal = P1 * pi_i
    V2 = 1.0

    dW_sub = np.where(pi_range > pi_i, V2*(P2 - Pi_internal), np.nan)
    dW_sobre = np.where(pi_range < pi_i, V2*(Pi_internal - P2), np.nan)

    ax.plot(pi_range/pi_i, dW_sub, color=RED, lw=2.2, label=r"Subcompressão $\Delta \dot{W}_{sub}$ ($\pi>\pi_i$)")
    ax.plot(pi_range/pi_i, dW_sobre, color=BLUE, lw=2.2, label=r"Sobrecompressão $\Delta \dot{W}_{sobre}$ ($\pi<\pi_i$)")
    ax.axvline(1.0, color=GREEN, lw=1.6, ls="--")
    ax.annotate(r"Ponto de projeto ($\pi = \pi_i$)" "\nperda mínima", xy=(1.0, 0.02), xytext=(1.05, 0.55),
                fontsize=8.3, color=GREEN,
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.0))

    ax.set_xlabel(r"Razão $\pi \, / \, \pi_i$  (pressão de rede sobre pressão interna ideal)")
    ax.set_ylabel(r"Perda de trabalho $\Delta \dot{W}$  [un. relativa]")
    ax.set_title("Perdas termodinâmicas por descasamento de $V_i$", fontsize=10.5, color=NAVY)
    ax.legend(fontsize=8.3, frameon=False, loc="upper center")
    ax.set_ylim(0, None)
    save(fig, "fig_5_1_vi_perdas.pdf")

# =====================================================================
# FIG 7.1 - Curva de viscosidade de Vogel  Eq 7.2
# =====================================================================
def fig_vogel():
    fig, ax = plt.subplots(figsize=(5.4, 3.5))
    a, b, c = 0.06, 850.0, 180.0  # constantes ilustrativas (mPa.s, K)
    T = np.linspace(300, 380, 300)  # Kelvin
    mu = a * np.exp(b/(T - c))

    ax.plot(T - 273.15, mu, color=NAVY, lw=2.3)
    ax.set_xlabel(r"Temperatura do óleo, $T$  [$^{\circ}$C]")
    ax.set_ylabel(r"Viscosidade dinâmica, $\mu(T)$  [mPa$\cdot$s] (ilustrativo)")
    ax.set_title(r"Equação de Vogel: $\mu(T) = a \cdot \exp\left(\dfrac{b}{T-c}\right)$", fontsize=10, color=NAVY)
    ax.axhspan(0, mu.min()*3, color="#fdf0e3", alpha=0.0)
    ax.annotate("Zona de risco de\nfilme insuficiente\n(alta T, baixa $\\mu$)", xy=(T[-1]-273.15, mu[-1]),
                xytext=(T[-1]-273.15-28, mu[0]*0.45), fontsize=8, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.9))
    save(fig, "fig_7_1_vogel.pdf")

# =====================================================================
# FIG 8.1 - Esquema cinematico da caixa multiplicadora (bull gear + pinhoes)
# =====================================================================
def fig_gearbox():
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.set_aspect("equal")
    ax.axis("off")

    bull = Circle((0, 0), 1.3, facecolor="#eaf1f8", edgecolor=NAVY, lw=1.8, zorder=3)
    ax.add_patch(bull)
    ax.text(0, 0, "Bull Gear\n(motor)", ha="center", va="center", fontsize=8.6, color=NAVY, fontweight="bold")

    pin_lp = Circle((1.85, 1.15), 0.62, facecolor="#f2e3d5", edgecolor="#8a5a2b", lw=1.6, zorder=3)
    ax.add_patch(pin_lp)
    ax.text(1.85, 1.15, "Pinhão\nLP", ha="center", va="center", fontsize=8, color="#8a5a2b", fontweight="bold")

    pin_hp = Circle((1.85, -1.15), 0.48, facecolor="#e3f2e6", edgecolor=GREEN, lw=1.6, zorder=3)
    ax.add_patch(pin_hp)
    ax.text(1.85, -1.15, "Pinhão\nHP", ha="center", va="center", fontsize=7.6, color=GREEN, fontweight="bold")

    sync = Circle((-1.7, 0.75), 0.32, facecolor="#f5e3ea", edgecolor="#8a2b5a", lw=1.3, zorder=3)
    ax.add_patch(sync)
    ax.text(-1.7, 0.75, "Timing", ha="center", va="center", fontsize=6.5, color="#8a2b5a")

    ax.annotate("", xy=(0.62, 0.38), xytext=(1.29, 0.85),
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8, ls=":"))
    ax.annotate("", xy=(0.66, -0.38), xytext=(1.42, -0.75),
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8, ls=":"))

    ax.annotate(r"$N_{macho,LP} = N_{mot} \cdot Z_{bull}/Z_{pin,LP}$", xy=(1.85, 1.85), ha="center", fontsize=7.6, color="#8a5a2b")
    ax.annotate(r"$N_{macho,HP} = N_{mot} \cdot Z_{bull}/Z_{pin,HP}$", xy=(1.85, -1.95), ha="center", fontsize=7.6, color=GREEN)

    ax.annotate("", xy=(-0.6, 0.4), xytext=(-1.35, 0.65),
                arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.3,
                                 connectionstyle="arc3,rad=0.3"))
    ax.text(-1.05, 1.02, r"$\tau_{mot}$", fontsize=9, color=NAVY)

    ax.set_xlim(-2.7, 3.0)
    ax.set_ylim(-2.6, 2.6)
    save(fig, "fig_8_1_gearbox.pdf")

# =====================================================================
# FIG 8.2 - Diagrama de Campbell simplificado
# =====================================================================
def fig_campbell():
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    N = np.linspace(0, 12000, 300)  # RPM
    f1 = N/60.0
    f2 = 2*N/60.0
    Z = 6
    fgmf = Z*N/60.0

    ax.plot(N, f1, color=BLUE, lw=1.8, label=r"$1\times$ RPM")
    ax.plot(N, f2, color=GREEN, lw=1.8, label=r"$2\times$ RPM")
    ax.plot(N, fgmf, color="#8a5a2b", lw=1.8, label=r"$GMF$ ($Z=6$)")

    wcr_hz = 340.0
    ax.axhline(wcr_hz, color=RED, lw=2.0, ls="--", label=r"Velocidade crítica $\omega_{cr}$")

    op_lo, op_hi = 7500, 10200
    ax.axvspan(op_lo, op_hi, color="#dbe7f2", alpha=0.55, label="Faixa de operação (VSD)")

    margin_lo = wcr_hz*0.8
    margin_hi = wcr_hz*1.2
    ax.axhspan(margin_lo, margin_hi, color=RED, alpha=0.08)

    ax.set_xlabel("Rotação do eixo, $N$ [RPM]")
    ax.set_ylabel("Frequência de excitação [Hz]")
    ax.set_title("Diagrama de Campbell — cruzamento de excitações com $\\omega_{cr}$", fontsize=10, color=NAVY)
    ax.legend(fontsize=7.6, frameon=False, loc="upper left")
    ax.set_xlim(0, 12000)
    ax.set_ylim(0, 700)
    save(fig, "fig_8_2_campbell.pdf")

# =====================================================================
# FIG 8.3 - Vida de rolamento L10h vs carga (lei de potencia)
# =====================================================================
def fig_l10h():
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    C = 45000.0  # N, capacidade dinamica ilustrativa
    p = 3.0
    N_rot = 12000.0
    P = np.linspace(3000, 30000, 300)
    L10h = (C/P)**p * 1e6/(60*N_rot)

    ax.plot(P/1000, L10h, color=NAVY, lw=2.3)
    ax.set_yscale("log")
    ax.set_xlabel("Carga equivalente, $P$ [kN]")
    ax.set_ylabel(r"Vida nominal, $L_{10h}$ [horas] (escala log)")
    ax.set_title(r"Sensibilidade da vida do rolamento à carga ($L_{10h} \propto P^{-3}$)", fontsize=10, color=NAVY)

    for frac, lbl in [(0.5, "50% da carga\nnominal"), (1.0, "carga\nnominal")]:
        Px = frac*12000
        Lx = (C/Px)**p * 1e6/(60*N_rot)
        ax.plot([Px/1000], [Lx], "o", color=RED, ms=5)
        ax.annotate(lbl, xy=(Px/1000, Lx), xytext=(Px/1000+2.5, Lx*1.4),
                    fontsize=7.6, color=RED)
    save(fig, "fig_8_3_l10h.pdf")

# =====================================================================
# FIG 9.1 - Eficiencia volumetrica vs folga  Eq 9.3
# =====================================================================
def fig_etav():
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    K = 45.0
    L = 0.5  # comprimento de referência do rotor [m]
    delta = np.linspace(0, 500e-6, 300)  # folga radial/flanco [m], até 500 micrometros
    for pr, style in [(3, "-"), (6, "--"), (9, ":")]:
        etav = 1 - K*(delta/L)*np.sqrt(pr)
        ax.plot(delta*1e6, etav, lw=2.0, ls=style, color=NAVY, label=fr"$P_2/P_1={pr}$")

    ax.set_xlabel(r"Folga, $\delta$ [$\mu$m] (ilustrativo, $L=0{,}5$ m)")
    ax.set_ylabel(r"Eficiência volumétrica, $\eta_v$")
    ax.set_title(r"$\eta_v = 1 - K(\delta/L)\sqrt{P_2/P_1}$ — efeito do desgaste de folga", fontsize=10, color=NAVY)
    ax.legend(fontsize=8.3, frameon=False)
    ax.set_ylim(0.5, 1.02)
    save(fig, "fig_9_1_etav.pdf")

# =====================================================================
# FIG 10.1 - Perfil de temperatura no trocador (LMTD, contracorrente)
# =====================================================================
def fig_lmtd():
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    x = np.linspace(0, 1, 200)
    Th_in, Th_out = 95.0, 42.0
    Tc_in, Tc_out = 25.0, 55.0
    Th = Th_in + (Th_out - Th_in)*x
    Tc = Tc_out + (Tc_in - Tc_out)*x  # contracorrente: Tc_in na saida x=1

    ax.plot(x, Th, color=RED, lw=2.2, label="Ar comprimido (quente)")
    ax.plot(x, Tc, color=BLUE, lw=2.2, label="Água de resfriamento (fria)")
    ax.fill_between(x, Th, Tc, color="#f5e6b8", alpha=0.5)

    dT1 = Th_in - Tc_in
    dT2 = Th_out - Tc_out
    ax.annotate("", xy=(0, Tc_in), xytext=(0, Th_in), arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1))
    ax.text(0.02, (Th_in+Tc_in)/2, r"$\Delta T_1$", fontsize=8.5, color=GRAY)
    ax.annotate("", xy=(1, Tc_out), xytext=(1, Th_out), arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1))
    ax.text(0.90, (Th_out+Tc_out)/2, r"$\Delta T_2$", fontsize=8.5, color=GRAY)

    ax.set_xlabel("Posição relativa ao longo do trocador")
    ax.set_ylabel(r"Temperatura [$^{\circ}$C]")
    ax.set_title(r"Perfil de temperatura — origem física da $\Delta T_{lm}$", fontsize=10, color=NAVY)
    ax.legend(fontsize=8.3, frameon=False, loc="center right")
    ax.set_xticks([])
    save(fig, "fig_10_1_lmtd.pdf")

# =====================================================================
# FIG 10.2 - Curva de pressao de saturacao (Arden Buck)
# =====================================================================
def fig_psat():
    fig, ax = plt.subplots(figsize=(5.3, 3.5))
    T = np.linspace(0, 80, 300)
    Psat = 0.61121*np.exp((18.678 - T/234.5)*(T/(257.14+T)))
    ax.plot(T, Psat, color=NAVY, lw=2.3)
    ax.set_yscale("log")
    ax.set_xlabel(r"Temperatura, $T$ [$^{\circ}$C]")
    ax.set_ylabel(r"$P_{sat}(T)$ [kPa] (escala log)")
    ax.set_title("Correlação de Arden Buck — pressão de saturação do vapor", fontsize=10, color=NAVY)
    for Tx in [25, 45, 65]:
        Px = 0.61121*np.exp((18.678 - Tx/234.5)*(Tx/(257.14+Tx)))
        ax.plot([Tx], [Px], "o", color=RED, ms=4.5)
        ax.annotate(f"{Px:.1f} kPa", xy=(Tx, Px), xytext=(Tx+2, Px*0.6), fontsize=7.6, color=RED)
    save(fig, "fig_10_2_psat.pdf")

# =====================================================================
# FIG 15.1 - Esquema das torres PSA (adsorcao / regeneracao)
# =====================================================================
def fig_psa():
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)

    for x, label, color, state in [(1.8, "Torre A", "#dbe7f2", "ADSORVENDO"), (6.2, "Torre B", "#f2e3d5", "REGENERANDO")]:
        tower = FancyBboxPatch((x, 0.8), 2.0, 3.0, boxstyle="round,pad=0.02,rounding_size=0.15",
                                facecolor=color, edgecolor=NAVY, linewidth=1.6)
        ax.add_patch(tower)
        # leito representado por hachura
        for yy in np.linspace(1.1, 3.5, 9):
            ax.plot([x+0.15, x+1.85], [yy, yy], color="#ffffff", lw=3, alpha=0.6, zorder=2)
            ax.plot([x+0.15, x+1.85], [yy, yy], color=NAVY, lw=0.6, alpha=0.5, zorder=3)
        ax.text(x+1.0, 4.15, label, ha="center", fontsize=9.5, fontweight="bold", color=NAVY)
        ax.text(x+1.0, 1.05, state, ha="center", fontsize=8.3,
                color=GREEN if state=="ADSORVENDO" else RED, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.75))

    ax.annotate("", xy=(1.8+1.0, 3.8+0.35), xytext=(1.8+1.0, 3.8),
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.8))
    ax.text(1.8+1.0, 4.5, "ar seco\n(saída)", ha="center", fontsize=7.6, color=BLUE)

    ax.annotate("", xy=(1.8+1.0, 0.8), xytext=(1.8+1.0, 0.3),
                arrowprops=dict(arrowstyle="<-", color=NAVY, lw=1.8))
    ax.text(1.8+1.0, -0.05, "ar úmido\n(entrada)", ha="center", fontsize=7.6, color=NAVY)

    ax.annotate("", xy=(6.2+1.0, 0.3), xytext=(6.2+1.0, 0.8),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.6, ls="--"))
    ax.text(6.2+1.0, -0.05, r"purga $\dot{m}_{purge}$" "\n(exaustão)", ha="center", fontsize=7.6, color=RED)

    ax.annotate("", xy=(6.2-0.15, 2.3), xytext=(1.8+2.15, 2.3),
                arrowprops=dict(arrowstyle="->", color="#8a5a2b", lw=1.4, ls=":",
                                 connectionstyle="arc3,rad=-0.35"))
    ax.text(4.0, 3.55, "parte do ar seco\nalimenta a purga", ha="center", fontsize=7.2, color="#8a5a2b")

    save(fig, "fig_15_1_psa.pdf")

# =====================================================================
# FIG 15.2 - Capacidade de adsorcao dinamica q_d(t)  Eq 15.1
# =====================================================================
def fig_adsorcao():
    fig, ax = plt.subplots(figsize=(5.4, 3.5))
    t = np.linspace(0, 1, 300)  # t_ads/t_res
    qeq = 1.0
    for k, style in [(0.5, "-"), (1.5, "--"), (3.0, ":")]:
        qd = qeq*np.exp(-k*t)
        ax.plot(t, qd, lw=2.0, ls=style, color=NAVY, label=fr"$k_{{ads}}={k}$")
    ax.set_xlabel(r"Tempo relativo de adsorção, $t_{ads}/t_{res}$")
    ax.set_ylabel(r"Capacidade dinâmica, $q_d \, / \, q_{eq}$")
    ax.set_title(r"$q_d = q_{eq}\exp(-k_{ads}\, t_{ads}/t_{res})$ — saturação do leito", fontsize=10, color=NAVY)
    ax.legend(fontsize=8.3, frameon=False)
    save(fig, "fig_15_2_adsorcao.pdf")

# =====================================================================
# FIG 20.1 - Curva S-N de Basquin + Regra de Miner (conceitual)
# =====================================================================
def fig_basquin():
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    C = 1e12
    bf = -9.0
    N = np.logspace(3, 8, 300)
    sigma = (C/N)**(-1/bf) if False else (C/N)**(1.0/(-bf))
    # sigma_i^bf * N = C  => sigma = (C/N)^(1/bf), bf negative slope typical -> use magnitude
    b = 9.0
    sigma = (C/N)**(1.0/b)

    ax.plot(N, sigma, color=NAVY, lw=2.2, label="Curva S-N (Basquin)")
    ax.set_xscale("log")
    ax.set_yscale("log")

    Ns = [2e4, 3e5, 4e6]
    for Nx in Ns:
        sx = (C/Nx)**(1.0/b)
        ax.plot([Nx], [sx], "o", color=RED, ms=5)
    ax.annotate(r"histórico de ciclos" "\n" r"$n_i$ observados em $\sigma_i$" "\n" r"$\to D=\sum n_i/N_i(\sigma_i)$",
                xy=(Ns[1], (C/Ns[1])**(1.0/b)), xytext=(Ns[1]*3, (C/Ns[1])**(1.0/b)*2.2),
                fontsize=7.6, color=RED, arrowprops=dict(arrowstyle="->", color=RED, lw=0.9))

    ax.set_xlabel(r"Ciclos até a falha, $N_i$ (escala log)")
    ax.set_ylabel(r"Amplitude de tensão, $\sigma_i$ (escala log)")
    ax.set_title(r"$\sigma_i^{\,b_f} \cdot N_i = C$ — base da Regra de Miner", fontsize=10, color=NAVY)
    save(fig, "fig_20_1_basquin.pdf")

# =====================================================================
# FIG 21.1 - Ciclo de predicao-correcao do EKF (conceitual)
# =====================================================================
def fig_ekf():
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    k = np.arange(0, 7)
    rng = np.random.default_rng(7)
    true_state = 50 + 3*np.sin(k/2)
    meas = true_state + rng.normal(0, 2.6, size=len(k))
    pred_unc = 2.0 + 0.9*np.ones(len(k))
    corr_unc = 0.7*np.ones(len(k))

    ax.plot(k, true_state, color=GREEN, lw=1.8, label="Estado real (não observado)")
    ax.scatter(k, meas, color=GRAY, marker="x", s=45, label=r"Medições ruidosas $z_k$", zorder=4)

    est = np.zeros(len(k))
    est[0] = meas[0]
    for i in range(1, len(k)):
        est[i] = 0.55*meas[i] + 0.45*est[i-1]

    ax.plot(k, est, color=NAVY, lw=2.2, marker="o", ms=4, label=r"Estimativa EKF $\hat{x}_{k|k}$")
    ax.fill_between(k, est-corr_unc*2, est+corr_unc*2, color=NAVY, alpha=0.15,
                     label=r"Intervalo de confiança ($P_{k|k}$)")

    ax.set_xlabel(r"Passo de tempo discreto, $k$")
    ax.set_ylabel("Variável de estado (ex.: folga residual)")
    ax.set_title("Ciclo de predição-correção do EKF ao longo do tempo", fontsize=10, color=NAVY)
    ax.legend(fontsize=7.6, frameon=False, loc="upper left")
    save(fig, "fig_21_1_ekf.pdf")

# =====================================================================
# FIG 3.1 - Par de rotores em 3D (varredura helicoidal do perfil da
# Fig. 2.2). O perfil 2D vem de rotor_mesh_commons.svg (= Asymmetric
# Screw Compressor Rotor Mesh, Slashme, Wikimedia Commons, CC BY-SA 4.0);
# a extrusao 3D e' original. Obra derivada -> manter credito no caption.
# =====================================================================

# Geometria do SVG (coordenadas da layer1): centros e num. de lobulos
_C_M = np.array([-116.73804, 507.60663])   # rotor macho (5 lobulos)
_C_F = np.array([321.82086, 507.92651])    # rotor femea (6 cavidades)
_Z_M, _Z_F = 5, 6

def _svg_lobos(path_svg):
    """Extrai os dois paths de lobulo do SVG e os converte em pontos."""
    import re
    svg = open(path_svg).read()
    ds = re.findall(r'\bd="([^"]*)"', svg)

    def parse(d):
        tokens = re.findall(r'[mc]|-?\d+\.?\d*(?:e-?\d+)?', d, re.I)
        pts, i, cur, mode = [], 0, np.zeros(2), None
        while i < len(tokens):
            t = tokens[i]
            if t in "mcMC":
                mode = t; i += 1; continue
            if mode == "m":
                cur = cur + [float(tokens[i]), float(tokens[i+1])]
                pts.append(cur.copy()); i += 2; mode = "l"
            elif mode == "c":
                p0 = cur
                p1 = cur + [float(tokens[i]),   float(tokens[i+1])]
                p2 = cur + [float(tokens[i+2]), float(tokens[i+3])]
                p3 = cur + [float(tokens[i+4]), float(tokens[i+5])]
                for s in np.linspace(0, 1, 40)[1:]:
                    pts.append(((1-s)**3)*p0 + 3*s*(1-s)**2*p1
                               + 3*s**2*(1-s)*p2 + s**3*p3)
                cur = p3; i += 6
            else:
                raise ValueError(f"comando SVG inesperado: {mode}")
        return np.array(pts)

    return parse(ds[0]), parse(ds[1])  # (macho/vermelho, femea/magenta)

def _perfil_fechado(lobo, center, n_lobos, n_pontos=220):
    """Fecha o contorno replicando o lobulo por rotacao e reamostra."""
    def rot(pts, ang):
        c, s = np.cos(ang), np.sin(ang)
        return (pts - center) @ np.array([[c, -s], [s, c]]).T + center
    prof = np.vstack([rot(lobo, 2*np.pi*k/n_lobos) for k in range(n_lobos)])
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(prof, axis=0), axis=1))]
    s = np.linspace(0, d[-1], n_pontos, endpoint=False)
    return np.column_stack([np.interp(s, d, prof[:, 0]),
                            np.interp(s, d, prof[:, 1])])

def fig_parafuso3d():
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    N_Z = 90                            # fatias axiais
    WRAP_M = np.deg2rad(300.0)          # torcao total do macho
    WRAP_F = -WRAP_M * _Z_M / _Z_F      # femea contrarrotativa (5:6)
    LUZ = np.array([-0.45, -0.6, 0.66]); LUZ /= np.linalg.norm(LUZ)
    COR_M = (0.72, 0.35, 0.32)          # tons casados com a Fig. 2.2
    COR_F = (0.62, 0.40, 0.62)
    CINZA = (0.62, 0.62, 0.65)

    svg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "rotor_mesh_commons.svg")
    lobo_m, lobo_f = _svg_lobos(svg)
    pm = _perfil_fechado(lobo_m, _C_M, _Z_M)
    pf = _perfil_fechado(lobo_f, _C_F, _Z_F)
    pm[:, 1] *= -1; pf[:, 1] *= -1      # y do SVG cresce para baixo
    cm = _C_M * [1, -1]; cf = _C_F * [1, -1]
    R_M = np.max(np.hypot(*(pm - cm).T))
    L = 2.9 * R_M                       # comprimento axial (L/D ~ 1.45)

    quads, cores = [], []

    def add(poly, cor):                 # eixo axial no X do plot
        quads.append(poly[:, [2, 0, 1]]); cores.append(cor)

    def sombra(normal, cor, amb=0.32):
        lam = abs(np.dot(normal, LUZ))
        return np.clip(np.array(cor) * (amb + (1-amb)*lam), 0, 1)

    for prof, cen, wrap, cor in ((pm, cm, WRAP_M, COR_M),
                                 (pf, cf, WRAP_F, COR_F)):
        rel = prof - cen
        r = np.hypot(rel[:, 0], rel[:, 1])
        a0 = np.arctan2(rel[:, 1], rel[:, 0])
        n_p = len(prof)
        zs = np.linspace(0, L, N_Z)
        grid = np.empty((N_Z, n_p, 3))
        for i, z in enumerate(zs):
            a = a0 + wrap * z / L
            grid[i, :, 0] = cen[0] + r*np.cos(a)
            grid[i, :, 1] = cen[1] + r*np.sin(a)
            grid[i, :, 2] = z
        # superficie helicoidal
        for i in range(N_Z - 1):
            for j in range(n_p):
                j2 = (j + 1) % n_p
                q = np.array([grid[i, j], grid[i, j2],
                              grid[i+1, j2], grid[i+1, j]])
                nv = np.cross(q[1]-q[0], q[3]-q[0])
                nn = np.linalg.norm(nv)
                if nn < 1e-12:
                    continue
                add(q, sombra(nv/nn, cor))
        # tampas: leque de triangulos (perfil e' estrelado em rel. ao eixo)
        for i in (0, N_Z - 1):
            c3 = np.array([cen[0], cen[1], zs[i]])
            cor_tampa = sombra(np.array([0, 0, 1.0]), cor, amb=0.40)
            for j in range(n_p):
                add(np.array([c3, grid[i, j], grid[i, (j+1) % n_p]]),
                    cor_tampa)
        # tocos de eixo nas duas extremidades
        r_eixo = 0.55 * r.min()
        ang = np.linspace(0, 2*np.pi, 48, endpoint=False)
        for z0, z1, zcap in ((-0.22*L, 0.0, -0.22*L), (L, 1.22*L, 1.22*L)):
            for j in range(48):
                j2 = (j + 1) % 48
                q = np.array([
                    [cen[0]+r_eixo*np.cos(ang[j]),  cen[1]+r_eixo*np.sin(ang[j]),  z0],
                    [cen[0]+r_eixo*np.cos(ang[j2]), cen[1]+r_eixo*np.sin(ang[j2]), z0],
                    [cen[0]+r_eixo*np.cos(ang[j2]), cen[1]+r_eixo*np.sin(ang[j2]), z1],
                    [cen[0]+r_eixo*np.cos(ang[j]),  cen[1]+r_eixo*np.sin(ang[j]),  z1]])
                nv = np.array([np.cos((ang[j]+ang[j2])/2),
                               np.sin((ang[j]+ang[j2])/2), 0.0])
                add(q, sombra(nv, CINZA))
            c3 = np.array([cen[0], cen[1], zcap])
            cor_tampa = sombra(np.array([0, 0, 1.0]), CINZA, amb=0.40)
            for j in range(48):
                j2 = (j + 1) % 48
                add(np.array([c3,
                              [cen[0]+r_eixo*np.cos(ang[j]),  cen[1]+r_eixo*np.sin(ang[j]),  zcap],
                              [cen[0]+r_eixo*np.cos(ang[j2]), cen[1]+r_eixo*np.sin(ang[j2]), zcap]]),
                    cor_tampa)

    fig = plt.figure(figsize=(11, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(
        quads, facecolors=cores, edgecolors=cores, linewidths=0.15,
        zsort="average", rasterized=True))
    allpts = np.vstack([q.reshape(-1, 3) for q in quads])
    for setl, dim in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), range(3)):
        lo, hi = allpts[:, dim].min(), allpts[:, dim].max()
        pad = 0.05 * (hi - lo)
        setl(lo - pad, hi + pad)
    ax.set_box_aspect(tuple(np.ptp(allpts[:, d]) for d in range(3)))
    ax.view_init(elev=22, azim=-155)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    save(fig, "fig_3_1_parafuso3d.pdf")
    # eixos 3D do matplotlib deixam margens brancas grandes -> pdfcrop
    import subprocess
    pdf = os.path.join(OUTDIR, "fig_3_1_parafuso3d.pdf")
    subprocess.run(["pdfcrop", "--margins", "6", pdf, pdf],
                   check=True, capture_output=True)
    print("cropped", pdf)

# =====================================================================
# FIG 2.3 - Conjunto completo em 3D: motor -> acoplamento -> gearbox ->
# estagio LP -> intercooler -> estagio HP -> saida. Reaproveita a mesma
# geometria helicoidal da Fig. 3.1 (perfil derivado do SVG CC BY-SA, ver
# nota acima) para os dois pares de rotores, em escalas diferentes
# (LP maior, HP menor). Motor/gearbox/tubulacao sao primitivas simples
# (cilindros e caixas) -- esquema ilustrativo, nao um desenho de projeto.
# =====================================================================

_LUZ3D = np.array([-0.45, -0.6, 0.66])
_LUZ3D = _LUZ3D / np.linalg.norm(_LUZ3D)

def _sombra3d(normal, cor, amb=0.35):
    lam = abs(np.dot(normal, _LUZ3D))
    return np.clip(np.array(cor, dtype=float) * (amb + (1 - amb) * lam), 0, 1)

def _caixa_quads(x0, x1, y0, y1, z0, z1, cor, amb=0.35):
    """Caixa (paralelepipedo) alinhada aos eixos globais, com sombreamento
    plano por face (uma cor por face, conforme a normal)."""
    faces = [
        ([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]], (0, 0, -1)),
        ([[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], (0, 0, 1)),
        ([[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], (0, -1, 0)),
        ([[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], (0, 1, 0)),
        ([[x0, y0, z0], [x0, y1, z0], [x0, y1, z1], [x0, y0, z1]], (-1, 0, 0)),
        ([[x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]], (1, 0, 0)),
    ]
    quads, cores = [], []
    for poly, n in faces:
        quads.append(np.array(poly, dtype=float))
        cores.append(_sombra3d(np.array(n, dtype=float), cor, amb))
    return quads, cores

def _cil_quads(eixo, lo, hi, c1, c2, r, cor, n_seg=28, amb=0.35, tampas=True):
    """Cilindro circular reto alinhado a um dos eixos globais ('x','y','z'),
    de `lo` a `hi` nesse eixo, com o eixo transversal centrado em (c1, c2)
    (nas duas outras coordenadas, em ordem ciclica x->y->z->x)."""
    ang = np.linspace(0, 2 * np.pi, n_seg, endpoint=False)
    quads, cores = [], []

    def ponto(ax_val, c1v, c2v):
        if eixo == "x":
            return (ax_val, c1v, c2v)
        elif eixo == "y":
            return (c2v, ax_val, c1v)
        else:
            return (c1v, c2v, ax_val)

    def normal(c1v, c2v):
        if eixo == "x":
            return (0.0, c1v, c2v)
        elif eixo == "y":
            return (c2v, 0.0, c1v)
        else:
            return (c1v, c2v, 0.0)

    for j in range(n_seg):
        j2 = (j + 1) % n_seg
        c1a, c2a = c1 + r * np.cos(ang[j]), c2 + r * np.sin(ang[j])
        c1b, c2b = c1 + r * np.cos(ang[j2]), c2 + r * np.sin(ang[j2])
        q = np.array([ponto(lo, c1a, c2a), ponto(lo, c1b, c2b),
                      ponto(hi, c1b, c2b), ponto(hi, c1a, c2a)])
        nv = np.array(normal(np.cos((ang[j] + ang[j2]) / 2),
                              np.sin((ang[j] + ang[j2]) / 2)))
        quads.append(q); cores.append(_sombra3d(nv, cor, amb))
    if tampas:
        for ax_val, sinal in ((lo, -1.0), (hi, 1.0)):
            centro = np.array(ponto(ax_val, c1, c2))
            cor_tampa = _sombra3d(np.array(normal(0, 0)) + np.array(
                ponto(sinal, 0, 0)) - np.array(ponto(0, 0, 0)), cor, amb + 0.05)
            for j in range(n_seg):
                j2 = (j + 1) % n_seg
                c1a, c2a = c1 + r * np.cos(ang[j]), c2 + r * np.sin(ang[j])
                c1b, c2b = c1 + r * np.cos(ang[j2]), c2 + r * np.sin(ang[j2])
                quads.append(np.array([centro, ponto(ax_val, c1a, c2a),
                                        ponto(ax_val, c1b, c2b)]))
                cores.append(cor_tampa)
    return quads, cores

def _engrenagem_quads(eixo, lo, hi, c1, c2, r_raiz, r_dente, n_dentes, cor,
                      amb=0.35, tampas=True):
    """Disco com dentes retangulares (engrenagem estilizada) -- mesma
    convencao ciclica de eixos de `_cil_quads`, mas com um perfil radial
    variavel (raiz/dente) em vez de raio constante."""
    passo = 2 * np.pi / n_dentes
    largura = 0.55 * passo
    angs, rads = [], []
    for i in range(n_dentes):
        a0 = i * passo
        angs += [a0, a0 + largura, a0 + largura, a0 + passo]
        rads += [r_dente, r_dente, r_raiz, r_raiz]
    angs = np.array(angs); rads = np.array(rads)
    n_p = len(angs)

    def ponto(ax_val, c1v, c2v):
        if eixo == "x":
            return (ax_val, c1v, c2v)
        elif eixo == "y":
            return (c2v, ax_val, c1v)
        else:
            return (c1v, c2v, ax_val)

    def normal(c1v, c2v):
        if eixo == "x":
            return (0.0, c1v, c2v)
        elif eixo == "y":
            return (c2v, 0.0, c1v)
        else:
            return (c1v, c2v, 0.0)

    quads, cores = [], []
    for j in range(n_p):
        j2 = (j + 1) % n_p
        c1a, c2a = c1 + rads[j] * np.cos(angs[j]), c2 + rads[j] * np.sin(angs[j])
        c1b, c2b = c1 + rads[j2] * np.cos(angs[j2]), c2 + rads[j2] * np.sin(angs[j2])
        q = np.array([ponto(lo, c1a, c2a), ponto(lo, c1b, c2b),
                      ponto(hi, c1b, c2b), ponto(hi, c1a, c2a)])
        amid = (angs[j] + angs[j2]) / 2
        nv = np.array(normal(np.cos(amid), np.sin(amid)))
        quads.append(q); cores.append(_sombra3d(nv, cor, amb))
    if tampas:
        for ax_val, sinal in ((lo, -1.0), (hi, 1.0)):
            centro = np.array(ponto(ax_val, c1, c2))
            cor_tampa = _sombra3d(np.array(ponto(sinal, 0, 0)) -
                                  np.array(ponto(0, 0, 0)), cor, amb + 0.05)
            for j in range(n_p):
                j2 = (j + 1) % n_p
                c1a, c2a = c1 + rads[j] * np.cos(angs[j]), c2 + rads[j] * np.sin(angs[j])
                c1b, c2b = c1 + rads[j2] * np.cos(angs[j2]), c2 + rads[j2] * np.sin(angs[j2])
                quads.append(np.array([centro, ponto(ax_val, c1a, c2a),
                                        ponto(ax_val, c1b, c2b)]))
                cores.append(cor_tampa)
    return quads, cores

def _par_rotores_quads(x0, ylat, zlat, escala=1.0, wrap_deg=300.0, N_Z=50):
    """Par de rotores helicoidais (mesma geometria da Fig. 3.1) posicionado
    no espaco global: eixo helicoidal ao longo de X a partir de x0,
    recentralizado lateralmente em (ylat, zlat) e escalado por `escala`.
    Retorna (quads, cores, comprimento_axial_global)."""
    WRAP_M = np.deg2rad(wrap_deg)
    WRAP_F = -WRAP_M * _Z_M / _Z_F
    COR_M = (0.72, 0.35, 0.32)
    COR_F = (0.62, 0.40, 0.62)
    CINZA = (0.62, 0.62, 0.65)

    svg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "rotor_mesh_commons.svg")
    lobo_m, lobo_f = _svg_lobos(svg)
    pm = _perfil_fechado(lobo_m, _C_M, _Z_M)
    pf = _perfil_fechado(lobo_f, _C_F, _Z_F)
    pm[:, 1] *= -1; pf[:, 1] *= -1
    cm = _C_M * [1, -1]; cf = _C_F * [1, -1]
    R_M = np.max(np.hypot(*(pm - cm).T))
    L = 2.9 * R_M
    centro_lat = (cm + cf) / 2.0
    # O perfil vem do SVG em unidades de pixel (R_M ~ milhares) -- normaliza
    # para que `escala` represente o raio do rotor macho em unidades globais
    # da cena (mesma unidade usada para motor/gearbox/tubulacao).
    escala = escala / R_M

    quads, cores = [], []

    def add_global(poly_local):
        p = np.asarray(poly_local, dtype=float)
        xg = x0 + escala * p[:, 2]
        yg = ylat + escala * (p[:, 0] - centro_lat[0])
        zg = zlat + escala * (p[:, 1] - centro_lat[1])
        return np.column_stack([xg, yg, zg])

    for prof, cen, wrap, cor in ((pm, cm, WRAP_M, COR_M),
                                 (pf, cf, WRAP_F, COR_F)):
        rel = prof - cen
        r = np.hypot(rel[:, 0], rel[:, 1])
        a0 = np.arctan2(rel[:, 1], rel[:, 0])
        n_p = len(prof)
        zs = np.linspace(0, L, N_Z)
        grid = np.empty((N_Z, n_p, 3))
        for i, z in enumerate(zs):
            a = a0 + wrap * z / L
            grid[i, :, 0] = cen[0] + r * np.cos(a)
            grid[i, :, 1] = cen[1] + r * np.sin(a)
            grid[i, :, 2] = z
        for i in range(N_Z - 1):
            for j in range(n_p):
                j2 = (j + 1) % n_p
                q_local = np.array([grid[i, j], grid[i, j2],
                                    grid[i+1, j2], grid[i+1, j]])
                nv = np.cross(q_local[1]-q_local[0], q_local[3]-q_local[0])
                nn = np.linalg.norm(nv)
                if nn < 1e-12:
                    continue
                quads.append(add_global(q_local))
                cores.append(_sombra3d(nv/nn, cor, amb=0.32))
        for i in (0, N_Z - 1):
            c3 = np.array([cen[0], cen[1], zs[i]])
            cor_tampa = _sombra3d(np.array([0, 0, 1.0]), cor, amb=0.40)
            for j in range(n_p):
                q_local = np.array([c3, grid[i, j], grid[i, (j+1) % n_p]])
                quads.append(add_global(q_local)); cores.append(cor_tampa)
        r_eixo = 0.55 * r.min()
        ang = np.linspace(0, 2*np.pi, 40, endpoint=False)
        for z0l, z1l, zcap in ((-0.22*L, 0.0, -0.22*L), (L, 1.22*L, 1.22*L)):
            for j in range(40):
                j2 = (j + 1) % 40
                q_local = np.array([
                    [cen[0]+r_eixo*np.cos(ang[j]),  cen[1]+r_eixo*np.sin(ang[j]),  z0l],
                    [cen[0]+r_eixo*np.cos(ang[j2]), cen[1]+r_eixo*np.sin(ang[j2]), z0l],
                    [cen[0]+r_eixo*np.cos(ang[j2]), cen[1]+r_eixo*np.sin(ang[j2]), z1l],
                    [cen[0]+r_eixo*np.cos(ang[j]),  cen[1]+r_eixo*np.sin(ang[j]),  z1l]])
                nv = np.array([np.cos((ang[j]+ang[j2])/2),
                               np.sin((ang[j]+ang[j2])/2), 0.0])
                quads.append(add_global(q_local))
                cores.append(_sombra3d(nv, CINZA, amb=0.32))
            c3 = np.array([cen[0], cen[1], zcap])
            cor_tampa = _sombra3d(np.array([0, 0, 1.0]), CINZA, amb=0.40)
            for j in range(40):
                j2 = (j + 1) % 40
                q_local = np.array([c3,
                    [cen[0]+r_eixo*np.cos(ang[j]),  cen[1]+r_eixo*np.sin(ang[j]),  zcap],
                    [cen[0]+r_eixo*np.cos(ang[j2]), cen[1]+r_eixo*np.sin(ang[j2]), zcap]])
                quads.append(add_global(q_local)); cores.append(cor_tampa)

    return quads, cores, L * escala

def fig_conjunto3d():
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    quads, cores = [], []
    def ext(par):
        qs, cs = par[0], par[1]
        quads.extend(qs); cores.extend(cs)

    COR_MOTOR   = (0.20, 0.30, 0.44)
    COR_ALETA   = (0.24, 0.35, 0.50)
    COR_CAIXAL  = (0.16, 0.24, 0.36)   # caixa de ligacao do motor
    COR_PE      = (0.22, 0.22, 0.24)
    COR_ACOPL   = (0.50, 0.51, 0.54)
    COR_GB      = (0.74, 0.76, 0.79)
    COR_GB_TAMPA= (0.60, 0.62, 0.66)
    COR_BULL    = (0.58, 0.60, 0.64)
    COR_PINLP   = (0.62, 0.47, 0.26)
    COR_PINHP   = (0.42, 0.55, 0.47)
    COR_EIXO    = (0.50, 0.50, 0.53)
    COR_FLANGE  = (0.38, 0.38, 0.41)
    COR_TUBO_SUC = (0.30, 0.50, 0.72)   # sucao/interestagio: tons de azul
    COR_TUBO_DESC = (0.74, 0.36, 0.30)  # descarga final: tom quente
    COR_IC      = (0.46, 0.66, 0.56)
    COR_CHAO    = (0.88, 0.89, 0.90)

    def flange(eixo, xc, c1, c2, r, cor=COR_FLANGE, largura=0.09):
        ext(_cil_quads(eixo, xc - largura/2, xc + largura/2, c1, c2, r,
                       cor, n_seg=24))

    # --- Motor eletrico: corpo com aletas de refrigeracao, caixa de
    # ligacao e pes de fixacao (em vez de um cilindro liso) ---
    ext(_cil_quads("x", 0.0, 3.4, 0.0, 0.0, 1.0, COR_MOTOR, n_seg=40, tampas=False))
    ext(_cil_quads("x", 0.0, 0.06, 0.0, 0.0, 1.0, COR_MOTOR, n_seg=40))       # tampa traseira
    ext(_cil_quads("x", 3.34, 3.4, 0.0, 0.0, 1.0, COR_MOTOR, n_seg=40))      # tampa dianteira
    for xa in np.arange(0.35, 3.05, 0.26):
        ext(_cil_quads("x", xa, xa + 0.09, 0.0, 0.0, 1.11, COR_ALETA, n_seg=40, tampas=False))
    ext(_caixa_quads(1.25, 2.05, -0.42, 0.42, 1.0, 1.62, COR_CAIXAL))         # caixa de ligacao
    ext(_caixa_quads(0.25, 3.15, -1.05, -1.35, -1.65, -1.0, COR_PE))          # base/pes

    # --- Acoplamento flexivel (com colar central) ---
    ext(_cil_quads("x", 3.4, 3.78, 0.0, 0.0, 0.40, COR_ACOPL, n_seg=28))
    flange("x", 3.59, 0.0, 0.0, 0.50, cor=COR_ACOPL, largura=0.10)

    # --- Gearbox: corpo com nervuras de reforco, tampa de inspecao e
    # flange de acoplamento na face do motor ---
    ext(_caixa_quads(3.78, 6.10, -1.35, 1.35, -1.65, 1.65, COR_GB))
    for za in (-1.2, -0.4, 0.4, 1.2):
        ext(_caixa_quads(3.78, 6.10, -1.37, -1.30, za - 0.08, za + 0.08, COR_GB_TAMPA))
    ext(_caixa_quads(4.15, 5.35, 1.65, 1.80, -0.55, 0.55, COR_GB_TAMPA))      # tampa de inspecao
    flange("x", 3.80, 0.0, 0.0, 0.62, cor=COR_GB_TAMPA, largura=0.10)

    # --- Engrenagens (dentes reais, nao discos lisos) ---
    ext(_engrenagem_quads("x", 6.08, 6.22, 0.0, 0.0, 0.80, 0.95, 26, COR_BULL))
    ext(_engrenagem_quads("x", 6.08, 6.22, 0.0, 1.3, 0.44, 0.55, 16, COR_PINLP))
    ext(_engrenagem_quads("x", 6.08, 6.22, 0.0, -1.3, 0.33, 0.42, 12, COR_PINHP))

    # --- Eixos para os estagios LP (cima) e HP (baixo), com colar de
    # acoplamento onde encontram o rotor ---
    X0_ROTORES = 7.35
    ext(_cil_quads("x", 6.22, X0_ROTORES, 0.0, 1.3, 0.16, COR_EIXO, n_seg=20))
    flange("x", X0_ROTORES - 0.12, 0.0, 1.3, 0.30, cor=COR_EIXO, largura=0.14)

    # --- Estagio LP (maior: menor pressao, maior vazao) ---
    quads_lp, cores_lp, L_LP = _par_rotores_quads(
        X0_ROTORES, ylat=0.0, zlat=1.3, escala=1.15, N_Z=50)
    quads.extend(quads_lp); cores.extend(cores_lp)
    fim_LP = X0_ROTORES + L_LP

    # --- Estagio HP (menor: maior pressao, menor vazao), deslocado a
    # jusante ao longo do fluxo pneumatico (o eixo mecanico ate ele e
    # apenas mais longo -- simplificacao esquematica) ---
    X0_HP = fim_LP + 1.3
    ext(_cil_quads("x", 6.22, X0_HP, 0.0, -1.3, 0.13, COR_EIXO, n_seg=20))
    flange("x", X0_HP - 0.10, 0.0, -1.3, 0.25, cor=COR_EIXO, largura=0.12)
    quads_hp, cores_hp, L_HP = _par_rotores_quads(
        X0_HP, ylat=0.0, zlat=-1.3, escala=0.68, N_Z=50)
    quads.extend(quads_hp); cores.extend(cores_hp)
    fim_HP = X0_HP + L_HP

    # --- Tubulacao de processo (deslocada para +Y, "na frente" do trem
    # mecanico, para nao se confundir com eixos/gearbox), com flanges nas
    # juncoes -- em vez de tubos lisos "flutuando" ---
    Y_TUBO = 1.05
    R_SUC, R_INTER, R_DESC = 0.20, 0.13, 0.19

    # sucao: bocal apontando para cima a partir do topo do estagio LP
    # (evita atravessar o corpo do rotor, que confunde o zsort do mplot3d)
    X_SUC = X0_ROTORES + 0.35
    Z_TOPO_LP = 1.3 + 1.15 + 0.05
    ext(_cil_quads("z", Z_TOPO_LP, Z_TOPO_LP + 1.1, X_SUC, 0.0, R_SUC, COR_TUBO_SUC, n_seg=22))
    flange("z", Z_TOPO_LP + 0.05, X_SUC, 0.0, R_SUC + 0.09, largura=0.10)
    flange("z", Z_TOPO_LP + 1.05, X_SUC, 0.0, R_SUC + 0.07, largura=0.08)

    # interestagio: sai da descarga do LP, desce ate a altura do HP,
    # passando por uma "caixa" de intercooler (com tampas/nervuras), e
    # entra na sucao do HP
    ext(_cil_quads("y", 0.0, Y_TUBO, 1.3, fim_LP - 0.3, R_INTER, COR_TUBO_SUC, n_seg=18))
    ext(_caixa_quads(fim_LP - 0.75, fim_LP + 0.15, Y_TUBO - 0.05, Y_TUBO + 0.55,
                     -0.35, 1.05, COR_IC))
    for zc in (-0.05, 0.35, 0.75):
        ext(_caixa_quads(fim_LP - 0.80, fim_LP - 0.75, Y_TUBO - 0.02, Y_TUBO + 0.52,
                         zc, zc + 0.10, COR_GB_TAMPA))
    ext(_cil_quads("z", -1.3, 1.3, fim_LP - 0.3, Y_TUBO + 0.25, R_INTER, COR_TUBO_SUC, n_seg=18))
    ext(_cil_quads("x", fim_LP - 0.3, X0_HP - 0.15, Y_TUBO + 0.25, -1.3, R_INTER, COR_TUBO_SUC, n_seg=18))
    ext(_cil_quads("y", 0.0, Y_TUBO + 0.25, -1.3, X0_HP - 0.15, R_INTER, COR_TUBO_SUC, n_seg=18))
    flange("y", Y_TUBO + 0.25, -1.3, X0_HP - 0.15, R_INTER + 0.06, largura=0.08)

    # descarga final apos o HP
    ext(_cil_quads("x", fim_HP - 0.15, fim_HP + 1.4, Y_TUBO, -1.3, R_DESC, COR_TUBO_DESC, n_seg=22))
    flange("x", fim_HP + 0.05, Y_TUBO, -1.3, R_DESC + 0.08, cor=(0.55, 0.28, 0.24), largura=0.09)
    flange("x", fim_HP + 1.35, Y_TUBO, -1.3, R_DESC + 0.06, cor=(0.55, 0.28, 0.24), largura=0.08)

    # --- Plano de chao (contexto/sombra) -- evita o efeito de pecas
    # "flutuando" no vazio ---
    cx = (0.0 + fim_HP + 1.4) / 2
    cy = 0.0
    rx, ry = (fim_HP + 1.4) * 0.62, 2.6
    ang_chao = np.linspace(0, 2 * np.pi, 60, endpoint=False)
    z_chao = -1.3 - 0.68 - 0.75
    chao = np.array([[cx + rx * np.cos(a), cy + ry * np.sin(a), z_chao] for a in ang_chao])
    quads.append(chao); cores.append(np.array(COR_CHAO))

    fig = plt.figure(figsize=(13, 6.5))
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(
        quads, facecolors=cores, edgecolors=cores, linewidths=0.08,
        zsort="average", rasterized=True))
    allpts = np.vstack([np.asarray(q).reshape(-1, 3) for q in quads])
    for setl, dim in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), range(3)):
        lo, hi = allpts[:, dim].min(), allpts[:, dim].max()
        pad = 0.05 * (hi - lo)
        setl(lo - pad, hi + pad)
    ax.set_box_aspect(tuple(np.ptp(allpts[:, d]) for d in range(3)))
    ax.view_init(elev=20, azim=-60)
    ax.set_axis_off()

    # --- Rotulos ---
    rotulos = [
        (1.7, 0.0, 2.05, "Motor Elétrico"),
        (4.95, 0.0, 2.15, "Gearbox"),
        (X0_ROTORES + L_LP/2, 0.0, 1.3 + 1.15*1.0 + 0.55, "Estágio LP"),
        (X0_HP + L_HP/2, 0.0, -1.3 - 0.68*1.0 - 0.55, "Estágio HP"),
        (fim_LP - 0.3, Y_TUBO + 0.25, 0.35, "Intercooler"),
        (X_SUC, 0.0, Z_TOPO_LP + 1.35, "Sucção\n(ar atmosférico)"),
        (fim_HP + 0.9, Y_TUBO, -1.75, "Saída\n(Aftercooler/Secagem)"),
    ]
    for x, y, z, txt in rotulos:
        ax.text(x, y, z, txt, fontsize=7.6, color="#1a1a1a", ha="center")

    fig.tight_layout(pad=0)
    save(fig, "fig_2_3_conjunto3d.pdf")
    import subprocess
    pdf = os.path.join(OUTDIR, "fig_2_3_conjunto3d.pdf")
    subprocess.run(["pdfcrop", "--margins", "6", pdf, pdf],
                   check=True, capture_output=True)
    print("cropped", pdf)

if __name__ == "__main__":
    # NOTE: fig_rotores() and fig_psa() are NOT called here on purpose.
    # fig_2_1_rotores.pdf and fig_15_1_psa.pdf are produced from real
    # CC-licensed Wikimedia Commons SVGs (edited/converted via Inkscape),
    # not from these matplotlib draft functions. Calling them would
    # overwrite the production files with the old placeholder drafts.
    fig_arquitetura()
    fig_vi_perdas()
    fig_vogel()
    fig_gearbox()
    fig_campbell()
    fig_l10h()
    fig_etav()
    fig_lmtd()
    fig_psat()
    fig_adsorcao()
    fig_basquin()
    fig_ekf()
    fig_parafuso3d()
    fig_conjunto3d()
    print("done")

# =====================================================================
# FIG 3.1 - Corte esquematico do pacote compressor (motor-gearbox-airend)
# =====================================================================
def fig_corte_pacote():
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.set_aspect("equal")
    ax.axis("off")

    hatch_kw = dict(facecolor="#dbe3ea", edgecolor=NAVY, linewidth=1.3, hatch="////")

    # Invólucro (hood) tracejado envolvendo todo o pacote
    hood = FancyBboxPatch((-0.3, -2.35), 13.0, 5.0, boxstyle="round,pad=0.02,rounding_size=0.15",
                           fill=False, edgecolor=GRAY, linewidth=1.2, linestyle=(0, (6, 4)))
    ax.add_patch(hood)
    ax.text(6.2, 2.85, "Invólucro do pacote (hood)", ha="center", fontsize=8.6, color=GRAY, style="italic")

    # --- Motor elétrico (cilindro em corte) ---
    motor_body = Rectangle((0.2, -1.1), 2.6, 2.2, facecolor="#eef2f6", edgecolor=NAVY, linewidth=1.6)
    ax.add_patch(motor_body)
    # estator hachurado
    for yy in [-1.1, 0.9]:
        r = Rectangle((0.2, yy), 2.6, 0.3, **hatch_kw)
        ax.add_patch(r)
    # rotor do motor (eixo)
    ax.add_patch(Rectangle((0.2, -0.15), 2.6, 0.3, facecolor="#b9c6d1", edgecolor=NAVY, linewidth=1.0))
    shaft = Rectangle((2.8, -0.06), 0.9, 0.12, facecolor="#7a7a7a", edgecolor="none")
    ax.add_patch(shaft)
    ax.text(1.5, 1.55, "Motor Elétrico", ha="center", fontsize=9, fontweight="bold", color=NAVY)

    # --- Acoplamento ---
    coupl = Circle((3.85, 0.0), 0.32, facecolor="#c9d3db", edgecolor=NAVY, linewidth=1.3, zorder=4)
    ax.add_patch(coupl)
    ax.text(3.85, -0.75, "Acoplamento", ha="center", fontsize=7.6, color=NAVY)

    # --- Caixa multiplicadora (gearbox) ---
    gb_body = Rectangle((4.2, -0.95), 1.9, 1.9, facecolor="#eef2f6", edgecolor=NAVY, linewidth=1.6)
    ax.add_patch(gb_body)
    bull = Circle((5.15, 0.0), 0.62, facecolor="#dbe3ea", edgecolor=NAVY, linewidth=1.3, hatch="\\\\\\\\")
    ax.add_patch(bull)
    pin = Circle((5.75, 0.35), 0.28, facecolor="#dbe3ea", edgecolor=NAVY, linewidth=1.1, hatch="\\\\\\\\")
    ax.add_patch(pin)
    ax.text(5.15, 1.55, "Gearbox", ha="center", fontsize=9, fontweight="bold", color=NAVY)

    gb_shaft = Rectangle((6.1, -0.06), 0.55, 0.12, facecolor="#7a7a7a", edgecolor="none")
    ax.add_patch(gb_shaft)

    # --- Airend (carcaca do elemento compressor com rotores em corte) ---
    airend = FancyBboxPatch((6.65, -1.25), 3.6, 2.5, boxstyle="round,pad=0.02,rounding_size=0.12",
                             facecolor="#eef2f6", edgecolor=NAVY, linewidth=1.8)
    ax.add_patch(airend)
    rotor_m = Circle((7.85, 0.0), 0.78, facecolor="#f3d9c4", edgecolor="#8a5a2b", linewidth=1.6, hatch="////", zorder=4)
    rotor_f = Circle((9.15, 0.0), 0.78, facecolor="#dbe7f2", edgecolor=NAVY, linewidth=1.6, hatch="\\\\\\\\", zorder=3)
    ax.add_patch(rotor_m)
    ax.add_patch(rotor_f)
    for c in [(7.85, 0.0), (9.15, 0.0)]:
        ax.plot([c[0]], [c[1]], marker="+", color="#333333", ms=8, mew=1.4, zorder=5)
    ax.text(8.5, 1.55, "Airend (rotores)", ha="center", fontsize=9, fontweight="bold", color=NAVY)

    # bocal de descarga
    disch = Rectangle((8.75, 1.25), 0.55, 0.55, facecolor="#eef2f6", edgecolor=NAVY, linewidth=1.4)
    ax.add_patch(disch)
    ax.annotate("", xy=(9.0, 2.15), xytext=(9.0, 1.8),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.4))
    ax.text(9.75, 1.95, "descarga\n(alta pressão)", ha="left", fontsize=7.6, color=RED)

    # sucção
    ax.annotate("", xy=(6.75, -0.55), xytext=(6.35, -0.95),
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.4))
    ax.text(5.55, -1.55, "sucção\n(ar atmosférico)", ha="center", fontsize=7.6, color=BLUE)

    ax.text(6.2, -2.05, "Corte esquemático longitudinal — motor, acoplamento, gearbox e airend dentro do invólucro do pacote.",
            ha="center", fontsize=7.6, color="#555555", style="italic")

    ax.set_xlim(-0.6, 13.0)
    ax.set_ylim(-2.7, 3.15)
    save(fig, "fig_3_1_corte.pdf")

# NOTE: fig_corte_pacote() nao e' mais chamada — a Figura 3.1 passou a ser
# o render 3D dos rotores (fig_parafuso3d, ver bloco __main__). A funcao
# fica mantida caso o corte esquematico volte a ser usado no futuro.
