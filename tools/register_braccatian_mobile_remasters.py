"""Publish one current canonical study per mobile ship; retain prior evidence."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
KEYS=['rattlesnake','widowmaker','heartsblood','morning-glory']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def write(path,data):
    crlf=path.exists() and b'\r\n' in path.read_bytes();text=json.dumps(data,indent=2)+'\n';path.write_bytes(text.replace('\n','\r\n' if crlf else '\n').encode())


def main():
    inventory=ROOT/'sources/docs/reconstruction/models/inventory.json';data=json.loads(inventory.read_text());published=[]
    for key in KEYS:
        rel=Path('objects/braccatian')/key;folder=ROOT/'sources'/rel;meta=json.loads((folder/'model.json').read_text());report=json.loads((folder/'runtime-verification.json').read_text())
        assert report['binaries']=={k:sha(folder/('model.'+k)) for k in ['blend','glb']}
        assert report['generator_sha256']==sha(ROOT/'sources/tools/blender/remaster_braccatian_mobile_ships.py')
        assert report['verifier_sha256']==sha(ROOT/'sources/tools/blender/verify_braccatian_mobile_remasters.py')
        assert report['relative_surface_deviation']<.012 and report['source_import_position_error']<1e-5
        for filename,digest in report['renders'].items():assert sha(ROOT/'gallery/media'/rel/filename)==digest
        row=next(r for r in data['records'] if r['id']==meta['id']);old=[s for s in row['available_studies'] if s['blend']!=(rel/'model.blend').as_posix()]
        for s in old:s['status']='historical_not_for_packaging'
        if old:row.setdefault('superseded_studies',[]).extend(old)
        row['available_studies']=[dict(stage='mobile-ship-remaster',blend=(rel/'model.blend').as_posix(),present=True,sha256=report['binaries']['blend'],views=[dict(label=label,image=(Path('gallery/media')/rel/name).as_posix()) for label,name in [('Rear machinery','rear-quarter.png'),('Actual imported wireframe','technical-wireframe.png'),('Legacy heading4 view','heading-04.png')]],final_visual_acceptance='User review pending; source/import runtime verified')]
        row['selected_refinement']=dict(stage='mobile-ship-remaster',blend=(rel/'model.blend').as_posix(),glb=(rel/'model.glb').as_posix(),issue=244,integration='One canonical model for gameplay, ship/build menus and SciTek; retain original catalogue id. World-size proposal and sockets require client calibration.')
        row['acceptance'].update(reference_views_reviewed=True,silhouette_and_proportions=True,high_detail_structure=True,materials=True,native_and_glb_runtime=True)
        published.append(dict(id=meta['id'],blend=('sources/'+(rel/'model.blend').as_posix()),glb=('sources/'+(rel/'model.glb').as_posix()),blend_sha256=report['binaries']['blend'],glb_sha256=report['binaries']['glb'],size_class=meta['size_class'],world_size_proposal=meta['world_size_proposal'],triangles=meta['triangles'],mesh_batches=4))
    write(inventory,data)
    write(ROOT/'sources/docs/reconstruction/models/braccatian-mobile-remaster.json',dict(issue=244,models=published,scope='Asset runtime verified, game integration separate; size values are proposals, not recovered dimensions.'))
    layout_path=ROOT/'project/layout.json';layout=json.loads(layout_path.read_text());known={r['destination'] for r in layout['files']}
    files=[]
    for key in KEYS:files+=list((ROOT/'sources/objects/braccatian'/key).glob('*'))+list((ROOT/'gallery/media/objects/braccatian'/key).glob('*'))
    files+=list((ROOT/'sources/materials/braccatian/mobile-ships').glob('*'))
    files+=[ROOT/'sources/tools/blender'/n for n in ['remaster_braccatian_mobile_ships.py','verify_braccatian_mobile_remasters.py']]
    files+=[ROOT/'sources/docs/reconstruction/models'/n for n in ['braccatian-mobile-remaster.json','braccatian-mobile-remaster.md','braccatian-mobile-delivery.json']]
    files+=[ROOT/'gallery/media/objects/braccatian/mobile-ships.jpg']
    for entry in layout['files']:
        if entry['destination'].startswith('sources/materials/braccatian/mobile-ships/') and entry['destination'].endswith('.png'):entry['role']='material-texture'
    for p in sorted(files):
        if not p.is_file():continue
        dest=p.relative_to(ROOT).as_posix()
        if dest in known:continue
        original=dest.removeprefix('gallery/media/' if dest.startswith('gallery/media/') else 'sources/')
        role='media' if dest.startswith('gallery/') else 'material-texture' if dest.startswith('sources/materials/') and dest.endswith('.png') else 'source'
        layout['files'].append(dict(original=original,destination=dest,role=role,ownership='authored'));known.add(dest)
    write(layout_path,layout);print('BRACCATIAN_MOBILE_REGISTERED',len(published))


if __name__=='__main__':main()
