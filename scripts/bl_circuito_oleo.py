import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_common import (limpar_cena, mat, cilindro, cone_tronco, caixa, piso,
                             montar_luzes_mundo, montar_camera, configurar_render, renderizar)

limpar_cena()

M_TANQUE = mat("Tanque", "#3B4A3B", metalico=0.5, rugosidade=0.45)
M_VISOR  = mat("Visor", "#8CB8CC", metalico=0.1, rugosidade=0.15)
M_PE     = mat("PeCircuito", "#2A2A2C", metalico=0.4, rugosidade=0.55)
M_BOMBA  = mat("Bomba", "#6A6C72", metalico=0.7, rugosidade=0.35)
M_MOTORB = mat("MotorBomba", "#1F3B57", metalico=0.5, rugosidade=0.45)
M_DEAER  = mat("Deaerador", "#8C8E96", metalico=0.6, rugosidade=0.35)
M_VALV   = mat("ValvTermo", "#9E781A", metalico=0.55, rugosidade=0.4)
M_RESF   = mat("Resfriador", "#4E8066", metalico=0.55, rugosidade=0.4)
M_RESFT  = mat("ResfriadorTampa", "#8A8C92", metalico=0.6, rugosidade=0.35)
M_GB     = mat("GearboxCirc", "#A8AAB0", metalico=0.55, rugosidade=0.4)
M_TUBO   = mat("TuboOleo", "#8C6A2E", metalico=0.6, rugosidade=0.35)
M_RETORNO= mat("TuboRetorno", "#8A8C90", metalico=0.5, rugosidade=0.5)
M_FLANGE = mat("FlangeCirc", "#4A4A4E", metalico=0.7, rugosidade=0.3)
M_PLACA  = mat("PlacaCirc", "#E5E5E0", metalico=0.1, rugosidade=0.4)

def flange_x(xc, y, z, r):
    cilindro("Fl%.2f" % xc, raio=r, altura=0.09, local=(xc, y, z), rot_eixo="X", material=M_FLANGE, segs=28)

Z0 = 0.35  # altura da linha principal de oleo

# --- Reservatorio ---
caixa("Reservatorio", dx=1.0, dy=1.0, dz=0.70, local=(0.5, 0, 0.35), material=M_TANQUE)
caixa("Visor", dx=0.05, dy=0.30, dz=0.40, local=(1.0, 0, 0.35), material=M_VISOR)
caixa("PeReserv", dx=0.80, dy=1.10, dz=0.15, local=(0.5, 0, -0.075), material=M_PE)

# --- Tubulacao ate a bomba ---
cilindro("TuboBomba", raio=0.07, altura=0.55, local=(1.275, 0, Z0), rot_eixo="X", material=M_TUBO, segs=20)

# --- Bomba + motor acoplado ---
cilindro("Bomba", raio=0.26, altura=0.40, local=(1.95, 0, Z0), rot_eixo="X", material=M_BOMBA, segs=32)
cilindro("MotorBomba", raio=0.16, altura=0.26, local=(1.75, 0, Z0 + 0.42), rot_eixo="X", material=M_MOTORB, segs=24)
flange_x(2.15, 0, Z0, 0.30)

# --- Tubulacao ate o deaerador ---
cilindro("TuboDeaer", raio=0.07, altura=0.55, local=(2.475, 0, Z0), rot_eixo="X", material=M_TUBO, segs=20)

# --- Deaerador (vaso vertical com topo afunilado) ---
XD = 2.85
cilindro("Deaerador", raio=0.34, altura=1.15, local=(XD, 0, 0.575), rot_eixo="Z", material=M_DEAER, segs=32)
cone_tronco("DeaeradorTopo", r1=0.34, r2=0.10, altura=0.30, local=(XD, 0, 1.30), rot_eixo="Z", material=M_DEAER, segs=32)
cilindro("Respiro", raio=0.05, altura=0.23, local=(XD, 0, 1.565), rot_eixo="Z", material=M_TUBO, segs=16)

# --- Tubulacao ate a valvula termostatica ---
cilindro("TuboValv", raio=0.07, altura=0.50, local=(3.44, 0, Z0), rot_eixo="X", material=M_TUBO, segs=20)

# --- Valvula termostatica de 3 vias ---
XV = 3.70
cilindro("CorpoValv", raio=0.16, altura=0.30, local=(XV, 0, Z0), rot_eixo="X", material=M_VALV, segs=28)
cilindro("HasteValv", raio=0.06, altura=0.28, local=(XV, 0, Z0 + 0.28), rot_eixo="Z", material=M_VALV, segs=16)

# --- Bypass reto (corre por baixo do resfriador, continuo ate a saida) ---
cilindro("Bypass", raio=0.055, altura=1.45, local=(XV + 0.15 + 0.725, 0, Z0), rot_eixo="X", material=M_TUBO, segs=18)

# --- Ramal do resfriador: sobe, atravessa, desce ---
Z1 = Z0 + 0.85
cilindro("Sobe", raio=0.055, altura=Z1 - Z0, local=(XV + 0.35, 0, (Z0 + Z1) / 2), rot_eixo="Z", material=M_TUBO, segs=16)
cilindro("RamalResf", raio=0.055, altura=0.85, local=(XV + 0.775, 0, Z1), rot_eixo="X", material=M_TUBO, segs=18)

caixa("Resfriador", dx=0.50, dy=0.64, dz=0.60, local=(4.60, 0, Z1), material=M_RESF)
for zc in (Z1 - 0.22, Z1, Z1 + 0.20):
    caixa("ResfTampa%.2f" % zc, dx=0.05, dy=0.60, dz=0.09, local=(4.325, 0, zc), material=M_RESFT)

cilindro("Desce", raio=0.055, altura=Z1 - Z0, local=(5.05, 0, (Z0 + Z1) / 2), rot_eixo="Z", material=M_TUBO, segs=16)

# --- Saida para mancais/gearbox ---
caixa("Gearbox", dx=0.80, dy=1.10, dz=1.10, local=(5.65, 0, 0.20), material=M_GB)
for za in (-0.35, 0.20, 0.75):
    caixa("GBTampa%.2f" % za, dx=0.04, dy=1.06, dz=0.06, local=(5.27, 0, za), material=M_RESFT)

# --- Retorno (oleo aquecido), nivel inferior, cor distinta ---
ZR = -0.55
cilindro("RetornoDesce1", raio=0.06, altura=ZR + 0.05 - (-0.35), local=(5.6, 0, (ZR + -0.35) / 2), rot_eixo="Z", material=M_RETORNO, segs=16)
cilindro("RetornoHoriz", raio=0.06, altura=5.6 - 0.5, local=((0.5 + 5.6) / 2, 0, ZR), rot_eixo="X", material=M_RETORNO, segs=18)
cilindro("RetornoSobe", raio=0.06, altura=0.55, local=(0.5, 0, ZR / 2), rot_eixo="Z", material=M_RETORNO, segs=16)

piso(raio=3.6, z=ZR - 0.35)
montar_luzes_mundo()
montar_camera(alvo=(2.9, 0.1, 0.25), distancia=8.5, elev_graus=24, azim_graus=-42, lente_mm=38)
configurar_render("fig_12_1_circuito_oleo.png", res_x=2100, res_y=1300, samples=220)
renderizar()
