"""Audit seven station pairs against current GLB buffers, source evidence and runtime reports."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gallery_animation_assets import animation_previews, glb_clips

ROOT=Path(__file__).resolve().parents[1]
KEYS={'BR4C','PS7C','RI4C','MK4C','AR5C','MN5C','AC3C'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))


class Glb:
    def __init__(self,path):
        raw=path.read_bytes();assert raw[:4]==b'glTF' and struct.unpack_from('<I',raw,8)[0]==len(raw)
        size,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a;self.data=json.loads(raw[20:20+size]);offset=20+size
        size,kind=struct.unpack_from('<II',raw,offset);assert kind==0x004e4942;self.binary=raw[offset+8:offset+8+size]
        self.nodes={n['name']:i for i,n in enumerate(self.data['nodes'])};assert len(self.nodes)==len(self.data['nodes'])
        self.parents={c:i for i,n in enumerate(self.data['nodes']) for c in n.get('children',[])};self.world={}
        for i in range(len(self.data['nodes'])):self.matrix(i)

    def accessor(self,index):
        a=self.data['accessors'][index];assert 'sparse' not in a;v=self.data['bufferViews'][a['bufferView']];assert v['buffer']==0
        dtype=np.dtype({5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]);columns={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',columns*dtype.itemsize)
        return np.ndarray((a['count'],columns),dtype=dtype,buffer=self.binary,offset=offset,strides=(stride,dtype.itemsize)).copy()

    def matrix(self,index):
        if index in self.world:return self.world[index]
        n=self.data['nodes'][index]
        if 'matrix' in n:m=np.array(n['matrix'],dtype=float).reshape((4,4),order='F')
        else:
            x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]];m[:3,:3]=m[:3,:3]@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0])
        self.world[index]=self.matrix(self.parents[index])@m if index in self.parents else m
        return self.world[index]

    def mesh_nodes(self):return {n['name']:i for i,n in enumerate(self.data['nodes']) if 'mesh' in n}

    def attributes(self,node):
        matrix=self.world[node];out=[]
        for p in self.data['meshes'][self.data['nodes'][node]['mesh']]['primitives']:
            attrs={k:self.accessor(v).astype(float) for k,v in p['attributes'].items()};pos=attrs['POSITION'];attrs['POSITION']=(np.c_[pos,np.ones(len(pos))]@matrix.T)[:,:3]
            if 'NORMAL' in attrs:
                normals=attrs['NORMAL']@np.linalg.inv(matrix[:3,:3]);attrs['NORMAL']=normals/np.linalg.norm(normals,axis=1)[:,None]
            out.append((attrs,self.accessor(p['indices']),p.get('mode',4),self.data['materials'][p['material']]['name']))
        return out


def compare_finished(finished,construction):
    names=finished.mesh_nodes();assert names.keys()<=construction.mesh_nodes().keys();error=0.0
    for name,index in finished.nodes.items():
        assert name in construction.nodes;other=construction.nodes[name]
        assert np.allclose(finished.world[index],construction.world[other],atol=1e-6,rtol=0),(name,'Finished transform changed')
        p=finished.parents.get(index);q=construction.parents.get(other)
        assert (None if p is None else finished.data['nodes'][p]['name'])==(None if q is None else construction.data['nodes'][q]['name'])
    for name,index in names.items():
        a=finished.attributes(index);b=construction.attributes(construction.nodes[name]);assert len(a)==len(b)
        for (aa,ai,am,material),(ba,bi,bm,othermaterial) in zip(a,b):
            assert aa.keys()==ba.keys() and np.array_equal(ai,bi) and am==bm and material==othermaterial,(name,'Topology/material changed')
            for key in aa:
                assert aa[key].shape==ba[key].shape and np.allclose(aa[key],ba[key],atol=2e-6,rtol=0),(name,key,'Finished vertex attribute changed')
                error=max(error,float(np.abs(aa[key]-ba[key]).max()))
    return len(names),error


def validate_activity(model):
    assert len(model.data.get('animations',[]))==1;clip=model.data['animations'][0];assert clip['name']=='ConstructionActivity'
    target={c['target']['node'] for c in clip['channels']};assert len(target)==1
    index=next(iter(target));assert model.data['nodes'][index]['name']=='ConstructionWorkCarriage'
    descendants=set()
    def visit(i):
        descendants.add(i)
        for child in model.data['nodes'][i].get('children',[]):visit(child)
    visit(index);moving=sorted(model.data['nodes'][i]['name'] for i in descendants if 'mesh' in model.data['nodes'][i]);assert len(moving)==3
    changes=[]
    for channel in clip['channels']:
        assert channel['target']['path'] in ['translation','rotation'];s=clip['samplers'][channel['sampler']];times=model.accessor(s['input']);values=model.accessor(s['output']);assert s.get('interpolation','LINEAR')=='LINEAR'
        assert abs(float(times[-1,0]-times[0,0])-6)<1e-5 and np.allclose(values[0],values[-1],atol=1e-6,rtol=0)
        changes.append(float(np.ptp(values,axis=0).max()))
    assert max(changes)>.01
    return moving


def bound_report(state,pair,source_hashes):
    model=ROOT/state['blend'];meta=read(model.with_suffix('.json'));path=ROOT/state['validation'];report=read(path)
    for ext in ['blend','glb']:assert sha(model.with_suffix('.'+ext))==state[ext+'_sha256']==meta[ext+'_sha256']==report[ext+'_sha256']
    assert report['native_mesh_count']==report['imported_mesh_count'] and report['maximum_native_imported_position_error']<1e-4
    assert meta['generator_sha256'] in source_hashes and report['generator_sha256'] in source_hashes and report['verifier_sha256'] in source_hashes
    for record,key in [(meta,'dependency_sha256'),(meta,'dependencies_sha256'),(report,'verifier_dependencies_sha256')]:
        for n,digest in record.get(key,{}).items():assert sha(ROOT/'sources/tools/blender'/n)==digest
    for n,digest in meta.get('texture_sha256',{}).items():assert sha(ROOT/n)==digest
    if meta.get('source_study'):assert sha(ROOT/meta['source_study'])==meta['source_blend_sha256']
    if meta.get('source_glb_sha256'):assert sha((ROOT/meta['source_study']).with_suffix('.glb'))==meta['source_glb_sha256']
    for view,result in report['renders'].items():
        assert result['native_sha256']==sha(path.parent/(view+'.png')) and result['imported_sha256']==sha(path.parent/('imported-'+view+'.png'))
        assert result['silhouette_iou']>=.99998 and result['foreground_rgb_mean_difference_255']<1
    for side in ['native','imported']:assert report[side+'_structure']['positive_closed_meshes']==report[side+'_mesh_count']
    return meta,report


def source_review(pair,legacy,archive,entries,codec,baseline,cdb):
    if pair['key']=='BR4C':
        evidence=next(x for x in baseline['records'] if x['key']=='BR4C')['surface'];frames=evidence['layers'];lore=read(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json');assert lore['source']['sha256']==sha(legacy/'_TEXT/ENGLISH.CDB');records=lore['records']
    else:
        evidence=read(ROOT/pair['evidence']);frames=evidence['decoded_frames'];records=evidence.get('full_cdb_records_read',[])
        assert evidence['archive_sha256']==sha(legacy/'_S/_S') and evidence['codec_sha256']==sha(legacy/'tools/fragile256.py')
        assert evidence['ship_reference_index_sha256']==sha(ROOT/'sources/docs/reconstruction/models/ship-reference-index.json')
        if 'functional_index_sha256' in evidence:assert evidence['functional_index_sha256']==sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json')
        assert evidence.get('cdb_sha256',evidence.get('cdb',{}).get('sha256'))==sha(legacy/'_TEXT/ENGLISH.CDB')
        if pair['key']=='PS7C':
            headings=evidence['cdb']['section_headings'];assert [h['record'] for h in headings]==[i for i,b in enumerate(cdb) if b.startswith(b'>')]
            for h in headings:assert cdb[h['record']].decode('cp1252')==h['text']
    functional=read(ROOT/'sources/docs/reconstruction/models/functional-text-index.json')
    def find(value):
        if isinstance(value,dict):
            if value.get('id')==pair['id']:return value
            children=value.values()
        elif isinstance(value,list):children=value
        else:return None
        for child in children:
            found=find(child)
            if found:return found
    current=find(functional);assert current is not None
    if pair['key']!='BR4C':assert evidence['functional_record']==current
    language=(legacy/'_TEXT/ENGLISH.TXT').read_bytes();assert hashlib.sha256(language).hexdigest()==functional['sources']['language_file']['sha256']
    name=current['name_reference'];assert name['sha256']==hashlib.sha256(language[name['offset']:name['offset']+name['byte_length']]).hexdigest()
    entry=entries[evidence['source_entry']];payload=archive[entry.offset:entry.offset+entry.length];assert hashlib.sha256(payload).hexdigest()==evidence['source_sha256']
    private=ROOT/'artifacts/issue-192/audit-decoded';private.mkdir(parents=True,exist_ok=True);path=private/evidence['source_entry'];path.write_bytes(payload);raw,descriptors,palette,_=codec.read_sprites(path);assert len(descriptors)==len(frames)==2
    decoded=[]
    for descriptor,reference in zip(descriptors,frames):
        start=codec.GLOBAL_HEADER_SIZE+descriptor.stream_offset;indices=codec.decode_sprite(raw[start:start+descriptor.stream_length],descriptor.width,descriptor.height);im=Image.frombytes('P',(descriptor.width,descriptor.height),indices);im.putpalette(codec.palette_to_png(palette));rgba=im.convert('RGBA');rgba.putalpha(Image.frombytes('L',im.size,bytes(255 if v else 0 for v in indices)))
        ref=ROOT/reference['png'];assert sha(ref)==reference['png_sha256'] and rgba.tobytes()==Image.open(ref).convert('RGBA').tobytes();decoded.append(dict(index=reference['index'],size=list(rgba.size),indices_sha256=hashlib.sha256(indices).hexdigest()))
    for record in records:
        index=record.get('index',record.get('record'));assert hashlib.sha256(cdb[index]).hexdigest()==record['sha256']
    return dict(functional_name_sha256=name['sha256'],payload_sha256=evidence['source_sha256'],freshly_decoded_descriptors=decoded,cdb_records_revalidated=len(records))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--legacy-root',type=Path,required=True);args=parser.parse_args();legacy=args.legacy_root
    manifest_path=ROOT/'sources/docs/reconstruction/models/orbital-station-variants.json';manifest=read(manifest_path);assert {x['key'] for x in manifest['records']}==KEYS and len(manifest['records'])==7
    assert manifest['shared_scale_reference']=='finished' and manifest['shared_placement_root']=='PlacementRoot'
    catalogue={x['id']:x for x in read(ROOT/'gallery/catalogue.json')};baseline=read(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json');assert len(baseline['records'])==38
    for row in baseline['records']:
        for ext in ['blend','glb']:assert sha((ROOT/row['baseline_study']).with_suffix('.'+ext))==row[ext+'_sha256']
    source_hashes={sha(p) for p in (ROOT/'sources/tools/blender').glob('*.py')};sys.path.insert(0,str(legacy/'tools'));codec=importlib.import_module('fragile256');_,archive,entries=codec.read_archive(legacy/'_S/_S');entries={e.name:e for e in entries};cdb=(legacy/'_TEXT/ENGLISH.CDB').read_bytes().split(b'\0');results=[]
    for pair in manifest['records']:
        assert pair['status']=='runtime-verified' and pair['finished']['legacy_sprite_frame']==0 and pair['construction']['legacy_sprite_frame']==1
        fm,fr=bound_report(pair['finished'],pair,source_hashes);cm,cr=bound_report(pair['construction'],pair,source_hashes)
        if pair.get('evidence'):
            assert cm['evidence_sha256']==sha(ROOT/pair['evidence'])
            if 'evidence_sha256' in cr:assert cr['evidence_sha256']==cm['evidence_sha256']
        assert cm['source_study']==pair['finished']['blend'] and cm['source_blend_sha256']==pair['finished']['blend_sha256']
        assert cr['finished_body_geometry_uv_normals_preserved'] and cr['finished_helpers_preserved'] and len(cr['sampled_frames'])==13
        assert cr['native_structure']['closed_positive_components']>600 and len(cr['static_mesh_names'])==cr['native_mesh_count']-3
        finished=Glb(ROOT/pair['finished']['glb']);construction=Glb(ROOT/pair['construction']['glb']);assert not finished.data.get('animations');count,error=compare_finished(finished,construction);assert count==fr['native_mesh_count']==len(cm['preserved_mesh_names'])
        moving=validate_activity(construction);assert moving==cr['moving_mesh_names'];clips=animation_previews(pair['construction']['blend'],pair['construction']['glb'],(ROOT/pair['construction']['validation']).parent);assert len(clips)==1 and clips[0]['duration']==6 and clips[0]['frames']==144 and clips[0]['distinct_pose_count']>100
        assert not glb_clips(ROOT/pair['finished']['glb']);studies=catalogue[pair['id']]['studies']
        for variant in ['finished','construction']:
            state=pair[variant];matching=[s for s in studies if s['blend']==state['blend']];assert len(matching)==1 and matching[0]['sha256']==state['blend_sha256'];assert bool(matching[0]['animations'])==(variant=='construction')
        result=dict(key=pair['key'],id=pair['id'],finished_meshes=count,construction_meshes=cr['native_mesh_count'],construction_closed_components=cr['native_structure']['closed_positive_components'],direct_glb_finished_world_attribute_error=error,render_pairs=len(fr['renders'])+len(cr['renders']),maximum_runtime_position_error=max(fr['maximum_native_imported_position_error'],cr['maximum_native_imported_position_error']),finished_validation_sha256=sha(ROOT/pair['finished']['validation']),construction_validation_sha256=sha(ROOT/pair['construction']['validation']),moving_meshes=moving,clip=clips[0],source_review=source_review(pair,legacy,archive,entries,codec,baseline,cdb));results.append(result)
    sheet=Image.new('RGB',(1200,1780),(25,29,33));draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=18);small=ImageFont.load_default(size=14);draw.text((20,15),'ORBITAL STATIONS | Finished and under construction',fill='white',font=font);draw.text((20,44),'Actual model previews; each view is independently framed, not a runtime scale comparison.',fill=(180,190,200),font=small)
    for i,pair in enumerate(manifest['records']):
        y=80+i*240;draw.text((20,y),pair['key']+'  '+pair['name']+'  /  '+pair['culture'],fill=(225,210,180),font=font)
        for j,variant in enumerate(['finished','construction']):
            p=(ROOT/pair[variant]['validation']).parent/'front-quarter.png';im=Image.open(p).convert('RGBA');im=im.crop(im.getchannel('A').getbbox());im.thumbnail((550,185));sheet.paste(im,(20+j*600+(550-im.width)//2,y+30+(185-im.height)//2),im)
        draw.line((20,y+230,1180,y+230),fill=(60,68,74))
    overview=ROOT/'gallery/sheets/orbital-station-pairs.jpg';sheet.save(overview,quality=92)
    output=dict(issue=192,overview=dict(path=overview.relative_to(ROOT).as_posix(),sha256=sha(overview)),scope='Seven finished/construction orbital-station pairs; not the pending all-38 Braccatian completion audit',audit_tool_sha256=sha(Path(__file__)),functional_index_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),manifest_sha256=sha(manifest_path),gallery_sha256=sha(ROOT/'gallery/catalogue.json'),original_braccatian_model_pairs_preserved=38,records=results,totals=dict(pairs=len(results),models=14,construction_movies=7,finished_meshes=sum(r['finished_meshes'] for r in results),construction_meshes=sum(r['construction_meshes'] for r in results),closed_construction_components=sum(r['construction_closed_components'] for r in results),paired_renders=sum(r['render_pairs'] for r in results)),limitations=['Authored hidden geometry, profiles, repeated counts and six-second activity timing; no recovered legacy timing claimed','Finished reference normalization must be shared by both states; final game scale/orientation and mount calibration remain integration work'])
    path=ROOT/'sources/docs/reconstruction/models/orbital-station-audit.json';path.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8');print('ORBITAL_STATION_AUDIT_OK',output['totals'])


if __name__=='__main__':main()
