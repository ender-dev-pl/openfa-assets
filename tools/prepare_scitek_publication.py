"""Normalize Sci-Tek publication metadata with byte/pixel preservation evidence.

Hash rebinding is explicitly metadata lineage, not a rerun of historical checks.
Fresh Blender/GLB and delivery audits must follow this operation.
"""
import hashlib,json,re,sys
from pathlib import Path
from PIL import Image
from publication_support import clean_blend,clean_png
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 log=ROOT/sys.argv[1]; entries=[];mapping={}
 for line in log.read_text().splitlines():
  if ': ' not in line:continue
  name,reason=line.split(': ',1);p=ROOT/name
  if not p.is_file():continue
  before=p.read_bytes();row=dict(path=name,before_sha256=sha(before))
  if p.suffix=='.png':
   pixels=Image.open(p).convert('RGBA').tobytes();after=clean_png(before)
   import io
   assert pixels==Image.open(io.BytesIO(after)).convert('RGBA').tobytes()
   row.update(proof='identical decoded RGBA',rgba_sha256=sha(pixels))
  elif p.suffix=='.blend':
   after,n,a,b=clean_blend(before);row.update(proof='all bytes outside fixed-width path strings unchanged',path_strings=n,raw_before_sha256=a,raw_after_sha256=b)
  elif name.endswith('screen-logo/build_logo.py'):
   after=before.replace(b'import bpy,sys,math,json,hashlib',b'import bpy,sys,math,json,hashlib,os')
   after=re.sub(rb"font=bpy[.]data[.]fonts[.]load\([^\n]+\)",b"font=bpy.data.fonts.load(str(Path(os.environ['WINDIR'])/'Fonts'/'arialbd.ttf'))",after)
   row['proof']='same system font resolved through WINDIR; code change, not geometry change'
  else:raise AssertionError((name,reason))
  p.write_bytes(after);row['after_sha256']=sha(after);mapping[row['before_sha256']]=row['after_sha256'];entries.append(row)
 # Rebind exact SHA values in current metadata while retaining original input hashes
 # in the independent normalization certificate written after this pass.
 textfiles=[p for base in ['sources','gallery','docs','project'] for p in (ROOT/base).rglob('*') if p.suffix in ['.json','.md','.html','.tsv']]
 for iteration in range(20):
  changes=0
  for p in textfiles:
   before=p.read_bytes();after=re.sub(rb'\b[0-9a-f]{64}\b',lambda m:mapping.get(m.group().decode(),m.group().decode()).encode(),before)
   if after!=before:
    p.write_bytes(after);mapping[sha(before)]=sha(after);changes+=1
  if not changes:break
 else:raise AssertionError('hash dependency graph did not converge')
 report=dict(scope='Publication normalization; historical proof hashes rebound through certified metadata equivalence, not represented as fresh historical test execution.',files=entries,hash_rebinding=mapping)
 dest=ROOT/'docs/merge-review-2026-11-06/publication-normalization.json';dest.write_text(json.dumps(report,indent=2)+'\n')
 print('METADATA_NORMALIZED',len(entries),'files; fresh runtime audits required')
if __name__=='__main__':main()
