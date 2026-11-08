"""Register the verified in-place PB14 correction and current gallery views."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = 'sources/docs/assets/bootstrap-3d/terran-refined/pb14'
MEDIA = 'gallery/media/docs/assets/bootstrap-3d/terran-refined/pb14'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    old = path.read_bytes() if path.exists() else b''
    text = json.dumps(data, indent=2) + '\n'
    path.write_bytes(text.replace('\n', '\r\n' if b'\r\n' in old else '\n').encode())


def main():
    folder = ROOT / BASE
    media = ROOT / MEDIA
    report = json.loads((folder / 'correction-runtime-verification.json').read_text())
    for kind, digest in report['binaries'].items():
        assert sha(folder / ('model.' + kind)) == digest
    frames = [Image.open(media / 'iris' / f'{i:02}.png').convert('RGB') for i in range(17)]
    loop = frames + frames[-2:0:-1]
    loop[0].save(media / 'iris.gif', save_all=True, append_images=loop[1:], duration=62, loop=0)
    metadata = json.loads((folder / 'model.json').read_text())
    if 'historical_metadata' not in metadata:
        metadata = dict(historical_metadata=metadata)
    metadata.update(building_id='terran:missile-silo', name='Missile Silo', culture='terran', footprint=[2, 2], binaries=report['binaries'], ground_level=0, preserve_ground_origin=True, animation=dict(name='Animation', duration_seconds=2, closed_seconds=0, fully_open_seconds=1, closed_again_seconds=2), status_lamps=dict(channels=['StatusLampLeft', 'StatusLampRight'], presets=dict(Hybrid=[255, 210, 138], AttackOnly=[194, 93, 93], DefenceOnly=[150, 170, 210]), control='Exactly one preset mesh at unit scale per lit channel; all presets zero scale when off; no lamp animation'), integration='Preserve grade Z=0 native / Y=0 glTF. Flat iris blades rotate about fixed rim pivots; hold payload below closed iris until open, then lift. Explicit client state/node binding required.', verification='correction-runtime-verification.json')
    metadata['iris_mechanism'] = dict(blades=16, fixed_pivots=True, motion='Rotation in the lid plane; no vertical carrier or out-of-plane folding', blade_count_status='Authored to fit the fully clear aperture into the surrounding rim; not recovered legacy engineering', proof='diaphragm-verification.json')
    write(folder / 'model.json', metadata)
    path = ROOT / 'sources/docs/reconstruction/models/inventory.json'
    inventory = json.loads(path.read_text())
    row = next(r for r in inventory['records'] if r['id'] == 'terran:missile-silo')
    for reference in row['references']:
        if reference['entry'] == 'PB14.VID':
            reference.update(kind='operational-video', palette_status='embedded palette reviewed; opening and closing, fixed camera')
    old = [r for r in row['available_studies'] if r['stage'] == 'silhouette-study']
    for study in old:
        study['status'] = 'historical_not_for_packaging; payload preserved as earlier study'
    if old:
        row.setdefault('superseded_studies', []).extend(old)
    current = next(r for r in row['available_studies'] if r['stage'] == 'refined-study')
    current['sha256'] = report['binaries']['blend']
    current['views'] = [dict(label=label, image=MEDIA+'/'+name+'.png') for name, label in [('closed', 'Closed iris'), ('decoy-clearance', 'Decoy clearance fixture'), ('lamps-AttackOnly', 'Attack: red'), ('lamps-DefenceOnly', 'Defence: blue'), ('lamps-Hybrid', 'Hybrid: base colour'), ('lamps-off', 'Both lamps off'), ('lamps-left', 'Left lamp only'), ('lamps-right', 'Right lamp only')]]
    row['available_studies'] = [current]
    row['selected_refinement'] = dict(stage='refined-study', blend=BASE.removeprefix('sources/')+'/model.blend', glb=BASE.removeprefix('sources/')+'/model.glb', issue=242, integration='Use one canonical payload across surface, build menu and SciTek. Explicit terrain, stored-payload and lamp controls require game runtime integration.')
    row['acceptance'].update(reference_views_reviewed=True, moving_assemblies=True, native_and_glb_runtime=True)
    row['open_evidence_questions'] = ['No on/off timing recovered in reviewed surface phases or 120 PB14.VID frames; drive independent lamps from actual game state.', 'Final client placement, launch timing and status binding need runtime verification.']
    write(path, inventory)
    layout_path = ROOT / 'project/layout.json'
    layout = json.loads(layout_path.read_text())
    known = {r['destination'] for r in layout['files']}
    files = list(folder.glob('*')) + list(media.rglob('*')) + [ROOT/'sources/tools/blender/correct_missile_silo.py', ROOT/'sources/tools/blender/verify_missile_silo_correction.py', ROOT/'sources/tools/blender/verify_silo_diaphragm.py']
    for path in sorted(files):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel not in known:
            layout['files'].append(dict(original=rel, destination=rel, role='media' if rel.startswith('gallery/') else 'source', ownership='authored'))
    write(layout_path, layout)
    print('SILO_REGISTERED')


if __name__ == '__main__':
    main()
