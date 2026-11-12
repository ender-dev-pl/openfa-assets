"""Verify saved AR19 and independent GLB import, including real review renders."""
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
    required=['Force Fields low rounded green housing','Force Fields broad pale circular face','Force Fields recessed copper centre','Force Fields pale front vertical rail','Force Fields short lower toe']
    required += ['Force Fields '+part+' '+str(i) for i in range(2) for part in ['seated capsule stalk','open green capsule frame','central segment support','gold tip cap','small dark front point','small front point rim']]
    required += ['Force Fields amber segment '+str(i)+' '+str(j) for i in range(2) for j in range(3)]
    required += ['Force Fields hidden front rail bracket '+str(i) for i in range(2)]
    assert set(result)==set(required) and len(result)==25
    body=result[required[0]];pts=body['points'];assert 1.44<max(p.x for p in pts)-min(p.x for p in pts)<1.46 and .54<max(p.z for p in pts)-min(p.z for p in pts)<.55,'Low broad horizontal source housing'
    def inside(tree,p):
        surface,normal,_,_=tree.find_nearest(p);return surface is not None and normal.dot(p-surface)<-1e-5
    meta=json.loads((ROOT/'sources/objects/artemian/force-fields/model.json').read_bytes())
    for i,pillar in enumerate(meta['pillars']):
        x,y=pillar['x'],pillar['y'];frame=result['Force Fields open green capsule frame '+str(i)];stalk=result['Force Fields seated capsule stalk '+str(i)];rod=result['Force Fields central segment support '+str(i)]
        q=Vector(pillar['roof'])-Vector((0,0,.01));assert inside(body['tree'],q) and inside(stalk['tree'],q),'Capsule stalk seated inside actual housing'
        for q,name in [(Vector((x,y,.64)),'seated capsule stalk'),(Vector((x,y,.675)),'central segment support'),(Vector((x,y,1.51)),'central segment support'),(Vector((x,y,1.792)),'gold tip cap')]:assert inside(frame['tree'],q) and inside(result['Force Fields '+name+' '+str(i)]['tree'],q),'Stalk,rod ends andgold cap physically join frame'
        for j,z in enumerate([.81,1.06,1.31]):
            core=result['Force Fields amber segment '+str(i)+' '+str(j)];q=Vector((x,y,z));assert inside(rod['tree'],q) and inside(core['tree'],q),'Each of3cores mounted on real support'
            assert .178<max(p.z for p in core['points'])-min(p.z for p in core['points'])<.182
            assert frame['tree'].ray_cast(Vector((x+.09,y-1,z)),Vector((0,1,0)))[0] is None,'Actual opening beside each amber segment'
            assert core['tree'].ray_cast(Vector((x+.09,y-1,z)),Vector((0,1,0)))[0] is None,'Segment does not mask side gap'
            assert frame['tree'].ray_cast(Vector((x+.15,y-1,z)),Vector((0,1,0)))[0] is not None,'Green side rail surrounds actual open chamber'
        assert abs(max(p.z for p in frame['points'])-1.80)<1e-4,'Same physical capsule height;perspective accounts for source stagger'
    port=meta['large_port'];point=Vector(port['point']);normal=Vector(port['normal']);u=normal.cross(Vector((0,0,1))).normalized();face=result['Force Fields broad pale circular face'];copper=result['Force Fields recessed copper centre']
    for tangent in [u,-u,Vector((0,0,1)),Vector((0,0,-1))]:
        q=point-normal*.10+tangent*.18;assert inside(body['tree'],q) and inside(face['tree'],q),'Broad face has real embedded support around centre'
    floor=body['tree'].ray_cast(point+normal*.2,-normal)[0];assert floor and .034<(point-floor).dot(normal)<.036
    q=point-normal*.037;assert inside(body['tree'],q) and inside(copper['tree'],q),'Copper backing seated in actual blind recess'
    for i,port in enumerate(meta['small_ports']):
        point=Vector(port['point']);normal=Vector(port['normal']);u=normal.cross(Vector((0,0,1))).normalized();q=point-normal*.004+u*.034;assert inside(body['tree'],q) and inside(result['Force Fields small front point rim '+str(i)]['tree'],q)
        q=point-normal*.020;assert inside(body['tree'],q) and inside(result['Force Fields small dark front point '+str(i)]['tree'],q)
        assert abs(point.x+.28)<1e-5 and abs(point.z-[.45,.26][i])<1e-5,'Two small points vertically stacked beside front rail'
        assert normal.dot(Vector((10,-10,7)).normalized())>.35,'Both small front points remain readable from source review direction'
    for i,bracket in enumerate(meta['front_rail']['brackets']):
        support=result['Force Fields hidden front rail bracket '+str(i)];q=Vector(bracket['body_point'])+Vector((0,.008,0));assert inside(body['tree'],q) and inside(support['tree'],q),'Actual bracket embedded in curved housing'
        q=Vector(bracket['rail_point']);assert inside(support['tree'],q) and inside(result['Force Fields pale front vertical rail']['tree'],q),'Actual bracket supports straight rail'
    railpts=result['Force Fields pale front vertical rail']['points'];assert max(p.y for p in railpts)-min(p.y for p in railpts)<.041 and .429<max(p.z for p in railpts)-min(p.z for p in railpts)<.431,'Source narrow straight vertical fabricated rail'
    toe=result['Force Fields short lower toe'];surface,normal,_,_=body['tree'].ray_cast(Vector((meta['toe'][0],-3,.14)),Vector((0,1,0)));assert surface is not None;q=surface-normal*.004;assert inside(body['tree'],q) and inside(toe['tree'],q),'Short lower toe joined to body'
    assert max(p.z for p in toe['points'])<meta['small_ports'][1]['point'][2]-.04,'Lower toe cannot mask the lower dark point'
    evidence=meta['physical_dent'];point=Vector(evidence['point']);normal=Vector(evidence['normal']);hit=body['tree'].ray_cast(point+normal*.2,-normal)[0];assert hit and .002<(point-hit).dot(normal)<.008,'Real shallow service dent'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/125';assert list(root['footprint'])==[2,2]
    assert all(o.parent==root for o in bpy.context.scene.objects if o.type=='MESH')
    images={i.name:dict(size=list(i.size),pixels=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in i.pixels)).hexdigest()) for i in bpy.data.images if i.users and i.size[0] and i.source!='VIEWER'}
    return result,images,[float(v) for row in root.matrix_world for v in row]

def setup():
    for obj in list(bpy.context.scene.objects):
        if obj.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.film_transparent=True;s.world=bpy.data.worlds.new('Review studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO'
    for loc,power,size in [((4,-6,8),950,5),((-4,-2,5),700,4),((2,5,7),1100,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.3))-o.location).to_track_quat('-Z','Y').to_euler()
    return s

def render(label,media):
    s=setup();meshes=[o for o in s.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box];centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);renders={}
    for view,direction in [('front-quarter',(10,-10,7)),('front',(0,-16,9)),('rear-quarter',(7,12,9))]:
        v=Vector(direction).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];midpoint=Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0));s.camera.location+=s.camera.rotation_euler.to_matrix()@midpoint;s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;p=media/f'{label}-{view}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));renders[p.name]=sha(p)
    return renders

def main():
    folder=ROOT/'sources/objects/artemian/force-fields';media=ROOT/'gallery/media/objects/artemian/force-fields';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_artemian_force_fields.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_artemian_force_fields.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/ar19-concept-review.json'
    assert json.loads((ROOT/meta['concept_review']).read_bytes())['id']==meta['id']
    for ext,h in meta['binaries'].items():assert sha(folder/f'model.{ext}')==h
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False);native,ni,nr=snapshot();renders=render('native',media)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'));imported,ii,ir=snapshot();assert native.keys()==imported.keys();assert nr==ir
    # Importer may rename embedded images. Compare exact decoded pixels/sizes,
    # not Blender datablock labels or filesystem paths.
    assert sorted((v['size'],v['pixels']) for v in ni.values())==sorted((v['size'],v['pixels']) for v in ii.values())
    error=0
    for name,n in native.items():
        other=imported[name];assert n['triangles']==other['triangles'];assert n['materials']==other['materials'];assert max(abs(a-b) for a,b in zip(n['matrix'],other['matrix']))<1e-5
        error=max(error,max(other['tree'].find_nearest(p)[3] for p in n['points']),max(n['tree'].find_nearest(p)[3] for p in other['points']))
    assert error<1e-5;raw=(folder/'model.glb').read_bytes();gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values());assert tri<30000;assert not gltf.get('animations');assert len(gltf['materials'])==5;assert all('bufferView' in i for i in gltf['images']);renders.update(render('imported',media))
    s=bpy.context.scene
    for label,centre,scale in [('open-capsules-and-three-segments-detail',Vector((-.40,0,1.25)),1.9),('pale-face-and-front-fittings-detail',Vector((.10,-.25,.31)),1.65)]:
        direction=Vector((4,-16,10)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
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
    direction=Vector((4,-14,10)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    s.camera.data.ortho_scale=3.3;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    glowing=[m for m in gltf['materials'] if m.get('name')=='Amber cores and tip caps - steady authored emission'];assert len(glowing)==1 and min(glowing[0].get('emissiveFactor',[0]))>0 and 'emissiveTexture' in glowing[0]
    for obj in s.objects:
        if obj.type=='CURVE':obj.hide_render=True
        elif obj.type=='MESH':obj.hide_render=False
    for obj in s.objects:
        if obj.type=='LIGHT':obj.data.energy=3
    s.world.node_tree.nodes['Background'].inputs[1].default_value=.015
    direction=Vector((7,-12,8)).normalized();centre=Vector((-.02,0,.95));s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=2.8
    mat=bpy.data.materials['Amber cores and tip caps - steady authored emission'];shader=mat.node_tree.nodes.get('Principled BSDF');saved=shader.inputs['Emission Strength'].default_value;assert saved>0
    for label,strength in [('emission-review-on',saved),('emission-review-off',0)]:
        shader.inputs['Emission Strength'].default_value=strength;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    shader.inputs['Emission Strength'].default_value=saved
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=260,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=[],renders=renders,scope='Saved native and independent GLB runtime geometry, roots, texture pixels and actual renders. Pixel review is a separate step. No client scale/state mapping, FPS certification or final user artistic acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('AR19_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
