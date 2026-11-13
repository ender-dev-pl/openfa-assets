"""Keep finished orbital stations distinct from legacy frame-1 construction."""
import hashlib,json,struct
from pathlib import Path

def clips(path):
    with path.open('rb') as stream:
        header=stream.read(20)
        if header[:4]!=b'glTF':raise ValueError('Invalid station GLB')
        document=json.loads(stream.read(struct.unpack_from('<I',header,12)[0]))
    return {entry.get('name') for entry in document.get('animations',[])}

def verify(root,registry):
    root=Path(root);path=root/'project/orbital-station-variants.json'
    if not path.is_file():return 0
    declaration=json.loads(path.read_text(encoding='utf-8'));stations=declaration['stations']
    expected={'achaean','artemian','braccatian','mauna','mikotaj','rigellian'}
    if len(stations)!=6 or {row['culture'] for row in stations}!=expected:raise ValueError('Incomplete orbital station state coverage')
    models={row['path']:row for row in registry['models']};catalogue={row['id']:row for row in registry['catalogue']}
    for row in stations:
        finished=row['finished'];construction=row['construction']
        if finished['legacy_sprite_frame']!=0 or construction['legacy_sprite_frame']!=1:raise ValueError('Station legacy frame roles changed')
        if finished['glb']==construction['glb'] or finished['glb_sha256']==construction['glb_sha256']:raise ValueError('Finished station aliases construction model')
        primary=catalogue[row['id']]['studies'][0]
        if any(primary[key]!=finished[key] for key in ['blend','glb']):raise ValueError('Primary station must be the finished model')
        for state,purpose in [(finished,'canonical-definition'),(construction,'construction-animation')]:
            for kind in ['blend','glb']:
                entry=models.get(state[kind]);target=root/state[kind]
                if not entry or not target.is_file():raise ValueError('Missing functional station state: '+state[kind])
                digest=hashlib.sha256(target.read_bytes()).hexdigest()
                if digest!=state[kind+'_sha256'] or digest!=entry['sha256'] or entry['purpose']!=purpose:raise ValueError('Changed functional station state: '+state[kind])
        if construction['clip'] not in clips(root/construction['glb']) or construction['clip'] in clips(root/finished['glb']):raise ValueError('ConstructionActivity must belong only to the construction model')
        metadata=json.loads((root/construction['glb']).with_suffix('.json').read_text(encoding='utf-8'))
        if metadata.get('variant')!='construction' or metadata.get('legacy_sprite_frame')!=1 or metadata['source_study']!=finished['blend']:raise ValueError('Construction model source-study role differs')
        for kind in ['blend','glb']:
            if metadata['source_'+kind+'_sha256']!=finished[kind+'_sha256']:raise ValueError('Finished station differs from verified construction source')
        sources=primary.get('animation_sources',[])
        if not any(all(item.get(k)==construction[k] for k in ['blend','glb']) for item in sources):raise ValueError('Station construction animation missing from gallery')
    evidence=declaration.get('runtime_evidence')
    if evidence:
        proof=json.loads((root/evidence).read_text(encoding='utf-8'))
        if hashlib.sha256((root/proof['verifier']).read_bytes()).hexdigest()!=proof['verifier_sha256']:raise ValueError('Changed restoration runtime verifier')
        reports={item['id']:item for item in proof['models']}
        if set(reports)!={item['id'] for item in stations}:raise ValueError('Missing station runtime evidence')
        for row in stations:
            report=reports[row['id']]
            if any(report[k+'_sha256']!=row['finished'][k+'_sha256'] for k in ['blend','glb']):raise ValueError('Restoration runtime binaries changed')
            if len(report['renders'])!=2:raise ValueError('Missing native/imported restoration renders')
            for name,digest in report['renders'].items():
                if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('Changed restoration runtime render')
    print('ORBITAL_STATION_STATES_VERIFIED',len(stations),'finished and construction pairs')
    return len(stations)

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    verify(root,json.loads((root/'project/canonical-assets.json').read_text(encoding='utf-8')))
