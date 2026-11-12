"""Source-bound acceptance for directional Achaean remasters with per-model Blender checks."""
import hashlib,json,struct
from pathlib import Path
from achaean_building_runtime_evidence import digest,pixel_pairs

def exported_triangles(document):
    return sum(document['accessors'][p['indices']]['count']//3 for n in document['nodes'] if 'mesh' in n for p in document['meshes'][n['mesh']]['primitives'])

def verify(root,record):
    root=Path(root).resolve();project=root.parent if root.name=='sources' else root;proof=record['reviewed_model']['runtime_evidence'];assert proof['format']=='achaean-directional-building-remaster-v1';assert proof['scope']=='blender-native-and-imported-glb' and proof['game_client_integration'] is False;assert record['culture']=='achaean' and record['category']=='buildings'
    def path(rel):
        p=(project/rel).resolve();assert p.is_relative_to(project) and p.is_file(),rel;return p
    files=proof['files']
    for rel,h in files.items():assert digest(path(rel))==h,'Changed evidence: '+rel
    study,=record['available_studies'];assert study['blend']==record['reviewed_model']['blend'];folder='sources/'+Path(study['blend']).parent.as_posix();meta=json.loads(path(folder+'/model.json').read_bytes());report=json.loads(path(folder+'/runtime-review.json').read_bytes());visual=json.loads(path(folder+'/visual-review.json').read_bytes());assert meta['id']==report['id']==record['id'];assert meta['culture']=='achaean';assert meta['binaries']==report['binaries']==visual['binaries']
    assert meta['footprint']==record['footprint']
    assert meta['definition_class']==record['legacy_identity']['definitionClass']
    assert meta['construction_updates']==record['legacy_identity']['constructionUpdates']
    for ext,h in meta['binaries'].items():assert files[folder+'/model.'+ext]==h
    assert study['sha256']==record['reviewed_model']['sha256']==meta['binaries']['blend'];assert hashlib.sha256(path(folder+'/model.json').read_bytes()).hexdigest()==report['metadata_sha256']
    author=path(meta['author']);assert author.is_relative_to(project/'sources/tools/blender') and author.suffix=='.py';assert hashlib.sha256(author.read_bytes()).hexdigest()==meta['author_sha256']
    assert meta['author'] in report['helpers'] and report['verifier'] in report['helpers']
    for rel,h in report['helpers'].items():assert rel in files and hashlib.sha256(path(rel).read_bytes()).hexdigest()==h
    assert report['maximum_bidirectional_surface_error']<1e-5 and report['texture_pixels_equal'] is True;assert report['positive_closed_meshes']['native']==report['positive_closed_meshes']['imported']==report['meshes']==meta['mesh_nodes'];assert report['game_client_integration'] is report['final_artistic_acceptance'] is visual['final_user_artistic_acceptance'] is False
    assert report['native_motion'] and report['native_motion'].keys()==report['imported_motion'].keys()
    for k,a in report['native_motion'].items():
        b=report['imported_motion'][k]
        if isinstance(a,(int,float)) and not isinstance(a,bool):assert abs(a-b)<1e-5
        else:assert a==b
    raw=path(folder+'/model.glb').read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=exported_triangles(doc);assert tri==meta['triangles']==report['triangles']<meta['triangle_budget']<=120000;verify_animation_document(meta,report,doc);assert len(doc['materials'])==report['materials']==meta['materials']<=12
    assert sum('mesh' in n for n in doc['nodes'])==report['meshes']<=180
    media=project/proof['render_directory'];assert media.resolve().is_relative_to(project/'gallery/media') and len(report['renders'])==6
    for image,h in report['renders'].items():assert hashlib.sha256(path(proof['render_directory']+'/'+image).read_bytes()).hexdigest()==h
    assert 1<=len(visual['concept_attempts'])<=3;assert visual['runtime_report_sha256']==hashlib.sha256(path(folder+'/runtime-review.json').read_bytes()).hexdigest();assert visual['pixel_pairs']==pixel_pairs(media)
    for a in visual['concept_attempts']:assert files[a['image']]==a['sha256'] and a['feedback'] and a['prompt'] in files
    manifest=json.loads(path(proof['render_directory']+'/animation-previews.json').read_bytes())
    assert manifest['renderer'] in files and manifest['renderer_sha256']==hashlib.sha256(path(manifest['renderer']).read_bytes()).hexdigest()
    for rel,h in manifest['renderer_helpers'].items():assert rel in files and hashlib.sha256(path(rel).read_bytes()).hexdigest()==h
    assert manifest['glb_sha256']==meta['binaries']['glb'] and manifest['blend_sha256']==meta['binaries']['blend']
    preview,=manifest['clips'];assert preview['name']=='Animation' and preview['frames']==24 and preview['fps']==24 and preview['distinct_pose_count']>20
    assert preview['video'] in files and files[preview['video']]==preview['sha256']
    return dict(id=record['id'],files=len(files),views=len(report['renders']),scope=proof['scope'],game_client_integration=False)


def verify_animation_document(meta,report,doc):
    assert meta['key']=='AC20' and meta['id']=='openfa:building/legacy/170'
    assert report['retained_controller_signature']==meta['animation']['retained_controller_signature']
    assert meta['animation']['direction_count']==16 and meta['animation']['frames']==[1,17] and meta['animation']['fps']==16 and meta['animation']['timing_recovered'] is False
    assert report['clips']==['Animation'];clip,=doc['animations'];assert clip['name']=='Animation'
    assert len(clip['channels'])==1 and all(doc['nodes'][c['target']['node']]['name']=='DirectionalHead' and c['target']['path']=='rotation' for c in clip['channels'])
    for s in clip['samplers']:
        a=doc['accessors'][s['input']];assert a['count']==65 and abs(a['min'][0]-1/16)<1e-6 and abs(a['max'][0]-17/16)<1e-6;assert s.get('interpolation','LINEAR')=='LINEAR'
    assert report['maximum_animation_matrix_error']<1e-5 and report['continuous_sweep_proven'] is False
    for label in ['native_motion','imported_motion']:
        m=report[label];assert m['sample_frames']==[1+i/4 for i in range(65)] and m['bearing_contact_checks']==65 and m['fork_rail_gap_bed_rays']==260
        assert m['nonbearing_surface_intersections']==0 and m['nonbearing_surface_pair_checks']>1000 and m['closed_cycle_matrix_error']<1e-5 and m['stationary_meshes_constant'] is True
        assert m['grounded_pedestal_and_foot'] and m['body_foot_relief_bearing_contacts'] and m['source_status_visibility_rays']==2 and m['coral_roughness_range']>.2
        assert m['emitter_attachment_and_visibility_checks']==260
    emitter=meta['emitter'];assert emitter['interpretation'] is True and emitter['firing_animation_recovered'] is False
    assert all(emitter[key] in meta['animation']['moving_meshes'] for key in ['housing','surround','aperture'])

