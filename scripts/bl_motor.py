import bpy, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_common import (limpar_cena, mat, cilindro, caixa, piso, toro, unir_solidos,
                             posicao_radial_x,
                             montar_luzes_mundo, montar_camera, configurar_render, renderizar)

limpar_cena()

M_CORPO = mat("CorpoMotor", "#1F3B57", metalico=0.35, rugosidade=0.55)
M_ALETA = mat("AletaMotor", "#2B5A80", metalico=0.35, rugosidade=0.55)
M_CAIXA = mat("CaixaLigacao", "#B8860B", metalico=0.6, rugosidade=0.4)
M_PE = mat("PeMotor", "#2A2A2C", metalico=0.5, rugosidade=0.5)
M_EIXO = mat("EixoMotor", "#7D7D82", metalico=0.9, rugosidade=0.25)
M_PLACA = mat("PlacaMotor", "#E5E5E0", metalico=0.1, rugosidade=0.4)

L, R = 2.3, 0.52
corpo = cilindro("Corpo", raio=R, altura=L, local=(L/2, 0, 0), rot_eixo="X", material=M_CORPO, segs=72)

# Aletas axiais retas (perfil real de motor nervurado) -- muito mais
# controlavel em proporcao do que aneis toroidais completos (que, testados
# antes, dominavam o silhueta como uma "mola", ver CONTEXTO.md): cada
# aleta e' uma placa fina, longa ao longo de X, distribuida ao redor da
# circunferencia. Nao cruza o corpo o bastante para precisar de uniao
# booleana (a base da aleta so encosta na superficie).
N_FINS = 16
FIN_LEN = L - 0.55
FIN_PROTRUSAO = 0.11
FIN_ESPESSURA = 0.045
for i in range(N_FINS):
    ang = i * 360.0 / N_FINS
    x, y, z = posicao_radial_x(0.30 + FIN_LEN / 2, R + FIN_PROTRUSAO / 2 - 0.01, ang)
    caixa("Aleta%d" % i, dx=FIN_LEN, dy=FIN_ESPESSURA, dz=FIN_PROTRUSAO, local=(x, y, z),
         rot_graus_x=ang, material=M_ALETA)

caixa("CaixaLigacaoBase", dx=0.60, dy=0.64, dz=0.32, local=(1.25, 0, R + 0.14), material=M_CAIXA)
caixa("CaixaLigacaoTampa", dx=0.70, dy=0.72, dz=0.10, local=(1.25, 0, R + 0.35), material=M_CAIXA)

for yc in (-0.34, 0.34):
    caixa("Pe%.2f" % yc, dx=L - 0.50, dy=0.26, dz=0.20, local=(L / 2, yc, -R - 0.14), material=M_PE)

caixa("Placa", dx=0.20, dy=0.48, dz=0.04, local=(1.85, 0, R), material=M_PLACA)

cilindro("Eixo", raio=0.15, altura=0.34, local=(L + 0.17, 0, 0), rot_eixo="X", material=M_EIXO, segs=48)
cilindro("FlangeAcopl", raio=0.27, altura=0.12, local=(L + 0.26, 0, 0), rot_eixo="X", material=M_EIXO, segs=48)

piso(raio=2.6, z=-R - 0.30)
montar_luzes_mundo()
montar_camera(alvo=(L * 0.45, 0, 0.05), distancia=4.6, elev_graus=17, azim_graus=-55, lente_mm=50)
configurar_render("fig_4_1_motor.png", res_x=1900, res_y=1300, samples=220)
renderizar()
