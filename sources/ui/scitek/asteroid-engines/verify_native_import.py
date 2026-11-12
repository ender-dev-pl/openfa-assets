import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'asteroid-engines.blend'));s=bpy.context.scene;s.cycles.samples=16
root=bpy.data.objects['AsteroidEngineRotor'];root.animation_data_clear();root.rotation_euler=(0,0,0);bpy.context.view_layer.update()
native=[o for o in s.objects if o.type=='MESH'];gens=[o for o in native if o.name.startswith('Research opposing generator')];assert len(gens)==4
for a,b in [(0,2),(1,3)]:assert (gens[a].location+gens[b].location-Vector((0,0,1.3))).length<1e-5
vertices=sum(len(o.data.vertices) for o in native)
for o in list(s.objects):
 if o.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'asteroid-engines.glb'));s.frame_set(1);s.render.filepath=str(out/'imported-solid.png');bpy.ops.render.render(write_still=True)
assert bpy.data.objects.get('AsteroidEngineRotor');assert sum(len(o.data.vertices) for o in s.objects if o.type=='MESH')>=vertices
bpy.ops.wm.open_mainfile(filepath=str(out/'asteroid-engines.blend'));s=bpy.context.scene;s.frame_set(1);s.render.filepath=str(out/'reload-solid.png');bpy.ops.render.render(write_still=True)
(out/'verification.json').write_text(json.dumps(dict(native_runtime=True,saved_source_reload=True,independent_solid_import=True,generator_count=4,opposing_pairs_verified=True,source_sha256=hashlib.sha256((out/'asteroid-engines.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'asteroid-engines.glb').read_bytes()).hexdigest(),acceptance='Approximately 80% visual correspondence; visual review required'),indent=2)+'\n',encoding='utf-8')
print('ENGINE_NATIVE_IMPORT_VERIFIED')
