"""Focused source/import/material/render and canonical-selection regression gates."""
from pathlib import Path
import hashlib,json,struct
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    models=json.loads((ROOT/'sources/docs/reconstruction/models/mikotaj-mobile-remaster.json').read_text())['models'];assert len(models)==4
    inventory=json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_text());results=[]
    for row in models:
        folder=(ROOT/row['blend']).parent;report=json.loads((folder/'runtime-verification.json').read_text());meta=json.loads((folder/'model.json').read_text());media=ROOT/'gallery/media/objects/mikotaj'/folder.name
        for k in ['blend','glb']:assert sha(ROOT/row[k])==row[k+'_sha256']==report['binaries'][k]
        assert report['generator_sha256']==sha(ROOT/'sources/tools/blender/remaster_mikotaj_mobile_ships.py')
        assert report['verifier_sha256']==sha(ROOT/report.get('verifier_path','sources/tools/blender/verify_mikotaj_mobile_remasters.py'))
        assert meta['shared_primitives_sha256']==sha(ROOT/'sources/tools/blender/remaster_braccatian_mobile_ships.py')
        assert meta['maps_generator_sha256']==sha(ROOT/'tools/author_mikotaj_ship_maps.py')
        for n,h in meta['map_sha256'].items():assert sha(ROOT/'sources/materials/mikotaj/mobile-ships'/n)==h
        for n,h in report['renders'].items():assert sha(media/n)==h
        concept=json.loads((folder/'concept-review.json').read_text())
        assert 1<=len(concept['iterations'])<=3
        assert concept['reviewed_binary_hashes']==report['binaries']
        refs=json.loads((ROOT/'sources/docs/reconstruction/models/ship-reference-index.json').read_text())['ships']
        ref=next(r for r in refs if r['id']==row['id'])
        assert concept['legacy_identity']['source_sha256']==ref['source_sha256']
        for iteration in concept['iterations']:
            assert iteration['prompt'] and iteration['verdict'] and sha(ROOT/iteration['image'])==iteration['sha256']
        if folder.name=='hiero':
            spikes=json.loads((folder/'spike-verification.json').read_text())
            assert spikes['binaries']==report['binaries']
            assert spikes['spikes']==8 and spikes['spacing_degrees']==45 and spikes['seated_native_contacts']==8
            assert spikes['ray_checks']==dict(native=8,imported=8)
            assert spikes['patcher_sha256']==sha(ROOT/'sources/tools/blender/refine_hiero_peripheral_spikes.py')
            assert spikes['verifier_sha256']==sha(ROOT/'sources/tools/blender/verify_hiero_peripheral_spikes.py')
        assert report['mesh_batches']==4 and report['triangles']<55000
        assert report['source_import_position_error']<1e-5
        revised=meta.get('geometry_revision')=='glass-sphere-parallel-modules'
        if revised:
            assert folder.name=='falari-lourn' and report['parallel_modules']==4 and report['seated_modules']==4
            assert report['spacing_degrees']==90 and report['imported_glass_transmission_verified']
            assert report['revision_generator_sha256']==sha(ROOT/meta['geometry_refinement']['generator'])
            assert all(abs(a+2.8)<1e-5 and abs(b-2.8)<1e-5 for a,b in report['common_longitudinal_extents'])
        else:assert report['relative_surface_deviation']<.012
        raw=(folder/'model.glb').read_bytes();g=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
        assert len(g['materials'])==(2 if revised else 1) and len(g['meshes'])==4 and len(g['images'])==3
        if revised:
            glass=[m for m in g['materials'] if m.get('extensions',{}).get('KHR_materials_transmission',{}).get('transmissionFactor',0)>.7]
            assert len(glass)==1 and abs(glass[0]['extensions']['KHR_materials_ior']['ior']-1.46)<1e-5
        assert not g.get('animations') and all('uri' not in image for image in g['images'])
        assert sum(len(m['primitives']) for m in g['meshes'])==4
        side=Image.open(media/'heading-04.png').convert('RGBA').getchannel('A');box=side.point(lambda value:255 if value>128 else 0).getbbox();aspect=(box[2]-box[0])/(box[3]-box[1]);w,h=meta['reference_side_alpha_bounds']
        assert abs(aspect/(w/h)-1)<.15,('legacy side silhouette aspect',folder.name,aspect,w/h)
        selected=next(r for r in inventory['records'] if r['id']==row['id']);assert len(selected['available_studies'])==1
        assert 'sources/'+selected['available_studies'][0]['blend']==row['blend']
        native=np.asarray(Image.open(media/'verified-native.png').convert('RGBA')).astype(float);imported=np.asarray(Image.open(media/'verified-imported.png').convert('RGBA')).astype(float)
        a=native[:,:,3]>128;b=imported[:,:,3]>128;iou=float((a&b).sum()/(a|b).sum());rgb=float(abs(native[:,:,:3]-imported[:,:,:3])[a&b].mean())
        assert iou>.995 and rgb<4,(row['id'],iou,rgb)
        results.append(dict(id=row['id'],alpha_iou=iou,mean_rgb_error_255=rgb,**report['binaries']))
    output=ROOT/'sources/docs/reconstruction/models/mikotaj-mobile-delivery.json';output.write_text(json.dumps(dict(models=results,scope='Asset verification only; runtime scaling and weapon socket calibration remain separate'),indent=2)+'\n');print('MIKOTAJ_DELIVERY_OK',results)


if __name__=='__main__':main()
