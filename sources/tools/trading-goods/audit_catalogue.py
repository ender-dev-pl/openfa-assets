"""Audit complete coloured-model coverage without requiring Blender or private reference media."""
from pathlib import Path
import argparse,json,hashlib,struct,math
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3]);ap.add_argument('--report',type=Path);a=ap.parse_args();repo=a.repo.resolve();d=json.loads((repo/'docs/trading-goods/coverage.json').read_text());items=d['items'];assert len(items)==101 and [x['id'] for x in items]==list(range(101));registered={r['destination'] for r in json.loads((repo/'project/layout.json').read_text())['files']};records=[];inherited=0
for item in items:
 ident=f"TI{item['id']+1:03d}";assert item['legacy_stem']==ident;assert item['model_status']=='coloured_model_verified';paths={}
 for key in ['native','static_glb','validation']:
  rel=item[key];p=(repo/rel).resolve();assert p.is_relative_to(repo) and p.is_file(),rel;assert rel in registered,rel;paths[key]=p
 r=json.loads(paths['validation'].read_text());assert all(r[k] for k in ['native_reopened','independent_glb_import','base_colours_roundtrip_verified']);assert r['imported_geometry_objects']>=r['native_geometry_objects']>0;assert r['original_bitmaps_used'] is False
 assert hashlib.sha256(paths['native'].read_bytes()).hexdigest()==r['native_sha256'];blob=paths['static_glb'].read_bytes();assert hashlib.sha256(blob).hexdigest()==r['glb_sha256'];magic,version,size=struct.unpack_from('<4sII',blob);assert (magic,version,size)==(b'glTF',2,len(blob));length,kind=struct.unpack_from('<I4s',blob,12);assert kind==b'JSON';gltf=json.loads(blob[20:20+length]);assert not gltf.get('images');assert gltf.get('meshes') and gltf.get('materials')
 for m in gltf['materials']:
  rgba=m.get('pbrMetallicRoughness',{}).get('baseColorFactor',[1,1,1,1]);assert len(rgba)==4 and all(math.isfinite(c) and 0<=c<=1 for c in rgba)
 evidence=json.loads((paths['native'].parent/'model.json').read_text());assert evidence['item_id']==item['id'] and evidence['legacy_stem']==ident;assert evidence['reference_pixels_published'] is False;assert evidence['native_sha256']==r['native_sha256'] and evidence['glb_sha256']==r['glb_sha256'];assert all(im['status']=='deferred_by_user' and im['output'] is None for im in item['images'].values())
 inheritance=paths['native'].parent/'inheritance.json'
 if inheritance.exists():
  proof=json.loads(inheritance.read_text());assert proof['geometry_preserved_during_reuse'] is True;assert proof['inherited_native_sha256']==evidence['observations']['inherited_native_sha256'];assert proof['inherited_source']==evidence['observations']['inherited_source'];inherited+=1
 records.append(dict(id=item['id'],legacy_stem=ident,native_sha256=r['native_sha256'],glb_sha256=r['glb_sha256'],model_verified=True))
assert inherited==13
report=dict(coverage_sha256=hashlib.sha256((repo/'docs/trading-goods/coverage.json').read_bytes()).hexdigest(),source_tools_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((repo/'sources/tools/trading-goods').iterdir()) if p.is_file() and p.suffix in ['.py','.json']},coloured_models_verified=101,native_sources=101,static_glbs=101,independent_runtime_reports=101,base_colour_roundtrips=101,final_images_deferred=202,inherited_missile_sources=13,original_reference_pixels_published=False,geometry_artistic_limit='First reconstruction pass with inferred hidden parts/markings; refining and game integration remain separate.',items=records)
if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
print('CATALOGUE_VERIFIED: 101 coloured models, 101 native/GLB runtime reports, 202 final images deferred')
