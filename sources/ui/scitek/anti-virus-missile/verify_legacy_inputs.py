"""Optional original installation verification using the actual audit bindings.

Usage: python verify_scitek_legacy_inputs.py INDEX OUTPUT [LEGACY_ROOT ASSET_ROOT]
Private reference pixels are never copied into authored deliverables.
"""
import sys,json,hashlib
from pathlib import Path
index=int(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
legacy=Path(sys.argv[3] if len(sys.argv)>3 else '../legacy').resolve()
assets=Path(sys.argv[4] if len(sys.argv)>4 else '../openfa-assets').resolve()
sys.path.insert(0,str(legacy/'tools'));import fragile256
audit=json.loads((assets/'sources/docs/reconstruction/scitek/menu-audit.json').read_text())['records'][index]
captions=json.loads((assets/'sources/docs/reconstruction/scitek/caption-phase-map.json').read_text())['records'][index]
_,raw,entries=fragile256.read_archive(legacy/'_MA/_MA')
entry=next(x for x in entries if x.name==audit['preview']['file'])
digest=hashlib.sha256(raw[entry.offset:entry.offset+entry.length]).hexdigest();assert digest==audit['preview']['sha256']
proof=dict(research_index=index,research_id=audit['research_id'],tile=dict(file=entry.name,sha256=digest),videos={},captions=[])
for key in ['preview_animation','information']:
 record=audit[key];binding=record['source'];path=legacy/binding['directoryName']/binding['fileName']
 digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==record['source_sha256']
 proof['videos'][key]=dict(source=binding,sha256=digest,timeline_frames=record['timeline_frames'])
records=(legacy/'_TEXT/ENGLISH.TXT').read_bytes().split(b'\0')
for caption in captions['captions']:
 text=records[caption['textRecord']].decode('cp1252');assert text==caption['text']
 proof['captions'].append(dict(text_record=caption['textRecord'],text=text,first_frame=caption['firstFrame'],last_frame=caption['lastFrame']))
(out/'legacy-input-verification.json').write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
print('SCITEK_LEGACY_INPUTS_VERIFIED',index,entry.name,len(proof['captions']))
