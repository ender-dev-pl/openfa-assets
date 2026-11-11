"""Revalidate canonical culture-building evidence; never promote artistic/client gates."""
import hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageChops,ImageStat

FORMAT='culture-building-remaster-v1'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def pixel_pairs(media):
    result=[]
    for view in ['front-quarter','front','rear-quarter']:
        a=Image.open(media/('native-'+view+'.png')).convert('RGBA');b=Image.open(media/('imported-'+view+'.png')).convert('RGBA')
        assert a.size==b.size==(512,512),'Unexpected review image size'
        box=ImageChops.lighter(a.getchannel('A'),b.getchannel('A')).getbbox();assert box,'Empty model render'
        margin=min(box[0],box[1],512-box[2],512-box[3]);assert margin>=24,'Clipped review render'
        error=max(ImageStat.Stat(ImageChops.difference(a,b).crop(box)).mean);assert error<1.0,('Native/imported render mismatch',view,error)
        result.append(dict(view=view,maximum_channel_mean_difference=error,margin=margin))
    return result

def verify(source_root,record):
    source_root=Path(source_root).resolve();root=source_root.parent if source_root.name=='sources' else source_root
    proof=record['reviewed_model']['runtime_evidence'];assert proof['format']==FORMAT
    assert proof['scope']=='blender-native-and-imported-glb' and proof['game_client_integration'] is False
    assert record['culture'] in ['mikotaj','artemian','mauna'] and record['category']=='buildings'
    def path(name):
        p=(root/name).resolve();assert p.is_relative_to(root) and p.is_file(),'Evidence path must remain in repository'
        return p
    files=proof['files'];assert files,'Missing bound evidence'
    for name,digest in files.items():assert sha(path(name))==digest,'Changed runtime evidence: '+name
    study,=record['available_studies'];assert study['present'] and study['stage']=='canonical-game-remaster'
    assert study['blend']==record['reviewed_model']['blend'];folder='sources/'+Path(study['blend']).parent.as_posix()
    required=[folder+'/'+name for name in ['model.blend','model.glb','model.json','runtime-review.json','visual-review.json']]
    assert all(name in files for name in required),'Incomplete canonical runtime evidence'
    meta=json.loads(path(folder+'/model.json').read_bytes());runtime=json.loads(path(folder+'/runtime-review.json').read_bytes());visual=json.loads(path(folder+'/visual-review.json').read_bytes())
    assert meta['id']==runtime['id']==visual['id']==record['id'],'Model identity mismatch'
    concept_name=meta['concept_review'];assert concept_name in files,'Concept reference is not bound to this model'
    concept=json.loads(path(concept_name).read_bytes())
    assert concept['id']==record['id'] and concept['key']==meta['key'],'Concept identity mismatch'
    assert len(concept['iterations'])==len(visual['concept_attempts']),'Concept/visual attempt mismatch'
    for actual,reviewed in zip(concept['iterations'],visual['concept_attempts']):
        assert all(actual[name]==reviewed[name] for name in ['attempt','image','sha256','prompt']),'Concept/visual attempt mismatch'
    assert meta['culture']==record['culture'] and meta['footprint']==record['footprint']
    assert meta['binaries']==runtime['binaries']==visual['binaries'],'Stale visual/model revision'
    for kind,digest in meta['binaries'].items():assert files[folder+'/model.'+kind]==digest
    assert study['sha256']==record['reviewed_model']['sha256']==meta['binaries']['blend']
    assert runtime['metadata_sha256']==files[folder+'/model.json']
    assert meta['author'] in files and meta['author_sha256']==files[meta['author']]
    for name,digest in meta.get('textures',{}).items():
        texture=folder.replace('/objects/','/materials/',1)+'/'+name
        assert texture in files and files[texture]==digest,'Unbound material map'
    assert proof['verifier'] in files and runtime['verifier_sha256']==files[proof['verifier']]
    assert runtime['maximum_bidirectional_surface_error']<1e-5 and runtime['texture_pixels_equal'] is True
    assert runtime['positive_closed_meshes']['native']==runtime['positive_closed_meshes']['imported']==runtime['meshes']==meta['mesh_nodes']
    assert runtime['game_client_integration'] is runtime['final_artistic_acceptance'] is visual['final_user_artistic_acceptance'] is False
    assert visual['runtime_report_sha256']==files[folder+'/runtime-review.json']
    raw=path(folder+'/model.glb').read_bytes();assert raw[:4]==b'glTF';doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
    triangles=sum(doc['accessors'][p['indices']]['count']//3 for mesh in doc['meshes'] for p in mesh['primitives'])
    assert triangles==meta['triangles']==runtime['triangles']<=meta['triangle_budget']<=60000,'Export triangle budget mismatch'
    assert len(doc['materials'])==runtime['materials']==meta['materials']
    assert all('bufferView' in image for image in doc.get('images',[])),'External export image'
    assert [clip.get('name','') for clip in doc.get('animations',[])]==runtime['clips']==meta['animation_clips']
    media=(root/proof['render_directory']).resolve();assert media.is_relative_to(root/'gallery/media') and media.is_dir()
    for name,digest in runtime['renders'].items():assert proof['render_directory']+'/'+name in files and sha(media/name)==digest
    assert visual['pixel_pairs']==pixel_pairs(media)
    assert 1<=len(visual['concept_attempts'])<=3
    for attempt in visual['concept_attempts']:
        assert attempt['image'] in files and attempt['prompt'] in files and files[attempt['image']]==attempt['sha256'] and attempt['feedback']
    for accepted,evidence in record.get('acceptance_evidence',{}).items():
        assert record['acceptance'][accepted] and evidence['report'] in files and evidence['sha256']==files[evidence['report']]
    for gate,accepted in record['acceptance'].items():
        if accepted:assert gate in record.get('acceptance_evidence',{}),'Unbound acceptance gate'
    assert not record['acceptance'].get('final_visual_acceptance') and not record['acceptance'].get('attachment_transforms')
    return dict(id=record['id'],triangles=triangles,renders=len(runtime['renders']),scope=proof['scope'],game_client_integration=False)
