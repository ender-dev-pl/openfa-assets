"""Encode actual OpenFA GPU studio frames and publish playable gallery cycles."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'gallery/media/construction-cycles'
LABELS={'ready':'Construction site','erection':'Erecting scaffold','reveal':'Finished building inserted',
        'dismantling':'Dismantling from the top','complete':'Construction complete'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def fonts(size):
    for name in ['C:/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(name).is_file():return ImageFont.truetype(name,size)
    return ImageFont.load_default()


def caption(plan,path,phase,stage):
    image=Image.new('RGB',(640,720),(15,22,31))
    with Image.open(path) as raw:
        assert raw.size==(640,640)
        bg=Image.new('RGBA',raw.size,(15,22,31,255));bg.alpha_composite(raw.convert('RGBA'))
        image.paste(bg.convert('RGB'),(0,44))
    draw=ImageDraw.Draw(image)
    draw.text((20,10),plan['culture'].title()+' | '+plan['building_name'],font=fonts(21),fill=(228,239,245))
    text=LABELS[phase]+(f"  /  stage {stage} of {plan['ceiling']}" if stage else '')
    draw.text((20,690),text,font=fonts(17),fill=(157,201,219))
    return image


def encode(folder):
    plan_path=folder/'sequence.json';plan=json.loads(plan_path.read_text())
    rendered=folder/'rendered';evidence=json.loads((rendered/'runtime-evidence.json').read_text())
    assert evidence['renderer']=='OpenFA.Client.MonoGameSurfaceModelRenderer'
    assert evidence['method']=='RenderStudioProof' and not evidence['gameplayIntegration']
    assert evidence['planSha256']==sha(plan_path)
    assert evidence['archiveSha256']==sha(folder/plan['archive'])
    frames={f['image']:f for f in plan['frames']}
    for frame in evidence['frames']:
        assert frame['image'] in frames and sha(rendered/frame['image'])==frame['sha256']
    assert len(evidence['frames'])==len(plan['frames'])
    for path,digest in plan['sources'].items():assert sha(ROOT/path)==digest,path
    culture=plan['culture'];target=DEST/culture;target.mkdir(parents=True,exist_ok=True)
    video=target/'construction.webm'
    command=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','640x720',
             '-framerate','30','-i','pipe:0','-an','-c:v','libvpx-vp9','-crf','28','-b:v','0',
             '-pix_fmt','yuv420p','-row-mt','1','-threads','4','-deadline','good','-cpu-used','4',str(video)]
    emitted=0;elapsed=0;timeline=[]
    process=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for entry in plan['timeline']:
            image=caption(plan,rendered/entry['image'],entry['phase'],entry['stage'])
            elapsed+=entry['duration'];end=round(elapsed*30);count=end-emitted
            assert count>0
            timeline.append(dict(phase=entry['phase'],stage=entry['stage'],start_frame=emitted,frames=count,image=entry['image']))
            raw=image.tobytes()
            for _ in range(count):process.stdin.write(raw)
            emitted=end
        process.stdin.close()
        assert process.wait()==0,'Video encoding failed'
    except BaseException:
        process.kill();process.wait();raise
    final=next(f for f in plan['frames'] if f['key']=='complete')
    reveal=next(f for f in plan['frames'] if f['key']==f"reveal-{plan['ceiling']:02}")
    caption(plan,rendered/reveal['image'],'reveal',plan['ceiling']).save(target/'poster.png')
    caption(plan,rendered/final['image'],'complete',0).save(target/'complete.png')
    # Durable identification/reproduction data; raw poses and model archives remain
    # working artifacts, not additional authored model studies.
    shutil.copy2(plan_path,target/'sequence.json')
    shutil.copy2(rendered/'runtime-evidence.json',target/'runtime-evidence.json')
    metadata=dict(issue=189,culture=culture,building=plan['building_name'],definition_id=plan['definition_id'],family=plan['family'],
                  renderer=evidence['renderer'],render_mode='Game-engine asset studio; not live gameplay integration',
                  width=640,height=720,fps=30,frames=emitted,duration=emitted/30,timeline=timeline,
                  video_sha256=sha(video),poster_sha256=sha(target/'poster.png'),complete_sha256=sha(target/'complete.png'),
                  sequence_sha256=sha(target/'sequence.json'),runtime_evidence_sha256=sha(target/'runtime-evidence.json'),
                  encoder_sha256=sha(Path(__file__)),host_source_sha256=sha(ROOT/'tools/ConstructionPreview/Program.cs'),
                  host_project_sha256=sha(ROOT/'tools/ConstructionPreview/ConstructionPreview.csproj'))
    (target/'video.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('CONSTRUCTION_VIDEO_ENCODED',culture,emitted,flush=True)
    return metadata


def gallery(records):
    cards=[]
    for record in records:
        culture=record['culture'];path='media/construction-cycles/'+culture
        cards.append(f'<article><h2>{html.escape(culture.title())}</h2><p>{html.escape(record["building"])}</p>'
                     f'<video controls loop muted playsinline preload="none" poster="{path}/poster.png" aria-label="{culture} construction cycle">'
                     f'<source src="{path}/construction.webm" type="video/webm"></video>'
                     '<p class="phases">Erect scaffold → insert building → dismantle from the top</p>'
                     f'<a href="{path}/construction.webm">Download video</a> · <a href="{path}/video.json">Rendering evidence</a></article>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenFA construction cycles</title><style>
:root{color-scheme:dark}body{margin:0;background:#101722;color:#e7eff7;font:16px system-ui}header{padding:28px;max-width:1100px}h1{margin:0 0 12px}a{color:#80ccff}p{color:#b3c7dc}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:20px;padding:20px}article{background:#192637;border-radius:12px;padding:20px}h2{margin:0}video{display:block;width:100%;height:auto;max-height:720px;background:#0f161f;margin:16px 0}.phases{font-size:14px}a:focus-visible,video:focus-visible{outline:3px solid #f3bd68;outline-offset:3px}
</style><header><h1>Construction cycles</h1><p>Seven cultures, rendered by the actual OpenFA game engine with PBR lighting, shadows and ambient occlusion.</p><p>These are authored asset-studio sequences. They demonstrate the requested construction cycle; live gameplay integration is separate.</p><a href="index.html">Model catalogue</a> · <a href="scaffolds-cultures.md">Scaffold families</a></header><main>'''+''.join(cards)+'''</main><script>
const videos=[...document.querySelectorAll('video')];
for(const video of videos)video.addEventListener('play',()=>{for(const other of videos)if(other!==video)other.pause()});
</script></html>'''
    (ROOT/'gallery/construction-animations.html').write_text(page,encoding='utf-8',newline='\n')
    (DEST/'index.json').write_text(json.dumps(dict(issue=189,clips=records),indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('frames',type=Path);args=parser.parse_args()
    records=[encode(args.frames/culture) for culture in ['terran','rigellian','braccatian','mikotaj','artemian','mauna','achaean']]
    gallery(records)


if __name__=='__main__':main()
