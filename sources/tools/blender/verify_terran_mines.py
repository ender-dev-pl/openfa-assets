"""Blender native/reimport proof and paired footprint-fit preview for #271."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from correct_terran_mines import bounds,meshes,render,sha,signature,evaluated_triangles,clean_render


def inventory(objects):
    return dict(objects=len(objects),triangles=evaluated_triangles(objects),bounds=bounds(objects))


def close(a,b,tolerance=.0001):
    assert all(abs(x-y)<tolerance for row0,row1 in zip(a,b) for x,y in zip(row0,row1)),(a,b)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--models',type=Path,required=True)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--generation-proofs',type=Path,help='Canonical gallery proof directory, when validating published source paths')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    args.proof.mkdir(parents=True,exist_ok=True)
    results={}
    for code in ['pb08','pb13']:
        folder=args.models/code
        record_path=args.generation_proofs/(code+'-generation.json') if args.generation_proofs else folder/'correction.json'
        record=json.loads(record_path.read_text())
        assert sha(folder/'model.blend')==record['blend_sha256']
        assert sha(folder/'model.glb')==record['glb_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'))
        native=inventory(meshes());close(native['bounds'],record['bounds'])
        if record.get('utility_contract'):
            assert sha(Path(__file__).with_name('soften_mine_utilities.py'))==record['generator_sha256']
            assert not any('fence' in o.name.lower() for o in meshes())
            housings=[o for o in meshes() if 'point service' in o.name and o.name.endswith('housing')]
            assert len(housings)==4,'Expected four separate point installations'
            utilities=[o for o in meshes() if o.get('mine_correction_role')=='utility']
            assert bounds(utilities)[1][2]<=.14
            area=sum(o.dimensions.x*o.dimensions.y for o in housings)
            overall=(record['bounds'][1][0]-record['bounds'][0][0])*(record['bounds'][1][1]-record['bounds'][0][1])
            assert area/overall<.03,'Utility islands must remain sparse'
        else:
            assert sha(Path(__file__).with_name('correct_terran_mines.py'))==record['generator_sha256']
        for name,expected in record['unchanged_original_meshes'].items():
            assert signature(bpy.data.objects[name])==expected,name
        for key in ['continuous bore pipe','downward cutting crown','deck rotary chuck']:
            assert any(key in o.name for o in meshes()),(code,key)
        assert native['bounds'][0][2]>=-.00001
        assert native['triangles']<35000,(code,'Unnecessary runtime geometry growth')
        for obj in list(meshes()):bpy.data.objects.remove(obj,do_unlink=True)
        bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'))
        imported=inventory(meshes());close(native['bounds'],imported['bounds'])
        assert imported['triangles']==native['triangles'],(code,native,imported)
        for key in ['continuous bore pipe','downward cutting crown','deck rotary chuck']:
            assert any(key in o.name for o in meshes()),(code,'Missing imported drill part',key)
        target=((imported['bounds'][0][0]+imported['bounds'][1][0])/2,
                (imported['bounds'][0][1]+imported['bounds'][1][1])/2,.85)
        scene=bpy.context.scene;images={}
        for name,a in [('front-quarter',-60),('rear-quarter',120)]:
            path=args.proof/(code+'-imported-'+name+'.png')
            render(scene,path,a,target,4.25 if code=='pb08' else 3.5);images[name]=sha(path)
        scene.camera.location=(0,0,10);scene.camera.rotation_euler=(0,0,0)
        scene.camera.data.ortho_scale=3.75 if code=='pb08' else 3.2
        path=args.proof/(code+'-imported-top.png');scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True);clean_render(path);images['top']=sha(path)
        results[code]=dict(blend_sha256=sha(folder/'model.blend'),glb_sha256=sha(folder/'model.glb'),native=native,imported=imported,
                           unchanged_original_meshes_verified=len(record['unchanged_original_meshes']),images=images)
    # The preview applies the same 2x2 XY bounding-box fit used by the game,
    # without adding a renderer occupancy factor. It is not a game screenshot.
    for obj in list(meshes()):bpy.data.objects.remove(obj,do_unlink=True)
    for i,code in enumerate(['pb08','pb13']):
        previous=set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(args.models/code/'model.glb'))
        imported=[o for o in bpy.context.scene.objects if o not in previous]
        bb=bounds([o for o in imported if o.type=='MESH']);lo,hi=map(Vector,bb)
        fit=min(2/(hi.x-lo.x),2/(hi.y-lo.y))
        transform=Matrix.Translation(Vector(((i-.5)*3.35,0,0))) @ Matrix.Diagonal(Vector((fit,fit,fit,1))) @ Matrix.Translation(Vector((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z)))
        for obj in imported:
            if obj.parent not in imported:obj.matrix_world=transform@obj.matrix_world
        results[code]['footprint_fit_scale']=fit
        results[code]['fitted_original_deck_width']=2.1500000953674316*fit
    scene=bpy.context.scene
    camera=scene.camera;camera.location=(4.8,-9,6.8)
    target=Vector((0,0,.7));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=7.0
    scene.render.resolution_x=1440;scene.render.resolution_y=860
    scene.render.film_transparent=True;scene.cycles.samples=32
    path=args.proof/'paired-footprint-fit.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    clean_render(path)
    ratio=results['pb08']['footprint_fit_scale']/results['pb13']['footprint_fit_scale']
    assert abs(ratio-.75)<.0001,ratio
    report=dict(format='terran-mine-runtime-correction-v1',issue=271,verifier_sha256=sha(__file__),generator_sha256=sha(Path(__file__).with_name('correct_terran_mines.py')),
                models=results,small_to_deep_structure_scale=ratio,paired_render_sha256=sha(path),point_utility_generator_sha256=sha(Path(__file__).with_name('soften_mine_utilities.py')),
                note='Actual native BLEND and independent GLB imports rendered in Blender. Paired image emulates game footprint fit; real gameplay/construction/ghost/picking/shadow integration acceptance is not claimed.')
    (args.proof/'runtime-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MINE_RUNTIME_VERIFIED',ratio,{key:value['native']['triangles'] for key,value in results.items()},flush=True)


if __name__=='__main__':
    main()
