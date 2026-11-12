"""Publish previews of authored proposals without registering gameplay assets."""
import argparse,hashlib,html,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

# Current small-craft catalogue entries;large combat ships are not substituted for small units.
STYLE_UNITS={
    'terran':('assault-fighter','scoutship'),
    'rigellian':('delphini-assault','lazzaro-research'),
    'braccatian':('morning-glory','rattlesnake'),
    'mikotaj':('ylikt-shan','hiero'),
    'artemian':('all-purpose-assault','gerla-kans-explorer'),
    'mauna':('combat-craft-type-1-5','surveillance-craft-type-5'),
    'achaean':('dedicated-fighter','hunter-prospector'),
}

STYLE_NOTES={'terran': 'Partial match: red fields and cool hull colours connect the designs,but the engineering ships have broad box-like bodies while the small fleet uses wedges,layered plates and round engine details.', 'rigellian': 'Canonical-style pass:one reviewed cycle introduced a green-dominant elongated oval hull,gold fields/crown,slate gondolas and darker ventral casings. Palette/effective PBR values derive from current canonical GLBs;matching-studio references are available. Repair has six animation channels including separate jaws. User artistic acceptance is pending.', 'braccatian': 'Partial match: coral,ochre and brass belong together,but the engineering barrels and broad black reinforcement strips read more industrial than the tapered,lobed small craft.', 'mikotaj': 'Canonical-style pass:three reviewed cycles introduced slate-blue/gunmetal structure,dulled-gold accents,tapered rail profiles and slimmer faceted pods related to Ylikt-shan and Hiero. Gold and primary paint map medians match the canonical authored palette. Utility frames and tools remain functionally distinct;user artistic acceptance is pending.', 'artemian': 'Canonical-style pass:two reviewed cycles introduced a pointed green deck,separated faceted silver fairings and canonical material medians. Current canonical GLB references are rendered in the same review studio. Repair has independent sliders,wrist and closing jaws;user artistic acceptance is pending.', 'mauna': 'Close structural match: rectangular volumes,stepped sections,slots and grey/blue-grey materials connect the ships. Surface finish differs;lighting and separate rendering passes limit exact colour judgement.', 'achaean': 'Close match: copper spindle hulls,thin red/silver crescents and sparse hatches repeat the fleet language. The repaired ship now has mirrored wings;small functional tooling remains distinct.'}

def style_comparison():
    catalogue=json.loads((ROOT/'gallery/catalogue.json').read_text());rows=[];sections=[]
    for culture,slugs in STYLE_UNITS.items():
        units=[];studio={}
        studio_path=ROOT/'sources/proposals/engineering-ships'/culture/'canonical-reference-review.json'
        if studio_path.is_file():
            studio_report=json.loads(studio_path.read_text());assert digest(ROOT/studio_report['renderer'])==studio_report['renderer_sha256']
            studio={x['model']:x for x in studio_report['references']}
        for role,label in [('terraform','Terraforming Ship'),('repair','Repair Ship')]:
            folder=ROOT/'sources/proposals/engineering-ships'/culture/role
            meta=json.loads((folder/'model.json').read_text());image='gallery/media/proposals/engineering-ships/'+culture+'/'+role+'/imported-front-quarter.png'
            units.append(dict(name=label,role=role,status='engineering proposal',model=(folder/'model.glb').relative_to(ROOT).as_posix(),image=image,model_sha256=meta['binaries']['glb'],image_sha256=digest(ROOT/image)))
        for index,slug in enumerate(slugs):
            item,=[x for x in catalogue if x['category']=='ships' and x['culture']==culture and x['id'].split(':')[-1].split('/')[-1]==slug]
            study=item['studies'][-1]
            units.append(dict(name=item['name'],role='small combat/craft reference' if index==0 else 'small scout/research reference',status='current catalogue',catalogue_id=item['id'],stage=study['stage'],model=study['glb'],image=study['image'],model_sha256=digest(ROOT/study['glb']),image_sha256=digest(ROOT/study['image'])))
            if study['glb'] in studio:
                common=studio[study['glb']];assert common['model_sha256']==units[-1]['model_sha256'];preview=common['comparison_preview'];assert digest(ROOT/preview['path'])==preview['sha256']
                units[-1].update(catalogue_image=study['image'],image=preview['path'],image_sha256=preview['sha256'],preview_conditions='Independent canonical GLB import in the same review studio as engineering ships')
        figures=[]
        for unit in units:
            image=unit['image'].removeprefix('gallery/');model='../'+unit['model'];label=html.escape(unit['name']);role=html.escape(unit['role'])
            figures.append(f'<figure><a href="{image}"><img src="{image}" alt="{label}" loading="lazy"></a><figcaption>{label}<br><small>{role}</small><br><a href="{model}" download>GLB</a></figcaption></figure>')
        sections.append('<section class="culture-comparison"><h3>'+culture.title()+'</h3><div class="fleet-comparison">'+''.join(figures)+'</div><p>'+html.escape(STYLE_NOTES[culture])+'</p></section>')
        rows.append(dict(culture=culture,units=units,common_studio=bool(studio),assessment=STYLE_NOTES[culture],assessment_scope='Author visual review of current catalogue previews;not user artistic acceptance.'))
    report=dict(issue=265,purpose='Construction-style comparison;current engineering proposals against current small-craft catalogue models.',limits='Actual model previews;canonical GLB references use the same review studio where a source-bound reference report is available. Other cameras and lighting vary between authoring passes. Image fitting normalizes display size independently and does not establish physical game scale. Scout/research craft are labelled separately from combat/craft references.',cultures=rows)
    (ROOT/'gallery/engineering-style-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    return '<section id="style-comparison"><h2>Engineering ships versus the established small-craft fleet</h2><p>Compare hull sections,wing profiles,structural divisions,materials and construction detail. Each image is fitted independently: this is a style comparison,not physical game scale. Canonical GLB references use the same review studio where available;other previews retain their existing cameras and lighting. Scout/research references are labelled separately.</p>'+''.join(sections)+'</section>'

def main():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--ffprobe',default='ffprobe');a=p.parse_args()
    comparison_html=style_comparison()
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
        comparison=(f'<p><a href="{m}/refinement-comparison.png">Before / refined model comparison</a></p>' if meta.get('revision')==2 else '')
        cycle_path=folder/'style-refinement.json'
        if cycle_path.is_file():
            history=json.loads(cycle_path.read_text());assert len(history['cycles'])<=history['max_cycles']==3
            links=[]
            for cycle in history['cycles']:
                if cycle.get('status')!='visually-reviewed':continue
                preview=cycle['comparison']['path'].removeprefix('gallery/')
                links.append('<a href="'+preview+'">Cycle '+str(cycle['number'])+'</a>')
            comparison+='<p>Canonical-fleet refinement: '+str(len(history['cycles']))+' / 3 cycles. '+ ' | '.join(links)+' | <a href="../'+base+'/style-refinement.json">Review history</a>. User artistic acceptance pending.</p>'
        revision=(' | Refined r2 - defined hull planes and PBR surfaces' if meta.get('revision')==2 else '')
        cards.append(f'<article><h2>{html.escape(title)}</h2><p>New OpenFA proposal | awaiting mechanics{revision}</p><div class="views"><figure><img src="{concept}" alt="Selected supplied concept"><figcaption>Original selected concept</figcaption></figure><figure><img src="{m}/imported-front-quarter.png" alt="Independent GLB import"><figcaption>Actual GLB render</figcaption></figure></div><video controls loop muted playsinline preload="none" poster="{m}/imported-front-quarter.png" src="{m}/imported-ToolOperation.mp4"></video><p>{meta["triangles"]:,} triangles | 4-second ToolOperation clip</p><a href="../{base}/model.glb" download>GLB</a> | <a href="../{base}/model.blend" download>Editable Blend</a> | <a href="../{base}/runtime-review.json">Runtime evidence</a>{comparison}</article>')
        published.append(dict(culture=culture,role=role,model=base+'/model.glb',revision=meta.get('revision',1),metadata_sha256=digest(folder/'model.json')))
    (ROOT/'gallery/engineering-proposals.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OpenFA engineering ship proposals</title><style>body{background:#171c24;color:#e7edf5;font:16px system-ui;max-width:1200px;margin:auto;padding:24px}a{color:#9cceff}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px}article{background:#222b36;padding:16px;border-radius:12px}h2{font-size:20px}.views{display:flex}figure{width:50%;margin:0}img{width:100%}video{width:100%;max-height:340px}figcaption{font-size:13px}.fleet-comparison{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.fleet-comparison figure{width:auto}.fleet-comparison img{height:230px;object-fit:contain;background:#11151b}.fleet-comparison figcaption{padding:8px}.culture-comparison{margin:24px 0;background:#222b36;padding:16px}@media(max-width:760px){.fleet-comparison{grid-template-columns:repeat(2,minmax(0,1fr))}}html{scroll-behavior:smooth}</style><a href="index.html">Asset catalogue</a> | <a href="#style-comparison">Compare with the small-craft fleet</a><h1>Engineering ship proposals</h1><p>These are new authored OpenFA designs based on selected concepts. Animated assets only: game mechanics, unit definitions, blueprints, production routes and integration are pending. Scale is provisional. They are not recovered legacy units.</p><main>'+''.join(cards)+'</main>'+comparison_html+'</html>\n')
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
