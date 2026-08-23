import bpy
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_common import (limpar_cena, mat, cilindro, cone_tronco, caixa, piso,
                             montar_luzes_mundo, montar_camera, configurar_render, renderizar)

limpar_cena()

M_CORPO = mat("CorpoValvula", "#8A8D93", metalico=0.85, rugosidade=0.30)
M_CAPUZ = mat("CapuzMola", "#D97E1A", metalico=0.6, rugosidade=0.35)
M_FLANGE = mat("FlangeValvula", "#4A4A4E", metalico=0.85, rugosidade=0.40)
M_ALAV = mat("Alavanca", "#333336", metalico=0.7, rugosidade=0.45)

# Flange de entrada
cilindro("FlangeEntrada", raio=0.34, altura=0.10, local=(0, 0, 0.05), material=M_FLANGE)
# Coto de entrada
cilindro("CotoEntrada", raio=0.16, altura=0.18, local=(0, 0, 0.19), material=M_CORPO)
# Corpo bojudo (dois troncos de cone)
cone_tronco("CorpoBaixo", r1=0.16, r2=0.40, altura=0.27, local=(0, 0, 0.415), material=M_CORPO)
cone_tronco("CorpoAlto", r1=0.40, r2=0.30, altura=0.40, local=(0, 0, 0.75), material=M_CORPO)
# Flange do capuz
cilindro("FlangeCapuz", raio=0.38, altura=0.10, local=(0, 0, 1.0), material=M_FLANGE)
import math
for ang in range(0, 360, 45):
    a = math.radians(ang)
    cilindro("Parafuso%d" % ang, raio=0.035, altura=0.16, local=(0.36 * math.cos(a), 0.36 * math.sin(a), 1.0), material=M_ALAV, segs=12)
# Capuz da mola
cone_tronco("CapuzBase", r1=0.30, r2=0.24, altura=0.10, local=(0, 0, 1.10), material=M_CAPUZ)
cilindro("CapuzCorpo", raio=0.24, altura=0.50, local=(0, 0, 1.40), material=M_CAPUZ)
cilindro("CapuzTopo", raio=0.24, altura=0.07, local=(0, 0, 1.685), material=M_CAPUZ)
# Alavanca de teste manual
cilindro("PivoAlavanca", raio=0.05, altura=0.18, local=(0, 0, 1.81), material=M_ALAV, segs=16)
cilindro("BracoAlavanca", raio=0.035, altura=0.32, local=(0, 0.16, 1.80), rot_eixo="X", rot_graus=0, material=M_ALAV, segs=12)

piso(raio=1.4, z=-0.02)
montar_luzes_mundo()
montar_camera(alvo=(0, 0, 0.9), distancia=3.4, elev_graus=18, azim_graus=-50, lente_mm=55)
configurar_render("fig_13_1_valvulas.png", res_x=1400, res_y=1700, samples=200)
renderizar()
