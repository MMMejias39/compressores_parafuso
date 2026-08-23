import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_common import (limpar_cena, mat, cilindro, piso, montar_luzes_mundo,
                             montar_camera, configurar_render, renderizar)

limpar_cena()
M_X = mat("EixoX", "#CC3333", metalico=0.2, rugosidade=0.5)
M_Y = mat("EixoY", "#33CC33", metalico=0.2, rugosidade=0.5)
M_Z = mat("EixoZ", "#3333CC", metalico=0.2, rugosidade=0.5)

# cilindro fino e longo em cada eixo, saindo da origem, para ver claramente a direcao
cilindro("CilX", raio=0.08, altura=2.0, local=(1.0, 0, 0), rot_eixo="X", material=M_X)
cilindro("CilY", raio=0.08, altura=2.0, local=(0, 1.0, 0), rot_eixo="Y", material=M_Y)
cilindro("CilZ", raio=0.08, altura=2.0, local=(0, 0, 1.0), rot_eixo="Z", material=M_Z)

piso(raio=3.0, z=-0.05)
montar_luzes_mundo()
montar_camera(alvo=(0.5, 0.5, 0.5), distancia=6.0, elev_graus=25, azim_graus=-40, lente_mm=45)
configurar_render("teste_eixos.png", res_x=900, res_y=700, samples=80)
renderizar()
