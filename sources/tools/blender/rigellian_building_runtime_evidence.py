"""Validate canonical building evidence without conflating it with client acceptance."""
import hashlib
import json
import struct
from pathlib import Path


def digest(path):
    raw = path.read_bytes()
    if path.suffix in {'.json', '.py'}:
        raw = raw.replace(b'\r\n', b'\n')
    return hashlib.sha256(raw).hexdigest()


def verify_supported_dome_contract(metadata, report, document):
    animation = metadata['animation']
    expected = {animation['cycle_clip'], animation['descriptor_clip']}
    assert set(report['clips']) == expected
    clips = {clip['name']: clip for clip in document['animations']}
    assert set(clips) == expected and len(document['meshes']) == report['meshes']
    assert len(animation['target_nodes']) == 2
    for name, clip in clips.items():
        assert len(clip['channels']) == 2
        assert {document['nodes'][c['target']['node']]['name'] for c in clip['channels']} == set(animation['target_nodes'])
        assert all(c['target']['path'] == 'rotation' for c in clip['channels'])
        interpolation = 'STEP' if name == animation['descriptor_clip'] else 'LINEAR'
        assert all(s['interpolation'] == interpolation for s in clip['samplers'])
    assert animation['cycle_frames'] == [1,61] and animation['descriptor_frames'] == [2,17]
    assert animation['fps'] == 30 and animation['continuous_timing_recovered'] is False
    motion = report['sampled_motion']
    assert motion['cycle_frames'] == list(range(1,62))
    assert motion['descriptor_domain'] == [s['descriptor'] for s in metadata['states']] == list(range(2,18))
    assert motion['leaf_old_body_surface_intersections'] is False
    assert motion['maximum_axle_leaf_distance'] < .018
    assert max(motion['maximum_cycle_matrix_error'],motion['maximum_descriptor_matrix_error']) < 1e-5
    assert motion['continuous_sweep_proven'] is False and motion['descriptor17_composition_verified'] is False
    for state in metadata['states']:
        assert state['clip'] == animation['descriptor_clip'] and state['frame'] == state['descriptor']
        assert abs(state['time_seconds']-state['frame']/30) < 1e-9
        fraction = min(1,(state['descriptor']-2)/14)
        assert abs(state['opening_fraction']-fraction) < 1e-9
        assert abs(state['angle_degrees']-110*fraction) < 1e-9
    assert metadata['states'][-1]['lower_shadow_composition_verified'] is False
    for key in ['native','imported']:
        sweep = report['supported_hardware_sweep'][key]
        assert [s['frame'] for s in sweep['samples']] == list(range(1,62))
        assert all(s['opposite_hardware_contacts'] == 0 for s in sweep['samples'])
        assert sweep['allowed_axis_seat_radius'] == .065 and sweep['allowed_axis_half_length'] == .096
        assert sweep['maximum_contact_envelope_radius'] < .065
        assert report[key]['low_floor_seated_in_original_ring'] is True
        assert report[key]['supported_hardware_contact_points'] == 24


def verify_animation_contract(metadata, report, document):
    if metadata['animation'].get('mechanism_kind') == 'ri18-supported-dome-v1':
        return verify_supported_dome_contract(metadata, report, document)
    animation = metadata['animation']
    expected = {animation['cycle_clip'], animation['descriptor_clip']}
    assert set(report['clips']) == expected
    clips = {clip['name']: clip for clip in document['animations']}
    assert set(clips) == expected and len(document['meshes']) == report['meshes']
    for name, clip in clips.items():
        assert len(clip['channels']) == 6
        assert {document['nodes'][c['target']['node']]['name'] for c in clip['channels']} == set(animation['target_nodes'])
        assert all(c['target']['path'] == 'translation' for c in clip['channels'])
        if name == animation['descriptor_clip']:
            assert all(s['interpolation'] == 'STEP' for s in clip['samplers'])
    assert [s['descriptor'] for s in metadata['states']] == report['descriptor_domain'] == list(range(2,18))
    assert all(s['clip'] == animation['descriptor_clip'] and s['frame'] == s['descriptor'] for s in metadata['states'])
    assert all(abs(s['time_seconds'] - s['frame']/animation['fps']) < 1e-9 for s in metadata['states'])
    validation = report['animation_validation']
    assert validation['cycle_integer_frames'] == 61 and validation['descriptor_poses'] == 16
    assert validation['channels_per_clip'] == 6
    assert validation['translation_only'] is True and validation['descriptor_step'] is True
    assert validation['duplicate_state_meshes'] is False
    assert validation['continuous_sweep_proven'] is False and validation['descriptor17_composition_verified'] is False
    assert report['maximum_animation_matrix_error'] < .00003
    for key in ['native', 'imported']:
        assert report[key]['sweep']['sampled_frames'] == list(range(1,62))
        assert not report[key]['sweep']['surface_intersections']


def verify_dual_lance_yaw_contract(metadata,report,document):
    import math
    articulation = metadata['articulation']
    assert metadata['id']==report['id']=='openfa:building/legacy/062'
    assert articulation['kind']=='ri23-dual-lance-yaw-v1'
    assert articulation['axis']==articulation['tip_forward_axis']=='local +Z'
    assert articulation['pivot_position']==[0,0,1]
    assert articulation['descriptor_formula']=='2+(((heading+8)>>4)&15)'
    assert articulation['descriptor_domain']==list(range(2,18))
    for field in ['legacy_static_base_descriptor_empty','complete_directional_building_frames',
                  'model_yaw_phase_sign_calibrated','firing_or_pitch_cycle_established']:
        assert articulation[field] is False
    assert not document.get('animations') and report['clips']==[]
    assert metadata['mesh_nodes']==report['meshes']==len(document['meshes'])==22
    moving = {'RI23 rotating green head','RI23 bronze lance -1','RI23 bronze lance 1'}
    assert set(articulation['moving_meshes'])==moving
    sockets = articulation['tip_sockets']
    assert len(sockets)==2
    assert {s['name'] for s in sockets}=={'LanceTipSocket -1','LanceTipSocket 1'}
    assert {s['lance_mesh'] for s in sockets}==moving-{'RI23 rotating green head'}
    nodes = document['nodes']
    indices = {node['name']:i for i,node in enumerate(nodes)}
    pivot,root = indices[articulation['pivot']],indices['PlacementRoot']
    assert pivot in nodes[root]['children']
    for socket in sockets:
        assert socket['name']=='LanceTipSocket '+socket['lance_mesh'].rsplit(' ',1)[1]
        assert indices[socket['name']] in nodes[pivot]['children']
    for node in nodes:
        if 'mesh' in node:
            assert indices[node['name']] in nodes[pivot if node['name'] in moving else root]['children']
    assert len(metadata['protected_parts'])==9 and len(metadata['optimized_parts'])==13
    assert set(metadata['protected_parts']).isdisjoint(metadata['optimized_parts'])
    assert set(report['optimized_parts'])==set(metadata['optimized_parts'])
    assert set(report['protected_parts'])==set(metadata['protected_parts'])
    assert metadata['original_triangles']>metadata['triangles']==report['triangles']
    assert report['protected_surface_error']<1e-6 and report['optimized_surface_error']<1e-4
    for key,tolerance in [('source_uv_comparison',.001),('exported_uv_comparison',1e-5)]:
        uv = report[key]
        assert uv['uv_tolerance']==tolerance and uv['maximum_uv_corner_error']<tolerance
        assert uv['matched_directed_corners']>0
        assert uv['maximum_sampled_surface_distance']<uv['position_tolerance']
    validation = report['articulation_validation']
    assert validation['kind']==articulation['kind']
    assert validation['sampled_yaw_degrees']==[i*22.5 for i in range(16)]
    assert validation['maximum_moving_matrix_error']<1e-5
    assert validation['model_yaw_phase_sign_calibrated'] is False
    def rotate(point,angle,origin):
        x,y,z = [value-centre for value,centre in zip(point,origin)]
        return [origin[0]+x*math.cos(angle)-y*math.sin(angle),
                origin[1]+x*math.sin(angle)+y*math.cos(angle),origin[2]+z]
    for key in ['native','imported']:
        form = report[key]
        foot = form['retained_refined_foot']
        assert foot['horizontal_segment_relief'] is True and foot['preserved_two_lance_rig'] is True
        assert len(foot['segment_root_contacts'])==36 and .5<foot['tapered_foot_radius_ratio']<.6
        assert len(form['sampled_contact_graph']['components'])==1 and not form['sampled_contact_graph']['isolated']
        yaw = form['yaw_validation']
        assert yaw['maximum_socket_error']<1e-5 and yaw['fixed_base_unchanged'] is True
        assert yaw['model_yaw_phase_sign_calibrated'] is False and yaw['continuous_collision_sweep_proven'] is False
        assert [p['index'] for p in yaw['poses']]==list(range(16))
        for index,pose in enumerate(yaw['poses']):
            assert pose['authored_yaw_degrees']==index*22.5
            assert pose['fixed_base_unchanged'] is True and set(pose['moving_world_matrices'])==moving
            assert set(pose['tip_sockets'])=={'-1','1'} and abs(pose['tip_separation']-.36)<1e-5
            angle = math.radians(index*22.5)
            for socket in sockets:
                tip = pose['tip_sockets'][socket['name'].rsplit(' ',1)[1]]
                expected = rotate(socket['position_zero_yaw'],angle,articulation['pivot_position'])
                forward = rotate(articulation['lance_axis_zero_yaw'],angle,[0,0,0])
                assert max(abs(a-b) for a,b in zip(tip['position'],expected))<1e-5
                assert max(abs(a-b) for a,b in zip(tip['forward'],forward))<1e-5


def verify_manual_yaw_contract(metadata,report,document):
    if metadata['articulation']['kind']=='ri23-dual-lance-yaw-v1':
        return verify_dual_lance_yaw_contract(metadata,report,document)
    articulation = metadata['articulation']
    expected_moving_counts = {'ri19-manual-yaw-v1':4,'ri22-manual-yaw-v1':11}
    assert articulation['kind'] in expected_moving_counts
    assert not document.get('animations') and report['clips'] == []
    assert articulation['descriptor_formula'] == '2+(((heading+8)>>4)&15)'
    assert articulation['descriptor_domain'] == list(range(2,18))
    assert articulation['model_yaw_phase_sign_calibrated'] is False
    assert articulation['firing_or_pitch_cycle_established'] is False
    nodes = document['nodes']
    indices = {node['name']:i for i,node in enumerate(nodes)}
    root,pivot = indices['PlacementRoot'],indices[articulation['pivot']]
    assert pivot in nodes[root]['children']
    moving = set(articulation['moving_meshes'])
    assert len(moving) == expected_moving_counts[articulation['kind']]
    assert indices[articulation['tip_socket']] in nodes[pivot]['children']
    for node in nodes:
        if 'mesh' in node:
            parent = pivot if node['name'] in moving else root
            assert indices[node['name']] in nodes[parent]['children']
    if articulation['kind'] == 'ri22-manual-yaw-v1':
        assert articulation['legacy_static_base_descriptor_empty'] is True
        assert articulation['complete_directional_building_frames'] is True
        for name in ['source_uv_comparison','exported_uv_comparison']:
            assert report[name]['maximum_uv_corner_error'] < 1e-5
            assert report[name]['matched_directed_corners'] > 0
    validation = report['articulation_validation']
    assert validation['kind'] == articulation['kind']
    assert validation['sampled_yaw_degrees'] == [i*22.5 for i in range(16)]
    assert validation['maximum_moving_matrix_error'] < 1e-5
    assert validation['model_yaw_phase_sign_calibrated'] is False
    for key in ['native','imported']:
        yaw = report[key]['yaw_validation']
        assert yaw['maximum_socket_error'] < 1e-5 and yaw['fixed_base_unchanged'] is True
        assert yaw['model_yaw_phase_sign_calibrated'] is False and yaw['continuous_collision_sweep_proven'] is False
        assert [p['index'] for p in yaw['poses']] == list(range(16))
        assert [p['authored_yaw_degrees'] for p in yaw['poses']] == [i*22.5 for i in range(16)]
        assert all(p['fixed_base_unchanged'] is True and set(p['moving_world_matrices']) == moving for p in yaw['poses'])


def verify_preserved_cpu_contract(metadata,report):
    assert metadata['id']==report['id']=='openfa:building/legacy/040'
    assert metadata['mesh_nodes']==report['meshes']==len(report['protected_parts'])==75
    assert metadata['triangles']==metadata['original_triangles']==report['triangles']==40636
    assert metadata['changes']==[] and report['protected_surface_error']<1e-6
    assert report['clips']==[] and not metadata.get('animation') and not metadata.get('articulation')
    assert report['material_count']==7 and report['embedded_images']==2
    assert len(report['renders'])==9
    for name in ['source_uv_comparison','exported_uv_comparison']:
        uv = report[name]
        assert uv['maximum_uv_corner_error']<1e-5 and uv['matched_directed_corners']>0
        assert uv['position_tolerance']==uv['uv_tolerance']==1e-5
    for key in ['native','imported']:
        form = report[key]
        for field in ['retained_cut_roof_well_and_seated_cooling_fins',
                      'retained_conformal_cap_and_open_neck_grille','clean_body_and_existing_crown_finish_preserved']:
            assert form[field] is True
        assert len(form['texture_pixels_and_uvs'])==7
        assert len(form['sampled_contact_graph']['components'])==1 and not form['sampled_contact_graph']['isolated']
        assert set(form['crown'])=={'left','right'}
        for arm in form['crown'].values():
            assert arm['volume']>0 and arm['taper_ratio']>2.6 and arm['minimum_upper_gap']>.168
    assert report['native']['texture_pixels_and_uvs']==report['imported']['texture_pixels_and_uvs']


def verify_retained_extractor_contract(metadata,report):
    assert metadata['id'] == report['id'] == 'openfa:building/legacy/059'
    assert metadata['mesh_nodes'] == report['meshes'] == len(report['protected_parts']) == 39
    assert metadata['triangles'] == metadata['original_triangles'] == report['triangles']
    assert report['protected_surface_error'] < 1e-6
    assert report['clips'] == [] and not metadata.get('animation')
    for name in ['source_uv_comparison','exported_uv_comparison']:
        comparison = report[name]
        assert comparison['maximum_uv_corner_error'] < 1e-5
        assert comparison['matched_directed_corners'] > 0 and comparison['position_tolerance'] == 1e-5
    assert report['source_uv_comparison']['matched_directed_corners'] == report['exported_uv_comparison']['matched_directed_corners']
    for key in ['native','imported']:
        form = report[key]
        assert len(form['sampled_contact_graph']['components']) == 1 and not form['sampled_contact_graph']['isolated']
        assert len(form['retained_two_casing_dents']) == 2
        assert len(form['recessed_slots']) == 2 and len(form['lower_ribs']) == 3
        assert len(form['texture_pixels_and_uvs']) == 2


def verify(root, record):
    root = Path(root).resolve()
    project = root.parent if root.name == 'sources' else root
    assert (project / 'project/layout.json').is_file(), 'Canonical project context required'
    reviewed = record['reviewed_model']
    proof = reviewed['runtime_evidence']
    assert proof['format'] == 'rigellian-building-remaster-v1'
    assert proof['scope'] == 'blender-native-and-imported-glb'
    assert proof['game_client_integration'] is False
    files = proof['files']

    def path(relative):
        result = (project / relative).resolve()
        assert result.is_relative_to(project) and result.is_file(), relative
        return result

    for relative, expected in files.items():
        assert digest(path(relative)) == expected, 'Changed evidence: ' + relative
    study, = record['available_studies']
    blend = 'sources/' + study['blend']
    folder = Path(blend).parent
    assert reviewed['blend'] == study['blend']
    assert files[blend] == study['sha256'] == reviewed['sha256']
    metadata_path = (folder / 'model.json').as_posix()
    report_path = (folder / 'runtime-review.json').as_posix()
    metadata = json.loads(path(metadata_path).read_bytes())
    report = json.loads(path(report_path).read_bytes())
    assert metadata['id'] == report['id'] == record['id']
    assert metadata['binaries'] == report['binaries']
    for kind, expected in metadata['binaries'].items():
        assert files[(folder / ('model.' + kind)).as_posix()] == expected
    assert hashlib.sha256(path(metadata_path).read_bytes()).hexdigest() == report['metadata_sha256']
    assert report['native']['positive_closed_meshes'] == report['imported']['positive_closed_meshes'] == report['meshes']
    assert report['maximum_bidirectional_surface_error'] < 1e-5
    assert report['final_artistic_acceptance'] is False and report['game_client_integration'] is False
    if metadata.get('recipe'):
        recipe_path = metadata['recipe']
        assert recipe_path in files
        assert hashlib.sha256(path(recipe_path).read_bytes()).hexdigest() == metadata['recipe_sha256']
        recipe = json.loads(path(recipe_path).read_bytes())
        if recipe.get('state_evidence'):
            state_evidence = recipe['state_evidence']
            assert state_evidence in files
            assert hashlib.sha256(path(state_evidence).read_bytes()).hexdigest() == recipe['state_evidence_sha256']
    if metadata.get('animation'):
        mechanism = metadata['mechanism_evidence']
        assert mechanism in files and hashlib.sha256(path(mechanism).read_bytes()).hexdigest() == metadata['mechanism_sha256']
        raw = path((folder / 'model.glb').as_posix()).read_bytes()
        document = json.loads(raw[20:20+struct.unpack_from('<I', raw, 12)[0]])
        verify_animation_contract(metadata, report, document)
    if metadata['id'] == 'openfa:building/legacy/040':
        verify_preserved_cpu_contract(metadata,report)
    if metadata['id'] == 'openfa:building/legacy/059':
        verify_retained_extractor_contract(metadata,report)
    if metadata.get('articulation'):
        raw = path((folder / 'model.glb').as_posix()).read_bytes()
        document = json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
        verify_manual_yaw_contract(metadata,report,document)
    for helper, expected in report['helpers'].items():
        assert helper in files
        assert hashlib.sha256(path(helper).read_bytes()).hexdigest() == expected
    for image, expected in report['renders'].items():
        relative = proof['render_directory'] + '/' + image
        assert relative in files and files[relative] == expected
    return dict(id=record['id'], files=len(files), views=len(report['renders']),
                scope=proof['scope'], game_client_integration=False)
