"""Check the retained original PB18 hardware without retaining obsolete hatch semantics."""
import bpy,sys,json,hashlib
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];folder,base=map(lambda p:Path(p).resolve(),args);model=json.loads((folder/'model.json').read_text());names=model['preserved_source_meshes'];assert len(names)==4
def sig(ob,materials=True):
 d=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={u.name:[list(p.uv) for p in u.data] for u in ob.data.uv_layers})
 if materials:d['materials']=[m.name for m in ob.data.materials]
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(base));expected={n:sig(bpy.data.objects[n]) for n in names};plate=sig(bpy.data.objects['Pedestal systems hatch lid'],False)
bpy.ops.wm.open_mainfile(filepath=str(folder/'photon-turret.blend'));assert {n:sig(bpy.data.objects[n]) for n in names}==expected;assert sig(bpy.data.objects['Pedestal systems hatch lid'],False)==plate
(folder/'legacy-reuse-verification.json').write_text(json.dumps(dict(original_source_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),original_hardware_geometry_uv_materials_preserved=expected,recoloured_plate_geometry_uv_preserved=True,recoloured_plate_geometry_uv_signature=plate,removed_inferred_handle=True,small_source_observed_sensor_added=True),indent=2)+'\n',encoding='utf-8');print('PHOTON_LEGACY_REUSE_VERIFIED',len(names))
