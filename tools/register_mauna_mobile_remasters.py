"""Register verified canonical ships incrementally; keep missing faction work visible."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def write(path,data):
    crlf=path.exists() and b'\r\n' in path.read_bytes();text=json.dumps(data,indent=2)+'\n';path.write_bytes(text.replace('\n','\r\n' if crlf else '\n').encode())


def main():
    index=json.loads((ROOT/'sources/docs/reconstruction/models/ship-reference-index.json').read_text());expected=[r['id'] for r in index['ships'] if r['culture']=='mauna' and not r['runtime_fixed_scale']]
    inventory_path=ROOT/'sources/docs/reconstruction/models/inventory.json';inventory=json.loads(inventory_path.read_text());published=[];files=[]
    for folder in sorted((ROOT/'sources/objects/mauna').iterdir()):
        if not (folder/'model.json').exists():continue
        key=folder.name;rel=Path('objects/mauna')/key;meta=json.loads((folder/'model.json').read_text());report=json.loads((folder/'runtime-verification.json').read_text());review=json.loads((folder/'concept-review.json').read_text())
        assert meta['id'] in expected and report['binaries']=={kind:sha(folder/('model.'+kind)) for kind in ['blend','glb']}
        assert review['reviewed_binary_hashes']==report['binaries']
        assert report['generator_sha256']==sha(ROOT/'sources/tools/blender/remaster_mauna_mobile_ship.py')
        assert report['verifier_sha256']==sha(ROOT/'sources/tools/blender/verify_mauna_mobile_ship.py')
        assert meta['shared_recipe_helpers_sha256']==sha(ROOT/'sources/tools/blender/remaster_artemian_mobile_ship.py')
        assert report['shared_geometry_verifier_sha256']==sha(ROOT/'sources/tools/blender/verify_artemian_mobile_ship.py')
        assert report['recipe_sha256']==sha(folder/'recipe.json') and report['relative_surface_deviation']<.012 and report['source_import_position_error']<1e-5
        media=ROOT/'gallery/media'/rel
        for name,digest in report['renders'].items():assert sha(media/name)==digest
        row=next(r for r in inventory['records'] if r['id']==meta['id']);old=[s for s in row['available_studies'] if s['blend']!=(rel/'model.blend').as_posix()]
        for s in old:s['status']='historical_not_for_packaging'
        if old:row.setdefault('superseded_studies',[]).extend(old)
        views=[dict(label=label,image=(Path('gallery/media')/rel/name).as_posix()) for label,name in [('Rear fittings','rear-quarter.png'),('Actual imported wireframe','technical-wireframe.png'),('Legacy heading4 comparison','heading-04.png')]]
        views += [dict(label=it['gallery_label'],image=it['image']) for it in review['iterations']]
        row['available_studies']=[dict(stage='mobile-ship-remaster',blend=(rel/'model.blend').as_posix(),present=True,sha256=report['binaries']['blend'],views=views,final_visual_acceptance='Agent legacy/concept/imported-render review complete; final user acceptance and client calibration separate')]
        row['selected_refinement']=dict(stage='mobile-ship-remaster',blend=(rel/'model.blend').as_posix(),glb=(rel/'model.glb').as_posix(),issue=251,integration='One canonical source/export across gameplay, ship/build menus and SciTek. Keep the original catalogue id; WorldSize and equipment mounts require client calibration.')
        row['remaster_protocol']=dict(issue=251,concept_review='reviewed',review=(rel/'concept-review.json').as_posix(),iterations=len(review['iterations']),final_user_acceptance='pending')
        row['acceptance'].update(reference_views_reviewed=True,silhouette_and_proportions=True,high_detail_structure=True,materials=True,native_and_glb_runtime=True)
        published.append(dict(id=meta['id'],blend='sources/'+(rel/'model.blend').as_posix(),glb='sources/'+(rel/'model.glb').as_posix(),blend_sha256=report['binaries']['blend'],glb_sha256=report['binaries']['glb'],triangles=meta['triangles'],mesh_batches=meta['mesh_batches'],material_count=meta['material_count'],size_class=meta['size_class'],world_size_proposal=meta['world_size_proposal']))
        files+=list(folder.glob('*'))+list(media.glob('*.png'))
    write(inventory_path,inventory)
    write(ROOT/'sources/docs/reconstruction/models/mauna-mobile-remaster.json',dict(issue=251,expected_mobile_ship_count=len(expected),models=published,pending=[i for i in expected if i not in {r['id'] for r in published}],scope='Incremental verified asset milestones; no complete faction, client calibration or final user artistic acceptance inferred from a partial list.'))
    files+=list((ROOT/'sources/materials/mauna/mobile-ships').glob('*'))+list((ROOT/'gallery/media/concepts/mauna').glob('*.png'))
    files += [ROOT/'sources/tools/blender'/name for name in ['remaster_mauna_mobile_ship.py','verify_mauna_mobile_ship.py']]
    files += [ROOT/'sources/docs/reconstruction/models'/name for name in ['mauna-mobile-remaster.json','mauna-mobile-remaster.md','mauna-mobile-delivery.json']]
    path=ROOT/'project/layout.json';layout=json.loads(path.read_text());known={r['destination'] for r in layout['files']}
    for p in sorted(files):
        if not p.is_file():continue
        destination=p.relative_to(ROOT).as_posix()
        if destination in known:continue
        original=destination.removeprefix('gallery/media/' if destination.startswith('gallery/media/') else 'sources/')
        role='media' if destination.startswith('gallery/') else 'material-texture' if destination.startswith('sources/materials/') and destination.endswith('.png') else 'source'
        layout['files'].append(dict(original=original,destination=destination,role=role,ownership='authored'));known.add(destination)
    write(path,layout);print('MAUNA_REGISTERED',len(published),'of',len(expected))


if __name__=='__main__':main()
