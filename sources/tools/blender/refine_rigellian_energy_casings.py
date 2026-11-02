"""RI14: readable horizontal/vertical bronze casing divisions beside the pale conduit."""
import json
import math
from pathlib import Path
import sys
import bmesh
import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from rigellian_energy_gatherer_parts import PROFILES,profile_radius
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'sources/docs/assets/reconstruction/buildings/rigellian/energy-gatherer/model.blend'
REL=Path('docs/assets/reconstruction/rigellian-refined/ri14')
OUTPUT,MEDIA=ROOT/'sources'/REL,ROOT/'gallery/media'/REL
TEXTURES=ROOT/'sources/materials/reconstruction/rigellian-refined/ri14'
BODY='RI14 twin chamber lower body'
PHI0,PHI1=-2.52,-1.23
VIEWS={'front-quarter':(6,-13,8),'front':(0,-16,4),'side':(16,0,4),
       'rear-quarter':(-7,12,7),'casing-detail':(4,-14,4)}


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


def sector(name,z0,z1,phi0,phi1,inside,outside,material):
    rows,columns=33,49
    points=[]
    for offset in [outside,inside]:
        for row in range(rows):
            z=z0+(z1-z0)*row/(rows-1)
            r=profile_radius(PROFILES[BODY],z)+offset
            for col in range(columns):
                phi=phi0+(phi1-phi0)*col/(columns-1)
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
    return mesh(name,points,faces,material)


def selected_view(view):
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    return [o for o in objects if 'refined casing' in o.name] if view=='casing-detail' else objects


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    MEDIA.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene,root=bpy.context.scene,bpy.data.objects['PlacementRoot']
    original={o.name for o in scene.objects if o.type=='MESH'}
    removed=[]
    for obj in list(scene.objects):
        if obj.name.startswith(('RI14 service panel','RI14 service inset','RI14 panel captive fastener')):
            removed.append(obj.name)
            bpy.data.objects.remove(obj,do_unlink=True)
    bronze=bpy.data.objects[BODY].data.materials[0]
    recessed=finish_material(bronze,'RI14 | worn recessed bronze casing',(.24,.18,.075),'recessed-bronze-finish.png')
    sector('RI14 refined casing lower backing',.13,.66,PHI0,PHI1,-.015,.020,recessed)
    sector('RI14 refined casing upper backing',.99,1.49,PHI0,PHI1,-.015,.020,recessed)
    for i,z in enumerate([1.05,1.23,1.41]):
        sector(f'RI14 refined casing upper horizontal rib {i}',z-.033,z+.033,PHI0+.03,PHI1-.03,.005,.048,bronze)
    for i,(a,b) in enumerate([(-2.45,-2.22),(-2.05,-1.82),(-1.66,-1.43)]):
        sector(f'RI14 refined casing lower vertical rib {i}',.18,.62,a,b,.005,.048,bronze)
    added=[o.name for o in scene.objects if o.type=='MESH' and o.name not in original]
    for obj in scene.objects:
        if obj.type!='MESH' or obj.name not in added:
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
    collection=bpy.data.collections.new('Energy Gatherer refined complete editable source')
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
    meta=dict(issue=185,id='openfa:building/legacy/053',culture='rigellian',name='Energy Gatherer',
              stage='visible-casing-refinement',source_study=SOURCE.relative_to(ROOT).as_posix(),
              source_blend_sha256=sha(SOURCE),blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),
              generator_sha256=sha(Path(__file__)),preserved_objects=sorted(original-set(removed)),
              modified_objects=[],removed_objects=removed,added_objects=added,
              views=list(VIEWS),blender=bpy.app.version_string,
              lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
              reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-building-references.json'),
              functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
              dependency_sha256={name:sha(Path(__file__).with_name(name)) for name in
                  ['rigellian_energy_gatherer_parts.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']},
              texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in TEXTURES.glob('*.png')},
              observed=['Upper bronze chamber has broad horizontal divisions; lower chamber has pronounced vertical sections',
                        'Pale front conduit, grey connector and open upper crown retained after surface/all-phase review'],
              inferred=['Three ribs per chamber, exact casing profiles and material identity remain authored interpretations',
                        'Legacy deliberately leaves power-generation method unexplained; no reactor or operational loop invented'],
              acceptance='Visible-casing refinement; final artistic acceptance and game calibration remain open')
    (OUTPUT/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('RI14_CASINGS_REFINED',len([o for o in scene.objects if o.type=='MESH']),flush=True)


if __name__=='__main__':
    main()
