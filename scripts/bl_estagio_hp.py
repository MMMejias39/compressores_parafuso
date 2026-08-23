import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_common import (limpar_cena, mat, cilindro, caixa, piso, posicao_radial_x,
                             montar_luzes_mundo, montar_camera, configurar_render, renderizar)

limpar_cena()

M_CASC   = mat("CascoHP", "#94969E", metalico=0.55, rugosidade=0.40)
M_NERV   = mat("NervuraHP", "#7A7C84", metalico=0.55, rugosidade=0.40)
M_MANC   = mat("MancalHP", "#66686E", metalico=0.55, rugosidade=0.40)
M_TAMPA  = mat("TampaHP", "#4A4A4E", metalico=0.55, rugosidade=0.40)
M_PE     = mat("PeHP", "#2A2A2C", metalico=0.4, rugosidade=0.55)
M_FLANGE = mat("FlangeHP", "#3D3D41", metalico=0.7, rugosidade=0.30)
M_EIXO   = mat("EixoHP", "#808088", metalico=0.9, rugosidade=0.20)
M_ACOPL  = mat("AcoplHP", "#808088", metalico=0.9, rugosidade=0.20)
M_SUC    = mat("SucHP", "#3C80B8", metalico=0.6, rugosidade=0.35)
M_DESC   = mat("DescHP", "#BC5C4C", metalico=0.6, rugosidade=0.35)
M_PLACA  = mat("PlacaHP", "#E5E5E0", metalico=0.1, rugosidade=0.4)

L, R = 2.3, 0.62
corpo = cilindro("Casco", raio=R, altura=L, local=(L/2, 0, 0), rot_eixo="X", material=M_CASC, segs=72)

# Nervuras de reforco axiais (mesmo padrao validado no motor -- aneis
# toroidais completos dominavam a silhueta como uma "mola", ver
# CONTEXTO.md); nervuras retas ao longo de X, distribuidas ao redor
N_NERV = 10
NERV_LEN = L - 0.65
for i in range(N_NERV):
    ang = i * 360.0 / N_NERV
    x, y, z = posicao_radial_x(0.30 + NERV_LEN / 2, R + 0.03, ang)
    caixa("Nerv%d" % i, dx=NERV_LEN, dy=0.05, dz=0.06, local=(x, y, z),
         rot_graus_x=ang, material=M_NERV)

# Carcacas de mancal/engrenagem de sincronismo nas duas extremidades
cilindro("MancalTraseiro", raio=R + 0.14, altura=0.24, local=(-0.11, 0, 0), rot_eixo="X", material=M_MANC, segs=56)
cilindro("MancalDianteiro", raio=R + 0.10, altura=0.24, local=(L + 0.12, 0, 0), rot_eixo="X", material=M_MANC, segs=56)

# Tampa de inspecao no topo
caixa("TampaInspecao", dx=0.80, dy=0.62, dz=0.19, local=(1.15, 0, R + 0.055), material=M_TAMPA)

# Pes de fixacao
for yc in (-0.45, 0.45):
    caixa("Pe%.2f" % yc, dx=L - 0.50, dy=0.30, dz=0.23, local=(L / 2, yc, -R - 0.135), material=M_PE)

# Placa de identificacao
caixa("Placa", dx=0.20, dy=0.56, dz=0.05, local=(1.45, 0, R), material=M_PLACA)

# Coto de eixo + flange de acoplamento (lado de acionamento)
cilindro("Eixo", raio=0.17, altura=0.33, local=(-0.385, 0, 0), rot_eixo="X", material=M_EIXO, segs=48)
cilindro("FlangeAcopl", raio=0.30, altura=0.12, local=(-0.36, 0, 0), rot_eixo="X", material=M_ACOPL, segs=48)

# Flange de succao (topo, vindo do intercooler)
Z_SUC0 = R + 0.02
cilindro("Succao", raio=0.22, altura=0.75, local=(0.55, 0, Z_SUC0 + 0.375), rot_eixo="Z", material=M_SUC, segs=40)
cilindro("FlangeSuccao", raio=0.30, altura=0.10, local=(0.55, 0, Z_SUC0 + 0.73), rot_eixo="Z", material=M_FLANGE, segs=40)

# Flange de descarga (lateral, proximo ao lado nao acionado)
X_DESC = L - 0.55
cilindro("Descarga", raio=0.16, altura=0.62, local=(X_DESC, -R - 0.31, 0), rot_eixo="Y", material=M_DESC, segs=32)
cilindro("FlangeDescarga", raio=0.23, altura=0.10, local=(X_DESC, -R - 0.58, 0), rot_eixo="Y", material=M_FLANGE, segs=32)

piso(raio=2.6, z=-R - 0.30)
montar_luzes_mundo()
montar_camera(alvo=(L * 0.5, -0.05, 0.05), distancia=6.2, elev_graus=20, azim_graus=-68, lente_mm=45)
configurar_render("fig_11_1_estagio_hp.png", res_x=1900, res_y=1300, samples=220)
renderizar()
