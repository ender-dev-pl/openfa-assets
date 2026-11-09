"""Verify the preserved eight-leaf shape and lifted radial opening."""
from pathlib import Path
import hashlib
import json
import math
import sys
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
FOLDER=ROOT/'sources/docs/assets/bootstrap-3d/terran-refined/pb14'
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_png


def world_mesh(obj):
    assert all(material is not None for material in obj.data.materials),('Unbound material',obj.name)
    deps=bpy.context.evaluated_depsgraph_get();evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh()
    points=[obj.matrix_world@v.co for v in mesh.vertices];faces=[list(f.vertices) for f in mesh.polygons];evaluated.to_mesh_clear()
    return points,BVHTree.FromPolygons(points,faces)


def support_proof(leaves):
    bunker=world_mesh(bpy.data.objects['Silo flared bunker'])[1];anchors=0
    for i in range(8):
        foot=world_mesh(bpy.data.objects[f'Iris mount body {i+1:02}'])[1]
        assert bunker.overlap(foot),('Unanchored foot',i);anchors+=1
    return anchors


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
    heights=[];openings=[];minimum_overlap=1;minimum_stroke_overlap=1;mount_contacts=0;actuator_contacts=0
    anchors=support_proof(leaves)
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
            radial=Vector((math.cos(angle),math.sin(angle),0))
            head=bpy.data.objects[f'Iris lift carriage {i+1:02}']
            rack=bpy.data.objects[f'Iris sliding guide {i+1:02}']
            body=bpy.data.objects[f'Iris lift carriage body {i+1:02}']
            foot=bpy.data.objects[f'Iris mount body {i+1:02}']
            axle=bpy.data.objects[f'Iris hinge axle {i+1:02}']
            rp,rt=world_mesh(rack);hp,ht=world_mesh(body)
            rmin=min(p.dot(radial) for p in rp);rmax=max(p.dot(radial) for p in rp)
            hmin=min(p.dot(radial) for p in hp);hmax=max(p.dot(radial) for p in hp)
            overlap=min(rmax,hmax)-max(rmin,hmin);assert overlap>.0999
            minimum_overlap=min(minimum_overlap,overlap)
            assert abs((min(p.z for p in rp)+max(p.z for p in rp))/2-head.matrix_world.translation.z+.010)<1e-6
            rod_bottom=head.matrix_world.translation.z-.18;rod_top=head.matrix_world.translation.z-.045
            engagement=min(rod_top,.585)-max(rod_bottom,.455);assert engagement>.0699
            minimum_stroke_overlap=min(minimum_stroke_overlap,engagement)
            assert ht.overlap(world_mesh(foot)[1]),('Disconnected lift piston',frame,i);actuator_contacts+=1
            assert world_mesh(axle)[1].overlap(world_mesh(leaf)[1]),('Disconnected leaf bearing',frame,i);mount_contacts+=1
            ap,at=world_mesh(axle)
            assert min(p.z for p in ap)<max(p.z for p in rp),('Bearing floats above rack',frame,i)

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
    return dict(blades=8,frames=33,original_shape_error=shape_error,turn_degrees=50,radial_travel=.60,lift=max(heights)-min(heights),folding=False,scaling=False,opening_samples=openings,support=dict(anchored_feet=anchors,minimum_rack_engagement=minimum_overlap,minimum_piston_engagement=minimum_stroke_overlap,leaf_bearing_contacts=mount_contacts,actuator_contacts=actuator_contacts))


def main():
    bpy.ops.wm.open_mainfile(filepath=str(FOLDER/'model.blend'),load_ui=False,use_scripts=False);native=check(0)
    for obj in list(bpy.context.scene.objects):
        if obj.type in {'MESH','EMPTY'}:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(FOLDER/'model.glb'));bpy.context.scene.render.fps=16;imported=check(1)
    scene=bpy.context.scene;camera=scene.camera;target=Vector((.42,-1.0,.65));direction=Vector((2.8,-3.8,2.0))
    camera.location=target+direction;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=1.65
    scene.frame_set(16);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA'
    detail=ROOT/'gallery/media/docs/assets/bootstrap-3d/terran-refined/pb14/mechanism-detail.png';scene.render.filepath=str(detail);bpy.ops.render.render(write_still=True);detail.write_bytes(clean_png(detail.read_bytes()))
    report=dict(detail_render=dict(path=detail.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(detail.read_bytes()).hexdigest()),native=native,imported=imported,binaries={suffix:hashlib.sha256((FOLDER/('model.'+suffix)).read_bytes()).hexdigest() for suffix in ['blend','glb']},verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (FOLDER/'diaphragm-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('ORIGINAL_LEAF_MOTION_VERIFIED',json.dumps(report))


if __name__=='__main__':main()
