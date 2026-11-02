"""Register verified separate Braccatian studies while preserving previous sources."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CASES={'br22':('refine_braccatian_pithoi.py','verify_refined_braccatian_pithoi.py')}
CASES.update({key:('refine_braccatian_vessels.py','verify_refined_braccatian_vessels.py') for key in ['br04','br14','br15']})
CASES.update({key:('refine_braccatian_mast_facilities.py','verify_refined_braccatian_mast_facilities.py') for key in ['br03','br13','br16']})


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,data):
    newline='\r\n' if b'\r\n' in path.read_bytes() else '\n'
    path.write_bytes((json.dumps(data,indent=2)+'\n').replace('\n',newline).encode())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args().model
    rel=Path('docs/assets/reconstruction/braccatian-refined')/key
    source,media=ROOT/'sources'/rel,ROOT/'gallery/media'/rel
    meta=json.loads((source/'model.json').read_text())
    report=json.loads((media/'validation.json').read_text())
    generator,verifier=CASES[key]
    assert report['generator_sha256']==meta['generator_sha256']==sha(ROOT/'sources/tools/blender'/generator)
    assert report['verifier_sha256']==sha(ROOT/'sources/tools/blender'/verifier)
    assert report['source_blend_sha256']==meta['source_blend_sha256']==sha(ROOT/meta['source_study'])
    for kind in ['blend','glb']:
        assert meta[kind+'_sha256']==report[kind+'_sha256']==sha(source/('model.'+kind))
    assert report['maximum_native_imported_position_error']<.0001
    for side in ['native','imported']:
        assert report[side+'_structure']['positive_closed_meshes']==report[side+'_mesh_count']
    for view,result in report['renders'].items():
        assert result['native_sha256']==sha(media/(view+'.png'))
        assert result['imported_sha256']==sha(media/('imported-'+view+'.png'))
    for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    inventory_path=ROOT/'sources/docs/reconstruction/models/inventory.json'
    inventory=json.loads(inventory_path.read_text())
    row=next(r for r in inventory['records'] if r['id']==meta['id'])
    study=dict(stage=meta['stage'],blend=(rel/'model.blend').as_posix(),present=True,
               sha256=meta['blend_sha256'],final_visual_acceptance='not-established')
    previous=[s for s in row['available_studies'] if s['blend']==study['blend']]
    assert not previous or previous==[study],'Preserve accepted prior iterations; use a new path'
    if not previous:row['available_studies'].append(study)
    layout_path=ROOT/'project/layout.json'
    layout=json.loads(layout_path.read_text())
    destinations={r['destination'] for r in layout['files']}
    paths=list(source.iterdir())+list(media.iterdir())+list((ROOT/'sources/materials/reconstruction/braccatian-refined'/key).glob('*.png'))
    paths += [ROOT/'sources/tools/blender'/n for n in [generator,verifier]]
    paths += [ROOT/'sources/docs/reconstruction/models/braccatian-structural-refinement.md']
    for path in sorted(paths):
        assert path.is_file() and path.suffix!='.blend1','Keep working backups outside canonical sources'
        destination=path.relative_to(ROOT).as_posix()
        if destination in destinations:continue
        media_file=destination.startswith('gallery/media/')
        original=destination.removeprefix('gallery/media/' if media_file else 'sources/')
        assert not any(r['original']==original for r in layout['files'])
        role='media' if media_file else 'material-texture' if original.startswith('materials/') else 'source'
        layout['files'].append(dict(original=original,destination=destination,role=role,ownership='authored'))
    save(inventory_path,inventory)
    save(layout_path,layout)
    print('BRACCATIAN_REFINEMENT_REGISTERED',key)


if __name__=='__main__':main()
