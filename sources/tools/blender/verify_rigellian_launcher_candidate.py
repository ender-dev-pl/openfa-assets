"""Actual RI18 candidate sweep and descriptor diagnostics; delivery stays unaccepted."""
import hashlib
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
from remaster_rigellian_launcher import ROOT,FOLDER,CYCLE,STATES,TARGETS,select_clip
from audit_rigellian_launcher_source import inspect,tree


def support_checks():
    maximum = 0
    for frame in range(1,62):
        select_clip(CYCLE,frame)
        for sign in [-1,1]:
            leaf = bpy.data.objects['Split pointed cap '+str(sign)]
            point = Vector((sign*.26,0,1.63))
            distance = tree(leaf).find_nearest(point)[3]
            assert distance < .018,(frame,sign,'Leaf detached from axle',distance)
            maximum = max(maximum,distance)
    return maximum


def descriptors():
    offsets = []
    for name in TARGETS:
        strip = bpy.data.objects[name].animation_data.nla_tracks[STATES].strips[0]
        offsets.append(strip.action_frame_start-strip.frame_start)
    assert max(offsets)-min(offsets)<1e-5
    offset = offsets[0]
    assert abs(offset-round(offset))<1e-5
    values = {}
    for descriptor in range(2,18):
        select_clip(STATES,descriptor-int(round(offset)))
        values[descriptor] = {name:[float(v) for row in bpy.data.objects[name].matrix_world for v in row]
                              for name in TARGETS}
    return offset,values


def main():
    meta = json.loads((FOLDER/'model.json').read_bytes())
    for kind,expected in meta['binaries'].items():
        assert hashlib.sha256((FOLDER/('model.'+kind)).read_bytes()).hexdigest()==expected
    bpy.ops.wm.open_mainfile(filepath=str(FOLDER/'model.blend'),load_ui=False,use_scripts=False)
    select_clip(CYCLE,1)
    native,native_matrices = inspect()
    native_support = support_checks()
    native_offset,native_states = descriptors()
    for obj in list(bpy.context.scene.objects):
        if obj.type in ['MESH','EMPTY']:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(FOLDER/'model.glb'))
    select_clip(CYCLE,1)
    imported,imported_matrices = inspect()
    imported_support = support_checks()
    imported_offset,imported_states = descriptors()
    for label,report in [('native',native),('imported',imported)]:
        assert report['meshes']==38
        assert all(x['closed'] and x['signed_volume']>0 for x in report['topology'].values()),label
        assert not any(s['leaf_fixed_surface_intersections'] for s in report['samples']),label
        assert max(report['samples'][30]['open_bore_heights'])<.051,label
    assert native_matrices.keys()==imported_matrices.keys()
    assert all(native_matrices[f].keys()==imported_matrices[f].keys() for f in native_matrices)
    error = max(abs(a-b) for f in native_matrices for name in native_matrices[f]
                for a,b in zip(native_matrices[f][name],imported_matrices[f][name]))
    state_error = max(abs(a-b) for d in native_states for name in TARGETS
                      for a,b in zip(native_states[d][name],imported_states[d][name]))
    assert max(error,state_error)<1e-5,(error,state_error)
    report = dict(id=meta['id'],issue=253,binaries=meta['binaries'],blender=bpy.app.version_string,
        metadata_sha256=hashlib.sha256((FOLDER/'model.json').read_bytes()).hexdigest(),
        verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        helpers={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in [
            'sources/tools/blender/remaster_rigellian_launcher.py',
            'sources/tools/blender/audit_rigellian_launcher_source.py']},
        native=native,imported=imported,
        native_maximum_axle_to_leaf_distance=native_support,
        imported_maximum_axle_to_leaf_distance=imported_support,
        maximum_cycle_matrix_error=error,maximum_descriptor_matrix_error=state_error,
        native_descriptor_nla_offset=native_offset,imported_descriptor_nla_offset=imported_offset,
        descriptor_domain=list(range(2,18)),
        scope='Candidate diagnostics only. Hinge hardware seating, source geometry/maps, complete missile volume, continuous sweep, render comparisons and descriptor17 composition still require review.',
        canonical_delivery_ready=False)
    (FOLDER/'candidate-motion-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('RI18_SUPPORTED_CANDIDATE_SWEEP_OK',error,state_error,flush=True)


if __name__=='__main__':
    main()
