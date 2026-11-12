"""Bind the hidef mobile fleet to actual native/imported Blender evidence."""
import hashlib
import json
from pathlib import Path
from PIL import Image
import numpy as np


def digest(path):
    raw=Path(path).read_bytes()
    if Path(path).suffix in {'.py','.json'}:raw=raw.replace(b'\r\n',b'\n')
    return hashlib.sha256(raw).hexdigest()


def verify(root,record):
    root=Path(root).resolve();project=root.parent
    model=record['reviewed_model'];proof=model['runtime_evidence']
    assert proof['format']=='rigellian-mobile-hidef-v1'
    assert proof['game_client_integration'] is False
    def bound(relative,expected):
        target=(root/relative).resolve()
        assert target.is_relative_to(project) and target.is_file(),relative
        assert digest(target)==expected,('Stale bound evidence',relative)
        return target
    folder=Path(model['blend']).parent
    required={proof['report'],proof['visual_report'],str(folder/'model.blend').replace('\\','/'),str(folder/'model.glb').replace('\\','/'),str(folder/'model.json').replace('\\','/'),'tools/blender/build_rigellian_mobile_fleet.py','tools/blender/verify_rigellian_mobile_fleet.py','tools/blender/rigellian_mobile_runtime_evidence.py'}
    assert required<=proof['files'].keys(),'Incomplete bound runtime evidence'
    for relative,value in proof['files'].items():bound(relative,value)
    report=json.loads((root/proof['report']).read_text())
    meta=json.loads((root/Path(model['blend']).parent/'model.json').read_text())
    visual=json.loads((root/proof['visual_report']).read_text())
    assert meta['id']==report['id']==record['id']==visual['id']
    for ext in ['blend','glb']:
        path=root/Path(model['blend']).parent/('model.'+ext)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==report[ext+'_sha256']==meta[ext+'_sha256']==visual[ext+'_sha256']
    assert model['sha256']==meta['blend_sha256']
    for label,file in [('generator','build_rigellian_mobile_fleet.py'),('verifier','verify_rigellian_mobile_fleet.py')]:
        assert hashlib.sha256((root/'tools/blender'/file).read_bytes()).hexdigest()==report[label+'_sha256']
    assert report['maximum_bidirectional_position_error']<1e-5 and report['closed_pressure_hull'] and report['source_unchanged']
    assert report['unobstructed_drive_exit_ray_checks_native']>0 and report['unobstructed_drive_exit_ray_checks_imported']>0
    media=project/visual['media']
    for name,value in report['renders'].items():assert hashlib.sha256((media/name).read_bytes()).hexdigest()==value
    a=np.array(Image.open(media/'verified-native.png').convert('RGBA'));b=np.array(Image.open(media/'verified-imported.png').convert('RGBA'))
    first=a[:,:,3]>16;second=b[:,:,3]>16;overlap=first&second
    assert (first&second).sum()/(first|second).sum()>.999
    assert np.abs(a[:,:,:3].astype(float)-b[:,:,:3]).mean(axis=2)[overlap].mean()<1
    assert visual['observations'] and visual['legacy_entries'] and not visual['user_artistic_acceptance']
    for key,accepted in record['acceptance'].items():
        if accepted:assert record['acceptance_evidence'][key]['files']==proof['files']
    return dict(id=record['id'],scope='blender-native-and-imported-glb',game_client_integration=False)


def bind(project,record,ship):
    project=Path(project);root=project/'sources';folder=project/ship['canonical_directory']
    report=folder/'runtime-verification.json';visual=folder/'legacy-visual-review.json'
    assert visual.is_file(),'Actual visual review must precede acceptance binding'
    files=[folder/('model.'+ext) for ext in ['blend','glb','json']]+[report,visual]
    files += [root/'tools/blender'/name for name in ['build_rigellian_mobile_fleet.py','verify_rigellian_mobile_fleet.py','rigellian_mobile_runtime_evidence.py']]
    proof=dict(format='rigellian-mobile-hidef-v1',report=report.relative_to(root).as_posix(),visual_report=visual.relative_to(root).as_posix(),game_client_integration=False,files={p.relative_to(root).as_posix():digest(p) for p in files})
    record['reviewed_model']=dict(blend=(folder/'model.blend').relative_to(root).as_posix(),sha256=hashlib.sha256((folder/'model.blend').read_bytes()).hexdigest(),runtime_evidence=proof)
    record['acceptance_evidence']={key:dict(files=proof['files'],scope='Agent legacy/concept review and Blender native/import evidence;user artistic and game acceptance pending') for key,value in record['acceptance'].items() if value}
    verify(root,record)
