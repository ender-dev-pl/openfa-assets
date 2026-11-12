"""Publish previews of authored proposals without registering gameplay assets."""
import argparse,hashlib,html,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--ffprobe',default='ffprobe');a=p.parse_args()
    cards=[];published=[]
    for folder in sorted((ROOT/'sources/proposals/engineering-ships').glob('*/*')):
        if not (folder/'runtime-review.json').is_file():continue
        meta=json.loads((folder/'model.json').read_text());review=json.loads((folder/'runtime-review.json').read_text());assert review['metadata_sha256']==digest(folder/'model.json')
        culture=meta['culture'];role=meta['role'];media=ROOT/'gallery/media/proposals/engineering-ships'/culture/role
        clips={}
        for label in ['native','imported']:
            output=media/(label+'-ToolOperation.mp4');frames=media/(label+'-frames')
            if frames.is_dir():
                subprocess.run([a.ffmpeg,'-v','error','-y','-framerate','6','-i',str(frames/'%03d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-crf','19','-movflags','+faststart','-map_metadata','-1',str(output)],check=True)
            doc=json.loads(subprocess.check_output([a.ffprobe,'-v','error','-count_frames','-show_streams','-of','json',str(output)]))['streams'][0]
            assert int(doc['nb_read_frames'])==24 and abs(float(doc['duration'])-4)<.01
            subprocess.run([a.ffmpeg,'-v','error','-i',str(output),'-f','null','-'],check=True)
            clips[output.relative_to(ROOT).as_posix()]=dict(sha256=digest(output),frames=24,seconds=4)
        (folder/'video-review.json').write_text(json.dumps(dict(binaries=meta['binaries'],runtime_review_sha256=digest(folder/'runtime-review.json'),clips=clips),indent=2)+'\n')
        base=folder.relative_to(ROOT).as_posix();m=media.relative_to(ROOT/'gallery').as_posix();concept='../'+meta['concept']['image']
        title=culture.title()+' - '+('Terraforming Ship' if role=='terraform' else 'Repair / Construction Assist Ship')
        cards.append(f'<article><h2>{html.escape(title)}</h2><p>New OpenFA proposal | awaiting mechanics</p><div class="views"><figure><img src="{concept}" alt="Selected supplied concept"><figcaption>Selected concept</figcaption></figure><figure><img src="{m}/imported-front-quarter.png" alt="Independent GLB import"><figcaption>Actual GLB render</figcaption></figure></div><video controls loop muted playsinline preload="none" poster="{m}/imported-front-quarter.png" src="{m}/imported-ToolOperation.mp4"></video><p>{meta["triangles"]:,} triangles | 4-second ToolOperation clip</p><a href="../{base}/model.glb" download>GLB</a> | <a href="../{base}/model.blend" download>Editable Blend</a> | <a href="../{base}/runtime-review.json">Runtime evidence</a></article>')
        published.append(dict(culture=culture,role=role,model=base+'/model.glb',metadata_sha256=digest(folder/'model.json')))
    (ROOT/'gallery/engineering-proposals.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OpenFA engineering ship proposals</title><style>body{background:#171c24;color:#e7edf5;font:16px system-ui;max-width:1200px;margin:auto;padding:24px}a{color:#9cceff}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px}article{background:#222b36;padding:16px;border-radius:12px}h2{font-size:20px}.views{display:flex}figure{width:50%;margin:0}img{width:100%}video{width:100%;max-height:340px}figcaption{font-size:13px}</style><a href="index.html">Asset catalogue</a><h1>Engineering ship proposals</h1><p>These are new authored OpenFA designs based on selected concepts. Animated assets only: game mechanics, unit definitions, blueprints, production routes and integration are pending. Scale is provisional. They are not recovered legacy units.</p><main>'+''.join(cards)+'</main></html>\n')
    (ROOT/'gallery/engineering-proposals.json').write_text(json.dumps(dict(issue=265,status='proposals-awaiting-mechanics',models=published),indent=2)+'\n')
    layout_path=ROOT/'project/layout.json';layout=json.loads(layout_path.read_text());known={x['destination'] for x in layout['files']}
    for prefix in ['sources/proposals/engineering-ships','sources/artwork/proposals/engineering-ships','sources/materials/proposals/engineering-ships','sources/tools/blender/proposals']:
        for path in sorted((ROOT/prefix).rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:continue
            rel=path.relative_to(ROOT).as_posix()
            if rel in known:continue
            role='source-input' if '/artwork/' in rel else 'material-texture' if '/materials/' in rel else 'source'
            layout['files'].append(dict(original=rel,destination=rel,role=role,ownership='authored'));known.add(rel)
    layout_path.write_text(json.dumps(layout,indent=2)+'\n');print('ENGINEERING_PROPOSALS_PUBLISHED',len(published))
if __name__=='__main__':main()
