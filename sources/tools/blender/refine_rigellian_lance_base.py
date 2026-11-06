"""RI23: restore a tapered segmented bronze base while preserving the yaw rig."""
import json
import math
from pathlib import Path
import sys
import bmesh
import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from rigellian_ultrathermal_lance_parts import MOVING,PIVOT,LANCE_TIPS,LANCE_AXIS
from manufactured_vessels import profile_radius
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'sources/docs/assets/reconstruction/buildings/rigellian/ultrathermal-lance/model.blend'
REL=Path('docs/assets/reconstruction/rigellian-refined/ri23')
OUTPUT,MEDIA=ROOT/'sources'/REL,ROOT/'gallery/media'/REL
TEXTURES=ROOT/'sources/materials/reconstruction/rigellian-refined/ri23'
SKIRT='RI23 fixed bronze skirt'
PROFILE=[(0,.25),(.025,.32),(.07,.39),(.13,.435),(.19,.46),(.22,.46),(.25,.43)]
VIEWS={'front-quarter':(12,-8,7),'front':(0,-16,4),'side':(16,0,4),
       'rear-quarter':(-7,12,7),'skirt-detail':(6,-13,5)}


def finish_material(original, name, colour, filename):
    """Preserve authored wear variation, changing its broad material colour."""
    mat = original.copy()
    mat.name = name
    node = mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].links[0].from_node
    image = node.image
    data = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(data)
    data = data.reshape(image.size[1], image.size[0], 4)
    size = 512
    values = data[np.linspace(0, image.size[1]-1, size).astype(int)[:, None],
                  np.linspace(0, image.size[0]-1, size).astype(int)[None, :]].copy()
    luminance = np.mean(values[:, :, :3], axis=2)
    variation = np.clip(luminance/max(.01, float(np.median(luminance))), .65, 1.35)
    values[:, :, :3] = np.asarray(colour)[None, None, :]*variation[:, :, None]
    authored = bpy.data.images.new(name+' authored colour wear', width=size, height=size)
    authored.pixels.foreach_set(values.ravel())
    TEXTURES.mkdir(parents=True, exist_ok=True)
    path = TEXTURES/filename
    authored.filepath_raw, authored.file_format = str(path), 'PNG'
    authored.save()
    authored = bpy.data.images.load(str(path), check_existing=False)
    authored.colorspace_settings.name = 'sRGB'
    authored.pack()
    node.image = authored
    return mat


def skirt(material):
    rows,rings=101,96
    points=[]
    for row in range(rows):
        z=.25*row/(rows-1)
        r=profile_radius(PROFILE,z)
        for i in range(rings):
            phi=math.tau*i/rings
            d=.002*math.exp(-2*((phi-(math.tau-2.2))/.12)**2-2*((z-.13)/.07)**2)
            points.append(((r-d)*math.cos(phi),(r-d)*math.sin(phi),z))
    faces=[tuple(reversed(range(rings))),tuple(range((rows-1)*rings,rows*rings))]
    for row in range(rows-1):
        for i in range(rings):
            j=(i+1)%rings
            faces.append((row*rings+i,row*rings+j,(row+1)*rings+j,(row+1)*rings+i))
    obj=mesh(SKIRT,points,faces,material)
    for face in obj.data.polygons:
        face.use_smooth=len(face.vertices)==4


def segment(index,material):
    rows,columns=81,17
    centre=math.tau*index/12
    points=[]
    for inner in [False,True]:
        for row in range(rows):
            z=.045+.175*row/(rows-1)
            groove=.012*(math.exp(-((z-.103)/.008)**4)+math.exp(-((z-.165)/.008)**4))
            r=profile_radius(PROFILE,z)+(-.010 if inner else .016-groove)
            for col in range(columns):
                phi=centre-.22+.44*col/(columns-1)
                points.append((r*math.cos(phi),r*math.sin(phi),z))
    n=rows*columns
    faces=[]
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col
            f=(a,a+1,a+columns+1,a+columns)
            faces.extend([f,tuple(n+i for i in reversed(f))])
    border=list(range(columns))+[r*columns+columns-1 for r in range(1,rows)]
    border+=list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))
    border+=[r*columns for r in reversed(range(1,rows-1))]
    for a,b in zip(border,border[1:]+border[:1]):
        faces.append((a,a+n,b+n,b))
    mesh(f'RI23 bronze skirt segment {index:02}',points,faces,material)


def selected_view(view):
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    return [o for o in objects if o.name==SKIRT or o.name.startswith('RI23 bronze skirt segment')] if view=='skirt-detail' else objects


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    MEDIA.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene,root=bpy.context.scene,bpy.data.objects['PlacementRoot']
    original={o.name for o in scene.objects if o.type=='MESH'}
    bronze=bpy.data.objects[SKIRT].data.materials[0]
    recessed=finish_material(bronze,'RI23 | worn recessed bronze skirt',(.23,.16,.065),'recessed-skirt-finish.png')
    removed=[]
    for obj in list(scene.objects):
        if obj.name.startswith('RI23 lower base inset'):
            removed.append(obj.name)
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.objects.remove(bpy.data.objects[SKIRT],do_unlink=True)
    skirt(recessed)
    for index in range(12):
        segment(index,bronze)
    added=[o.name for o in scene.objects if o.type=='MESH' and o.name not in original]
    modified=[SKIRT]
    for obj in scene.objects:
        if obj.type!='MESH' or obj.name not in set(modified+added):
            continue
        obj.parent=root
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data);bm.free()
        uv(obj)
        bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE')
        mod.keep_custom_normals=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    collection=bpy.data.collections.new('Ultrathermal Lance refined complete editable source')
    scene.collection.children.link(collection)
    for previous in bpy.data.collections:
        if previous.asset_data:
            previous.asset_clear()
    for obj in list(scene.objects):
        if obj.type in ['MESH','EMPTY']:
            collection.objects.link(obj)
            for previous in list(obj.users_collection):
                if previous!=collection:
                    previous.objects.unlink(obj)
    collection.asset_mark()
    scene.render.resolution_x=scene.render.resolution_y=768
    scene.render.resolution_percentage=100
    scene.render.film_transparent=True
    scene.render.image_settings.color_mode='RGBA'
    scene.cycles.samples=32
    fit_camera(VIEWS['front-quarter'],selected_view('front-quarter'))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:
            obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT/'model.glb'),export_format='GLB',use_selection=True,
                             export_apply=True,export_extras=True,export_animations=False)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/'model.blend'))
    for view,direction in VIEWS.items():
        fit_camera(direction,selected_view(view))
        scene.render.filepath=str(MEDIA/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    meta=dict(issue=185,id='openfa:building/legacy/062',culture='rigellian',name='Ultrathermal Lance',
              stage='visible-base-refinement',source_study=SOURCE.relative_to(ROOT).as_posix(),
              source_blend_sha256=sha(SOURCE),blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),
              generator_sha256=sha(Path(__file__)),preserved_objects=sorted(original-set(removed)-set(modified)),
              modified_objects=modified,removed_objects=removed,added_objects=added,
              views=list(VIEWS),blender=bpy.app.version_string,
              lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
              reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-building-references.json'),
              functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
              dependency_sha256={name:sha(Path(__file__).with_name(name)) for name in
                  ['rigellian_ultrathermal_lance_parts.py','manufactured_vessels.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']},
              texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in TEXTURES.glob('*.png')},
              observed=['Tapered segmented bronze lower bowl under fixed green pedestal; retained asymmetric side spur',
                        'Paired lances across sixteen correctly positioned overlays; same separation and elevation retained'],
              inferred=['Twelve cast segments, exact groove counts, base curve and hidden construction remain authored interpretations',
                        'New quarter-view camera exposes both lances without asserting recovered sprite calibration',
                        'Yaw rig and tip sockets retained; no unverified firing, pitch or idle animation introduced'],
              acceptance='Visible-base refinement; final artistic acceptance and game calibration remain open')
    (OUTPUT/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('RI23_SEGMENTED_BASE_REFINED',len([o for o in scene.objects if o.type=='MESH']),flush=True)


if __name__=='__main__':
    main()
