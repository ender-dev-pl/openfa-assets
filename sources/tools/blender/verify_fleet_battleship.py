"""Scoped native/imported runtime verification, separate from artistic acceptance."""
import hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_fleet_battleship import ROOT,REPO,sha
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from fleet_battleship_parts import SECTIONS,SOCKETS,DENTS,section,CROSS,WING,wing_top,interpolate
from verify_assault_fighter import check_meshes
from verify_nuclear_missile import geometry_bounds
from verify_cannon_equipment import ray
from verify_rigellian_filtration import material_values


def inside(obj,p):
    n=Vector((.173,.291,.941)).normalized();a=ray(obj,p-n*8,n);b=ray(obj,p+n*8,-n)
    return a is not None and b is not None and a.dot(n)<p.dot(n)<b.dot(n)


def texture_evidence(meshes):
    result={}
    for name in ['Fleet Battleship | worn violet hull','Fleet Battleship | worn red markings']:
        shader=bpy.data.materials[name].node_tree.nodes.get('Principled BSDF');image=shader.inputs['Base Color'].links[0].from_node.image
        rough=shader.inputs['Roughness'].links[0].from_node;channel=0
        if rough.type in ['SEPARATE_COLOR','SEPRGB']: channel=1;rough=rough.inputs[0].links[0].from_node
        assert image.packed_file and rough.image.packed_file and list(image.size)==[1024,1024]
        result[name]=dict(colour=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in image.pixels[:])).hexdigest(),roughness=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in rough.image.pixels[:][channel::4])).hexdigest())
    mapped=0
    for obj in meshes:
        if not any(m.name in result for m in obj.data.materials): continue
        uv=obj.data.uv_layers.get('Authored box wear') or obj.data.uv_layers.active;assert uv
        points=[v.co for v in obj.data.vertices];low=[min(p[a] for p in points) for a in range(3)];high=[max(p[a] for p in points) for a in range(3)]
        for face in obj.data.polygons:
            valid=False
            for axes in [(0,1),(0,2),(1,2)]:
                if all(max(abs(uv.data[i].uv[j]-(points[obj.data.loops[i].vertex_index][a]-low[a])/max(1e-8,high[a]-low[a])) for j,a in enumerate(axes))<2e-5 for i in face.loop_indices): valid=True;break
            assert valid,(obj.name,'UV is not an authored box projection')
        mapped+=1
    assert mapped==7
    return dict(materials=result,mapped_meshes=mapped)


def structure(meshes,imported=False):
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:fleet-battleship' and root['forward_axis']=='local -Y'
    assert all(obj.parent==root for obj in meshes)
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6
    # glTF splits vertices at UV/flat-normal seams; test geometric closure after a one-millionth-unit weld in the diagnostic BMesh only.
    seam_splits={};geometric_vertices={}
    for obj in meshes:
        bm=bmesh.new();bm.from_mesh(obj.data);before=len(bm.verts)
        if imported: bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        seam_splits[obj.name]=before-len(bm.verts);geometric_vertices[obj.name]=len(bm.verts)
        assert all(e.is_manifold for e in bm.edges),obj.name+' geometric boundary';assert bm.calc_volume(signed=True)>0;bm.free()
    body=bpy.data.objects['Fleet Battleship long central hull'];dents=[]
    for x,y,depth in DENTS:
        w,z,h=section(y);expected=z+h*(1-abs(x)/w*.15/.65);hit=ray(body,(x,y,3),(0,0,-1));assert hit
        measured=expected-hit.z;assert depth*.5<measured<depth*1.5,('Missing dent',measured,depth);dents.append(measured)
    wing=bpy.data.objects['Fleet Battleship continuous arched wing'];engine=bpy.data.objects['Fleet Battleship central engine housing'];nozzle=bpy.data.objects['Fleet Battleship central exhaust'];throat=bpy.data.objects['Fleet Battleship exhaust throat']
    for obj,p in [(wing,Vector((0,.30,.30))),(engine,Vector((0,.55,-.05)))]:
        assert inside(body,p) and inside(obj,p),(obj.name,'Hull attachment gap')
    p=Vector((.30,1.08,-.18));assert inside(engine,p) and inside(nozzle,p),'Nozzle root gap'
    assert ray(nozzle,(0,2.5,-.18),(0,-1,0)) is None,'Nozzle axis cap'
    hit=ray(throat,(0,2.5,-.18),(0,-1,0));assert hit and 1.07<hit.y<1.13
    for side in [-1,1]:
        x=side*2.35;cy,depth,z,h=interpolate(WING,x);tip=bpy.data.objects['Fleet Battleship tip fairing '+str(side)];p=Vector((x,cy,z));assert inside(wing,p) and inside(tip,p),'Tip fairing gap'
        band=bpy.data.objects['Fleet Battleship narrow red wing stripe '+str(side)]
        for xx in [side*.9,side*1.5,side*2.05]:
            p=Vector(wing_top(xx,.48));p.z-=.002;assert inside(wing,p) and inside(band,p),'Narrow marking gap'
    band=bpy.data.objects['Fleet Battleship broad red wing stripe']
    for x in [-2.0,-1.0,0,1.0,2.0]:
        for v in [-.1,.1,.24]:
            p=Vector(wing_top(x,v));p.z-=.002;assert inside(wing,p) and inside(band,p),'Broad marking gap'
    probe=bpy.data.objects['Fleet Battleship bow probe'];p=Vector((0,-2.68,.04));assert inside(body,p) and inside(probe,p),'Bow probe gap'
    sockets={};root.rotation_mode='QUATERNION'
    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
        root.rotation_quaternion=Quaternion((0,0,1),angle);bpy.context.view_layer.update();rotation=root.matrix_world.to_3x3()
        for name,(p,n) in SOCKETS.items():
            obj=bpy.data.objects[name];assert obj.parent==root and obj['forward_axis']=='local +Z'
            assert (obj.matrix_world.translation-rotation @ Vector(p)).length<1e-5
            forward=(obj.matrix_world.to_3x3() @ Vector((0,0,1))).normalized();assert (forward-rotation @ Vector(n)).length<1e-5
            sockets[name]=dict(position=list(p),forward=list(n))
    root.rotation_quaternion=Quaternion((0,0,1),0);bpy.context.view_layer.update()
    bounds=geometry_bounds(meshes);assert -2.5<bounds[0]<-2.3 and 2.3<bounds[3]<2.5 and -3.1<bounds[1]<-2.9 and 1.3<bounds[4]<1.5
    assert not any(obj.animation_data for obj in meshes)
    return dict(bounds=bounds,dent_depths=dents,sockets=sockets,seam_vertices_welded=seam_splits,geometric_vertices=geometric_vertices,closure_weld_tolerance=1e-6 if imported else 0)


def nozzle_normals():
    mesh=bpy.data.objects['Fleet Battleship central exhaust'].data;result={}
    for face in mesh.polygons:
        for index in face.loop_indices:
            p=mesh.vertices[mesh.loops[index].vertex_index].co;key=tuple(round(v,6) for v in p)
            result.setdefault(key,[]).append(tuple(mesh.corner_normals[index].vector))
    return result


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for field,p in [('generator_sha256',Path(__file__).with_name('build_fleet_battleship.py')),('parts_sha256',Path(__file__).with_name('fleet_battleship_parts.py')),('reference_sha256',REPO/'docs/reconstruction/models/ship-reference-index.json'),('functional_source_sha256',REPO/'docs/reconstruction/models/functional-text-index.json'),('authored_wear_sha256',ROOT/'authored-wear.json')]:assert sha(p)==meta[field]
    for name,digest in meta['helper_sha256'].items():assert sha(Path(__file__).with_name(name))==digest
    assert sha(Path(__file__).with_name('author_fleet_battleship_wear.py'))==wear['generator_sha256']
    for name,digest in wear['images'].items():assert sha(ROOT/name)==digest
    for ext in ['blend','glb']:assert sha(ROOT/('model.'+ext))==meta[ext+'_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native_normals=nozzle_normals();native=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes);assert len(materials)==5 and len(meshes)==meta['mesh_objects']
    for image in bpy.data.images:
        if image.source=='FILE':assert sha(ROOT/image.name)==hashlib.sha256(image.packed_file.data).hexdigest()
    transforms={o.name:([list(row) for row in o.matrix_world],geometry_bounds([o])) for o in meshes}
    cam=bpy.context.scene.camera;front=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale)
    offset=Vector((4,10,6)).normalized()*20;cam.location=Vector((0,1.20,-.18))+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.2;detail=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale);render_to(bpy.context.scene,ROOT/'engine-detail.png')
    scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'));imported=[o for o in scene.objects if o.type=='MESH'];check_meshes(imported,allow_packed_images=True)
    imported_normals=nozzle_normals();assert native_normals.keys()==imported_normals.keys()
    normal_error=max(min((Vector(n)-Vector(other)).length for other in imported_normals[p]) for p,ns in native_normals.items() for n in ns);assert normal_error<1e-5,'Nozzle normal mismatch'
    exported=structure(imported,imported=True);assert exported['geometric_vertices']==native['geometric_vertices'],'Export lost geometric vertices';assert texture_evidence(imported)==textures
    assert {o.name for o in imported}==set(transforms)
    for o in imported:
        matrix,bounds=transforms[o.name];assert max(abs(o.matrix_world[i][j]-matrix[i][j]) for i in range(4) for j in range(4))<1e-5;assert max(abs(a-b) for a,b in zip(geometry_bounds([o]),bounds))<1e-5
    other=material_values(imported);assert materials.keys()==other.keys()
    for name,value in materials.items():assert max(abs(a-b) for a,b in zip(value[0]+value[1:],other[name][0]+other[name][1:]))<1/255+.00001
    for name,camera in [('imported-glb-front-quarter',front),('imported-glb-engine-detail',detail)]:
        scene.camera.location=camera[0];scene.camera.rotation_euler=camera[1];scene.camera.data.ortho_scale=camera[2];render_to(scene,ROOT/(name+'.png'))
    report=dict(issue=998,verifier_sha256=sha(Path(__file__)),blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],mesh_objects=len(meshes),materials=materials,native=native,imported=exported,textures=textures,nozzle_maximum_normal_error=normal_error,checks=['Closed positive topology, bounds/transforms, packed image bytes and decoded texture pixels','Authored box UVs, two physical dents and hull/wing/engine/nozzle/marking/tip/probe contacts','Seven socket positions/axes under four rigid rotations; no animation timing claim'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('FLEET_BATTLESHIP_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
