"""Exact-byte evidence bundles for published mobile remaster inventory gates."""
from functools import lru_cache
from pathlib import Path
from archive_evidence import verify_bound_input
import hashlib,json

FORMAT='mobile-remaster-runtime-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_bytes().decode('utf-8-sig'))


@lru_cache(maxsize=4)
def tool_index(root):
    root=Path(root);result={}
    for p in sorted(list((root/'sources/tools/blender').glob('*.py'))+list((root/'tools').glob('*.py'))):
        result.setdefault(sha(p),p.relative_to(root).as_posix())
    return result


def binary_hashes(report):
    return report.get('binaries') or dict(blend=report.get('blend_sha256',report.get('source_sha256')),glb=report.get('glb_sha256',report.get('export_sha256')))


def bind_record(root,record):
    root=Path(root).resolve();relative=record['available_studies'][0]['blend'];folder=root/'sources'/Path(relative).parent
    metadata=load(folder/'model.json');runtime=load(folder/'runtime-verification.json');tools=tool_index(str(root));files={}
    def add(p):
        p=Path(p).resolve();assert p.is_relative_to(root) and p.is_file(),p
        name=p.relative_to(root).as_posix();files[name]=sha(p);return name
    def tool(digest):
        assert digest in tools,('Unknown runtime/source tool',record['id'],digest)
        return add(root/tools[digest])
    model=add(folder/'model.blend');add(folder/'model.glb');meta=add(folder/'model.json');proof=add(folder/'runtime-verification.json')
    visual=next((p for p in [folder/'concept-review.json',folder/'reference-evidence.json',folder.parent/'fleet-style.json'] if p.is_file()),None)
    assert visual is not None,('Missing reference/visual evidence',record['id']);visual=add(visual)
    for name in ['delivery-review.json','generation.json','recipe.json']:
        if (folder/name).is_file():add(folder/name)
    if metadata.get('baseline_sha256'):add(root/'sources'/metadata['source']/'model.blend')
    for document in [metadata,runtime]:
        for key,value in document.items():
            if key.endswith('_sha256') and isinstance(value,str) and value in tools:tool(value)
    media=root/'gallery/media'/Path(relative).parent
    for name,digest in runtime['renders'].items():
        assert sha(media/name)==digest,('Stale runtime render',name);add(media/name)
    native=add(media/'verified-native.png');imported=add(media/'verified-imported.png')
    evidence=dict(format=FORMAT,scope='blender-native-and-imported-glb',text_hash_policy='exact-bytes',game_client_integration=False,metadata=meta,runtime_report=proof,visual_review=visual,generator=tool(runtime['generator_sha256']),verifier=tool(runtime['verifier_sha256']),native_render=native,imported_render=imported,files=files)
    record['reviewed_model']=dict(blend=relative,sha256=files[model],runtime_evidence=evidence)
    record['acceptance_evidence']={gate:dict(report=proof if gate=='native_and_glb_runtime' else visual,sha256=files[proof if gate=='native_and_glb_runtime' else visual],scope='Bound agent/source evidence only; final user and client acceptance remain separate') for gate,accepted in record['acceptance'].items() if accepted}
    verify_record(root/'sources',record)


def verify_record(source_root,record):
    source_root=Path(source_root).resolve();root=source_root.parent;assert source_root.name=='sources' and (root/'project/layout.json').is_file()
    reviewed=record['reviewed_model'];proof=reviewed['runtime_evidence'];assert proof['format']==FORMAT
    assert proof['scope']=='blender-native-and-imported-glb' and proof['text_hash_policy']=='exact-bytes' and proof['game_client_integration'] is False
    files=proof['files'];assert isinstance(files,dict) and files
    def path(relative):
        p=(root/relative).resolve();assert p.is_relative_to(root),'Runtime evidence must remain in repository'
        assert relative.startswith(('sources/','gallery/media/')) or (p.parent==root/'tools' and p.suffix=='.py'),'Unsupported evidence location'
        return p
    for name in files:path(name)
    for name,digest in files.items():assert path(name).is_file() and sha(path(name))==digest,'Runtime evidence changed: '+name
    model=(source_root/reviewed['blend']).resolve();assert model.is_relative_to(source_root)
    relative=model.relative_to(root).as_posix();folder=Path(relative).parent
    required=[relative,(folder/'model.glb').as_posix(),(folder/'model.json').as_posix(),(folder/'runtime-verification.json').as_posix()]
    required += [proof.get(k) for k in ['metadata','runtime_report','visual_review','generator','verifier','native_render','imported_render']]
    assert all(isinstance(p,str) and p in files for p in required),'Incomplete bound runtime evidence'
    assert proof['metadata']==(folder/'model.json').as_posix() and proof['runtime_report']==(folder/'runtime-verification.json').as_posix()
    for key in ['generator','verifier']:assert path(proof[key]).is_relative_to(source_root/'tools/blender') and path(proof[key]).suffix=='.py'
    metadata=load(path(proof['metadata']));runtime=load(path(proof['runtime_report']));assert metadata['id']==runtime['id']==record['id'],'Runtime evidence catalogue identity differs'
    binaries={kind:files[(folder/('model.'+kind)).as_posix()] for kind in ['blend','glb']}
    assert binary_hashes(metadata)==binary_hashes(runtime)==binaries,'Runtime report/binary revision differs'
    assert binaries['blend']==reviewed['sha256']
    assert reviewed['blend'] in {s['blend'] for s in record['available_studies'] if s['present'] and s['sha256']==reviewed['sha256']}
    assert metadata.get('generator_sha256',runtime['generator_sha256'])==runtime['generator_sha256']==sha(path(proof['generator']))
    assert runtime['verifier_sha256']==sha(path(proof['verifier']))
    if metadata.get('recipe_sha256'):
        recipe=(folder/'recipe.json').as_posix();assert recipe in files and files[recipe]==metadata['recipe_sha256']==runtime['recipe_sha256']
    if metadata.get('baseline_sha256'):
        baseline='sources/'+metadata['source']+'/model.blend';verify_bound_input(root,proof,baseline,metadata['baseline_sha256'])
    assert metadata['triangles']==runtime['triangles'] and metadata['mesh_batches']==runtime['mesh_batches']
    error=next((runtime[k] for k in ['source_import_position_error','maximum_bidirectional_world_position_error','maximum_bidirectional_position_error'] if k in runtime),None)
    assert isinstance(error,(int,float)) and 0<=error<1e-4,'Missing/failed independent import position evidence'
    media=Path('gallery/media')/Path(reviewed['blend']).parent;views=runtime['renders'];assert 'verified-native.png' in views and 'verified-imported.png' in views
    assert proof['native_render']==(media/'verified-native.png').as_posix() and proof['imported_render']==(media/'verified-imported.png').as_posix()
    for name,digest in views.items():
        image=(media/name).as_posix();assert image in files and files[image]==digest,'Unbound render pixels: '+image
    for gate,accepted in record['acceptance'].items():
        if accepted:
            evidence=record.get('acceptance_evidence',{}).get(gate);assert isinstance(evidence,dict),'Acceptance requires explicit evidence'
            assert evidence['report']==proof['runtime_report' if gate=='native_and_glb_runtime' else 'visual_review'],'Acceptance gate points to the wrong report'
            assert evidence['report'] in files and evidence['sha256']==files[evidence['report']]
    return dict(id=record['id'],files=len(files),views=len(views),scope=proof['scope'],game_client_integration=False,format=FORMAT)
