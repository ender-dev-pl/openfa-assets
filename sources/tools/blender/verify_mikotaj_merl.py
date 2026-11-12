"""Verify saved MK20 and independent GLB import, including real review renders."""
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
    required=['Merl broad asymmetric mineral mound','Merl compact forked mineral head','Merl worn pale lens bezel','Merl dark lens seat','Merl pale blue front lens','Merl source gold discharge'];assert all(name in result for name in required) and len(result)==6
    body=result[required[0]];points=body['points'];width=max(p.x for p in points)-min(p.x for p in points);height=max(p.z for p in points)-min(p.z for p in points);assert 1.55<width<1.90 and .58<height<.82,'Low broad ore mound'
    head=result[required[1]];points=head['points'];assert 1.37<max(p.z for p in points)<1.45 and .30<max(p.x for p in points)-min(p.x for p in points)<.42,'Short narrow forked head'
    tree=head['tree'];middle=tree.ray_cast(Vector((0,.07,2)),Vector((0,0,-1)))[0];left=tree.ray_cast(Vector((-.13,.07,2)),Vector((0,0,-1)))[0];right=tree.ray_cast(Vector((.12,.07,2)),Vector((0,0,-1)))[0];assert middle and left and right and min(left.z,right.z)-middle.z>.13 and left.z>right.z+.02,'Real open U-shaped unequal prongs'
    for sample in [Vector((x,.07,.55)) for x in [-.06,0,.06]]:
        for structure in [body,head]:
            surface,normal,_,distance=structure['tree'].find_nearest(sample);assert surface and normal.dot(sample-surface)<-1e-4,'Head and mound share actual interior volume'
    for name in required[2:5]:
        pts=result[name]['points'];centre=sum(pts,Vector())/len(pts);assert abs(centre.x)<.01 and .91<centre.z<.97 and head['tree'].find_nearest(centre)[3]<.09,'Small source front lens seated on head'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/105';assert list(root['footprint'])==[2,2]
    assert all(o.parent==root for o in bpy.context.scene.objects if o.type=='MESH')
    images={i.name:dict(size=list(i.size),pixels=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in i.pixels)).hexdigest()) for i in bpy.data.images if i.users and i.size[0] and i.source!='VIEWER'}
    return result,images,[float(v) for row in root.matrix_world for v in row]

def setup():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.film_transparent=True;s.world=bpy.data.worlds.new('Review studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO'
    for loc,power,size in [((4,-6,8),950,5),((-4,-2,5),700,4),((2,5,7),1100,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.7))-o.location).to_track_quat('-Z','Y').to_euler()
    # Preview bloom illustrates actual portable GLB emission;client bloom is separate.
    s.use_nodes=True;nodes=s.node_tree.nodes;nodes.clear();layers=nodes.new('CompositorNodeRLayers');glow=nodes.new('CompositorNodeGlare');glow.glare_type='FOG_GLOW';glow.quality='HIGH';glow.threshold=1.2;glow.size=7;output=nodes.new('CompositorNodeComposite');s.node_tree.links.new(layers.outputs['Image'],glow.inputs['Image']);s.node_tree.links.new(glow.outputs['Image'],output.inputs['Image'])
    return s

def render(label,media):
    s=setup();meshes=[o for o in s.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box];centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);renders={}
    for view,direction in [('front-quarter',(5,-12,6)),('front',(0,-16,3)),('rear-quarter',(-7,12,6))]:
        v=Vector(direction).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];midpoint=Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0));s.camera.location+=s.camera.rotation_euler.to_matrix()@midpoint;s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;p=media/f'{label}-{view}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));renders[p.name]=sha(p)
    return renders

def motion_states():
    states={}
    for frame in [1,5,9,13,17,21,27,33]:
        bpy.context.scene.frame_set(frame);states[frame]=snapshot()[0]
    initial=states[1];final=states[33];name='Merl source gold discharge';assert max(p.z for p in initial[name]['points'])<.11 and max(p.z for p in final[name]['points'])<.11,'Pulse returns hidden inside mound'
    bright=states[13][name]['points'];assert max(p.z for p in bright)>1.60 and min(p.z for p in bright)<1.38,'Gold source pulse reaches above fork'
    for frame,state in states.items():
        for key in initial:
            if key!=name:assert max((a-b).length for a,b in zip(initial[key]['points'],state[key]['points']))<1e-7,'Only energetic pulse changes;head/body/lens stay fixed'
    bpy.context.scene.frame_set(1);return states

def main():
    folder=ROOT/'sources/objects/mikotaj/merl';media=ROOT/'gallery/media/objects/mikotaj/merl';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_mikotaj_merl.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_mikotaj_merl.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/mk20-concept-review.json'
    assert json.loads((ROOT/meta['concept_review']).read_bytes())['id']==meta['id']
    for ext,h in meta['binaries'].items():assert sha(folder/f'model.{ext}')==h
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False);bpy.context.scene.frame_set(1);native,ni,nr=snapshot();native_states=motion_states();renders=render('native',media)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'));bpy.context.scene.frame_set(1);imported,ii,ir=snapshot();imported_states=motion_states();assert native.keys()==imported.keys();assert nr==ir
    # Importer may rename embedded images. Compare exact decoded pixels/sizes,
    # not Blender datablock labels or filesystem paths.
    assert sorted((v['size'],v['pixels']) for v in ni.values())==sorted((v['size'],v['pixels']) for v in ii.values())
    error=0
    for name,n in native.items():
        other=imported[name];assert n['triangles']==other['triangles'];assert n['materials']==other['materials'];assert max(abs(a-b) for a,b in zip(n['matrix'],other['matrix']))<1e-5
        error=max(error,max(other['tree'].find_nearest(p)[3] for p in n['points']),max(n['tree'].find_nearest(p)[3] for p in other['points']))
    assert error<1e-5;raw=(folder/'model.glb').read_bytes();gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values());assert tri<30000;assert [a['name'] for a in gltf.get('animations',[])]==['PlasmaDischarge'];assert not gltf.get('skins');assert len(gltf['materials'])==5;assert all('bufferView' in i for i in gltf['images']);renders.update(render('imported',media))
    animation_checks=[]
    for frame,native_state in native_states.items():
        actual=imported_states[frame];assert native_state.keys()==actual.keys()
        state_error=max(max(actual[name]['tree'].find_nearest(p)[3] for p in n['points']) for name,n in native_state.items());assert state_error<1e-5,(frame,state_error);animation_checks.append(dict(frame=frame,surface_error=state_error))
    s=bpy.context.scene
    for label,centre,scale,frame in [('fork-and-lens-detail',Vector((0,0,1.05)),.95,1),('mineral-mound-detail',Vector((0,0,.26)),1.95,1),('pulse-peak',Vector((0,0,.83)),2.2,13)]:
        bpy.context.scene.frame_set(frame);direction=Vector((3,-16,5)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
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
        for edge in obj.data.edges:
            line=curve.splines.new('POLY');line.points.add(1)
            for point,index in zip(line.points,edge.vertices):point.co=(*(obj.matrix_world@obj.data.vertices[index].co),1)
        obj.hide_render=True
    edge_object=bpy.data.objects.new('Technical edges from actual canonical mesh',curve);s.collection.objects.link(edge_object);curve.materials.append(wire)
    direction=Vector((5,-12,6)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    s.camera.data.ortho_scale=2.3;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=259,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=['PlasmaDischarge'],animation_checks=animation_checks,renders=renders,scope='Saved native and independent GLB runtime geometry, roots, texture pixels and actual renders. Pixel review is a separate step. No client scale/state mapping, FPS certification or final user artistic acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('MK20_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
