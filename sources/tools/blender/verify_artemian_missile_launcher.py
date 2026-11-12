"""Verify saved AR16 and independent GLB import, including real review renders."""
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
    names=['hollow flared body and neck','single shallow hinged cap','moving cap hinge lug','fixed horizontal hinge axle','fixed hinge bearing 0','fixed hinge bearing 1','unequal pale upright 0','unequal pale upright 1','short joining rung','upper status rim','upper dark status seat','yellow square status core','lower recessed dark floor','lower opening rim','short foot mount 0','short foot mount 1'];required=['Missile Launcher '+n for n in names];assert set(result)==set(required) and len(result)==16
    body,cap,lug,axle,ear0,ear1,rail0,rail1,rung,status,seat,core,lowfloor,lowrim=[result[n] for n in required[:14]]
    pivot=bpy.data.objects['LaunchLidPivot'];rotation=pivot.matrix_world.to_3x3();assert abs(rotation[0][0]-math.cos(angle))<1e-5 and abs(rotation[0][2]-math.sin(angle))<1e-5,'Actual cap rotates about its horizontal axis'
    meta=json.loads((ROOT/'sources/objects/artemian/missile-launcher/model.json').read_text());origin=Vector(meta['hinge']['origin'])
    def world(p):return pivot.matrix_world@(Vector(p)-origin)
    def inside(tree,p):
        surface,normal,_,_=tree.find_nearest(p);return surface is not None and normal.dot(p-surface)<-1e-5
    pts=body['points'];width=max(p.x for p in pts)-min(p.x for p in pts);assert 1.51<width<1.53 and 1.39<max(p.z for p in pts)-min(p.z for p in pts)<1.40,'Flared body and taller narrow neck'
    q=world((-.48,0,1.48));assert inside(cap['tree'],q) and inside(lug['tree'],q),'Single cap attached to moving hinge lug'
    underside=cap['tree'].ray_cast(world((0,0,1.1)),rotation@Vector((0,0,1)))[0];edge=cap['tree'].ray_cast(world((.42,0,1.1)),rotation@Vector((0,0,1)))[0]
    assert underside and edge and abs((pivot.matrix_world.inverted()@underside+origin).z-1.575)<.0002 and (underside-edge).dot(rotation@Vector((0,0,1)))>.05,'Actual concave underside,not flat cap plate'
    q=origin;assert inside(lug['tree'],q) and inside(axle['tree'],q),'Rotating cap lug remains seated on fixed horizontal axle'
    for y,ear in [(-.19,ear0),(.19,ear1)]:
        q=Vector((-.52,y,1.44));assert inside(ear['tree'],q) and inside(axle['tree'],q),'Axle physically supported by bearing'
        q=Vector((-.39,y,1.35));assert inside(ear['tree'],q) and inside(body['tree'],q),'Bearing rooted in fixed neck'
    for i,(x,rail) in enumerate([(-.26,rail0),(-.10,rail1)]):
        mount=result['Missile Launcher short foot mount '+str(i)]
        q=Vector((x,-.67,.07));assert inside(body['tree'],q) and inside(mount['tree'],q),'Short foot mount rooted in flared foot'
        q=Vector((x,-.77,.07));assert inside(mount['tree'],q) and inside(rail['tree'],q),'Full-height upright rooted in foot mount'
        q=Vector((x,-.77,.615));assert inside(rung['tree'],q) and inside(rail['tree'],q),'Single joining rung meets both rails'
        for z in [.15,.30,.45,.60]:assert not inside(body['tree'],Vector((x,-.77,z))),'Source full-height pale rail remains visible outside flared shell'
    q=Vector((-.18,-.53,.615));assert inside(rung['tree'],q) and inside(body['tree'],q),'Joining rung also has real body contact'
    assert max(p.z for p in rail1['points'])-max(p.z for p in rail0['points'])>.16,'Source unequal upright heights'
    point=Vector(meta['status']['point']);normal=Vector(meta['status']['normal']);assert abs(math.degrees(math.atan2(point.y,point.x))+35)<.1,'Upper yellow fitting on right flank';q=point-normal*.004;assert inside(body['tree'],q) and inside(status['tree'],q)
    q=point+normal*.010;assert inside(status['tree'],q) and inside(seat['tree'],q);q=point+normal*.015;assert inside(seat['tree'],q) and inside(core['tree'],q),'Yellow square core seated in one upper dark circular fitting'
    point=Vector(meta['lower_port']['point']);normal=Vector(meta['lower_port']['normal']);u=normal.cross(Vector((0,0,1))).normalized();q=point-normal*.005+u*.065;assert inside(body['tree'],q) and inside(lowrim['tree'],q),'Lower rim seated in foot'
    hit=body['tree'].ray_cast(point+normal*.15,-normal)[0];assert hit and .029<(point-hit).dot(normal)<.031,'True lower round recess'
    q=point-normal*.031;assert inside(body['tree'],q) and inside(lowfloor['tree'],q),'Dark recessed floor physically mounted'
    evidence=meta['physical_dent'];point=Vector(evidence['point']);normal=Vector(evidence['normal']);hit=body['tree'].ray_cast(point+normal*.2,-normal)[0];assert hit and .0025<(point-hit).dot(normal)<.010,'Real shallow foot dent'
    for radius in [0,.28]:
        for i in range(8 if radius else 1):
            a=i*math.tau/8;q=Vector((radius*math.cos(a),radius*math.sin(a),3));hit=body['tree'].ray_cast(q,Vector((0,0,-1)))[0];assert hit and abs(hit.z-.12)<.0002,'Real shaft has dark solid floor,not concrete at neck height'
            if abs(angle)<1e-6:assert cap['tree'].ray_cast(q,Vector((0,0,-1)),1.58)[0] is not None,'Closed single cap covers aperture'
            if abs(angle+math.radians(110))<1e-6:assert cap['tree'].ray_cast(q,Vector((0,0,-1)),1.58)[0] is None,'Fully open single cap clears full authored aperture'
    assert min(p.z for p in cap['points'])>1.40,'Cap does not dive into body during hinge motion'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/122' and list(root['footprint'])==[2,2]
    for name in required:assert bpy.data.objects[name].parent==(pivot if name in required[1:3] else root)
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
    folder=ROOT/'sources/objects/artemian/missile-launcher';media=ROOT/'gallery/media/objects/artemian/missile-launcher';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text())
    assert meta['author']=='sources/tools/blender/remaster_artemian_missile_launcher.py' and meta['author_sha256']==sha(Path(__file__).with_name('remaster_artemian_missile_launcher.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/ar16-concept-review.json' and json.loads((ROOT/meta['concept_review']).read_bytes())['id']==meta['id']
    for ext,h in meta['binaries'].items():assert sha(folder/f'model.{ext}')==h
    frames=list(range(1,32,2))+[61];angles=[-math.radians(110)*(f-1)/30 if f<=31 else 0 for f in frames]
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False);native_samples=[]
    for frame,angle in zip(frames,angles):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();sample,images,root=snapshot(angle);native_samples.append(sample)
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();native,ni,nr=snapshot();renders=render('native',media)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'));error=0;pose_errors=[]
    for i,(frame,angle) in enumerate(zip(frames,angles)):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();sample,images,root=snapshot(angle);previous=native_samples[i];maximum=0
        for name,n in previous.items():
            other=sample[name];assert n['triangles']==other['triangles'] and n['materials']==other['materials'];assert max(abs(a-b) for a,b in zip(n['matrix'],other['matrix']))<1e-5
            maximum=max(maximum,max(other['tree'].find_nearest(p)[3] for p in n['points']),max(n['tree'].find_nearest(p)[3] for p in other['points']))
            if i and name not in ['Missile Launcher single shallow hinged cap','Missile Launcher moving cap hinge lug']:assert max((a-b).length for a,b in zip(n['points'],native_samples[0][name]['points']))<1e-7,'Neck,foot,rails,status and hinge bearings stay fixed'
        pose_errors.append(maximum);error=max(error,maximum)
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();imported,ii,ir=snapshot();assert nr==ir
    assert sorted((v['size'],v['pixels']) for v in ni.values())==sorted((v['size'],v['pixels']) for v in ii.values())
    assert error<1e-5;raw=(folder/'model.glb').read_bytes();gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values()) and tri<30000
    assert [clip['name'] for clip in gltf['animations']]==['LaunchFacilityCycle'];assert len(gltf['materials'])==4 and all('bufferView' in i for i in gltf['images']);renders.update(render('imported',media))
    s=bpy.context.scene
    for label,centre,scale in [('status-and-unequal-uprights-detail',Vector((.05,-.4,.7)),1.7),('lower-opening-and-used-metal-detail',Vector((.48,-.25,.32)),.85)]:
        direction=Vector((7,-12,8)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    for frame,label in [(16,'state-half-open'),(31,'state-open')]:
        s.frame_set(frame);centre=Vector((-.15,0,1.05));direction=Vector((7,-12,8)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=3.1;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    s.frame_set(1)
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
    report=dict(issue=260,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=['LaunchFacilityCycle'],pose_frames=frames,pose_surface_errors=pose_errors,renders=renders,scope='Actual saved-native/independent GLB17pose single-cap mechanism,attached hinge/bearings,fixed foot/neck/rails/status,real dark shaft/floor and open aperture,closed surfaces,texture pixels and renders. Hidden engineering,angle and timing authored;client state/scale/shaders and user acceptance separate.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('AR16_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
