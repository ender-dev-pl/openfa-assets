"""Bind reviewed RI18 launch-state semantics; no model or runtime code changes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from PIL import Image

REPO=Path(__file__).resolve().parents[2]
LEGACY=REPO.parent/'legacy'
TARGET=REPO/'docs/reconstruction/models/reviewed-mechanism-semantics.json'
IDENTITY='openfa:building/legacy/057'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def function(text,name):
    match=re.search(r'/\* '+name+r' at (0x[0-9A-Fa-f]+) \*/',text);assert match
    tail=text[match.end():];end=re.search(r'/\* \w+ at 0x[0-9A-Fa-f]+ \*/',tail)
    body=tail[:end.start()] if end else tail
    return dict(name=name,address=match.group(1),text_sha256=hashlib.sha256(body.encode()).hexdigest()),body


def build():
    folder=REPO/'docs/reconstruction/models'
    refs_path=folder/'rigellian-building-references.json';refs=json.loads(refs_path.read_text())
    record=next(r for r in refs['buildings'] if r['id']==IDENTITY)
    assert record['definition_class']==14 and not record['directional_runtime_path']
    assert sha(LEGACY/'_B/_B')==refs['archive_sha256']
    sys.path.insert(0,str(LEGACY/'tools'));import fragile256 as codec
    payload=REPO/'artifacts/rigellian-building-reference-study/RI18/RI18.256'
    assert sha(payload)==record['surface']['source_sha256']
    data,frames,palette,origin=codec.read_sprites(payload);assert origin=='RI18.256' and len(frames)==18
    rgb=codec.palette_to_png(palette)
    assert hashlib.sha256(bytes(rgb)).hexdigest()==record['surface']['palette_rgb_sha256']
    checked=[]
    for frame in frames:
        layer=record['surface']['layers'][frame.index];assert not layer.get('empty')
        assert layer['offset']==[frame.x,frame.y] and layer['size']==[frame.width,frame.height]
        start=codec.GLOBAL_HEADER_SIZE+frame.stream_offset
        indices=codec.decode_sprite(data[start:start+frame.stream_length],frame.width,frame.height)
        assert hashlib.sha256(indices).hexdigest()==layer['indexed_sha256']
        image=Image.frombytes('P',(frame.width,frame.height),indices);image.putpalette(rgb);rgba=image.convert('RGBA')
        rgba.putalpha(Image.frombytes('L',rgba.size,bytes(255 if v else 0 for v in indices)))
        path=REPO/layer['png'];assert sha(path)==layer['png_sha256'] and Image.open(path).convert('RGBA').tobytes()==rgba.tobytes()
        checked.append(dict(index=frame.index,png=layer['png'],sha256=sha(path)))
    assert sha(LEGACY/'_ZOOM/RI18.VID')==record['catalogue']['source_sha256']
    for phase in record['catalogue']['selected_phases']: assert sha(REPO/phase['png'])==phase['png_sha256']
    functional_path=folder/'functional-text-index.json';functional=json.loads(functional_path.read_text())
    entry=next(r for r in functional['records'] if r['id']==IDENTITY)
    assert entry['definition_class']==14
    buildings=json.loads((REPO/'content/standard/catalogues/legacy-buildings.json').read_text())['buildings']
    assert next(b for b in buildings if b['id']==IDENTITY)['legacy']['definitionClass']==14
    assert sha(REPO/'content/standard/catalogues/legacy-gameplay.json')==refs['gameplay_sha256']
    description=next(r for r in entry['descriptions'] if r['record']==918)
    text_path=LEGACY/'_TEXT/ENGLISH.TXT';raw=text_path.read_bytes();text=raw[description['offset']:description['offset']+description['byte_length']]
    assert hashlib.sha256(text).hexdigest()==description['sha256'] and b'missile silos' in text
    decompile_path=REPO/'artifacts/fragile-le-decompilation/FRAGILE.LE.decompiled.c';decompile=decompile_path.read_text()
    dispatcher,dispatch=function(decompile,'UpdateAsteroidSurfaceBuildingAnimationDescriptors')
    launch,launch_body=function(decompile,'UpdateMissileSiloLaunchSpriteFrame')
    heading,heading_body=function(decompile,'UpdateBuildingTurretSpriteFrame')
    assert 'if (bVar1 < 0xe)' in dispatch and 'if (bVar1 < 0xf)' in dispatch and launch['name']+'(' in dispatch
    assert '*(short *)(iVar2 + 0x1c)' in launch_body and '*(short *)(iVar2 + 0x1e)' in launch_body
    assert 'uVar2 + 8' in heading_body
    code_paths=[REPO/'src/OpenFA.Core/Presentation/LegacyBuildingSpriteFrameSelector.cs',
        REPO/'src/OpenFA.Assets/FrontEnd/LegacySurfaceObjectRenderer.Part1.cs',REPO/'src/OpenFA.Assets/FrontEnd/LegacySurfaceObjectRenderer.Part2.cs']
    sources=[refs_path,functional_path,decompile_path,folder/'rigellian-missile-launcher-study.md',
        folder/'rigellian-building-reference-review.md',REPO/'content/standard/catalogues/legacy-buildings.json',
        REPO/'content/standard/catalogues/legacy-gameplay.json',REPO/'docs/assets/bootstrap-3d/full-catalogue/recipes.json',Path(__file__).with_name('directional_catalogue_rules.py')]+code_paths
    return dict(issue=1114,reviewer_sha256=sha(Path(__file__)),
        source_sha256={str(p.relative_to(REPO)).replace('\\','/'):sha(p) for p in sources},
        legacy_source_sha256={str(p.relative_to(LEGACY)).replace('\\','/'):sha(p) for p in [LEGACY/'_B/_B',LEGACY/'_ZOOM/RI18.VID',text_path]},
        checked_surface_layers=checked,checked_catalogue_phases=record['catalogue']['selected_phases'],
        records=[dict(id=IDENTITY,classification='missile-silo-launch-activity',definition_class=14,
            functional_record=description,functional_text=text.decode('cp1252'),
            dispatch_evidence=[dispatcher,launch,heading],surface_activity_descriptors=list(range(2,18)),
            heading_rig_requirement_established=False,launch_activity_requirement_established=True,
            historical_heading_rule_status='Reviewed prototype heuristic; not evidence requiring a yaw head on this silo.',
            observed='Upper shell opens toward a circular aperture; catalogue phases reveal/highlight the same view.',
            source_semantics='Class 14 dispatches to launch activity, separately from heading selection; no attached launch record selects descriptor 2.',
            unresolved=['Exact cap leaf geometry/kinematics and final mixed-colour composition','3D state/direction calibration and client cross-culture selector behavior'],
            final_visual_acceptance=False)],
        scope='Source-reviewed classification bound to exact files. Existing #970/#990 findings are retained, not a new model or proof of current client end-to-end behavior.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    report=build()
    if args.check: assert json.loads(TARGET.read_text())==report,'Reviewed mechanism source bindings changed'
    else: TARGET.write_text(json.dumps(report,indent=2)+'\n')
    print('RI18_STATE_SEMANTICS_OK',len(report['checked_surface_layers']),len(report['checked_catalogue_phases']))


if __name__=='__main__': main()
