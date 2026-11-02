"""RI1C: broad conformal gold sides, lower slate casing and rounded copper masses."""
import json
import math
from pathlib import Path
import sys
import bmesh
import bpy
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import delphini_assault_parts as old
from refine_lazzaro_visible_forms import interpolate
from refine_rigellian_crowns import fit_camera, sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv
ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'sources/docs/assets/reconstruction/ships/rigellian/delphini-assault/model.blend'
REL = Path('docs/assets/reconstruction/rigellian-refined/delphini-assault')
OUTPUT, MEDIA = ROOT/'sources'/REL, ROOT/'gallery/media'/REL
TEXTURES = ROOT/'sources/materials/reconstruction/rigellian-refined/delphini-assault'
HULL = 'Delphini Assault rounded green hull'
VIEWS = {'front-quarter': (7,-12,9), 'rear-quarter': (-7,12,8), 'top': (0,0,20),
         'side': (16,0,4), 'underside': (5,-8,-12)}


def section(y):
    return interpolate(old.SECTIONS, y)


def skin(x,y):
    w,z,h=section(y)
    return z+h*math.sqrt(max(0,1-(x/w)**2))-old.dent(x,y)


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


def curved_shell(name, side, y0, y1, phi0, phi1, material):
    rows, columns = 101, 49
    points = []
    for offset in [.007, -.012]:
        for row in range(rows):
            y=y0+(y1-y0)*row/(rows-1)
            w,z,h=section(y)
            for col in range(columns):
                phi=phi0+(phi1-phi0)*col/(columns-1)
                x=side*(w+offset)*math.cos(phi)
                height=z+(h+offset)*math.sin(phi)
                if height>.08:
                    height-=old.dent(x,y)
                points.append((x,y,height))
    size=rows*columns
    faces=[]
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col
            f=(a,a+1,a+columns+1,a+columns)
            faces.extend([f,tuple(size+i for i in reversed(f))])
    border=list(range(columns))+[r*columns+columns-1 for r in range(1,rows)]
    border+=list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))
    border+=[r*columns for r in reversed(range(1,rows-1))]
    for a,b in zip(border,border[1:]+border[:1]):
        faces.append((a,a+size,b+size,b))
    obj=mesh(name,points,faces,material)
    for face in obj.data.polygons:
        face.use_smooth=True
    return obj


def pod(side, material):
    rows,rings=161,64
    points=[]
    for row in range(rows):
        y=old.POD_SECTIONS[0][0]+(old.POD_SECTIONS[-1][0]-old.POD_SECTIONS[0][0])*row/(rows-1)
        w,z,h=interpolate(old.POD_SECTIONS,y)
        for i in range(rings):
            phi=math.tau*i/rings
            points.append((side*.50+w*math.cos(phi),y,z+h*math.sin(phi)))
    faces=[tuple(reversed(range(rings))),tuple(range((rows-1)*rings,rows*rings))]
    for row in range(rows-1):
        for i in range(rings):
            j=(i+1)%rings
            faces.append((row*rings+i,row*rings+j,(row+1)*rings+j,(row+1)*rings+i))
    obj=mesh('Delphini Assault brown ventral body '+str(side),points,faces,material)
    for face in obj.data.polygons:
        face.use_smooth=len(face.vertices)==4
    return obj


def selected_view(view):
    return [o for o in bpy.context.scene.objects if o.type=='MESH']


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    MEDIA.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene,root=bpy.context.scene,bpy.data.objects['PlacementRoot']
    original={o.name for o in scene.objects if o.type=='MESH'}
    removed=[]
    for obj in list(scene.objects):
        if obj.name.startswith('Delphini Assault ventral fitting'):
            removed.append(obj.name)
            bpy.data.objects.remove(obj,do_unlink=True)
    hull=bpy.data.objects[HULL]
    bronze=bpy.data.objects['Delphini Assault brown ventral body -1'].data.materials[0]
    copper=finish_material(bronze,'RI1C | aged copper lower casings',(.30,.145,.085),'copper-casings.png')
    gold=finish_material(bronze,'RI1C | worn gold side fields',(.45,.34,.095),'gold-fields.png')
    slate=finish_material(hull.data.materials[0],'RI1C | worn slate lower skin',(.12,.16,.205),'lower-slate.png')
    modified=[HULL,'Delphini Assault brown tail detail']
    for v in hull.data.vertices:
        x,y,z=v.co
        ow,oz,oh=old.section(y)
        nw,nz,nh=section(y)
        depth=old.dent(x,y) if z>.08 else 0
        v.co.x=x*nw/ow
        v.co.z=nz+(z+depth-oz)*nh/oh
        if v.co.z>.08:
            v.co.z-=old.dent(v.co.x,y)
    tail=bpy.data.objects['Delphini Assault brown tail detail']
    tail.data.materials.clear()
    tail.data.materials.append(copper)
    for obj in scene.objects:
        if not obj.name.startswith(('Delphini Assault green service cover','Delphini Assault service slot')):
            continue
        inverse=obj.matrix_world.inverted()
        for v in obj.data.vertices:
            p=obj.matrix_world@v.co
            p.z+=skin(p.x,p.y)-old.skin(p.x,p.y)
            v.co=inverse@p
        modified.append(obj.name)
    for side in [-1,1]:
        names=['Delphini Assault brown ventral body '+str(side),'Delphini Assault gold upper patch '+str(side)]
        for name in names:
            bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
        pod(side,copper)
        curved_shell(names[1],side,-.34,.44,.30,1.02,gold)
        modified.extend(names)
    curved_shell('RI1C lower slate casing',1,-1.365,1.165,math.pi,2*math.pi,slate)
    changed=set(modified)|{'RI1C lower slate casing'}
    for obj in scene.objects:
        if obj.type!='MESH' or obj.name not in changed:
            continue
        obj.parent=root
        obj.data.normals_split_custom_set([(0,0,0)]*len(obj.data.loops))
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data);bm.free()
        uv(obj)
        bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE')
        mod.keep_custom_normals=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    collection=bpy.data.collections.new('Delphini refined complete editable source')
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
    meta=dict(issue=185,id='openfa:ship/rigellian/delphini-assault',culture='rigellian',name='Delphini Assault',
              stage='visible-section-refinement',source_study=SOURCE.relative_to(ROOT).as_posix(),
              source_blend_sha256=sha(SOURCE),blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),
              generator_sha256=sha(Path(__file__)),preserved_objects=sorted(original-set(removed)-set(modified)),
              modified_objects=modified,removed_objects=removed,added_objects=['RI1C lower slate casing'],
              views=list(VIEWS),blender=bpy.app.version_string,
              lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
              reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/ship-reference-index.json'),
              dependency_sha256={name:sha(Path(__file__).with_name(name)) for name in
                  ['delphini_assault_parts.py','refine_lazzaro_visible_forms.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']},
              texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in TEXTURES.glob('*.png')},
              observed=['Elongated gold side fields, green upper body, slate lower casing and separate copper lower masses across all 32 RI1C headings'],
              inferred=['Exact shell sections, material identities and lower attachment construction','CDB ergonomic/elegant architecture provides context rather than recovered ship mechanisms'],
              acceptance='Static visible-section refinement; final artistic acceptance and gameplay calibration remain open')
    (OUTPUT/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('DELPHINI_VISIBLE_SECTIONS_REFINED',len([o for o in scene.objects if o.type=='MESH']),flush=True)


if __name__=='__main__':
    main()
