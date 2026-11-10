"""Validate exact-file evidence for the Blender native/imported-GLB gate.

This technical gate does not accept visual fidelity, animation completeness,
attachment calibration or game-client integration.
"""
import hashlib
import json
from pathlib import Path


def evidence_digest(path):
    path=Path(path);data=path.read_bytes()
    if path.suffix in ['.json','.py']: data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()


def verify_runtime_evidence(root,record):
    root=Path(root).resolve();model=record['reviewed_model'];proof=model.get('runtime_evidence')
    assert isinstance(proof,dict),'Native/GLB gate requires bound runtime evidence'
    if proof.get('format') == 'culture-building-remaster-v1':
        from culture_building_remaster_runtime_evidence import verify
        return verify(root, record)
    if proof.get('format') == 'achaean-power-tower-remaster-v1':
        from achaean_power_tower_runtime_evidence import verify
        return verify(root, record)
    if proof.get('format') == 'achaean-stun-tower-remaster-v1':
        from achaean_stun_tower_runtime_evidence import verify
        return verify(root, record)
    if proof.get('format') == 'achaean-directional-building-remaster-v1':
        from achaean_directional_building_runtime_evidence import verify
        return verify(root, record)
    if proof.get('format') == 'achaean-animated-building-remaster-v1':
        from achaean_animated_building_runtime_evidence import verify
        return verify(root, record)
    if proof.get('format') == 'achaean-static-building-remaster-v2':
        from achaean_static_building_runtime_evidence import verify
        return verify(root, record)
    if proof.get('format') == 'achaean-building-remaster-v1':
        from achaean_building_runtime_evidence import verify
        return verify(root, record)
    if proof.get('format') == 'rigellian-building-remaster-v1':
        from rigellian_building_runtime_evidence import verify
        return verify(root, record)
    if proof.get('format') == 'mobile-remaster-runtime-v1':
        from mobile_remaster_evidence import verify_record
        return verify_record(root, record)
    assert proof.get('scope')=='blender-native-and-imported-glb'
    assert proof.get('text_hash_policy')=='lf-for-json-and-python'
    assert proof.get('game_client_integration') is False,'Do not infer game integration from Blender checks'
    files=proof.get('files');assert isinstance(files,dict) and files

    def path(relative):
        target=(root/relative).resolve()
        assert target.is_relative_to(root),'Runtime evidence must remain in repository'
        return target

    for relative,digest in files.items():
        target=path(relative)
        assert target.is_file(),'Missing runtime evidence: '+relative
        assert evidence_digest(target)==digest,'Runtime evidence changed: '+relative
    blend=Path(model['blend']);folder=blend.parent
    required=[str(folder/name).replace('\\','/') for name in ['model.blend','model.glb','model.json','technical-review.json','render-review.json']]
    required += [proof.get('verifier'),proof.get('render_reviewer'),proof.get('imported_render')]
    assert all(isinstance(name,str) and name in files for name in required),'Incomplete bound runtime evidence'
    for key in ['verifier','render_reviewer']:
        assert path(proof[key]).is_relative_to(root/'tools/blender') and path(proof[key]).suffix=='.py'
    assert Path(proof['imported_render']).parent==folder,'Imported render must belong to reviewed model'
    metadata=json.loads(path(str(folder/'model.json')).read_text())
    technical=json.loads(path(str(folder/'technical-review.json')).read_text())
    renders=json.loads(path(str(folder/'render-review.json')).read_text())
    assert metadata['id']==record['id'],'Runtime evidence catalogue identity differs'
    assert metadata['blend_sha256']==model['sha256']==files[str(blend).replace('\\','/')]
    glb=str(folder/'model.glb').replace('\\','/')
    assert metadata['glb_sha256']==files[glb]
    assert technical['blend_sha256']==metadata['blend_sha256'] and technical['glb_sha256']==metadata['glb_sha256']
    assert technical['revision']==renders['revision']==metadata['revision'],'Runtime evidence revisions differ'
    assert renders['blend_sha256']==metadata['blend_sha256']
    assert technical.get('checks') and technical['mesh_objects']==metadata['mesh_objects']
    assert renders.get('alpha') is True
    views=renders.get('view_hashes',{});required_views=set(metadata['views'])|{Path(proof['imported_render']).stem}
    assert required_views<=views.keys(),'Native/imported views missing from render evidence'
    for name,digest in views.items():
        relative=str(folder/(name+'.png')).replace('\\','/')
        assert relative in files and files[relative]==digest,'Unbound render pixels: '+relative
        assert renders.get('margins',{}).get(name,0)>=24,'Runtime render lacks verified framing margin'
    return dict(id=record['id'],revision=metadata['revision'],files=len(files),views=len(views),
        scope=proof['scope'],game_client_integration=False)
