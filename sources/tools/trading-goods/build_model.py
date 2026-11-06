"""Author one coloured trade model and static GLB; technical previews are not final item images."""
import bpy,sys,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import modelling as M
from recipes import BUILDERS
ap=argparse.ArgumentParser();ap.add_argument('--item',type=int,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--inherited-native',type=Path);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);assert a.item in BUILDERS;ident=f'TI{a.item:03d}';a.out.mkdir(parents=True,exist_ok=True);M.begin(ident);M.INHERITED_NATIVE=a.inherited_native;BUILDERS[a.item](a.item);bpy.context.view_layer.update();M.setup_camera();bpy.context.view_layer.update();s=bpy.context.scene;s.render.filepath='//inspection/';bpy.ops.wm.save_as_mainfile(filepath=str(a.out/(ident+'.blend')))
for o in list(s.objects):
 if o.type in ['FONT','CURVE']:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=str(a.out/(ident+'.glb')),export_format='GLB',export_animations=False,export_apply=True,export_cameras=False,export_lights=False)
if s.get('inherited_native_sha256'):(a.out/'inheritance.json').write_text(json.dumps({k:s[k] for k in ['inherited_native_sha256','inherited_source','inherited_local_geometry_hash','geometry_preserved_during_reuse','view_change']},indent=2)+'\n')
print('MODEL_BUILT',ident)
