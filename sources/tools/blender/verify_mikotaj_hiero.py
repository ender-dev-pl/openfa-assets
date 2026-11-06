"""Scoped native/imported runtime verification, separate from artistic acceptance."""
import hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_mikotaj_hiero import ROOT,REPO,sha
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from mikotaj_hiero_parts import PROFILES,SOCKETS,BODY_DENT,FIN_DENT,fin_point,roof
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
    for name in ['Hiero | worn slate blue metal','Hiero | dulled gold accents']:
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
    assert mapped==13
    return dict(materials=result,mapped_meshes=mapped)


def structure(meshes,imported=False):
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:ship/mikotaj/hiero' and root['forward_axis']=='local -Y'
    assert all(obj.parent==root for obj in meshes)
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6
    # glTF splits vertices at UV/flat-normal seams; test geometric closure after a one-millionth-unit weld in the diagnostic BMesh only.
    seam_splits={};geometric_vertices={}
    for obj in meshes:
        bm=bmesh.new();bm.from_mesh(obj.data);before=len(bm.verts)
        if imported: bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        seam_splits[obj.name]=before-len(bm.verts);geometric_vertices[obj.name]=len(bm.verts)
        assert all(e.is_manifold for e in bm.edges),obj.name+' geometric boundary';assert bm.calc_volume(signed=True)>0;bm.free()
    assert len(meshes)==34
    body=bpy.data.objects['Hiero faceted hull'];spike=bpy.data.objects['Hiero upper spike'];keel=bpy.data.objects['Hiero lower keel'];dents=[]
    phi,z,depth=BODY_DENT;n=Vector((math.cos(phi),math.sin(phi),0));hit=ray(body,n*3+Vector((0,0,z)),-n);assert hit
    measured=profile_radius(PROFILES[body.name],z)*math.cos(math.pi/8)-math.hypot(hit.x,hit.y);assert depth*.5<measured<depth*1.5,('Missing body dent',measured);dents.append(measured)
    for obj,z in [(spike,.175),(keel,-.15)]:
        for x in [-.03,0,.03]:
            p=Vector((x,.015,z));assert inside(body,p) and inside(obj,p),'Spike/keel root gap'
    fin_contacts=0;inset_contacts=0
    for i in range(4):
        obj=bpy.data.objects['Hiero radial fin '+str(i)];r,t,depth=FIN_DENT;p=fin_point(i,r,t);hit=ray(obj,(p.x,p.y,2),(0,0,-1));assert hit
        measured=.075-.10*(r-.36)-hit.z;assert depth*.5<measured<depth*1.5,('Missing fin dent',i,measured);dents.append(measured)
        for r in [.40,.46,.50]:
            for t in [-.035,0,.035]:
                p=fin_point(i,r,t,-.02);assert inside(body,p) and inside(obj,p),('Fin root gap',i,r,t);fin_contacts+=1
        inset=bpy.data.objects['Hiero fin inset '+str(i)]
        for r in [.70,.84,.98]:
            for t in [-.010,0,.010]:
                p=fin_point(i,r,t,-.004);assert inside(obj,p) and inside(inset,p),'Fin inset gap';inset_contacts+=1
    collar=bpy.data.objects['Hiero octagonal gold collar'];z=(.24+.275)/2;radius=profile_radius(PROFILES[spike.name],z)*math.cos(math.pi/8)-.006
    assert not inside(collar,Vector((0,0,z))),'Collar void is filled'
    for i in range(8):
        phi=i*math.pi/4;p=Vector((radius*math.cos(phi),radius*math.sin(phi),z));assert inside(spike,p) and inside(collar,p),'Gold collar root gap'
    stripe=bpy.data.objects['Hiero gold spike stripe']
    for z in [.31,.38,.46]:
        radius=profile_radius(PROFILES[spike.name],z)
        for u in [-.4,0,.4]:
            p=Vector((radius*math.sin(math.pi/8)*u,-radius*math.cos(math.pi/8)+.003,z));assert inside(spike,p) and inside(stripe,p),'Gold stripe root gap'
    meta=json.loads((ROOT/'model.json').read_text());panels=meta['conformal_panels'];assert len(panels)==12;contacts=0
    for spec in panels:
        obj=bpy.data.objects[spec['name']];support=bpy.data.objects[spec['support']];offset=-.004 if spec['support']==body.name else .0045
        for rf in [-.30,0,.30]:
            r=spec['radial']+spec['width']*rf
            for tf in [-.30,0,.30]:
                t=spec['depth']*tf;p,_=roof(spec['phi'],r,t);p+=Vector((0,0,offset))
                assert inside(obj,p) and inside(support,p),('Roof panel contact gap',spec['name'],rf,tf);contacts+=1
    for i in range(4):
        phi=math.pi/4+i*math.pi/2;cover=bpy.data.objects['Hiero roof service cover '+str(i)]
        for j,t in enumerate([-.040,.040]):
            p,normal=roof(phi,.34,t);p+=normal*.003;assert inside(cover,p) and inside(bpy.data.objects['Hiero roof fastener '+str(i)+' '+str(j)],p),'Roof fastener gap'
    p=Vector((.001,.001,.956));assert inside(spike,p) and inside(bpy.data.objects['Hiero upper needle'],p),'Needle root gap'
    sockets={};root.rotation_mode='QUATERNION'
    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
        root.rotation_quaternion=Quaternion((0,0,1),angle);bpy.context.view_layer.update();rotation=root.matrix_world.to_3x3()
        for name,(p,n) in SOCKETS.items():
            obj=bpy.data.objects[name];assert obj.parent==root and obj['forward_axis']=='local +Z'
            assert (obj.matrix_world.translation-rotation @ Vector(p)).length<1e-5
            forward=(obj.matrix_world.to_3x3() @ Vector((0,0,1))).normalized();assert (forward-rotation @ Vector(n)).length<1e-5
            sockets[name]=dict(position=list(p),forward=list(n))
    root.rotation_quaternion=Quaternion((0,0,1),0);bpy.context.view_layer.update()
    bounds=geometry_bounds(meshes);assert -1.17<bounds[0]<-1.15 and 1.15<bounds[3]<1.17 and -1.17<bounds[1]<-1.15 and 1.15<bounds[4]<1.17 and -.49<bounds[2]<-.48 and 1.09<bounds[5]<1.11
    assert not any(obj.animation_data for obj in meshes)
    return dict(bounds=bounds,dent_depths=dents,sockets=sockets,seam_vertices_welded=seam_splits,geometric_vertices=geometric_vertices,closure_weld_tolerance=1e-6 if imported else 0,roof_panel_root_samples=contacts,fin_root_samples=fin_contacts,fin_inset_root_samples=inset_contacts,gold_collar_samples=8,gold_stripe_samples=9,roof_fasteners=8)


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
    for field,p in [('generator_sha256',Path(__file__).with_name('build_mikotaj_hiero.py')),('parts_sha256',Path(__file__).with_name('mikotaj_hiero_parts.py')),('reference_sha256',REPO/'docs/reconstruction/models/ship-reference-index.json'),('functional_source_sha256',REPO/'docs/reconstruction/models/functional-text-index.json'),('cultural_style_sha256',REPO/'docs/reconstruction/models/cultural-architecture-index.json'),('catalogue_sha256',REPO/'content/standard/catalogues/legacy-gameplay.json'),('authored_wear_sha256',ROOT/'authored-wear.json')]:assert sha(p)==meta[field]
    for name,digest in meta['helper_sha256'].items():assert sha(Path(__file__).with_name(name))==digest
    assert sha(Path(__file__).with_name('author_mikotaj_hiero_wear.py'))==wear['generator_sha256']
    for name,digest in wear['images'].items():assert sha(ROOT/name)==digest
    for ext in ['blend','glb']:assert sha(ROOT/('model.'+ext))==meta[ext+'_sha256']
    catalogue=json.loads((REPO/'content/standard/catalogues/legacy-gameplay.json').read_text());entry=next(r for r in catalogue['ships'] if r['id']==meta['id']);assert entry['hardpointSlots']==2 and not entry.get('hardpointMounts') and meta['equipment_slots']==dict(declared=2,calibrated_3d_mounts=0)
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native_normals=normal_evidence(meshes,authored=True);native=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes);assert len(materials)==4 and len(meshes)==meta['mesh_objects']
    for image in bpy.data.images:
        if image.source=='FILE':assert sha(ROOT/image.name)==hashlib.sha256(image.packed_file.data).hexdigest()
    transforms={o.name:([list(row) for row in o.matrix_world],geometry_bounds([o])) for o in meshes}
    cam=bpy.context.scene.camera;front=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale)
    offset=Vector((4,-10,6)).normalized()*20;cam.location=Vector((0,0,.25))+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.85;detail=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale);render_to(bpy.context.scene,ROOT/'hull-detail.png')
    scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'));imported=[o for o in scene.objects if o.type=='MESH'];check_meshes(imported,allow_packed_images=True)
    exported_normals=normal_evidence(imported);normal_error=0
    for name,points in native_normals.items():
        other=exported_normals[name];assert points.keys()==other.keys(),(name,'Normal positions differ')
        for p,values in points.items():
            for n in values: normal_error=max(normal_error,min((Vector(n)-Vector(v)).length for v in other[p]))
    assert normal_error<1e-3,'Exported corner normals differ beyond custom-normal quantization'
    exported=structure(imported,imported=True);assert exported['geometric_vertices']==native['geometric_vertices'],'Export lost geometric vertices';assert texture_evidence(imported)==textures
    assert {o.name for o in imported}==set(transforms)
    for o in imported:
        matrix,bounds=transforms[o.name];assert max(abs(o.matrix_world[i][j]-matrix[i][j]) for i in range(4) for j in range(4))<1e-5;assert max(abs(a-b) for a,b in zip(geometry_bounds([o]),bounds))<1e-5
    other=material_values(imported);assert materials.keys()==other.keys()
    for name,value in materials.items():assert max(abs(a-b) for a,b in zip(value[0]+value[1:],other[name][0]+other[name][1:]))<1/255+.00001
    for name,camera in [('imported-glb-front-quarter',front),('imported-glb-hull-detail',detail)]:
        scene.camera.location=camera[0];scene.camera.rotation_euler=camera[1];scene.camera.data.ortho_scale=camera[2];render_to(scene,ROOT/(name+'.png'))
    report=dict(issue=1012,verifier_sha256=sha(Path(__file__)),blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],mesh_objects=len(meshes),materials=materials,native=native,imported=exported,textures=textures,maximum_corner_normal_error=normal_error,checks=['Closed positive topology, bounds/transforms, packed image bytes and decoded texture pixels','Authored box UVs, five measured dents; odd/even containment for fin/spike/keel/collar/stripe/roof/fastener/needle contacts; empty collar axis witness','One alignment helper positions/axes under four rigid rotations; no animation timing claim'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('MIKOTAJ_HIERO_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
