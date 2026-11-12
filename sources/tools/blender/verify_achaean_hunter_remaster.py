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
import remaster_achaean_hunter as author
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
        for y,z in [(.6,.2),(.6,-.2),(1.0,.2),(1.0,-.2)]:
            hit,*_=scene.ray_cast(graph,transform((side*1.1,y,z)),Vector((-side,0,0)),distance=.65*factor)
            assert not hit,('upright crescent aft mouth obstructed',side,y,z);gaps+=1
        for t in [-.7,-.3,.3,.7]:
            point=author.crescent(side,t,.5)
            hit,where,normal,index,obj,matrix=scene.ray_cast(graph,transform(point+Vector((side*.4,0,0))),Vector((-side,0,0)),distance=.8*factor)
            assert hit and obj.name in {'UprightCrescentCore','RedCrescentSkins','SilverCrescentRims'},('missing upright crescent',side,t,obj.name if obj else None)
            rims+=1
    # The rejected revision had a separate third trailing spar.
    hit,*_=scene.ray_cast(graph,transform((0,1.4,1)),Vector((0,0,-1)),distance=2*factor)
    assert not hit,'independent trailing spar must be absent'
    core=bpy.data.objects['UprightCrescentCore'];points=[core.matrix_world@v.co for v in core.data.vertices]
    ratios=[]
    for side in [-1,1]:
        wing=[p for p in points if p.x*side>0]
        ratio=(max(p.z for p in wing)-min(p.z for p in wing))/(max(p.x for p in wing)-min(p.x for p in wing))
        assert ratio>8,('wing must be an upright thin plate',ratio);ratios.append(ratio)
    return dict(open_aft_mouth_samples=gaps,occupied_crescent_samples=rims,wing_height_to_thickness=ratios,independent_spar_absent=True)


def packed_maps():
    images=[i for i in bpy.data.images if i.type=='IMAGE']
    assert len(images)==4 and all(i.packed_file for i in images)
    assert sorted(tuple(i.size) for i in images)==[(1024,1024)]*2+[(2048,2048)]*2
    return 4


def main():
    out=author.OUT;media=author.MEDIA;meta=json.loads((out/'generation.json').read_text())
    before={k:sha(out/f'model.{k}') for k in ['blend','glb']}
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False)
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==author.ID and tuple(root.scale)==(1,1,1)
    assert root['calibrated_weapon_sockets']==0 and root['equipment_slots']==2
    native=snapshot();triangles=sum(r['triangles'] for r in native.values())
    assert triangles==meta['triangles']<60000 and len(native)==meta['mesh_batches']<=20
    packed_maps();cores={}
    for name in ['GreenPressureHull','UprightCrescentCore']:
        bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data)
        assert all(e.is_manifold for e in bm.edges) and abs(bm.calc_volume())>1e-6,name
        cores[name]=len(bm.faces);bm.free()
    native_witnesses=witnesses(meta);scene=bpy.context.scene
    author.shared.aim(scene,(1,-1,.85),margin=1.20)
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
    points=[v for row in imported.values() for v in row['points']]
    width_to_length=(max(v.x for v in points)-min(v.x for v in points))/(max(v.y for v in points)-min(v.y for v in points))
    assert .38<width_to_length<.60,('paired plates around axial hull',width_to_length)
    scene.render.filepath=str(media/'verified-imported.png');bpy.ops.render.render(write_still=True)
    for heading,direction in [(0,(1,-1,.65)),(4,(1,0,.65)),(8,(1,1,.65)),(12,(0,1,.65)),(20,(-1,0,.65))]:
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
    author.shared.aim(scene,(1,-1,.85),margin=1.20);scene.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    for path in media.glob('*.png'):path.write_bytes(clean_png(path.read_bytes()))
    assert before=={k:sha(out/f'model.{k}') for k in before}
    report=dict(id=author.ID,blender=bpy.app.version_string,blend_sha256=before['blend'],glb_sha256=before['glb'],
        generator_sha256=sha(Path(author.__file__)),shared_helper_sha256=sha(Path(author.shared.__file__)),verifier_sha256=sha(Path(__file__)),
        triangles=triangles,mesh_batches=len(native),materials=2,packed_maps=4,closed_core_meshes=cores,
        maximum_bidirectional_world_position_error=maximum,native_witnesses=native_witnesses,imported_witnesses=imported_witnesses,
        width_to_length=width_to_length,source_unchanged=True,
        renders={p.name:sha(p) for p in media.glob('*.png')},
        scope='Blender asset verification and author visual review; final user/client acceptance separate')
    (out/'runtime-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('HUNTER_VERIFIED',json.dumps(report))


if __name__=='__main__':main()
