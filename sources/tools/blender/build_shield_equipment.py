"""Independent thick-wall Shield x10-x50 reconstruction studies from PH11-PH15."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import beam,cylinder,finish,material,setup_scene
from build_refined_terran import export_glb_to,render_to,save_blend_to
from catalogue_rendering import evaluated_points,fit_camera
from terran_light_ship_parts import orient_and_chamfer

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/hardpoints'


def palette():
    return dict(shell=material('Shield | warm titanium',(.28,.25,.18),.68,.37),
                trim=material('Shield | machined collar',(.45,.43,.34),.75,.3),
                dark=material('Shield | violet interior',(.035,.025,.055),.35,.55),
                gold=material('Shield | gold emitter',(.55,.34,.085),.72,.31),
                copper=material('Shield | conductor copper',(.38,.16,.08),.75,.38),
                ceramic=material('Shield | ceramic insulators',(.40,.39,.34),.15,.55))


def shell(name,profile,start,end,m,segments=48,thickness=.075):
    # Closed solid sector: actual inner surface and sealed cut edges, no alpha trick.
    full=abs(end-start-math.tau)<1e-5
    count=segments if full else segments+1
    vertices=[]
    for inner in [False,True]:
        for y,r in profile:
            radius=r-thickness if inner else r
            assert radius>0
            vertices += [(radius*math.cos(start+(end-start)*i/segments),y,
                          radius*math.sin(start+(end-start)*i/segments)) for i in range(count)]
    size=len(profile)*count
    faces=[]
    for row in range(len(profile)-1):
        for i in range(segments):
            following=(i+1)%count
            a=row*count+i
            b=row*count+following
            c=(row+1)*count+following
            d=(row+1)*count+i
            faces += [(a,b,c,d),(a+size,d+size,c+size,b+size)]
    for row in [0,len(profile)-1]:
        for i in range(segments):
            a=row*count+i
            b=row*count+(i+1)%count
            faces.append((a,a+size,b+size,b))
    if not full:
        for i in [0,count-1]:
            for row in range(len(profile)-1):
                a=row*count+i
                b=(row+1)*count+i
                faces.append((a,b,b+size,a+size))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(m['shell'])
    obj.data.materials.append(m['dark'])
    curved_count=(len(profile)-1)*segments*2
    for index,face in enumerate(mesh.polygons):
        if all(index>=size for index in face.vertices):
            face.material_index=1
        face.use_smooth=index<curved_count
    bevel=obj.modifiers.new('Machined cut-edge chamfer','BEVEL')
    bevel.width=.004
    bevel.segments=2
    obj['wall_thickness']=thickness
    return obj


def ring(name,y,r,width,surface):
    # Tube around +Y, with a genuine opening.
    fake=dict(shell=surface,dark=surface)
    return shell(name,[(y-width/2,r),(y+width/2,r)],0,math.tau,fake,64,.045)


def sphere(name,position,size,surface):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=position)
    obj=bpy.context.object
    obj.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(obj,name,surface,0)
    for face in obj.data.polygons:
        face.use_smooth=True
    return obj


def closed_cap(name,length,m):
    # Nested elliptical hemispheres share a sealed annular rim. Each pole is a
    # single vertex, avoiding a separate circular plug on the smooth front cap.
    vertices=[]
    layers=[]
    for radius,depth in [(.96,length),(.885,length-.075)]:
        pole=len(vertices)
        vertices.append((0,-1.0-depth,0))
        rings=[]
        for step in range(1,17):
            theta=step*math.pi/32
            rings.append(len(vertices))
            vertices.extend((radius*math.sin(theta)*math.cos(i*math.tau/64),
                -1.0-depth*math.cos(theta),radius*math.sin(theta)*math.sin(i*math.tau/64)) for i in range(64))
        layers.append((pole,rings))
    faces=[]
    for pole,rings in layers:
        faces += [(pole,rings[0]+i,rings[0]+(i+1)%64) for i in range(64)]
        for a,b in zip(rings,rings[1:]):
            faces += [(a+i,b+i,b+(i+1)%64,a+(i+1)%64) for i in range(64)]
    outer,inner=layers[0][1][-1],layers[1][1][-1]
    faces += [(outer+i,outer+(i+1)%64,inner+(i+1)%64,inner+i) for i in range(64)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj,name,m['shell'],0)
    obj.data.materials.append(m['dark'])
    inner_start=64+15*64
    for index,face in enumerate(mesh.polygons):
        face.use_smooth=index<len(faces)-64
        if inner_start<=index<inner_start*2:
            face.material_index=1
    obj['wall_thickness']=.075
    return obj


def build(tier,m):
    # All variants share the visible tapered connector end, not a guessed ship socket.
    shell('Tapered connector pressure shell',[(.18,.74),(.55,.67),(.94,.46),(1.24,.25),(1.37,.20)],
          0,math.tau,m,64,.065)
    ring('Broad mounting collar',.19,.87,.18,m['trim'])
    ring('Connector service ring',.67,.61,.055,m['trim'])
    cylinder('Recessed connector interior',(0,1.39,0),.13,.08,m['dark'],rotation=(math.pi/2,0,0))
    ring('Connector terminal lip',1.39,.205,.09,m['trim'])
    for i in range(12):
        angle=i*math.tau/12
        x,z=.82*math.cos(angle),.82*math.sin(angle)
        cylinder('Collar captive fastener',(x,.09,z),.024,.022,m['dark'],vertices=8,rotation=(math.pi/2,0,0))
    profile=[(-1.30,.83),(-1.10,.95),(-.70,.98),(-.28,.90),(.07,.79)]
    if tier==10:
        for a,b in [(0,123),(148,238),(275,337)]:
            shell('Open swept shell petal',profile,math.radians(a),math.radians(b),m,32)
    elif tier==20:
        for a,b in [(-35,110),(155,290)]:
            shell('Broad opposed shell lobe',[(-1.44,.79),(-1.16,.96),(-.70,1.0),(-.20,.90),(.07,.79)],
                  math.radians(a),math.radians(b),m,40)
    else:
        # More enclosed bodies have distinct front caps and different side windows.
        shell('Rear enclosure', [(-.30,.95),(.04,.84),(.16,.76)],0,math.tau,m,64)
        if tier in [30,40]:
            aperture=(math.radians(20 if tier==30 else 30),math.radians(60 if tier==30 else 50))
            shell('Windowed enclosure wall',[(-1.0,.96),(-.65,.99),(-.32,.95)],
                  aperture[1],aperture[0]+math.tau,m,80)
        else:
            shell('Unbroken enclosure wall',[(-1.0,.96),(-.65,.99),(-.32,.95)],0,math.tau,m,64)
        if tier==30:
            closed_cap('Rounded front enclosing cap',.48,m)
        elif tier==40:
            shell('Open circular front lip',[(-1.30,.70),(-1.20,.85),(-1.0,.96)],0,math.tau,m,64)
            sphere('Recessed dark end face',(0,-1.20,0),(.64,.08,.64),m['dark'])
        else:
            closed_cap('Continuous rounded front cap',.55,m)
        for y,r in [(-.98,.992),(-.65,1.022),(-.29,.982)]:
            if tier in [30,40] and y==-.65:
                shell('Window interrupted reinforcing band',[(y-.035,r),(y+.035,r)],
                      aperture[1],aperture[0]+math.tau,dict(shell=m['trim'],dark=m['trim']),64,.045)
            else:
                ring('Enclosure reinforcing band',y,r,.07,m['trim'])
        if tier in [30,40]:
            cylinder('External service accumulator',(.58,-.48,-.89),.085,.49,m['trim'],rotation=(math.pi/2,0,0))
            for y in [-.68,-.28]:
                ring_obj=ring('Accumulator clamp',y,.108,.045,m['dark'])
                ring_obj.location.x=.58
                ring_obj.location.z=-.89
    # Internal assembly is separate geometry, visible through open shells/windows.
    cylinder('Shield axial equipment spine',(0,-.32,0),.14,1.12,m['dark'],rotation=(math.pi/2,0,0))
    sphere('Gold central emitter',(0,-.98,0),(.24,.18,.24),m['gold'])
    ring('Emitter insulator collar',-.70,.24,.08,m['ceramic'])
    for i in range(8):
        a=i*math.tau/8
        c,s=math.cos(a),math.sin(a)
        beam('Internal copper feed',(c*.18,-.68,s*.18),(c*.48,-.15,s*.48),.024,m['copper'])
        cylinder('Internal radial insulator',(c*.51,-.15,s*.51),.046,.12,m['ceramic'],vertices=16,rotation=(math.pi/2,0,0))
    for i in range(6):
        a=i*math.tau/6
        c,s=math.cos(a),math.sin(a)
        beam('Rear connector seam',(c*.63,.45,s*.63),(c*.42,.94,s*.42),.006,m['dark'])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tiers',default='10,20,30,40,50')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    for tier in map(int,args.tiers.split(',')):
        assert tier in [10,20,30,40,50]
        output=ROOT/f'shield-x{tier}'
        output.mkdir(parents=True,exist_ok=True)
        scene=setup_scene(768,48)
        bpy.context.preferences.filepaths.save_version=0
        collection=bpy.data.collections.new(f'Shield x{tier} independent equipment')
        scene.collection.children.link(collection)
        bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
        build(tier,palette())
        collection.asset_mark()
        collection.asset_data.description='Thick-walled equipment study; cultural mounting and mechanical pivots unresolved'
        meshes=[obj for obj in collection.objects if obj.type=='MESH']
        orient_and_chamfer(meshes)
        points=evaluated_points(meshes)
        views=[('front-quarter',(8,-12,8)),('rear-quarter',(-8,12,8)),('front',(0,-15,2)),
               ('side',(15,0,3)),('top',(0,0,20)),('belly',(7,-8,-12))]
        for name,direction in views:
            fit_camera(scene,points,direction)
            render_to(scene,output/(name+'.png'))
        fit_camera(scene,points,views[0][1])
        bpy.ops.object.select_all(action='DESELECT')
        for obj in meshes:
            obj.select_set(True)
        bpy.context.view_layer.objects.active=meshes[0]
        export_glb_to(output/'model.glb')
        save_blend_to(output/'model.blend')
        metadata=dict(id=f'openfa:shield-x{tier}',issue=956,revision=3,tier=tier,
            blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),
            mesh_objects=len(meshes),views=[view for view,_ in views],reference=f'PH{10+tier//10:02}.VID',
            imported_geometry_or_textures=[],mechanical_animation='not established; inventory rotation is presentation only',
            inferred=['Exact petal angles/profile dimensions','Hidden conductor/insulator arrangement','Fastener pattern'],
            unresolved=['Matched-camera proportions','Cultural variants','3D ship mounting transforms','Final detail acceptance'],
            acceptance='study; not finally accepted',blender=bpy.app.version_string)
        (output/'model.json').write_text(json.dumps(metadata,indent=2)+'\n')
        print('SHIELD_MODEL_OK',tier,len(meshes),flush=True)


if __name__=='__main__':
    main()
