"""Validate the explicit canonical model set and private archive boundary."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(root=ROOT):
 return json.loads((root/'project/canonical-assets.json').read_text(encoding='utf-8'))
def verify(root=ROOT):
 data=load(root);actual={p.relative_to(root).as_posix() for p in (root/'sources').rglob('*') if p.suffix in {'.blend','.glb'}}
 expected={x['path'] for x in data['models']}
 if actual!=expected:raise ValueError(('Unregistered or missing model payloads',sorted(actual-expected),sorted(expected-actual)))
 for x in data['models']:
  if hashlib.sha256((root/x['path']).read_bytes()).hexdigest()!=x['sha256']:raise ValueError(('Changed canonical model: refresh its verified selection',x['path']))
 for row in data['catalogue']:
  if len(row['studies'])!=1:raise ValueError(('Expected one canonical study',row['id']))
  for key in ['blend','glb']:
   if row['studies'][0][key] not in expected:raise ValueError(('Unregistered canonical pair',row['id'],key))
 for culture in ['achaean','artemian','braccatian','mauna','mikotaj','rigellian','terran']:
  for role in ['repair','terraform']:
   for ext in ['blend','glb']:
    path=f'sources/proposals/engineering-ships/{culture}/{role}/model.{ext}'
    if path not in expected:raise ValueError(('Engineering ships must remain in main',path))
 for item in data['archive']['files']:
  if (root/item['path']).exists():raise ValueError(('Archived file restored to main',item['path']))
 inventory=root/'sources/docs/reconstruction/models/inventory.json'
 if inventory.is_file():
  archived={x['path']:x for x in data['archive']['files']}
  for row in json.loads(inventory.read_text(encoding='utf-8'))['records']:
   model=row.get('reviewed_model');proof=model.get('runtime_evidence') if isinstance(model,dict) else None
   if not isinstance(proof,dict):continue
   for relative,reference in proof.get('archived_inputs',{}).items():
    path=reference['archive_path'];entry=archived.get(path)
    if path in expected or entry is None or reference['sha256']!=entry['sha256'] or reference['source_blob']!=entry['source_blob'] or reference['archive_commit']!=data['archive']['commit']:
     raise ValueError(('Invalid archived evidence provenance',row['id'],relative))
 print('CANONICAL_BOUNDARY_VERIFIED',len(data['catalogue']),'definitions',len(expected),'model files',len(data['archive']['files']),'archived files')
if __name__=='__main__':verify()


def study_animation_previews(blend,glb,folder,study):
    """Expose a selected model's functional construction animation in the same card."""
    from gallery_animation_assets import animation_previews
    clips=animation_previews(blend,glb,folder)
    for source in study.get('animation_sources',[]):
        clips+=animation_previews(source['blend'],source['glb'],ROOT/source['media'])
    return clips
