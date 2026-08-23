"""
Utilitarios comuns para as cenas Blender do livro compressores.tex.
Rodar sempre via: blender --background --python <script_da_cena.py>

Todas as cenas seguem o mesmo padrao: limpar a cena default, construir a
geometria com as funcoes _obj_* deste modulo, aplicar materiais PBR
(Principled BSDF), montar 3 luzes + mundo claro, posicionar camera,
renderizar em Cycles com GPU (fallback CPU se GPU nao disponivel) e salvar
PNG em ../figuras_blender/, depois converter para PDF via ImageMagick (fora
deste script, no shell).
"""
import bpy
import math
import os

OUTDIR_PNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figuras_blender")
os.makedirs(OUTDIR_PNG, exist_ok=True)


def limpar_cena():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for bl in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(bl):
            if item.users == 0:
                bl.remove(item)


def cor_ral(hexstr):
    """Converte '#RRGGBB' para tupla (r,g,b,1) em espaco linear (aprox.)."""
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    # gamma sRGB -> linear aproximado, para a cor "ler" no viewport como o hex pedido
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b), 1.0)


_MAT_CACHE = {}


def mat(nome, cor_hex, metalico=0.9, rugosidade=0.35, emissao=0.0):
    key = (nome, cor_hex, metalico, rugosidade, emissao)
    if key in _MAT_CACHE:
        return _MAT_CACHE[key]
    m = bpy.data.materials.new(name=nome)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    cor = cor_ral(cor_hex)
    bsdf.inputs["Base Color"].default_value = cor
    bsdf.inputs["Metallic"].default_value = metalico
    bsdf.inputs["Roughness"].default_value = rugosidade
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = cor
        bsdf.inputs["Emission Strength"].default_value = emissao
    _MAT_CACHE[key] = m
    return m


def _add(obj, material):
    obj.data.materials.append(material)
    return obj


def _suave(obj, so_quads=True):
    """Sombreamento suave (normais interpoladas) em vez do flat shading
    padrao dos primitivos do Blender -- essencial em superficies curvas
    (cilindro, cone, esfera, torus): sem isso, cada face poligonal aparece
    com uma faceta visivel, e apos uma uniao booleana (`unir_solidos`) a
    triangulacao irregular da costura vira um padrao xadrez bem visivel.
    `so_quads=True` (default) suaviza so as faces quad (a lateral, em
    cilindro/cone) e deixa as tampas (n-gon) no flat shading original --
    suavizar a tampa tambem arredonda visualmente a quina viva entre a
    tampa plana e a lateral, fazendo um cilindro curto/gordo (ex.: uma
    flange) parecer uma pilula/esfera em vez de um disco com bordas
    definidas. Objetos sem tampas a preservar (torus, esfera) ou onde a
    peca inteira deve ficar redonda podem chamar com `so_quads=False`."""
    for p in obj.data.polygons:
        if so_quads and len(p.vertices) != 4:
            continue
        p.use_smooth = True
    return obj


def cilindro(nome, raio, altura, local, rot_eixo="Z", rot_graus=0.0, material=None, segs=64,
             tampas=True):
    """tampas=False cria um tubo aberto (sem disco nas duas pontas) -- usar
    sempre que o cilindro for embutido/sobreposto a outro solido (ex.:
    aletas de refrigeracao encostadas num corpo cilindrico maior), senao o
    disco da tampa fica quase coincidente com a superficie do solido
    vizinho e o Cycles produz z-fighting (padrao xadrez piscante)."""
    bpy.ops.mesh.primitive_cylinder_add(radius=raio, depth=altura, location=local, vertices=segs,
                                        end_fill_type="NGON" if tampas else "NOTHING")
    obj = bpy.context.active_object
    obj.name = nome
    if rot_eixo == "X":
        obj.rotation_euler = (0, math.radians(90 + rot_graus), 0)
    elif rot_eixo == "Y":
        obj.rotation_euler = (math.radians(90 + rot_graus), 0, 0)
    else:
        obj.rotation_euler = (0, 0, math.radians(rot_graus))
    _suave(obj)
    if material:
        _add(obj, material)
    return obj


def cone_tronco(nome, r1, r2, altura, local, rot_eixo="Z", rot_graus=0.0, material=None, segs=64):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=altura, location=local, vertices=segs)
    obj = bpy.context.active_object
    obj.name = nome
    if rot_eixo == "X":
        obj.rotation_euler = (0, math.radians(90 + rot_graus), 0)
    elif rot_eixo == "Y":
        obj.rotation_euler = (math.radians(90 + rot_graus), 0, 0)
    else:
        obj.rotation_euler = (0, 0, math.radians(rot_graus))
    _suave(obj)
    if material:
        _add(obj, material)
    return obj


def caixa(nome, dx, dy, dz, local, rot_graus_z=0.0, rot_graus_x=0.0, material=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=local)
    obj = bpy.context.active_object
    obj.name = nome
    obj.scale = (dx / 2, dy / 2, dz / 2)
    obj.rotation_euler = (math.radians(rot_graus_x), 0, math.radians(rot_graus_z))
    if material:
        _add(obj, material)
    return obj


def posicao_radial_x(xc, raio, angulo_graus):
    """Posicao (x,y,z) de um ponto a `raio` do eixo X global, girado por
    `angulo_graus` no plano Y-Z -- usar para distribuir pecas ao redor de
    um cilindro deitado em X (ex.: aletas axiais retas de um motor), junto
    com `rot_graus_x=angulo_graus` na propria peca para orienta-la
    radialmente."""
    a = math.radians(angulo_graus)
    return (xc, raio * math.sin(a), raio * math.cos(a))


def esfera(nome, raio, local, material=None, segs=48):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=raio, location=local, segments=segs, ring_count=segs // 2)
    obj = bpy.context.active_object
    obj.name = nome
    _suave(obj, so_quads=False)
    if material:
        _add(obj, material)
    return obj


def toro(nome, raio_maior, raio_menor, local, rot_eixo="Z", material=None, segs=48):
    """Torus com o eixo de simetria ao longo de `rot_eixo` -- default 'Z'
    (nativo do Blender). Usar 'X' para um anel que envolve um cilindro
    deitado ao longo de X (ex.: aleta de refrigeracao) -- evita o
    z-fighting de um disco cheio encostado no corpo (ver `cilindro`,
    `tampas=False`) sem deixar o anel "solto"/vazado como um tubo aberto."""
    bpy.ops.mesh.primitive_torus_add(major_radius=raio_maior, minor_radius=raio_menor,
                                      location=local, major_segments=segs, minor_segments=max(segs // 2, 12))
    obj = bpy.context.active_object
    obj.name = nome
    if rot_eixo == "X":
        obj.rotation_euler = (0, math.radians(90), 0)
    elif rot_eixo == "Y":
        obj.rotation_euler = (math.radians(90), 0, 0)
    _suave(obj)
    if material:
        _add(obj, material)
    return obj


def unir_solidos(obj_principal, objs_secundarios):
    """Uniao booleana real (CSG) de obj_principal com cada objeto em
    objs_secundarios, aplicada e consolidada num unico mesh. Usar sempre
    que dois solidos se cruzarem de verdade (ex.: aleta anelar atravessando
    o corpo cilindrico do motor) -- sobrepor objetos sem unir deixa uma
    costura onde as duas superficies se cruzam, e o Cycles produz
    z-fighting/moire ali (ambiguidade de qual face esta na frente), mesmo
    que visualmente as duas pecas devessem se ler como uma peca fundida
    unica. Encostar objetos sem cruzamento real (ex.: um pe apoiado embaixo
    de uma caixa, tocando so por uma face) nao precisa disso.

    Atencao: a preservacao de material do objeto secundario apos a uniao
    e' inconsistente (testado: funcionou para um torus fino cruzando um
    cilindro do mesmo tom de azul, falhou para uma caixa de cor bem
    diferente encostada de raspao -- o resultado saiu inteiro na cor do
    obj_principal). So usar esta funcao quando o cruzamento real de
    geometria estiver causando um defeito visivel (z-fighting); para
    pecas so encostadas/apoiadas, deixar como objetos separados e
    conferir o resultado antes de decidir se vale unir."""
    bpy.context.view_layer.objects.active = obj_principal
    for sec in objs_secundarios:
        mod = obj_principal.modifiers.new(name="Uniao", type="BOOLEAN")
        mod.operation = "UNION"
        mod.object = sec
        mod.solver = "EXACT"
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for sec in objs_secundarios:
        bpy.data.objects.remove(sec, do_unlink=True)
    _suave(obj_principal)
    return obj_principal


def duplicar_linkado(obj, local, nome=None):
    """Duplicata com mesh compartilhada (rapido, sem overhead de bpy.ops) --
    usado para grades repetitivas (ex.: tocos de tubo do espelho tubular)."""
    novo = obj.copy()
    if nome:
        novo.name = nome
    novo.location = local
    bpy.context.collection.objects.link(novo)
    return novo


def piso(raio=6.0, z=0.0):
    m = bpy.data.materials.new("Piso")
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.93, 0.93, 0.94, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.95
    bsdf.inputs["Metallic"].default_value = 0.0
    bpy.ops.mesh.primitive_circle_add(radius=raio, fill_type="NGON", location=(0, 0, z))
    obj = bpy.context.active_object
    obj.name = "Piso"
    obj.data.materials.append(m)
    return obj


def montar_luzes_mundo():
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.97, 0.97, 0.98, 1.0)
    bg.inputs[1].default_value = 1.15

    bpy.ops.object.light_add(type="AREA", location=(4.0, -5.0, 6.0))
    key = bpy.context.active_object
    key.data.energy = 900
    key.data.size = 4.0
    key.rotation_euler = (math.radians(45), 0, math.radians(35))

    bpy.ops.object.light_add(type="AREA", location=(-5.0, 3.0, 3.0))
    fill = bpy.context.active_object
    fill.data.energy = 300
    fill.data.size = 5.0
    fill.rotation_euler = (math.radians(70), 0, math.radians(-60))

    bpy.ops.object.light_add(type="AREA", location=(0.0, 4.0, 2.0))
    rim = bpy.context.active_object
    rim.data.energy = 220
    rim.data.size = 3.0
    rim.rotation_euler = (math.radians(100), 0, math.radians(180))


def montar_camera(alvo, distancia, elev_graus, azim_graus, lente_mm=50):
    ex = distancia * math.cos(math.radians(elev_graus)) * math.cos(math.radians(azim_graus))
    ey = distancia * math.cos(math.radians(elev_graus)) * math.sin(math.radians(azim_graus))
    ez = distancia * math.sin(math.radians(elev_graus))
    bpy.ops.object.camera_add(location=(alvo[0] + ex, alvo[1] + ey, alvo[2] + ez))
    cam = bpy.context.active_object
    cam.data.lens = lente_mm
    direcao = (alvo[0] - cam.location.x, alvo[1] - cam.location.y, alvo[2] - cam.location.z)
    import mathutils
    quat = mathutils.Vector(direcao).to_track_quat("-Z", "Y")
    cam.rotation_euler = quat.to_euler()
    bpy.context.scene.camera = cam
    return cam


def configurar_render(nome_arquivo, res_x=1800, res_y=1400, samples=256, transparente=True, gpu=True):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.film_transparent = transparente
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if transparente else "RGB"
    scene.render.filepath = os.path.join(OUTDIR_PNG, nome_arquivo)

    if gpu:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "CUDA"
        # get_devices_for_type() consulta só o backend CUDA -- get_devices()
        # (sem argumento) varre todos os backends, inclusive SYCL/oneAPI, que
        # crasha neste ambiente snap sandboxed (Level Zero indisponível).
        found = False
        try:
            devices = prefs.get_devices_for_type("CUDA")
        except AttributeError:
            devices = []
        for d in devices:
            if d.type == "CUDA":
                d.use = True
                found = True
        scene.cycles.device = "GPU" if found else "CPU"
        if not found:
            print("AVISO: nenhuma GPU CUDA encontrada, usando CPU")
    else:
        scene.cycles.device = "CPU"


def renderizar():
    bpy.ops.render.render(write_still=True)
    print("RENDER_OK", bpy.context.scene.render.filepath)
