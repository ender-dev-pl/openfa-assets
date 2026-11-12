"""Decode all Rigellian building layers and catalogue phases as reference-only evidence."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image,ImageDraw

REPO=Path(__file__).resolve().parents[2]
LEGACY=REPO.parent/'legacy'
OUT=REPO/'artifacts/rigellian-building-reference-study'
TARGET=REPO/'docs/reconstruction/models/rigellian-building-references.json'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def composite(layers,root,indices,name,check):
    selected=[layer for layer in layers if layer['index'] in indices and not layer.get('empty')]
    assert selected
    left=min(layer['offset'][0] for layer in selected);top=min(layer['offset'][1] for layer in selected)
    right=max(layer['offset'][0]+layer['size'][0] for layer in selected)
    bottom=max(layer['offset'][1]+layer['size'][1] for layer in selected)
    result=Image.new('RGBA',(right-left,bottom-top))
    for layer in selected:
        with Image.open(REPO/layer['png']) as im:
            result.alpha_composite(im,(layer['offset'][0]-left,layer['offset'][1]-top))
    path=root/name
    if not check: result.save(path)
    assert path.is_file() and Image.open(path).convert('RGBA').tobytes()==result.tobytes()
    return dict(layers=[layer['index'] for layer in selected],offset=[left,top],
        png=str(path.relative_to(REPO)).replace('\\','/'),png_sha256=sha(path))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    sys.path.insert(0,str(LEGACY/'tools'))
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    import fragile256 as codec
    import fragile_vid as video
    from review_assault_fighter import tile
    catalogue=REPO/'content/standard/catalogues/legacy-buildings.json'
    buildings=[r for r in json.loads(catalogue.read_text())['buildings'] if r['factionId']=='openfa:faction/rigellian']
    gameplay=REPO/'content/standard/catalogues/legacy-gameplay.json'
    def find_rules(value):
        if isinstance(value,dict):
            if 'directionalBodyDefinitionIds' in value: return value
            for child in value.values():
                found=find_rules(child)
                if found is not None: return found
        return None
    rules=find_rules(json.loads(gameplay.read_text()));assert rules is not None
    assert len(buildings)==23
    _,payload,entries=codec.read_archive(LEGACY/'_B/_B');archive={entry.name:entry for entry in entries}
    records=[];sheet=Image.new('RGB',(1800,1600),(20,25,34));draw=ImageDraw.Draw(sheet)
    for ordinal,building in enumerate(buildings):
        key=f"RI{building['legacy']['localType']+1:02}";root=OUT/key;root.mkdir(parents=True,exist_ok=True)
        entry=archive[key+'.256'];raw=payload[entry.offset:entry.offset+entry.length];path=root/(key+'.256')
        if not path.exists() or path.read_bytes()!=raw: path.write_bytes(raw)
        data,frames,palette,origin=codec.read_sprites(path);assert origin==key+'.256'
        rgb=codec.palette_to_png(palette);layers=[]
        for frame in frames:
            if not frame.width or not frame.height:
                layers.append(dict(index=frame.index,size=[frame.width,frame.height],offset=[frame.x,frame.y],empty=True))
                continue
            start=codec.GLOBAL_HEADER_SIZE+frame.stream_offset
            indices=codec.decode_sprite(data[start:start+frame.stream_length],frame.width,frame.height)
            im=Image.frombytes('P',(frame.width,frame.height),indices);im.putpalette(rgb)
            rgba=im.convert('RGBA');rgba.putalpha(Image.frombytes('L',rgba.size,bytes(255 if value else 0 for value in indices)))
            png=root/f'surface-{frame.index:02}.png'
            if not args.check: rgba.save(png)
            assert png.is_file() and Image.open(png).convert('RGBA').tobytes()==rgba.tobytes()
            layers.append(dict(index=frame.index,size=[frame.width,frame.height],offset=[frame.x,frame.y],
                indexed_sha256=hashlib.sha256(indices).hexdigest(),png=str(png.relative_to(REPO)).replace('\\','/'),png_sha256=sha(png)))
        source=LEGACY/'_ZOOM'/f'{key}.VID';hologram=root/'hologram'
        if not (hologram/'metadata.json').exists():
            assert not args.check,'Missing decoded video '+key
            video.export_png(source,hologram,LEGACY/'FRAGILE.EXE')
        count=json.loads((hologram/'metadata.json').read_text())['head']['frame_count']
        selected=sorted({0,(count-1)//4,(count-1)//2,3*(count-1)//4,count-1});phases=[]
        for index in selected:
            png=hologram/'frames'/f'{index:03}.png';assert png.is_file()
            phases.append(dict(index=index,png=str(png.relative_to(REPO)).replace('\\','/'),png_sha256=sha(png)))
        phase_sheet=Image.new('RGB',(1500,360),(20,25,34));phase_labels=ImageDraw.Draw(phase_sheet)
        for n,phase in enumerate(phases):
            phase_sheet.paste(tile(REPO/phase['png'],(300,325)),(n*300,30))
            phase_labels.text((n*300+10,8),f"VID phase {phase['index']}; not a spatial-view assertion",fill='white')
        if not args.check: phase_sheet.save(root/'catalogue-phases.png')
        preview=composite(layers,root,[1,2] if len(layers)==18 else [1],'surface-composite-preview.png',args.check)
        combinations=[]
        if len(layers)==18:
            directions=Image.new('RGB',(1000,1000),(20,25,34));labels=ImageDraw.Draw(directions)
            for n,index in enumerate(range(2,18)):
                if layers[index].get('empty'): continue
                combination=composite(layers,root,[1,index],f'layer-combination-{index:02}.png',args.check)
                combinations.append(combination)
                directions.paste(tile(REPO/combination['png'],(250,220)),(n%4*250,n//4*250+28))
                labels.text((n%4*250+10,n//4*250+8),f'Base 1 + layer {index}; diagnostic overlay',fill='white')
            if not args.check: directions.save(root/'layer-combinations.png')
        records.append(dict(id=building['id'],name=building['legacy']['name'],key=key,
            global_type=building['legacy']['globalType'],footprint=[building['footprintWidth'],building['footprintHeight']],
            definition_class=building['legacy']['definitionClass'],
            directional_runtime_path=building['id'] in rules['directionalBodyDefinitionIds'],
            surface=dict(source_sha256=sha(path),palette_rgb_sha256=hashlib.sha256(rgb).hexdigest(),layers=layers,
                preview=preview,layer_combinations=combinations),
            catalogue=dict(source_sha256=sha(source),frame_count=count,selected_phases=phases),
            spatial_views='Not established by phase sampling; requires visual review',final_visual_acceptance=False))
        x=ordinal%6*300;y=ordinal//6*400
        sheet.paste(tile(REPO/preview['png'],(145,330)),(x,y+55))
        sheet.paste(tile(REPO/phases[len(phases)//2]['png'],(145,330)),(x+150,y+55))
        draw.text((x+6,y+8),key+' '+building['legacy']['name'],fill='white')
        draw.text((x+6,y+25),'Surface layer / middle VID phase',fill='white')
        print('RIGELLIAN_REFERENCE',key,len(layers),count,flush=True)
    result=dict(issue=970,culture='rigellian',count=len(records),catalogue_sha256=sha(catalogue),
        archive_sha256=sha(LEGACY/'_B/_B'),gameplay_sha256=sha(gameplay),
        selector_sha256=sha(REPO/'src/OpenFA.Core/Presentation/LegacyBuildingSpriteFrameSelector.cs'),
        composition='Diagnostic base layer 1 plus one extra layer at decoded offsets; not proof of runtime blend, shadow-ramp or activity selection semantics',
        palette='Embedded VGA flags masked, 6-bit channels expanded; index 0 transparent',
        decoder_sha256={name:sha(LEGACY/name) for name in ['tools/fragile256.py','tools/fragile_vid.py','FRAGILE.EXE']},
        interpretation='Catalogue phase sampling is not proof of rotations, animation mechanisms, construction or damage states',buildings=records)
    if args.check: assert json.loads(TARGET.read_text())==result,'Stale Rigellian reference manifest'
    else:
        TARGET.write_text(json.dumps(result,indent=2)+'\n');sheet.save(OUT/'surface-catalogue-sheet.png')
    print('RIGELLIAN_BUILDING_REFERENCES_OK',len(records),flush=True)


if __name__=='__main__': main()
