"""Source-bound geometry, export, concept feedback and one-canonical-selection gates."""
from pathlib import Path
import hashlib,io,json,struct
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def atlas_areas(raw,document,json_length,mesh_name):
    def read(index):
        a=document['accessors'][index];v=document['bufferViews'][a['bufferView']]
        dtype=np.dtype({5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]);size={'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']]
        return np.ndarray((a['count'],size),dtype=dtype,buffer=raw,offset=28+json_length+v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',size*dtype.itemsize),dtype.itemsize))
    totals=np.zeros(8)
    mesh=document['meshes'][next(n['mesh'] for n in document['nodes'] if n['name']==mesh_name)]
    for primitive in mesh['primitives']:
        indices=read(primitive['indices']).reshape(-1,3);points=read(primitive['attributes']['POSITION'])[indices];uv=read(primitive['attributes']['TEXCOORD_0'])[indices]
        # glTF exporter flips Blender V: GLB coordinates address top image row
        # at V=0, unlike the authoring UV coordinates used by the generator.
        tiles=np.floor(uv[:,:,0]*4).astype(int)+4*np.floor(uv[:,:,1]*2).astype(int)
        assert (tiles[:,0]==tiles[:,1]).all() and (tiles[:,0]==tiles[:,2]).all(),'triangle crosses atlas materials'
        area=np.linalg.norm(np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0]),axis=1)/2
        for tile in range(8):totals[tile]+=area[tiles[:,0]==tile].sum()
    return totals/totals.sum()


def main():
    publication=json.loads((ROOT/'sources/docs/reconstruction/models/artemian-mobile-remaster.json').read_text());models=publication['models'];assert 1<=len(models)<=publication['expected_mobile_ship_count']==5
    refs=json.loads((ROOT/'sources/docs/reconstruction/models/ship-reference-index.json').read_text())['ships'];expected={r['id'] for r in refs if r['culture']=='artemian' and not r['runtime_fixed_scale']}
    assert {r['id'] for r in models}|set(publication['pending'])==expected and not {r['id'] for r in models}&set(publication['pending'])
    inventory=json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_text());results=[]
    for row in models:
        folder=(ROOT/row['blend']).parent;meta=json.loads((folder/'model.json').read_text());proof=json.loads((folder/'runtime-verification.json').read_text());review=json.loads((folder/'concept-review.json').read_text());media=ROOT/'gallery/media/objects/artemian'/folder.name
        assert proof['generator_sha256']==sha(ROOT/'sources/tools/blender/remaster_artemian_mobile_ship.py') and proof['verifier_sha256']==sha(ROOT/'sources/tools/blender/verify_artemian_mobile_ship.py')
        assert proof['recipe_sha256']==meta['recipe_sha256']==sha(folder/'recipe.json')
        assert meta['shared_primitives_sha256']==sha(ROOT/'sources/tools/blender/remaster_braccatian_mobile_ships.py') and meta['maps_generator_sha256']==sha(ROOT/'tools/author_artemian_mobile_maps.py')
        for kind in ['blend','glb']:assert sha(folder/('model.'+kind))==proof['binaries'][kind]==row[kind+'_sha256']
        assert review['reviewed_binary_hashes']==proof['binaries'] and 1<=len(review['iterations'])<=3
        ref=next(r for r in refs if r['id']==row['id']);assert review['legacy_identity']['source_sha256']==ref['source_sha256']
        for it in review['iterations']:assert it['prompt'] and it['verdict'] and sha(ROOT/it['image'])==it['sha256'] and it['input_images']
        for name,digest in meta['map_sha256'].items():assert sha(ROOT/'sources/materials/artemian/mobile-ships'/name)==digest
        for name,digest in proof['renders'].items():assert sha(media/name)==digest
        assert proof['relative_surface_deviation']<.012 and proof['source_import_position_error']<1e-5 and proof['triangles']<meta['max_triangles']
        assert len(proof['attachments_checked'])==len(meta.get('attachment_pairs',[]))
        assert len(proof['protected_dents'])==len(meta.get('protected_dents',[])) and len(proof['profile_checks'])==len(meta.get('profile_constraints',[]))
        if folder.name=='all-purpose-assault':
            names={name for group in meta['editable_part_vertex_groups'].values() for name in group}
            assert len(names)==54 and {name for name in names if 'grey cowl' in name}=={'All-Purpose central grey cowl','All-Purpose port grey cowl','All-Purpose starboard grey cowl'}
            # Actual surface-distance evidence must detect a manufactured edge
            # change; simply recording a bevel recipe does not prove it ran.
            assert .0003<proof['part_surface_errors']['All-Purpose green delta hull']<.01
            assert all(.0003<proof['part_surface_errors'][f'All-Purpose service cover {i}']<.01 for i in range(6))
            assert len(proof['attachments_checked'])==53 and len(proof['protected_dents'])==4
        raw=(folder/'model.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+length])
        assert len(g['materials'])==1 and len(g['meshes'])==meta['mesh_batches']==4 and len(g['images'])==3
        assert sum(len(m['primitives']) for m in g['meshes'])<=meta['max_primitives'] and not g.get('animations')
        assert all('uri' not in im for im in g['images'])
        if folder.name=='shielded-multi-assault':
            names={name for group in meta['editable_part_vertex_groups'].values() for name in group}
            assert len(names)==46 and len(proof['attachments_checked'])==45 and len(proof['protected_dents'])==3
            # Read actual GLB positions, UVs and indices: bronze must be a
            # subordinate alloy region, not the historical exact half split.
            areas=atlas_areas(raw,g,length,'PrimaryHullAndArmour')
            assert areas[0]>.65 and .04<areas[2]<.30 and areas[1]<.001,areas.tolist()
        if folder.name=='ultimate-mk-ii':
            names={name for group in meta['editable_part_vertex_groups'].values() for name in group}
            assert len(names)==55 and len({n for n in names if 'perimeter fitting' in n})==12
            assert len(proof['attachments_checked'])==54 and len(proof['protected_dents'])==2
            assert all(d['measured_depth']>.004 for d in proof['protected_dents'])
            assert len(meta['part_transforms'])==12 and all(c['axial_scale']<.5 for c in meta['part_transforms'])
            assert all(proof['part_surface_errors'][c['part']]<.005 for c in meta['part_transforms'])
            lower=atlas_areas(raw,g,length,'PrimaryHullAndArmour');lid=atlas_areas(raw,g,length,'ServiceAssemblies')
            assert lower[1]>.5 and lid[0]>.8,(lower.tolist(),lid.tolist())
            assert not any(g['materials'][0].get('emissiveFactor',[0,0,0])),'unproven emission'
        if folder.name=='hardcore':
            names={name for group in meta['editable_part_vertex_groups'].values() for name in group}
            assert len(names)==48 and len({n for n in names if 'main pressure body' in n})==2 and len({n for n in names if 'lateral module' in n})==4
            assert len(proof['attachments_checked'])==51 and len(proof['protected_dents'])==6
            assert all(d['measured_depth']>(.003 if 'main pressure' in d['part'] else .001) for d in proof['protected_dents'])
            areas=atlas_areas(raw,g,length,'PrimaryHullAndArmour');assert areas[2]>.80 and .01<areas[0]<.20 and areas[1]<.001,areas.tolist()
            assert not any(g['materials'][0].get('emissiveFactor',[0,0,0])),'unproven emission'
        ti=g['materials'][0]['pbrMetallicRoughness']['metallicRoughnessTexture']['index'];im=g['images'][g['textures'][ti]['source']];view=g['bufferViews'][im['bufferView']];start=28+length+view.get('byteOffset',0)
        texture=np.asarray(Image.open(io.BytesIO(raw[start:start+view['byteLength']])).convert('RGB')).astype(float)/255
        assert texture.shape[:2]==(1024,2048) and .52<texture[:512,:512,1].mean()<.60 and .75<texture[:512,:512,2].mean()<.81
        native=np.asarray(Image.open(media/'verified-native.png').convert('RGBA')).astype(float);imported=np.asarray(Image.open(media/'verified-imported.png').convert('RGBA')).astype(float);a=native[:,:,3]>128;b=imported[:,:,3]>128
        iou=float((a&b).sum()/(a|b).sum());rgb=float(abs(native[:,:,:3]-imported[:,:,:3])[a&b].mean());assert iou>.995 and rgb<4
        bounds=Image.open(media/'heading-04.png').convert('RGBA').getchannel('A').point(lambda v:255 if v>128 else 0).getbbox();aspect=(bounds[2]-bounds[0])/(bounds[3]-bounds[1]);w,h=meta['reference_side_bounds'];assert abs(aspect/(w/h)-1)<.18,(folder.name,aspect,w/h)
        record=next(r for r in inventory['records'] if r['id']==row['id']);assert len(record['available_studies'])==1 and 'sources/'+record['available_studies'][0]['blend']==row['blend']
        results.append(dict(id=row['id'],alpha_iou=iou,mean_rgb_error_255=rgb,**proof['binaries']))
    path=ROOT/'sources/docs/reconstruction/models/artemian-mobile-delivery.json';path.write_text(json.dumps(dict(models=results,pending=publication['pending'],scope='Verified asset milestones only; client calibration and final user acceptance separate'),indent=2)+'\n');print('ARTEMIAN_DELIVERY_OK',results)


if __name__=='__main__':main()
