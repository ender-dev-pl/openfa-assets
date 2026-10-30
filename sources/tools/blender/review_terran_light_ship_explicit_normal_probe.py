from pathlib import Path
import json,hashlib
from PIL import Image,ImageChops,ImageStat,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for slug in ['combat-eagle','scoutship']:
  base=ROOT/'docs/assets/reconstruction/evidence/terran-light-ship-runtime'/slug
  folder=ROOT/'docs/assets/reconstruction/evidence/terran-light-ship-explicit-normals'/slug
  probe=json.loads((folder/'probe.json').read_text());baseline=json.loads((base/'runtime-audit.json').read_text());assert sha(base/'runtime-audit.json')==probe['baseline_sha256']
  results={};sheet=Image.new('RGB',(1536,1080),(20,25,34));draw=ImageDraw.Draw(sheet)
  for row,view in enumerate(['front-quarter','rear-quarter']):
   paths=[base/('imported-'+view+'.png'),base/('native-'+view+'.png'),folder/('explicit-native-'+view+'.png')];images=[]
   for col,path in enumerate(paths):
    hashes=probe['render_sha256'] if col==2 else baseline['render_sha256'];assert sha(path)==hashes[path.name]
    im=Image.open(path).convert('RGBA');images.append(im);im=im.resize((512,512));sheet.paste(im,(col*512,row*540+25),im);draw.text((col*512+8,row*540+5),['unchanged GLB target','native baseline','native explicit normals probe'][col],fill='white')
   values={}
   for label,im in zip(['baseline','probe'],images[1:]):
    d=ImageChops.difference(images[0],im);values[label]=dict(mean_rgba=ImageStat.Stat(d,images[0].getchannel('A')).mean,alpha_changed=sum(v!=0 for v in d.getchannel('A').tobytes()))
   results[view]=values
  sheet.save(folder/'comparison.png');report=dict(issue=1102,reviewer_sha256=sha(Path(__file__)),probe_sha256=sha(folder/'probe.json'),comparisons=results,final_visual_acceptance=False);(folder/'pixel-review.json').write_text(json.dumps(report,indent=2)+'\n');print(slug,json.dumps(results))
if __name__=='__main__':main()
