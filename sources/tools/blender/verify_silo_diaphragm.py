"""Original curved leaves and original drop/50-degree motion; black shaft floor."""
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
    assert not any(o.name.startswith(('Iris coax','Iris internal mounting')) for o in bpy.context.scene.objects)
    heights=[];openings=[];pose_error=0
    for frame in range(1,34):
        bpy.context.scene.frame_set(frame-offset);bpy.context.view_layer.update()
        drop=.20*min(1,(frame-1)/4,(33-frame)/4)
        turn=50*max(0,min((frame-5)/12,(29-frame)/12))
        for i,leaf in enumerate(leaves):
            angle=i*math.tau/8+math.pi/8;pivot=leaf.matrix_world.translation
            expected=Vector((.82*math.cos(angle),.82*math.sin(angle),.64-drop))
            pose_error=max(pose_error,(pivot-expected).length,(leaf.matrix_world.to_3x3()@Vector((1,0,0))-Vector((math.cos(math.radians(turn)),math.sin(math.radians(turn)),0))).length)
            assert (leaf.matrix_world.to_3x3()@Vector((0,0,1))-Vector((0,0,1))).length<1e-6
            assert max(abs(value-1) for value in leaf.scale)<1e-6
            heights.append(pivot.z)
        if frame in [1,5,9,13,17]:
            deps=bpy.context.evaluated_depsgraph_get();clear=0;samples=0
            for x in range(-7,8):
                for y in range(-7,8):
                    px,py=x*.05,y*.05
                    if math.hypot(px,py)>.33 or (x==0 and y==0):continue
                    hit,*_=bpy.context.scene.ray_cast(deps,Vector((px,py,1.1)),Vector((0,0,-1)),distance=.9)
                    clear+=not hit;samples+=1
            openings.append(dict(frame=frame,clear=clear,samples=samples))
    assert pose_error<1e-6
    assert openings[0]['clear']==0 and openings[-1]['clear']==openings[-1]['samples']
    assert all(a['clear']<=b['clear'] for a,b in zip(openings,openings[1:])),openings
    floor=bpy.data.objects['Launch well bottom'];points,_=world_mesh(floor)
    assert max(v.z for v in points)<-3.1
    shader=next(n for n in floor.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    assert max(shader.inputs['Base Color'].default_value[:3])==0
    assert shader.inputs['Metallic'].default_value==0
    bpy.context.scene.frame_set(17-offset);deps=bpy.context.evaluated_depsgraph_get()
    for radius in [0,.1,.2,.3,.33]:
        for i in range(32):
            origin=Vector((radius*math.cos(math.tau*i/32),radius*math.sin(math.tau*i/32),1.1))
            hit,position,normal,index,obj,matrix=bpy.context.scene.ray_cast(deps,origin,Vector((0,0,-1)),distance=5)
            assert hit and obj.name=='Launch well bottom' and position.z<-3.1,(obj.name,position)
    return dict(blades=8,frames=33,original_shape_error=shape_error,maximum_original_pose_error=pose_error,turn_degrees=50,radial_travel=0,drop=max(heights)-min(heights),folding=False,scaling=False,opening_samples=openings,floor_black=True,floor_below_payload=True,top_view_floor_rays=160)



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
    (FOLDER/'diaphragm-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('ORIGINAL_IRIS_TUBE_VERIFIED',json.dumps(report))


if __name__=='__main__':main()
