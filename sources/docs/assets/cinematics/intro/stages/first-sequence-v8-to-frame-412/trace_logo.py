"""Recover editable outline geometry from the supplied legacy end-card, not an image plane."""
from pathlib import Path
from collections import defaultdict
import json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,binary_closing
p=Path(__file__).resolve().parent;ref=p.parent.parent/'reference/intro-gdv-remaster/continuation-to-412/frames/frame-000400.png';a=np.array(Image.open(ref).convert('RGB')).astype(float)
m=(a[:,:,0]>45)&(a[:,:,0]>a[:,:,1]*1.45)&(a[:,:,1]>a[:,:,2]*1.15);m[:50]=False;m[275:]=False;m[:,:85]=False;m[:,225:]=False;m=gaussian_filter(m.astype(float),.45)>.22;m=binary_closing(m,iterations=1)
edges=defaultdict(list)
for y,x in zip(*np.where(m)):
 for dy,dx,start,end in [(-1,0,(x,y),(x+1,y)),(0,1,(x+1,y),(x+1,y+1)),(1,0,(x+1,y+1),(x,y+1)),(0,-1,(x,y+1),(x,y))]:
  if not m[y+dy,x+dx]:edges[start].append(end)
loops=[]
while edges:
 start=next(iter(edges));cur=start;loop=[]
 for _ in range(20000):
  loop.append(cur);nxt=edges[cur].pop()
  if not edges[cur]:del edges[cur]
  cur=nxt
  if cur==start:break
  if cur not in edges:break
 if len(loop)>8:loops.append(loop)
y,x=np.where(m);bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
# Keep the native line shape and correct its display Y aspect before making 3D curves.
(p/'tetra-outline.json').write_text(json.dumps(dict(provenance='Vector boundary trace of orange outlines in original frame 400; no legacy raster embedded in the rendered scene.',source_frame=400,bbox=bbox,vertical_scale=262/560,loops=[[[int(x),int(y)] for x,y in loop] for loop in loops]),separators=(',',':'))+'\n');Image.fromarray((m*255).astype('uint8')).save(p/'logo-trace-mask.png');print('Logo bbox',bbox,'loops',len(loops),'vertices',sum(map(len,loops)))
