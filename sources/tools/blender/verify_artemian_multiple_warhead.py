"""Scoped native/imported runtime verification, separate from artistic acceptance."""
import hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_artemian_multiple_warhead import ROOT,REPO,sha
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from artemian_multiple_warhead_parts import CORE,TUBE,NOSE,TAIL,PROFILES,LOCATIONS,ROTATIONS,SOCKETS,DENTS,PANELS,STRAPS,surface,hull_frame
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
    for name in ['Artemian Multiple Warhead | worn red polar alloy','Artemian Multiple Warhead | worn green body alloy','Artemian Multiple Warhead | worn gold belt alloy']:
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
            if obj.name in PROFILES:
                start,end=PROFILES[obj.name][0][0],PROFILES[obj.name][-1][0];values=[]
                for index in face.loop_indices:
                    p=ROTATIONS[obj.name].transposed() @ (obj.data.vertices[obj.data.loops[index].vertex_index].co-LOCATIONS[obj.name])
                    values.append(((math.atan2(p.y,p.x)/math.tau)%1,(p.z-start)/(end-start)))
                # glTF triangulates cap n-gons, so permit equivalent per-loop
                # integer U wrap while retaining exact angular/axial mapping.
                for index,(u,v) in zip(face.loop_indices,values):
                    actual=uv.data[index].uv;du=actual.x-u
                    assert abs(du-round(du))<2e-5 and abs(actual.y-v)<2e-5,(obj.name,'Lathe UV mismatch')
                continue
            valid=False
            for axes in [(0,1),(0,2),(1,2)]:
                if all(max(abs(uv.data[i].uv[j]-(points[obj.data.loops[i].vertex_index][a]-low[a])/max(1e-8,high[a]-low[a])) for j,a in enumerate(axes))<2e-5 for i in face.loop_indices): valid=True;break
            assert valid,(obj.name,'UV is not an authored box projection')
        mapped+=1
    assert mapped==11
    return dict(materials=result,mapped_meshes=mapped)


def structure(meshes,imported=False):
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:missile/artemian/multiple-warhead' and root['forward_axis']=='local -Y'
    assert all(obj.parent==root for obj in meshes)
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6
    # glTF splits vertices at UV/flat-normal seams; test geometric closure after a one-millionth-unit weld in the diagnostic BMesh only.
    seam_splits={};geometric_vertices={}
    for obj in meshes:
        bm=bmesh.new();bm.from_mesh(obj.data);before=len(bm.verts)
        if imported: bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        seam_splits[obj.name]=before-len(bm.verts);geometric_vertices[obj.name]=len(bm.verts)
        assert all(e.is_manifold for e in bm.edges),obj.name+' geometric boundary';assert bm.calc_volume(signed=True)>0;bm.free()
    assert len(meshes)==23
    dents=[];assembly_contacts=0;contacts=0;fastener_contacts=0
    for owner,(phi,z,depth) in DENTS.items():
        n=ROTATIONS[owner] @ Vector((math.cos(phi),math.sin(phi),0));hit=ray(bpy.data.objects[owner],surface(owner,phi,z,.5),-n);assert hit
        measured=(surface(owner,phi,z,depth)-hit).dot(n);assert depth*.5<measured<depth*1.5,(owner,measured);dents.append(measured)
    def join(a,b,points):
        nonlocal assembly_contacts
        for p in points:assert inside(bpy.data.objects[a],p) and inside(bpy.data.objects[b],p),('Assembly gap',a,b,p);assembly_contacts+=1
    join(CORE,TUBE,[(x,0,0) for x in [-.20,0,.20]])
    join(CORE,NOSE,[(x,-.32,0) for x in [-.20,0,.20]])
    join(TUBE,TAIL,[(x,.32,0) for x in [-.20,0,.20]])
    for y,owner in [(-.06,CORE),(.06,TUBE)]:
        for phi in [0,math.pi/2,math.pi,3*math.pi/2]:join(owner,'Artemian Multiple Warhead gold transverse belt',[(.410*math.cos(phi),y,.410*math.sin(phi))])
    exposed_castings=0
    for phi in [0,math.pi,math.pi/4,5*math.pi/4]:
        point=Vector((.445*math.cos(phi),0,.445*math.sin(phi)))
        assert inside(bpy.data.objects['Artemian Multiple Warhead gold transverse belt'],point) and all(not inside(obj,point) for obj in meshes if obj.name!='Artemian Multiple Warhead gold transverse belt'),'Belt buried';exposed_castings+=1
    exposed_straps=0
    for i,(owner,y0,y1,phi) in enumerate(STRAPS):
        name='Artemian Multiple Warhead green longitudinal strap '+str(i);point=surface(owner,phi,-.05 if owner==CORE else .05,.024)
        assert inside(bpy.data.objects[name],point) and all(not inside(obj,point) for obj in meshes if obj.name!=name),('Green strap buried',name);exposed_straps+=1
    waist_clearance=0
    for y in [-.55,.55]:
        point=Vector((.10,y,0));assert all(not inside(obj,point) for obj in meshes),('Compact shell grew an axial extension',point);waist_clearance+=1
    for y in [-.20,0,.20]:assert any(inside(bpy.data.objects[owner],(0,y,0)) for owner in [CORE,TUBE]),'Missing compact shell volume'
    faceted_samples=0
    for owner,y in [(CORE,-.30),(TUBE,.30)]:
        for phi in [0,math.pi/16,math.pi/8,3*math.pi/16,math.pi,17*math.pi/16]:
            n=ROTATIONS[owner] @ Vector((math.cos(phi),math.sin(phi),0));target=surface(owner,phi,y);hit=ray(bpy.data.objects[owner],target+n,-n)
            assert hit and (hit-target).length<.0004,('Faceted shell mismatch',owner,phi);faceted_samples+=1
    meta=json.loads((ROOT/'model.json').read_text());assert len(meta['conformal_panels'])==10
    for spec in meta['conformal_panels']:
        obj=bpy.data.objects[spec['name']];support=bpy.data.objects[spec['support']];offset=-.005 if spec['support']==spec['owner'] else -.004 if 'centre recess surround' in spec['support'] else .006
        for zf in [.2,.5,.8]:
            z=spec['z0']+(spec['z1']-spec['z0'])*zf
            for pf in [.2,.5,.8]:
                phi=spec['phi']+spec['width']*(-1+2*pf);probe=surface(spec['owner'],phi,z,offset)
                assert inside(obj,probe) and inside(support,probe),('Fitted patch root gap',spec['name'],zf,pf);contacts+=1
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        cover=bpy.data.objects['Artemian Multiple Warhead service cover '+str(i)]
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);probe=p+n*.003
                assert inside(cover,probe) and inside(bpy.data.objects['Artemian Multiple Warhead fastener '+str(i)+' '+str(j)+' '+str(k)],probe),'Service fastener gap';fastener_contacts+=1
    sockets={};root.rotation_mode='QUATERNION'
    for axis,angle in [((0,0,1),0),((0,0,1),math.pi/2),((1,0,0),math.pi/2),((0,1,0),math.pi/2)]:
        root.rotation_quaternion=Quaternion(axis,angle);bpy.context.view_layer.update();rotation=root.matrix_world.to_3x3()
        for name,(p,n) in SOCKETS.items():
            obj=bpy.data.objects[name];assert obj.parent==root and obj['forward_axis']=='local +Z'
            assert (obj.matrix_world.translation-rotation @ Vector(p)).length<1e-5
            forward=(obj.matrix_world.to_3x3() @ Vector((0,0,1))).normalized();assert (forward-rotation @ Vector(n)).length<1e-5
            sockets[name]=dict(position=list(p),forward=list(n))
    root.rotation_quaternion=Quaternion((0,0,1),0);bpy.context.view_layer.update()
    bounds=geometry_bounds(meshes);assert -.451<bounds[0]<-.449 and .449<bounds[3]<.451 and -.501<bounds[1]<-.499 and .499<bounds[4]<.501 and -.461<bounds[2]<-.459 and .459<bounds[5]<.461,bounds
    assert not any(obj.animation_data for obj in meshes)
    return dict(bounds=bounds,dent_depths=dents,sockets=sockets,seam_vertices_welded=seam_splits,geometric_vertices=geometric_vertices,closure_weld_tolerance=1e-6 if imported else 0,assembly_contacts=assembly_contacts,fitted_patch_samples=contacts,service_fasteners=fastener_contacts,axial_extension_clearance_samples=waist_clearance,occupied_body_samples=3,exposed_belt_samples=exposed_castings,exposed_longitudinal_strap_samples=exposed_straps,faceted_section_samples=faceted_samples)




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
    for field,p in [('generator_sha256',Path(__file__).with_name('build_artemian_multiple_warhead.py')),('parts_sha256',Path(__file__).with_name('artemian_multiple_warhead_parts.py')),('reference_sha256',REPO/'docs/reconstruction/models/missile-reference-index.json'),('functional_source_sha256',REPO/'docs/reconstruction/models/functional-text-index.json'),('catalogue_sha256',REPO/'content/standard/catalogues/legacy-gameplay.json'),('authored_wear_sha256',ROOT/'authored-wear.json')]:assert sha(p)==meta[field]
    assert sha(REPO/'docs/reconstruction/models/cultural-architecture-index.json')==meta['cultural_style_sha256']
    for name,digest in meta['helper_sha256'].items():assert sha(Path(__file__).with_name(name))==digest
    assert sha(Path(__file__).with_name('author_artemian_multiple_warhead_wear.py'))==wear['generator_sha256']
    for name,digest in wear['images'].items():assert sha(ROOT/name)==digest
    for ext in ['blend','glb']:assert sha(ROOT/('model.'+ext))==meta[ext+'_sha256']
    catalogue=json.loads((REPO/'content/standard/catalogues/legacy-gameplay.json').read_text());entry=next(r for r in catalogue['missiles'] if r['id']==meta['id']);assert entry['legacy']['globalTypeIndex']==43 and entry['legacy']['totalOreUnits']==8 and entry['legacy']['missileBudgetCost']==25 and entry['effectBehaviorId']=='openfa:missile-effect-behavior/scatter'
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native_normals=normal_evidence(meshes,authored=True);native=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes);assert len(materials)==5 and len(meshes)==meta['mesh_objects']
    for image in bpy.data.images:
        if image.source=='FILE':assert sha(ROOT/image.name)==hashlib.sha256(image.packed_file.data).hexdigest()
    transforms={o.name:([list(row) for row in o.matrix_world],geometry_bounds([o])) for o in meshes}
    cam=bpy.context.scene.camera;front=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale)
    offset=Vector((4,10,6)).normalized()*20;cam.location=Vector((.02,0,.02))+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.0;detail=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale);render_to(bpy.context.scene,ROOT/'hull-detail.png')
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
    report=dict(issue=1073,verifier_sha256=sha(Path(__file__)),blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],mesh_objects=len(meshes),materials=materials,native=native,imported=exported,textures=textures,maximum_corner_normal_error=normal_error,checks=['Closed positive topology, bounds/transforms, packed image bytes and decoded texture pixels','Angular/axial primary UVs and box detail UVs, four measured dents; actual green shell/red polar cap/gold belt contacts, fitted green straps/covers/fasteners; two axial-extension clearance witnesses and twelve actual faceted-section probes','Uncalibrated alignment helper under yaw/pitch/roll; no aiming/recoil/mount calibration claim'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('ARTEMIAN_MULTIPLE_WARHEAD_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
