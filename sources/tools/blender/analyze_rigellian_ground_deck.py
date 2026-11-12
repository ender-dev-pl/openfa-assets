"""Measure RI10 reference descriptors and document the legacy class-26 state law."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

REPO=Path(__file__).resolve().parents[2]
TARGET=REPO/'docs/reconstruction/models/rigellian-ground-deck-mechanism.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def descriptor(altitude):
    # FRAGILE.LE 0x44BE0: signed SHIPS+0x3c, class-26 dispatcher 0x451xx.
    activity=1
    if altitude is not None and altitude<192:
        if altitude < -191:
            return 2
        distance=abs(altitude)
        activity=20-distance*20//192
    return min(activity,16)+1


def measure(record):
    result=[]
    for layer in record['surface']['layers']:
        item=dict(index=layer['index'],size=layer['size'],offset=layer['offset'])
        if layer.get('empty'):
            item['role']='Empty descriptor: no cover mesh or geometry to invent'
            result.append(item)
            continue
        path=REPO/layer['png'];assert sha(path)==layer['png_sha256']
        with Image.open(path) as image:
            alpha=image.convert('RGBA').getchannel('A');box=alpha.getbbox()
            item.update(png_sha256=sha(path),opaque_pixels=sum(v>0 for v in alpha.tobytes()),alpha_bounds=list(box))
            if 2<=layer['index']<=14:
                halves=[]
                for side,x0,x1 in [('left',0,image.width//2),('right',image.width//2,image.width)]:
                    mask=alpha.crop((x0,0,x1,image.height));bounds=mask.getbbox();assert bounds
                    left,top,right,bottom=bounds
                    halves.append(dict(side=side,source_bounds=[left+x0+layer['offset'][0],top+layer['offset'][1],right+x0+layer['offset'][0],bottom+layer['offset'][1]],
                        projected_width=right-left,projected_height=bottom-top,opaque_pixels=sum(v>0 for v in mask.tobytes())))
                item['halves']=halves
                item['role']='Paired green cover overlay'
            else:
                item['role']={0:'Separate shadow descriptor',1:'Static base with deep hangar-access shaft, vertical wall features and red fittings',17:'Lower structure plus mixed purple shadow pixels; not a cover pose'}[layer['index']]
        result.append(item)
    return result


def gold_regions(record):
    layer=next(item for item in record['surface']['layers'] if item['index']==1)
    with Image.open(REPO/layer['png']) as opened:
        image=opened.convert('RGBA');width,height=image.size
        points=set()
        for y in range(height):
            for x in range(width):
                r,g,b,a=image.getpixel((x,y))
                if a>0 and r>g*1.15 and g>b*1.2 and r>45: points.add((x,y))
    components=[]
    while points:
        seed=min(points);points.remove(seed);pending=[seed];group=[seed]
        while pending:
            x,y=pending.pop()
            for neighbour in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if neighbour in points:
                    points.remove(neighbour);pending.append(neighbour);group.append(neighbour)
        if len(group)>5:
            bounds=[min(p[0] for p in group),min(p[1] for p in group),max(p[0] for p in group)+1,max(p[1] for p in group)+1]
            components.append(dict(pixels=len(group),bounds=bounds))
    components.sort(key=lambda item:item['bounds'])
    front=[item for item in components if item['bounds'][1]>=17 and item['bounds'][3]==height]
    assert len(front)==2
    centres=[(item['bounds'][0]+item['bounds'][2])/2 for item in front]
    return dict(source_layer=1,source_size=[width,height],png_sha256=layer['png_sha256'],
        method='4-connected opaque RGB mask: R>1.15*G, G>1.2*B, R>45; components larger than five pixels',
        interpretation='Colour-based diagnostic regions; front support assignment was checked visually and does not establish exact 3D dimensions',
        components=components,front_support_regions=front,front_region_centre_spacing_fraction=(centres[1]-centres[0])/width)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    manifest=REPO/'docs/reconstruction/models/rigellian-building-references.json'
    record=next(r for r in json.loads(manifest.read_text())['buildings'] if r['key']=='RI10')
    assert record['definition_class']==26 and record['footprint']==[3,3]
    layers=measure(record)
    assert [x['index'] for x in layers if x.get('role','').startswith('Empty')]==[15,16]
    covers=[x for x in layers if 'halves' in x]
    for side in [0,1]:
        widths=[x['halves'][side]['projected_width'] for x in covers]
        assert all(a>=b for a,b in zip(widths,widths[1:])),widths
    bands=[]
    for altitude in range(-32768,32768):
        frame=descriptor(altitude)
        if bands and bands[-1]['frame']==frame: bands[-1]['altitude_max']=altitude
        else: bands.append(dict(altitude_min=altitude,altitude_max=altitude,frame=frame))
    decomp=REPO/'artifacts/fragile-le-decompilation/FRAGILE.LE.decompiled.c'
    text=decomp.read_text();start=text.index('/* UpdateLandingPadActivitySpriteFrame at 0x00044BE0 */');end=text.index('/* UpdateMissileSiloLaunchSpriteFrame',start)
    source=text[start:end]
    assert 'iVar3 = 0x14 - (iVar2 * 0x14) / 0xc0;' in source
    assert 'if (iVar2 < -0xbf)' in source and 'if (0x10 < iVar3)' in source
    dispatch_start=text.index('if (bVar1 < 0x1a) goto LAB_000452d4;')
    dispatch=text[dispatch_start:dispatch_start+350]
    assert 'if (bVar1 < 0x1b)' in dispatch and 'UpdateLandingPadActivitySpriteFrame' in dispatch
    selector=REPO/'src/OpenFA.Core/Presentation/LegacyBuildingSpriteFrameSelector.cs'
    gameplay=REPO/'content/standard/catalogues/legacy-gameplay.json'
    language=REPO.parent/'legacy/_TEXT/ENGLISH.TXT';language_bytes=language.read_bytes()
    text_entries=[]
    for offset,label in [(0x1137e,'Ground Deck identity'),(0xf421,'Landing Pad function'),(0xf2a0,'Ship Yard and underground hangars')]:
        payload=language_bytes[offset:language_bytes.index(b'\0',offset)]
        text_entries.append(dict(offset=hex(offset),label=label,sha256=hashlib.sha256(payload).hexdigest(),text=payload.decode('cp1252')))
    assert text_entries[0]['text']=='The Ground Deck is the Rigellian Landing Pad.'
    assert 'vast underground hangars' in text_entries[1]['text']
    result=dict(issue=980,id=record['id'],name=record['name'],definition_class=26,footprint=[3,3],
        reference_manifest_sha256=sha(manifest),source_payload_sha256=record['surface']['source_sha256'],palette_rgb_sha256=record['surface']['palette_rgb_sha256'],
        functional_description=dict(source='../legacy/_TEXT/ENGLISH.TXT',sha256=sha(language),entries=text_entries,
            conclusion='Surface access to underground spacecraft hangars; an open deep shaft, not a grille or shallow landing floor'),
        gold_region_measurements=gold_regions(record),measurements=layers,legacy_mapping=dict(function='UpdateLandingPadActivitySpriteFrame',address='0x44BE0',
            dispatcher_class=26,input='Attached SHIPS signed 16-bit altitude at +0x3c; absent record selects descriptor 2',
            no_attached_ship_frame=descriptor(None),signed_altitude_bands=bands,
            function_text_sha256=hashlib.sha256(source.encode()).hexdigest(),dispatcher_excerpt_sha256=hashlib.sha256(dispatch.encode()).hexdigest(),
            semantics='State depends on altitude; it is not a fixed-rate 16-frame turntable or arbitrary timer'),
        runtime_scope=dict(selector_sha256=sha(selector),gameplay_sha256=sha(gameplay),configured_landing_pad_id='terran:landing-pad',
            alien_mapping_verified=False,note='Legacy class dispatcher covers class 26. Current selector/configuration explicitly names Terran landing pad; full alien integration requires separate tracing.'),
        observed=['Paired overlays lose projected width until only thin outer strips remain','Static base reveals a deep hangar-access shaft with vertical wall features and red fittings','Descriptor 15 and 16 are empty; descriptor 17 contains lower structure and mixed shadow pixels'],
        unresolved=['Retraction versus hinge rotation is not uniquely established by these low-resolution contours','Hidden pocket/hinge geometry, cover thickness, sweep clearances and animation timing','Source-to-world projection and attachment/calibration in game runtime'],
        planned_assemblies=['Identity PlacementRoot with fixed static shell/interior','Independent left/right cover roots; axis and motion require render comparison','Separate lower-structure/shadow composition state, not a fabricated third cover'],
        original_pixels_distributed=False,final_visual_acceptance=False)
    serialized=json.dumps(result,indent=2)+'\n'
    if args.check:
        assert json.loads(TARGET.read_text())==result,'Stale RI10 mechanism evidence'
    else: TARGET.write_text(serialized)
    print('RI10_MECHANISM_REFERENCE_VERIFIED',len(layers),'descriptors',len(bands),'signed altitude bands')


if __name__=='__main__': main()
