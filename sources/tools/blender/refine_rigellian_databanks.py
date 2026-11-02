"""RI08: restore the readable pale perforated upper equipment casing."""
import json
import math
from pathlib import Path
import sys
import bmesh
import bpy
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from rigellian_databanks_parts import HEAD,radius
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_extractor import mesh,box
from refine_rigellian_missiles import uv
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'sources/docs/assets/reconstruction/buildings/rigellian/databanks/model.blend'
REL=Path('docs/assets/reconstruction/rigellian-refined/ri08')
OUTPUT,MEDIA=ROOT/'sources'/REL,ROOT/'gallery/media'/REL
TEXTURES=ROOT/'sources/materials/reconstruction/rigellian-refined/ri08'
HEAD_NAME='RI08 rounded upper head'
PANEL='RI08 pale perforated equipment casing'
PORTS=[(phi,z) for z in [2.43,2.62] for phi in [-math.pi/2-.66,-math.pi/2-.22,-math.pi/2+.22,-math.pi/2+.66]]
VIEWS={'front-quarter':(6,-13,8),'front':(0,-16,4),'side':(16,0,4),
       'rear-quarter':(-7,12,7),'head-detail':(4,-14,6)}


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


def casing(material):
    rows,columns=73,97
    points=[]
    for offset in [.018,-.020]:
        for row in range(rows):
            z=2.335+.425*row/(rows-1)
            r=radius(HEAD,z)+offset
            for col in range(columns):
                phi=-math.pi/2-.96+1.92*col/(columns-1)
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
    obj=mesh(PANEL,points,faces,material)
    for face in obj.data.polygons:
        face.use_smooth=True
    return obj


def selected_view(view):
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    if view=='head-detail':
        return [o for o in objects if o.name in [HEAD_NAME,PANEL] or o.name.startswith('RI08 broad equipment port')]
    return objects


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    MEDIA.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene,root=bpy.context.scene,bpy.data.objects['PlacementRoot']
    original={o.name for o in scene.objects if o.type=='MESH'}
    removed=[]
    for obj in list(scene.objects):
        if obj.name.startswith('RI08 head captive dark fastener'):
            removed.append(obj.name)
            bpy.data.objects.remove(obj,do_unlink=True)
    head=bpy.data.objects[HEAD_NAME]
    pale=finish_material(head.data.materials[0],'RI08 | worn pale upper equipment shell',(.40,.46,.43),'pale-head-finish.png')
    dark=bpy.data.materials['RI08 | recessed equipment']
    panel=casing(pale)
    for i,(phi,z) in enumerate(PORTS):
        normal=Vector((math.cos(phi),math.sin(phi),0))
        centre=normal*.43;centre.z=z
        cutter=box('Temporary RI08 broad port cutter',centre,(.074,.20,.10),dark,.006)
        cutter.rotation_euler.z=phi-math.pi/2
        for target in [head,panel]:
            bpy.context.view_layer.objects.active=target
            mod=target.modifiers.new('Physical upper equipment recess','BOOLEAN')
            mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
            bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
        centre=normal*.338;centre.z=z
        backing=box(f'RI08 broad equipment port {i} dark backing',centre,(.067,.034,.088),dark,.003)
        backing.rotation_euler.z=phi-math.pi/2
    added=[o.name for o in scene.objects if o.type=='MESH' and o.name not in original]
    modified=[HEAD_NAME]
    for obj in scene.objects:
        if obj.type!='MESH' or obj.name not in set(modified+added):
            continue
        obj.parent=root
        obj.data.normals_split_custom_set([(0,0,0)]*len(obj.data.loops))
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data);bm.free()
        uv(obj)
        bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE')
        mod.keep_custom_normals=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    collection=bpy.data.collections.new('Databanks refined complete editable source')
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
    meta=dict(issue=185,id='openfa:building/legacy/047',culture='rigellian',name='Databanks',
              stage='visible-equipment-refinement',source_study=SOURCE.relative_to(ROOT).as_posix(),
              source_blend_sha256=sha(SOURCE),blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),
              generator_sha256=sha(Path(__file__)),preserved_objects=sorted(original-set(removed)-set(modified)),
              modified_objects=modified,removed_objects=removed,added_objects=added,
              views=list(VIEWS),blender=bpy.app.version_string,
              lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
              reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-building-references.json'),
              functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
              dependency_sha256={name:sha(Path(__file__).with_name(name)) for name in
                  ['rigellian_databanks_parts.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']},
              texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in TEXTURES.glob('*.png')},
              equipment_ports=[dict(phi=phi,z=z) for phi,z in PORTS],
              observed=['Pale patterned upper equipment casing with dark recess-like squares in paletted surface and catalogue phase 20',
                        'Twin support rods, side equipment casing, silver fork and flared central/lower bodies retained'],
              inferred=['Eight-port layout, physical recess depth and hidden equipment purpose are authored interpretations',
                        'Catalogue reveal/highlights are not a mechanical opening sequence; no new process loop',
                        'CDB knowledge/research and ergonomic architecture provide context without specifying alloys'],
              acceptance='Visible-equipment refinement; final artistic acceptance and game calibration remain open')
    (OUTPUT/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('RI08_EQUIPMENT_REFINED',len([o for o in scene.objects if o.type=='MESH']),flush=True)


if __name__=='__main__':
    main()
