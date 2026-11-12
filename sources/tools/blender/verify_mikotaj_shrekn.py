"""Verify saved MK17 and independent GLB import, including real review renders."""
import hashlib,json,math,struct,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_png

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
    result={};deps=bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();points=[obj.matrix_world@v.co for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons]
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.free()
        assert obj.data.uv_layers.active and all(math.isfinite(v) for p in points for v in p)
        result[obj.name]=dict(points=points,tree=BVHTree.FromPolygons(points,faces),triangles=len(mesh.loop_triangles),matrix=[float(v) for row in obj.matrix_world for v in row],materials=sorted(m.name for m in obj.data.materials if m));evaluated.to_mesh_clear()
    required=['Shrekn hollow mineral casing and side chambers','Shrekn opaque deep shaft floor','Shrekn one-piece silver mushroom dome','Shrekn attached rigid spiral groove','Shrekn Blue state lens','Shrekn Red state lens']
    assert all(name in result for name in required) and len(result)==16
    body=result[required[0]]['points'];width=max(p.x for p in body)-min(p.x for p in body);assert 1.50<width<1.85 and 1.84<max(p.z for p in body)<1.89,'Source short mineral neck and broad side chambers'
    assert 1.0<max(p.z for p in body)/width<1.30
    for index,x in enumerate([-.4,.4]):
        distance=result[required[0]]['tree'].find_nearest(Vector((x,.08,1.75)))[3];assert distance<.05,'Guide support physically seated on upper casing'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/102';assert list(root['footprint'])==[2,2]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        ancestor=obj.parent
        while ancestor and ancestor!=root:ancestor=ancestor.parent
        assert ancestor==root,'Every mesh must remain below canonical placement root'
    images={i.name:dict(size=list(i.size),pixels=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in i.pixels)).hexdigest()) for i in bpy.data.images if i.users and i.size[0] and i.source!='VIEWER'}
    return result,images,[float(v) for row in root.matrix_world for v in row]

def setup():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.film_transparent=True;s.world=bpy.data.worlds.new('Review studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO'
    for loc,power,size in [((4,-6,8),950,5),((-4,-2,5),700,4),((2,5,7),1100,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.7))-o.location).to_track_quat('-Z','Y').to_euler()
    return s

def render(label,media):
    s=setup();meshes=[o for o in s.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box];centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);renders={}
    for view,direction in [('front-quarter',(5,-12,6)),('front',(0,-16,3)),('rear-quarter',(-7,12,6))]:
        v=Vector(direction).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];mid=Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0));s.camera.location+=s.camera.rotation_euler.to_matrix()@mid;s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;p=media/f'{label}-{view}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));renders[p.name]=sha(p)
    return renders

def motion_states():
    states={}
    for frame in [1,8,16,24,31,46,61]:
        bpy.context.scene.frame_set(frame);states[frame]=snapshot()[0]
    cap='Shrekn one-piece silver mushroom dome';groove='Shrekn attached rigid spiral groove'
    for frame,state in states.items():
        fraction=(frame-1)/30 if frame<=31 else (61-frame)/30;translation=Vector((0,1.15*fraction,0))
        for name in [cap,groove]+['Shrekn cap bearing '+str(i) for i in range(2)]:
            assert len(states[1][name]['points'])==len(state[name]['points'])
            assert max((a+translation-b).length for a,b in zip(states[1][name]['points'],state[name]['points']))<1e-5,'Whole cap/relief/carriage must translate as ONE rigid unit'
        for index in range(2):
            name='Shrekn sliding guide rod '+str(index);assert max((a+Vector((0,.90*fraction,0))-b).length for a,b in zip(states[1][name]['points'],state[name]['points']))<1e-5
            points=state[name]['points'];lo=min(p.y for p in points);hi=max(p.y for p in points);bearing=state['Shrekn cap bearing '+str(index)]['points'];centre=sum(bearing,Vector())/len(bearing)
            assert lo+.04<centre.y<hi-.04 and min(hi,.60)-max(lo,.05)>.04,'Telescopic overlap and bearing remain supported throughout motion'
        blue=max(p.z for p in state['Shrekn Blue state lens']['points']);red=max(p.z for p in state['Shrekn Red state lens']['points']);assert (blue>.5)!=(red>.5),'Exactly one colour of the same status port visible'
    assert max(p.z for p in states[1]['Shrekn Blue state lens']['points'])>.5 and max(p.z for p in states[31]['Shrekn Red state lens']['points'])>.5
    # Direct actual-mesh containment: bearing contacts underside of the rigid
    # cap instead of leaving a levitating cap above the authored guides.
    for index,x in enumerate([-.4,.4]):
        point=Vector((x,-.05,1.905))
        for name in [cap,'Shrekn cap bearing '+str(index)]:
            co,normal,_,_=states[1][name]['tree'].ray_cast(point,Vector((0,0,1)));assert co and normal.z>0,'Cap must contact carriage bearing'
    for i in range(9):
        angle=i*math.tau/8;x=.23*math.cos(angle) if i<8 else 0;y=.23*math.sin(angle) if i<8 else 0
        closed=states[1][cap]['tree'].ray_cast(Vector((x,y,3)),Vector((0,0,-1)))[0];assert closed and closed.z>1.89,'Closed cap covers full aperture'
        for name,state in states[31].items():
            hit=state['tree'].ray_cast(Vector((x,y,3)),Vector((0,0,-1)))[0];assert hit is None or hit.z<.14,('Open launch aperture obstruction',name,x,y)
    # Envelope test at every actual frame,not just the seven comparison poses.
    for frame in range(1,62):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        for index in range(2):
            rod=bpy.data.objects['Shrekn sliding guide rod '+str(index)];sleeve=bpy.data.objects['Shrekn fixed telescopic sleeve '+str(index)];bearing=bpy.data.objects['Shrekn cap bearing '+str(index)]
            rp=[rod.matrix_world@Vector(p) for p in rod.bound_box];sp=[sleeve.matrix_world@Vector(p) for p in sleeve.bound_box];lo=min(p.y for p in rp);hi=max(p.y for p in rp);sl=min(p.y for p in sp);sh=max(p.y for p in sp);y=bearing.matrix_world.translation.y;assert lo+.04<y<hi-.04 and min(hi,sh)-max(lo,sl)>.04,'Actual evaluated support failed at frame '+str(frame)
    bpy.context.scene.frame_set(1);return states

def render_state(label,media,renders):
    scene=bpy.context.scene;direction=Vector((5,-12,6)).normalized();centre=Vector((0,.40,1.08));scene.camera.location=centre+direction*15;scene.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=3.6
    path=media/('state-'+label+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)

def main():
    folder=ROOT/'sources/objects/mikotaj/shrekn';media=ROOT/'gallery/media/objects/mikotaj/shrekn';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_mikotaj_shrekn.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_mikotaj_shrekn.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/mk17-concept-review.json'
    assert json.loads((ROOT/meta['concept_review']).read_bytes())['id']==meta['id']
    for ext,h in meta['binaries'].items():assert sha(folder/f'model.{ext}')==h
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False);bpy.context.scene.frame_set(1);native,ni,nr=snapshot();native_states=motion_states();renders=render('native',media)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'),disable_bone_shape=True);bpy.context.scene.frame_set(1);imported,ii,ir=snapshot();imported_states=motion_states();assert native.keys()==imported.keys();assert nr==ir
    # Importer may rename embedded images. Compare exact decoded pixels/sizes,
    # not Blender datablock labels or filesystem paths.
    assert sorted((v['size'],v['pixels']) for v in ni.values())==sorted((v['size'],v['pixels']) for v in ii.values())
    error=0
    for name,n in native.items():
        other=imported[name];assert n['triangles']==other['triangles'];assert n['materials']==other['materials'];assert max(abs(a-b) for a,b in zip(n['matrix'],other['matrix']))<1e-5
        error=max(error,max(other['tree'].find_nearest(p)[3] for p in n['points']),max(n['tree'].find_nearest(p)[3] for p in other['points']))
    assert error<1e-5;raw=(folder/'model.glb').read_bytes();gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values());assert tri<30000;assert [a['name'] for a in gltf['animations']]==['LaunchFacilityCycle'];assert len(gltf.get('skins',[]))==0;assert len(gltf['materials'])==6;assert all('bufferView' in i for i in gltf['images']);renders.update(render('imported',media))
    animation_checks=[]
    for frame,native_state in native_states.items():
        actual=imported_states[frame];assert native_state.keys()==actual.keys()
        state_error=max(max(actual[name]['tree'].find_nearest(p)[3] for p in n['points']) for name,n in native_state.items());assert state_error<1e-5,(frame,state_error);animation_checks.append(dict(frame=frame,surface_error=state_error))
    for frame,label in [(1,'closed'),(16,'half-open'),(31,'open')]:
        bpy.context.scene.frame_set(frame);render_state(label,media,renders)
    bpy.context.scene.frame_set(1)
    scene=bpy.context.scene
    for frame,label,centre,direction,scale in [(1,'silver-cap-detail',Vector((0,0,1.96)),Vector((4,-10,8)),1.55),(31,'rear-guides-detail',Vector((0,.65,1.75)),Vector((5,9,7)),2.25)]:
        scene.frame_set(frame);direction.normalize();scene.camera.location=centre+direction*15;scene.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=scale;path=media/(label+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    bpy.context.scene.frame_set(1)
    s=bpy.context.scene
    wire=bpy.data.materials.new('Technical diagram from canonical geometry');wire.use_nodes=True
    node=wire.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.04,.3,.07,1)
    node.inputs['Emission Color'].default_value=(.04,.3,.07,1);node.inputs['Emission Strength'].default_value=.4
    # Render the actual canonical edge coordinates as thin curves. Wireframe
    # face offset on very slender Boolean triangles can create miter spikes.
    points=[obj.matrix_world@Vector(v) for obj in s.objects if obj.type=='MESH' for v in obj.bound_box]
    centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)])
    curve=bpy.data.curves.new('Exact canonical edge coordinates','CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=.0014;curve.bevel_resolution=0
    for obj in list(s.objects):
        if obj.type!='MESH':continue
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        for edge in mesh.edges:
            line=curve.splines.new('POLY');line.points.add(1)
            for point,index in zip(line.points,edge.vertices):point.co=(*(evaluated.matrix_world@mesh.vertices[index].co),1)
        evaluated.to_mesh_clear();obj.hide_render=True
    edge_object=bpy.data.objects.new('Technical edges from actual canonical mesh',curve);s.collection.objects.link(edge_object);curve.materials.append(wire)
    direction=Vector((5,-12,6)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    s.camera.data.ortho_scale=3.1;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=259,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=['LaunchFacilityCycle'],animation_checks=animation_checks,renders=renders,scope='Saved native and independent GLB runtime geometry, roots, texture pixels and actual renders. Pixel review is a separate step. No client scale/state mapping, FPS certification or final user artistic acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('MK17_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
