"""Present each ship's five verified Blender construction renders as a movie.

Stage changes are hard cuts, matching cumulative mesh visibility. This does not
invent interpolated assembly motion or alter any canonical model.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image,ImageChops,ImageDraw,ImageFont,ImageStat

ROOT=Path(__file__).resolve().parents[3]
SHIPS={'assault-fighter':'Assault Fighter','combat-eagle':'Combat Eagle','scoutship':'Scoutship'}
LABELS=['Podstawa szkieletu','Rozbudowa szkieletu','Szkielet z elementami pełnymi','Częściowo osadzone poszycie','Kompletne poszycie']


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ffmpeg=shutil.which('ffmpeg');probe=shutil.which('ffprobe');assert ffmpeg and probe
    font=ImageFont.truetype(str(ROOT/'sources/ui/legacy-menu-labels/font/NotoSerif-Bold.ttf'),23)
    title_font=ImageFont.truetype(str(ROOT/'sources/ui/legacy-menu-labels/font/NotoSerif-Bold.ttf'),28)
    for ship,title in SHIPS.items():
        source=ROOT/'sources/objects/terran'/ship/'construction';media=ROOT/'gallery/media/objects/terran'/ship/'construction'
        review=json.loads((source/'visual-review.json').read_text(encoding='utf-8'))
        assert review['glb_sha256']==sha(source/'model.glb') and review['blend_sha256']==sha(source/'model.blend')
        frames=ROOT/'artifacts/issue-227'/('individual-build-'+ship);frames.mkdir(parents=True,exist_ok=True)
        stage_inputs={};lines=[];reference_frames=[]
        for index,label in enumerate(LABELS):
            path=media/f'stage-{index+1:02}.png';digest=sha(path);assert review['images'][path.name]==digest
            stage_inputs[path.relative_to(ROOT).as_posix()]=digest
            image=Image.open(path).convert('RGBA');background=Image.new('RGBA',image.size,(22,28,35,255));background.alpha_composite(image)
            draw=ImageDraw.Draw(background);draw.text((28,22),title,font=title_font,fill=(240,240,240))
            draw.text((28,65),f'{index+1}/5  {label}',font=font,fill=(255,189,82))
            for stage in range(5):draw.rounded_rectangle((28+stage*144,720,162+stage*144,730),radius=3,fill=(235,165,45) if stage<=index else (65,73,82))
            frame=frames/f'{index:02}.png';reference_frames.append(background.convert('RGB'));reference_frames[-1].save(frame)
            lines += ["file '"+frame.as_posix()+"'",'duration '+str(2.4 if index==4 else 1.4)]
        assert len(set(stage_inputs.values()))==5,'Construction stages must be visually distinct'
        lines += ["file '"+(frames/'04.png').as_posix()+"'"]
        concat=frames/'frames.txt';concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        outputs={}
        for extension,codec in [('mp4',['-c:v','libx264','-crf','18','-movflags','+faststart']),('webm',['-c:v','libvpx-vp9','-crf','27','-b:v','0','-deadline','good','-cpu-used','4'])]:
            output=media/('construction-stages.'+extension)
            subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-vf','fps=30,tpad=stop_mode=clone:stop_duration=3','-frames:v','240',*codec,'-threads','2','-pix_fmt','yuv420p','-an',str(output)],check=True)
            result=json.loads(subprocess.check_output([probe,'-v','error','-count_frames','-show_entries','stream=nb_read_frames:format=duration','-of','json',str(output)],text=True))
            assert int(result['streams'][0]['nb_read_frames'])==240 and abs(float(result['format']['duration'])-8)<.04
            subprocess.run([ffmpeg,'-v','error','-i',str(output),'-f','null','-'],check=True,capture_output=True)
            outputs[extension]=dict(path=output.relative_to(ROOT).as_posix(),sha256=sha(output))
        recognized=[]
        for index,seconds in enumerate([.7,2.1,3.5,4.9,6.3]):
            raw=subprocess.check_output([ffmpeg,'-v','error','-ss',str(seconds),'-i',str(ROOT/outputs['mp4']['path']),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
            actual=Image.frombytes('RGB',(768,768),raw)
            errors=[sum(ImageStat.Stat(ImageChops.difference(actual,ref)).mean)/3 for ref in reference_frames]
            best=min(range(5),key=lambda k:errors[k]);assert best==index and errors[best]<5,(ship,index,errors)
            recognized.append(best+1)
        inputs=[Path(__file__),source/'model.blend',source/'model.glb',source/'model.json',source/'visual-review.json']
        manifest=dict(issue=227,inputs={p.relative_to(ROOT).as_posix():sha(p) for p in inputs},stage_images=stage_inputs,decoded_stage_order=recognized,clips=[dict(name=title+' — five construction stages',video=outputs['webm']['path'],sha256=outputs['webm']['sha256'],frames=240,duration=8,distinct_pose_count=5,mp4=outputs['mp4'])],method='Sequence of five verified actual Blender stage renders, fixed camera and scale. Hard cuts reproduce cumulative mesh visibility; no interpolated assembly motion.',downloads=outputs)
        (source/'showcase.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print('INDIVIDUAL_BUILD_MOVIE_VERIFIED',ship,240,8,flush=True)


if __name__=='__main__':main()
