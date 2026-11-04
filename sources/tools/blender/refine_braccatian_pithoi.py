"""BR22: replace a generic placeholder with the source-supported decorated jar assembly."""
import json
import math
from pathlib import Path
import random
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene, cylinder
from manufactured_vessels import vessel, profile_radius
from manufactured_annuli import annulus
from refine_rigellian_crowns import fit_camera, sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/braccatian/br22/model.blend'
REL = Path('docs/assets/reconstruction/braccatian-refined/br22')
OUTPUT, MEDIA = ROOT/'sources'/REL, ROOT/'gallery/media'/REL
TEXTURES = ROOT/'sources/materials/reconstruction/braccatian-refined/br22'
BASE = [(0,.35),(.035,.40),(.09,.425),(.87,.425),(.97,.38),(1.02,.33)]
JAR = [(.94,.33),(1.00,.43),(1.07,.53),(1.15,.59),(1.23,.60),(1.31,.55),
       (1.39,.46),(1.45,.46),(1.53,.55),(1.64,.60),(1.75,.595),(1.85,.54),
       (1.96,.41),(2.06,.26),(2.13,.14),(2.18,.13)]
NECK = [(2.12,.13),(2.18,.16),(2.23,.17),(2.54,.15),(2.61,.095),(2.70,.095)]
ORB = [(2.64,.035),(2.67,.105),(2.73,.16),(2.81,.18),(2.88,.16),(2.94,.10),(2.97,.025)]
VIEWS = {'front-quarter':(6,-13,7), 'front':(0,-16,4), 'side':(16,0,4),
         'rear-quarter':(-7,12,7), 'jar-detail':(3,-13,5)}


def worn_material(style, colour, metallic):
    material = bpy.data.materials.new('BR22 | worn '+style)
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Metallic'].default_value = metallic
    coords = material.node_tree.nodes.new('ShaderNodeTexCoord')
    TEXTURES.mkdir(parents=True, exist_ok=True)
    for kind, socket in [('colour','Base Color'), ('roughness','Roughness')]:
        size, pixels, rng = 256, [], random.Random(19022)
        for y in range(size):
            for x in range(size):
                u, v = x/(size-1), y/(size-1)
                grain = .025*math.sin(u*91+v*33)+rng.uniform(-.02,.02)
                dirt = .16*math.exp(-((v-.08)/.10)**2)*(1+.3*math.sin(u*43))
                dirt += .10*math.exp(-((u-.67)/.12)**2-((v-.52)/.18)**2)
                scratch = .16 if x in [35,36,149,213] and 74<y<125 else 0
                value = .94+grain-dirt+scratch
                rgb = [c*value for c in colour] if kind == 'colour' else [min(.85,.49+dirt-grain-scratch*.5)]*3
                pixels.extend([*rgb,1])
        image = bpy.data.images.new('BR22 independently authored '+style+' '+kind, width=size,height=size)
        image.pixels.foreach_set(pixels)
        path = TEXTURES/(style+'-'+kind+'.png')
        image.filepath_raw, image.file_format = str(path), 'PNG'
        image.save()
        image = bpy.data.images.load(str(path), check_existing=False)
        image.colorspace_settings.name = 'sRGB' if kind == 'colour' else 'Non-Color'
        image.pack()
        node = material.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = image
        material.node_tree.links.new(coords.outputs['UV'],node.inputs['Vector'])
        material.node_tree.links.new(node.outputs['Color'],shader.inputs[socket])
    return material


def skin(profile, x, z):
    radius = profile_radius(profile, z)
    return -math.sqrt(radius*radius-x*x)


def patch(name, profile, xr, zr, material, relief=.015):
    rows, columns = 13, 13
    points = []
    for front in [True,False]:
        for row in range(rows):
            z = zr[0]+(zr[1]-zr[0])*row/(rows-1)
            for col in range(columns):
                x = xr[0]+(xr[1]-xr[0])*col/(columns-1)
                y = skin(profile,x,z)+(-relief if front else .012)
                points.append((x,y,z))
    n, faces = rows*columns, []
    for row in range(rows-1):
        for col in range(columns-1):
            a = row*columns+col
            f = (a,a+1,a+columns+1,a+columns)
            faces.extend([f,tuple(n+i for i in reversed(f))])
    border = list(range(columns))+[r*columns+columns-1 for r in range(1,rows)]
    border += list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))
    border += [r*columns for r in reversed(range(1,rows-1))]
    for a,b in zip(border,border[1:]+border[:1]):
        faces.append((a,a+n,b+n,b))
    return mesh(name,points,faces,material)


def face_ring(name, profile, zcentre, outer, inner, material):
    count, points = 128, []
    for depth in [-.038,.012]:
        for radius in [outer,inner]:
            for i in range(count):
                angle = math.tau*i/count
                x, z = radius*math.cos(angle), zcentre+radius*math.sin(angle)
                points.append((x,skin(profile,x,z)+depth,z))
    faces = []
    for i in range(count):
        j=(i+1)%count
        faces.extend([(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),
                      (i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)])
    return mesh(name,points,faces,material)


def selected(view):
    objects = [o for o in bpy.context.scene.objects if o.type=='MESH']
    return [o for o in objects if o.name.startswith(('BR22 rose','BR22 front','BR22 gold louver'))] if view=='jar-detail' else objects


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    MEDIA.mkdir(parents=True,exist_ok=True)
    scene = setup_scene(768,32)
    collection = bpy.data.collections.new('Pithoi refined complete editable source')
    scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    materials = {name:worn_material(name,colour,metallic) for name,colour,metallic in [
        ('rose-casing',(.48,.235,.17),.65),('gold-casting',(.48,.33,.115),.76),
        ('recess',(.035,.028,.019),.48),('pale-blue',(.48,.61,.72),.62)]}
    gold, rose, dark, blue = [materials[n] for n in ['gold-casting','rose-casing','recess','pale-blue']]
    vessel('BR22 gold lower cylinder',BASE,gold,[(-2.1,.55,.003)])
    vessel('BR22 rose double shoulder jar',JAR,rose,[(-1.8,1.65,.003)])
    vessel('BR22 gold upper neck',NECK,gold,[(-1.7,2.43,.002)])
    vessel('BR22 gold terminal globe',ORB,gold,[(-1.7,2.80,.001)])
    cylinder('BR22 terminal top button',(0,0,2.975),.035,.035,gold,vertices=64)
    for i in range(12):
        angle=math.tau*i/12
        if i==9:
            continue # The front service column stays readable.
        obj=patch(f'BR22 lower gold flute {i:02}',BASE,(-.035,.035),(.12,.87),gold,.025)
        obj.rotation_euler.z=angle+math.pi/2
    patch('BR22 front lower dark equipment backing',BASE,(-.10,.10),(.16,.82),dark,.010)
    for i,z in enumerate([.28,.49,.70]):
        obj=annulus(f'BR22 front lower gold port {i}',(0,0),[(-.025,.076,.050),(.025,.076,.050)],gold,(0,0,0))
        obj.rotation_euler=Vector((0,-1,0)).to_track_quat('Z','Y').to_euler()
        obj.location=(0,-.43,z)
        cylinder(f'BR22 front pale blue inset {i}',(0,-.445,z),.055,.025,blue,vertices=64,rotation=obj.rotation_euler)
    patch('BR22 front middle gold louver frame',JAR,(-.22,.22),(1.29,1.47),gold,.020)
    for i in range(5):
        x=-.16+i*.08
        patch(f'BR22 front dark louver field {i}',JAR,(x-.023,x+.023),(1.32,1.44),dark,.024)
    face_ring('BR22 front upper broad gold round bezel',JAR,1.78,.205,.135,gold)
    patch('BR22 front upper dark fitting backing',JAR,(-.135,.135),(1.645,1.915),dark,.004)
    face_ring('BR22 front upper inner gold round fitting',JAR,1.78,.10,.052,gold)
    patch('BR22 front upper central gold fitting',JAR,(-.043,.043),(1.737,1.823),gold,.026)
    patch('BR22 upper neck red inset',NECK,(-.045,.045),(2.28,2.49),rose,.015)
    for z in [2.29,2.48]:
        patch('BR22 upper neck gold transverse trim '+str(z),NECK,(-.065,.065),(z-.012,z+.012),gold,.021)
    root=bpy.data.objects.new('PlacementRoot',None)
    collection.objects.link(root)
    root['catalogue_id']='openfa:building/legacy/084'
    root['footprint_width']=root['footprint_height']=2
    objects=[o for o in scene.objects if o.type=='MESH']
    for obj in objects:
        obj.parent=root
        if obj.name not in collection.objects:
            collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:
                previous.objects.unlink(obj)
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data);bm.free()
        uv(obj)
        mod=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE')
        mod.keep_custom_normals=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    collection.asset_mark()
    collection.asset_data.description='Pithoi source-supported decorated jar assembly; dimensions and hidden construction authored'
    for view,direction in VIEWS.items():
        fit_camera(direction,selected(view))
        scene.render.filepath=str(MEDIA/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    fit_camera(VIEWS['front-quarter'],objects)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects+[root]:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/'model.blend'))
    meta=dict(issue=190,id='openfa:building/legacy/084',name='Pithoi',culture='braccatian',stage='visible-jar-refinement',
              source_study=SOURCE.relative_to(ROOT).as_posix(),source_blend_sha256=sha(SOURCE),
              blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),generator_sha256=sha(Path(__file__)),
              lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),
              reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json'),
              functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
              dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in ['build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']},
              texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(TEXTURES.glob('*.png'))},
              mesh_objects=len(objects),preserved_objects=[],views=list(VIEWS),blender=bpy.app.version_string,
              observed=['Gold lower cylinder, two rose shoulder/bulb regions, gold upper neck and terminal globe','Large gold circular upper face fitting, middle dark vertical fields, lower pale-blue inset column and red upper-neck inset','Functional text explicitly describes highly decorated storage jars; all 41 catalogue phases and surface parts inspected'],
              inferred=['Exact profiles/dimensions, eleven lower flutes and hidden rear construction','Fitting depths, gold alloy identity and interpretation of small service regions'],
              geometry_policy='Entire generic placeholder assembly replaced in a separate study; no prior geometry retention claim',
              acceptance='Source-supported refinement pending rendered review; final artistic acceptance and game calibration remain separate')
    (OUTPUT/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('BR22_REFINED_JAR_BUILT',len(objects),flush=True)


if __name__=='__main__':main()
