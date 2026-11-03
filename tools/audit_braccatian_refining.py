"""Completion audit for all 38 Braccatian decisions, source evidence and preserved gallery assets."""
import argparse
from collections import Counter
import hashlib
import importlib
import json
from pathlib import Path
import struct
import subprocess
import sys
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gallery_animation_assets import animation_previews,glb_clips
from register_braccatian_refinements import CASES
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'sources/docs/reconstruction/models'
BASE='cf2843c751be17d697d65e6b9e43136f9261354a'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def assert_identity(entry,canonical):
    assert entry['id']==canonical['id'] and entry['name']==canonical['name'],('Decision identity mismatch',entry['id'],entry['name'],canonical['name'])


def validate_scope(rows,canonical):
    assert len(rows)==len(canonical)==38 and len({x['id'] for x in rows})==38
    assert {x['id'] for x in rows}==set(canonical)
    assert Counter(x['category'] for x in rows)==dict(buildings=23,ships=5,missiles=10)
    for row in rows:assert_identity(row,canonical[row['id']])
    assert Counter(x['decision'] for x in rows)=={'refined':26,'retained-after-focused-review':12}


def decode_films(legacy):
    sys.path.insert(0,str(legacy/'tools'));video=importlib.import_module('fragile_vid');baseline=read(DOCS/'braccatian-refining-baseline.json');assert sha(legacy/'tools/fragile_vid.py')==baseline['video_codec_sha256'] and sha(legacy/'FRAGILE.EXE')==baseline['executable_sha256'];result=[]
    for row in baseline['records']:
        if row['category']!='buildings':continue
        source=legacy/'_ZOOM'/(row['key']+'.VID');assert sha(source)==row['catalogue_source_sha256'];dest=ROOT/'artifacts/issue-190/final-audit-decoded'/row['key'];video.export_png(source,dest,legacy/'FRAGILE.EXE');frames=sorted((dest/'frames').glob('*.png'));old=ROOT/'artifacts/issue-190/references'/row['key']/'catalogue/frames';assert len(frames)==row['catalogue_phases']==41
        for p in frames:assert Image.open(p).convert('RGBA').tobytes()==Image.open(old/p.name).convert('RGBA').tobytes()
        result.append(dict(key=row['key'],source_sha256=sha(source),decoded_frames_sha256=hashlib.sha256(json.dumps([[p.name,sha(p)] for p in frames],separators=(',',':')).encode()).hexdigest(),frames=len(frames)))
    path=ROOT/'artifacts/issue-190/final-audit-decoded/films.json';path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('FRESH_BUILDING_FILMS_VERIFIED',len(result),sum(x['frames'] for x in result),flush=True)


def source_evidence(legacy):
    sys.path.insert(0,str(legacy/'tools'));codec=importlib.import_module('fragile256');baseline=read(DOCS/'braccatian-refining-baseline.json');assert sha(legacy/'tools/fragile256.py')==baseline['codec_sha256'];archives={};sprite_records=[];_,_,palette,_=codec.read_sprites(legacy/'_MS/BUTTONS.256');game_palette=codec.palette_to_png(palette)
    for row in baseline['records']:
        source=row['surface'];directory=source['source_directory']
        if directory not in archives:
            path=legacy/directory/directory;assert sha(path)==baseline['archives'][directory];_,blob,entries=codec.read_archive(path);archives[directory]={e.name:blob[e.offset:e.offset+e.length] for e in entries}
        payload=archives[directory][source['source_entry']];assert hashlib.sha256(payload).hexdigest()==source['source_sha256'];private=ROOT/'artifacts/issue-190/final-audit-decoded'/row['key'];private.mkdir(parents=True,exist_ok=True);path=private/source['source_entry'];path.write_bytes(payload);raw,frames,palette,_=codec.read_sprites(path);colours=game_palette if directory=='_M' else codec.palette_to_png(palette);assert hashlib.sha256(colours).hexdigest()==source['palette_rgb_sha256'];assert len(frames)==len(source['layers']);filled=0
        for frame,old in zip(frames,source['layers']):
            assert [frame.width,frame.height]==old['size'] and [frame.x,frame.y]==old['offset']
            if not frame.width or not frame.height:continue
            start=codec.GLOBAL_HEADER_SIZE+frame.stream_offset;indices=codec.decode_sprite(raw[start:start+frame.stream_length],frame.width,frame.height);assert hashlib.sha256(indices).hexdigest()==old['indexed_sha256'];im=Image.frombytes('P',(frame.width,frame.height),indices);im.putpalette(colours);rgba=im.convert('RGBA');rgba.putalpha(Image.frombytes('L',im.size,bytes(255 if v else 0 for v in indices)));assert sha(ROOT/old['png'])==old['png_sha256'] and rgba.tobytes()==Image.open(ROOT/old['png']).convert('RGBA').tobytes();filled+=1
        sprite_records.append(dict(key=row['key'],descriptor_count=len(frames),populated_descriptors=filled,payload_sha256=source['source_sha256']))
    lore=read(DOCS/'braccatian-lore-evidence.json');cdb=(legacy/lore['source']['path_relative_to_legacy']).read_bytes();assert hashlib.sha256(cdb).hexdigest()==lore['source']['sha256'];records=cdb.split(b'\0');assert set(range(33,62))<={r['record'] for r in lore['records']}
    for item in lore['records']:assert hashlib.sha256(records[item['record']]).hexdigest()==item['sha256']
    functional=read(DOCS/'functional-text-index.json');text=(legacy/functional['sources']['language_file']['relative_to_legacy']).read_bytes();assert hashlib.sha256(text).hexdigest()==functional['sources']['language_file']['sha256'];functions=[r for r in functional['records'] if r.get('culture')=='braccatian'];assert len(functions)==38;passages=0
    for row in functions:
        for item in [row['name_reference']]+row['descriptions']:
            assert hashlib.sha256(text[item['offset']:item['offset']+item['byte_length']]).hexdigest()==item['sha256'];passages+=1
    return dict(sprites=sprite_records,full_cdb_records_revalidated=len(lore['records']),functional_definitions=38,functional_names_and_passages_revalidated=passages,building_films=read(ROOT/'artifacts/issue-190/final-audit-decoded/films.json'))


def check_model(row,study,report_path,generator,verifier):
    model=ROOT/study['blend'];meta=read(model.with_suffix('.json'));report=read(report_path);assert meta['id']==row['id'];assert report['generator_sha256']==meta['generator_sha256']==sha(ROOT/'sources/tools/blender'/generator);assert report['verifier_sha256']==sha(ROOT/'sources/tools/blender'/verifier)
    for ext in ['blend','glb']:assert sha(model.with_suffix('.'+ext))==meta[ext+'_sha256']==report[ext+'_sha256']
    assert study['sha256']==meta['blend_sha256'] and report['native_mesh_count']==report['imported_mesh_count'];assert report['maximum_native_imported_position_error']<1e-4
    for data,key in [(meta,'dependency_sha256'),(meta,'helper_sha256'),(report,'verifier_dependencies_sha256')]:
        for n,digest in data.get(key,{}).items():assert sha(ROOT/'sources/tools/blender'/n)==digest
    for n,digest in meta.get('texture_sha256',{}).items():assert sha(ROOT/n)==digest
    for key,name in [('lore_sha256','braccatian-lore-evidence.json'),('functional_sha256','functional-text-index.json')]:
        if key in meta:assert meta[key]==sha(DOCS/name)
    if meta.get('source_study'):assert sha(ROOT/meta['source_study'])==meta['source_blend_sha256']
    for side in ['native','imported']:
        if 'native_structure' in report:assert report[side+'_structure']['positive_closed_meshes']==report[side+'_mesh_count']
        else:assert report[side+'_contract']['closed_positive_meshes']==report[side+'_mesh_count']
    for view,result in report['renders'].items():
        assert result['native_sha256']==sha(report_path.parent/(view+'.png')) and result['imported_sha256']==sha(report_path.parent/('imported-'+view+'.png'));assert result['silhouette_iou']>.99998 and result['foreground_rgb_mean_difference_255']<1
    raw=model.with_suffix('.glb').read_bytes();length,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a;glb=json.loads(raw[20:20+length]);assert sum('mesh' in n for n in glb['nodes'])==report['imported_mesh_count']
    clips=glb_clips(model.with_suffix('.glb'));baseline=ROOT/row['baseline_study'];assert clips==glb_clips(baseline.with_suffix('.glb'))
    actual=animation_previews(study['blend'],study['glb'],(ROOT/study['image']).parent);assert len(actual)==len(clips)==len(study['animations'])
    for preview in actual:assert preview['frames']>1 and preview['distinct_pose_count']>1
    if row['key']=='BR03':assert report['native_structure']['continuous_flared_casings'] and report['native_structure']['independent_grounded_units']==3
    if row['key']=='BR06':assert len(report['native_structure']['open_arched_entrances'])==3 and all(x['clear_depth']>.5 and len(x['clear_heights'])==3 for x in report['native_structure']['open_arched_entrances'])
    if row['key']=='BR08':assert report['native_structure']['actual_blue_collared_towers']==6 and report['native_structure']['open_ward_entrances']==3
    if row['key'] in ['BR11','BR12','BR19']:
        assert report['retained_animation_curves_equal'] and len(report['pose_frames'])==9 and report['source_preservation_position_error']<1e-4
        assert len(report['native_open_aperture_heights'])==len(report['imported_open_aperture_heights'])==49
    if row['key'] in ['BR18','BR20','BR23']:assert report['retained_heading_controller_and_action'] and len(report['pose_frames'])==17
    if row['key']=='BR4C':assert report['native_structure']['expanded_core_volume']>4.5 and report['native_structure']['expanded_core_radial_sections'][1]>.85 and max(abs(x) for x in report['native_structure']['radial_casing_to_hemisphere_gaps'])<.04
    return meta,report,actual


def preservation(catalogue):
    prior=json.loads(subprocess.check_output(['git','show',BASE+':gallery/catalogue.json'],cwd=ROOT));current={r['id']:r for r in catalogue};tree=subprocess.check_output(['git','ls-tree','-r',BASE],cwd=ROOT,text=True);objects={line.split('\t',1)[1]:line.split()[2] for line in tree.splitlines()};studies=movies=0
    for row in prior:
        for study in row['studies']:
            actual=next(s for s in current[row['id']]['studies'] if s['blend']==study['blend']);assert actual==study
            assert sha(ROOT/study['blend'])==study['sha256'];studies+=1
            for key in ['glb','image']:
                data=(ROOT/study[key]).read_bytes();assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==objects[study[key]]
            for clip in study['animations']:assert sha(ROOT/clip['video'])==clip['sha256'];movies+=1
    assert studies==406 and movies==43
    return dict(base=BASE,prior_studies_preserved=studies,prior_glb_files_preserved=studies,prior_posters_preserved=studies,prior_movies_preserved=movies)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--legacy-root',type=Path,required=True);parser.add_argument('--decoder-python',type=Path);parser.add_argument('--decode-films-only',action='store_true');args=parser.parse_args()
    if args.decode_films_only:decode_films(args.legacy_root);return
    decoder=args.decoder_python or Path(sys.executable);subprocess.run([str(decoder),str(Path(__file__)),'--legacy-root',str(args.legacy_root),'--decode-films-only'],check=True)
    evidence=source_evidence(args.legacy_root);baseline=read(DOCS/'braccatian-refining-baseline.json');catalogue=read(ROOT/'gallery/catalogue.json');canonical={r['id']:r for r in catalogue if r['culture']=='braccatian'};ship=read(DOCS/'braccatian-ship-decisions.json');missile=read(DOCS/'braccatian-missile-decisions.json');decisions={r['id']:r for r in ship['records']+missile['records']};rows=[];render_count=meshes=0;max_error=0.;min_iou=1.
    for row in baseline['records']:
        cat=canonical[row['id']];assert_identity(row,cat)
        if row['category']=='buildings':
            key=row['key'].lower();study=next(s for s in cat['studies'] if s['blend']==f'sources/docs/assets/reconstruction/braccatian-refined/{key}/model.blend');validation=ROOT/study['image'];validation=validation.parent/'validation.json';generator,verifier=CASES[key];decision='refined'
        else:
            choice=decisions[row['id']];assert_identity(choice,cat);study=next(s for s in cat['studies'] if s['blend']==choice['model']);validation=ROOT/choice['validation'];assert sha(validation)==choice['validation_sha256'];decision=choice['decision'];generator='refine_braccatian_ships.py' if decision=='refined' else 'build_braccatian_'+row['id'].rsplit('/',1)[1].replace('-','_')+'.py';verifier='verify_refined_braccatian_ships.py' if row['category']=='ships' else 'verify_braccatian_missile_retention.py'
        for ext in ['blend','glb']:assert sha((ROOT/row['baseline_study']).with_suffix('.'+ext))==row[ext+'_sha256']
        meta,report,clips=check_model(row,study,validation,generator,verifier);render_count+=len(report['renders']);meshes+=report['native_mesh_count'];max_error=max(max_error,report['maximum_native_imported_position_error']);min_iou=min(min_iou,min(r['silhouette_iou'] for r in report['renders'].values()))
        reason=decisions[row['id']]['reason'] if row['id'] in decisions else meta['observed'];rows.append(dict(id=row['id'],key=row['key'],name=row['name'],category=row['category'],decision=decision,reason=reason,model=study['blend'],glb=study['glb'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],validation=validation.relative_to(ROOT).as_posix(),validation_sha256=sha(validation),closed_meshes=report['native_mesh_count'],paired_renders=len(report['renders']),animations=clips))
    validate_scope(rows,canonical);retention=preservation(catalogue);station=read(DOCS/'orbital-station-audit.json');assert station['manifest_sha256']==sha(DOCS/'orbital-station-variants.json') and station['gallery_sha256']==sha(ROOT/'gallery/catalogue.json') and station['totals']['pairs']==7
    for row in station['records']:
        pair=next(x for x in read(DOCS/'orbital-station-variants.json')['records'] if x['key']==row['key'])
        for v in ['finished','construction']:assert row[v+'_validation_sha256']==sha(ROOT/pair[v]['validation'])
    scitek=read(DOCS/'braccatian-scitek-evidence.json');assert len(scitek['records'])==36 and scitek['no_direct_braccatian_previews'];assert scitek['audit_tool_sha256']==sha(ROOT/'tools/audit_braccatian_scitek_references.py')
    for row in scitek['records']:assert sha(args.legacy_root/row['information_source']['directoryName']/row['information_source']['fileName'])==row['source_sha256']
    # A current, source-bound visual summary includes retained models honestly.
    sheet=Image.new('RGB',(1800,1930),(25,29,33));draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=15);draw.text((15,10),'BRACCATIAN | 38 reviewed definitions: 26 refined studies, 12 retained models',fill='white',font=font)
    for i,row in enumerate(rows):
        d=(ROOT/row['validation']).parent;im=Image.open(d/'front-quarter.png').convert('RGBA');im=im.crop(im.getchannel('A').getbbox());im.thumbnail((245,205));x=(i%7)*257;y=45+(i//7)*310;sheet.paste(im,(x+(250-im.width)//2,y+(210-im.height)//2),im);draw.text((x+8,y+225),row['key']+' '+row['name'],fill='white',font=font);draw.text((x+8,y+250),row['decision'],fill=(170,190,200),font=ImageFont.load_default(size=12))
    overview=ROOT/'gallery/sheets/braccatian-refining-completion.jpg';sheet.save(overview,quality=92)
    dependencies=['register_braccatian_refinements.py','register_braccatian_ship_refinements.py','register_braccatian_missile_review.py','gallery_animation_assets.py'];proofs=['braccatian-refining-baseline.json','braccatian-lore-evidence.json','braccatian-scitek-evidence.json','braccatian-ship-decisions.json','braccatian-missile-evidence.json','braccatian-missile-decisions.json','orbital-station-audit.json','orbital-station-variants.json','functional-text-index.json']
    result=dict(issue=190,scope='Full 38-definition Braccatian asset refining and seven-culture station extension; final artistic/gameplay calibration separate',audit_tool_sha256=sha(Path(__file__)),audit_dependencies_sha256={n:sha(ROOT/'tools'/n) for n in dependencies},evidence_sha256={n:sha(DOCS/n) for n in proofs},gallery_sha256=sha(ROOT/'gallery/catalogue.json'),overview=dict(path=overview.relative_to(ROOT).as_posix(),sha256=sha(overview)),totals=dict(definitions=38,buildings=23,ships=5,missiles=10,refined_normal_studies=26,retained_normal_models=12,closed_normal_meshes=meshes,paired_normal_renders=render_count,minimum_render_iou=min_iou,maximum_position_error=max_error,station_pairs=7),preservation=retention,source_review=evidence,scitek=dict(subjects=36,image_updates=sum(x['image_updates'] for x in scitek['records']),timeline_frames=sum(x['timeline_frames'] for x in scitek['records']),sampled_updates_visually_reviewed=sum(len(x['sampled_updates']) for x in scitek['records']),provenance=scitek['decode_provenance']),records=rows,limitations=['Exact alloys, hidden sections, transverse profiles and repeated hidden detail counts remain authored','Source projection, runtime scale/orientation and equipment mounts require game integration calibration','Sci-Tek visual review samples 648 updates and does not claim inspection of every decoded frame; no direct Braccatian subject binding','Construction activity timing is authored; complete station evidence is separately audited'])
    out=DOCS/'braccatian-refining-completion.json';out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('BRACCATIAN_FULL_REFINING_AUDIT_OK',result['totals'],retention,flush=True)


if __name__=='__main__':main()
