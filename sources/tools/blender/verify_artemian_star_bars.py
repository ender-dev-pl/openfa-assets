"""Verify saved AR15 and independent GLB import, including real review renders."""
import hashlib,json,math,struct,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_png

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(angle=0):
    result={};deps=bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();points=[obj.matrix_world@v.co for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons]
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.free()
        assert obj.data.uv_layers.active and all(math.isfinite(v) for p in points for v in p)
        result[obj.name]=dict(points=points,tree=BVHTree.FromPolygons(points,faces),triangles=len(mesh.loop_triangles),matrix=[float(v) for row in obj.matrix_world for v in row],materials=sorted(m.name for m in obj.data.materials if m));evaluated.to_mesh_clear()
    required=['Star Bars fixed rounded bowl','Star Bars rotating green head','Star Bars tapered collared emitter with blind bore','Star Bars short stem green collar','Star Bars narrow pale vertical stem']+['Star Bars fixed front port '+part+' '+str(i) for i in range(2) for part in ['rim','dark']]
    # Dark names read naturally while preserving explicit canonical identities.
    required=required[:5]+['Star Bars fixed front port rim '+str(i) for i in range(2)]+['Star Bars fixed dark front port '+str(i) for i in range(2)]
    assert set(result)==set(required) and len(result)==9
    body=result[required[0]];head=result[required[1]];tube=result[required[2]];collar=result[required[3]];stem=result[required[4]]
    yaw=bpy.data.objects['StarBarsYaw'];rotation=yaw.matrix_world.to_3x3();assert abs(rotation[0][0]-math.cos(angle))<1e-5 and abs(rotation[1][0]-math.sin(angle))<1e-5,'Actual azimuth follows clip at sampled heading'
    def world(v):return yaw.matrix_world@Vector(v)
    def inside(tree,p):
        surface,normal,_,_=tree.find_nearest(p);return surface is not None and normal.dot(p-surface)<-1e-5
    pts=body['points'];width=max(p.x for p in pts)-min(p.x for p in pts);depth=max(p.y for p in pts)-min(p.y for p in pts)
    assert 1.59<width<1.61 and abs(width-depth)<.005,'Circular squat fixed bowl'
    q=Vector((0,0,.505));assert inside(body['tree'],q) and inside(head['tree'],q),'Head seated in fixed circular bearing'
    for component in [collar,stem]:
        for a in [0,1]:assert abs(max(p[a] for p in component['points'])+min(p[a] for p in component['points']))<1e-5,'Own sprite stem remains on yaw axis through all headings'
    meta=json.loads((ROOT/'sources/objects/artemian/star-bars/model.json').read_text());emitter=meta['emitter'];origin=Vector(emitter['origin']);direction=Vector(emitter['direction']);q=world(origin+direction*.02);assert inside(head['tree'],q) and inside(tube['tree'],q),'Emitter physically rooted in rotating head'
    q=world((0,0,1.00));assert inside(head['tree'],q) and inside(collar['tree'],q),'Stem collar rooted in head';q=world((0,0,1.12));assert inside(collar['tree'],q) and inside(stem['tree'],q),'Pale stem rooted in green collar'
    floor=tube['tree'].ray_cast(world(origin+direction*.99),-(rotation@direction))[0];assert floor and abs((yaw.matrix_world.inverted()@floor-origin).dot(direction)-.82)<.0002,'Emitter has actual recessed blind bore and a solid floor'
    for i,port in enumerate(meta['fixed_ports']):
        point=Vector(port['point']);normal=Vector(port['normal']);u=normal.cross(Vector((0,0,1))).normalized();rim=result['Star Bars fixed front port rim '+str(i)];dark=result['Star Bars fixed dark front port '+str(i)]
        q=point-normal*.005+u*.052;assert inside(body['tree'],q) and inside(rim['tree'],q),'Fixed port rim mounted in fixed bowl'
        q=point+u*.044;assert inside(rim['tree'],q) and inside(dark['tree'],q),'Dark port inset seated inside rim'
        assert abs(math.degrees(math.atan2(point.y,point.x))-[-57,-31][i])<.1,'Two front-right fixed points remain aligned on bowl'
    evidence=meta['physical_dent'];point=Vector(evidence['point']);normal=Vector(evidence['normal']);hit=head['tree'].ray_cast(world(point+normal*.2),-(rotation@normal))[0];assert hit and .0025<(world(point)-hit).dot(rotation@normal)<.010,'Actual head dent survives all headings'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/121' and list(root['footprint'])==[2,2]
    for name in required[:5]:assert bpy.data.objects[name].parent==(root if name==required[0] else yaw)
    for name in required[5:]:assert bpy.data.objects[name].parent==root
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
    for view,direction in [('front-quarter',(7,-12,8)),('front',(0,-16,9)),('rear-quarter',(7,12,9))]:
        v=Vector(direction).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];midpoint=Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0));s.camera.location+=s.camera.rotation_euler.to_matrix()@midpoint;s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;p=media/f'{label}-{view}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));renders[p.name]=sha(p)
    return renders

def main():
    folder=ROOT/'sources/objects/artemian/star-bars';media=ROOT/'gallery/media/objects/artemian/star-bars';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text())
    assert meta['author']=='sources/tools/blender/remaster_artemian_star_bars.py' and meta['author_sha256']==sha(Path(__file__).with_name('remaster_artemian_star_bars.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/ar15-concept-review.json' and json.loads((ROOT/meta['concept_review']).read_bytes())['id']==meta['id']
    for ext,h in meta['binaries'].items():assert sha(folder/f'model.{ext}')==h
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False);native_samples=[]
    for i in range(17):
        bpy.context.scene.frame_set(1+6*i);bpy.context.view_layer.update();sample,images,root=snapshot(i*math.tau/16);native_samples.append(sample)
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();native,ni,nr=snapshot();renders=render('native',media)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'));error=0;heading_errors=[]
    for i in range(17):
        bpy.context.scene.frame_set(1+6*i);bpy.context.view_layer.update();sample,images,root=snapshot(i*math.tau/16);previous=native_samples[i];maximum=0
        for name,n in previous.items():
            other=sample[name];assert n['triangles']==other['triangles'] and n['materials']==other['materials'];assert max(abs(a-b) for a,b in zip(n['matrix'],other['matrix']))<1e-5
            maximum=max(maximum,max(other['tree'].find_nearest(p)[3] for p in n['points']),max(n['tree'].find_nearest(p)[3] for p in other['points']))
            if i and name.startswith('Star Bars fixed'):assert max((a-b).length for a,b in zip(n['points'],native_samples[0][name]['points']))<1e-7,'Bowl and both points stay fixed during whole animation'
        heading_errors.append(maximum);error=max(error,maximum)
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();imported,ii,ir=snapshot();assert nr==ir
    assert sorted((v['size'],v['pixels']) for v in ni.values())==sorted((v['size'],v['pixels']) for v in ii.values())
    assert error<1e-5;raw=(folder/'model.glb').read_bytes();gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values()) and tri<30000
    assert [clip['name'] for clip in gltf['animations']]==['StarBarsAzimuth'];assert len(gltf['materials'])==3 and all('bufferView' in i for i in gltf['images']);renders.update(render('imported',media))
    s=bpy.context.scene
    for label,centre,scale in [('emitter-stem-and-bearing-detail',Vector((.1,.1,1.05)),1.9),('fixed-bowl-paired-points-detail',Vector((.15,-.4,.34)),1.15)]:
        direction=Vector((7,-12,8)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
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
    direction=Vector((12,-8,10)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    s.camera.data.ortho_scale=3.0;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=260,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=['StarBarsAzimuth'],heading_samples=17,heading_surface_errors=heading_errors,renders=renders,scope='Saved native and independent GLB actual17heading animation samples,closed surfaces,fixed bowl/head joints,blind bore,texture pixels and actual renders. Four-second duration authored;client aiming/timing/scale/shaders and final user artistic acceptance separate.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('AR15_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
