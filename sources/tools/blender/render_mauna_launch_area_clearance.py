import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[3];M=R/'gallery/media/objects/mauna/launch-area';P=M
sys.path.insert(0,str(R/'sources/tools/blender'));from verify_mauna_launch_area import setup,review_ground
sys.path.insert(0,str(R/'tools'));from publication_support import clean_png
rows=[]
for rel,world,yaw in [('mauna/surveillance-craft-type-5',40,0),('mauna/combat-craft-type-1-5',56,45),('terran/assault-fighter',30,0),('terran/combat-eagle',32,0),('terran/scoutship',28,0)]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'sources/objects/mauna/launch-area/model.glb'));bpy.context.scene.render.fps=24;bpy.context.scene.frame_set(49);bpy.context.view_layer.update();pad=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.context.scene.frame_set(1);bpy.context.view_layer.update();pts=[o.matrix_world@v.co for o in pad for v in o.data.vertices];span=max(max(p[a] for p in pts)-min(p[a] for p in pts) for a in [0,1]);bpy.context.scene.frame_set(49)
 before=set(bpy.data.objects);path=R/'sources/objects'/rel/'model.glb';bpy.ops.import_scene.gltf(filepath=str(path));new=[o for o in bpy.data.objects if o not in before]
 # Freeze ship at its completed stage; the pad alone retains an operating clip.
 end=max([97]+[strip.frame_end for o in new if o.animation_data for track in o.animation_data.nla_tracks for strip in track.strips]);bpy.context.scene.frame_set(int(end));bpy.context.view_layer.update();basis={o:o.matrix_basis.copy() for o in new}
 for o in new:
  if o.animation_data:o.animation_data_clear()
  o.matrix_basis=basis[o]
 bpy.context.scene.frame_set(49);bpy.context.view_layer.update();pts=[o.matrix_world@v.co for o in new if o.type=='MESH' for v in o.data.vertices];lo=Vector([min(p[a] for p in pts) for a in range(3)]);hi=Vector([max(p[a] for p in pts) for a in range(3)]);centre=(lo+hi)/2;scale=world/max(hi-lo)/(64/span)
 roots=[o for o in new if o.parent not in new];placement=Matrix.Translation((0,0,.40))@Matrix.Rotation(math.radians(yaw),4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-centre)
 for o in roots:o.matrix_world=placement@o.matrix_world
 scene=setup();scene.cycles.samples=32;review_ground(True);target=Vector((0,0,.70));direction=Vector((5,-12,16)).normalized();scene.camera.location=target+direction*15;scene.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=2.9;scene.render.filepath=str(M/('clearance-'+rel.split('/')[-1]+'.png'));bpy.ops.render.render(write_still=True);rendered=Path(scene.render.filepath);rendered.write_bytes(clean_png(rendered.read_bytes()))
 rows.append(dict(model=path.relative_to(R).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),world_size=world,yaw_degrees=yaw,scale_source="Asset proposal;not installed game scale" if rel.startswith("mauna/") else "Supplementary Terran package scale",same_culture_authoritative=rel.startswith("mauna/"),scale=scale,preview=Path(scene.render.filepath).relative_to(R).as_posix(),meaning='Actual ship at its complete stage and explicit uniform renderer-equivalent scale. Centre Z.40 shows maximum planform at open mouth; not a client screenshot.'))
(P/'clearance-renders.json').write_text(json.dumps(rows,indent=2)+'\n');print('MN09_ACTUAL_SHIP_CLEARANCE_RENDERS',len(rows))
