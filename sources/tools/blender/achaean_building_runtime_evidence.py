"""Check source-bound Achaean runtime evidence and recompute rendered pixel parity."""
import hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageChops,ImageStat

def digest(path):
    path=Path(path);data=path.read_bytes()
    if path.suffix in ['.py','.json','.txt']:data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()

def pixel_pairs(directory):
    rows=[]
    for view in ['front-quarter','front','rear-quarter']:
        a=Image.open(directory/f'native-{view}.png').convert('RGBA');b=Image.open(directory/f'imported-{view}.png').convert('RGBA');assert a.size==b.size==(512,512)
        bbox=ImageChops.lighter(a.getchannel('A'),b.getchannel('A')).getbbox();assert bbox
        assert min(bbox[0],bbox[1],512-bbox[2],512-bbox[3])>=24
        delta=ImageStat.Stat(ImageChops.difference(a,b).crop(bbox));mean=max(delta.mean);assert mean<1.0,(view,mean)
        rows.append(dict(view=view,maximum_channel_mean_difference=mean,margin=min(bbox[0],bbox[1],512-bbox[2],512-bbox[3])))
    return rows

def verify(root,record):
    root=Path(root).resolve();project=root.parent if root.name=='sources' else root;proof=record['reviewed_model']['runtime_evidence'];assert proof['format']=='achaean-building-remaster-v1';assert proof['scope']=='blender-native-and-imported-glb' and proof['game_client_integration'] is False
    def path(rel):
        p=(project/rel).resolve();assert p.is_relative_to(project) and p.is_file(),rel;return p
    files=proof['files']
    for rel,h in files.items():assert digest(path(rel))==h,'Changed evidence: '+rel
    study,=record['available_studies'];assert study['blend']==record['reviewed_model']['blend'];folder='sources/'+Path(study['blend']).parent.as_posix();meta=json.loads(path(folder+'/model.json').read_bytes());report=json.loads(path(folder+'/runtime-review.json').read_bytes());visual=json.loads(path(folder+'/visual-review.json').read_bytes());assert meta['id']==report['id']==record['id']=='openfa:building/legacy/151';assert meta['binaries']==report['binaries']==visual['binaries']
    for ext,h in meta['binaries'].items():assert files[folder+'/model.'+ext]==h
    assert study['sha256']==record['reviewed_model']['sha256']==meta['binaries']['blend'];assert hashlib.sha256(path(folder+'/model.json').read_bytes()).hexdigest()==report['metadata_sha256'];assert meta['author_sha256']==hashlib.sha256(path('sources/tools/blender/remaster_achaean_footprint.py').read_bytes()).hexdigest();assert report['verifier_sha256']==hashlib.sha256(path('sources/tools/blender/verify_achaean_footprint.py').read_bytes()).hexdigest()
    assert report['maximum_bidirectional_surface_error']<1e-5;assert report['texture_pixels_equal'] is True;assert report['positive_closed_meshes']['native']==report['positive_closed_meshes']['imported']==report['meshes']==meta['mesh_nodes'];assert report['game_client_integration'] is report['final_artistic_acceptance'] is visual['final_user_artistic_acceptance'] is False
    raw=path(folder+'/model.glb').read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives']);assert tri==meta['triangles']==report['triangles']<30000;assert not doc.get('animations') and report['clips']==[];assert len(doc['materials'])==report['materials']==6
    media=project/proof['render_directory'];assert media.resolve().is_relative_to(project/'gallery/media')
    for image,h in report['renders'].items():assert hashlib.sha256(path(proof['render_directory']+'/'+image).read_bytes()).hexdigest()==h
    assert 1<=len(visual['concept_attempts'])<=3;assert visual['runtime_report_sha256']==hashlib.sha256(path(folder+'/runtime-review.json').read_bytes()).hexdigest();assert visual['pixel_pairs']==pixel_pairs(media)
    for a in visual['concept_attempts']:assert files[a['image']]==a['sha256'] and a['feedback'] and a['prompt'] in files
    return dict(id=record['id'],files=len(files),views=len(report['renders']),scope=proof['scope'],game_client_integration=False)
