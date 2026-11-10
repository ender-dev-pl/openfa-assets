"""AC12 actual retained-cycle, native/import geometry/material and collision review."""
import bpy,bmesh,sys,json,math,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from verify_achaean_building_centered import setup
from checks_achaean_shipyard import material_contract
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'));from publication_support import clean_png
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
F=ROOT/'sources/objects/achaean/landing-pad';M=ROOT/'gallery/media/objects/achaean/landing-pad'


def snap():
    result={};deps=bpy.context.evaluated_depsgraph_get();root=bpy.data.objects['PlacementRoot']
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        p=o
        while p.parent:p=p.parent
        assert p==root;o2=o.evaluated_get(deps);mesh=o2.to_mesh();mesh.calc_loop_triangles();ps=[o2.matrix_world@v.co for v in mesh.vertices];faces=[tuple(f.vertices) for f in mesh.polygons];bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;bm.free();assert mesh.uv_layers.active
        result[o.name]=dict(points=ps,tree=BVHTree.FromPolygons(ps,faces),matrix=[float(v) for row in o2.matrix_world for v in row],triangles=len(mesh.loop_triangles),materials=sorted(m.name for m in o.data.materials));o2.to_mesh_clear()
    return result


def images():return sorted((tuple(i.size),sha_pixels(i)) for i in bpy.data.images if i.users and i.size[0] and i.source!='VIEWER')
def sha_pixels(i):return hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in i.pixels)).hexdigest()


def sample(meta):
    scene=bpy.context.scene;states={};names=sorted('AC12 cover segment '+str(sign)+' '+str(i) for sign in [-1,1] for i in range(6));collision_tests=0;maxradius=0;minz=10;maxz=-10
    for fr in range(1,62):
        scene.frame_set(fr);current=snap();states[fr]=current;assert sorted(n for n in current if n.startswith('AC12 cover segment '))==names
        fixed=[n for n in current if n not in names]
        for a,name in enumerate(names):
            leaf=current[name]
            for p in leaf['points']:maxradius=max(maxradius,math.hypot(p.x,p.y));minz=min(minz,p.z);maxz=max(maxz,p.z)
            for other in names[a+1:]+fixed:assert not leaf['tree'].overlap(current[other]['tree']),('Surface contact',fr,name,other);collision_tests+=1
    assert maxradius<1.185 and minz>.38 and maxz<.461
    for name in states[1]:assert states[1][name]['matrix']==states[61][name]['matrix']
    scene.frame_set(31)
    travel_error=0
    for name,old in meta['animation']['retained_open_translations'].items():
        actual=bpy.data.objects[name].matrix_world.translation
        travel_error=max(travel_error,max(abs(a-b) for a,b in zip(actual,[0,old[0],old[2]])))
    assert travel_error<1e-5
    root_matrix=[float(v) for row in bpy.data.objects['PlacementRoot'].matrix_world for v in row]
    assert max(abs(v-(1 if i%5==0 else 0)) for i,v in enumerate(root_matrix))<1e-5
    allp=[];faces=[];owners=[]
    for o in scene.objects:
        if o.type!='MESH':continue
        offset=len(allp);allp.extend(o.matrix_world@v.co for v in o.data.vertices)
        for f in o.data.polygons:faces.append(tuple(offset+i for i in f.vertices));owners.append(o.name)
    tree=BVHTree.FromPolygons(allp,faces);heights=[]
    for x,y in [(0,0)]+[(.60*math.cos(i*math.pi/4),.60*math.sin(i*math.pi/4)) for i in range(8)]:
        hit=tree.ray_cast(Vector((x,y,3)),Vector((0,0,-1)),4);assert hit[0] is not None and owners[hit[2]]=='AC12 dark continuous well floor';assert hit[0].z<.095;heights.append(hit[0].z)
    scene.frame_set(1)
    for x,expected in [(0,'Worn green cover'),(-.32,'Two red cover bands'),(.32,'Two red cover bands')]:
        candidates=[]
        for o in scene.objects:
            if o.type!='MESH':continue
            tr=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons]);hit=tr.ray_cast(Vector((x,.20,3)),Vector((0,0,-1)),4)
            if hit[0] is not None:candidates.append((hit[3],o.data.materials[o.data.polygons[hit[2]].material_index].name))
        assert min(candidates)[1]==expected,(x,candidates)
    return states,dict(frames=list(range(1,62)),surface_pair_checks=collision_tests,surface_intersections=0,maximum_moving_radius=maxradius,minimum_moving_z=minz,maximum_moving_z=maxz,open_floor_heights=heights,closed_cycle_equal=True,retained_travel_error=travel_error,root_matrix=root_matrix,coral_roughness_range=material_contract())


def render(label):
    s=setup();points=[]
    for fr in [1,31]:
        s.frame_set(fr);points.extend(o.matrix_world@Vector(v) for o in s.objects if o.type=='MESH' for v in o.bound_box)
    centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);out={}
    views=[('front-quarter',(5,-12,9),1),('front',(0,-16,10),1),('rear-quarter',(-7,12,9),1),('half-open-front-quarter',(5,-12,9),20),('open-front-quarter',(5,-12,9),31)]
    for name,d,fr in views:
        s.frame_set(fr);v=Vector(d).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;s.camera.location+=s.camera.matrix_world.to_3x3()@Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0));bpy.context.view_layer.update();p=M/f'{label}-{name}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));out[p.name]=sha(p)
    return out


def main():
    M.mkdir(parents=True,exist_ok=True);meta=json.loads((F/'model.json').read_bytes())
    for rel,h in {**meta['helpers'],meta['author']:meta['author_sha256']}.items():assert sha(ROOT/rel)==h
    for x,h in meta['binaries'].items():assert sha(F/f'model.{x}')==h
    bpy.ops.wm.open_mainfile(filepath=str(F/'model.blend'),load_ui=False,use_scripts=False);native,nmotion=sample(meta);ni=images();renders=render('native')
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30;bpy.ops.import_scene.gltf(filepath=str(F/'model.glb'));imported,imotion=sample(meta);ii=images();assert ni==ii;error=0;matrixerror=0
    for fr in native:
        assert native[fr].keys()==imported[fr].keys()
        for name,a in native[fr].items():
            b=imported[fr][name];assert a['triangles']==b['triangles'] and a['materials']==b['materials'];matrixerror=max(matrixerror,max(abs(x-y) for x,y in zip(a['matrix'],b['matrix'])));error=max(error,max(b['tree'].find_nearest(p)[3] for p in a['points']),max(a['tree'].find_nearest(p)[3] for p in b['points']))
    assert error<3e-5 and matrixerror<3e-5;renders.update(render('imported'));raw=(F/'model.glb').read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(doc['accessors'][p['indices']]['count']//3 for n in doc['nodes'] if 'mesh'in n for p in doc['meshes'][n['mesh']]['primitives']);assert tri==meta['triangles']==sum(v['triangles'] for v in native[1].values())<meta['triangle_budget'];assert len(doc['materials'])==meta['materials'];assert [a['name'] for a in doc['animations']]==['LaunchFacilityCycle'];assert len(doc['animations'][0]['channels'])==12
    animation=doc['animations'][0]
    assert {doc['nodes'][c['target']['node']]['name'] for c in animation['channels']}==set(meta['animation']['retained_open_translations'])
    assert all(c['target']['path']=='translation' for c in animation['channels'])
    assert all(s.get('interpolation','LINEAR')=='LINEAR' for s in animation['samplers'])
    inputs=[doc['accessors'][s['input']] for s in animation['samplers']]
    assert abs(min(a['min'][0] for a in inputs)-1/30)<1e-6 and abs(max(a['max'][0] for a in inputs)-61/30)<1e-6
    points=[p for n in native[1].values() for p in n['points']];bounds=[min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)];assert bounds[2]>=-1e-5;helpers={**meta['helpers'],meta['author']:meta['author_sha256'],Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)), 'sources/tools/blender/verify_achaean_building_centered.py':sha(Path(__file__).with_name('verify_achaean_building_centered.py')),'sources/tools/blender/checks_achaean_shipyard.py':sha(Path(__file__).with_name('checks_achaean_shipyard.py'))}
    report=dict(issue=256,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(F/'model.json'),verifier=Path(__file__).relative_to(ROOT).as_posix(),helpers=helpers,triangles=tri,meshes=len(native[1]),materials=len(doc['materials']),embedded_images=len(doc['images']),maximum_bidirectional_surface_error=error,maximum_animation_matrix_error=matrixerror,positive_closed_meshes=dict(native=len(native[1]),imported=len(imported[1])),native_world_bounds=bounds,native_root_matrix=nmotion['root_matrix'],texture_pixels_equal=True,native_motion=nmotion,imported_motion=imotion,clips=['LaunchFacilityCycle'],renders=renders,continuous_sweep_proven=False,descriptor17_composition_verified=False,final_artistic_acceptance=False,game_client_integration=False)
    (F/'runtime-review.json').write_text(json.dumps(report,indent=2)+chr(10),encoding='utf-8');print('AC12_RUNTIME_OK',tri,error,matrixerror,flush=True)
if __name__=='__main__':main()
