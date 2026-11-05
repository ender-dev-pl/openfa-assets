import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parent
base=p.parent/'first-scene-v3-nebula/opening-reconstruction-nebula.blend'
target=p/'opening-reconstruction-ship-fit.blend'
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(1)
 root=next(o for o in s.objects if o.name.startswith('SHIP —'))
 local={o.name:[list(row) for row in o.matrix_basis] for o in s.objects if o.parent==root}
 poses={}
 for f in [1,73,121,145,161,177,192]:
  s.frame_set(f);poses[f]={o.name:[list(row) for row in o.matrix_world] for o in s.objects if o.animation_data and o!=root and o.parent!=root}
 return dict(local=local,poses=poses,meshes=len(local),fps=s.render.fps,frames=s.frame_end,images=[i.name for i in bpy.data.images if i.source=='FILE'])
a=capture(base);b=capture(target)
assert a['local']==b['local'],'Ship geometry transforms changed'
assert a['poses']==b['poses'],'Background animation changed'
assert b['fps']==24 and b['frames']==192
report=dict(unchanged_ship_part_local_transforms=b['meshes'],background_animation_unchanged=True,fps=b['fps'],frames=b['frames'],external_file_images=b['images'])
(p/'scene-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
