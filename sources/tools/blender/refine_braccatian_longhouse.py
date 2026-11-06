"""Recover BR06's joined terraced halls, open entrance arches and red-collared towers."""
import argparse
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
import refine_braccatian_pithoi as authored
from build_openfa_assets import setup_scene,box,finish
from manufactured_vessels import vessel
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
VIEWS={'front-quarter':(6,-13,7),'front':(0,-16,4),'side':(16,0,4),
       'rear-quarter':(-7,12,7),'entrance-detail':(2,-13,3)}
CENTRES=[-.72,0,.72]
HEIGHTS=[2.23,2.04,1.85]


def source():return ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/braccatian/br06/model.blend'


def folders():
    rel=Path('docs/assets/reconstruction/braccatian-refined/br06')
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def selected(view):
    return [o for o in bpy.context.scene.objects if o.type=='MESH' and
            (view!='entrance-detail' or 'hall' in o.name or 'entrance' in o.name or 'link' in o.name)]


def square_loft(name,profile,mat):
    # A square terraced tower rather than a generic circular cone.
    vertices=[(sx*r,sy*r,z) for z,r in profile for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    faces=[(3,2,1,0)]+[(4*j+i,4*j+(i+1)%4,4*(j+1)+(i+1)%4,4*(j+1)+i)
      for j in range(len(profile)-1) for i in range(4)]
    faces.append(tuple(4*(len(profile)-1)+i for i in range(4)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=5,use_grid_fill=True)
    for vertex in bm.verts:
        x,y,z=vertex.co
        radius=next((ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(profile,profile[1:]) if za-1e-6<=z<=zb+1e-6),None)
        if radius and abs(y+radius)<1e-5:
            vertex.co.y += .0025*math.exp(-2*((x/.13)**2+((z-.90)/.16)**2))
    bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    return finish(obj,name,mat,.007)


def tower_profile(height):
    return [(.46,.30),(.64,.27),(.66,.245),(1.02,.205),(1.04,.18),
            (height-.43,.125),(height-.41,.105),(height-.08,.075),(height,.065)]


def arch(name,x,mat):
    # Extruded non-convex arch section: the opening is empty geometry, not a decal.
    outer=[(-.30,0)]+[(.30*math.cos(a),.17+.30*math.sin(a)) for a in [math.pi-i*math.pi/32 for i in range(33)]]+[(.30,0)]
    inner=[(.16,0)]+[(.16*math.cos(a),.17+.16*math.sin(a)) for a in [i*math.pi/32 for i in range(33)]]+[(-.16,0)]
    polygon=outer+inner;n=len(polygon)
    vertices=[(x+px,y,z) for y in [-.79,-.30] for px,z in polygon]
    faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    return finish(obj,name,mat,.006)


def build(m):
    box('BR06 rear hall connecting lintel',(0,.25,.36),(2.20,.30,.22),m['rose-casing'],.012)
    for i,(x,height) in enumerate(zip(CENTRES,HEIGHTS)):
        p=f'BR06 segment {i} '
        box(p+'hall rear chamber',(x,.08,.23),(.68,.78,.46),m['gold-casting'],.012)
        box(p+'hall broad rose terrace',(x,-.16,.465),(.73,1.34,.09),m['rose-casing'],.013)
        box(p+'hall gold roof inset',(x,-.13,.511),(.62,1.15,.035),m['gold-casting'],.009)
        arch(p+'entrance open rose arch',x,m['rose-casing'])
        for sign in [-1,1]:
            box(p+f'entrance gold jamb fitting {sign}',(x+sign*.237,-.796,.115),(.052,.026,.14),m['gold-casting'],.005)
            for j,y in enumerate([-.16,.08,.32]):
                box(p+f'hall side pale field {sign} {j}',(x+sign*.342,y,.24),(.025,.085,.14),m['pale-gold'],.004)
        profile=tower_profile(height)
        obj=square_loft(p+'terraced gold tower',profile,m['gold-casting']);obj.location=(x,.12,0)
        obj.data.materials.append(m['rose-casing'])
        for face in obj.data.polygons:
            if face.normal.x>.7:face.material_index=1
        # Rose casings on the two exposed vertical corner bands follow the stepped profile.
        for sign in [-1,1]:
            strip=[(z,r+.008) for z,r in profile]
            verts=[]
            for z,r in strip:
                xx=sign*r
                verts += [(xx-sign*.055,-r-.002,z),(xx+sign*.006,-r-.002,z),
                          (xx+sign*.006,-r+.025,z),(xx-sign*.055,-r+.025,z)]
            faces=[(3,2,1,0)]+[(4*j+k,4*j+(k+1)%4,4*(j+1)+(k+1)%4,4*(j+1)+k)
                for j in range(len(strip)-1) for k in range(4)]
            faces.append(tuple(4*(len(strip)-1)+k for k in range(4)))
            mesh=bpy.data.meshes.new(p+'stepped rose corner');mesh.from_pydata(verts,[],faces);mesh.update()
            obj=bpy.data.objects.new(p+f'stepped rose corner {sign}',mesh);bpy.context.collection.objects.link(obj)
            finish(obj,obj.name,m['rose-casing'],0);obj.location=(x,.12,0)
        obj=vessel(p+'red upper collar',[(height-.08,.075),(height-.055,.145),(height+.045,.145),(height+.075,.055)],m['red-field'],[])
        obj.location=(x,.12,0)
        obj=vessel(p+'gold upper handle',[(height+.04,.036),(height+.30,.034),(height+.32,.018)],m['gold-casting'],[])
        obj.location=(x,.12,0)
        # Three broad pale/gold face fittings visible on the terraced shaft.
        for j,z in enumerate([.83,1.18,1.48]):
            if z>height-.22:continue
            r=next(ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(profile,profile[1:]) if za<=z<=zb)
            box(p+f'tower front field {j}',(x,-r+.116,z),(.070,.025,.085),m['pale-gold'],.004)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=['br06'],default='br06')
    parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    output,media=folders();output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    original=json.loads(source().with_suffix('.json').read_text());assert original['global_type']==68
    scene=setup_scene(768,32)
    collection=bpy.data.collections.new('Longhouse complete editable terraced assembly');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/braccatian-refined/br06'
    materials={}
    for style,colour,metal in [('rose-casing',(.48,.235,.17),.65),('gold-casting',(.48,.33,.115),.76),
         ('red-field',(.42,.025,.018),.55),('pale-gold',(.68,.51,.24),.60)]:
        materials[style]=authored.worn_material(style,colour,metal);materials[style].name='BR06 | worn '+style
    build(materials)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']='openfa:building/legacy/068';root['footprint_width'],root['footprint_height']=original['footprint']
    objects=[o for o in scene.objects if o.type=='MESH']
    for obj in objects:
        obj.parent=root;bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        uv(obj)
        modifier=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE');modifier.keep_custom_normals=True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    collection.asset_mark();collection.asset_data.description='Longhouse: linked terraced dwellings and open arches; hidden construction authored'
    for view,direction in VIEWS.items():
        fit_camera(direction,selected(view));scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    fit_camera(VIEWS['front-quarter'],objects)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects+[root]:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    dependencies=['refine_braccatian_pithoi.py','refine_braccatian_vessels.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=190,id=root['catalogue_id'],name='Longhouse',culture='braccatian',stage='joined-terraced-longhouse-refinement',
      source_study=source().relative_to(ROOT).as_posix(),source_blend_sha256=sha(source()),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),
      dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in dependencies},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},
      lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json'),functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
      observed=['All 41 paletted catalogue phases and both surface descriptors inspected','Three linked low halls with rose terraces and arched entrances; descending terraced towers with red upper collars and single gold tips','Numerous extended-family living quarters per original functional narrative'],
      inferred=['Exact tower profiles, spatial arrangement, hidden rear connection, entrance depth and repeated fitting counts','No universal bronze alloy or symbolic clan ornament established'],
      geometry_policy='New assembly; old generic towers preserved separately',mesh_objects=len(objects),views=list(VIEWS),blender=bpy.app.version_string,
      acceptance='Actual source-led assembly; final artistic and gameplay calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('BRACCATIAN_LONGHOUSE_REFINED',len(objects),flush=True)


if __name__=='__main__':main()
