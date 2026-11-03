"""Re-decode all Braccatian missile descriptors and bind focused review evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OBSERVED={
'mega-blast':'Two broad gold expansions separated by a thin banded waist, copper forward neck and gold terminals.',
'flaming-ruin':'A broad continuous gold body with longitudinal divisions, copper neck/coupling and gold terminals.',
'volcano':'A long narrow copper shaft between two broad gold collars, with gold terminals; the waist must remain exposed.',
'multi-blast':'One broad gold rear section, narrow banded connecting shaft and separate small gold terminal regions.',
'dancing-bolt':'Broad gold/yellow-green central body with visible bands and longitudinal divisions, red terminal pieces.',
'hotbomb':'Two expanded end regions with gold side castings/collars and a much narrower copper-coloured middle.',
'outbreak':'Two separated gold masses with conspicuous pink side castings, narrow copper connection and gold terminals.',
'anti-outbreak':'One broad continuous gold chamber with pink side fittings and exposed copper forward/aft regions.',
'midwinter':'Gold central body with yellow-green bands/longitudinal regions, copper neck and small gold terminal regions.',
'comms-killer':'Two substantial gold bodies around a narrow central join, with copper-coloured terminals and longitudinal highlight regions.'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def find(value,target):
    if isinstance(value,dict):
        if value.get('id')==target:return value
        children=value.values()
    elif isinstance(value,list):children=value
    else:return None
    for child in children:
        found=find(child,target)
        if found:return found


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--legacy-root',type=Path,required=True);args=parser.parse_args();legacy=args.legacy_root;sys.path.insert(0,str(legacy/'tools'));import fragile256 as codec
    docs=ROOT/'sources/docs/reconstruction/models';baseline=json.loads((docs/'braccatian-refining-baseline.json').read_text());functional=json.loads((docs/'functional-text-index.json').read_text());lore=json.loads((docs/'braccatian-lore-evidence.json').read_text());scitek=json.loads((docs/'braccatian-scitek-evidence.json').read_text());assert scitek
    _,archive,entries=codec.read_archive(legacy/'_M/_M');entries={e.name:e for e in entries};language=(legacy/'_TEXT/ENGLISH.TXT').read_bytes();assert hashlib.sha256(language).hexdigest()==functional['sources']['language_file']['sha256'];cdb=(legacy/'_TEXT/ENGLISH.CDB').read_bytes();assert hashlib.sha256(cdb).hexdigest()==lore['source']['sha256'];records=cdb.split(b'\0');_,_,game_palette,_=codec.read_sprites(legacy/'_MS/BUTTONS.256');colours=codec.palette_to_png(game_palette)
    for item in lore['records']:assert hashlib.sha256(records[item['record']]).hexdigest()==item['sha256']
    rows=[]
    for row in baseline['records']:
        if row['category']!='missiles':continue
        surface=row['surface'];assert hashlib.sha256(colours).hexdigest()==surface['palette_rgb_sha256'];entry=entries[surface['source_entry']];payload=archive[entry.offset:entry.offset+entry.length];assert hashlib.sha256(payload).hexdigest()==surface['source_sha256'];private=ROOT/'artifacts/issue-190/missile-review'/row['key'];private.mkdir(parents=True,exist_ok=True);path=private/surface['source_entry'];path.write_bytes(payload);raw,frames,palette,_=codec.read_sprites(path);assert len(frames)==len(surface['layers'])==14;decoded=[]
        for frame,old in zip(frames,surface['layers']):
            start=codec.GLOBAL_HEADER_SIZE+frame.stream_offset;indices=codec.decode_sprite(raw[start:start+frame.stream_length],frame.width,frame.height);assert hashlib.sha256(indices).hexdigest()==old['indexed_sha256'];im=Image.frombytes('P',(frame.width,frame.height),indices);im.putpalette(colours);rgba=im.convert('RGBA');rgba.putalpha(Image.frombytes('L',im.size,bytes(255 if v else 0 for v in indices)));assert rgba.tobytes()==Image.open(ROOT/old['png']).convert('RGBA').tobytes();out=private/(f"{old['index']:03}.png");rgba.save(out);decoded.append(dict(index=old['index'],size=list(rgba.size),indices_sha256=old['indexed_sha256'],png=out.relative_to(ROOT).as_posix(),png_sha256=sha(out)))
        function=find(functional,row['id']);name=function['name_reference'];assert hashlib.sha256(language[name['offset']:name['offset']+name['byte_length']]).hexdigest()==name['sha256'];assert not function['descriptions'];slug=row['id'].rsplit('/',1)[1];source=ROOT/row['baseline_study']
        for ext in ['blend','glb']:assert sha(source.with_suffix('.'+ext))==row[ext+'_sha256']
        rows.append(dict(id=row['id'],key=row['key'],name=row['name'],slug=slug,model=row['baseline_study'],blend_sha256=row['blend_sha256'],glb_sha256=row['glb_sha256'],source_entry=surface['source_entry'],payload_sha256=surface['source_sha256'],decoded_frames=decoded,functional_record=function,observed=OBSERVED[slug],review='All fourteen correctly paletted descriptors visually reviewed. Descriptors 0-6 provide heading changes, 7-9 body/reveal states and 10-13 the body plus bright exhaust. Exhaust is not solid missile geometry. Exact historical frame sequencing/timing is not newly recovered here.',candidate_decision='Retain pending fresh native/independent GLB and render review: major visible form/colour regions already present; do not invent subpixel machinery.',uncertainty='Exact transverse profiles, hidden sections, alloy identity and detailed projection remain authored. Comms Killer faceting and HotBomb casting cross-sections are existing interpretations, not proven by tiny sprites.'))
    out=dict(issue=190,culture='braccatian',scope='All ten missiles / 140 descriptors; source review before runtime decisions',review_tool_sha256=sha(Path(__file__)),palette_source='_MS/BUTTONS.256 runtime palette; embedded missile palettes are grayscale placeholders',palette_file_sha256=sha(legacy/'_MS/BUTTONS.256'),palette_rgb_sha256=hashlib.sha256(colours).hexdigest(),archive_sha256=sha(legacy/'_M/_M'),codec_sha256=sha(legacy/'tools/fragile256.py'),baseline_sha256=sha(docs/'braccatian-refining-baseline.json'),lore_sha256=sha(docs/'braccatian-lore-evidence.json'),functional_index_sha256=sha(docs/'functional-text-index.json'),scitek_evidence_sha256=sha(docs/'braccatian-scitek-evidence.json'),cultural_scope='Complete Braccatian CDB and functional mappings reviewed previously; original bytes revalidated here. Bronze Age analogy does not identify an alloy or require decorative missile machinery. No mapped per-missile narrative exists beyond catalogue name/effect-role evidence.',scitek_scope='The completed 36-subject audit contains no Braccatian preview binding. Generic/other-culture technical films do not establish missing Braccatian missile geometry or operating motion.',records=rows)
    (docs/'braccatian-missile-evidence.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print('BRACCATIAN_MISSILE_SOURCE_REVIEW_OK',len(rows),sum(len(x['decoded_frames']) for x in rows))


if __name__=='__main__':main()
