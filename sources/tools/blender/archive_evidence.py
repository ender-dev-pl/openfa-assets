"""Check active input bytes or explicit immutable historical-input provenance."""
import hashlib,json
from pathlib import Path

def verify_bound_input(project,proof,relative,expected):
    project=Path(project).resolve()
    if relative in proof['files']:
        target=(project/relative).resolve()
        assert target.is_relative_to(project) and target.is_file(),relative
        assert hashlib.sha256(target.read_bytes()).hexdigest()==expected,'Changed bound input: '+relative
        return 'current-bytes'
    reference=proof.get('archived_inputs',{}).get(relative)
    assert isinstance(reference,dict),'Unbound input: '+relative
    policy=json.loads((project/'project/canonical-assets.json').read_text(encoding='utf-8'))
    name=relative if relative.startswith('sources/') else 'sources/'+relative
    assert reference['archive_path']==name,relative
    entry=next((x for x in policy['archive']['files'] if x['path']==name),None)
    assert entry and name not in {x['path'] for x in policy['models']},relative
    assert not (project/name).exists(),'Historical input unexpectedly restored: '+name
    assert expected==reference['sha256']==entry['sha256'],relative
    assert reference['source_blob']==entry['source_blob'],relative
    assert reference['archive_commit']==policy['archive']['commit'],relative
    return 'historical-input-provenance'
