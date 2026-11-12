"""Recover per-frame red/green selection from source-bound original-codec caches.

This records state metadata only. Original reference pixels are not published.
Usage: python audit_scitek_material_clocks.py ASSET_ROOT LEGACY_ROOT CACHE_ROOT OUTPUT
"""
import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
assets,legacy,cache,out=map(Path,sys.argv[1:5]);out.parent.mkdir(parents=True,exist_ok=True)
audit=json.loads((assets/'sources/docs/reconstruction/scitek/menu-audit.json').read_text())
captions=json.loads((assets/'sources/docs/reconstruction/scitek/caption-phase-map.json').read_text())
records=[]
for record,caption in zip(audit['records'],captions['records']):
 index=record['index'];binding=record['information']['source'];source=legacy/binding['directoryName']/binding['fileName'];raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==record['information']['source_sha256']
 folder=cache/f'ST{index:02}';inputs=json.loads((folder/'inputs.json').read_text());assert inputs['source_sha256']==sha
 metadata=json.loads((folder/'metadata.json').read_text());clock=[];update=-1;expected_offset=28
 for chunk in metadata['chunks']:
  offset=chunk['offset'];assert offset==expected_offset;assert chunk['size']>=8;expected_offset+=chunk['size'];assert raw[offset:offset+4].decode('ascii')==chunk['tag'];assert int.from_bytes(raw[offset+4:offset+8],'little')==chunk['size']
  if chunk['tag']=='Fram':update+=1;assert chunk['index']==update
  if chunk['tag'] in ['Fram','Same']:assert update>=0;clock.append(update)
 assert expected_offset==len(raw)
 assert len(clock)==record['information']['timeline_frames']==caption['timeline_frames']
 assert update+1==record['information']['image_updates']
 counts=[];frame_hash=hashlib.sha256()
 for n in range(update+1):
  path=folder/'frames'/f'{n:03}.png';frame_hash.update(hashlib.sha256(path.read_bytes()).digest())
  im=Image.open(path).convert('RGB');r,g,b=im.split()
  positive=lambda channel:channel.point(lambda v:255 if v>0 else 0)
  mask=ImageChops.multiply(r.point(lambda v:255 if v>70 else 0),positive(ImageChops.subtract(r,g.point(lambda v:min(255,v*2)))))
  mask=ImageChops.multiply(mask,positive(ImageChops.subtract(r,b.point(lambda v:min(255,v*2)))))
  counts.append(mask.histogram()[255])
 active=[counts[n]>0 for n in clock]
 text_phases=[next((i for i,c in enumerate(caption['captions']) if c['firstFrame']<=f<=c['lastFrame']),-1) for f in range(len(clock))]
 mismatch=[f for f,(a,b) in enumerate(zip(active,text_phases)) if a!=(b>=0)]
 records.append(dict(index=index,research_id=record['research_id'],source=binding,source_sha256=sha,cache_provenance=inputs,cached_png_hash_chain=frame_hash.hexdigest(),timeline_frames=len(clock),decoded_update_by_frame=clock,red_pixel_count_by_update=counts,red_active_by_frame=active,caption_phase_by_frame=text_phases,caption_red_mismatch_frames=mismatch,caption_windows=caption['captions']))
 print('MATERIAL_CLOCK',index,len(clock),'frames;',len(mismatch),'caption/material differences')
result=dict(issue=208,method='Exhaustive Fram/Same source-byte-verified clock; source-bound cached RGB red presence: R>70, R>2G, R>2B. Red activity and caption visibility are recorded separately.',limitations=['This audit measures red presence, not the semantic identity of the highlighted component. Component transitions require separate subject-specific source review.','This audit does not recover 3D geometry, camera interpolation, exact colour intensity or pixel-level renderer equivalence.','Cache decoder provenance is retained; the codec is not re-executed by this audit.'],records=records,subjects=len(records),total_frames=sum(x['timeline_frames'] for x in records),subjects_with_distinct_material_clock=sum(bool(x['caption_red_mismatch_frames']) for x in records))
assert len(records)==36
out.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
print('SCITEK_MATERIAL_CLOCKS_AUDITED',len(records),result['total_frames'],result['subjects_with_distinct_material_clock'])
