"""Scoped native/imported runtime verification, separate from artistic acceptance."""
import hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_mikotaj_falari_lourn import ROOT,REPO,sha
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from mikotaj_falari_lourn_parts import SOCKETS,BODY_DENT,WING_DENTS,FIXTURES,body_skin,body_dent,wing_skin,wing_base,roof
from verify_assault_fighter import check_meshes
from verify_nuclear_missile import geometry_bounds
from verify_cannon_equipment import ray
from verify_rigellian_filtration import material_values


def inside(obj,p):
    # Count actual shell crossings, including annular voids. A near/far envelope
    # alone cannot establish containment for a ring or another concave mesh.
    n=Vector((.173,.291,.941)).normalized();origin=Vector(p);crossings=0
    for _ in range(64):
        hit=ray(obj,origin,n)
        if hit is None:return crossings%2==1
        crossings+=1;origin=hit+n*1e-5
    raise AssertionError((obj.name,'Unbounded containment ray'))


def texture_evidence(meshes):
    result={}
    for name in ['Falari-Lourn | worn blue pressure shell','Falari-Lourn | worn green wing','Falari-Lourn | dulled gold fixtures']:
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
    assert mapped==14
    return dict(materials=result,mapped_meshes=mapped)


def structure(meshes,imported=False):
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:ship/mikotaj/falari-lourn' and root['forward_axis']=='local -Y'
    assert all(obj.parent==root for obj in meshes)
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6
    # glTF splits vertices at UV/flat-normal seams; test geometric closure after a one-millionth-unit weld in the diagnostic BMesh only.
    seam_splits={};geometric_vertices={}
    for obj in meshes:
        bm=bmesh.new();bm.from_mesh(obj.data);before=len(bm.verts)
        if imported: bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        seam_splits[obj.name]=before-len(bm.verts);geometric_vertices[obj.name]=len(bm.verts)
        assert all(e.is_manifold for e in bm.edges),obj.name+' geometric boundary';assert bm.calc_volume(signed=True)>0;bm.free()
    assert len(meshes)==30
    body=bpy.data.objects['Falari-Lourn blue pressure hull'];wing=bpy.data.objects['Falari-Lourn continuous green wing'];dents=[]
    x,y,depth=BODY_DENT;hit=ray(body,(x,y,3),(0,0,-1));assert hit
    measured=body_skin(x,y)+body_dent(x,y)-hit.z;assert depth*.5<measured<depth*1.5;dents.append(measured)
    for x,y,depth in WING_DENTS:
        hit=ray(wing,(x,y,3),(0,0,-1));assert hit;measured=wing_base(x,y)-hit.z;assert depth*.5<measured<depth*1.5;dents.append(measured)
    joint_contacts=0;fixture_contacts=0;bezel_contacts=0
    for x in [-.30,0,.30]:
        for y in [-.30,0,.30]:
            point=Vector((x,y,wing_skin(x,y)-.02));assert inside(body,point) and inside(wing,point),'Wing/hull joint gap';joint_contacts+=1
    for y in [-1.6,1.6]:assert inside(wing,Vector((0,y,wing_skin(0,y)-.02))),'Continuous wing void'
    for i,(x,y) in enumerate(FIXTURES):
        saddle=bpy.data.objects['Falari-Lourn green saddle '+str(i)];fixture=bpy.data.objects['Falari-Lourn gold wing fixture '+str(i)]
        for dx,dy in [(0,0),(-.02,0),(.02,0),(0,-.02),(0,.02)]:
            z=wing_skin(x+dx,y+dy);point=Vector((x+dx,y+dy,z-.006));assert inside(wing,point) and inside(saddle,point),'Saddle root gap'
            point=Vector((x+dx,y+dy,z+.008));assert inside(fixture,point) and inside(saddle,point),'Gold fixture root gap';fixture_contacts+=1
    for side in [-1,1]:
        bezel=bpy.data.objects['Falari-Lourn body bezel '+str(side)];face=bpy.data.objects['Falari-Lourn body face '+str(side)];n=Vector((0,side,0));centre=Vector((0,side*.73,-.035))
        for i in range(32):
            angle=math.tau*i/32;point=centre+Vector((.105*math.cos(angle),0,.105*math.sin(angle)));hit=ray(body,point+n*2,-n);assert hit
            probe=hit-n*.006;assert inside(body,probe) and inside(bezel,probe),'Body bezel root gap';bezel_contacts+=1
        assert inside(bezel,centre+n*.024) and inside(face,centre+n*.024),'Bezel/face gap'
    meta=json.loads((ROOT/'model.json').read_text());panels=meta['conformal_panels'];assert len(panels)==12;contacts=0
    for spec in panels:
        obj=bpy.data.objects[spec['name']];support=bpy.data.objects[spec['support']];skin=body_skin if spec['domain']=='hull' else wing_skin
        offset=.006 if 'service slot' in spec['name'] else -.004
        for yf in [.2,.5,.8]:
            y=spec['cy']+spec['depth']*(yf-.5)
            for xf in [.2,.5,.8]:
                x=spec['cx']+spec['width']*(xf-.5);point=Vector((x,y,skin(x,y)+offset))
                assert inside(obj,point) and inside(support,point),('Fitted patch root gap',spec['name'],yf,xf);contacts+=1
    for i,x in enumerate([-.22,.22]):
        cover=bpy.data.objects['Falari-Lourn hull service cover '+str(i)]
        for j,dx in enumerate([-.055,.055]):
            for k,dy in enumerate([-.105,.105]):
                point,normal=roof(x+dx,.10+dy);point+=normal*.004;assert inside(cover,point) and inside(bpy.data.objects['Falari-Lourn hull fastener '+str(i)+' '+str(j)+' '+str(k)],point),'Cover fastener gap'
    sockets={};root.rotation_mode='QUATERNION'
    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
        root.rotation_quaternion=Quaternion((0,0,1),angle);bpy.context.view_layer.update();rotation=root.matrix_world.to_3x3()
        for name,(p,n) in SOCKETS.items():
            obj=bpy.data.objects[name];assert obj.parent==root and obj['forward_axis']=='local +Z'
            assert (obj.matrix_world.translation-rotation @ Vector(p)).length<1e-5
            forward=(obj.matrix_world.to_3x3() @ Vector((0,0,1))).normalized();assert (forward-rotation @ Vector(n)).length<1e-5
            sockets[name]=dict(position=list(p),forward=list(n))
    root.rotation_quaternion=Quaternion((0,0,1),0);bpy.context.view_layer.update()
    bounds=geometry_bounds(meshes);assert -.77<bounds[0]<-.75 and .75<bounds[3]<.77 and -2.81<bounds[1]<-2.79 and 2.79<bounds[4]<2.81 and -.51<bounds[2]<-.49 and .49<bounds[5]<.52,bounds
    assert not any(obj.animation_data for obj in meshes)
    return dict(bounds=bounds,dent_depths=dents,sockets=sockets,seam_vertices_welded=seam_splits,geometric_vertices=geometric_vertices,closure_weld_tolerance=1e-6 if imported else 0,fitted_patch_samples=contacts,wing_hull_joint_samples=joint_contacts,gold_fixture_root_samples=fixture_contacts,body_bezel_root_samples=bezel_contacts,continuous_wing_witnesses=2,roof_fasteners=8)



def normal_evidence(meshes,authored=False):
    result={}
    for obj in meshes:
        if authored: assert obj.data.has_custom_normals and all(face.use_smooth for face in obj.data.polygons),obj.name+' authored normal contract'
        values={}
        for face in obj.data.polygons:
            for index in face.loop_indices:
                p=obj.data.vertices[obj.data.loops[index].vertex_index].co;key=tuple(round(v,5) for v in p)
                values.setdefault(key,[]).append(tuple(obj.data.corner_normals[index].vector))
        result[obj.name]=values
    return result


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for field,p in [('generator_sha256',Path(__file__).with_name('build_mikotaj_falari_lourn.py')),('parts_sha256',Path(__file__).with_name('mikotaj_falari_lourn_parts.py')),('reference_sha256',REPO/'docs/reconstruction/models/ship-reference-index.json'),('functional_source_sha256',REPO/'docs/reconstruction/models/functional-text-index.json'),('cultural_style_sha256',REPO/'docs/reconstruction/models/cultural-architecture-index.json'),('catalogue_sha256',REPO/'content/standard/catalogues/legacy-gameplay.json'),('authored_wear_sha256',ROOT/'authored-wear.json')]:assert sha(p)==meta[field]
    for name,digest in meta['helper_sha256'].items():assert sha(Path(__file__).with_name(name))==digest
    assert sha(Path(__file__).with_name('author_mikotaj_falari_lourn_wear.py'))==wear['generator_sha256']
    for name,digest in wear['images'].items():assert sha(ROOT/name)==digest
    for ext in ['blend','glb']:assert sha(ROOT/('model.'+ext))==meta[ext+'_sha256']
    catalogue=json.loads((REPO/'content/standard/catalogues/legacy-gameplay.json').read_text());entry=next(r for r in catalogue['ships'] if r['id']==meta['id']);assert entry['hardpointSlots']==5 and not entry.get('hardpointMounts') and meta['equipment_slots']==dict(declared=5,calibrated_3d_mounts=0)
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native_normals=normal_evidence(meshes,authored=True);native=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes);assert len(materials)==5 and len(meshes)==meta['mesh_objects']
    for image in bpy.data.images:
        if image.source=='FILE':assert sha(ROOT/image.name)==hashlib.sha256(image.packed_file.data).hexdigest()
    transforms={o.name:([list(row) for row in o.matrix_world],geometry_bounds([o])) for o in meshes}
    cam=bpy.context.scene.camera;front=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale)
    offset=Vector((4,-10,6)).normalized()*20;cam.location=Vector((0,0,.2))+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.50;detail=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale);render_to(bpy.context.scene,ROOT/'hull-detail.png')
    scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'));imported=[o for o in scene.objects if o.type=='MESH'];check_meshes(imported,allow_packed_images=True)
    exported_normals=normal_evidence(imported);normal_error=0
    for name,points in native_normals.items():
        other=exported_normals[name];object_error=0;assert points.keys()==other.keys(),(name,'Normal positions differ')
        for p,values in points.items():
            for n in values: object_error=max(object_error,min((Vector(n)-Vector(v)).length for v in other[p]))
        normal_error=max(normal_error,object_error)
        if object_error>=1e-3:print('NORMAL_MISMATCH',name,object_error,flush=True)
    assert normal_error<1e-3,'Exported corner normals differ beyond custom-normal quantization'
    exported=structure(imported,imported=True);assert exported['geometric_vertices']==native['geometric_vertices'],'Export lost geometric vertices';assert texture_evidence(imported)==textures
    assert {o.name for o in imported}==set(transforms)
    for o in imported:
        matrix,bounds=transforms[o.name];assert max(abs(o.matrix_world[i][j]-matrix[i][j]) for i in range(4) for j in range(4))<1e-5;assert max(abs(a-b) for a,b in zip(geometry_bounds([o]),bounds))<1e-5
    other=material_values(imported);assert materials.keys()==other.keys()
    for name,value in materials.items():assert max(abs(a-b) for a,b in zip(value[0]+value[1:],other[name][0]+other[name][1:]))<1/255+.00001
    for name,camera in [('imported-glb-front-quarter',front),('imported-glb-hull-detail',detail)]:
        scene.camera.location=camera[0];scene.camera.rotation_euler=camera[1];scene.camera.data.ortho_scale=camera[2];render_to(scene,ROOT/(name+'.png'))
    report=dict(issue=1014,verifier_sha256=sha(Path(__file__)),blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],mesh_objects=len(meshes),materials=materials,native=native,imported=exported,textures=textures,maximum_corner_normal_error=normal_error,checks=['Closed positive topology, bounds/transforms, packed image bytes and decoded texture pixels','Authored box UVs, three measured dents; odd/even containment for wing/hull/fixture/bezel/patch/fastener contacts; continuous wing witnesses','One alignment helper positions/axes under four rigid rotations; no animation timing claim'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('MIKOTAJ_FALARI_LOURN_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
