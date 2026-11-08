"""Verify the preserved eight-leaf shape and lifted radial opening."""
from pathlib import Path
import hashlib
import json
import math
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[3]
FOLDER=ROOT/'sources/docs/assets/bootstrap-3d/terran-refined/pb14'


def check(offset):
    leaves=[bpy.data.objects[f'Iris curved leaf {i+1:02}'] for i in range(8)]
    shape_error=0
    for i,leaf in enumerate(leaves):
        theta=i*math.tau/8;angle=theta+math.pi/8;pivot=Vector((.82*math.cos(angle),.82*math.sin(angle),.64))
        tree=KDTree(len(leaf.data.vertices))
        for index,vertex in enumerate(leaf.data.vertices):tree.insert(vertex.co,index)
        tree.balance()
        for row in range(17):
            radius=.003+.88*row/16;sweep=.48*(1-radius/.883)
            for col in range(11):
                a=theta+sweep+(col/10)*(math.tau/8+.08)-.04
                height=.64+.22*math.sqrt(max(0,1-(radius/.883)**2))+i*.0015
                point=Vector((radius*math.cos(a),radius*math.sin(a),height))-pivot
                shape_error=max(shape_error,tree.find(point)[2])
    assert shape_error<1e-6
    heights=[];openings=[]
    for frame in range(1,34):
        bpy.context.scene.frame_set(frame-offset);bpy.context.view_layer.update()
        for i,leaf in enumerate(leaves):
            angle=i*math.tau/8+math.pi/8;pivot=leaf.matrix_world.translation;radius=math.hypot(pivot.x,pivot.y)
            assert .81999<=radius<=1.42001
            assert abs(pivot.x*math.sin(angle)-pivot.y*math.cos(angle))<1e-6
            assert .63999<=pivot.z<=.72001
            assert (leaf.matrix_world.to_3x3()@Vector((0,0,1))-Vector((0,0,1))).length<1e-6
            assert max(abs(s-1) for s in leaf.scale)<1e-6
            heights.append(pivot.z)
            if frame==17:
                assert abs(radius-1.42)<1e-6 and abs(pivot.z-.72)<1e-6
                assert abs(leaf.rotation_quaternion.angle-math.radians(50))<1e-6
        if frame in [1,5,9,13,17]:
            deps=bpy.context.evaluated_depsgraph_get();clear=0;samples=0
            for x in range(-16,17):
                for y in range(-16,17):
                    px,py=x*.05,y*.05
                    if math.hypot(px,py)>.82 or (x==0 and y==0):continue
                    hit,*_=bpy.context.scene.ray_cast(deps,Vector((px,py,1.1)),Vector((0,0,-1)),distance=.6)
                    clear+=not hit;samples+=1
            openings.append(dict(frame=frame,clear=clear,samples=samples))
    assert openings[0]['clear']==0 and openings[-1]['clear']==openings[-1]['samples']
    assert all(a['clear']<b['clear'] for a,b in zip(openings,openings[1:])),openings
    return dict(blades=8,frames=33,original_shape_error=shape_error,turn_degrees=50,radial_travel=.60,lift=max(heights)-min(heights),folding=False,scaling=False,opening_samples=openings)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(FOLDER/'model.blend'),load_ui=False,use_scripts=False);native=check(0)
    for obj in list(bpy.context.scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(FOLDER/'model.glb'));bpy.context.scene.render.fps=16;imported=check(1)
    report=dict(native=native,imported=imported,binaries={suffix:hashlib.sha256((FOLDER/('model.'+suffix)).read_bytes()).hexdigest() for suffix in ['blend','glb']},verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (FOLDER/'diaphragm-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('ORIGINAL_LEAF_MOTION_VERIFIED',json.dumps(report))


if __name__=='__main__':main()
