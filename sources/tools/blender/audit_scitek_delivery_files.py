"""Read-only current-state delivery audit; decode every published research film."""
from pathlib import Path
import json,sys,hashlib,subprocess,concurrent.futures
from PIL import Image,ImageChops
root,out=map(lambda p:Path(p).resolve(),sys.argv[1:]);integration=json.loads((root/'gallery/media/ui/scitek/integration.json').read_text());rows=[];jobs=[];failures=[];lookup={r['id']:r for r in integration['records']};legacy={r['research_id']:r for r in json.loads((root/'sources/docs/reconstruction/scitek/menu-audit.json').read_text())['records']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for rec in integration['records']:
 row=dict(id=rec['id'],binding=rec.get('binding'));rows.append(row)
 try:
  for key in ['native','hires','blend','glb','readme']:
   assert (root/rec[key]).is_file(),(key,rec.get(key))
  for view in rec.get('gallery_views',[]):
   for key in ['image','video','blend','glb']:
    if view.get(key):assert (root/view[key]).is_file(),(key,view[key])
  media=(root/rec['native']).parent;native=Image.open(root/rec['native']).convert('RGBA');hires=Image.open(root/rec['hires']).convert('RGBA');row['native_size']=list(native.size);row['hires_size']=list(hires.size)
  if '/research/' in rec.get('binding',''):
   expected=legacy[rec['id']]['preview']['sizes'];assert hires.size==tuple(v*4 for v in native.size);row['legacy_canvas_options']=expected
   if list(native.size) not in expected:row['format_error']='Published tile canvas differs from actual legacy product sprite';failures.append(dict(id=rec['id'],error=row['format_error'],published=list(native.size),legacy=expected))
   disabled=Image.open(root/rec['disabled']).convert('RGBA');assert disabled.size==native.size;assert ImageChops.difference(native.getchannel('A'),disabled.getchannel('A')).getbbox() is None
   channels=disabled.split();assert ImageChops.difference(channels[0],channels[1]).getbbox() is None and ImageChops.difference(channels[1],channels[2]).getbbox() is None
   info_path=root/rec['information_animation']['timeline'];timeline=json.loads(info_path.read_text());assert timeline['source_sha256']==sha(root/rec['blend']);assert timeline['frame_count']==len(timeline['timeline'])==rec['information_animation']['frame_count']
   if 'rendered_frame_count' in timeline:assert timeline['rendered_frame_count']==timeline['frame_count']
   proof=json.loads((media/'preview-verification.json').read_text());assert proof['source_sha256']==sha(root/rec['blend']);count=proof['frames'];assert proof['fps']==15
   jobs.extend([(rec['id'],'preview',media/'preview.webm',count),(rec['id'],'information',media/'information.webm',timeline['frame_count'])]);row.update(kind='research',colour_frames=count,information_frames=timeline['frame_count'],current_information_source=True,current_preview_source=True,disabled_alpha_and_grayscale=True,model_relationship='shared-object' if rec.get('shared_object') else rec.get('model_relationship',{}).get('kind'));assert row['model_relationship'] in ['shared-object','upgrade-device-presentation']
  elif rec['id'].startswith('scitek:category-'):
   assert native.size==(80,64) and hires.size==(320,256);c=native.split();assert ImageChops.difference(c[0],c[1]).getbbox() is None and ImageChops.difference(c[1],c[2]).getbbox() is None
   proof=json.loads((media/'provenance.json').read_text());assert proof['blend_sha256']==sha(root/rec['blend']) and proof['glb_sha256']==sha(root/rec['glb']);subjects=[]
   for subject in proof['subjects']:
    source=root/subject['source'];assert subject['source_sha256']==sha(source);meta=json.loads((source.parent/'model.json').read_text());owner=lookup.get(meta.get('id'));subjects.append(dict(source=subject['source'],current_source_hash=True,uses_authoritative_shared_path=(owner is None or not owner.get('shared_object') or owner['blend']==subject['source'])))
   assert json.loads((media/'raster-verification.json').read_text())['derived_exact_monochrome'];row.update(kind='category',current_source_provenance=True,subjects=subjects)
  elif rec['id']=='scitek:screen-logo':
   assert native.size==(320,160) and hires.size==(1280,640);proof=json.loads((media/'proof.json').read_text());assert proof['hashes']['scitek-screen-logo.blend']==sha(root/rec['blend']) and proof['hashes']['scitek-screen-logo.glb']==sha(root/rec['glb']);assert proof['silhouette_iou']>.999;row.update(kind='logo',native_reload_and_independent_import_proof=proof['checks'],independent_import_silhouette_iou=proof['silhouette_iou'])
  row['status']='failed' if row.get('format_error') else 'verified'
 except Exception as error:row.update(status='failed',error=str(error));failures.append(dict(id=rec['id'],error=str(error)))
def movie(job):
 ident,kind,path,count=job
 try:
  stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(path)]))['streams'][0];assert int(stream['nb_read_frames'])==count,(kind,stream['nb_read_frames'],count)
  subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(path),'-f','null','-'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  return dict(id=ident,kind=kind,path=path.relative_to(root).as_posix(),frames=count,sha256=sha(path),decoded=True)
 except Exception as error:return dict(id=ident,kind=kind,decoded=False,error=str(error))
movies=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for result in pool.map(movie,jobs):movies.append(result);print('SCITEK_FILM_CHECKED',result['id'],result['kind'],result['decoded'],flush=True)
report=dict(scope='All36 research deliveries, all72 complete films, six category collages and main logo. File/provenance/format/film checks complement independent Blender import and subject-specific legacy/geometry/raster checks.',records=rows,movies=movies,failures=failures,counts=dict(research=sum(r.get('kind')=='research' for r in rows),categories=sum(r.get('kind')=='category' for r in rows),logos=sum(r.get('kind')=='logo' for r in rows),movies=len(movies),failed_records=len(failures),failed_movies=sum(not x['decoded'] for x in movies)),limitations=['This does not inspect the game package or replace actual client/GPU checks owned by the integration thread.','File/decode checks alone are not visual legacy-fidelity acceptance.'])
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SCITEK_DELIVERY_AUDIT',report['counts']);assert not failures and len(movies)==72 and all(x['decoded'] for x in movies)
