import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_common import (limpar_cena, mat, cilindro, cone_tronco, caixa, piso,
                             montar_luzes_mundo, montar_camera, configurar_render, renderizar)

limpar_cena()

M_CASCO  = mat("CascoVaso", "#8A8D93", metalico=0.55, rugosidade=0.40)
M_CABECA = mat("CabecaVaso", "#7E828A", metalico=0.55, rugosidade=0.40)
M_PERNA  = mat("PernaVaso", "#2A2A2C", metalico=0.4, rugosidade=0.55)
M_BASE   = mat("BaseVaso", "#5A5A5E", metalico=0.3, rugosidade=0.7)
M_BOCAL  = mat("BocalVaso", "#3C80B8", metalico=0.6, rugosidade=0.35)
M_PSV    = mat("PsvVaso", "#D97E1A", metalico=0.6, rugosidade=0.35)
M_FLANGE = mat("FlangeVaso", "#4A4A4E", metalico=0.7, rugosidade=0.3)
M_PLACA  = mat("PlacaVaso", "#E5E5E0", metalico=0.1, rugosidade=0.4)

R, Z0, Z1 = 0.85, 1.0, 4.6

cilindro("Casco", raio=R, altura=Z1 - Z0, local=(0, 0, (Z0 + Z1) / 2), rot_eixo="Z", material=M_CASCO, segs=56)
cone_tronco("CabecaTopo", r1=R, r2=0.14, altura=0.42, local=(0, 0, Z1 + 0.21), rot_eixo="Z", material=M_CABECA, segs=56)
cone_tronco("CabecaBase", r1=R, r2=0.14, altura=0.42, local=(0, 0, Z0 - 0.21), rot_eixo="Z", material=M_CABECA, segs=56)

# Pernas de apoio (4) + base
import math
Z_BASE = Z0 - 0.55
for ang in (45, 135, 225, 315):
    a = math.radians(ang)
    cx, cy = (R - 0.05) * math.cos(a), (R - 0.05) * math.sin(a)
    cilindro("Perna%d" % ang, raio=0.09, altura=1.05, local=(cx, cy, Z_BASE - 0.525),
             rot_eixo="Z", material=M_PERNA, segs=16)
caixa("Base", dx=(R + 0.1) * 2, dy=(R + 0.1) * 2, dz=0.15, local=(0, 0, Z_BASE - 1.125), material=M_BASE)

# Bocal de entrada (lateral, proximo a base)
cilindro("Entrada", raio=0.14, altura=0.55, local=(0, -(R + 0.275), Z0 + 0.55), rot_eixo="Y", material=M_BOCAL, segs=24)
cilindro("FlangeEntrada", raio=0.20, altura=0.06, local=(0, -(R + 0.55), Z0 + 0.55), rot_eixo="Y", material=M_FLANGE, segs=24)

# Bocal de saida (lateral, proximo ao topo)
cilindro("Saida", raio=0.14, altura=0.55, local=(0, R + 0.275, Z1 - 0.55), rot_eixo="Y", material=M_BOCAL, segs=24)
cilindro("FlangeSaida", raio=0.20, altura=0.06, local=(0, R + 0.55, Z1 - 0.55), rot_eixo="Y", material=M_FLANGE, segs=24)

# PSV no topo
cilindro("PsvCorpo", raio=0.09, altura=0.28, local=(0, 0, Z1 + 0.47), rot_eixo="Z", material=M_PSV, segs=20)
cilindro("PsvCapuz", raio=0.14, altura=0.14, local=(0, 0, Z1 + 0.66), rot_eixo="Z", material=M_PSV, segs=20)

# Dreno na base
cilindro("Dreno", raio=0.07, altura=0.23, local=(0, 0, Z0 - 0.525), rot_eixo="Z", material=M_BOCAL, segs=16)

# Placa de identificacao
caixa("Placa", dx=0.28, dy=0.05, dz=0.35, local=(0, R, 2.7), material=M_PLACA)

piso(raio=2.4, z=Z_BASE - 1.22)
montar_luzes_mundo()
montar_camera(alvo=(0, 0.15, 2.3), distancia=8.5, elev_graus=10, azim_graus=-55, lente_mm=42)
configurar_render("fig_16_1_vaso_pulmao.png", res_x=1500, res_y=1900, samples=220)
renderizar()
