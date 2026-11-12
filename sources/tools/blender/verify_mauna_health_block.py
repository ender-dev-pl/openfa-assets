"""Verify saved MN05 and independent GLB import, including real review renders."""
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
    keys=['upper front','upper right','mid front left','mid front right','lower front point','lower right 0','lower right 1','lower right 2']
    required=['Health Block lower concrete body','Health Block smaller upper tower','Health Block nineteen amber panes','Health Block three angular service conduits','Health Block three attached lower mounts']+['Health Block '+key+' backing' for key in keys]+['Health Block lower brass panel '+str(i) for i in range(2)]+['Health Block red corner strip '+str(i) for i in range(2)]+['Health Block brass roof element '+str(i) for i in range(3)]+['Health Block pale roof upright '+str(i) for i in range(2)]
    assert set(result)==set(required) and len(result)==22
    meta=json.loads((ROOT/'sources/objects/mauna/health-block/model.json').read_bytes());assert meta['construction_updates']==16 and meta['definition_class']==34 and meta['culture']=='mauna'
    def inside(tree,p):
        surface,normal,_,_=tree.find_nearest(p);return surface is not None and normal.dot(p-surface)<-1e-5
    def components(name):
        bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);remaining=set(bm.verts);count=0
        while remaining:
            queue=[remaining.pop()];count+=1
            while queue:
                vertex=queue.pop()
                for edge in vertex.link_edges:
                    other=edge.other_vert(vertex)
                    if other in remaining:remaining.remove(other);queue.append(other)
        bm.free();return count
    lower=result[required[0]];upper=result[required[1]];panes=result[required[2]];conduits=result[required[3]];mounts=result[required[4]]
    assert abs(min(p.z for p in lower['points'])-.08)<1e-5 and abs(max(p.z for p in lower['points'])-1.60)<1e-5
    assert abs(min(p.z for p in upper['points'])-1.56)<1e-5 and abs(max(p.z for p in upper['points'])-2.44)<1e-5
    q=Vector((-.12,.08,1.58));assert inside(lower['tree'],q) and inside(upper['tree'],q),'Upper tower physically seated in lower body'
    assert len(meta['rectangular_recesses'])==12
    for field in meta['rectangular_recesses']:
        body=result[field['body']];q=Vector(field['point']);n=Vector(field['normal']);floor=body['tree'].ray_cast(q+n*.12,-n)[0];assert floor and abs((q-floor).dot(n)-field['depth'])<1e-5,'Actual blind service field'
        witness=q-n*(field['depth']+.007);assert inside(body['tree'],witness) and inside(result[field['object']]['tree'],witness),'Backing physically seated in core'
    assert components(required[2])==19 and len(meta['pane_banks'])==8
    assert [b['cols']*b['rows'] for b in meta['pane_banks']]==[4,4,2,2,1,2,2,2]
    for bank in meta['pane_banks']:
        assert len(bank['contacts'])==bank['cols']*bank['rows']
        for point in bank['contacts']:
            q=Vector(point);assert inside(panes['tree'],q) and inside(result[bank['backing']]['tree'],q),'Each of19pane elements contacts its actual backing'
    assert components(required[3])==3 and components(required[4])==3 and len(meta['conduit_contacts'])==3
    for fixture in meta['conduit_contacts']:
        q=Vector(fixture['upper_contact']);assert inside(upper['tree'],q) and inside(conduits['tree'],q),'Angular conduit upper end physically embedded in tower'
        q=Vector(fixture['mount_contact']);assert inside(conduits['tree'],q) and inside(mounts['tree'],q),'Conduit lower end joins actual lower mounting block'
        q=Vector(fixture['wall_contact']);assert inside(lower['tree'],q) and inside(mounts['tree'],q),'Mount physically attached to lower wall'
        for point in fixture['route'][1:-1]:assert lower['tree'].find_nearest(Vector(point))[3]>.030,'Conduit route passes above/outside shoulder instead of cutting through concrete'
    assert len(meta['roof_elements'])==5 and [r['material'] for r in meta['roof_elements']].count('brass')==3
    assert [r['material'] for r in meta['roof_elements']].count('pale-alloy')==2
    tops=[]
    for element in meta['roof_elements']:
        part=result[element['object']];q=Vector(element['contact']);assert inside(upper['tree'],q) and inside(part['tree'],q),'Allfive roofelements seated in tower roof'
        top=max(p.z for p in part['points']);assert abs(top-element['top'])<1e-5;tops.append(top)
    view=Vector((10,-10,7)).normalized()
    for element in meta['roof_elements']:
        q=Vector((*element['contact'][:2],element['top']-.025))
        for other in meta['roof_elements']:
            if other['object']!=element['object']:assert result[other['object']]['tree'].ray_cast(q+view*5,-view,4.99)[0] is None,'Each of five source roofelements has a visible top from source-review direction'
    assert tops[4]>tops[1]>tops[3]>tops[0]>tops[2],'Tallpale,tallbrass,shortpale andtwoshortbrass elements retain unequal hierarchy'
    for chip in meta['physical_chips']:
        q=Vector(chip['point']);n=Vector(chip['normal']);hit=result[chip['body']]['tree'].ray_cast(q+n*.2,-n)[0];assert hit and .003<(q-hit).dot(n)<.012,'Actual shallow cast service chip'
    glass=next(m for m in bpy.data.materials if m.name=='Yellowgreen service panes with authored steady light');node=glass.node_tree.nodes.get('Principled BSDF');emission=[node.inputs['Emission Color'].default_value[i]*node.inputs['Emission Strength'].default_value for i in range(3)];assert max(abs(a-b) for a,b in zip(emission,[.075,.075,.01625]))<1e-5,'Authored lowsteadyemission preserved withoutinventing timedphase'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/134' and list(root['footprint'])==[2,2]
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
    folder=ROOT/'sources/objects/mauna/health-block';media=ROOT/'gallery/media/objects/mauna/health-block';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_mauna_health_block.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_mauna_health_block.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/mn05-concept-review.json'
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
    assert error<1e-5;raw=(folder/'model.glb').read_bytes();gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values());assert tri<30000;assert not gltf.get('animations');assert len(gltf['materials'])==6;assert all('bufferView' in i for i in gltf['images']);renders.update(render('imported',media))
    s=bpy.context.scene
    for label,centre,scale in [('five-roof-elements-detail',Vector((-.12,.08,2.68)),1.65),('three-attached-conduits-and-service-fields-detail',Vector((.32,0,1.43)),2.35)]:
        direction=Vector((8,-10,10) if label.startswith('five') else (12,-10,8)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
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
    s.camera.data.ortho_scale=4.0;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=261,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=[],renders=renders,scope='Saved native and independent GLB runtime geometry, roots, texture pixels and actual renders. Pixel review is a separate step. No client scale/state mapping, FPS certification or final user artistic acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('MN05_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
