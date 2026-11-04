"""Replace PB10's coarse wire emitters with original faceted luminous crystal assemblies."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_refined_terran import ROOT, render_to, export_glb_to, save_blend_to
from catalogue_rendering import evaluated_points, fit_camera
from refined_terran_parts import Detailer
from build_openfa_assets import material


def crystal(d,name,x,z0,z1,radius,surfaces):
    count=6
    profile=[(z0,.008),(z0+(z1-z0)*.20,radius*.76),
             (z0+(z1-z0)*.70,radius),(z1,.006)]
    vertices=[(x+r*math.cos(i*math.tau/count+math.pi/6),r*math.sin(i*math.tau/count+math.pi/6),z)
              for z,r in profile for i in range(count)]
    faces=[tuple(reversed(range(count)))]
    for band in range(len(profile)-1):
        for i in range(count):
            j=(i+1)%count
            faces.append((band*count+i,band*count+j,(band+1)*count+j,(band+1)*count+i))
    faces.append(tuple(range((len(profile)-1)*count,len(profile)*count)))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    d.collection.objects.link(obj)
    for surface in surfaces:
        mesh.materials.append(surface)
    for i,face in enumerate(mesh.polygons):
        face.material_index=i%len(surfaces)
        face.use_smooth=False
    obj['field_emitter_crystal']=True
    return d.keep(obj)


def main():
    output=ROOT/'pb10'
    meta=json.loads((output/'model.json').read_text(encoding='utf-8'))
    code_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
    scene=bpy.context.scene
    collection=next(c for c in bpy.data.collections if c.asset_data)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    prefixes=('Shield emitter stem','Shield emitter cage','Shield cage crown',
        'Emitter insulated mounting','Emitter induction collar','Emitter power feed',
        'Crystal emitter ','Field crystal ','Field crystal core','Field corona ','Field emitter assembly')
    for obj in list(collection.objects):
        if obj.name.startswith(prefixes):
            bpy.data.objects.remove(obj,do_unlink=True)
    d=Detailer(collection)
    facets=[]
    for i,colour in enumerate([(0.015,.10,.16),(.055,.32,.46),(.32,.68,.83)]):
        surface=material('Field crystal polished facet '+str(i),colour,.55,.08,.15)
        shader=surface.node_tree.nodes['Principled BSDF']
        shader.inputs['IOR'].default_value=1.8
        if 'Coat Weight' in shader.inputs:
            shader.inputs['Coat Weight'].default_value=.85
            shader.inputs['Coat Roughness'].default_value=.035
        if 'Transmission Weight' in shader.inputs:
            shader.inputs['Transmission Weight'].default_value=.1
        facets.append(surface)
    core=material('Field crystal luminous core',(.25,.72,.85),.1,.18,3.5)
    corona=material('Field crystal energy corona',(.20,.66,.80),.1,.18,2.5)
    names=[]
    roots=[]
    for index in range(3):
        x=(index-1)*.65
        first=len(d.created)
        d.disc('Crystal emitter insulated socket',(x,0,.64),.13,.12,'dark')
        d.disc('Crystal emitter metallic stem',(x,0,.81),.065,.30,'edge')
        d.disc('Crystal emitter socket crown',(x,0,.96),.11,.08,'bronze')
        for z in [.73,.82,.91]:
            d.ring('Crystal emitter insulator lip',(x,0,z),.082,.012,'blue')
        names.append(crystal(d,f'Field crystal {index+1:02}',x,.94,1.92,.17,facets).name)
        crystal(d,f'Field crystal core {index+1:02}',x,1.02,1.83,.055,[core])
        # Short arcs around the emitter tips convey energy; these are not flat collector panels.
        for arc in range(3):
            points=[]
            for step in range(9):
                a=arc*math.tau/3+step*.11
                radius=.19+step*.003
                points.append((x+radius*math.cos(a),radius*math.sin(a),1.63+.10*math.sin(a*2)))
            obj=d.pipe('Field corona arc',points,.005,'light')
            obj.data.materials.clear()
            obj.data.materials.append(corona)
        d.pipe('Crystal emitter braided feed',[(x,-.12,.52),(x,-.12,.77),(x,0,.94)],.018,'bronze')
        # Rotation references show the side emitters splaying away from the middle.
        # Tilt the whole rigid assembly at its mounting point, not just the crystal tip.
        root=bpy.data.objects.new(f'Field emitter assembly {index+1:02}',None)
        collection.objects.link(root)
        root.location=(x,0,.58)
        bpy.context.view_layer.update()
        for obj in d.created[first:]:
            world=obj.matrix_world.copy()
            obj.parent=root
            obj.matrix_world=world
        root.rotation_euler.y=math.radians([-22,-4,22][index])
        roots.append(root.name)
        bpy.context.view_layer.update()
    meshes=[obj for obj in collection.objects if obj.type=='MESH']
    points=evaluated_points(meshes)
    views=[('front-quarter',(8,-12,10.1)),('rear-quarter',(-8,12,10.1)),('top',(0,0,20))]
    for view,direction in views:
        fit_camera(scene,points,direction)
        render_to(scene,output/(view+'.png'))
    low,high=fit_camera(scene,points,views[0][1])
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    export_glb_to(output/'model.glb')
    meta.update(mesh_objects=len(meshes),mesh_faces=sum(len(obj.data.polygons) for obj in meshes),
        detail_objects=sum('detail_role' in obj for obj in meshes),bounds_min=list(low),bounds_max=list(high))
    meta['detail_features']=['Curved hull armour, outward-canted polished field crystals, insulated sockets and energy coronas']
    meta['screen_emitter_refinement']=dict(generator_sha256=code_hash,crystals=names,assemblies=roots,
        tilt_y_degrees=[-22,-4,22],reference_frames=[0,15,30,45],
        reference='PB10 rotation views confirm canted crystalline force-field emitters; exact angles authored',
        hidden_geometry='authored crystal facets, sockets and energy accents')
    collection['detail_features']='; '.join(meta['detail_features'])
    # Save collection metadata together with its updated geometry.
    save_blend_to(output/'model.blend')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print('SCREEN_CRYSTAL_EMITTERS_OK',len(names),len(meshes),flush=True)


if __name__=='__main__':
    main()
