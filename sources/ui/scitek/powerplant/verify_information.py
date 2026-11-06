from pathlib import Path
import json,hashlib,sys
from PIL import Image
out=Path(sys.argv[1]);source=Path(sys.argv[2]);data=json.loads((out/'information-timeline.json').read_text());clock=json.loads((source/'material-clock.json').read_text())
assert data['frame_count']==564 and data['rendered_frame_count']==564
assert data['renderer_sha256']==hashlib.sha256((source/'animate_information.py').read_bytes()).hexdigest()
assert sorted(p.name for p in (out/'frames').glob('*.png'))==[f'{i:03}.png' for i in range(564)]
for i,t in enumerate(data['timeline']):
 expected=clock['components'][clock['component_phase_by_frame'][i]] if clock['red_active_by_frame'][i] else None
 caption=clock['components'][clock['caption_phase_by_frame'][i]] if clock['caption_phase_by_frame'][i]>=0 else None
 assert t['highlight_component']==expected and t['caption_component']==caption
 im=Image.open(out/f'frames/{i:03}.png').convert('RGB');assert im.getbbox()
assert len({t['ortho_scale'] for t in data['timeline']})>50
ious={}
for f in data['independent_import_samples']:
 a=Image.open(out/f'frames/{f:03}.png').convert('RGB');b=Image.open(out/f'imported-{f:03}.png').convert('RGB')
 aa={i for i,p in enumerate(a.getdata()) if max(p)>40};bb={i for i,p in enumerate(b.getdata()) if max(p)>40};iou=len(aa&bb)/len(aa|bb);assert iou>.80,(f,iou);ious[f]=iou
proof=dict(frame_count=564,independent_import_samples=len(ious),foreground_iou=ious,timeline_material_and_caption_source_states=True,all_frames_nonempty=True,animated_zoom=True,source_sha256=data['source_sha256'],renderer_sha256=data['renderer_sha256'],limitations=['Authored camera, geometry and wire topology; approximate visual correspondence, no pixel fidelity claim.'])
(out/'verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print('ENGINE_INFORMATION_VERIFIED',min(ious.values()))
