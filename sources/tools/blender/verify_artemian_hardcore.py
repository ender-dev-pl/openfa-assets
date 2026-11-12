"""Scoped native/imported runtime verification, separate from artistic acceptance."""
import hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_artemian_hardcore import ROOT,REPO,sha
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from artemian_hardcore_parts import MAIN_PROFILE,PROFILES,LOCATIONS,SOCKETS,DENTS,PANELS,surface,hull_frame
from manufactured_vessels import profile_radius
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
    for name in ['Hardcore | worn silver bridge','Hardcore | worn gold brown shells']:
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
    assert mapped==21
    return dict(materials=result,mapped_meshes=mapped)


def structure(meshes,imported=False):
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:ship/artemian/hardcore' and root['forward_axis']=='local -Y'
    assert all(obj.parent==root for obj in meshes)
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6
    # glTF splits vertices at UV/flat-normal seams; test geometric closure after a one-millionth-unit weld in the diagnostic BMesh only.
    seam_splits={};geometric_vertices={}
    for obj in meshes:
        bm=bmesh.new();bm.from_mesh(obj.data);before=len(bm.verts)
        if imported: bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        seam_splits[obj.name]=before-len(bm.verts);geometric_vertices[obj.name]=len(bm.verts)
        assert all(e.is_manifold for e in bm.edges),obj.name+' geometric boundary';assert bm.calc_volume(signed=True)>0;bm.free()
    assert len(meshes)==48
    dents=[];bridge_contacts=0;rail_contacts=0;arm_contacts=0;tail_contacts=0;trim_contacts=0;bezel_contacts=0;fastener_contacts=0
    for owner,(phi,z,depth) in DENTS.items():
        n=Vector((math.cos(phi),math.sin(phi),0));hit=ray(bpy.data.objects[owner],surface(owner,phi,z,.5),-n);assert hit
        measured=(surface(owner,phi,z,depth)-hit).dot(n);assert depth*.5<measured<depth*1.5,(owner,measured);dents.append(measured)
    bridge=bpy.data.objects['Hardcore silver connecting bridge']
    for i,y in enumerate([-1.30,1.30]):
        body=bpy.data.objects['Hardcore main pressure body '+str(i)];sign=-1 if i==0 else 1;trim=bpy.data.objects['Hardcore silver body trim '+str(i)];z=-.04;r=profile_radius(MAIN_PROFILE,z)-.008
        assert not inside(trim,Vector((0,y,z))),'Silver trim annular void filled'
        for j in range(16):
            phi=j*math.tau/16;probe=Vector((r*math.cos(phi),y+r*math.sin(phi),z));assert inside(body,probe) and inside(trim,probe),'Body trim attachment gap';trim_contacts+=1
        for x in [-.20,0,.20]:
            probe=Vector((x,sign*.78,-.06));assert inside(body,probe) and inside(bridge,probe),'Silver bridge/body gap';bridge_contacts+=1
        for side in [-1,1]:
            rail=bpy.data.objects['Hardcore bridge edge rail '+str(side)];probe=Vector((side*.25,sign*.85,.02));assert inside(rail,probe) and inside(body,probe),'Bridge rail/body gap';rail_contacts+=1
            arm=bpy.data.objects['Hardcore lateral arm '+str(i)+' '+str(side)];module=bpy.data.objects['Hardcore lateral module '+str(i)+' '+str(side)]
            for x,support in [(.65,body),(1.10,module)]:
                probe=Vector((side*x,y,-.03));assert inside(arm,probe) and inside(support,probe),'Lateral arm attachment gap';arm_contacts+=1
    for side in [-1,1]:
        probe=Vector((side*.25,0,0));assert inside(bridge,probe) and inside(bpy.data.objects['Hardcore bridge edge rail '+str(side)],probe),'Bridge rail/plate gap';rail_contacts+=1
        start=Vector((side*.42,1.70,0));end=Vector((side*.52,2.65,-.02));probe=start+(end-start).normalized()*.02
        assert inside(bpy.data.objects['Hardcore aft blue grey projection '+str(side)],probe) and inside(bpy.data.objects['Hardcore main pressure body 1'],probe),'Aft projection root gap'
    tail=bpy.data.objects['Hardcore tail plane'];body=bpy.data.objects['Hardcore main pressure body 1']
    for x in [-.20,0,.20]:
        for y in [1.65,1.70,1.75]:
            probe=Vector((x,y,-.10));assert inside(tail,probe) and inside(body,probe),'Tail plane/body gap';tail_contacts+=1
    bezel=bpy.data.objects['Hardcore fore interface bezel'];face=bpy.data.objects['Hardcore blue grey fore interface'];body=bpy.data.objects['Hardcore main pressure body 0'];origin=Vector((0,-2.12,-.01));n=Vector((0,-1,0))
    for i in range(32):
        phi=i*math.tau/32;p=origin+Vector((.12*math.cos(phi),0,.12*math.sin(phi)));hit=ray(body,p+n*2,-n);assert hit
        probe=hit-n*.006;assert inside(body,probe) and inside(bezel,probe),'Fore bezel root gap';bezel_contacts+=1
    probe=origin+n*.0225;assert inside(bezel,probe) and inside(face,probe),'Fore interface join gap'
    meta=json.loads((ROOT/'model.json').read_text());panels=meta['conformal_panels'];assert len(panels)==12;contacts=0
    for spec in panels:
        obj=bpy.data.objects[spec['name']];support=bpy.data.objects[spec['support']];offset=-.004 if spec['support']==spec['owner'] else .006
        for zf in [.2,.5,.8]:
            z=spec['z0']+(spec['z1']-spec['z0'])*zf
            for pf in [.2,.5,.8]:
                phi=spec['phi']+spec['width']*(-1+2*pf);probe=surface(spec['owner'],phi,z,offset)
                assert inside(obj,probe) and inside(support,probe),('Fitted patch root gap',spec['name'],zf,pf);contacts+=1
    for i in range(2):
        owner='Hardcore main pressure body '+str(i)
        for j,phi in enumerate(PANELS):
            cover=bpy.data.objects['Hardcore service cover '+str(i)+' '+str(j)]
            for k,z in enumerate([.165,.265]):
                for l,offset in enumerate([-.14,.14]):
                    p,n=hull_frame(owner,phi+offset,z);probe=p+n*.003
                    assert inside(cover,probe) and inside(bpy.data.objects['Hardcore fastener '+str(i)+' '+str(j)+' '+str(k)+' '+str(l)],probe),'Service fastener gap';fastener_contacts+=1
    sockets={};root.rotation_mode='QUATERNION'
    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
        root.rotation_quaternion=Quaternion((0,0,1),angle);bpy.context.view_layer.update();rotation=root.matrix_world.to_3x3()
        for name,(p,n) in SOCKETS.items():
            obj=bpy.data.objects[name];assert obj.parent==root and obj['forward_axis']=='local +Z'
            assert (obj.matrix_world.translation-rotation @ Vector(p)).length<1e-5
            forward=(obj.matrix_world.to_3x3() @ Vector((0,0,1))).normalized();assert (forward-rotation @ Vector(n)).length<1e-5
            sockets[name]=dict(position=list(p),forward=list(n))
    root.rotation_quaternion=Quaternion((0,0,1),0);bpy.context.view_layer.update()
    bounds=geometry_bounds(meshes);assert -1.39<bounds[0]<-1.37 and 1.37<bounds[3]<1.39 and -2.17<bounds[1]<-2.15 and 2.74<bounds[4]<2.76 and -.376<bounds[2]<-.374 and .436<bounds[5]<.439,bounds
    assert not any(obj.animation_data for obj in meshes)
    return dict(bounds=bounds,dent_depths=dents,sockets=sockets,seam_vertices_welded=seam_splits,geometric_vertices=geometric_vertices,closure_weld_tolerance=1e-6 if imported else 0,bridge_body_samples=bridge_contacts,bridge_rail_samples=rail_contacts,lateral_arm_samples=arm_contacts,tail_body_samples=tail_contacts,body_trim_root_samples=trim_contacts,body_trim_void_witnesses=2,fore_bezel_root_samples=bezel_contacts,fore_interface_joins=1,aft_projection_root_samples=2,fitted_patch_samples=contacts,service_fasteners=fastener_contacts)



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
    for field,p in [('generator_sha256',Path(__file__).with_name('build_artemian_hardcore.py')),('parts_sha256',Path(__file__).with_name('artemian_hardcore_parts.py')),('reference_sha256',REPO/'docs/reconstruction/models/ship-reference-index.json'),('functional_source_sha256',REPO/'docs/reconstruction/models/functional-text-index.json'),('cultural_style_sha256',REPO/'docs/reconstruction/models/cultural-architecture-index.json'),('catalogue_sha256',REPO/'content/standard/catalogues/legacy-gameplay.json'),('authored_wear_sha256',ROOT/'authored-wear.json')]:assert sha(p)==meta[field]
    for name,digest in meta['helper_sha256'].items():assert sha(Path(__file__).with_name(name))==digest
    assert sha(Path(__file__).with_name('author_artemian_hardcore_wear.py'))==wear['generator_sha256']
    for name,digest in wear['images'].items():assert sha(ROOT/name)==digest
    for ext in ['blend','glb']:assert sha(ROOT/('model.'+ext))==meta[ext+'_sha256']
    catalogue=json.loads((REPO/'content/standard/catalogues/legacy-gameplay.json').read_text());entry=next(r for r in catalogue['ships'] if r['id']==meta['id']);assert entry['hardpointSlots']==5 and not entry.get('hardpointMounts') and meta['equipment_slots']==dict(declared=5,calibrated_3d_mounts=0)
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native_normals=normal_evidence(meshes,authored=True);native=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes);assert len(materials)==4 and len(meshes)==meta['mesh_objects']
    for image in bpy.data.images:
        if image.source=='FILE':assert sha(ROOT/image.name)==hashlib.sha256(image.packed_file.data).hexdigest()
    transforms={o.name:([list(row) for row in o.matrix_world],geometry_bounds([o])) for o in meshes}
    cam=bpy.context.scene.camera;front=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale)
    offset=Vector((4,-10,6)).normalized()*20;cam.location=Vector((0,-1.20,.20))+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.60;detail=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale);render_to(bpy.context.scene,ROOT/'hull-detail.png')
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
    report=dict(issue=1021,verifier_sha256=sha(Path(__file__)),blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],mesh_objects=len(meshes),materials=materials,native=native,imported=exported,textures=textures,maximum_corner_normal_error=normal_error,checks=['Closed positive topology, bounds/transforms, packed image bytes and decoded texture pixels','Authored box UVs, six measured dents; odd/even containment for bodies/bridge/rails/arms/tail/trims with clear axes, fore interface, aft projections and fitted patches/fasteners','One alignment helper positions/axes under four rigid rotations; no animation timing claim'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('ARTEMIAN_HARDCORE_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
