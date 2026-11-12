"""AC25 retained heading action and actual native/import checks across a sampled rotation."""
import bpy,json,sys,struct,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from remaster_achaean_stun_tower import ROOT,signature,sha
from verify_achaean_landing_pad import snap,images
from verify_achaean_building_centered import render
from checks_achaean_shipyard import material_contract
F=ROOT/'sources/objects/achaean/stun-tower';M=ROOT/'gallery/media/objects/achaean/stun-tower'

def sample(meta):
    scene=bpy.context.scene;frames=[1+i/4 for i in range(65)];states={};collisions=0;fork_rays=0;bearing_checks=0;nozzle_checks=0
    for frame in frames:
        scene.frame_set(int(frame),subframe=frame%1);s=snap();states[str(frame)]=s;head=bpy.data.objects['DirectionalHead'];base=bpy.data.objects['StaticBase'];root=bpy.data.objects['PlacementRoot']
        assert head.parent==base.parent==root and root['catalogue_id']==meta['id'] and list(root['footprint'])==[2,2]
        assert set(o.name for o in head.children)==set(meta['animation']['moving_meshes']) and set(o.name for o in base.children)==set(meta['animation']['static_meshes'])
        assert s['AC25 stationary rounded collar']['tree'].overlap(s['AC25 moving bearing spindle']['tree']);bearing_checks+=1
        for n in meta['animation']['moving_meshes']:
            if n=='AC25 moving bearing spindle':continue
            for f in meta['animation']['static_meshes']:
                assert not s[n]['tree'].overlap(s[f]['tree']),(frame,n,f);collisions+=1
        for n in meta['animation']['static_meshes']:
            assert s[n]['matrix']==states[str(frames[0])][n]['matrix'] and s[n]['points']==states[str(frames[0])][n]['points']
        p=[];faces=[];owners=[]
        for name in meta['animation']['moving_meshes']:
            o=bpy.data.objects[name];off=len(p);p.extend(o.matrix_world@v.co for v in o.data.vertices)
            for face in o.data.polygons:faces.append(tuple(off+i for i in face.vertices));owners.append(name)
        tree=BVHTree.FromPolygons(p,faces)
        nozzle=meta['nozzle'];axis=head.matrix_world.to_3x3()@Vector(nozzle['axis']);centre=head.matrix_world@(Vector(nozzle['centre'])-Vector(meta['animation']['retained_controller_signature']['location']))
        assert s['AC25 spherical directional head']['tree'].overlap(s['AC25 moving bearing spindle']['tree']);nozzle_checks+=1
        assert s['AC25 tapered raised nozzle']['tree'].overlap(s['AC25 spherical directional head']['tree']);nozzle_checks+=1
        assert s['AC25 recessed muzzle face']['tree'].overlap(s['AC25 tapered raised nozzle']['tree']);nozzle_checks+=1
        hit=tree.ray_cast(centre+axis*1.1,-axis,1)
        assert hit[0] is not None and owners[hit[2]]=='AC25 recessed muzzle face',(frame,'Blocked blind bore');assert abs((hit[0]-centre).dot(axis)-.637)<1e-4;nozzle_checks+=1
        side=head.matrix_world.to_3x3()@Vector((.04,0,0));hit=tree.ray_cast(centre+side+axis*1.1,-axis,1)
        assert hit[0] is not None and owners[hit[2]]=='AC25 tapered raised nozzle' and (hit[0]-centre).dot(axis)>.72;nozzle_checks+=1
    scene.frame_set(1);s=snap()
    for name in ['AC25 grounded flared casing','AC25 grounded buttress -1','AC25 grounded buttress 1']:
        assert abs(min(p.z for p in s[name]['points']))<1e-5
    for name in ['AC25 grounded buttress -1','AC25 grounded buttress 1','AC25 red narrow neck','AC25 left slate service fitting']:
        assert s[name]['tree'].overlap(s['AC25 grounded flared casing']['tree']),name
    for a,b in [('AC25 stationary rounded collar','AC25 red narrow neck'),('AC25 left ochre coupling','AC25 left slate service fitting')]:assert s[a]['tree'].overlap(s[b]['tree']),(a,b)
    assert min(p.z for p in s['AC25 red narrow neck']['points'])>.9
    for i in range(6):
        name='AC25 blue status field '+str(i);o=bpy.data.objects[name];normal=o.matrix_world.to_3x3()@Vector((0,-1,0));allvs=[];allfaces=[];owners=[]
        for n in s:
            off=len(allvs);allvs.extend(s[n]['points'])
            for f in bpy.data.objects[n].data.polygons:allfaces.append(tuple(off+j for j in f.vertices));owners.append(n)
        hit=BVHTree.FromPolygons(allvs,allfaces).ray_cast(o.matrix_world.translation+normal,-normal,2);assert hit[0] is not None and owners[hit[2]]==name,(name,'Source field occluded')
    for axis in [Vector((1,0,0)),Vector((-1,0,0)),Vector((0,1,0)),Vector((0,-1,0))]:
        hit=s['AC25 spherical directional head']['tree'].ray_cast(Vector((0,0,1.78))+axis,-axis,2);assert hit[0] is not None and abs((hit[0]-Vector((0,0,1.78))).length-.34)<.003
    moved=meta['animation']['moving_meshes'];assert all(states['1.0'][n]['matrix']!=states['5.0'][n]['matrix'] for n in moved)
    cycle=max(abs(a-b) for n in moved for a,b in zip(states['1.0'][n]['matrix'],states['17.0'][n]['matrix']));assert cycle<1e-5
    assert nozzle_checks==325
    return states,dict(sample_frames=frames,stationary_meshes_constant=True,closed_cycle_matrix_error=cycle,bearing_contact_checks=bearing_checks,nonbearing_surface_pair_checks=collisions,nonbearing_surface_intersections=0,nozzle_support_bore_lip_checks=nozzle_checks,source_status_visibility_rays=6,grounded_body_and_buttresses=True,neck_collar_service_contacts=True,spherical_head_radial_checks=4,coral_roughness_range=material_contract())


def main():
    meta=json.loads((F/'model.json').read_bytes());source=ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac25/model.blend'
    for ext,h in meta['binaries'].items():assert sha(F/f'model.{ext}')==h
    for rel,h in meta['helpers'].items():assert sha(ROOT/rel)==h
    assert sha(ROOT/meta['author'])==meta['author_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);original=signature()
    bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'),load_ui=False,use_scripts=False);assert signature()==original==meta['animation']['retained_controller_signature'];native,nmotion=sample(meta);ni=images();M.mkdir(parents=True,exist_ok=True);renders=render('native',M)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=16;bpy.ops.import_scene.gltf(filepath=str(F/'model.glb'));imported,imotion=sample(meta);assert ni==images();error=0;matrixerror=0
    for fr,s in native.items():
        assert s.keys()==imported[fr].keys()
        for n,a in s.items():
            b=imported[fr][n];assert a['triangles']==b['triangles'] and a['materials']==b['materials'];error=max(error,max(b['tree'].find_nearest(p)[3] for p in a['points']),max(a['tree'].find_nearest(p)[3] for p in b['points']));matrixerror=max(matrixerror,max(abs(v-w) for v,w in zip(a['matrix'],b['matrix'])))
    print('AC25_PARITY_ERRORS',error,matrixerror,flush=True)
    assert error<1e-5 and matrixerror<1e-5;renders.update(render('imported',M));raw=(F/'model.glb').read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
    tri=sum(doc['accessors'][p['indices']]['count']//3 for n in doc['nodes'] if 'mesh'in n for p in doc['meshes'][n['mesh']]['primitives']);assert tri==meta['triangles']<30000 and len(doc['materials'])==meta['materials']
    a,=doc['animations'];assert a['name']=='Animation';assert all(doc['nodes'][c['target']['node']]['name']=='DirectionalHead' and c['target']['path']=='rotation' for c in a['channels']);assert all(s.get('interpolation','LINEAR')=='LINEAR' for s in a['samplers'])
    input_bounds=[doc['accessors'][s['input']] for s in a['samplers']];assert abs(min(a['min'][0] for a in input_bounds)-1/16)<1e-6 and abs(max(a['max'][0] for a in input_bounds)-17/16)<1e-6
    points=[p for s in native.values() for n in s.values() for p in n['points']];bounds=[min(p[i] for p in points) for i in range(3)]+[max(p[i] for p in points) for i in range(3)];assert bounds[2]>=-1e-5
    helpers={**meta['helpers'],meta['author']:sha(ROOT/meta['author'])}
    for name in ['verify_achaean_stun_tower.py','remaster_achaean_stun_tower.py','verify_achaean_landing_pad.py','verify_achaean_building_left_quarter.py','verify_achaean_building_centered.py','checks_achaean_shipyard.py']:helpers['sources/tools/blender/'+name]=sha(Path(__file__).with_name(name))
    root=bpy.data.objects['PlacementRoot'];report=dict(issue=256,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(F/'model.json'),verifier=Path(__file__).relative_to(ROOT).as_posix(),helpers=helpers,triangles=tri,meshes=len(native['1.0']),materials=len(doc['materials']),embedded_images=len(doc['images']),maximum_bidirectional_surface_error=error,maximum_animation_matrix_error=matrixerror,positive_closed_meshes=dict(native=len(native['1.0']),imported=len(imported['1.0'])),native_world_bounds=bounds,native_root_matrix=[float(v) for row in root.matrix_world for v in row],texture_pixels_equal=True,native_motion=nmotion,imported_motion=imotion,retained_controller_signature=original,clips=['Animation'],renders=renders,continuous_sweep_proven=False,game_client_integration=False,final_artistic_acceptance=False)
    (F/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('AC25_RUNTIME_OK',tri,error,matrixerror,flush=True)
if __name__=='__main__':main()


