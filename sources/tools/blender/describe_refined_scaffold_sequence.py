"""Describe the user-requested erection/reveal/removal asset sequence."""
import hashlib
import json
from pathlib import Path
import re
import struct

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'docs/assets/reconstruction/scaffolds/rigellian/size-2-refined'


def interior_node(name):
    if ' internal tie ' in name:
        return True
    match = re.search(r'(?:upright|joint sleeve|clamp(?: pin)?|Ground foot) (\d+)', name)
    return bool(match and int(match.group(1)) >= 24)


def build_contract():
    manifest = json.loads((ROOT / 'model.json').read_text())
    limits = json.loads((REPO / 'docs/reconstruction/models/scaffold-stage-limits.json').read_text())
    stages = []
    for case in manifest['cases']:
        path = ROOT / f"stage-{case['total_stage']:02}/model.glb"
        raw = path.read_bytes()
        length = struct.unpack_from('<I', raw, 12)[0]
        gltf = json.loads(raw[20:20 + length])
        names = [node['name'] for node in gltf['nodes'] if 'mesh' in node]
        interior = [name for name in names if interior_node(name)]
        assert interior and len(interior) < len(names)
        stages.append(dict(stage=case['total_stage'],frames=case['frames'],
                           glb=path.relative_to(ROOT).as_posix(),glb_sha256=hashlib.sha256(raw).hexdigest(),
                           hide_during_reveal_and_removal=interior))
    definitions = []
    for record in limits['records']:
        if record['family'] != 'RIS2':
            continue
        ceiling = record['max_stage_while_constructing']
        definitions.append(dict(id=record['id'],name=record['name'],ceiling=ceiling,
                                erection_stages=list(range(1,ceiling+1)),
                                dismantling_stages=list(range(ceiling,0,-1))))
    return dict(schema_version=1,issue=186,family='RIS2',
                provenance='User-requested presentation sequence; not a recovered legacy timing rule',
                phases=[dict(id='erection',target_building_visible=False,interior_scaffold_visible=True),
                        dict(id='reveal',target_building_visible=True,interior_scaffold_visible=False),
                        dict(id='dismantling',target_building_visible=True,interior_scaffold_visible=False),
                        dict(id='complete',target_building_visible=True,scaffold_visible=False)],
                reveal_rule='At target scaffold height insert the finished building; remove scaffolding in reverse stage order, exposing the building from the top',
                interior_rule='Remove temporary interior shoring at reveal so it cannot intersect the inserted building; retain perimeter scaffolding during removal',
                timing='Owned by simulation/presenter; asset metadata supplies ordering, not durations',
                calibration='Presenter must fit the scaffold envelope and target height around the real building; physical pitch remains provisional',
                model_manifest_sha256=hashlib.sha256((ROOT/'model.json').read_bytes()).hexdigest(),
                generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                stages=stages,definitions=definitions)


if __name__ == '__main__':
    contract=build_contract()
    (ROOT/'construction-sequence.json').write_text(json.dumps(contract,indent=2)+'\n')
    print('RIS2_CONSTRUCTION_SEQUENCE_OK',len(contract['definitions']))
