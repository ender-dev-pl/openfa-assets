"""Reusable saved-native/imported Achaean GLB runtime and real-render gate."""
import argparse,hashlib,importlib,json,math,struct,sys
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
    root=bpy.data.objects['PlacementRoot'];assert all(o.parent==root for o in bpy.context.scene.objects if o.type=='MESH')
    images={i.name:dict(size=list(i.size),pixels=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in i.pixels)).hexdigest()) for i in bpy.data.images if i.users and i.size[0] and i.source!='VIEWER'}
    return result,images,[float(v) for row in root.matrix_world for v in row]

def setup():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.film_transparent=True;s.world=bpy.data.worlds.new('Review studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO'
    for loc,power,size in [((4,-6,8),950,5),((-4,-2,5),700,4),((2,5,7),1100,4),((0,-6,2.5),220,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.7))-o.location).to_track_quat('-Z','Y').to_euler()
    return s

def render(label,media):
    s=setup();meshes=[o for o in s.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box];centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);renders={}
    for view,direction in [('front-quarter',(5,-12,6)),('front',(0,-16,3)),('rear-quarter',(-7,12,6))]:
        v=Vector(direction).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;p=media/f'{label}-{view}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));renders[p.name]=sha(p)
    return renders

def main(folder):
    assert folder.isidentifier() or all(p.isalnum() for p in folder.split('-'))
    output=(ROOT/'sources/objects/achaean'/folder).resolve();assert output.is_relative_to((ROOT/'sources/objects/achaean').resolve())
    media=ROOT/'gallery/media/objects/achaean'/folder;media.mkdir(parents=True,exist_ok=True);meta=json.loads((output/'model.json').read_bytes());assert meta['culture']=='achaean'
    author=(ROOT/meta['author']).resolve();assert author.is_relative_to((ROOT/'sources/tools/blender').resolve()) and sha(author)==meta['author_sha256']
    for rel,h in meta['helpers'].items():assert sha(ROOT/rel)==h
    for ext,h in meta['binaries'].items():assert sha(output/f'model.{ext}')==h
    assert meta['structure_checks'].isidentifier();sys.path.insert(0,str(Path(__file__).parent));module=importlib.import_module(meta['structure_checks']);structure=module.structure
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'),load_ui=False,use_scripts=False);native,ni,nr=snapshot();native_form=structure();renders=render('native',media)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'));imported,ii,ir=snapshot();imported_form=structure();assert native.keys()==imported.keys() and nr==ir
    assert sorted((v['size'],v['pixels']) for v in ni.values())==sorted((v['size'],v['pixels']) for v in ii.values())
    error=0
    for name,n in native.items():
        other=imported[name];assert n['triangles']==other['triangles'];assert n['materials']==other['materials'];assert max(abs(a-b) for a,b in zip(n['matrix'],other['matrix']))<1e-5
        error=max(error,max(other['tree'].find_nearest(p)[3] for p in n['points']),max(n['tree'].find_nearest(p)[3] for p in other['points']))
    assert error<1e-5;raw=(output/'model.glb').read_bytes();document=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(document['accessors'][p['indices']]['count']//3 for node in document['nodes'] if 'mesh' in node for p in document['meshes'][node['mesh']]['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values())<meta['triangle_budget'];assert not document.get('animations');assert len(document['materials'])==meta['materials'];assert all('bufferView' in i for i in document['images']);renders.update(render('imported',media))
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    assert bounds[2]>=-1e-5
    helpers={**meta['helpers'],meta['author']:sha(author),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),Path(module.__file__).relative_to(ROOT).as_posix():sha(Path(module.__file__))}
    report=dict(issue=256,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(output/'model.json'),verifier=Path(__file__).relative_to(ROOT).as_posix(),helpers=helpers,triangles=tri,meshes=len(native),materials=len(document['materials']),embedded_images=len(document['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,native_anatomy=native_form,imported_anatomy=imported_form,clips=[],renders=renders,scope='Actual saved-native/independent GLB geometry, rooted anatomy, textures and renders. Source-specific checks run on both. Pixel review separate; client scale/state/FPS and final user artistic acceptance remain unverified.',final_artistic_acceptance=False,game_client_integration=False)
    (output/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('ACHAEAN_RUNTIME_OK',meta['key'],tri,len(native),error,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.model)
