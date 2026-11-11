"""Verify saved MN06 and independent GLB import, including real review renders."""
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
    required=['The Cube concrete core','The Cube shallow overhanging roof lip','The Cube low slotted roof block','The Cube two dark roof cells','The Cube upper front red band','The Cube upper corner red return']+['The Cube lower right red band '+str(i) for i in range(2)]+['The Cube lower front red return '+str(i) for i in range(2)]+['The Cube five pale front slits','The Cube three pale side slits','The Cube three short front brass posts','The Cube three pale post caps','The Cube five unequal right brass staves','The Cube three small brass roof pins']
    assert set(result)==set(required) and len(result)==16
    meta=json.loads((ROOT/'sources/objects/mauna/the-cube/model.json').read_bytes());assert meta['construction_updates']==30 and meta['definition_class']==255 and meta['culture']=='mauna'
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
    body=result[required[0]];roof=result[required[1]];vent=result[required[2]];cells=result[required[3]]
    assert abs(min(p.z for p in body['points'])-.08)<1e-5 and abs(max(p.z for p in body['points'])-1.88)<1e-5
    assert abs(max(p.z for p in roof['points'])-1.95)<1e-5 and abs(max(p.z for p in vent['points'])-2.06)<1e-5
    q=Vector((0,0,1.86));assert inside(body['tree'],q) and inside(roof['tree'],q),'Roof lip seated in actual cube core'
    q=Vector((-.24,-.18,1.94));assert inside(roof['tree'],q) and inside(vent['tree'],q),'Low roof vent physically seated on roof lip'
    assert len(meta['rectangular_recesses'])==9
    for field in meta['rectangular_recesses']:
        q=Vector(field['point']);n=Vector(field['normal']);floor=body['tree'].ray_cast(q+n*.12,-n)[0];assert floor and abs((q-floor).dot(n)-field['depth'])<1e-5,'Actual blind red/pale field depth'
        witness=q-n*(field['depth']+.007);assert inside(body['tree'],witness) and inside(result[field['object']]['tree'],witness),'Red/pale backing physically seated in core'
    assert components('The Cube five pale front slits')==5 and components('The Cube three pale side slits')==3
    assert len(meta['front_slit_contacts'])==5
    for point in meta['front_slit_contacts']:
        q=Vector(point);assert inside(result['The Cube five pale front slits']['tree'],q) and inside(result['The Cube upper front red band']['tree'],q),'Five front slits contact actual upper red backing'
    assert components('The Cube three short front brass posts')==3 and components('The Cube three pale post caps')==3
    for fixture in meta['front_post_contacts']:
        q=Vector(fixture['body_contact']);assert inside(body['tree'],q) and inside(result['The Cube three short front brass posts']['tree'],q),'Short front brass posts seated in concrete'
        q=Vector(fixture['cap_contact']);assert inside(result['The Cube three short front brass posts']['tree'],q) and inside(result['The Cube three pale post caps']['tree'],q),'Allthree pale caps actually contact their brass posts'
    staves=result['The Cube five unequal right brass staves'];assert components('The Cube five unequal right brass staves')==5 and len(meta['right_staves'])==5
    for stave in meta['right_staves']:
        q=Vector(stave['body_contact']);assert inside(body['tree'],q) and inside(staves['tree'],q),'Allfive unequal right staves seated in core'
        points=[p for p in staves['points'] if abs(p.y-stave['u'])<.051];assert points and abs(max(p.z for p in points)-stave['top'])<1e-5 and abs(min(p.z for p in points)-stave['bottom'])<1e-5,'Measured source-specific irregular stave heights'
    assert components('The Cube three small brass roof pins')==3 and len(meta['roof_pins'])==3
    for pin in meta['roof_pins']:
        q=Vector(pin['contact']);assert inside(roof['tree'],q) and inside(result['The Cube three small brass roof pins']['tree'],q),'Three small angular roof pins seated on roof'
    assert components(required[3])==2 and len(meta['roof_cells'])==2
    for cell in meta['roof_cells']:
        x,y=cell['centre'];hit=vent['tree'].ray_cast(Vector((x,y,2.4)),Vector((0,0,-1)))[0];assert hit and abs(hit.z-cell['floor'])<1e-5,'Two-cell reading has actual blind floors'
        q=Vector(cell['contact']);assert inside(vent['tree'],q) and inside(cells['tree'],q),'Dark roof cells seated inside actual recesses'
    view=Vector((10,-10,7)).normalized()
    for field in meta['rectangular_recesses']:
        if field['object']=='The Cube three pale side slits':assert staves['tree'].ray_cast(Vector(field['point'])+view*5,-view,4.99)[0] is None,'Three side slits remain visible among unequal staves'
    for chip in meta['physical_chips']:
        q=Vector(chip['point']);n=Vector(chip['normal']);hit=result[chip['body']]['tree'].ray_cast(q+n*.2,-n)[0];assert hit and .003<(q-hit).dot(n)<.012,'Actual shallow cast service chip'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/135' and list(root['footprint'])==[3,3]
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
    folder=ROOT/'sources/objects/mauna/the-cube';media=ROOT/'gallery/media/objects/mauna/the-cube';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_mauna_the_cube.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_mauna_the_cube.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/mn06-concept-review.json'
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
    assert error<1e-5;raw=(folder/'model.glb').read_bytes();gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values());assert tri<30000;assert not gltf.get('animations');assert all(not any(m.get('emissiveFactor',[0,0,0])) for m in gltf['materials']);assert len(gltf['materials'])==5;assert all('bufferView' in i for i in gltf['images']);renders.update(render('imported',media))
    s=bpy.context.scene
    for label,centre,scale in [('slotted-roof-block-and-three-pins-detail',Vector((0,0,1.96)),2.05),('red-bands-pale-slits-and-unequal-staves-detail',Vector((.20,-.20,1.0)),2.45)]:
        direction=Vector((10,-10,10)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
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
    report=dict(issue=261,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=[],renders=renders,scope='Saved native and independent GLB runtime geometry, roots, texture pixels and actual renders. Pixel review is a separate step. No client scale/state mapping, FPS certification or final user artistic acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('MN06_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
