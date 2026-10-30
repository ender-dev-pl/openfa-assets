"""Scoped native/imported runtime verification, separate from artistic acceptance."""
import hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_braccatian_heartsblood import ROOT,REPO,sha
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from braccatian_heartsblood_parts import SOCKETS,SOURCE,INHERITED,renamed,geometry_signature,POD_PROFILE,BAND_CENTRES,CRADLE_Y,pod_centre,main_surface
from manufactured_vessels import profile_radius
from braccatian_widowmaker_parts import DENTS,section,surface,patch_halfwidth
from verify_assault_fighter import check_meshes
from verify_nuclear_missile import geometry_bounds
from verify_cannon_equipment import ray
from verify_rigellian_filtration import material_values


def inside(obj,p):
    n=Vector((.173,.291,.941)).normalized();a=ray(obj,p-n*8,n);b=ray(obj,p+n*8,-n)
    return a is not None and b is not None and a.dot(n)<p.dot(n)<b.dot(n)


def texture_evidence(meshes):
    result={}
    for name in ['HeartsBlood | worn rose copper','HeartsBlood | worn gold hull','HeartsBlood | worn grey armour']:
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
    assert mapped==50
    return dict(materials=result,mapped_meshes=mapped)


def structure(meshes,imported=False):
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:ship/braccatian/heartsblood' and root['forward_axis']=='local -Y'
    assert all(obj.parent==root for obj in meshes)
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-6
    # glTF splits vertices at UV/flat-normal seams; test geometric closure after a one-millionth-unit weld in the diagnostic BMesh only.
    seam_splits={};geometric_vertices={}
    for obj in meshes:
        bm=bmesh.new();bm.from_mesh(obj.data);before=len(bm.verts)
        if imported: bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        seam_splits[obj.name]=before-len(bm.verts);geometric_vertices[obj.name]=len(bm.verts)
        assert all(e.is_manifold for e in bm.edges),obj.name+' geometric boundary';assert bm.calc_volume(signed=True)>0;bm.free()
    dents=[]
    for name,(x,y,depth) in DENTS.items():
        obj=bpy.data.objects[renamed(name)];w,z,h=section(name,y);hit=ray(obj,(x,y,3),(0,0,-1));assert hit
        measured=z+h*math.sqrt(1-(x/w)**2)-hit.z;assert depth*.5<measured<depth*1.5,('Missing inherited physical dent',name,measured);dents.append(measured)
    body=bpy.data.objects['HeartsBlood gold pressure hull'];nose=bpy.data.objects['HeartsBlood rose nose']
    for x in [-.1,0,.1]:
        p=Vector((x,-1.50,0));assert inside(body,p) and inside(nose,p),'Nose/body joint gap'
    inherited=json.loads(SOURCE.with_name('model.json').read_text());panels=[p for p in inherited['conformal_panels'] if p['name'].startswith('WidowMaker rose neck accent')];assert len(panels)==8;contacts=0
    for spec in panels:
        obj=bpy.data.objects[renamed(spec['name'])]
        for yf in [.2,.5,.8]:
            y=spec['y0']+(spec['y1']-spec['y0'])*yf;centre=spec['phi']+spec['drift']*yf;half=patch_halfwidth(spec,y)
            for uf in [.2,.5,.8]:
                p=surface(spec['owner'],centre+half*(-1+2*uf),y,-.005)
                assert inside(obj,p) and inside(body,p),'Inherited neck accent root gap';contacts+=1
    duct_contacts=0;pod_contacts=0;band_contacts=0;cradle_contacts=0
    for i in range(4):
        phi=i*math.pi/2;n=Vector((math.cos(phi),0,math.sin(phi)));centre=pod_centre(i)
        duct=bpy.data.objects['HeartsBlood aft duct housing '+str(i)];floor=bpy.data.objects['HeartsBlood recessed duct floor '+str(i)];x=.39*math.cos(phi);z=.39*math.sin(phi)
        for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
            p=Vector((x+.195*math.cos(angle),1.42,z+.195*math.sin(angle)));assert inside(body,p) and inside(duct,p),'Duct root gap';duct_contacts+=1
        p=Vector((x,1.515,z));assert inside(body,p) and inside(floor,p),'Duct floor/body gap'
        p=Vector((x+.162,1.53,z));assert inside(duct,p) and inside(floor,p),'Duct floor/housing gap'
        assert ray(duct,(x,4,z),(0,-1,0)) is None,'Duct opening is capped'
        hit=ray(floor,(x,4,z),(0,-1,0));assert hit and 1.53<hit.y<1.55,'Duct floor is not recessed'
        pod=bpy.data.objects['HeartsBlood radial pod '+str(i)]
        hit=ray(pod,centre+n*2+Vector((0,.20,0)),-n);assert hit
        measured=profile_radius(POD_PROFILE,.20)-(hit-centre).dot(n);assert .002<measured<.006,('Missing new pod dent',i,measured);dents.append(measured)
        for y,r in [(-.20,.565),(.40,.62),(.70,.65)]:
            p=n*r+Vector((0,y,0));assert inside(body,p) and inside(pod,p),('Pod/body overlap gap',i,y);pod_contacts+=1
        for j,y in enumerate(BAND_CENTRES):
            band=bpy.data.objects['HeartsBlood pod clamp '+str(i)+' '+str(j)]
            for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
                r=profile_radius(POD_PROFILE,y)-.010;p=pod.matrix_world @ Vector((r*math.cos(angle),r*math.sin(angle),y))
                assert inside(pod,p) and inside(band,p),('Pod clamp root gap',i,j,angle);band_contacts+=1
        for label,y in [('fore',-.96),('aft',1.09)]:
            p=centre+Vector((.03,y,0));assert inside(pod,p) and inside(bpy.data.objects['HeartsBlood pod '+label+' cap '+str(i)],p),'Pod terminal root gap'
        for j,y in enumerate(CRADLE_Y):
            cradle=bpy.data.objects['HeartsBlood pod cradle '+str(i)+' '+str(j)];w,_,_=section('WidowMaker gold pressure hull',y)
            p=n*(w-.02)+Vector((0,y,0));assert inside(body,p) and inside(cradle,p),'Cradle hull root gap'
            p=n*.665+Vector((0,y,0));assert inside(pod,p) and inside(cradle,p),'Cradle pod root gap';cradle_contacts+=2
    bezel=bpy.data.objects['HeartsBlood central nose bezel'];face=bpy.data.objects['HeartsBlood central nose face'];n=Vector((0,-1,0))
    for i in range(32):
        phi=i*math.tau/32;p=Vector((.115*math.cos(phi),-2.095,.115*math.sin(phi)));back=ray(bezel,p-n*2,n);front=ray(bezel,p+n*2,-n);skin=ray(nose,p+n*2,-n)
        assert back is not None and front is not None and skin is not None
        assert back.dot(n)<skin.dot(n)<front.dot(n),'Nose bezel root gap'
    p=Vector((0,-2.088,0));assert inside(bezel,p) and inside(face,p),'Nose face/bezel gap'
    for i in range(4):
        phi=i*math.pi/2;x=.40*math.cos(phi);z=.40*math.sin(phi);hit=ray(nose,(x,-4,z),(0,1,0));assert hit
        p=hit+Vector((0,.003,0));assert inside(nose,p) and inside(bpy.data.objects['HeartsBlood gold nose stud '+str(i)],p),'Nose stud gap'
    sockets={};root.rotation_mode='QUATERNION'
    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
        root.rotation_quaternion=Quaternion((0,0,1),angle);bpy.context.view_layer.update();rotation=root.matrix_world.to_3x3()
        for name,(p,n) in SOCKETS.items():
            obj=bpy.data.objects[name];assert obj.parent==root and obj['forward_axis']=='local +Z'
            assert (obj.matrix_world.translation-rotation @ Vector(p)).length<1e-5
            forward=(obj.matrix_world.to_3x3() @ Vector((0,0,1))).normalized();assert (forward-rotation @ Vector(n)).length<1e-5
            sockets[name]=dict(position=list(p),forward=list(n))
    root.rotation_quaternion=Quaternion((0,0,1),0);bpy.context.view_layer.update()
    bounds=geometry_bounds(meshes);assert -1.08<bounds[0]<-1.05 and 1.05<bounds[3]<1.08 and -2.12<bounds[1]<-2.09 and 1.73<bounds[4]<1.76 and -1.08<bounds[2]<-1.05 and 1.05<bounds[5]<1.08
    assert not any(obj.animation_data for obj in meshes)
    return dict(bounds=bounds,dent_depths=dents,sockets=sockets,seam_vertices_welded=seam_splits,geometric_vertices=geometric_vertices,closure_weld_tolerance=1e-6 if imported else 0,inherited_neck_root_samples=contacts,duct_root_samples=duct_contacts,pod_root_samples=pod_contacts,band_root_samples=band_contacts,cradle_root_samples=cradle_contacts,nose_studs=4)


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
    for field,p in [('generator_sha256',Path(__file__).with_name('build_braccatian_heartsblood.py')),('parts_sha256',Path(__file__).with_name('braccatian_heartsblood_parts.py')),('reference_sha256',REPO/'docs/reconstruction/models/ship-reference-index.json'),('functional_source_sha256',REPO/'docs/reconstruction/models/functional-text-index.json'),('cultural_style_sha256',REPO/'docs/reconstruction/models/cultural-architecture-index.json'),('catalogue_sha256',REPO/'content/standard/catalogues/legacy-gameplay.json'),('authored_wear_sha256',ROOT/'authored-wear.json')]:assert sha(p)==meta[field]
    for name,digest in meta['helper_sha256'].items():assert sha(Path(__file__).with_name(name))==digest
    assert sha(Path(__file__).with_name('author_braccatian_heartsblood_wear.py'))==wear['generator_sha256']
    for name,digest in wear['images'].items():assert sha(ROOT/name)==digest
    for ext in ['blend','glb']:assert sha(ROOT/('model.'+ext))==meta[ext+'_sha256']
    catalogue=json.loads((REPO/'content/standard/catalogues/legacy-gameplay.json').read_text());entry=next(r for r in catalogue['ships'] if r['id']==meta['id']);assert entry['hardpointSlots']==6 and not entry.get('hardpointMounts') and meta['equipment_slots']==dict(declared=6,calibrated_3d_mounts=0)
    assert sha(SOURCE)==meta['reused_source_blend_sha256'] and sha(SOURCE.with_name('model.json'))==meta['reused_source_metadata_sha256']
    assert meta['reused_source_objects']==INHERITED and meta['reused_source_blend']=='docs/assets/reconstruction/ships/braccatian/widowmaker/model.blend'
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));source_geometry={name:geometry_signature(bpy.data.objects[name]) for name in INHERITED};source_matrices={name:[list(row) for row in bpy.data.objects[name].matrix_world] for name in INHERITED}
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    for name,digest in source_geometry.items():
        obj=bpy.data.objects[renamed(name)];assert geometry_signature(obj)==digest,(name,'Reused source geometry changed')
        assert max(abs(obj.matrix_world[i][j]-source_matrices[name][i][j]) for i in range(4) for j in range(4))<1e-7,(name,'Reused source transform changed')
    native_normals=normal_evidence(meshes,authored=True);native=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes);assert len(materials)==5 and len(meshes)==meta['mesh_objects']
    for image in bpy.data.images:
        if image.source=='FILE':assert sha(ROOT/image.name)==hashlib.sha256(image.packed_file.data).hexdigest()
    transforms={o.name:([list(row) for row in o.matrix_world],geometry_bounds([o])) for o in meshes}
    cam=bpy.context.scene.camera;front=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale)
    offset=Vector((7,-8,10)).normalized()*20;cam.location=Vector((0,.40,0))+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.70;detail=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.ortho_scale);render_to(bpy.context.scene,ROOT/'hull-detail.png')
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
    report=dict(issue=1009,verifier_sha256=sha(Path(__file__)),blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],mesh_objects=len(meshes),reused_geometry_sha256=source_geometry,materials=materials,native=native,imported=exported,textures=textures,maximum_corner_normal_error=normal_error,checks=['Closed positive topology, bounds/transforms, packed image bytes and decoded texture pixels','Exact geometry preservation for 24 prior authored objects; box UVs, two inherited/four new physical dents, shared pod/body, 48 clamp and 16 cradle contacts, terminal fittings and inherited open ducts/nose cast roots','One alignment helper positions/axes under four rigid rotations; no animation timing claim'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_HEARTSBLOOD_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
