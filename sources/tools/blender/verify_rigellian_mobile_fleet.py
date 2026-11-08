"""Actual saved-native reopen, independent GLB import, geometry and render checks."""
import hashlib
import json
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree

sys.path.insert(0,str(Path(__file__).parent))
import build_rigellian_mobile_fleet as author
ROOT=author.ROOT
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_png


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    bpy.context.view_layer.update();result={}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        assert obj.data.uv_layers,(obj.name,'missing UV')
        assert len(obj.data.materials)==1,(obj.name,'material count')
        assert all(v.co.length<100 for v in obj.data.vertices),(obj.name,'invalid coordinates')
        points=[obj.matrix_world@v.co for v in obj.data.vertices]
        result[obj.name]={'points':points,'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons)}
    return result


def geometry_error(first,second):
    assert first.keys()==second.keys(),(first.keys(),second.keys())
    maximum=0
    for name in first:
        assert first[name]['triangles']==second[name]['triangles'],(name,'triangulation changed')
        for a,b in [(first[name]['points'],second[name]['points']),(second[name]['points'],first[name]['points'])]:
            tree=KDTree(len(a))
            for i,point in enumerate(a):tree.insert(point,i)
            tree.balance();maximum=max(maximum,max(tree.find(p)[2] for p in b))
    assert maximum<.00001,maximum
    return maximum


def drive_visibility(scene,length):
    """Local exit rays must hit blue throat faces, not an overlapping pod/core."""
    bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();checks=0
    def blue(obj,face):
        uv=obj.data.uv_layers.active.data
        u=sum(uv[i].uv.x for i in face.loop_indices)/len(face.loop_indices)
        v=sum(uv[i].uv.y for i in face.loop_indices)/len(face.loop_indices)
        return int(u*4)+4*int((1-v)*4)==6
    for obj in scene.objects:
        if obj.type!='MESH' or obj.name!='DriveAssemblies':continue
        for face in obj.data.polygons:
            normal=obj.matrix_world.to_3x3()@face.normal
            if abs(normal.y)<.999 or not blue(obj,face):continue
            p=obj.matrix_world@face.center
            hit,location,normal,index,other,matrix=scene.ray_cast(graph,p+Vector((0,length*.025,0)),Vector((0,-1,0)),distance=length*.05)
            assert hit and other.name=='DriveAssemblies' and blue(other,other.data.polygons[index]),('covered drive throat',p,other.name if hit else None)
            checks+=1
    assert checks>0,'no blue drive exit caps found'
    return checks


def verify(ship):
    out=ROOT/ship['canonical_directory'];media=ROOT/'gallery/media/objects/rigellian'/ship['slug']
    before={ext:sha(out/f'model.{ext}') for ext in ['blend','glb']}
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;root=bpy.data.objects['PlacementRoot']
    assert root['catalogue_id']==ship['id']
    assert tuple(root.scale)==(1,1,1)
    native=snapshot();assert len(native)<=24
    native_exit_checks=drive_visibility(scene,ship['authoring_length_units'])
    total=sum(row['triangles'] for row in native.values());assert total<=110000
    images=[im for im in bpy.data.images if im.type=='IMAGE']
    assert len(images)==3 and all(im.packed_file for im in images)
    assert all(tuple(im.size)==(2048,2048) for im in images)
    core=bpy.data.objects['PressureHull'];bm=bmesh.new();bm.from_mesh(core.data)
    assert all(edge.is_manifold for edge in bm.edges),'pressure hull must be closed'
    bm.free()
    author.aim(scene,(1.15,-.8,.65),ship['authoring_length_units'])
    scene.render.filepath=str(media/'verified-native.png');bpy.ops.render.render(write_still=True)
    for obj in list(scene.objects):
        if obj.type=='MESH' or obj==root:bpy.data.objects.remove(obj,do_unlink=True)
    for collection in [bpy.data.meshes,bpy.data.materials,bpy.data.images]:
        for item in list(collection):
            if item.users==0:collection.remove(item)
    bpy.ops.import_scene.gltf(filepath=str(out/'model.glb'));imported=snapshot()
    imported_exit_checks=drive_visibility(scene,ship['authoring_length_units'])
    error=geometry_error(native,imported)
    images=[im for im in bpy.data.images if im.type=='IMAGE']
    assert len(images)==3 and all(im.packed_file for im in images)
    scene.render.filepath=str(media/'verified-imported.png');bpy.ops.render.render(write_still=True)
    for png in media.glob('*.png'):png.write_bytes(clean_png(png.read_bytes()))
    assert before=={ext:sha(out/f'model.{ext}') for ext in before},'verifier changed source'
    report={'id':ship['id'],'blender':bpy.app.version_string,'triangles':total,'mesh_batches':len(native),
            'blend_sha256':before['blend'],'glb_sha256':before['glb'],
            'maximum_bidirectional_position_error':error,'closed_pressure_hull':True,
            'packed_maps_native_and_imported':3,'source_unchanged':True,
            'unobstructed_drive_exit_ray_checks_native':native_exit_checks,
            'unobstructed_drive_exit_ray_checks_imported':imported_exit_checks,
            'generator_sha256':sha(Path(author.__file__)),'verifier_sha256':sha(Path(__file__)),
            'scope':'Saved native reopen and independent portable GLB; game runtime and weapons sockets not accepted',
            'renders':{png.name:sha(png) for png in media.glob('*.png')}}
    (out/'runtime-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RIGELLIAN_VERIFIED '+json.dumps(report),flush=True)


def fleet_comparison():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for index,ship in enumerate(author.STYLE['ships']):
        bpy.ops.import_scene.gltf(filepath=str(ROOT/ship['canonical_directory']/'model.glb'))
        imported=list(bpy.context.selected_objects)
        for obj in imported:
            if not obj.parent:obj.location.x+=(-6.7,-3.3,.5,5.0)[index]
    scene=author.studio(18,1600);scene.cycles.samples=48
    folder=ROOT/'gallery/media/objects/rigellian/fleet';folder.mkdir(parents=True,exist_ok=True)
    for name,direction in [('shared-scale-top',(0,-.001,1.5)),('shared-scale-oblique',(1.15,-1.2,1.1))]:
        author.aim(scene,direction,18);scene.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
        path=folder/(name+'.png');path.write_bytes(clean_png(path.read_bytes()))
    report={'scale':'One native unit per ten proposed world units; no per-ship fitting/scaling',
            'world_sizes':[s['proposed_world_size'] for s in author.STYLE['ships']],
            'left_to_right':[s['name'] for s in author.STYLE['ships']],
            'renders':{p.name:sha(p) for p in folder.glob('*.png')}}
    (ROOT/'sources/objects/rigellian/fleet-comparison.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    for ship in author.STYLE['ships']:verify(ship)
    fleet_comparison()
