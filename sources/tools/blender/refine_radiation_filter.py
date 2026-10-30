"""Author PB05 hollow curved pipes with the divergent intake directions seen in rotation references."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_refined_terran import ROOT,render_to,export_glb_to,save_blend_to
from catalogue_rendering import evaluated_points,fit_camera
from refined_terran_parts import Detailer


def hollow_tube(d,name,base,heading,height):
    direction=Vector((math.cos(heading),math.sin(heading),0))
    across=Vector((-direction.y,direction.x,0))
    origin=Vector((*base,0))
    path=[origin+Vector((0,0,z)) for z in [.03,.25,.65,height]]
    bend=.27
    for i in range(1,17):
        a=i*math.pi/32
        path.append(origin+direction*(bend*(1-math.cos(a)))+Vector((0,0,height+bend*math.sin(a))))
    for distance in [.13,.30]:
        path.append(origin+direction*(bend+distance)+Vector((0,0,height+bend)))
    vertices,faces=[],[]
    segments=48
    for i,point in enumerate(path):
        tangent=(path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized()
        normal=across.cross(tangent).normalized()
        for radius in [.21,.165]:
            for j in range(segments):
                a=j*math.tau/segments
                vertices.append(tuple(point+radius*(normal*math.cos(a)+across*math.sin(a))))
    stride=segments*2
    for i in range(len(path)-1):
        for j in range(segments):
            k=(j+1)%segments
            a,b=i*stride,(i+1)*stride
            faces.append((a+j,a+k,b+k,b+j))
            faces.append((a+segments+j,b+segments+j,b+segments+k,a+segments+k))
    side_count=len(faces)
    for ring in [0,len(path)-1]:
        a=ring*stride
        for j in range(segments):
            k=(j+1)%segments
            faces.append((a+j,a+segments+j,a+segments+k,a+k))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    d.collection.objects.link(obj)
    mesh.materials.append(d.m['alloy'])
    mesh.materials.append(d.m['dark'])
    for i,face in enumerate(mesh.polygons):
        face.material_index=1 if i<side_count and i%2 else 0
        face.use_smooth=i<side_count
    obj['filter_tube']=True
    obj['intake_heading_degrees']=math.degrees(heading)
    d.keep(obj)
    return path[-1],direction,across


def main():
    output=ROOT/'pb05'
    meta=json.loads((output/'model.json').read_text(encoding='utf-8'))
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
    scene=bpy.context.scene
    collection=next(c for c in bpy.data.collections if c.asset_data)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    for obj in list(collection.objects):
        if obj.type=='MESH':
            bpy.data.objects.remove(obj,do_unlink=True)
    d=Detailer(collection)
    specifications=[((-.47,-.23),210,1.90),((.47,-.23),330,1.70),((0,.52),90,2.25)]
    names=[]
    directions=[]
    for i,(base,degrees,height) in enumerate(specifications):
        mouth,direction,across=hollow_tube(d,f'Radiation filter hollow tube {i+1:02}',base,math.radians(degrees),height)
        names.append(d.created[-1].name)
        directions.append(list(direction))
        x,y=base
        d.disc('Filter foundation socket',(x,y,.07),.26,.14,'dark')
        d.disc('Filter internal dust trap',(x,y,.08),.165,.035,'dark')
        for z in [.18,.60,1.15,height-.08]:
            d.ring('Filter segmented sleeve',(x,y,z),.213,.024,'edge')
        d.ring('Intake bolted flange',mouth,.219,.025,'bronze',direction)
        d.ring('Intake inner pressure lip',mouth+direction*.008,.169,.012,'dark',direction)
        for bolt in range(8):
            a=bolt*math.tau/8
            point=mouth+direction*.025+.207*(across*math.cos(a)+Vector((0,0,1))*math.sin(a))
            d.disc('Intake flange fastener',point,.014,.025,'edge',direction)
        p=Vector((x,y,.73))+direction*.224
        d.hatch('Filter pressure instrument',p,.07,direction,'bronze')
        d.pipe('Filter pressure monitoring line',[(x+across.x*.23,y+across.y*.23,.20),
            (x+across.x*.23,y+across.y*.23,height-.08),
            (x+across.x*.17,y+across.y*.17,height+.13)],.012,'bronze')
    meshes=[obj for obj in collection.objects if obj.type=='MESH']
    points=evaluated_points(meshes)
    for view,direction in [('front-quarter',(8,-12,10.1)),('rear-quarter',(-8,12,10.1)),('top',(0,0,20))]:
        fit_camera(scene,points,direction)
        render_to(scene,output/(view+'.png'))
    low,high=fit_camera(scene,points,(8,-12,10.1))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    export_glb_to(output/'model.glb')
    meta.update(mesh_objects=len(meshes),mesh_faces=sum(len(obj.data.polygons) for obj in meshes),
        detail_objects=sum('detail_role' in obj for obj in meshes),bounds_min=list(low),bounds_max=list(high))
    meta['detail_features']=['Three divergent hollow intakes, smoothly swept elbows, pressure instruments and bolted mouth flanges']
    meta['filter_direction_refinement']=dict(generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        tubes=names,intake_directions=directions,heading_degrees=[210,330,90],reference_frames=[0,15,30,45],
        reference='PB05 rotation frames show separated outward-facing intake directions; exact angles and bend radii authored')
    collection['detail_features']='; '.join(meta['detail_features'])
    save_blend_to(output/'model.blend')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print('RADIATION_DIVERGENT_INTAKES_OK',len(names),len(meshes),flush=True)


if __name__=='__main__':
    main()
