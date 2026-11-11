"""Verify saved MN07 and independent GLB import, including real review renders."""
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
    required=['Elite Block main concrete body','Elite Block main roof lip','Elite Block upper command sensor tower','Elite Block tall point-bearing pale mast','Elite Block shorter pale mast','Elite Block five unequal brass roof pins','Elite Block four straight blue fields','Elite Block blue L field','Elite Block eighteen dark field backings','Elite Block fortyfour amber points','Elite Block two brass front frames','Elite Block two dark panel centres']
    assert set(result)==set(required) and len(result)==12
    meta=json.loads((ROOT/'sources/objects/mauna/elite-block/model.json').read_bytes());assert meta['construction_updates']==56 and meta['definition_class']==16 and meta['culture']=='mauna'
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
    body=result[required[0]];roof=result[required[1]];tower=result[required[2]];tall=result[required[3]];short=result[required[4]]
    assert abs(min(p.z for p in body['points'])-.08)<1e-5 and abs(max(p.z for p in body['points'])-2.38)<1e-5
    assert abs(max(p.z for p in roof['points'])-2.43)<1e-5 and abs(max(p.z for p in tower['points'])-3.10)<1e-5
    q=Vector((0,0,2.36));assert inside(body['tree'],q) and inside(roof['tree'],q),'Roof lip physically seated in main body'
    q=Vector((-.06,.07,2.415));assert inside(roof['tree'],q) and inside(tower['tree'],q),'Upper tower physically seated on main roof'
    for name,q in [(required[3],Vector((.02,0,3.09))),(required[4],Vector((-.12,.07,3.09)))]:assert inside(tower['tree'],q) and inside(result[name]['tree'],q),'Both split mast uprights seated in upper roof'
    assert abs(max(p.z for p in tall['points'])-3.75)<1e-5 and abs(max(p.z for p in short['points'])-3.56)<1e-5
    assert components(required[8])==18 and components(required[9])==44 and components(required[6])==4 and components(required[10])==2 and components(required[11])==2
    assert len(meta['rectangular_recesses'])==24 and len(meta['point_banks'])==18
    for field in meta['rectangular_recesses']:
        part=result[field['body']];q=Vector(field['point']);n=Vector(field['normal']);floor=part['tree'].ray_cast(q+n*.12,-n)[0];assert floor and abs((q-floor).dot(n)-field['depth'])<1e-5,'Actual blind field floor'
        witness=q-n*field.get('contact_depth',field['depth']+.007);assert inside(part['tree'],witness) and inside(result[field['object']]['tree'],witness),'All field/frame backings physically seated'
    assert sum(bank['cols']*bank['rows'] for bank in meta['point_banks'])==44
    for bank in meta['point_banks']:
        assert len(bank['contacts'])==bank['cols']*bank['rows']
        for point in bank['contacts']:
            q=Vector(point);assert inside(result[required[8]]['tree'],q) and inside(result[required[9]]['tree'],q),'Every small amber point physically contacts its actual backing'
    for point in meta['blue_l_witnesses']:
        q=Vector(point);hit=body['tree'].ray_cast(q+Vector((.1,0,0)),Vector((-1,0,0)))[0];assert hit and abs(hit.x-.615)<1e-5,'True L-shaped blind field has authored depth'
        witness=Vector((.612,q.y,q.z));assert inside(body['tree'],witness) and inside(result[required[7]]['tree'],witness),'Cobalt L backing seated in actual recess'
    hit=body['tree'].ray_cast(Vector((1,.30,.90)),Vector((-1,0,0)))[0];assert hit and abs(hit.x-.65)<1e-5,'Intact wall inside missing lower-right region distinguishes L from rectangle'
    for panel in meta['brass_panel_centres']:
        q=Vector(panel['face']);n=Vector(panel['normal']);floor=result[required[10]]['tree'].ray_cast(q+n*.1,-n)[0];assert floor and abs((q-floor).dot(n)-panel['depth'])<1e-5,'Two brass frames have actual blind dark centres'
        witness=Vector(panel['contact']);assert inside(result[required[10]]['tree'],witness) and inside(result[required[11]]['tree'],witness),'Dark panel centres seated in brass frames'
    assert components(required[5])==5 and len(meta['roof_pins'])==5
    for pin in meta['roof_pins']:
        q=Vector(pin['contact']);assert inside(result[pin['support']]['tree'],q) and inside(result[required[5]]['tree'],q),'Allfive angular roof pins seated on actual roof/tower supports'
    for chip in meta['physical_chips']:
        q=Vector(chip['point']);n=Vector(chip['normal']);hit=result[chip['body']]['tree'].ray_cast(q+n*.2,-n)[0];assert hit and .003<(q-hit).dot(n)<.012,'Actual shallow cast service chip'
    view=Vector((10,-10,7)).normalized()
    for bank in meta['point_banks']:
        if bank['key']=='mast points':
            for p in bank['contacts']:assert short['tree'].ray_cast(Vector(p)+view*5,-view,4.99)[0] is None,'Tallmast points visible past shorter companion'
    glass=next(m for m in bpy.data.materials if m.name=='Warm amber service points with authored steady light');node=glass.node_tree.nodes.get('Principled BSDF');emission=[node.inputs['Emission Color'].default_value[i]*node.inputs['Emission Strength'].default_value for i in range(3)];assert max(abs(a-b) for a,b in zip(emission,[.075,.06,.025]))<1e-5
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/136' and list(root['footprint'])==[3,3]
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
    folder=ROOT/'sources/objects/mauna/elite-block';media=ROOT/'gallery/media/objects/mauna/elite-block';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_mauna_elite_block.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_mauna_elite_block.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/mn07-concept-review.json'
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
    for label,centre,scale in [('split-sensor-mast-and-roof-pins-detail',Vector((-.06,.07,3.10)),1.9),('blue-l-field-and-command-panels-detail',Vector((.05,-.05,1.15)),2.35)]:
        direction=Vector((8,-10,10) if label.startswith('split') else (12,-10,8)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
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
    s.camera.data.ortho_scale=4.5;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=261,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=[],renders=renders,scope='Saved native and independent GLB runtime geometry, roots, texture pixels and actual renders. Pixel review is a separate step. No client scale/state mapping, FPS certification or final user artistic acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('MN07_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
