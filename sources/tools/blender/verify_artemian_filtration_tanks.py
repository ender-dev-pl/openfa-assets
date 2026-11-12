"""Verify saved AR03 and independent GLB import, including real review renders."""
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
    required=['Filtration Tanks broad green metal carapace']+['Filtration Tanks '+label+' '+str(i) for i in range(3) for label in ['pale side fitting','pale side cap']]+['Filtration Tanks '+label+' '+str(i) for i in range(4) for label in ['dark module seat','amber roof module']]+['Filtration Tanks '+label+' '+str(i) for i in range(2) for label in ['red front inset','front inset rim']]+['Filtration Tanks tall rear silver upright','Filtration Tanks silver upright cap','Filtration Tanks connected return bend','Filtration Tanks separate short roof upright','Filtration Tanks tiny dark roof point'];assert all(name in result for name in required) and len(result)==24
    body=result[required[0]];points=body['points'];width=max(p.x for p in points)-min(p.x for p in points);length=max(p.y for p in points)-min(p.y for p in points);height=max(p.z for p in points)-min(p.z for p in points);assert 1.54<width<1.62 and 1.45<length/width<1.55 and .38<height/width<.43,'Broad low oval source shell'
    def inside(tree,p):
        surface,normal,_,distance=tree.find_nearest(p);return surface is not None and normal.dot(p-surface)<-1e-5
    for i,y in enumerate([.48,0,-.48]):
        post=result['Filtration Tanks pale side fitting '+str(i)];pts=post['points'];cx=(min(p.x for p in pts)+max(p.x for p in pts))/2;sample=Vector((cx+.020,y,.13));assert inside(body['tree'],sample) and inside(post['tree'],sample),'Three pale side fittings rooted against real low shell'
        cap=result['Filtration Tanks pale side cap '+str(i)]['points'];assert min(p.z for p in cap)<max(p.z for p in pts)<max(p.z for p in cap) and max(p.z for p in cap)<.38,'Small source pale rounded tops overlap fittings'
    for i,y in enumerate([.20,.38,.56,.74]):
        roof=body['tree'].ray_cast(Vector((-.34,y,2)),Vector((0,0,-1)))[0];assert roof;sample=roof-Vector((0,0,.003));assert inside(body['tree'],sample) and inside(result['Filtration Tanks dark module seat '+str(i)]['tree'],sample),'Four module seats meet actual curved roof'
        a=result['Filtration Tanks dark module seat '+str(i)]['points'];b=result['Filtration Tanks amber roof module '+str(i)]['points'];assert min(p.z for p in b)<max(p.z for p in a)<max(p.z for p in b),'Amber module physically overlaps its seat';assert max(p.z for p in b)-min(p.z for p in b)<.05,'Source modules remain small'
    main=result['Filtration Tanks tall rear silver upright'];pipe=result['Filtration Tanks connected return bend']
    for x,structure in [(.10,main),(-.12,pipe)]:
        roof=body['tree'].ray_cast(Vector((x,.60,2)),Vector((0,0,-1)))[0];assert roof;sample=roof-Vector((0,0,.025));assert inside(body['tree'],sample) and inside(structure['tree'],sample),'Both rear pipe roots lie inside shell'
    join=Vector((.085,.60,1.05));assert inside(main['tree'],join) and inside(pipe['tree'],join),'Actual connected pipe bend'
    cap=result['Filtration Tanks silver upright cap']['points'];assert min(p.z for p in cap)<max(p.z for p in main['points'])<max(p.z for p in cap) and max(p.z for p in cap)<1.25
    short=result['Filtration Tanks separate short roof upright']['points'];assert max(p.z for p in short)<.85 and max(p.z for p in cap)-max(p.z for p in short)>.35,'One clearly shorter separate roof upright'
    for i in range(2):
        pts=result['Filtration Tanks red front inset '+str(i)]['points'];centre=sum(pts,Vector())/len(pts);assert centre.y<-.90 and body['tree'].find_nearest(centre)[3]<.04,'Two unequal red front points seated on shell'
    extent=lambda ps:max(max(p[a] for p in ps)-min(p[a] for p in ps) for a in range(3));assert 1.35<extent(result['Filtration Tanks red front inset 1']['points'])/extent(result['Filtration Tanks red front inset 0']['points'])<1.65
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/109';assert list(root['footprint'])==[3,3]
    assert all(o.parent==root for o in bpy.context.scene.objects if o.type=='MESH')
    images={i.name:dict(size=list(i.size),pixels=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in i.pixels)).hexdigest()) for i in bpy.data.images if i.users and i.size[0] and i.source!='VIEWER'}
    return result,images,[float(v) for row in root.matrix_world for v in row]

def setup():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.film_transparent=True;s.world=bpy.data.worlds.new('Review studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO'
    for loc,power,size in [((4,-6,8),950,5),((-4,-2,5),700,4),((2,5,7),1100,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.3))-o.location).to_track_quat('-Z','Y').to_euler()
    return s

def render(label,media):
    s=setup();meshes=[o for o in s.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box];centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);renders={}
    for view,direction in [('front-quarter',(-10,-10,9)),('front',(0,-16,9)),('rear-quarter',(7,12,9))]:
        v=Vector(direction).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];midpoint=Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0));s.camera.location+=s.camera.rotation_euler.to_matrix()@midpoint;s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;p=media/f'{label}-{view}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));renders[p.name]=sha(p)
    return renders

def main():
    folder=ROOT/'sources/objects/artemian/filtration-tanks';media=ROOT/'gallery/media/objects/artemian/filtration-tanks';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_artemian_filtration_tanks.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_artemian_filtration_tanks.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/ar03-concept-review.json'
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
    for label,centre,scale in [('side-fittings-and-module-detail',Vector((-.38,.18,.35)),1.55),('rear-pipe-and-front-marker-detail',Vector((0,.10,.58)),2.2)]:
        direction=Vector((-8,-16,8)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
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
    direction=Vector((-10,-10,9)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    s.camera.data.ortho_scale=3.3;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=260,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=[],renders=renders,scope='Saved native and independent GLB runtime geometry, roots, texture pixels and actual renders. Pixel review is a separate step. No client scale/state mapping, FPS certification or final user artistic acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('AR03_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
