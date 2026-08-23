import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_common import (limpar_cena, mat, cilindro, cone_tronco, caixa, piso,
                             montar_luzes_mundo, montar_camera, configurar_render, renderizar)

limpar_cena()

M_CORPO = mat("CorpoSep", "#8C9096", metalico=0.55, rugosidade=0.40)
M_CONE  = mat("ConeSep", "#767A82", metalico=0.55, rugosidade=0.40)
M_TUBO  = mat("TuboSep", "#3C80B8", metalico=0.6, rugosidade=0.35)
M_FLANGE= mat("FlangeSep", "#4A4A4E", metalico=0.7, rugosidade=0.3)
M_DRENO = mat("DrenoSep", "#9E781A", metalico=0.55, rugosidade=0.40)
M_PE    = mat("PeSep", "#2A2A2C", metalico=0.4, rugosidade=0.55)

R = 0.55

cilindro("CorpoCil", raio=R, altura=1.0, local=(0, 0, 1.4), rot_eixo="Z", material=M_CORPO, segs=56)
cone_tronco("TampaTopo", r1=R, r2=R * 0.35, altura=0.15, local=(0, 0, 1.975), rot_eixo="Z", material=M_CORPO, segs=56)
# Corpo conico alongado (altura ~1.6x o diametro do corpo, proporcao real
# de ciclone -- a primeira versao, altura 0.9 para diametro 1.1, ficou
# curta e larga demais, "em forma de peao de xadrez", em vez do cone fino
# e comprido que gera o vortice de separacao. Corrigido a pedido do autor.
ALT_CONE = 1.8
R_PONTA = 0.06
Z_TOPO_CONE = 0.9  # = base do CorpoCil (1.4 - altura/2)
Z_PONTA_CONE = Z_TOPO_CONE - ALT_CONE
cone_tronco("CorpoConico", r1=R, r2=R_PONTA, altura=ALT_CONE,
           local=(0, 0, (Z_TOPO_CONE + Z_PONTA_CONE) / 2), rot_eixo="Z", material=M_CONE, segs=56)

# Dreno de condensado (na ponta do cone)
cilindro("Dreno", raio=0.09, altura=0.35, local=(0, 0, Z_PONTA_CONE - 0.175), rot_eixo="Z", material=M_DRENO, segs=20)
cilindro("ValvDreno", raio=0.15, altura=0.10, local=(0, 0, Z_PONTA_CONE - 0.40), rot_eixo="Z", material=M_DRENO, segs=20)

# Entrada tangencial (deslocada do centro)
YIN = R * 0.55
cilindro("Entrada", raio=0.15, altura=0.78, local=(0.39, YIN, 1.65), rot_eixo="X", material=M_TUBO, segs=24)
cilindro("FlangeEntrada", raio=0.21, altura=0.06, local=(0.80, YIN, 1.65), rot_eixo="X", material=M_FLANGE, segs=24)

# Saida de ar central (vortex finder)
cilindro("Saida", raio=0.16, altura=0.70, local=(0, 0, 2.40), rot_eixo="Z", material=M_TUBO, segs=28)
cilindro("FlangeSaida", raio=0.23, altura=0.06, local=(0, 0, 2.72), rot_eixo="Z", material=M_FLANGE, segs=28)

# Pes de sustentacao -- presos perto do topo do cone (onde o diametro
# ainda e' largo, como num suporte real) e estendidos ate o piso
import math
Z_PE_TOPO = -0.30  # com folga extra (a primeira tentativa, -0.1, ainda
                   # tocava de raspao a superficie do cone na tampa do pe)
Z_PISO = Z_PONTA_CONE - 0.55
ALT_PE = Z_PE_TOPO - Z_PISO
for ang in (45, 135, 225, 315):
    a = math.radians(ang)
    cx, cy = 0.32 * math.cos(a), 0.32 * math.sin(a)
    cilindro("Pe%d" % ang, raio=0.045, altura=ALT_PE, local=(cx, cy, (Z_PE_TOPO + Z_PISO) / 2),
             rot_eixo="Z", material=M_PE, segs=12)

piso(raio=1.6, z=Z_PISO)
montar_luzes_mundo()
montar_camera(alvo=(0, 0, 0.75), distancia=6.6, elev_graus=13, azim_graus=-50, lente_mm=45)
configurar_render("fig_14_2_separador.png", res_x=1400, res_y=1900, samples=220)
renderizar()
