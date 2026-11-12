"""Verify saved AR21 and independent GLB import, including real review renders."""
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
    required=['Rare Ore Extractor continuous scalloped shell and raised hood','Rare Ore Extractor lower brass fitting','Rare Ore Extractor lower dark annular rim','Rare Ore Extractor open pale capsule frame','Rare Ore Extractor continuous brass core','Rare Ore Extractor straight pale stem','Rare Ore Extractor short red copper banded upright']
    required += ['Rare Ore Extractor '+part+' '+str(i) for i in range(2) for part in ['upper dark point','brass core collar','short stem mount']]
    assert set(result)==set(required) and len(result)==13
    meta=json.loads((ROOT/'sources/objects/artemian/rare-ore-extractor/model.json').read_bytes());assert meta['construction_updates']==40 and meta['definition_class']==21
    body=result[required[0]]
    def inside(tree,p):
        surface,normal,_,_=tree.find_nearest(p);return surface is not None and normal.dot(p-surface)<-1e-5
    pts=body['points'];assert 1.95<max(p.x for p in pts)-min(p.x for p in pts)<2.15 and abs(max(p.z for p in pts)-1.11)<1e-5 and abs(min(p.z for p in pts)-.025)<1e-5,'Low wide shell and raised tapered hood'
    for i,port in enumerate(meta['upper_ports']):
        q=Vector(port['point']);n=Vector(port['normal']);assert abs(q.z-.73)<1e-5;assert n.dot(Vector((10,-10,7)).normalized())>.25
        floor=body['tree'].ray_cast(q+n*.1,-n)[0];assert floor and .019<(q-floor).dot(n)<.021,'Actual blind upper point recess'
        witness=q-n*.022;assert inside(body['tree'],witness) and inside(result['Rare Ore Extractor upper dark point '+str(i)]['tree'],witness),'Both small dark points seated in actual hood'
    q=Vector(meta['lower_port']['point']);n=Vector(meta['lower_port']['normal']);u=n.cross(Vector((0,0,1))).normalized();floor=body['tree'].ray_cast(q+n*.1,-n)[0];assert floor and .024<(q-floor).dot(n)<.026
    witness=q-n*.027;assert inside(body['tree'],witness) and inside(result['Rare Ore Extractor lower brass fitting']['tree'],witness)
    witness=q-n*.018+u*.071;assert inside(body['tree'],witness) and inside(result['Rare Ore Extractor lower dark annular rim']['tree'],witness)
    x,y=meta['frame_centre'];frame=result['Rare Ore Extractor open pale capsule frame'];core=result['Rare Ore Extractor continuous brass core'];stem=result['Rare Ore Extractor straight pale stem']
    for z in [.945,1.775]:
        q=Vector((x,y,z));assert inside(frame['tree'],q) and inside(core['tree'],q),'Brass core physically seated at both ends of pale frame'
        cap_normal=Vector((-1,1,0)).normalized();origin=q+cap_normal*.3;cap_hit=frame['tree'].ray_cast(origin,-cap_normal)[0];core_hit=core['tree'].ray_cast(origin,-cap_normal)[0];assert cap_hit and core_hit and (cap_hit-core_hit).dot(cap_normal)>.005,'Pale endcaps enclose core ends without exposed brass tip'
    q=Vector((x,y,.88));assert inside(frame['tree'],q) and inside(stem['tree'],q),'Frame joined to straight support stem'
    for i,z in enumerate([1.20,1.47]):
        q=Vector((x,y,z));assert inside(core['tree'],q) and inside(result['Rare Ore Extractor brass core collar '+str(i)]['tree'],q)
    u=Vector((1,1,0)).normalized();normal=Vector((-1,1,0)).normalized()
    for z in [1.10,1.20,1.35,1.47,1.60]:
        q=Vector((x,y,z))+u*.07-normal;assert frame['tree'].ray_cast(q,normal)[0] is None and core['tree'].ray_cast(q,normal)[0] is None,'Real side gap of open pale frame'
        assert frame['tree'].ray_cast(Vector((x,y,z))+u*.115-normal,normal)[0] is not None,'Pale side rail bounds actual opening'
    assert 1.847<max(p.z for p in frame['points'])<1.848,'Measured post-bevel rounded capsule tip,not unmodified control point'
    for i,mount in enumerate(meta['stem_mounts']):
        part=result['Rare Ore Extractor short stem mount '+str(i)];q=Vector(mount['body_point']);hit,n,_,_=body['tree'].find_nearest(q);q=q-n*.012;assert inside(body['tree'],q) and inside(part['tree'],q),'Short stem mount physically embedded in actual shell'
        q=Vector(mount['stem_point']);assert inside(stem['tree'],q) and inside(part['tree'],q),'Short mount physically touches pale stem'
    q=Vector(meta['toe_contact']);assert inside(body['tree'],q) and inside(result['Rare Ore Extractor short red copper banded upright']['tree'],q),'Red copper upright contacts source front-left shell'
    dent=meta['physical_dent'];q=Vector(dent['point']);n=Vector(dent['normal']);hit=body['tree'].ray_cast(q+n*.2,-n)[0];assert hit and .002<(q-hit).dot(n)<.008,'Actual shallow service dent'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/127' and list(root['footprint'])==[3,3]
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
    folder=ROOT/'sources/objects/artemian/rare-ore-extractor';media=ROOT/'gallery/media/objects/artemian/rare-ore-extractor';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_artemian_rare_ore_extractor.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_artemian_rare_ore_extractor.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/ar21-concept-review.json'
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
    for label,centre,scale in [('open-pale-capsule-and-supported-brass-core-detail',Vector((-.75,-.55,1.37)),1.35),('hood-points-and-lower-front-fittings-detail',Vector((0,-.50,.53)),1.65)]:
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
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=260,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=[],renders=renders,scope='Saved native and independent GLB runtime geometry, roots, texture pixels and actual renders. Pixel review is a separate step. No client scale/state mapping, FPS certification or final user artistic acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('AR21_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
