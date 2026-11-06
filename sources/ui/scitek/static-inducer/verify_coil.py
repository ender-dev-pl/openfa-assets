"""Rounded coil cross-section, through-hole and independent imported anatomy."""
import bpy,sys,json,math,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();base=Path(sys.argv[sys.argv.index('--')+2]).resolve()
def error(vertices):return max(abs(math.hypot(math.hypot(v.x,v.z)-.48,v.y+.43)-.055) for v in vertices)
bpy.ops.wm.open_mainfile(filepath=str(base));old=bpy.data.objects['Static Inducer collar 0'];control_error=error([old.matrix_world@v.co for v in old.data.vertices]);assert control_error>.01
def inspect():
 root=bpy.data.objects['StaticInducerRoot'];ob=bpy.data.objects['Toroidal interference coil'];transform=root.matrix_world.inverted()@ob.matrix_world;mesh=ob.data;vs=[transform@v.co for v in mesh.vertices]
 deviation=error(vs);assert deviation<2e-6,deviation
 tree=BVHTree.FromPolygons(vs,[list(p.vertices) for p in mesh.polygons]);assert tree.ray_cast(Vector((0,-1,0)),Vector((0,1,0)))[0] is None
 hit=tree.ray_cast(Vector((.48,-1,0)),Vector((0,1,0)))[0];assert hit is not None and abs(hit.y+.485)<2e-5
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update();bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert bad==0 and volume>0;bm.free()
 cells=[]
 for i in range(3):
  cell=bpy.data.objects[f'Static Inducer blue terminal {i}'];mapping=root.matrix_world.inverted()@cell.matrix_world;points=[mapping@v.co for v in cell.data.vertices]
  spans=[max(v[k] for v in points)-min(v[k] for v in points) for k in range(3)];ratio=spans[1]/max(spans[0],spans[2]);assert .9<ratio<1.0,(i,spans,ratio);cells.append(dict(axial_span=spans[1],radial_diameter=max(spans[0],spans[2]),axial_radial_ratio=ratio))
 return dict(circular_cross_section_max_error=deviation,central_hole_clear=True,axial_front_surface_y=hit.y,nonmanifold_edges=bad,signed_volume=volume,rounded_power_cells=cells)
bpy.ops.wm.open_mainfile(filepath=str(out/'static-inducer.blend'));bpy.context.scene.frame_set(1);native=inspect()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out/'static-inducer.glb'));bpy.context.scene.render.fps=15;bpy.context.scene.frame_set(1);bpy.context.view_layer.update();imported=inspect()
(out/'coil-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256((out/'static-inducer.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'static-inducer.glb').read_bytes()).hexdigest(),verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),native=native,independent_import=imported,old_flat_collar_negative_control_max_deviation=control_error,rounded_toroidal_coil_verified=True),indent=2)+'\n',encoding='utf-8')
print('STATIC_TOROIDAL_COIL_VERIFIED')
