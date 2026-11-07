"""Encode the five verified construction stages ON the shipyard platform (#227).

Fixed-camera Blender stage renders reproduce discrete layer visibility. These
previews cover construction, not the subsequent crane/hangar transfer.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image,ImageChops,ImageDraw,ImageFont,ImageStat

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'sources/objects/terran/ship-yard/hangar'
MEDIA=ROOT/'gallery/media/objects/terran/ship-yard/hangar'
SHIPS={'assault-fighter':'Assault Fighter','combat-eagle':'Combat Eagle','scoutship':'Scoutship'}
STAGES=[('build-base','Podstawa szkieletu'),('build-frame','Rozbudowa szkieletu'),('build-systems','Szkielet z elementami pełnymi'),('partial-hull','Częściowo osadzone poszycie'),('complete','Kompletne poszycie')]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ffmpeg=shutil.which('ffmpeg');probe=shutil.which('ffprobe');assert ffmpeg and probe
    evidence=json.loads((SOURCE/'showcase-stills.json').read_text(encoding='utf-8'))
    renderer=Path(__file__).with_name('render_shipyard_construction.py')
    assert evidence['renderer_sha256']==sha(renderer)
    font_path=ROOT/'sources/ui/legacy-menu-labels/font/NotoSerif-Bold.ttf'
    font=ImageFont.truetype(str(font_path),23);title_font=ImageFont.truetype(str(font_path),28)
    clips=[];downloads={};images={};verified_order={}
    for ship,title in SHIPS.items():
        folder=ROOT/'artifacts/issue-227'/('yard-build-'+ship);folder.mkdir(parents=True,exist_ok=True)
        lines=[];references=[]
        for index,(suffix,label) in enumerate(STAGES):
            source=MEDIA/(ship+'-'+suffix+'.png');digest=sha(source);assert evidence['images'][source.name]==digest
            images[source.relative_to(ROOT).as_posix()]=digest
            image=Image.open(source).convert('RGB');assert image.size==(768,768)
            draw=ImageDraw.Draw(image);draw.rectangle((0,0,768,108),fill=(22,28,35))
            draw.text((28,18),title+' — stocznia',font=title_font,fill='white')
            draw.text((28,61),f'{index+1}/5  {label}',font=font,fill=(255,189,82))
            for k in range(5):draw.rounded_rectangle((28+k*144,720,162+k*144,730),radius=3,fill=(235,165,45) if k<=index else (65,73,82))
            references.append(image);frame=folder/f'{index:02}.png';image.save(frame)
            lines.extend(["file '"+frame.as_posix()+"'",'duration '+str(2.4 if index==4 else 1.4)])
        lines.append("file '"+(folder/'04.png').as_posix()+"'");concat=folder/'frames.txt';concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        outputs={}
        for extension,codec in [('mp4',['-c:v','libx264','-crf','18','-movflags','+faststart']),('webm',['-c:v','libvpx-vp9','-crf','27','-b:v','0','-deadline','good','-cpu-used','4'])]:
            output=MEDIA/('shipyard-build-'+ship+'.'+extension)
            subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-vf','fps=30,tpad=stop_mode=clone:stop_duration=3','-frames:v','240',*codec,'-threads','2','-pix_fmt','yuv420p','-an',str(output)],check=True)
            data=json.loads(subprocess.check_output([probe,'-v','error','-count_frames','-show_entries','stream=nb_read_frames:format=duration','-of','json',str(output)],text=True))
            assert int(data['streams'][0]['nb_read_frames'])==240 and abs(float(data['format']['duration'])-8)<.04
            subprocess.run([ffmpeg,'-v','error','-i',str(output),'-f','null','-'],check=True,capture_output=True)
            outputs[extension]=dict(path=output.relative_to(ROOT).as_posix(),sha256=sha(output));downloads[ship+'-'+extension]=outputs[extension]
        order=[]
        for index,seconds in enumerate([.7,2.1,3.5,4.9,6.3]):
            raw=subprocess.check_output([ffmpeg,'-v','error','-ss',str(seconds),'-i',str(ROOT/outputs['mp4']['path']),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
            actual=Image.frombytes('RGB',(768,768),raw)
            errors=[sum(ImageStat.Stat(ImageChops.difference(actual,ref)).mean)/3 for ref in references]
            best=min(range(5),key=lambda k:errors[k]);assert best==index and errors[best]<5,(ship,index,errors)
            order.append(best+1)
        verified_order[ship]=order
        clips.append(dict(kind='yard-build',name=title+' — construction on shipyard platform',video=outputs['webm']['path'],sha256=outputs['webm']['sha256'],mp4=outputs['mp4'],frames=240,duration=8,distinct_pose_count=5))
        print('SHIPYARD_BUILD_VIDEO_VERIFIED',ship,240,8,order,flush=True)
    inputs=[Path(__file__),renderer,SOURCE.parent/'model.blend',SOURCE.parent/'model.glb',SOURCE.parent/'model.json',SOURCE/'showcase-stills.json']
    for ship in SHIPS:inputs.extend(ROOT/'sources/objects/terran'/ship/name for name in ['model.glb','model.json'])
    data=dict(issue=227,inputs={p.relative_to(ROOT).as_posix():sha(p) for p in inputs},clips=clips,downloads=downloads,stage_images=images,decoded_stage_order=verified_order,method='Five actual Blender construction-stage renders on the yard platform, fixed game-calibrated placement and camera, discrete visibility changes. No interpolated assembly motion or post-build transfer in these three clips.')
    path=SOURCE/'yard-build-previews.json';path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    gallery_path=SOURCE/'showcase.json';gallery=json.loads(gallery_path.read_text(encoding='utf-8'))
    gallery['inputs'].update(data['inputs']);gallery['inputs'][path.relative_to(ROOT).as_posix()]=sha(path)
    gallery['clips']=[clip for clip in gallery['clips'] if clip.get('kind')!='yard-build']+clips
    gallery.setdefault('downloads',{}).update(downloads)
    gallery_path.write_text(json.dumps(gallery,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


if __name__=='__main__':main()
