"""Verify the complete 14-model proposal delivery, separate from game catalogues."""
import argparse,hashlib,json,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tools'))
from verify_project import LocalLinks
from verify_publication import problems

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--base');p.add_argument('--cultures',nargs='+');a=p.parse_args();base=ROOT/'sources/proposals/engineering-ships';concepts=read(base/'concepts.json')['models'];expected={(c,r) for c in ['terran','rigellian','braccatian','mikotaj','artemian','mauna','achaean'] for r in ['terraform','repair']}
    assert {(x['culture'],x['role']) for x in concepts}==expected and len(concepts)==14
    gallery=read(ROOT/'gallery/engineering-proposals.json');assert {(x['culture'],x['role']) for x in gallery['models']}==expected and len(gallery['models'])==14
    LocalLinks().feed((ROOT/'gallery/engineering-proposals.html').read_text(encoding='utf-8'))
    models=[]
    assert not a.cultures or set(a.cultures)<={c for c,_ in expected}
    selected={pair for pair in expected if not a.cultures or pair[0] in a.cultures}
    for culture,role in sorted(selected):
        folder=base/culture/role;meta=read(folder/'model.json');runtime=read(folder/'runtime-review.json');visual=read(folder/'visual-review.json');videos=read(folder/'video-review.json')
        assert not any(meta[k] for k in ['legacy_unit','runtime_integration','mechanics_available','blueprint_registered','package_registered'])
        assert meta['status']=='proposed-assets-awaiting-mechanics' and meta['triangles']<40000 and meta['triangle_budget']==40000 and meta['revision']==2
        assert meta['concept'] in concepts and sha(ROOT/meta['concept']['image'])==meta['concept']['sha256']
        assert sha(ROOT/meta['refinement_helper'])==meta['refinement_helper_sha256']
        assert sha(ROOT/meta['author'])==meta['author_sha256'] and sha(ROOT/meta['helper'])==meta['helper_sha256']
        for ext,digest in meta['binaries'].items():assert sha(folder/('model.'+ext))==digest
        for name,digest in meta['maps'].items():assert sha(ROOT/name)==digest
        assert runtime['metadata_sha256']==sha(folder/'model.json') and runtime['binaries']==meta['binaries']
        assert runtime['verifier_sha256']==sha(Path(__file__).with_name('verify_engineering_refinement.py'))
        assert runtime['revision']==2 and runtime['pbr_texture_pixels_equal']
        assert runtime['motion_frames']==[1,13,25,49,73,97] and runtime['moving_parts'] and runtime['connected_support_graph'] and runtime['texture_pixels_equal']
        assert runtime['maximum_animation_surface_error']<1e-5 and runtime['maximum_bidirectional_surface_error']<1e-5
        assert visual['revision']==2 and sha(ROOT/visual['comparison']['path'])==visual['comparison']['sha256'] and visual['comparison']['refined_binary_sha256']==meta['binaries']['glb']
        assert visual['binaries']==meta['binaries'] and visual['observations'] and not runtime['final_user_artistic_acceptance']
        assert videos['binaries']==meta['binaries'] and videos['runtime_review_sha256']==sha(folder/'runtime-review.json')
        for name,record in videos['clips'].items():assert sha(ROOT/name)==record['sha256'] and record['frames']==24 and record['seconds']==4
        media=ROOT/'gallery/media/proposals/engineering-ships'/culture/role
        assert len(runtime['renders'])==6
        for name,digest in runtime['renders'].items():assert sha(media/name)==digest
        assert not list(media.glob('*-frames')),'Unremoved intermediate animation frames'
        glb=(folder/'model.glb').read_bytes();doc=json.loads(glb[20:20+struct.unpack_from('<I',glb,12)[0]])
        assert len(doc['animations'])==1 and doc['animations'][0]['name']=='ToolOperation'
        assert len(doc['animations'][0]['channels'])==len(meta['clips'][0]['motion'])==runtime['exported_animation_channels']
        assert all('normalTexture' in m and 'metallicRoughnessTexture' in m['pbrMetallicRoughness'] for m in doc['materials'])
        assert sum(doc['accessors'][primitive['indices']]['count']//3 for mesh in doc['meshes'] for primitive in mesh['primitives'])==meta['triangles']
        assert all('bufferView' in image for image in doc['images'])
        nodes={n['name']:n for n in doc['nodes'] if 'name' in n};assert nodes['ProposalRoot']['extras']['status']=='proposal-awaiting-mechanics' and nodes['ProposalRoot']['extras']['asset_revision']==2
        row,=[x for x in gallery['models'] if (x['culture'],x['role'])==(culture,role)];assert row['metadata_sha256']==sha(folder/'model.json')
        for path in list(folder.iterdir())+list(media.iterdir()):
            if path.is_file():assert not problems(path),(path.relative_to(ROOT).as_posix(),problems(path))
        models.append(dict(culture=culture,role=role,triangles=meta['triangles'],meshes=meta['meshes'],moving_parts=len(runtime['moving_parts']),animation_channels=runtime['exported_animation_channels']))
    if a.base:
        protected=['gallery/catalogue.json','gallery/supplemental-catalogue.json','sources/docs/reconstruction/models/inventory.json','sources/content']
        assert not subprocess.check_output(['git','diff','--name-only',a.base,'--',*protected],cwd=ROOT).strip(),'Canonical/runtime catalogue changed'
    print('ENGINEERING_DELIVERY_OK',json.dumps(dict(refinement_revision=2,selected_cultures=sorted(a.cultures) if a.cultures else 'all seven',models=models,runtime_integration=False,new_legacy_units=False)))
if __name__=='__main__':main()
