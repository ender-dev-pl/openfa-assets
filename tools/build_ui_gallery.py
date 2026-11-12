"""Publish existing reviewed UI renders; no model generation."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]

def build():
    cards = [
        ('Complete HUD icons', 'legacy-icon-set/gameplay-icons.png', 'legacy-icon-set', '111 records; standalone icons and oval buttons, five states at native and 8x resolution.'),
        ('Oval HUD buttons', 'legacy-icon-set/gameplay-buttons.png', 'legacy-icon-set', 'Legacy-referenced motifs with separate chrome and transparent icon delivery.'),
        ('Main menu — amber neon', 'legacy-main-menu-refined/composition-amber.png', 'legacy-main-menu-refined', 'Current registered panels. Shared canvas, identical overlap pixels and continuous red emblem.'),
        ('Preset menu — green neon', 'legacy-main-menu-refined/composition-green.png', 'legacy-main-menu-refined', 'Neon follows menu context; the sphere retains its red logo.'),
        ('Menu lighting states', 'legacy-main-menu-refined/sphere-states.png', 'legacy-main-menu-refined', 'Six interaction states. Additional lighting variants are OpenFA extensions.'),
        ('Interactive sphere — front', 'interactive-menu-sphere/front.png', 'interactive-menu-sphere', 'Full sphere, centered rotor and stationary bezel. Models only; click handling remains to integrate.'),
        ('Interactive sphere — rear', 'interactive-menu-sphere/rear.png', 'interactive-menu-sphere', 'Mirrored continuous logo on the reverse. Both emblems are closed manifold meshes.'),
        ('Interactive sphere — illuminated spin', 'interactive-menu-sphere/spin-37.png', 'interactive-menu-sphere', 'Blender animation demonstration. Client drives random-axis rotation and the independent emission pulse.'),
        ('Independent GLB import', 'interactive-menu-sphere/imported-front.png', 'interactive-menu-sphere', 'Actual imported-model render. Export uses explicit PBR approximations of editable Blender materials.'),
        ('Camera orbit and pitch mode', 'camera-mode-icon/preview.png', 'camera-mode-icon', 'New camera-mode control: silver camera, blue orbit and gold pitch arrows. Transparent 48x40 and 8x icons, five states; separate from camera reset.'),
    ]
    body=[]
    for title, image, source, description in cards:
        assert (ROOT/'gallery/media/ui'/image).is_file(), image
        links='<a href="../sources/ui/'+source+'/README.md">Source and contract</a>'
        if source=='camera-mode-icon':
            for ext in ['blend','glb']:
                links+=' · <a href="../sources/ui/camera-mode-icon/camera-mode-icon.'+ext+'">'+ext.upper()+'</a>'
            for size in ['native','hires']:
                links+=' · <a href="media/ui/camera-mode-icon/icons/'+size+'/camera-mode-icon.png">'+size+' PNG</a>'
        if source in ['interactive-menu-sphere','legacy-main-menu-refined']:
            stem='interactive-sphere' if source=='interactive-menu-sphere' else 'main-menu'
            for ext in ['blend','glb']:
                target='sources/ui/'+source+'/'+stem+'.'+ext
                assert (ROOT/target).is_file()
                links+=' · <a href="../'+target+'">'+ext.upper()+'</a>'
        preview='<img loading="lazy" src="media/ui/'+image+'" alt="'+escape(title)+'">'
        if image == 'interactive-menu-sphere/spin-37.png':
            import hashlib, json
            folder=ROOT/'gallery/media/ui/interactive-menu-sphere'
            proof=json.loads((folder/'animation-proof.json').read_text())
            assert proof['source_sha256']==hashlib.sha256((ROOT/'sources/ui/interactive-menu-sphere/interactive-sphere.blend').read_bytes()).hexdigest()
            assert proof['video_sha256']==hashlib.sha256((folder/'sphere-spin.webm').read_bytes()).hexdigest()
            preview='<video controls loop muted playsinline preload="none" poster="media/ui/'+image+'" aria-label="Sphere rotation and illumination"><source src="media/ui/interactive-menu-sphere/sphere-spin.webm" type="video/webm">Your browser does not support WebM.</video>'
        body.append('<article><h2>'+escape(title)+'</h2>'+preview+'<p>'+escape(description)+'</p><p>'+links+'</p></article>')
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OpenFA UI assets</title><style>body{margin:0;background:#101722;color:#e7eff7;font:16px system-ui}header{padding:24px;background:#162334}a{color:#80ccff}main{padding:20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:20px}article{background:#192637;border-radius:12px;padding:20px}img,video{width:100%;height:360px;object-fit:contain;background:#101722}p{line-height:1.5;color:#b3c7dc}h2{font-size:21px}</style><header><h1>OpenFA UI assets</h1><p>Current legacy-referenced HUD and menu deliveries. Asset previews and Blender runtime proofs; game integration remains separate. Historical iterations are preserved in the private openfa-assets-archive repository.</p><a href="index.html">Model catalogue</a> · <a href="ui.md">Current UI sources and evidence</a></header><main>'+''.join(body)+'</main></html>'
    (ROOT/'gallery/ui.html').write_text(page,encoding='utf-8',newline='\n')
    print('UI_GALLERY_OK',len(cards))

if __name__ == '__main__':
    build()
