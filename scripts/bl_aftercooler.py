import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_common import (limpar_cena, mat, cilindro, caixa, piso, duplicar_linkado,
                             montar_luzes_mundo, montar_camera, configurar_render, renderizar)

limpar_cena()

M_CASCO  = mat("CascoAC", "#8A8D93", metalico=0.55, rugosidade=0.40)
M_CABECA = mat("CabecaAC", "#A8AC92", metalico=0.5, rugosidade=0.45)
M_FLANGE = mat("FlangeAC", "#4A4A4E", metalico=0.7, rugosidade=0.3)
M_ESPELHO= mat("EspelhoAC", "#3C3C3E", metalico=0.5, rugosidade=0.5)
M_TUBO   = mat("TuboFeixe", "#26262A", metalico=0.6, rugosidade=0.35)
M_BOCALQ = mat("BocalQuente", "#B85C4C", metalico=0.6, rugosidade=0.35)
M_BOCALF = mat("BocalFrio", "#3C80B8", metalico=0.6, rugosidade=0.35)
M_PE     = mat("PeAC", "#2A2A2C", metalico=0.4, rugosidade=0.55)

L, R = 2.6, 0.55
X_ESP = 0.0

cilindro("Casco", raio=R, altura=L, local=(L/2, 0, 0), rot_eixo="X", material=M_CASCO, segs=64)
cilindro("Cabecote", raio=R * 0.85, altura=0.30, local=(L + 0.15, 0, 0), rot_eixo="X", material=M_CABECA, segs=56)
cilindro("FlangeCabecote", raio=R + 0.08, altura=0.06, local=(L, 0, 0), rot_eixo="X", material=M_FLANGE, segs=56)

# Espelho tubular exposto (face aberta, esquerda)
cilindro("Espelho", raio=R, altura=0.04, local=(X_ESP - 0.02, 0, 0), rot_eixo="X", material=M_ESPELHO, segs=64)
cilindro("FlangeEspelho", raio=R + 0.09, altura=0.06, local=(X_ESP - 0.05, 0, 0), rot_eixo="X", material=M_FLANGE, segs=64)

# Grade de tocos de tubo (feixe) -- um objeto criado, os demais duplicados
# (rapido, sem overhead de bpy.ops por toco)
base_tubo = cilindro("Tubo_0_0", raio=0.032, altura=0.18, local=(X_ESP + 0.07, 0, 0),
                     rot_eixo="X", material=M_TUBO, segs=10)
passo = 0.11
n_anel = int(R / passo)
for i in range(-n_anel, n_anel + 1):
    for j in range(-n_anel, n_anel + 1):
        if i == 0 and j == 0:
            continue
        cy, cz = i * passo, j * passo
        if (cy**2 + cz**2) ** 0.5 > R - 0.09:
            continue
        duplicar_linkado(base_tubo, local=(X_ESP + 0.07, cy, cz), nome="Tubo_%d_%d" % (i, j))

# Chicana central visivel na face aberta
caixa("Chicana", dx=0.15, dy=(R - 0.06) * 2, dz=0.10, local=(X_ESP + 0.045, 0, 0), material=M_FLANGE)

# Bocais de ar (em linha com o eixo)
cilindro("ArQuente", raio=0.15, altura=0.55, local=(-0.325, 0, R * 0.55), rot_eixo="X", material=M_BOCALQ, segs=28)
cilindro("ArResfriado", raio=0.15, altura=0.55, local=(L + 0.575, 0, 0), rot_eixo="X", material=M_BOCALF, segs=28)

# Bocais de agua de resfriamento
cilindro("AguaIn", raio=0.10, altura=0.35, local=(0.65, -(R + 0.175), 0), rot_eixo="Y", material=M_BOCALF, segs=20)
cilindro("AguaOut", raio=0.10, altura=0.35, local=(1.95, R + 0.175, 0), rot_eixo="Y", material=M_BOCALQ, segs=20)

# Pes de apoio
for xc in (0.55, L - 0.35):
    caixa("Pe%.2f" % xc, dx=0.36, dy=0.90, dz=0.10, local=(xc, 0, -R - 0.05), material=M_PE)

piso(raio=2.8, z=-R - 0.30)
montar_luzes_mundo()
montar_camera(alvo=(L * 0.42, 0, 0.05), distancia=6.4, elev_graus=18, azim_graus=-52, lente_mm=42)
configurar_render("fig_14_1_aftercooler.png", res_x=1950, res_y=1300, samples=220)
renderizar()
