"""Recover distinct BR01/02/05 joined pyramids, cylindrical core, stepped neck and open crowns."""
import argparse
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import refine_braccatian_pithoi as authored
from refine_braccatian_vessels import band
from refine_braccatian_longhouse import square_loft
from refine_braccatian_public_facilities import pyramid_fitting
from manufactured_vessels import vessel,profile_radius
from build_openfa_assets import setup_scene,box,beam
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
CASES={'br01':(63,'First Step'),'br02':(64,'Clan Heart'),'br05':(67,"Aesir's Hall")}
VIEWS={'front-quarter':(6,-13,7),'front':(0,-16,4),'side':(16,0,4),'rear-quarter':(-7,12,7),'equipment-detail':(3,-13,4),'crown-detail':(5,-12,4)}
FIRST=[(0,.46,2.42),(-.49,-.02,2.10),(.49,-.02,2.10),(0,-.47,1.85)]
CLAN_SIDES=[(-.50,-.02,1.48),(.50,-.02,1.72),(0,-.49,1.22)]
AIR_SIDES=[(-.29,-.15),( .29,-.15),(0,.30)]
CLAN_CORE=[(0,.22),(.05,.29),(1.50,.29),(1.57,.32)]
AIR_CORE=[(0,.18),(.10,.23),(.30,.23),(.45,.18),(.54,.22),(.65,.24),(.75,.22),(.82,.10),(1.10,.10)]


def source(key):return ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/braccatian'/key/'model.blend'


def folders(key):
    rel=Path('docs/assets/reconstruction/braccatian-refined')/key
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def selected(view):
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    if view=='crown-detail':return [o for o in objects if 'crown' in o.name] or objects
    if view=='equipment-detail':return [o for o in objects if not any(s in o.name for s in ['crown','upper mast','single tip'])]
    return objects


def shift_new(before,xy):
    for obj in bpy.context.scene.objects:
        if obj.type=='MESH' and obj.name not in before:obj.location+=Vector((*xy,0))


def planar_solid(name,profile,polygon,material,front=-.018,back=.012):
    """Closed relief on the sloping planar front of a square pyramid."""
    vertices=[(x,-profile_radius(profile,z)+depth,z) for depth in [front,back] for x,z in polygon]
    n=len(polygon);faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vertices,faces,material,smooth=False)


def panel(name,profile,xr,zr,material,relief=.018):
    # Add explicit intermediate rows so relief follows any terraced profile.
    rows=sorted(set([zr[0],zr[1]]+[z for z,_ in profile if zr[0]<z<zr[1]]))
    polygon=[(xr[0],z) for z in rows]+[(xr[1],z) for z in reversed(rows)]
    return planar_solid(name,profile,polygon,material,front=-relief)


def pyramid(name,profile,m):
    obj=square_loft(name,profile,m['gold-casting']);obj.data.materials.append(m['rose-casing'])
    for face in obj.data.polygons:
        if face.normal.x>.7:face.material_index=1
    for sign in [-1,1]:
        rows=profile;vertices=[]
        for z,r in rows:
            x=sign*r
            vertices += [(x-sign*.042,-r-.008,z),(x+sign*.004,-r-.008,z),
                         (x+sign*.004,-r+.020,z),(x-sign*.042,-r+.020,z)]
        faces=[(3,2,1,0)]+[(4*j+i,4*j+(i+1)%4,4*(j+1)+(i+1)%4,4*(j+1)+i) for j in range(len(rows)-1) for i in range(4)]
        faces.append(tuple(4*(len(rows)-1)+i for i in range(4)))
        mesh(name+f' rose edge {sign}',vertices,faces,m['rose-casing'],smooth=False)
    return obj


def blue_terminal(name,height,m):
    vessel(name+' blue collar',[(height-.27,.045),(height-.24,.105),(height-.14,.105),(height-.10,.035)],m['blue-collar'],[])
    vessel(name+' single tip',[(height-.15,.032),(height+.14,.030),(height+.18,.012)],m['gold-casting'],[])


def recessed_portal(name,obj,profile,m):
    triangle=[(-.155,.035),(.155,.035),(0,.455)]
    cutter=planar_solid(name+' temporary recess cutter',profile,triangle,m['recess'],front=-.06,back=.115)
    # Apply the tower bevel before the closed shallow recess Boolean.
    bpy.context.view_layer.objects.active=obj
    for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
    boolean=obj.modifiers.new('Actual shallow entrance recess','BOOLEAN');boolean.operation='DIFFERENCE';boolean.solver='EXACT';boolean.object=cutter
    bpy.ops.object.modifier_apply(modifier=boolean.name);bpy.data.objects.remove(cutter,do_unlink=True)
    planar_solid(name+' dark recessed back',profile,triangle,m['recess'],front=.107,back=.13)
    # Raised structural frame encloses the recess; the pale divisions are visible geometry.
    for i,(a,b) in enumerate(zip(triangle,triangle[1:]+triangle[:1])):
        start=(a[0],-profile_radius(profile,a[1])-.014,a[1]);end=(b[0],-profile_radius(profile,b[1])-.014,b[1])
        beam(name+f' gold frame {i}',start,end,.021,m['gold-casting'])
    for i,(x,top) in enumerate([(-.085,.205),(0,.405),(.085,.205)]):
        panel(name+f' pale vertical grille {i}',profile,(x-.020,x+.020),(.05,top),m['pale-gold'],.024)
    for i,z in enumerate([.115,.205]):
        half=.155*(.455-z)/.420
        panel(name+f' gold crossbar {i}',profile,(-half,half),(z-.012,z+.012),m['gold-casting'],.031)


def first_step(m):
    for i,(x,y,height) in enumerate(FIRST):
        before={o.name for o in bpy.context.scene.objects};p=f'BR01 pyramid {i}'
        profile=[(0,.43),(.08,.43),(height-.30,.055),(height-.24,.035)]
        obj=pyramid(p,profile,m)
        blue_terminal(p,height,m)
        for j,z in enumerate([.60,.90,1.20]):
            if z>height-.48:continue
            panel(p+f' rose equipment surround {j}',profile,(-.068,.068),(z-.065,z+.065),m['rose-casing'],.012)
            panel(p+f' dark equipment field {j}',profile,(-.044,.044),(z-.038,z+.038),m['recess'],.022)
            panel(p+f' pale equipment centre {j}',profile,(-.020,.020),(z-.020,z+.020),m['pale-gold'],.030)
        if i in [1,3]:recessed_portal(p+' entrance',obj,profile,m)
        shift_new(before,(x,y))


def crown(prefix,z,spread,m):
    # Two thick, closed editable loop castings make an open crown, not a solid globe.
    vessel(prefix+' crown rose seating',[(z-.14,.030),(z-.08,.070),(z,.045),(z+.04,.027)],m['rose-casing'],[])
    vessel(prefix+' crown upper mast',[(z-.02,.024),(z+.52,.024),(z+.58,.010)],m['gold-casting'],[])
    count=96
    for axis in range(2):
        vertices=[]
        for depth in [-.018,.018]:
            for inner in [False,True]:
                for i in range(count):
                    phi=i*math.tau/count;rx=spread-(.033 if inner else 0);rz=.18-(.030 if inner else 0)
                    vertices.append((rx*math.cos(phi),depth,z+.23+rz*math.sin(phi)))
        faces=[]
        for i in range(count):
            j=(i+1)%count
            faces += [(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),
               (i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)]
        obj=mesh(prefix+f' crown open loop {axis}',vertices,faces,m['gold-casting'],smooth=False);obj.rotation_euler.z=axis*math.pi/2


def satellite(prefix,xy,height,half,m,blue=True,fitting=None):
    before={o.name for o in bpy.context.scene.objects}
    top=height-.24 if blue else height-.16
    profile=[(0,half),(.06,half),(top,.035)]
    pyramid(prefix,profile,m)
    if blue:blue_terminal(prefix,height,m)
    else:vessel(prefix+' single tip',[(top-.015,.026),(height,.026),(height+.035,.012)],m['gold-casting'],[])
    if fitting:
        # Front face of the simple, straight tapered wall.
        slope_half=half+(half-.035)*.06/(top-.06)
        def fit(name,z,radius,mat,inner=0,relief=.025):
            return pyramid_fitting(name,z,radius,top,slope_half,.035,mat,inner,relief)
        fit(prefix+' gold face rim',.25,.115,m['gold-casting'],.077)
        fit(prefix+' dark face backing',.25,.081,m['recess'],relief=.008)
        if fitting=='red':fit(prefix+' red face',.25,.069,m['red-field'],relief=.040)
        else:
            for j,(xx,z) in enumerate([(0,.305),(-.040,.22),(.040,.22)]):
                obj=fit(prefix+f' blue face {j}',z,.030,m['pale-blue'],relief=.040);obj.location.x=xx
    shift_new(before,xy)


def clan_heart(m):
    p='BR02 '
    vessel(p+'central cylindrical core',CLAN_CORE,m['gold-casting'],[(-1.8,.95,.003)])
    for i,(z0,z1) in enumerate([(.20,.27),(.67,.74),(1.12,1.19),(1.48,1.56)]):band(p+f'rose core band {i}',CLAN_CORE,z0,z1,m['rose-casing'])
    authored.patch(p+'dark front equipment field',CLAN_CORE,(-.21,.21),(.10,1.47),m['recess'],.008)
    for i,x in enumerate([-.12,.12]):
        for j,z in enumerate([.38,.85,1.33]):authored.patch(p+f'pale vertical face {i} {j}',CLAN_CORE,(x-.034,x+.034),(z-.09,z+.09),m['pale-blue'],.023)
    for i,z in enumerate([.19,.65,1.11]):authored.patch(p+f'gold front separator {i}',CLAN_CORE,(-.22,.22),(z-.020,z+.020),m['gold-casting'],.025)
    pyramid(p+'tall square roof',[(1.51,.37),(2.39,.035)],m)
    crown(p,2.49,.22,m)
    for i,(x,y,height) in enumerate(CLAN_SIDES):satellite(p+f'peripheral pyramid {i}',(x,y),height,.34,m,True,'blue' if i<2 else None)


def aesir(m):
    p='BR05 '
    vessel(p+'stepped air-system body',AIR_CORE,m['gold-casting'],[(-1.8,.40,.002)])
    for i,(z0,z1) in enumerate([(.22,.27),(.46,.51),(.65,.70)]):band(p+f'rose body collar {i}',AIR_CORE,z0,z1,m['rose-casing'])
    authored.patch(p+'dark lower service field',AIR_CORE,(-.085,.085),(.10,.69),m['recess'],.008)
    for i,z in enumerate([.17,.31,.45,.60]):authored.patch(p+f'gold lower service division {i}',AIR_CORE,(-.065,.065),(z-.025,z+.025),m['gold-casting'],.020)
    vessel(p+'rose narrow neck',[(.77,.105),(1.09,.105)],m['rose-casing'],[])
    pyramid(p+'broad-foot upper spire',[(1.04,.29),(1.96,.035)],m)
    crown(p,2.06,.19,m)
    for i,xy in enumerate(AIR_SIDES):satellite(p+f'low satellite {i}',xy,.83,.235,m,False,'red' if i==0 else 'blue' if i==1 else None)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;number,name=CASES[key];output,media=folders(key)
    old=json.loads(source(key).with_suffix('.json').read_text());assert old['global_type']==number
    output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True);scene=setup_scene(768,32)
    collection=bpy.data.collections.new(name+' complete editable joined complex');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/braccatian-refined'/key;materials={}
    for style,colour,metal in [('rose-casing',(.48,.235,.17),.65),('gold-casting',(.48,.33,.115),.76),('blue-collar',(.045,.09,.36),.62),
      ('red-field',(.42,.025,.018),.55),('recess',(.035,.028,.019),.48),('pale-gold',(.68,.51,.24),.60),('pale-blue',(.48,.61,.72),.62)]:
        materials[style]=authored.worn_material(style,colour,metal);materials[style].name=key.upper()+' | worn '+style
    {'br01':first_step,'br02':clan_heart,'br05':aesir}[key](materials)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']=f'openfa:building/legacy/{number:03}';root['footprint_width'],root['footprint_height']=old['footprint']
    objects=[o for o in scene.objects if o.type=='MESH']
    for obj in objects:
        obj.parent=root;bpy.context.view_layer.objects.active=obj
        if obj.name not in collection.objects:collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();uv(obj)
        modifier=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE');modifier.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=modifier.name)
    for mat in list(materials.values()):
        if not mat.users:bpy.data.materials.remove(mat)
    used={Path(n.image.filepath_raw) for mat in bpy.data.materials if mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    for path in authored.TEXTURES.glob('*.png'):
        if path not in used:path.unlink() # Only newly generated unused case maps.
    collection.asset_mark();collection.asset_data.description=name+' source-supported joined construction; hidden sections authored'
    for view,direction in VIEWS.items():
        if view=='crown-detail' and key=='br01':continue
        fit_camera(direction,selected(view));scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    fit_camera(VIEWS['front-quarter'],objects);bpy.ops.object.select_all(action='DESELECT')
    for obj in objects+[root]:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    dependencies=['refine_braccatian_pithoi.py','refine_braccatian_vessels.py','refine_braccatian_longhouse.py','refine_braccatian_public_facilities.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    observations={'br01':['Four joined gold/rose pyramidal bodies with blue collars and single gold tips, front face fittings and two bright triangular portal grilles','First-built CPU counterpart per original functional narrative'],
      'br02':['Tall cylindrical central core with shoulder bands/pale vertical faces, steep square roof, open gold crown and three distinct peripheral pyramids','Command centre and Council of Elders seat with high security; no invented weapons or clan emblems'],
      'br05':['Stepped body, narrow neck, broad-foot upper spire/open gold crown, three low satellites and red/blue face fittings','Air circulation only: functional text explicitly states no ceremonial aspect despite the name']}
    meta=dict(issue=190,id=root['catalogue_id'],name=name,culture='braccatian',stage='joined-clan-complex-refinement',source_study=source(key).relative_to(ROOT).as_posix(),source_blend_sha256=sha(source(key)),
      blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in dependencies},
      texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),
      reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json'),functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
      observed=observations[key]+['All 41 paletted catalogue phases, body and shadow inspected; complete CDB and functional narratives read'],
      inferred=['Exact profiles/depth, hidden rear sections, repeated field/crown casting counts, recess/grille construction and alloy identities','No operating motion recovered from catalogue reveal/highlight phases'],
      geometry_policy='Separate new assembly; earlier generic source preserved unchanged',mesh_objects=len(objects),views=[v for v in VIEWS if key!='br01' or v!='crown-detail'],blender=bpy.app.version_string,
      acceptance='Source-led structural reconstruction; final artistic/game calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('BRACCATIAN_CLAN_COMPLEX_REFINED',key,len(objects),flush=True)


if __name__=='__main__':main()
