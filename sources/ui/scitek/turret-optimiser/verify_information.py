"""Check complete movie and source material/caption clocks independently."""
import sys,json,hashlib,subprocess,struct
from pathlib import Path
from PIL import Image,ImageChops
o=Path(sys.argv[1]);clock_path=Path(sys.argv[2]) if len(sys.argv)>2 else Path(__file__).parent/'material-clock.json';clock=json.loads(clock_path.read_text());d=json.loads((o/'information-timeline.json').read_text())
assert d['frame_count']==423 and len(d['timeline'])==423
assert d['material_clock_sha256']==hashlib.sha256(clock_path.read_bytes()).hexdigest()
assert d['renderer_sha256']==hashlib.sha256((clock_path.parent/'animate_information.py').read_bytes()).hexdigest()
assert d['source_sha256']==hashlib.sha256((clock_path.parent/'turret-optimiser.blend').read_bytes()).hexdigest()
relative='sources/docs/reconstruction/scitek/material-clocks.json';candidates=[p/r for p in Path(__file__).resolve().parents for r in [relative,relative.removeprefix('sources/')]]+[Path('../openfa-assets')/relative]
audit_path=next(p for p in candidates if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==clock['source_clock_audit_sha256'])
reference=json.loads(audit_path.read_text())['records'][31]
assert clock['red_active_by_frame']==reference['red_active_by_frame'] and clock['decoded_update_by_frame']==reference['decoded_update_by_frame']
assert clock['phase_start_updates']==[0,65,130] and clock['phase_start_frames']==[0,141,282]
assert clock['components']==['stored-energy-output','manual-pulse-control','flux-capacitor-system']
raw_glb=(o/'turret-optimiser-information.glb').read_bytes();gltf=json.loads(raw_glb[20:20+struct.unpack_from('<I',raw_glb,12)[0]])
assert 'KHR_materials_unlit' in gltf['extensionsUsed'] and len(gltf['materials'])==4
assert all('KHR_materials_unlit' in material.get('extensions',{}) for material in gltf['materials'])
frames=sorted((o/'frames').glob('*.png'));assert [p.name for p in frames]==[f'{i:03}.png' for i in range(423)]
def masks_from_image(im):
 r,g,b=im.split();positive=lambda c:c.point(lambda v:255 if v>0 else 0)
 red=ImageChops.multiply(r.point(lambda v:255 if v>70 else 0),positive(ImageChops.subtract(r,g.point(lambda v:min(255,v*2)))))
 red=ImageChops.multiply(red,positive(ImageChops.subtract(r,b.point(lambda v:min(255,v*2)))))
 whole=ImageChops.lighter(ImageChops.lighter(r,g),b).point(lambda v:255 if v>40 else 0)
 return whole,red
def masks(path):return masks_from_image(Image.open(path).convert('RGB'))
def iou(a,b):
 intersection=ImageChops.darker(a,b).histogram()[255];union=ImageChops.lighter(a,b).histogram()[255];return intersection/union
for i,path in enumerate(frames):
 frame=d['timeline'][i];update=clock['decoded_update_by_frame'][i];phase=max(j for j,start in enumerate(clock['phase_start_updates']) if update>=start)
 expected=clock['components'][phase] if clock['red_active_by_frame'][i] else None
 caption=clock['components'][reference['caption_phase_by_frame'][i]] if reference['caption_phase_by_frame'][i]>=0 else None
 assert frame['highlight_component']==expected and frame['caption_component']==caption and frame['source_decoded_update']==update,(i,frame)
 assert (masks(path)[1].getbbox() is not None)==clock['red_active_by_frame'][i],('rendered red presence',i)
 assert d['native_frame_sha256'][path.name]==hashlib.sha256(path.read_bytes()).hexdigest()
assert sum(f['highlight_component'] is not None for f in d['timeline'])==334
assert sum(f['caption_component'] is not None for f in d['timeline'])==333
ious={}
assert d['independent_import_samples']==clock['independent_import_samples'] and len(d['independent_import_samples'])==21
for i in d['independent_import_samples']:
 a,red_a=masks(o/f'frames/{i:03}.png');b,red_b=masks(o/f'imported-{i:03}.png');score=iou(a,b);assert score>.94,(i,score)
 assert (red_b.getbbox() is not None)==clock['red_active_by_frame'][i]
 red_score=iou(red_a,red_b) if clock['red_active_by_frame'][i] else None
 if red_score is not None:assert red_score>.9,(i,red_score)
 ious[str(i)]=dict(whole_iou=score,red_iou=red_score)
expected={tuple(round(v,5) for v in f['rotation_euler']+f['camera_position']+[f['ortho_scale']])+(f['highlight_component'],) for f in d['timeline']};assert len(expected)>150
assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in frames})>=len(expected)*.8
assert ImageChops.difference(Image.open(o/'frames/087.png'),Image.open(o/'reload-0088.png')).getbbox(alpha_only=False) is None
state=json.loads((o/'material-state-verification.json').read_text());assert state['material_clock_sha256']==d['material_clock_sha256'] and state['evaluated_frames']==423
subprocess.run(['ffmpeg','-y','-v','error','-framerate','15','-i',str(o/'frames/%03d.png'),'-c:v','libvpx-vp9','-lossless','1','-pix_fmt','gbrp',str(o/'information.webm')],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(o/'information.webm'),'-f','null','-'],check=True)
stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(o/'information.webm')]))['streams'][0];assert int(stream['nb_read_frames'])==423
assert stream['pix_fmt']=='gbrp' and stream['profile']=='Profile 1'
decoder=subprocess.Popen(['ffmpeg','-v','error','-i',str(o/'information.webm'),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
for i in range(423):
 raw=decoder.stdout.read(224*224*3);assert len(raw)==224*224*3
 assert raw==Image.open(frames[i]).convert('RGB').tobytes(),('lossless decoded RGB',i)
 assert (masks_from_image(Image.frombytes('RGB',(224,224),raw))[1].getbbox() is not None)==clock['red_active_by_frame'][i],('encoded red clock',i)
assert not decoder.stdout.read(1);assert decoder.wait()==0
(o/'verification.json').write_text(json.dumps(dict(frame_count=423,fps=15,source_sha256=d['source_sha256'],renderer_sha256=d['renderer_sha256'],material_clock_sha256=d['material_clock_sha256'],source_red_frames=334,caption_visible_frames=333,source_material_clock_matches_all_frames=True,source_caption_clock_matches_all_frames=True,decoded_movie_red_clock_matches_all_frames=True,decoded_movie_rgb_matches_all_frames=True,video_encoding="VP9 Profile 1 lossless RGB (gbrp)",information_materials_unlit=True,independent_import_samples=ious,video_sha256=hashlib.sha256((o/'information.webm').read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8',newline='\n')
print('OPTIMISER_COMPLETE_SOURCE_CLOCK_INFORMATION_VERIFIED')
