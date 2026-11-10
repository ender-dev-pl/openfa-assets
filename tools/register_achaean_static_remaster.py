"""Select one static Achaean source only after genuine runtime and visual review."""
import argparse,hashlib,json,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sources/tools/blender'))
from achaean_static_building_runtime_evidence import digest,verify

def write(path,data):
    raw=path.read_bytes() if path.exists() else b'';text=json.dumps(data,indent=2)+'\n';path.write_bytes(text.replace('\n','\r\n').encode('utf-8') if b'\r\n' in raw else text.encode('utf-8'))

def main(model):
    folder=model.resolve();assert folder.is_relative_to((ROOT/'sources/objects/achaean').resolve())
    meta=json.loads((folder/'model.json').read_bytes());runtime=json.loads((folder/'runtime-review.json').read_bytes());visual=json.loads((folder/'visual-review.json').read_bytes());assert meta['id']==runtime['id']==visual['id'];assert visual['final_user_artistic_acceptance'] is False
    media=ROOT/'gallery/media/objects/achaean'/folder.name;shutil.copyfile(media/'imported-front-quarter.png',media/'front-quarter.png')
    docs=ROOT/'sources/docs/reconstruction/models';inventory_path=docs/'inventory.json';inventory=json.loads(inventory_path.read_bytes());record=next(r for r in inventory['records'] if r['id']==meta['id']);relative=(folder/'model.blend').relative_to(ROOT/'sources').as_posix();old=record['available_studies']
    if not any(s['blend']==relative for s in old):
        record.setdefault('historical_studies',[]).extend(old)
        if record.get('reviewed_model'):record.setdefault('historical_runtime_review',record['reviewed_model'])
    record['available_studies']=[dict(stage='canonical-game-remaster',blend=relative,present=True,sha256=meta['binaries']['blend'],media=media.relative_to(ROOT).as_posix(),final_visual_acceptance='not-established',views=[dict(label='Legacy-based ImageGen concept (interpreted details)',image=visual['concept_attempts'][-1]['image']),dict(label='Actual independent GLB',image=(media/'imported-front-quarter.png').relative_to(ROOT).as_posix()),dict(label='Actual independent GLB rear',image=(media/'imported-rear-quarter.png').relative_to(ROOT).as_posix())])]
    paths={*folder.glob('*.json'),folder/'model.blend',folder/'model.glb',*media.glob('*.png'),*(ROOT/'sources/materials/achaean'/folder.name).glob('*.png')}
    paths.update(ROOT/p for p in runtime['helpers'])
    for attempt in visual['concept_attempts']:paths.update([ROOT/attempt['image'],ROOT/attempt['prompt']])
    proof=dict(format='achaean-static-building-remaster-v2',scope='blender-native-and-imported-glb',game_client_integration=False,render_directory=media.relative_to(ROOT).as_posix(),files={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)})
    record['reviewed_model']=dict(blend=relative,sha256=meta['binaries']['blend'],runtime_evidence=proof);record['acceptance']['native_and_glb_runtime']=True;number=visual['legacy']['functional_record'];assert number in record['functional_reference']['description_records'];record['functional_reference']['review_status']='reviewed-original-record-'+str(number);record.setdefault('acceptance_evidence',{})['native_and_glb_runtime']=['Actual saved-native/independent GLB with model-specific anatomy, textures and six real renders; client/final user artistic acceptance separate.',(folder/'runtime-review.json').relative_to(ROOT/'sources').as_posix(),(folder/'visual-review.json').relative_to(ROOT/'sources').as_posix()]
    verify(ROOT/'sources',record);write(inventory_path,inventory)
    path=docs/'achaean-building-remaster-delivery.json';delivery=json.loads(path.read_bytes());delivery['models']=[r for r in delivery['models'] if r['id']!=meta['id']];delivery['models'].append(dict(id=meta['id'],key=meta['key'],name=meta['name'],blend=(folder/'model.blend').relative_to(ROOT).as_posix(),glb=(folder/'model.glb').relative_to(ROOT).as_posix(),binaries=meta['binaries'],triangles=meta['triangles'],meshes=meta['mesh_nodes'],materials=runtime['materials'],embedded_images=runtime['embedded_images'],footprint=meta['footprint'],definition_class=meta['definition_class'],construction_updates=meta['construction_updates'],root='PlacementRoot',root_matrix=runtime['native_root_matrix'],native_world_bounds=runtime['native_world_bounds'],axes='Blender -Y front, +Z up',state_contract=meta['state_contract'],scale_contract=meta['scale_contract'],superseded_studies=[s['blend'] for s in record.get('historical_studies',[])],reuse='One current payload for gameplay/build/SciTek. Historical studies are not package selections.',limits='Client scale/state integration, Android frame time and final user artistic acceptance remain separate.'));delivery['models'].sort(key=lambda r:r['key']);delivery['pending']=[key for key in delivery['pending'] if key!=meta['key']];write(path,delivery)
    print('ACHAEAN_STATIC_REGISTERED',meta['key'],len(proof['files']))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--model',type=Path,required=True);main(parser.parse_args().model)
