"""Render continuous 3D assembly and complete crane/hangar cycles for three ships.

Actual canonical GLBs are evaluated and rendered at every output frame. A preview
assembly controller lowers successive rigid batches into place over eight seconds;
the authored yard animation then completes its entire transfer cycle. No still-image
holds, crossfades, frame duplication or optical-flow interpolation are used.
"""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
from render_shipyard_construction import combined_scene
from build_ship_construction_layers import sha,SHIPS
from build_shipyard_hangar import OUT,MEDIA

GROUPS=['Build01_BaseFrame','Build02_ExpandedFrame','Build03_Systems','HullPartial','HullFinal']
WINDOWS=[(0,1.3),(1.3,3.0),(3.0,4.9),(4.9,6.5),(6.5,8.0)]
DURATION=20


def clamp(value):return min(1,max(0,value))


def initialize(ship):
    scene,objects,config=combined_scene(ship);scene.frame_set(1);bpy.context.view_layer.update()
    root=next(obj for obj in objects if obj.name=='ShipAssembly')
    meta=json.loads((ROOT/'sources/objects/terran'/ship/'construction/model.json').read_text())
    size=max(b-a for a,b in zip(*meta['shell_bounds']));components=[]
    for obj in objects:
        if obj.type!='MESH':continue
        node=obj.parent
        while node and node.name not in GROUPS:node=node.parent
        assert node,obj.name
        components.append(dict(obj=obj,stage=GROUPS.index(node.name),location=obj.location.copy(),offset=obj.parent.matrix_world.to_3x3().inverted()@root.matrix_world.to_3x3()@Vector((0,0,size*.08))))
    components.sort(key=lambda item:(item['stage'],item['obj'].name))
    for stage in range(5):
        members=[item for item in components if item['stage']==stage]
        start,end=WINDOWS[stage]
        for index,item in enumerate(members):
            item['start']=start+(end-start)*.35*index/max(1,len(members)-1)
            item['end']=item['start']+(end-start)*.65
    yard=json.loads((OUT/'model.json').read_text());af=yard['ships']['assault-fighter']
    config['eye_height_offset']=config['socket'][2]-af['socket'][2]
    config['sling_directions']=[Vector(p)-Vector(config['socket']) for p in config['contacts']]
    config['af_sling_lengths']=[(Vector(p)-Vector(af['socket'])).length for p in af['contacts']]
    return scene,components,config


def pose(scene,components,config,seconds):
    frame=1+119*seconds/8 if seconds<=8 else 120+(seconds-8)*30
    scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update()
    for item in components:
        t=clamp((seconds-item['start'])/(item['end']-item['start']));smooth=t*t*(3-2*t)
        obj=item['obj'];obj.hide_render=seconds<item['start'];obj.location=item['location']+item['offset']*(1-smooth)
    # Crane services the build area continuously, and meets the exported trajectory at t=8.
    if seconds<8:bpy.data.objects['Trolley'].location.x+=1.5*math.sin(math.pi*seconds/8)**2
    # Payload-specific hoist and three sling legs; all ships keep identical ground scale.
    weight=clamp((frame-120)/25) if frame<145 else 1 if frame<=335 else 1-clamp((frame-335)/60)
    offset=config['eye_height_offset']*weight
    bpy.data.objects['Hoist'].location.z+=offset
    bpy.data.objects['HoistCables'].scale.z-=offset
    for index,direction in enumerate(config['sling_directions']):
        obj=bpy.data.objects[f'LoadSling_{index}'];obj.rotation_mode='QUATERNION';obj.rotation_quaternion=direction.to_track_quat('Z','Y')
        obj.scale.z*=direction.length/config['af_sling_lengths'][index]
        for child in obj.children:child.hide_render=frame<145 or frame>340
    bpy.context.view_layer.update()
    if 150<=frame<=335:
        carrier=bpy.data.objects['ShipConstructionPlacement'];eye=carrier.matrix_world@Vector(config['socket'])
        gap=(bpy.data.objects['LoadAttachment'].matrix_world.translation-eye).length
        assert gap<.00002,('load attachment drift',frame,gap)
        for index,contact in enumerate(config['contacts']):
            end=bpy.data.objects[f'LoadSling_{index}'].matrix_world@Vector((0,0,1))
            gap=(end-carrier.matrix_world@Vector(contact)).length
            assert gap<.00002,('sling contact drift',frame,index,gap)
    return frame


def configure(scene,resolution,engine):
    scene.render.engine=engine
    if engine=='CYCLES':scene.cycles.samples=12;scene.cycles.use_denoising=True
    else:scene.eevee.taa_render_samples=32
    scene.render.resolution_x=scene.render.resolution_y=resolution;scene.render.resolution_percentage=100
    scene.render.film_transparent=False;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ship',choices=SHIPS,required=True)
    parser.add_argument('--probe',action='store_true');parser.add_argument('--engine',default='BLENDER_EEVEE_NEXT');parser.add_argument('--resolution',type=int,default=768);parser.add_argument('--fps',type=int,default=24)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);ship=args.ship
    scene,components,config=initialize(ship);configure(scene,args.resolution,args.engine)
    folder=ROOT/'artifacts/issue-227'/('complete-3d-'+ship);folder.mkdir(parents=True,exist_ok=True)
    if args.probe:
        for seconds in [0,2.5,7.5,10.5,13,15,18.5,20]:
            pose(scene,components,config,seconds);scene.render.filepath=str(folder/f'probe-{seconds:g}.png');bpy.ops.render.render(write_still=True)
        return
    count=DURATION*args.fps;scene.render.fps=args.fps;states=set()
    for index in range(count):
        seconds=index/args.fps;frame=pose(scene,components,config,seconds)
        signature=tuple((obj.name,obj.hide_render,tuple(round(v,5) for row in obj.matrix_world for v in row)) for obj in [item['obj'] for item in components]+[bpy.data.objects[n] for n in ['Trolley','LoadAttachment','HangarDoor_Left','ShipConstructionPlacement']])
        states.add(signature)
        scene.render.filepath=str(folder/f'{index:04}.png');bpy.ops.render.render(write_still=True)
        if index%24==0:print('COMPLETE_3D_FRAME',ship,index,count,frame,flush=True)
    assert len(states)>count*.75,(ship,len(states),count)
    outputs={};ffmpeg=shutil.which('ffmpeg');probe=shutil.which('ffprobe');assert ffmpeg and probe
    for extension,codec in [('mp4',['-c:v','libx264','-crf','18','-movflags','+faststart']),('webm',['-c:v','libvpx-vp9','-crf','27','-b:v','0','-deadline','good','-cpu-used','4'])]:
        output=MEDIA/('complete-3d-'+ship+'.'+extension)
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate',str(args.fps),'-i',str(folder/'%04d.png'),'-frames:v',str(count),*codec,'-threads','2','-pix_fmt','yuv420p','-an',str(output)],check=True)
        data=json.loads(subprocess.check_output([probe,'-v','error','-count_frames','-show_entries','stream=nb_read_frames:format=duration','-of','json',str(output)],text=True))
        assert int(data['streams'][0]['nb_read_frames'])==count and abs(float(data['format']['duration'])-DURATION)<.04
        subprocess.run([ffmpeg,'-v','error','-i',str(output),'-f','null','-'],check=True,capture_output=True)
        outputs[extension]=dict(path=output.relative_to(ROOT).as_posix(),sha256=sha(output))
    files=[Path(__file__),Path(__file__).with_name('render_shipyard_construction.py'),OUT/'model.blend',OUT/'model.glb',OUT/'model.json']
    files.extend(ROOT/'sources/objects/terran'/ship/'construction'/name for name in ['model.glb','model.json'])
    clip=dict(kind='complete-3d',name=ship.replace('-',' ').title()+' — complete 3D construction and hangar transfer',video=outputs['webm']['path'],sha256=outputs['webm']['sha256'],mp4=outputs['mp4'],frames=count,duration=DURATION,distinct_pose_count=len(states))
    evidence=dict(issue=227,inputs={p.relative_to(ROOT).as_posix():sha(p) for p in files},clips=[clip],downloads=outputs,fps=args.fps,resolution=args.resolution,engine=args.engine,assembly_windows_seconds=WINDOWS,payload_hoist_offset=config['eye_height_offset'],per_frame_attachment_and_sling_checks=True,method='Every frame rendered from evaluated canonical 3D models. Preview-only batch placement animation during construction; full canonical yard transfer with calibrated per-payload rig. No interpolation between still renders or duplicated still-image holds. Canonical model geometry is unchanged.')
    (OUT/('complete-3d-'+ship+'.json')).write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print('COMPLETE_3D_VIDEO_VERIFIED',ship,count,len(states),flush=True)


if __name__=='__main__':main()
