"""Independent rigid-node animation checks, including the welding burst."""
import bpy,sys,json,hashlib,struct
from pathlib import Path
source=Path(sys.argv[sys.argv.index('--')+1]).resolve();out=Path(sys.argv[sys.argv.index('--')+2]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.render.resolution_x=288;s.render.resolution_y=320;s.cycles.samples=8;s.render.film_transparent=True
samples=[1,25,49,61,73,97,120];pivots=['HeavyGripPivot','LightArmPivot','WelderHeadPivot'];native={};roof=bpy.data.objects['Segmented umbrella canopy'];baseline=roof.matrix_world.copy()
def matrix_values(m):return [v for row in m for v in row]
def spark_radius():
 ob=bpy.data.objects['Welding spark 00'];points=[ob.matrix_world@v.co for v in ob.data.vertices];centre=sum(points,points[0]*0)/len(points);return max((p-centre).length for p in points)
def active_sparks():return sum(bpy.data.objects[f'Welding spark {i:02}'].matrix_world.translation.z<.70 and bpy.data.objects[f'Welding spark {i:02}'].scale.x>.01 for i in range(32))
def arc_visible():
 ob=bpy.data.objects['Spot welding arc'];return ob.matrix_world.translation.y<-.5 and ob.scale.x>.01
for f in samples:
 s.frame_set(f);bpy.context.view_layer.update();assert max(abs(a-b) for a,b in zip(matrix_values(roof.matrix_world),matrix_values(baseline)))<1e-5
 native[str(f)]={n:matrix_values(bpy.data.objects[n].matrix_world) for n in pivots};native[str(f)]['active_sparks']=active_sparks();native[str(f)]['arc_visible']=arc_visible();native[str(f)]['spark_radius']=spark_radius();s.render.filepath=str(out/f'native-{f:03}.png');bpy.ops.render.render(write_still=True)
s.frame_set(1);bpy.context.view_layer.update();start={ob.name:matrix_values(ob.matrix_world) for ob in s.objects if ob.type=='MESH'}
s.frame_set(121);bpy.context.view_layer.update();assert max(abs(a-b) for ob in s.objects if ob.name in start for a,b in zip(start[ob.name],matrix_values(ob.matrix_world)))<1e-5,'Preview must close its 120-frame cycle'
for ob in list(s.objects):
 if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(source.with_suffix('.glb')));errors={};s.frame_set(1);bpy.context.view_layer.update();imported_roof=bpy.data.objects['Segmented umbrella canopy'];imported_roof_baseline=matrix_values(imported_roof.matrix_world)
for f in samples:
 s.frame_set(f);bpy.context.view_layer.update();errors[str(f)]={n:max(abs(a-b) for a,b in zip(native[str(f)][n],matrix_values(bpy.data.objects[n].matrix_world))) for n in pivots};assert max(errors[str(f)].values())<1e-4,(f,errors[str(f)])
 assert max(abs(a-b) for a,b in zip(imported_roof_baseline,matrix_values(imported_roof.matrix_world)))<1e-5,'Imported body must remain stationary'
 active=active_sparks();assert active==native[str(f)]['active_sparks'],(f,active);assert arc_visible()==native[str(f)]['arc_visible'],f
 assert abs(spark_radius()-native[str(f)]['spark_radius'])<1e-5,(f,spark_radius(),native[str(f)]['spark_radius'])
 s.render.filepath=str(out/f'imported-{f:03}.png');bpy.ops.render.render(write_still=True)
assert native['1']['active_sparks']==0 and native['61']['active_sparks']>0 and native['120']['active_sparks']==0
assert not native['1']['arc_visible'] and native['61']['arc_visible'] and not native['73']['arc_visible']
raw=source.with_suffix('.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);assert len(doc.get('animations',[]))==1
(out/'inputs.json').write_text(json.dumps(dict(blend_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(raw).hexdigest(),frames=samples,body_turntable=False,canopy_static=True,pivot_matrix_max_errors=errors,spark_counts={f:native[f]['active_sparks'] for f in native},single_merged_animation_clip=True),indent=2)+'\n',newline='\n');print('DROID_ARTICULATION_VERIFIED')
