"""Check canonical delivery, actual GLB budgets and native/import image agreement."""
import hashlib
import json
from pathlib import Path
import struct
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    style=json.loads((ROOT/'sources/objects/rigellian/fleet-style.json').read_text())
    migration=json.loads((ROOT/'sources/objects/rigellian/canonical-assets.json').read_text())
    inventory=json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_text())
    gallery=json.loads((ROOT/'gallery/catalogue.json').read_text())
    results=[]
    for ship in style['ships']:
        folder=ROOT/ship['canonical_directory'];report=json.loads((folder/'runtime-verification.json').read_text())
        model=json.loads((folder/'model.json').read_text());generation=json.loads((folder/'generation.json').read_text())
        assert report['generator_sha256']==sha(ROOT/'sources/tools/blender/build_rigellian_mobile_fleet.py')
        assert report['verifier_sha256']==sha(ROOT/'sources/tools/blender/verify_rigellian_mobile_fleet.py')
        for ext in ['blend','glb']:
            assert sha(folder/f'model.{ext}')==report[ext+'_sha256']==model[ext+'_sha256']==generation[ext+'_sha256']
        data=(folder/'model.glb').read_bytes();assert data[:4]==b'glTF'
        length,kind=struct.unpack_from('<II',data,12);assert kind==0x4E4F534A
        document=json.loads(data[20:20+length]);assert document['asset']['version']=='2.0'
        assert len(document['materials'])==1
        assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' for m in document['materials'])
        assert len(document['images'])==3 and all('bufferView' in im and 'uri' not in im for im in document['images'])
        assert all('uri' not in b for b in document['buffers'])
        triangles=sum(document['accessors'][p['indices']]['count']//3 for mesh in document['meshes'] for p in mesh['primitives'])
        assert triangles==report['triangles']==model['triangles']<=style['budgets']['max_triangles_per_ship']
        assert len(document['meshes'])==report['mesh_batches']<=style['budgets']['max_meshes_per_ship']
        assert abs(max(model['measured_dimensions'])-ship['authoring_length_units'])<.00001
        selected=next(r for r in inventory['records'] if r['id']==ship['id'])
        published=next(r for r in gallery if r['id']==ship['id'])
        assert len(selected['available_studies'])==len(published['studies'])==1
        assert published['studies'][0]['glb']==ship['canonical_directory']+'/model.glb'
        retired=next(r for r in migration['models'] if r['id']==ship['id'])['removed_models']
        assert len(retired)==4 and all(not (ROOT/r['path']).exists() for r in retired)
        media=ROOT/'gallery/media/objects/rigellian'/ship['slug']
        for name,digest in report['renders'].items():assert sha(media/name)==digest
        a=np.array(Image.open(media/'verified-native.png').convert('RGBA'))
        b=np.array(Image.open(media/'verified-imported.png').convert('RGBA'))
        first,second=a[:,:,3]>16,b[:,:,3]>16;union=first|second;intersection=first&second
        iou=float(intersection.sum()/union.sum());assert iou>.999
        difference=float(np.abs(a[:,:,:3].astype(float)-b[:,:,:3]).mean(axis=2)[intersection].mean())
        assert difference<1,(ship['slug'],'material discrepancy',difference)
        yy,xx=np.where(union)
        assert min(xx)>8 and min(yy)>8 and max(xx)<a.shape[1]-9 and max(yy)<a.shape[0]-9,'clipped render'
        results.append({'id':ship['id'],'triangles':triangles,'mesh_batches':len(document['meshes']),
                        'native_import_alpha_iou':iou,'native_import_rgb_mae_255_foreground':difference,
                        'four_superseded_binary_payloads_retired':True,'embedded_images':3})
    output={'issue':232,'reviewer_sha256':sha(Path(__file__)),'models':results,
            'visual_review':'Broad formed skins; rejected dense grid removed. Functional details and restrained wear reviewed separately from technical equality. User and game visual acceptance not implied.',
            'scope':'Asset delivery only; proposed sizes and uncalibrated weapon sockets require client integration review.'}
    (ROOT/'sources/objects/rigellian/delivery-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print('RIGELLIAN_DELIVERY_VERIFIED',json.dumps(results))


if __name__=='__main__':main()
