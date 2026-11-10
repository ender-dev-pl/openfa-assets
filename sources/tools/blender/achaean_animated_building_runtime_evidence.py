"""Source-bound acceptance for the animated AC12 remaster; client acceptance is separate."""
import hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
from achaean_building_runtime_evidence import digest
from achaean_static_building_runtime_evidence import exported_triangles

VIEWS=['front-quarter','front','rear-quarter','half-open-front-quarter','open-front-quarter']


def pixel_pairs(directory):
    rows=[]
    for view in VIEWS:
        a=Image.open(directory/f'native-{view}.png').convert('RGBA');b=Image.open(directory/f'imported-{view}.png').convert('RGBA');assert a.size==b.size==(512,512)
        bbox=ImageChops.lighter(a.getchannel('A'),b.getchannel('A')).getbbox();assert bbox
        margin=min(bbox[0],bbox[1],512-bbox[2],512-bbox[3]);assert margin>=24
        mean=max(ImageStat.Stat(ImageChops.difference(a,b).crop(bbox)).mean);assert mean<1,(view,mean)
        rows.append(dict(view=view,maximum_channel_mean_difference=mean,margin=margin))
    return rows


def verify_animation_document(meta,report,doc):
    assert meta['key']=='AC12' and report['clips']==['LaunchFacilityCycle']
    animation,=doc['animations'];assert animation['name']=='LaunchFacilityCycle'
    channels=animation['channels'];assert len(channels)==12
    expected=set(meta['animation']['retained_open_translations']);assert len(expected)==12
    assert {doc['nodes'][c['target']['node']]['name'] for c in channels}==expected
    assert all(c['target']['path']=='translation' for c in channels)
    assert all(s.get('interpolation','LINEAR')=='LINEAR' for s in animation['samplers'])
    inputs=[doc['accessors'][s['input']] for s in animation['samplers']]
    assert abs(min(a['min'][0] for a in inputs)-1/30)<1e-6 and abs(max(a['max'][0] for a in inputs)-61/30)<1e-6
    assert report['maximum_animation_matrix_error']<3e-5
    for label in ['native_motion','imported_motion']:
        motion=report[label];assert motion['frames']==list(range(1,62))
        assert motion['surface_pair_checks']==13542 and motion['surface_intersections']==0
        assert motion['maximum_moving_radius']<1.185 and motion['minimum_moving_z']>.38 and motion['maximum_moving_z']<.461
        assert motion['closed_cycle_equal'] is True and motion['retained_travel_error']<1e-5
        assert len(motion['open_floor_heights'])==9 and all(.085<h<.095 for h in motion['open_floor_heights'])
        assert motion['coral_roughness_range']>.2
        assert len(motion['root_matrix'])==16 and max(abs(v-(1 if i%5==0 else 0)) for i,v in enumerate(motion['root_matrix']))<1e-5
    assert report['native_root_matrix']==report['native_motion']['root_matrix']
    assert report['continuous_sweep_proven'] is report['descriptor17_composition_verified'] is False


def verify(root,record):
    root=Path(root).resolve();project=root.parent if root.name=='sources' else root
    proof=record['reviewed_model']['runtime_evidence'];assert proof['format']=='achaean-animated-building-remaster-v1'
    assert proof['scope']=='blender-native-and-imported-glb' and proof['game_client_integration'] is False
    assert record['culture']=='achaean' and record['category']=='buildings'
    def path(rel):
        p=(project/rel).resolve();assert p.is_relative_to(project) and p.is_file(),rel;return p
    files=proof['files']
    for rel,h in files.items():assert digest(path(rel))==h,'Changed evidence: '+rel
    study,=record['available_studies'];assert study['blend']==record['reviewed_model']['blend']
    folder='sources/'+Path(study['blend']).parent.as_posix()
    meta=json.loads(path(folder+'/model.json').read_bytes());report=json.loads(path(folder+'/runtime-review.json').read_bytes());visual=json.loads(path(folder+'/visual-review.json').read_bytes())
    assert meta['id']==report['id']==record['id']==visual['id']=='openfa:building/legacy/162'
    assert meta['footprint']==record['footprint'] and meta['definition_class']==record['legacy_identity']['definitionClass'] and meta['construction_updates']==record['legacy_identity']['constructionUpdates']
    assert meta['binaries']==report['binaries']==visual['binaries']
    for ext,h in meta['binaries'].items():assert files[folder+'/model.'+ext]==h
    assert study['sha256']==record['reviewed_model']['sha256']==meta['binaries']['blend']
    assert hashlib.sha256(path(folder+'/model.json').read_bytes()).hexdigest()==report['metadata_sha256']
    assert meta['author'] in report['helpers'] and report['verifier'] in report['helpers']
    assert path(meta['author']).is_relative_to(project/'sources/tools/blender') and path(meta['author']).suffix=='.py'
    assert hashlib.sha256(path(meta['author']).read_bytes()).hexdigest()==meta['author_sha256']
    for rel,h in report['helpers'].items():assert rel in files and hashlib.sha256(path(rel).read_bytes()).hexdigest()==h
    assert report['maximum_bidirectional_surface_error']<1e-5 and report['texture_pixels_equal'] is True
    assert report['positive_closed_meshes']['native']==report['positive_closed_meshes']['imported']==report['meshes']==meta['mesh_nodes']
    assert report['game_client_integration'] is report['final_artistic_acceptance'] is visual['final_user_artistic_acceptance'] is False
    raw=path(folder+'/model.glb').read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
    assert exported_triangles(doc)==meta['triangles']==report['triangles']<meta['triangle_budget']<=30000
    assert len(doc['materials'])==report['materials']==meta['materials']<=12 and sum('mesh'in n for n in doc['nodes'])==report['meshes']<=180
    assert all('bufferView'in image for image in doc['images'])
    verify_animation_document(meta,report,doc)
    media=project/proof['render_directory'];assert media.resolve().is_relative_to(project/'gallery/media')
    assert set(report['renders'])=={label+'-'+view+'.png' for label in ['native','imported'] for view in VIEWS}
    for name,h in report['renders'].items():assert hashlib.sha256(path(proof['render_directory']+'/'+name).read_bytes()).hexdigest()==h
    assert visual['pixel_pairs']==pixel_pairs(media)
    assert visual['runtime_report_sha256']==hashlib.sha256(path(folder+'/runtime-review.json').read_bytes()).hexdigest()
    assert 1<=len(visual['concept_attempts'])<=3
    for a in visual['concept_attempts']:assert files[a['image']]==a['sha256'] and a['feedback'] and a['prompt'] in files
    manifest=json.loads(path(proof['render_directory']+'/animation-previews.json').read_bytes())
    assert manifest['renderer'] in files and manifest['renderer_sha256']==hashlib.sha256(path(manifest['renderer']).read_bytes()).hexdigest()
    for rel,h in manifest['renderer_helpers'].items():assert rel in files and hashlib.sha256(path(rel).read_bytes()).hexdigest()==h
    assert manifest['glb_sha256']==meta['binaries']['glb'] and manifest['blend_sha256']==meta['binaries']['blend']
    preview,=manifest['clips'];assert preview['name']=='LaunchFacilityCycle' and preview['frames']==48 and preview['fps']==24 and preview['distinct_pose_count']>20
    assert preview['video'] in files and files[preview['video']]==preview['sha256']
    return dict(id=record['id'],files=len(files),views=len(report['renders']),scope=proof['scope'],game_client_integration=False)
