"""Verify the cleaned saved source and independent GLB, not just a successful export."""
from pathlib import Path
import hashlib
import json
import sys
import bpy
import bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree

sys.path.insert(0,str(Path(__file__).parent))
import remaster_achaean_fighter as author
sys.path.insert(0,str(author.ROOT/'tools'))
from publication_support import clean_png


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    bpy.context.view_layer.update();result={}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        assert obj.data.uv_layers and len(obj.data.materials)==1,obj.name
        result[obj.name]=dict(points=[obj.matrix_world@v.co for v in obj.data.vertices],
                             triangles=sum(len(p.vertices)-2 for p in obj.data.polygons))
    return result


def witnesses(meta):
    scene=bpy.context.scene;graph=bpy.context.evaluated_depsgraph_get()
    factor=meta['normalization_factor'];centre=Vector(meta['normalization_centre'])
    transform=lambda p:(Vector(p)-centre)*factor
    gaps=rims=0
    for side in [-1,1]:
        for y,z in [(-1.8,.2),(-1.8,-.2),(-1.2,0),(-.5,0)]:
            hit,*_=scene.ray_cast(graph,transform((side*1.3,y,z)),Vector((-side,0,0)),distance=.7*factor)
            assert not hit,('forward crescent mouth obstructed',side,y,z);gaps+=1
        for t in [-.72,-.40,.40,.72]:
            point=author.crescent(side,t,.84)
            hit,where,normal,index,obj,matrix=scene.ray_cast(graph,transform(point+Vector((side*.4,0,0))),Vector((-side,0,0)),distance=.8*factor)
            assert hit and obj.name in {'CrescentStructure','SilverCrescentRims','CrimsonCrescentInsets'},('missing rim',side,t)
            rims+=1
    return dict(open_forward_mouth_samples=gaps,occupied_rim_samples=rims)


def packed_maps():
    images=[i for i in bpy.data.images if i.type=='IMAGE']
    assert len(images)==2 and all(i.packed_file and tuple(i.size)==(2048,2048) for i in images)
    return 2


def main():
    out=author.OUT;media=author.MEDIA;meta=json.loads((out/'generation.json').read_text())
    before={k:sha(out/f'model.{k}') for k in ['blend','glb']}
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False)
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==author.ID and tuple(root.scale)==(1,1,1)
    assert root['calibrated_weapon_sockets']==0 and root['equipment_slots']==4
    native=snapshot();triangles=sum(r['triangles'] for r in native.values())
    assert triangles==meta['triangles']<60000 and len(native)==meta['mesh_batches']<=16
    packed_maps();cores={}
    for name in ['PressureHull','CrescentStructure']:
        bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data)
        assert all(e.is_manifold for e in bm.edges) and abs(bm.calc_volume())>1e-6,name
        cores[name]=len(bm.faces);bm.free()
    native_witnesses=witnesses(meta);scene=bpy.context.scene
    author.shared.aim(scene,(1,-1,.55),margin=1.20)
    scene.render.filepath=str(media/'verified-native.png');bpy.ops.render.render(write_still=True)
    for obj in list(scene.objects):
        if obj.type in {'MESH','EMPTY'}:bpy.data.objects.remove(obj,do_unlink=True)
    for collection in [bpy.data.meshes,bpy.data.materials,bpy.data.images]:
        for item in list(collection):
            if item.users==0:collection.remove(item)
    bpy.ops.import_scene.gltf(filepath=str(out/'model.glb'));imported=snapshot();assert native.keys()==imported.keys()
    maximum=0
    for name in native:
        assert native[name]['triangles']==imported[name]['triangles']
        for first,second in [(native[name]['points'],imported[name]['points']),(imported[name]['points'],native[name]['points'])]:
            tree=KDTree(len(first))
            for i,p in enumerate(first):tree.insert(p,i)
            tree.balance();maximum=max(maximum,max(tree.find(p)[2] for p in second))
    assert maximum<1e-5;packed_maps();imported_witnesses=witnesses(meta)
    factor=meta['normalization_factor'];hull=imported['PressureHull']['points'];wing=imported['CrescentStructure']['points']
    fullness=(max(v.z for v in hull)-min(v.z for v in hull))/(max(v.z for v in wing)-min(v.z for v in wing))
    assert .45<fullness<.60,('end-on hull fullness versus crescents',fullness)
    points=[v for row in imported.values() for v in row['points']]
    width_to_length=(max(v.x for v in points)-min(v.x for v in points))/(max(v.y for v in points)-min(v.y for v in points))
    assert .48<width_to_length<.55,('compact spacing from AC1C end/side views',width_to_length)
    scene.render.filepath=str(media/'verified-imported.png');bpy.ops.render.render(write_still=True)
    for heading,direction in [(0,(1,-1,.14)),(4,(1,0,.14)),(8,(1,1,.14)),(12,(0,1,.14)),(20,(-1,0,.14))]:
        author.shared.aim(scene,direction,margin=1.20)
        scene.render.filepath=str(media/f'verified-heading-{heading}.png');bpy.ops.render.render(write_still=True)
    for obj in scene.objects:
        if obj.type!='MESH':continue
        mat=bpy.data.materials.new('Actual imported technical '+obj.name);mat.use_nodes=True
        tree=mat.node_tree;tree.nodes.clear();wire=tree.nodes.new('ShaderNodeWireframe');wire.use_pixel_size=True;wire.inputs['Size'].default_value=.6
        mix=tree.nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(0,0,0,1)
        mix.inputs[2].default_value=(.7,.03,.02,1) if 'Crescent' in obj.name else (.015,.58,.035,1)
        tree.links.new(wire.outputs[0],mix.inputs[0]);emission=tree.nodes.new('ShaderNodeEmission');tree.links.new(mix.outputs[0],emission.inputs[0])
        output=tree.nodes.new('ShaderNodeOutputMaterial');tree.links.new(emission.outputs[0],output.inputs[0]);obj.data.materials.clear();obj.data.materials.append(mat)
    author.shared.aim(scene,(1,-1,.55),margin=1.20);scene.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    for path in media.glob('*.png'):path.write_bytes(clean_png(path.read_bytes()))
    assert before=={k:sha(out/f'model.{k}') for k in before}
    report=dict(id=author.ID,blender=bpy.app.version_string,blend_sha256=before['blend'],glb_sha256=before['glb'],
        generator_sha256=sha(Path(author.__file__)),shared_helper_sha256=sha(Path(author.shared.__file__)),verifier_sha256=sha(Path(__file__)),
        triangles=triangles,mesh_batches=len(native),materials=1,packed_maps=2,closed_core_meshes=cores,
        maximum_bidirectional_world_position_error=maximum,native_witnesses=native_witnesses,imported_witnesses=imported_witnesses,
        end_on_hull_to_crescent_height=fullness,width_to_length=width_to_length,source_unchanged=True,
        renders={p.name:sha(p) for p in media.glob('*.png')},
        scope='Blender asset verification and author visual review; final user/client acceptance separate')
    (out/'runtime-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('FIGHTER_VERIFIED',json.dumps(report))


if __name__=='__main__':main()
