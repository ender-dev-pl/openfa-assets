"""Verify saved MN12 and independent GLB import, including real review renders."""
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
    meta=json.loads((ROOT/'sources/objects/mauna/arms-block/model.json').read_bytes())
    assert meta['definition_class']==7 and meta['construction_updates']==36 and meta['culture']=='mauna'
    assert len(result)==meta['mesh_nodes']==10 and len(meta['rectangular_recesses'])==11
    parts={}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        for group in obj.vertex_groups:
            indices={v.index for v in obj.data.vertices if any(g.group==group.index and g.weight>.5 for g in v.groups)};faces=[tuple(p.vertices) for p in obj.data.polygons if set(p.vertices).issubset(indices)];assert faces
            parts[group.name]=BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],faces)
    def tree(name):return parts[name] if name in parts else result[meta['part_batches'].get(name,name)]['tree']
    def inside(t,p):
        surface,normal,_,_=t.find_nearest(p);return surface is not None and normal.dot(p-surface)<-1e-5
    for field in meta['rectangular_recesses']:
        q=Vector(field['point']);n=Vector(field['normal']);hit=tree(field['body']).ray_cast(q+n*.1,-n)[0]
        assert hit and abs((q-hit).dot(n)-field['depth'])<1e-5,('Actual blind recess',field['object'])
        witness=q-n*field['contact_depth'];assert inside(tree(field['body']),witness) and inside(tree(field['object']),witness),('Seated blind field',field['object'])
    for contact in meta['attachment_contacts']:
        q=Vector(contact['point']);assert inside(tree(contact['object']),q) and inside(tree(contact['support']),q),('Actual connected part',contact['object'],contact['support'])
    def components(name):
        bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.verts.index_update();adj=[set() for _ in bm.verts]
        for e in bm.edges:a,b=[v.index for v in e.verts];adj[a].add(b);adj[b].add(a)
        bm.free();unseen=set(range(len(adj)));count=0
        while unseen:
            pending=[unseen.pop()];count+=1
            while pending:
                connected=adj[pending.pop()] & unseen;unseen.difference_update(connected);pending.extend(connected)
        return count
    assert components('Arms Block twenty-two source amber points')==22
    assert components('Arms Block pale roof and end assemblies')==9
    assert components('Arms Block red industrial mark')==1
    assert components('Arms Block dark blind backings')==11
    expected={'tower-front':5,'tower-right':3,'lower-front-upper':2,'lower-front-lower':4,'lower-end':4,'roof-post':1,'under-emblem':3}
    assert len(meta['warm_points'])==22
    assert {g:sum(p['group']==g for p in meta['warm_points']) for g in expected}==expected
    centres=[]
    for point in meta['warm_points']:
        centre=Vector(point['centre']);assert inside(tree(point['object']),centre),'Actual source-group point centre';assert all((centre-other).length>.06 for other in centres),'Distinct visible source points';centres.append(centre)
    main=tree('Arms Block tall inclined emblem block')
    for z in [.5,1.5]:
        hit=main.ray_cast(Vector((-.97,-3,z)),Vector((0,1,0)))[0];assert hit and abs(hit.y-(-.60+.45*(z-.10)/1.75))<1e-5,'Continuous inclined emblem wall,not stepped terraces'
    nose=tree('Arms Block low projecting sloping end foot')
    for z in [.2,.3]:
        hit=nose.ray_cast(Vector((3,0,z)),Vector((-1,0,0)))[0];assert hit and abs(hit.x-(1.18-.20*(z-.16)/.31))<1e-5,'Actual sloping end foot'
    for name,top in [('Arms Block square upper tower',2.80),('Arms Block lower connected service block',1.40),('Arms Block short lower roof service post',1.77)]:assert abs(max(p.z for p in result[name]['points'])-top)<1e-5,('Source height hierarchy',name)
    for chip in meta['physical_chips']:
        q=Vector(chip['point']);n=Vector(chip['normal']);hit=tree(chip['body']).ray_cast(q+n*.1,-n)[0];assert hit and .003<(q-hit).dot(n)<.012,'Actual shallow wear chip'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/141' and list(root['footprint'])==[4,4] and root['preserve_ground_origin'] and root['ground_level']==0
    assert all(o.parent==root and not o.animation_data for o in bpy.context.scene.objects if o.type=='MESH')
    allpoints=[p for n in result.values() for p in n['points']];assert abs(min(p.z for p in allpoints))<1e-5 and abs(max(p.z for p in allpoints)-3.61)<1e-5
    light=bpy.data.materials['Opaque warm amber service points'].node_tree.nodes.get('Principled BSDF');colour=light.inputs['Emission Color'].default_value;strength=light.inputs['Emission Strength'].default_value
    assert max(abs(colour[i]*strength-value) for i,value in enumerate([.195,.117,.0325]))<1e-5,'Authored steady source-colour emission'
    assert light.inputs['Alpha'].default_value==1 and light.inputs['Transmission Weight'].default_value==0
    reachable={node.image for obj in bpy.context.scene.objects if obj.type=='MESH' for mat in obj.data.materials if mat and mat.use_nodes for node in mat.node_tree.nodes if node.type=='TEX_IMAGE' and node.image}
    images={i.name:dict(size=list(i.size),pixels=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in i.pixels)).hexdigest()) for i in reachable if i.users and i.size[0] and i.source!='VIEWER'}
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
    s=setup();meshes=[o for o in s.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box ];centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);renders={}
    for view,direction in [('front-quarter',(10,-10,7)),('front',(0,-16,9)),('rear-quarter',(7,12,9))]:
        v=Vector(direction).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];midpoint=Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0));s.camera.location+=s.camera.rotation_euler.to_matrix()@midpoint;s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;p=media/f'{label}-{view}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));renders[p.name]=sha(p)
    return renders

def main():
    folder=ROOT/'sources/objects/mauna/arms-block';media=ROOT/'gallery/media/objects/mauna/arms-block';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_mauna_arms_block.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_mauna_arms_block.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/mn12-concept-review.json'
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
    s=bpy.context.scene
    for label,centre,scale in [('tower-masts-and-warm-fields-detail',Vector((-.52,.12,2.65)),2.05),('red-emblem-and-service-block-detail',Vector((.03,-.08,.94)),2.9)]:
        direction=Vector((8,-10,12)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
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
    s.camera.data.ortho_scale=4.5;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=261,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=[],renders=renders,scope='Saved native and independent GLB runtime geometry, roots, texture pixels and actual renders. Pixel review is a separate step. No client scale/state mapping, FPS certification or final user artistic acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('MN12_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
