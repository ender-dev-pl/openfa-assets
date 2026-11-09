"""Original curved leaves: fixed coaxial lift axes and a 90-degree opening."""
from pathlib import Path
import hashlib,json,math,sys
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
FOLDER=ROOT/'sources/docs/assets/bootstrap-3d/terran-refined/pb14'
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_png


def world_mesh(obj):
    assert all(m is not None for m in obj.data.materials),('Unbound material',obj.name)
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    points=[obj.matrix_world@v.co for v in mesh.vertices];faces=[list(f.vertices) for f in mesh.polygons];evaluated.to_mesh_clear()
    return points,BVHTree.FromPolygons(points,faces)


def check(offset):
    leaves=[bpy.data.objects[f'Iris curved leaf {i+1:02}'] for i in range(8)]
    assert not any(o.name.startswith(('Iris mount ','Iris lift carriage','Iris sliding guide','Iris drive wheel')) for o in bpy.context.scene.objects)
    shape_error=0
    for i,leaf in enumerate(leaves):
        theta=i*math.tau/8;angle=theta+math.pi/8;pivot=Vector((.82*math.cos(angle),.82*math.sin(angle),.64))
        tree=KDTree(len(leaf.data.vertices))
        for index,vertex in enumerate(leaf.data.vertices):tree.insert(vertex.co,index)
        tree.balance()
        for row in range(17):
            radius=.003+.88*row/16;sweep=.48*(1-radius/.883)
            for col in range(11):
                a=theta+sweep+(col/10)*(math.tau/8+.08)-.04;height=.64+.22*math.sqrt(max(0,1-(radius/.883)**2))+i*.0015
                shape_error=max(shape_error,tree.find(Vector((radius*math.cos(a),radius*math.sin(a),height))-pivot)[2])
    assert shape_error<1e-6
    ring=world_mesh(bpy.data.objects['Iris internal mounting ring'])[1]
    assert ring.overlap(world_mesh(bpy.data.objects['Launch well inner liner'])[1])
    anchors=0
    for i in range(8):
        assert ring.overlap(world_mesh(bpy.data.objects[f'Iris coax barrel {i+1:02}'])[1]);anchors+=1
    heights=[];openings=[];minimum_engagement=1;axis_error=0;mount_contacts=0;rod_contacts=0;actuator_contacts=0
    for frame in range(1,34):
        bpy.context.scene.frame_set(frame-offset);bpy.context.view_layer.update()
        for i,leaf in enumerate(leaves):
            angle=i*math.tau/8+math.pi/8;pivot=leaf.matrix_world.translation
            assert abs(math.hypot(pivot.x,pivot.y)-.82)<1e-6
            assert abs(pivot.x*math.sin(angle)-pivot.y*math.cos(angle))<1e-6
            assert .63999<=pivot.z<=.72001
            assert (leaf.matrix_world.to_3x3()@Vector((0,0,1))-Vector((0,0,1))).length<1e-6
            assert max(abs(s-1) for s in leaf.scale)<1e-6
            heights.append(pivot.z)
            if frame==17:assert abs(leaf.rotation_quaternion.angle-math.pi/2)<1e-6
            barrel=bpy.data.objects[f'Iris coax barrel {i+1:02}'];rod=bpy.data.objects[f'Iris coax rod {i+1:02}'];saddle=bpy.data.objects[f'Iris hinge axle {i+1:02}']
            for obj in [barrel,rod,saddle]:
                centre=obj.matrix_world.translation;error=math.hypot(centre.x-pivot.x,centre.y-pivot.y);axis_error=max(axis_error,error);assert error<1e-6
            bp,bt=world_mesh(barrel);rp,rt=world_mesh(rod);sp,st=world_mesh(saddle);lp,lt=world_mesh(leaf)
            engagement=min(max(p.z for p in bp),max(p.z for p in rp))-max(min(p.z for p in bp),min(p.z for p in rp))
            minimum_engagement=min(minimum_engagement,engagement);assert engagement>.0649
            assert bt.overlap(rt);actuator_contacts+=1
            assert rt.overlap(st);rod_contacts+=1
            assert st.overlap(lt);mount_contacts+=1
        if frame in [1,5,9,13,17]:
            deps=bpy.context.evaluated_depsgraph_get();clear=0;samples=0
            for x in range(-16,17):
                for y in range(-16,17):
                    px,py=x*.05,y*.05
                    if math.hypot(px,py)>.44 or (x==0 and y==0):continue
                    hit,*_=bpy.context.scene.ray_cast(deps,Vector((px,py,1.1)),Vector((0,0,-1)),distance=.6)
                    clear+=not hit;samples+=1
            openings.append(dict(frame=frame,clear=clear,samples=samples))
    assert openings[0]['clear']==0 and openings[-1]['clear']==openings[-1]['samples']
    assert all(a['clear']<b['clear'] for a,b in zip(openings,openings[1:])),openings
    return dict(blades=8,frames=33,original_shape_error=shape_error,turn_degrees=90,radial_travel=0,lift=max(heights)-min(heights),folding=False,scaling=False,opening_samples=openings,support=dict(mounting_ring_anchored=True,anchored_actuators=anchors,maximum_axis_error=axis_error,minimum_piston_engagement=minimum_engagement,leaf_bearing_contacts=mount_contacts,rod_bearing_contacts=rod_contacts,actuator_contacts=actuator_contacts))


def main():
    bpy.ops.wm.open_mainfile(filepath=str(FOLDER/'model.blend'),load_ui=False,use_scripts=False);native=check(0)
    for obj in list(bpy.context.scene.objects):
        if obj.type in {'MESH','EMPTY'}:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(FOLDER/'model.glb'));bpy.context.scene.render.fps=16;imported=check(1)
    scene=bpy.context.scene;camera=scene.camera;target=Vector((.31,-.76,.65));direction=Vector((2,-4,3.8))
    camera.location=target+direction;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=1.5
    scene.frame_set(16);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA'
    detail=ROOT/'gallery/media/docs/assets/bootstrap-3d/terran-refined/pb14/mechanism-detail.png';scene.render.filepath=str(detail);bpy.ops.render.render(write_still=True);detail.write_bytes(clean_png(detail.read_bytes()))
    report=dict(detail_render=dict(path=detail.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(detail.read_bytes()).hexdigest()),native=native,imported=imported,binaries={suffix:hashlib.sha256((FOLDER/('model.'+suffix)).read_bytes()).hexdigest() for suffix in ['blend','glb']},verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (FOLDER/'diaphragm-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('COAXIAL_90_VERIFIED',json.dumps(report))


if __name__=='__main__':main()
