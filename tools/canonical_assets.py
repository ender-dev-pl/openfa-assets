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
 from verify_orbital_station_variants import verify as verify_station_states
 verify_station_states(root,data)
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
    clips=selected_animation_previews(blend,glb,folder)
    for source in study.get('animation_sources',[]):
        clips+=selected_animation_previews(source['blend'],source['glb'],ROOT/source['media'])
    return clips


def preview_renderer(manifest):
    relative=Path(manifest.get('renderer_path',manifest.get('renderer','sources/tools/blender/render_gallery_animations.py')))
    assert not relative.is_absolute() and '..' not in relative.parts,'Expected repository-relative preview renderer'
    renderer=(ROOT/relative).resolve()
    assert renderer.is_relative_to((ROOT/'sources/tools/blender').resolve()) and renderer.suffix=='.py' and renderer.is_file(),'Invalid preview renderer'
    return renderer

def selected_animation_previews(blend,glb,media):
    from gallery_animation_assets import animation_previews,glb_clips
    manifest_path=Path(media)/'animation-previews.json'
    if not manifest_path.is_file():return animation_previews(blend,glb,media)
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    if 'renderer_path' not in manifest:return animation_previews(blend,glb,media)
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    clips=glb_clips(ROOT/glb)
    assert manifest['blend_sha256']==sha(ROOT/blend) and manifest['glb_sha256']==sha(ROOT/glb)
    assert manifest['renderer_sha256']==sha(preview_renderer(manifest))
    assert len(manifest['clips'])==len(clips)
    for actual,preview in zip(clips,manifest['clips']):
        assert all(actual[key]==preview[key] for key in actual)
        video=(ROOT/preview['video']).resolve()
        assert video.is_relative_to((ROOT/'gallery/media').resolve()) and sha(video)==preview['sha256']
        assert preview['distinct_pose_count']>1
    return manifest['clips']
