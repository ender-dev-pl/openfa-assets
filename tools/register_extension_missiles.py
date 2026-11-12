"""Register verified extension-only models without inventing legacy definitions."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
BASE='sources/objects/extensions/munitions'
MEDIA='gallery/media/objects/extensions/munitions'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p,r):
    old=p.read_bytes() if p.exists() else b'';s=json.dumps(r,indent=2)+'\n'
    p.write_bytes(s.replace('\n','\r\n' if b'\r\n' in old else '\n').encode())


def main():
    records=[]
    for name in ['interceptor','decoy']:
        folder=ROOT/BASE/name;r=json.loads((folder/'runtime-verification.json').read_text())
        for filename,digest in r['binaries'].items():assert sha(folder/filename)==digest
        refs=['sources/artwork/interceptor/source.jpg','sources/artwork/interceptor/menu-source.gif'] if name=='interceptor' else ['sources/artwork/decoy/bundle-source.png','sources/artwork/decoy/segment-source.png','sources/artwork/decoy/menu-source.gif']
        write(folder/'reference-evidence.json',dict(source_kind='user-authored OpenFA extension artwork; not recovered legacy body',references={p:sha(ROOT/p) for p in refs},review='Full-resolution images and sampled turntable phases reviewed; existing GIF is rotation only. Decoy separation is user-requested enhancement.',hidden_details='Authored sections, coupling contact pads, underside/nozzle construction and wear',palette='Existing source RGB/RGBA, no legacy indexed palette'))
        package='openfa.interceptor-missle' if name=='interceptor' else 'openfa.advanced-munitions'
        write(folder/'model.json',dict(id=r['id'],package=package,blend=BASE+'/'+name+'/model.blend',glb=BASE+'/'+name+'/model.glb',binaries=r['binaries'],triangles=r['triangles'],mesh_instances=r['mesh_instances'],unique_meshes=1,materials=1,packed_maps=2,native_forward='-Y',native_up='+Z',glb_forward='-Z',glb_up='+Y',native_bounds=r['native_bounds'],world_size_proposal=48,scale_status='unapplied generic fitting assumption, not physical metres',calibrated_sockets=0,legacy_missile_rig_note='Existing Terran Stasis nose+Z; mapping new native-Y to older+Z requires X-90deg, client coordinate equivalent must be verified',segment_visual_binding_proposal='openfa:missile/decoy-segment' if name=='decoy' else None,animation=r.get('animation_preview'),acceptance='Blender source/import checked; final user/client acceptance separate'))
        views=[dict(label='Verified imported '+name,image=MEDIA+'/'+name+'/verified-imported.png',blend=BASE+'/'+name+'/model.blend',glb=BASE+'/'+name+'/model.glb')]
        if name=='decoy':
            views[0]['video']=MEDIA+'/decoy/separation.webm'
            views.append(dict(label='Four separated segments',image=MEDIA+'/decoy/separated.png'))
        records.append(dict(id=r['id'],name='Interceptor' if name=='interceptor' else 'Decoy bundle / separation',category='missiles',culture='shared',views=views,detail=BASE+'/README.md'))
    records.append(dict(id='openfa:visual/decoy-segment',name='Decoy individual segment',category='missiles',culture='shared',views=[dict(label='Same shared segment geometry',image=MEDIA+'/decoy/segment.png',blend=BASE+'/decoy/model.blend',glb=BASE+'/decoy/segment.glb')],detail=BASE+'/README.md'))
    write(ROOT/BASE/'catalogue.json',records)
    page=['# Extension missiles','','[Interactive catalogue](index.html#race=shared&type=missiles) · [All models](README.md)','','Authored OpenFA extension products, not recovered legacy missiles. [Source and integration contract](../'+BASE+'/README.md).','']
    for row in records:
        v=row['views'][0];page+=['## '+row['name'],'','!['+row['name']+'](../'+v['image']+')','','[Blend](../'+v['blend']+') · [GLB](../'+v['glb']+')','']
        if v.get('video'):page+=['[Play full continuous separation animation](../'+v['video']+')','']
    (ROOT/'gallery/extension-missiles.md').write_text('\n'.join(page)+'\n')
    p=ROOT/'project/layout.json';layout=json.loads(p.read_text());known={r['destination'] for r in layout['files']}
    files=list((ROOT/BASE).rglob('*'))+list((ROOT/MEDIA).rglob('*'))+list((ROOT/'sources/materials/extensions/munitions').glob('*.png'))
    files += [ROOT/'sources/tools/blender/author_extension_missiles.py',ROOT/'sources/tools/blender/verify_extension_missiles.py']
    for pth in sorted(files):
        if not pth.is_file():continue
        rel=pth.relative_to(ROOT).as_posix()
        if rel not in known:layout['files'].append(dict(original=rel,destination=rel,role='media' if rel.startswith('gallery/') else ('material-texture' if '/materials/' in rel else 'source'),ownership='authored'))
    write(p,layout);print('EXTENSION_MODELS_REGISTERED',len(records))


if __name__=='__main__':main()
