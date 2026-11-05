"""Regenerate diagram curves from evaluated physical edges; preserve the solid."""
import bpy,bmesh,json,sys,shutil,math,bisect
from mathutils import Vector
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];src,out=map(lambda p:Path(p).resolve(),args);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src/'nuclear-missile.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['NuclearResearchRoot'];model=json.loads((src/'model.json').read_text());deps=bpy.context.evaluated_depsgraph_get();inverse=root.matrix_world.inverted();counts={}
for role,names in model['components'].items():
 ob=bpy.data.objects[role+' technical wire'];old=ob.data;curve=bpy.data.curves.new(role+' evaluated solid-edge diagram','CURVE');curve.dimensions='3D';curve.bevel_depth=.003;curve.bevel_resolution=0
 for mat in old.materials:curve.materials.append(mat)
 for name in names+(['Nuclear tapered dark pressure casing'] if role=='atomic-warhead-nose' else []):
  if 'wear seam' in name or 'trefoil' in name:continue
  physical=bpy.data.objects[name];ev=physical.evaluated_get(deps);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update()
  shaped=any(token in name for token in ['red tail pod','upper silver side form','Research rear manoeuvring'])
  if shaped:
   rows={}
   for v in bm.verts:rows.setdefault(round(v.co.z,5),[]).append(v.co)
   heights=sorted(rows);centres={z:sum(rows[z],Vector())/len(rows[z]) for z in heights}
   def nearest_height(value):
    i=bisect.bisect_left(heights,value);options=[j for j in [i-1,i] if 0<=j<len(heights)]
    return min(options,key=lambda j:abs(heights[j]-value))
   rings={nearest_height(heights[0]+(heights[-1]-heights[0])*(i+1)/13) for i in range(12)}
  for edge in bm.edges:
   if edge.calc_length()<1e-5:continue
   if shaped:
    p,q=[v.co for v in edge.verts]
    if abs(p.z-q.z)<1e-5:
     row=nearest_height(p.z)
     if row not in rings:continue
    else:
     if edge.calc_length()<.015:continue
     z=heights[nearest_height(p.z)];centre=centres[z]
     if round(math.atan2(p.y-centre.y,p.x-centre.x)/math.tau*256)%16:continue
   elif len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[inverse@physical.matrix_world@v.co for v in edge.verts]
   if name=='Nuclear tapered dark pressure casing':
    target='atomic-warhead-nose' if (a.z+b.z)/2>=4.70 else 'chassis'
    if role!=target:continue
   sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
  bm.free();ev.to_mesh_clear()
 ob.data=curve;bpy.data.curves.remove(old);counts[role]=len(curve.splines)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'nuclear-missile.blend'));shutil.copy2(src/'nuclear-missile.glb',out/'nuclear-missile.glb');model['diagram_edge_sources']={role:names+(['Nuclear tapered dark pressure casing'] if role=='atomic-warhead-nose' else []) for role,names in model['components'].items()};model['wire_geometry_contract']='Actual evaluated physical edges, continuous casing upper neck assigned to nose without duplicating solid';model['diagram_sampling']='Swept forms: twelve height-spaced actual rings and selected longitudinal edges >=0.015; decorative trefoil omitted; no synthetic contour geometry.';(out/'model.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');shutil.copy2(src/'material-clock.json',out/'material-clock.json')
(out/'wire-rebuild.json').write_text(json.dumps(dict(components=counts,solid_glb_unchanged=True,reason='Previous raw pre-modifier wire edges failed evaluated-solid correspondence.'),indent=2)+'\n',encoding='utf-8');print('NUCLEAR_EVALUATED_WIRES_READY',sum(counts.values()))
