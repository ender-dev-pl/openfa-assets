"""Scoped native/imported runtime verification, separate from artistic acceptance."""
import hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_braccatian_skymech import ROOT,REPO,sha
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from braccatian_skymech_parts import PROFILES,SOCKETS,DENTS,CAP_BANDS,CORE_BANDS,POD_PROFILE,POD_DENT,surface,pod_axis,pod_centre
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
    for name in ['SkyMech | worn rose copper','SkyMech | worn gold shell']:
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
    assert mapped==44
    return dict(materials=result,mapped_meshes=mapped)


def structure(meshes,imported=False):
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:ship/braccatian/skymech' and root['forward_axis']=='local +Z'
    assert all(obj.parent==root for obj in meshes)
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6
    # glTF splits vertices at UV/flat-normal seams; test geometric closure after a one-millionth-unit weld in the diagnostic BMesh only.
    seam_splits={};geometric_vertices={}
    for obj in meshes:
        bm=bmesh.new();bm.from_mesh(obj.data);before=len(bm.verts)
        if imported: bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        seam_splits[obj.name]=before-len(bm.verts);geometric_vertices[obj.name]=len(bm.verts)
        assert all(e.is_manifold for e in bm.edges),obj.name+' geometric boundary';assert bm.calc_volume(signed=True)>0;bm.free()
    assert len(meshes)==74
    dents=[]
    for name,(phi,z,depth) in DENTS.items():
        obj=bpy.data.objects[name];n=Vector((math.cos(phi),math.sin(phi),0));hit=ray(obj,n*3+Vector((0,0,z)),-n);assert hit
        measured=profile_radius(PROFILES[name],z)-math.hypot(hit.x,hit.y);assert depth*.5<measured<depth*1.5,('Missing physical dent',name,measured);dents.append(measured)
    core=bpy.data.objects['SkyMech dark axial core'];upper=bpy.data.objects['SkyMech upper gold dome'];lower=bpy.data.objects['SkyMech lower gold cone']
    for cap,z in [(upper,1.20),(lower,-1.40)]:
        p=Vector((.10,.02,z));assert inside(core,p) and inside(cap,p),'Cap/core joint gap'
    for name,owner,low,high in CAP_BANDS:
        band=bpy.data.objects[name];body=bpy.data.objects[owner]
        assert not inside(band,Vector((0,0,(low+high)/2))),'Cap rim void is filled'
        for phi in [0,math.pi/2,math.pi,3*math.pi/2]:
            p=surface(owner,phi,(low+high)/2,-.010);assert inside(body,p) and inside(band,p),'Cap rim gap'
    equator=bpy.data.objects['SkyMech rose equatorial collar'];assert not inside(equator,Vector((0,0,0))),'Equatorial void is filled'
    p=Vector((.40,0,0));assert inside(core,p) and inside(equator,p),'Equatorial collar gap'
    rib_contacts=0
    for i,(low,high,_,_) in enumerate(CORE_BANDS):
        band=bpy.data.objects['SkyMech core gold band '+str(i)]
        assert not inside(band,Vector((0,0,(low+high)/2))),'Core band void is filled'
        for phi in [0,math.pi/2,math.pi,3*math.pi/2]:
            p=surface(core.name,phi,(low+high)/2,-.008);assert inside(core,p) and inside(band,p),'Core band gap'
    for i in range(8):
        phi=i*math.tau/8;n=Vector((math.cos(phi),math.sin(phi),0));top=bpy.data.objects['SkyMech upper column rib '+str(i)];bottom=bpy.data.objects['SkyMech lower column rib '+str(i)]
        for rib,r,z in [(top,.33,.75),(bottom,.31,-.75)]:
            p=n*r+Vector((0,0,z));assert inside(core,p) and inside(rib,p),'Column rib/core gap';rib_contacts+=1
        for rib,cap,r,z in [(top,upper,.35,1.25),(bottom,lower,.33,-1.35)]:
            p=n*r+Vector((0,0,z));assert inside(cap,p) and inside(rib,p),'Column rib/cap gap';rib_contacts+=1
        for j,(low,high,_,_) in enumerate(CORE_BANDS):
            rib=top if j<2 else bottom;r=.35 if j<2 else .33;p=n*r+Vector((0,0,(low+high)/2))
            assert inside(rib,p) and inside(bpy.data.objects['SkyMech core gold band '+str(j)],p),'Column rib/band gap';rib_contacts+=1
    module_contacts=0
    for i in range(4):
        n=pod_axis(i);centre=pod_centre(i);pod=bpy.data.objects['SkyMech rose radial module '+str(i)];face=bpy.data.objects['SkyMech gold module face '+str(i)];rim=bpy.data.objects['SkyMech module gold rim '+str(i)];arm=bpy.data.objects['SkyMech radial arm '+str(i)]
        assert not inside(rim,centre),'Module rim void is filled'
        theta,z,depth=POD_DENT;origin=pod.matrix_world @ Vector((2*math.cos(theta),2*math.sin(theta),z));direction=pod.matrix_world.to_3x3() @ Vector((-math.cos(theta),-math.sin(theta),0));hit=ray(pod,origin,direction);assert hit
        local=pod.matrix_world.inverted() @ hit;measured=profile_radius(POD_PROFILE,z)-math.hypot(local.x,local.y);assert depth*.5<measured<depth*1.5,'Missing module dent';dents.append(measured)
        p=n*.40+Vector((0,0,.05));assert inside(core,p) and inside(equator,p) and inside(arm,p),'Arm/core/collar gap'
        p=n*1.40+Vector((0,0,.05));assert inside(pod,p) and inside(arm,p),'Arm/module gap'
        p=pod.matrix_world @ Vector((.05,.02,.15));assert inside(pod,p) and inside(face,p),'Module gold face gap'
        for phi in [0,math.pi/2,math.pi,3*math.pi/2]:
            r=profile_radius(POD_PROFILE,0)-.006;p=pod.matrix_world @ Vector((r*math.cos(phi),r*math.sin(phi),0));assert inside(pod,p) and inside(rim,p),'Module rim gap';module_contacts+=1
        p=centre+n*.225;assert inside(face,p) and inside(bpy.data.objects['SkyMech module face fitting '+str(i)],p),'Module face fitting gap'
        housing=bpy.data.objects['SkyMech arm service housing '+str(i)];inset=bpy.data.objects['SkyMech arm dark inset '+str(i)]
        p=n*.94+Vector((0,0,.05));assert inside(arm,p) and inside(housing,p),'Arm housing gap'
        p=n*.94+Vector((0,0,.146));assert inside(housing,p) and inside(inset,p),'Housing inset gap'
        for j,distance in enumerate([-.11,0,.11]):
            p=n*(.94+distance)+Vector((0,0,.1615));assert inside(inset,p) and inside(bpy.data.objects['SkyMech arm amber tile '+str(i)+' '+str(j)],p),'Arm tile gap'
    meta=json.loads((ROOT/'model.json').read_text());panels=meta['conformal_panels'];assert len(panels)==6;contacts=0
    for spec in panels:
        obj=bpy.data.objects[spec['name']];support=bpy.data.objects[spec['support']];offset=-.004 if spec['support']==spec['owner'] else .005
        for zf in [.2,.5,.8]:
            z=spec['z0']+(spec['z1']-spec['z0'])*zf
            for uf in [.2,.5,.8]:
                phi=spec['phi']+spec['width']*(-1+2*uf);p=surface(spec['owner'],phi,z,offset)
                assert inside(obj,p) and inside(support,p),('Upper panel root gap',spec['name'],zf,uf);contacts+=1
    p=Vector((.005,.003,1.997));assert inside(upper,p) and inside(bpy.data.objects['SkyMech upper aerial'],p) and inside(bpy.data.objects['SkyMech crown hatch'],p),'Crown/aerial joint gap'
    p=Vector((.005,.003,-2.11));assert inside(lower,p) and inside(bpy.data.objects['SkyMech lower aerial'],p),'Lower aerial joint gap'
    sockets={};root.rotation_mode='QUATERNION'
    for axis,angle in [((0,0,1),0),((0,0,1),math.pi/2),((1,0,0),math.pi/2),((0,1,0),math.pi/2)]:
        root.rotation_quaternion=Quaternion(axis,angle);bpy.context.view_layer.update();rotation=root.matrix_world.to_3x3()
        for name,(p,n) in SOCKETS.items():
            obj=bpy.data.objects[name];assert obj.parent==root and obj['forward_axis']=='local +Z'
            assert (obj.matrix_world.translation-rotation @ Vector(p)).length<1e-5
            forward=(obj.matrix_world.to_3x3() @ Vector((0,0,1))).normalized();assert (forward-rotation @ Vector(n)).length<1e-5
            sockets[name]=dict(position=list(p),forward=list(n))
    root.rotation_quaternion=Quaternion((0,0,1),0);bpy.context.view_layer.update()
    bounds=geometry_bounds(meshes);assert -1.83<bounds[0]<-1.79 and 1.79<bounds[3]<1.83 and -1.83<bounds[1]<-1.79 and 1.79<bounds[4]<1.83 and -2.51<bounds[2]<-2.49 and 2.44<bounds[5]<2.46
    assert not any(obj.animation_data for obj in meshes)
    return dict(bounds=bounds,dent_depths=dents,sockets=sockets,seam_vertices_welded=seam_splits,geometric_vertices=geometric_vertices,closure_weld_tolerance=1e-6 if imported else 0,panel_root_samples=contacts,rib_root_samples=rib_contacts,module_rim_root_samples=module_contacts,major_cap_dents=2,module_dents=4)


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
    for field,p in [('generator_sha256',Path(__file__).with_name('build_braccatian_skymech.py')),('parts_sha256',Path(__file__).with_name('braccatian_skymech_parts.py')),('reference_sha256',REPO/'docs/reconstruction/models/ship-reference-index.json'),('functional_source_sha256',REPO/'docs/reconstruction/models/functional-text-index.json'),('cultural_style_sha256',REPO/'docs/reconstruction/models/cultural-architecture-index.json'),('catalogue_sha256',REPO/'content/standard/catalogues/legacy-gameplay.json'),('authored_wear_sha256',ROOT/'authored-wear.json')]:assert sha(p)==meta[field]
    for name,digest in meta['helper_sha256'].items():assert sha(Path(__file__).with_name(name))==digest
    assert sha(Path(__file__).with_name('author_braccatian_skymech_wear.py'))==wear['generator_sha256']
    for name,digest in wear['images'].items():assert sha(ROOT/name)==digest
    for ext in ['blend','glb']:assert sha(ROOT/('model.'+ext))==meta[ext+'_sha256']
    catalogue=json.loads((REPO/'content/standard/catalogues/legacy-gameplay.json').read_text());entry=next(r for r in catalogue['ships'] if r['id']==meta['id']);assert entry['hardpointSlots']==5 and not entry.get('hardpointMounts') and meta['equipment_slots']==dict(declared=5,calibrated_3d_mounts=0)
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native_normals=normal_evidence(meshes,authored=True);native=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes);assert len(materials)==5 and len(meshes)==meta['mesh_objects']
    for image in bpy.data.images:
        if image.source=='FILE':assert sha(ROOT/image.name)==hashlib.sha256(image.packed_file.data).hexdigest()
    transforms={o.name:([list(row) for row in o.matrix_world],geometry_bounds([o])) for o in meshes}
    cam=bpy.context.scene.camera;front=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale)
    offset=Vector((4,-10,5)).normalized()*20;cam.location=Vector((0,0,.85))+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.90;detail=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale);render_to(bpy.context.scene,ROOT/'hull-detail.png')
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
    report=dict(issue=1011,verifier_sha256=sha(Path(__file__)),blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],mesh_objects=len(meshes),materials=materials,native=native,imported=exported,textures=textures,maximum_corner_normal_error=normal_error,checks=['Closed positive topology, bounds/transforms, packed image bytes and decoded texture pixels','Authored box UVs; six measured dents; cap/core, 56 rib contacts, annular rims/bands, radial arm/module/face/housing/tile joins, 54 curved panel roots and aerial/hatch attachment samples','One alignment helper positions/axes under four rigid rotations; no animation timing claim'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_SKYMECH_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
