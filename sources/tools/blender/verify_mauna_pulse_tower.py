"""Verify actual native and independent GLB MN13 geometry and retained heading motion."""
import hashlib,json,math,struct,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_png

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def signature(head):
    a=head.animation_data.action;curves=[]
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for c in bag.fcurves:curves.append(dict(path=c.data_path,index=c.array_index,keys=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right)) for k in c.keyframe_points]))
    return dict(location=list(head.location),rotation_mode=head.rotation_mode,action=a.name,curves=curves)

def snapshot():
    result={};deps=bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();points=[obj.matrix_world@v.co for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons]
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.free()
        assert mesh.uv_layers.active and all(math.isfinite(v) for p in points for v in p)
        assert all(math.isfinite(v) for uv in mesh.uv_layers.active.data for v in uv.uv)
        result[obj.name]=dict(points=points,tree=BVHTree.FromPolygons(points,faces),triangles=len(mesh.loop_triangles),matrix=[float(v) for row in obj.matrix_world for v in row],materials=sorted(m.name for m in obj.data.materials if m));evaluated.to_mesh_clear()
    return result

def images():
    reachable={node.image for obj in bpy.context.scene.objects if obj.type=='MESH' for mat in obj.data.materials if mat and mat.use_nodes for node in mat.node_tree.nodes if node.type=='TEX_IMAGE' and node.image}
    return sorted((tuple(i.size),hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in i.pixels)).hexdigest()) for i in reachable)

def sample(meta):
    assert meta['definition_class']==17 and meta['construction_updates']==32
    states={};checks=0;collision_checks=0;aperture_checks=0;fork_checks=0
    def inside(t,p):
        q,n,_,_=t.find_nearest(p);return q is not None and n.dot(p-q)<-1e-5
    frames=[1+i/4 for i in range(65)];pivot=meta['animation']['retained_controller_signature']['location'][2]
    for frame in frames:
        bpy.context.scene.frame_set(int(frame),subframe=frame%1);bpy.context.view_layer.update();s=snapshot();states[str(frame)]=s
        head=bpy.data.objects['DirectionalHead'];base=bpy.data.objects['StaticBase'];root=bpy.data.objects['PlacementRoot']
        assert head.parent==base.parent==root and root['catalogue_id']==meta['id'] and list(root['footprint'])==[2,2]
        assert len(s)==meta['mesh_nodes']==16 and set(o.name for o in head.children)==set(meta['animation']['moving_meshes']) and set(o.name for o in base.children)==set(meta['animation']['static_meshes'])
        for name in meta['animation']['static_meshes']:
            assert s[name]['matrix']==states[str(frames[0])][name]['matrix'] and s[name]['points']==states[str(frames[0])][name]['points']
        for a in meta['animation']['moving_meshes']:
            for b in meta['animation']['static_meshes']:
                if a=='Pulse Tower moving bearing' and b=='Pulse Tower fixed supported bearing':continue
                assert not s[a]['tree'].overlap(s[b]['tree']),(frame,'Moving/fixed interference',a,b);collision_checks+=1
        for c in meta['attachment_contacts']:
            q=Vector(c['point'])
            if c['object'] in meta['animation']['moving_meshes']:q=head.matrix_world@Vector((q.x,q.y,q.z-pivot))
            assert inside(s[c['object']]['tree'],q) and inside(s[c['support']]['tree'],q),(frame,'Unsupported joint',c);checks+=1
        # Test actual moving surfaces in local-head coordinates. A black decal
        # cannot pass the triangular opening or open fork-gap ray guards.
        rot=head.matrix_world.to_3x3()
        def world(p):return head.matrix_world@Vector((p[0],p[1],p[2]-pivot))
        yoke=s['Pulse Tower pierced rotating support']['tree']
        assert yoke.ray_cast(world((-.5,.03,1.36)),rot@Vector((1,0,0)),1)[0] is None,'Real triangular aperture'
        assert yoke.ray_cast(world((-.5,.03,1.15)),rot@Vector((1,0,0)),1)[0] is not None,'Solid support below aperture';aperture_checks+=2
        points=[];faces=[];owners=[]
        for name in meta['animation']['moving_meshes']:
            obj=bpy.data.objects[name];offset=len(points);points.extend(obj.matrix_world@v.co for v in obj.data.vertices)
            for f in obj.data.polygons:faces.append(tuple(offset+i for i in f.vertices));owners.append(name)
        moving=BVHTree.FromPolygons(points,faces)
        assert moving.ray_cast(world((0,-.70,3)),rot@Vector((0,0,-1)),1.4)[0] is None,'Actual clear gap between prongs';fork_checks+=1
        for i,x in enumerate([-.14,.14]):
            hit=moving.ray_cast(world((x,-.70,3)),rot@Vector((0,0,-1)),1.4);assert hit[0] is not None and owners[hit[2]]=='Pulse Tower parallel rectangular prong '+str(i),'Two distinct source rails';fork_checks+=1
    bpy.context.scene.frame_set(1);s=states[str(frames[0])]
    assert len(meta['attachment_contacts'])==14 and len(meta['rectangular_recesses'])==1
    for f in meta['rectangular_recesses']:
        q=Vector(f['point']);n=Vector(f['normal']);hit=s[f['body']]['tree'].ray_cast(q+n*.1,-n)[0];assert hit is not None and abs((q-hit).dot(n)-f['depth'])<1e-5,'Actual blind source service slot';q-=n*f['contact_depth'];assert inside(s[f['object']]['tree'],q) and inside(s[f['body']]['tree'],q),'Seated slot backing'
    for i,y in enumerate([-.20,.20]):
        assert inside(s['Pulse Tower brass side reservoir '+str(i)]['tree'],Vector((-.68,y,.39)))
        assert abs(max(p.z for p in s['Pulse Tower dark reservoir cap '+str(i)]['points'])-.68)<1e-5
    for chip in meta['physical_chips']:
        q=Vector(chip['point']);n=Vector(chip['normal']);hit=s[chip['body']]['tree'].ray_cast(q+n*.1,-n)[0];assert hit is not None and .003<(q-hit).dot(n)<.012,'Actual shallow cast chip'
    body=s['Pulse Tower inclined fixed cast body']['tree']
    for z in [.5,.8]:
        hit=body.ray_cast(Vector((.50,-3,z)),Vector((0,1,0)))[0];assert hit is not None and abs(hit.y-(-.75+.55*(z-.30)/.66))<1e-5,'Continuous sloping front'
    assert abs(min(p.z for item in s.values() for p in item['points']))<1e-5
    assert all(states['1.0'][name]['matrix']!=states['5.0'][name]['matrix'] for name in meta['animation']['moving_meshes'])
    cycle=max(abs(a-b) for name in s for a,b in zip(states['1.0'][name]['matrix'],states['17.0'][name]['matrix']));assert cycle<1e-5
    return states,dict(sample_frames=frames,attachment_checks=checks,nonbearing_collision_checks=collision_checks,nonbearing_intersections=0,triangular_aperture_rays=aperture_checks,paired_prong_and_gap_rays=fork_checks,source_reservoirs=2,source_opaque_front_points=2,physical_chips=2,stationary_base_constant=True,closed_cycle_matrix_error=cycle,continuous_sweep_proven=False)

def setup():
    for obj in list(bpy.context.scene.objects):
        if obj.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.film_transparent=True;s.world=bpy.data.worlds.new('Review studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO'
    for loc,power,size in [((4,-6,8),950,5),((-4,-2,5),700,4),((2,5,7),1100,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.3))-o.location).to_track_quat('-Z','Y').to_euler()
    return s

def render(label,media):
    bpy.context.scene.frame_set(5);bpy.context.view_layer.update()
    s=setup();meshes=[o for o in s.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box ];centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);renders={}
    for view,direction in [('front-quarter',(-10,-10,7)),('front',(0,-16,9)),('rear-quarter',(7,12,9))]:
        v=Vector(direction).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];midpoint=Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0));s.camera.location+=s.camera.rotation_euler.to_matrix()@midpoint;s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;p=media/f'{label}-{view}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));renders[p.name]=sha(p)
    return renders

def main():
    folder=ROOT/'sources/objects/mauna/pulse-tower';media=ROOT/'gallery/media/objects/mauna/pulse-tower';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_bytes())
    for ext,digest in meta['binaries'].items():assert sha(folder/('model.'+ext))==digest
    assert sha(ROOT/meta['author'])==meta['author_sha256']
    assert sha(ROOT/meta['source_controller'])==meta['source_controller_sha256']
    assert json.loads((ROOT/meta['concept_review']).read_bytes())['id']==meta['id']
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/meta['source_controller']),load_ui=False,use_scripts=False);original=signature(bpy.data.objects['DirectionalHead'])
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False);assert signature(bpy.data.objects['DirectionalHead'])==original==meta['animation']['retained_controller_signature'];native,nmotion=sample(meta);ni=images();renders=render('native',media)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=16;bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'));imported,imotion=sample(meta);ii=images();assert ni==ii
    error=0;matrix_error=0
    for frame,objects in native.items():
        assert objects.keys()==imported[frame].keys()
        for name,a in objects.items():
            b=imported[frame][name];assert a['triangles']==b['triangles'] and a['materials']==b['materials'];error=max(error,max(b['tree'].find_nearest(p)[3] for p in a['points']),max(a['tree'].find_nearest(p)[3] for p in b['points']));matrix_error=max(matrix_error,max(abs(v-w) for v,w in zip(a['matrix'],b['matrix'])))
    print('MN15_PARITY_ERRORS',error,matrix_error,flush=True);assert error<1e-5 and matrix_error<1e-5
    raw=(folder/'model.glb').read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(doc['accessors'][p['indices']]['count']//3 for mesh in doc['meshes'] for p in mesh['primitives']);assert tri==meta['triangles']<30000;assert len(doc['materials'])==meta['materials']==5 and len(doc['images'])==7;assert all('bufferView' in image for image in doc['images'])
    clip,=doc['animations'];assert clip['name']=='Animation'
    assert all(doc['nodes'][c['target']['node']]['name']=='DirectionalHead' and c['target']['path']=='rotation' for c in clip['channels'])
    bounds=[doc['accessors'][s['input']] for s in clip['samplers']];assert abs(min(a['min'][0] for a in bounds)-1/16)<1e-6 and abs(max(a['max'][0] for a in bounds)-17/16)<1e-6
    renders.update(render('imported',media));s=bpy.context.scene
    for name,target,scale in [('fork-head-and-triangular-support-detail',Vector((0,-.15,1.65)),2.2),('two-reservoirs-and-front-fittings-detail',Vector((-.15,-.05,.48)),2.5)]:
        direction=Vector((-8,-10,9)).normalized();s.camera.location=target+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(name+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    wire=bpy.data.materials.new('Technical edges of canonical geometry');wire.use_nodes=True;node=wire.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.04,.3,.07,1);node.inputs['Emission Color'].default_value=(.04,.3,.07,1);node.inputs['Emission Strength'].default_value=.4
    curve=bpy.data.curves.new('Canonical mesh edge coordinates','CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=.0014;curve.bevel_resolution=0
    for obj in list(s.objects):
        if obj.type!='MESH':continue
        for edge in obj.data.edges:
            line=curve.splines.new('POLY');line.points.add(1)
            for point,index in zip(line.points,edge.vertices):point.co=(*(obj.matrix_world@obj.data.vertices[index].co),1)
        obj.hide_render=True
    obj=bpy.data.objects.new('Exact canonical technical edges',curve);s.collection.objects.link(obj);curve.materials.append(wire);target=Vector((0,-.16,1.1));direction=Vector((-8,-10,9)).normalized();s.camera.location=target+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=3.3;path=media/'technical-wireframe.png';s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    points=[p for frame in native.values() for obj in frame.values() for p in obj['points']];bounds=[min(p[i] for p in points) for i in range(3)]+[max(p[i] for p in points) for i in range(3)];root=bpy.data.objects['PlacementRoot']
    report=dict(issue=261,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native['1.0']),materials=len(doc['materials']),embedded_images=len(doc['images']),maximum_bidirectional_surface_error=error,maximum_animation_matrix_error=matrix_error,positive_closed_meshes=dict(native=len(native['1.0']),imported=len(imported['1.0'])),native_world_bounds=bounds,native_root_matrix=[float(v) for row in root.matrix_world for v in row],texture_pixels_equal=True,clips=['Animation'],native_motion=nmotion,imported_motion=imotion,retained_controller_signature=original,renders=renders,scope='Actual saved native and independent GLB across65heading samples, positive closed surfaces, grounded fixed base, eight blind vent cells, supported rotating head/single barrel/bore, texture pixels and renders. Continuous sweep and client heading/scale/FPS are not certified.',game_client_integration=False,final_artistic_acceptance=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('MN15_RUNTIME_OK',tri,len(native['1.0']),error,matrix_error,flush=True)

if __name__=='__main__':main()
