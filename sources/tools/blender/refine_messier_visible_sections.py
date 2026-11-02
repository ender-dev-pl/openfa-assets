"""RI2C: broad body fields, curved hull and a recessed copper termination."""
import json
import math
from pathlib import Path
import sys
import bmesh
import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import messier_lukannon_parts as old
from refine_lazzaro_visible_forms import interpolate
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'sources/docs/assets/reconstruction/ships/rigellian/messier-lukannon/model.blend'
REL=Path('docs/assets/reconstruction/rigellian-refined/messier-lukannon')
OUTPUT,MEDIA=ROOT/'sources'/REL,ROOT/'gallery/media'/REL
TEXTURES=ROOT/'sources/materials/reconstruction/rigellian-refined/messier-lukannon'
HULL='Messier-Lukannon flattened slate hull'
TERMINAL='Messier-Lukannon copper terminal'
VIEWS={'front-quarter':(7,-12,9),'rear-quarter':(-7,12,8),'top':(0,0,20),
       'side':(16,0,4),'terminal-detail':(3,-15,5)}
RING=[(-1.785,.20,0,.205,.145,.150),(-1.76,.225,0,.220,.150,.155),
      (-1.62,.25,.02,.220,.150,.155),(-1.42,.25,.04,.200,.120,.120)]


def section(y):
    return interpolate(old.SECTIONS,max(old.SECTIONS[0][0],min(old.SECTIONS[-1][0],y)))


def skin(x,y):
    w,z,h=section(y)
    return z+h*math.sqrt(max(0,1-(x/w)**2))-old.dent(x,y)


def side_skin(y,z,original=False):
    w,cz,h=old.section(y) if original else section(y)
    return w*math.sqrt(max(0,1-((z-cz)/h)**2))


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


def terminal(copper,dark):
    rows,rings=81,96
    points=[]
    for inner in [False,True]:
        profile=[(r[0],r[4] if inner else r[1],r[2],r[5] if inner else r[3]) for r in RING]
        for row in range(rows):
            y=RING[0][0]+(RING[-1][0]-RING[0][0])*row/(rows-1)
            w,z,h=interpolate(profile,y)
            for i in range(rings):
                phi=math.tau*i/rings
                points.append((w*math.cos(phi),y,z+h*math.sin(phi)))
    size=rows*rings
    faces=[]
    for row in range(rows-1):
        for i in range(rings):
            j=(i+1)%rings
            f=(row*rings+i,row*rings+j,(row+1)*rings+j,(row+1)*rings+i)
            faces.extend([f,tuple(size+k for k in reversed(f))])
    for row in [0,rows-1]:
        for i in range(rings):
            j=(i+1)%rings
            a,b=row*rings+i,row*rings+j
            faces.append((a,b,b+size,a+size))
    obj=mesh(TERMINAL,points,faces,copper)
    for face in obj.data.polygons:
        face.use_smooth=True
    points=[]
    for y in [-1.622,-1.610]:
        for i in range(rings):
            phi=math.tau*i/rings
            points.append((.16*math.cos(phi),y,.02+.16*math.sin(phi)))
    faces=[tuple(reversed(range(rings))),tuple(range(rings,2*rings))]
    for i in range(rings):
        j=(i+1)%rings
        faces.append((i,j,rings+j,rings+i))
    mesh('RI2C recessed dark terminal face',points,faces,dark)


def green_field(side,material):
    rows,columns=81,25
    top=[]
    for row in range(rows):
        t=row/(rows-1)
        y=.08+1.19*t
        width=section(y)[0]
        for col in range(columns):
            u=.35+.39*col/(columns-1)
            x=side*width*u
            top.append((x,y,skin(x,y)+.006))
    n=len(top)
    points=top+[(x,y,z-.018) for x,y,z in top]
    faces=[]
    for row in range(rows-1):
        for col in range(columns-1):
            a=row*columns+col
            f=(a,a+1,a+columns+1,a+columns)
            faces.extend([f,tuple(n+i for i in reversed(f))])
    edge=list(range(columns))+[r*columns+columns-1 for r in range(1,rows)]
    edge+=list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))
    edge+=[r*columns for r in reversed(range(1,rows-1))]
    for a,b in zip(edge,edge[1:]+edge[:1]):
        faces.append((a,a+n,b+n,b))
    obj=mesh('RI2C green aft body field '+str(side),points,faces,material)
    for face in obj.data.polygons:
        face.use_smooth=True


def selected_view(view):
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    if view=='terminal-detail':
        return [o for o in objects if o.name in [TERMINAL,'RI2C recessed dark terminal face']]
    return objects


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    MEDIA.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene,root=bpy.context.scene,bpy.data.objects['PlacementRoot']
    original={o.name for o in scene.objects if o.type=='MESH'}
    hull=bpy.data.objects[HULL]
    copper=bpy.data.objects[TERMINAL].data.materials[0]
    dark=bpy.data.materials['Messier-Lukannon | soot graphite']
    green=finish_material(hull.data.materials[0],'RI2C | worn green aft fields',(.18,.30,.22),'green-body-fields.png')
    for v in hull.data.vertices:
        x,y,z=v.co
        y=max(old.SECTIONS[0][0],min(old.SECTIONS[-1][0],y))
        ow,oz,oh=old.section(y)
        nw,nz,nh=section(y)
        depth=old.dent(x,y) if z>.08 else 0
        v.co.x=x*nw/ow
        v.co.z=nz+(z+depth-oz)*nh/oh
        if v.co.z>.08:
            v.co.z-=old.dent(v.co.x,y)
    modified=[HULL,TERMINAL]
    for obj in scene.objects:
        if obj.type!='MESH' or obj.name in [HULL,TERMINAL] or 'ventral wing' in obj.name:
            continue
        inverse=obj.matrix_world.inverted()
        for v in obj.data.vertices:
            p=obj.matrix_world@v.co
            if 'side boss' in obj.name:
                side=1 if p.x>0 else -1
                p.x+=side*(side_skin(p.y,p.z)-side_skin(p.y,p.z,True))
            else:
                p.z+=skin(p.x,p.y)-old.skin(p.x,p.y)
            v.co=inverse@p
        modified.append(obj.name)
    bpy.data.objects.remove(bpy.data.objects[TERMINAL],do_unlink=True)
    terminal(copper,dark)
    for side in [-1,1]:
        green_field(side,green)
    added=['RI2C recessed dark terminal face']+['RI2C green aft body field '+str(s) for s in [-1,1]]
    for obj in scene.objects:
        if obj.type!='MESH' or obj.name not in set(modified+added):
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
    collection=bpy.data.collections.new('Messier refined complete editable source')
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
    meta=dict(issue=185,id='openfa:ship/rigellian/messier-lukannon',culture='rigellian',name='Messier-Lukannon',
              stage='visible-section-refinement',source_study=SOURCE.relative_to(ROOT).as_posix(),
              source_blend_sha256=sha(SOURCE),blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),
              generator_sha256=sha(Path(__file__)),preserved_objects=sorted(original-set(modified)),
              modified_objects=modified,removed_objects=[],added_objects=added,
              views=list(VIEWS),blender=bpy.app.version_string,
              lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
              reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/ship-reference-index.json'),
              dependency_sha256={name:sha(Path(__file__).with_name(name)) for name in
                  ['messier_lukannon_parts.py','refine_lazzaro_visible_forms.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']},
              texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in TEXTURES.glob('*.png')},
              observed=['Broad flattened hull, green aft colour regions and copper end with dark central region across 32 RI2C headings',
                        'Swept ventral projections and copper side bosses retained after all-heading review'],
              inferred=['Physical end recess, exact depth, hidden sections and green field boundaries are authored interpretations',
                        'No engine/weapon function or recovered alloy identity; CDB architecture provides cultural context only'],
              acceptance='Static visible-section refinement; final artistic acceptance and game calibration remain open')
    (OUTPUT/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('MESSIER_VISIBLE_SECTIONS_REFINED',len([o for o in scene.objects if o.type=='MESH']),flush=True)


if __name__=='__main__':
    main()
