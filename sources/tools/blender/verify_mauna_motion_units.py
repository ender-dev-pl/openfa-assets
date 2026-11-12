"""Verify saved MN20 and independent GLB import, including real review renders."""
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
    meta=json.loads((ROOT/'sources/objects/mauna/motion-units/model.json').read_bytes())
    assert meta['definition_class']==22 and meta['construction_updates']==66 and meta['culture']=='mauna'
    assert len(result)==meta['mesh_nodes']==10 and len(meta['rectangular_recesses'])==10
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
    assert len(meta['attachment_contacts'])==28 and len(meta['roof_prongs'])==2
    for prong in meta['roof_prongs']:
        t=tree(prong['object']);a=Vector(prong['start']);b=Vector(prong['end'])
        for fraction in [.05,.25,.50,.75,.95]:assert inside(t,a.lerp(b,fraction)),('Actual continuous solid prong',prong['object'],fraction)
    lower_prong=tree('Motion Units same-side brass prong 0');upper_prong=tree('Motion Units same-side brass prong 1')
    for y in [.16,.25,.35,.43]:
        lower_z=2.54+(y-.04)*.51/.56;upper_z=2.84+(y-.04)*.37/.42
        gap=Vector((0,y,(lower_z+upper_z)/2));direction=Vector((1,0,0))
        assert all(t.ray_cast(gap-direction*.3,direction,.6)[0] is None for t in [lower_prong,upper_prong,tree('Motion Units supported lower mast'),tree('Motion Units tapered upper mast')]),'Actual clear fork gap'
    assert tree('Motion Units continuous sloping red base band').ray_cast(Vector((0,0,.5)),Vector((0,0,-1)))[0] is None,'Sloping band is one hollow closed ring'
    assert tree('Motion Units continuous middle ledge').ray_cast(Vector((0,0,1.4)),Vector((0,0,-1)))[0] is None,'Middle ledge is one hollow closed ring'
    for name,count in [('four corners middle ledge roof cap and seat',7),('five fields seven markers and two prongs',14),('one continuous sloping base band',1),('two seated dark front channels',2)]:
        assert components('Motion Units '+name)==count,('Actual source component count',name)
    names=[field['object'] for field in meta['rectangular_recesses']]
    assert sum('right brass field' in name for name in names)==4 and sum('upper front brass field' in name for name in names)==1
    assert sum('lower front dark channel' in name for name in names)==2 and sum('mast brass marker' in name for name in names)==3
    for chip in meta['physical_chips']:
        q=Vector(chip['point']);n=Vector(chip['normal']);hit=tree(chip['body']).ray_cast(q+n*.1,-n)[0];assert hit and .003<(q-hit).dot(n)<.012,'Actual shallow wear chip'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/149' and list(root['footprint'])==[2,2] and root['ground_level']==0
    assert all(o.parent==root and not o.animation_data for o in bpy.context.scene.objects if o.type=='MESH')
    allpoints=[p for n in result.values() for p in n['points']];assert abs(min(p.z for p in allpoints))<1e-5 and abs(max(p.z for p in allpoints)-3.226882)<.002
    used={mat for obj in bpy.context.scene.objects if obj.type=='MESH' for mat in obj.data.materials if mat}
    for material in used:
        p=material.node_tree.nodes.get('Principled BSDF');colour=p.inputs['Emission Color'].default_value;strength=p.inputs['Emission Strength'].default_value
        assert max(abs(colour[i]*strength) for i in range(3))<1e-7,'No source-supported timed emission in Motion Units'
        assert p.inputs['Alpha'].default_value==1 and p.inputs['Transmission Weight'].default_value==0,'Opaque source material roles'
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
    folder=ROOT/'sources/objects/mauna/motion-units';media=ROOT/'gallery/media/objects/mauna/motion-units';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_mauna_motion_units.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_mauna_motion_units.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/mn20-concept-review.json'
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
    assert error<1e-5;raw=(folder/'model.glb').read_bytes();gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values());assert tri<30000;assert not gltf.get('animations');assert len(gltf['materials'])==5;assert len(gltf['images'])==len(ni)==7;assert all('bufferView' in i for i in gltf['images']);renders.update(render('imported',media))
    s=bpy.context.scene
    s=bpy.context.scene
    for label,centre,scale in [('supported-mast-and-two-clear-brass-prongs-detail',Vector((0,.15,2.62)),1.65),('two-storeys-recesses-and-sloping-red-base-detail',Vector((0,0,1.02)),2.25)]:
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
    s.camera.data.ortho_scale=4.0;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=261,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,all_materials_opaque_nonemissive=True,attachment_witnesses=28,real_blind_fields=10,continuous_roof_prongs=2,fork_gap_rays=4,clips=[],renders=renders,scope='Saved native and independent GLB runtime geometry, roots, texture pixels and actual renders. Pixel review is a separate step. No client scale/state mapping, FPS certification or final user artistic acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('MN20_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
