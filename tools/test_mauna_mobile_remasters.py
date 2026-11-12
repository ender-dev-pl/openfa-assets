"""Source-bound Mauna form, UV projection, voids, materials and canonical selection."""
from pathlib import Path
import hashlib,io,json,struct,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'sources/tools/blender'))
from archive_evidence import verify_bound_input
import numpy as np
from PIL import Image
from test_artemian_mobile_remasters import atlas_areas
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def read_accessor(raw,g,length,index):
    a=g['accessors'][index];v=g['bufferViews'][a['bufferView']]
    dtype=np.dtype({5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]);size={'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']]
    return np.ndarray((a['count'],size),dtype=dtype,buffer=raw,offset=28+length+v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',size*dtype.itemsize),dtype.itemsize))


def check_type5_end_uv(raw,g,length):
    mesh=g['meshes'][next(n['mesh'] for n in g['nodes'] if n['name']=='PrimaryHullAndArmour')];count=0;total=0
    for primitive in mesh['primitives']:
        pos=read_accessor(raw,g,length,primitive['attributes']['POSITION']);axis=int(np.argmax(np.ptp(pos,axis=0)))
        ids=read_accessor(raw,g,length,primitive['indices']).reshape(-1,3);p=pos[ids];uv=read_accessor(raw,g,length,primitive['attributes']['TEXCOORD_0'])[ids]
        geometric=np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1)/2
        a=uv[:,1]-uv[:,0];b=uv[:,2]-uv[:,0];textured=abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])/2
        end=(np.ptp(p[:,:,axis],axis=1)<1e-6)&(abs(p[:,:,axis].mean(axis=1))>.83)&(geometric>1e-9)
        # Cylindrical mapping collapses these broad planar end surfaces to a
        # texture line. Check actual exported triangles, not a UV-mode label.
        assert (textured[end]/geometric[end]>.01).all(),'collapsed end-face UVs'
        count+=int(end.sum());total+=float(geometric[end].sum())
    assert count>10 and total>1.0,(count,total)


def main():
    # The repository stores root tools as LF. Bind the generator's committed
    # byte representation, so a new clone can validate the same model proof.
    assert b'\r\n' not in (ROOT/'tools/author_mauna_mobile_maps.py').read_bytes(),'Normalize the map generator to repository LF before recording model hashes'
    doc=json.loads((ROOT/'sources/docs/reconstruction/models/mauna-mobile-remaster.json').read_text());models=doc['models'];assert 1<=len(models)<=doc['expected_mobile_ship_count']==5
    refs=json.loads((ROOT/'sources/docs/reconstruction/models/ship-reference-index.json').read_text())['ships'];expected={r['id'] for r in refs if r['culture']=='mauna' and not r['runtime_fixed_scale']}
    assert {r['id'] for r in models}|set(doc['pending'])==expected and not {r['id'] for r in models}&set(doc['pending'])
    assert doc['quality_followups']==[]
    inventory=json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_text());results=[]
    assert next(r for r in inventory['records'] if r['id']=='openfa:ship/mauna/elite-command-craft')['acceptance']['high_detail_structure'] is True
    for row in models:
        folder=(ROOT/row['blend']).parent;meta=json.loads((folder/'model.json').read_text());proof=json.loads((folder/'runtime-verification.json').read_text());review=json.loads((folder/'concept-review.json').read_text());media=ROOT/'gallery/media/objects/mauna'/folder.name
        suffix={'max-combat-craft-type-6':'type6','elite-command-craft':'elite'}.get(folder.name,'mobile_ship')
        assert proof['generator_sha256']==meta['generator_sha256']==sha(ROOT/('sources/tools/blender/remaster_mauna_'+suffix+'.py'))
        assert proof['verifier_sha256']==sha(ROOT/('sources/tools/blender/verify_mauna_'+suffix+'.py'))
        if suffix in ['type6','elite']:
            assert proof['verifier_inputs_unchanged'] is True
            assert proof['shared_mauna_verifier_sha256']==sha(ROOT/'sources/tools/blender/verify_mauna_mobile_ship.py')
            assert proof['detail_parts_sha256']==meta['detail_parts_sha256']==sha(ROOT/('sources/tools/blender/mauna_'+suffix+'_detail_parts.py'))
        assert meta['shared_recipe_helpers_sha256']==sha(ROOT/'sources/tools/blender/remaster_artemian_mobile_ship.py')
        assert proof['shared_geometry_verifier_sha256']==sha(ROOT/'sources/tools/blender/verify_artemian_mobile_ship.py')
        assert meta['shared_primitives_sha256']==sha(ROOT/'sources/tools/blender/remaster_braccatian_mobile_ships.py')
        assert meta['maps_generator_sha256']==sha(ROOT/'tools/author_mauna_mobile_maps.py')
        assert proof['recipe_sha256']==meta['recipe_sha256']==sha(folder/'recipe.json')
        assert proof['baseline_sha256']==meta['baseline_sha256']
        bound=next(r for r in inventory['records'] if r['id']==row['id'])['reviewed_model']['runtime_evidence']
        verify_bound_input(ROOT,bound,'sources/'+meta['source']+'/model.blend',meta['baseline_sha256'])
        for kind in ['blend','glb']:assert sha(folder/('model.'+kind))==proof['binaries'][kind]==row[kind+'_sha256']
        assert review['reviewed_binary_hashes']==proof['binaries'] and 1<=len(review['iterations'])<=3
        ref=next(r for r in refs if r['id']==row['id']);assert review['legacy_identity']['source_sha256']==ref['source_sha256']
        for it in review['iterations']:assert it['prompt'] and it['verdict'] and sha(ROOT/it['image'])==it['sha256'] and it['input_images']
        for name,digest in meta['map_sha256'].items():assert sha(ROOT/'sources/materials/mauna/mobile-ships'/name)==digest
        for name,digest in proof['renders'].items():assert sha(media/name)==digest
        assert proof['relative_surface_deviation']<.012 and proof['source_import_position_error']<1e-5 and proof['triangles']<meta['max_triangles']
        assert len(proof['attachments_checked'])==len(meta['attachment_pairs']) and len(proof['protected_dents'])==len(meta['protected_dents'])
        for stage in ['native','imported']:assert proof['ray_witnesses'][stage]=={key:len(meta.get(key,[])) for key in ['void_rays','solid_rays']}
        raw=(folder/'model.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+length])
        assert len(g['meshes'])==meta['mesh_batches']==4 and len(g['materials'])==1 and len(g['images'])==3
        assert sum(len(m['primitives']) for m in g['meshes'])<=meta['max_primitives'] and not g.get('animations')
        assert all('uri' not in image for image in g['images']) and not any(g['materials'][0].get('emissiveFactor',[0,0,0]))
        if folder.name=='max-combat-craft-type-6':
            names={name for group in meta['editable_part_vertex_groups'].values() for name in group}
            detail_names=set(meta['detailed_parts']['names'])
            assert len(names)==58+len(detail_names) and len(detail_names)>100
            assert len(proof['attachments_checked'])==len(names)-1 and len(proof['protected_dents'])==3
            assert proof['ray_witnesses']['native']==dict(void_rays=2,solid_rays=3)
            assert len({n for n in names if n.startswith('Type 6 red raised piece ')})==2
            assert len({n for n in names if 'detail roof shoulder armour ' in n})==4
            assert len({n for n in names if 'detail service bay backing ' in n})==6
            assert meta['material_tiles']['Type 6 | worn red raised pieces']==6
            assert review['attempts_used']==review['maximum_attempts']==3 and len(review['failed_attempts'])==2
            assert review['user_references'] and [it['number'] for it in review['iterations']]==[3]
            for item in review['user_references']:assert sha(ROOT/item['image'])==item['sha256']
            for field,name in [('detail_baseline_helpers_sha256','mauna_max_combat_craft_type_6_parts.py'),('detail_primitives_sha256','build_openfa_assets.py')]:
                assert proof[field]==meta[field]==sha(ROOT/'sources/tools/blender'/name)
            # Actual exported muted-red surfaces must remain separated across
            # the beam, at the same longitudinal deck station (glTF +Z=-Y).
            red=[]
            for mesh in g['meshes']:
                for prim in mesh['primitives']:
                    uv=read_accessor(raw,g,length,prim['attributes']['TEXCOORD_0']);pos=read_accessor(raw,g,length,prim['attributes']['POSITION']);idx=read_accessor(raw,g,length,prim['indices']).reshape(-1,3)
                    means=uv[idx].mean(axis=1);tiles=np.floor(means[:,0]*4)+4*np.floor(means[:,1]*2)
                    red.extend(pos[idx[tiles==6]].mean(axis=1))
            red=np.asarray(red);assert len(red)>20 and red[:,0].min()<-.25 and red[:,0].max()>.25
            assert red[:,2].min()>.60 and np.ptp(red[:,2])<.50
        if folder.name=='surveillance-craft-type-5':
            names={name for group in meta['editable_part_vertex_groups'].values() for name in group}
            assert len(names)==47 and len({n for n in names if 'crown tab' in n})==4 and len({n for n in names if 'warm lower tab' in n})==2
            assert len(proof['attachments_checked'])==46 and len(proof['protected_dents'])==2
            assert proof['ray_witnesses']['native']==dict(void_rays=3,solid_rays=4)
            areas=atlas_areas(raw,g,length,'PrimaryHullAndArmour');assert areas[0]>.8 and .01<areas[5]<.15,areas.tolist()
            check_type5_end_uv(raw,g,length)
        if folder.name=='combat-craft-type-1-5':
            names={name for group in meta['editable_part_vertex_groups'].values() for name in group}
            assert len(names)==49 and {'Type 1.5 fore raised deck','Type 1.5 aft raised deck'}<=names
            assert len(proof['attachments_checked'])==48 and len(proof['protected_dents'])==3
            assert proof['ray_witnesses']['native']==dict(void_rays=3,solid_rays=2)
            assert meta['material_tiles']['Type 1.5 | dull pale blue grey end']==3
            assert meta['comparison_heading_directions']=={'12':[0,-1,.95],'28':[0,1,.95]}
        if folder.name=='elite-command-craft':
            names={name for group in meta['editable_part_vertex_groups'].values() for name in group}
            detail_names=set(meta['detailed_parts']['names'])
            assert len(names)==59+len(detail_names) and len(detail_names)>90
            assert {'Elite pod -1','Elite pod 1','Elite central connection'}<=names
            assert len(proof['attachments_checked'])==len(names)-1 and len(proof['protected_dents'])==2
            assert len({n for n in names if 'detail end blue armour ' in n})==4
            assert len({n for n in names if 'detail end upper blue field ' in n})==2
            assert len({n for n in names if 'detail connector side truss ' in n})==8
            assert len({n for n in names if 'detail axial collar ' in n and 'pin' not in n})==4
            assert review['detail_reviewed_binary_hashes']==proof['binaries'] and review['construction_detail_feedback']
            for item in review['user_references']:assert sha(ROOT/item['image'])==item['sha256']
            assert meta['presentation_hero_direction']==[12,-8,6]
            for field,name in [('detail_baseline_helpers_sha256','mauna_elite_command_craft_parts.py'),('detail_primitives_sha256','build_openfa_assets.py')]:
                assert proof[field]==meta[field]==sha(ROOT/'sources/tools/blender'/name)
            assert proof['ray_witnesses']['native']==dict(void_rays=2,solid_rays=3)
            assert meta['material_tiles']['Elite | worn red tips']==6
            assert review['attempts_used']==review['maximum_attempts']==3 and len(review['failed_attempts'])==2
            assert [it['number'] for it in review['iterations']]==[3]
            assert meta['comparison_heading_directions']=={'12':[0,-1,.25],'28':[0,1,.25]}
            areas=atlas_areas(raw,g,length,'PrimaryHullAndArmour');assert areas[6]>0 and areas[3]>.02,areas.tolist()
            # Check actual broad blue end faces, beyond narrow vertical strips.
            broad_blue=0
            for mesh in g['meshes']:
                for prim in mesh['primitives']:
                    uv=read_accessor(raw,g,length,prim['attributes']['TEXCOORD_0']);pos=read_accessor(raw,g,length,prim['attributes']['POSITION']);idx=read_accessor(raw,g,length,prim['indices']).reshape(-1,3)
                    means=uv[idx].mean(axis=1);tiles=np.floor(means[:,0]*4)+4*np.floor(means[:,1]*2);points=pos[idx];centre=points.mean(axis=1)
                    mask=(tiles==3)&(abs(centre[:,2])>1.11)&(centre[:,1]>.145)&(centre[:,1]<.295)&(np.ptp(points[:,:,0],axis=1)>.60)
                    broad_blue+=int(mask.sum())
            assert broad_blue>=4,'Missing broad opaque blue end fields'

        if folder.name=='transportation-craft-type-3':
            names={name for group in meta['editable_part_vertex_groups'].values() for name in group}
            assert len(names)==83 and {f'Transport tower {i}' for i in [-1,0,1]}<=names
            assert len({n for n in names if n.startswith('Transport blue band ')})==12
            assert len(proof['attachments_checked'])==82 and len(proof['protected_dents'])==3
            assert proof['ray_witnesses']['native']==dict(void_rays=29,solid_rays=12)
            rotations=meta['part_rotations'];assert len(rotations)==3 and sum(len(r['parts']) for r in rotations)==66
            assert all(r['axis']=='Z' and abs(r['angle']+np.pi/2)<1e-8 for r in rotations)
            areas=atlas_areas(raw,g,length,'PrimaryHullAndArmour');assert .06<areas[3]<.35,areas.tolist()
        texture=g['materials'][0]['pbrMetallicRoughness']['metallicRoughnessTexture']['index'];image=g['images'][g['textures'][texture]['source']];view=g['bufferViews'][image['bufferView']];start=28+length+view.get('byteOffset',0)
        orm=np.asarray(Image.open(io.BytesIO(raw[start:start+view['byteLength']])).convert('RGB')).astype(float)/255
        assert orm.shape[:2]==(1024,2048) and .57<orm[:512,:512,1].mean()<.64 and .72<orm[:512,:512,2].mean()<.76
        native=np.asarray(Image.open(media/'verified-native.png').convert('RGBA')).astype(float);imported=np.asarray(Image.open(media/'verified-imported.png').convert('RGBA')).astype(float);a=native[:,:,3]>128;b=imported[:,:,3]>128
        iou=float((a&b).sum()/(a|b).sum());rgb=float(abs(native[:,:,:3]-imported[:,:,:3])[a&b].mean());assert iou>.995 and rgb<4
        bounds=Image.open(media/'heading-04.png').convert('RGBA').getchannel('A').point(lambda v:255 if v>128 else 0).getbbox();aspect=(bounds[2]-bounds[0])/(bounds[3]-bounds[1]);w,h=meta['reference_side_bounds']
        # One source pixel is significant for a six-pixel-high sprite. Keep
        # the prior coarse camera tolerance, with explicit raster uncertainty;
        # this is a proportion diagnostic, never an artistic acceptance score.
        low=min(.82*w/h,(w-1)/(h+1));high=max(1.18*w/h,(w+1)/max(1,h-1))
        assert low<aspect<high,(folder.name,aspect,(low,high),w/h)
        record=next(r for r in inventory['records'] if r['id']==row['id']);assert len(record['available_studies'])==1 and 'sources/'+record['available_studies'][0]['blend']==row['blend']
        results.append(dict(id=row['id'],alpha_iou=iou,mean_rgb_error_255=rgb,**proof['binaries']))
    (ROOT/'sources/docs/reconstruction/models/mauna-mobile-delivery.json').write_text(json.dumps(dict(models=results,pending=doc['pending'],scope='Verified asset milestones only; client calibration and final user artistic acceptance separate'),indent=2)+'\n');print('MAUNA_DELIVERY_OK',results)


if __name__=='__main__':main()
