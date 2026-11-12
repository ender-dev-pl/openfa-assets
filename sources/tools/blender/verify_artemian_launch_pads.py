"""Verify saved AR09 and independent GLB import, including real review renders."""
import hashlib,json,math,struct,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_png

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(expected=0,lift=0):
    result={};deps=bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();points=[obj.matrix_world@v.co for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons]
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.free()
        assert obj.data.uv_layers.active and all(math.isfinite(v) for p in points for v in p)
        result[obj.name]=dict(points=points,tree=BVHTree.FromPolygons(points,faces),triangles=len(mesh.loop_triangles),matrix=[float(v) for row in obj.matrix_world for v in row],materials=sorted(m.name for m in obj.data.materials if m));evaluated.to_mesh_clear()
    required=['Launch Pads low green landing shell','Launch Pads brass crosspiece']+['Launch Pads '+label+' '+str(i) for i in range(2) for label in ['copper base sleeve','tall brass rail','copper front inset','copper inset clear rim']]+['Launch Pads copper coupling '+str(i)+' '+str(j) for i in range(2) for j in range(2)]+['Launch Pads recessed grey baffle '+str(i)+' '+str(side) for i in range(4) for side in ([-1] if i==0 else [-1,1])]
    required += ['Launch Pads hinged roof '+str(side) for side in [-1,1]]+['Launch Pads dark underground shaft','Launch Pads black shaft floor']
    required += ['Launch Pads lifting hinge axle '+str(side) for side in [-1,1]]
    required += ['Launch Pads '+kind+' '+str(side)+' '+str(i) for side in [-1,1] for i in range(2) for kind in ['lifting bearing','attached hinge lug','fixed lift guide','captive lift rod']]
    assert set(result)==set(required) and len(result)==43
    body=result[required[0]];points=body['points'];width=max(p.x for p in points)-min(p.x for p in points);length=max(p.y for p in points)-min(p.y for p in points)
    assert 1.64<width<1.72 and .98<length/width<1.04,'Source fixed lower shell remains broad and low'
    def inside(tree,p):
        surface,normal,_,distance=tree.find_nearest(p);return surface is not None and normal.dot(p-surface)<-1e-5
    openness=abs(bpy.data.objects['HangarDoorPort'].rotation_euler.y)/math.radians(110)
    # Imported animation can use quaternions: derive physical opening from
    # world basis, rather than trusting Blender Euler representation.
    pivot=bpy.data.objects['HangarDoorPort'];basis=(Matrix.Rotation(math.radians(35),4,'Z')@pivot.matrix_world).to_3x3();angle=math.atan2(-basis[2][0],basis[0][0]);openness=abs(angle)/math.radians(110)
    assert abs(openness-expected)<2e-5,(openness,expected)
    if expected<1e-6 and lift<1e-6:
        closed=[body]+[result['Launch Pads hinged roof '+str(side)] for side in [-1,1]]
        height=max(p.z for obj in closed for p in obj['points'])-min(p.z for p in body['points']);assert .32<height/width<.36
        roof=result['Launch Pads hinged roof -1'];floor=roof['tree'].ray_cast(Vector((.08,.20,2)),Vector((0,0,-1)))[0];rim=result['Launch Pads hinged roof 1']['tree'].ray_cast(Vector((.35,.20,2)),Vector((0,0,-1)))[0]
        assert floor and rim and .30<floor.z<.32 and rim.z-floor.z>.17
        assert not inside(roof['tree'],Vector((.08,.20,.45))) and inside(roof['tree'],Vector((.08,.20,.30)))
        for i,offset in enumerate([-.15,-.05,.05,.15]):
            leaf=result['Launch Pads hinged roof '+str(-1 if .08+offset<.20 else 1)];baffle=result['Launch Pads recessed grey baffle '+str(i)+' '+str(-1 if .08+offset<.20 else 1)];sample=Vector((.08+offset,.20,.30));assert inside(leaf['tree'],sample) and inside(baffle['tree'],sample),'Source baffles move with actual supporting roof'
        for x in [-.55,-.35,-.12,.12,.35,.55]:
            assert any(obj['tree'].ray_cast(Vector((x,0,2)),Vector((0,0,-1)))[0] is not None for obj in closed),'Closed roof covers large flight opening'
    for side in [-1,1]:
        pivot=bpy.data.objects['HangarDoorPort' if side<0 else 'HangarDoorStarboard'];assert (pivot.matrix_world.translation-Matrix.Rotation(-math.radians(35),4,'Z')@Vector((side*.815,0,.17+lift))).length<1e-5
        for i,y in enumerate([-.18,.18]):
            sample=Matrix.Rotation(-math.radians(35),4,'Z')@Vector((side*.81,y,.10));assert inside(body['tree'],sample) and inside(result['Launch Pads fixed lift guide '+str(side)+' '+str(i)]['tree'],sample),'Guide bases physically meet fixed shell'
            guide=result['Launch Pads fixed lift guide '+str(side)+' '+str(i)];rod=result['Launch Pads captive lift rod '+str(side)+' '+str(i)];sample=Matrix.Rotation(-math.radians(35),4,'Z')@Vector((side*.824,y,.13+lift));assert inside(guide['tree'],sample) and inside(rod['tree'],sample),'Captive lift rods stay inside real guide cylinders'
        assert not body['tree'].overlap(result['Launch Pads hinged roof '+str(side)]['tree']),'Moving roof never crosses fixed body shell'
        for name,fitting in result.items():
            if name.startswith('Launch Pads copper ') or name.startswith('Launch Pads brass ') or name.startswith('Launch Pads tall brass '):assert not fitting['tree'].overlap(result['Launch Pads hinged roof '+str(side)]['tree']),('Roof must avoid fixed source fittings',name,expected,lift)
        for i,y in enumerate([-.19,.19]):
            sample=pivot.matrix_world@Vector((side*-.041,y,.035));assert inside(result['Launch Pads attached hinge lug '+str(side)+' '+str(i)]['tree'],sample),'Moving lug remains attached to pivot'
    # All actual shaft wall surfaces surround the flight corridor; floor is
    # separate and stays below it. No concrete plug occupies the passage.
    shaft=result['Launch Pads dark underground shaft'];assert min(p.z for p in shaft['points'])< -1.49
    assert max(p.z for p in result['Launch Pads black shaft floor']['points'])< -1.49
    anchors=[]
    for i,(x,top) in enumerate([(-.60,1.18),(-.36,1.10)]):
        sleeve=result['Launch Pads copper base sleeve '+str(i)];rail=result['Launch Pads tall brass rail '+str(i)];pts=sleeve['points'];cy=(min(p.y for p in pts)+max(p.y for p in pts))/2;sample=Vector((x,cy+.04,.12));assert inside(body['tree'],sample) and inside(sleeve['tree'],sample),'Both sleeve bases meet real shell';sample=Vector((x,cy,.20));assert inside(sleeve['tree'],sample) and inside(rail['tree'],sample),'Brass rails rooted inside copper sleeves';assert abs(max(p.z for p in rail['points'])-top)<1e-5;anchors.append(Vector((x,cy,.82)))
        for j,z in enumerate([.255,.315]):
            sample=Vector((x,cy,z));assert inside(rail['tree'],sample) and inside(result['Launch Pads copper coupling '+str(i)+' '+str(j)]['tree'],sample),'All four coupling rings intersect actual rails'
    for i,sample in enumerate(anchors):assert inside(result['Launch Pads tall brass rail '+str(i)]['tree'],sample) and inside(result['Launch Pads brass crosspiece']['tree'],sample),'Crosspiece joins both actual rails'
    centres=[]
    for i in range(2):
        disc=result['Launch Pads copper front inset '+str(i)];centre=sum(disc['points'],Vector())/len(disc['points']);centres.append(centre);assert centre.x>-.11 and centre.y<-.65 and body['tree'].find_nearest(centre)[3]<.025;nearest,normal,_,_=body['tree'].find_nearest(centre);sample=nearest-normal*.003;assert inside(body['tree'],sample) and inside(disc['tree'],sample);assert not inside(result['Launch Pads copper inset clear rim '+str(i)]['tree'],centre),'Two front inset centres unmasked'
    assert centres[1].x-centres[0].x>.28
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/115';assert list(root['footprint'])==[2,2]
    assert all(o.parent==root or o.parent.name in ['HangarDoorPort','HangarDoorStarboard','HangarLiftPort','HangarLiftStarboard'] for o in bpy.context.scene.objects if o.type=='MESH')
    assert bool(root['preserve_ground_origin']) and root['ground_level']==0
    reachable={node.image for obj in bpy.context.scene.objects if obj.type=='MESH' for mat in obj.data.materials if mat and mat.use_nodes for node in mat.node_tree.nodes if node.type=='TEX_IMAGE' and node.image}
    images={i.name:dict(size=list(i.size),pixels=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in i.pixels)).hexdigest()) for i in reachable if i.users and i.size[0] and i.source!='VIEWER'}
    return result,images,[float(v) for row in root.matrix_world for v in row]

def clearance_geometry(opened,meta,closed):
    def segment(a,b):
        d=b-a;t=max(0,min(1,-a.dot(d)/max(d.length_squared,1e-20)));return (a+t*d).length
    def radial(a,b,c):
        aa=Vector((a.x,a.y));bb=Vector((b.x,b.y));cc=Vector((c.x,c.y));cross=lambda u,v:u.x*v.y-u.y*v.x
        signs=[cross(bb-aa,-aa),cross(cc-bb,-bb),cross(aa-cc,-cc)]
        if all(v>=-1e-10 for v in signs) or all(v<=1e-10 for v in signs):
            if abs(cross(bb-aa,cc-aa))>1e-12:return 0.
        return min(segment(aa,bb),segment(bb,cc),segment(cc,aa))
    minimum=10.;limiter=None
    for name,obj in opened.items():
        mesh=bpy.data.objects[name].data;points=obj['points'];mesh.calc_loop_triangles()
        for triangle in mesh.loop_triangles:
            a,b,c=[points[i] for i in triangle.vertices]
            if max(a.z,b.z,c.z)< -1.25:continue
            distance=radial(a,b,c)
            if distance<minimum:minimum=distance;limiter=name
    assert minimum>.69,(minimum,limiter)
    root=bpy.context.scene;rows=[]
    fixed=[p for obj in closed.values() for p in obj['points']];span=max(max(p[a] for p in fixed)-min(p[a] for p in fixed) for a in [0,1]);building_scale=64/span
    for rel,world,source in [('terran/assault-fighter',30,'current game package'),('terran/combat-eagle',32,'current game package'),('terran/scoutship',28,'current game package'),('artemian/all-purpose-assault',48,'asset proposal; client fallback96 does not fit and must not be claimed accepted')]:
        path=ROOT/'sources/objects'/rel/'model.glb';before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=[o for o in bpy.data.objects if o not in before];bpy.context.view_layer.update()
        points=[o.matrix_world@v.co for o in new if o.type=='MESH' for v in o.data.vertices];lo=Vector([min(p[a] for p in points) for a in range(3)]);hi=Vector([max(p[a] for p in points) for a in range(3)]);centre=(lo+hi)/2;scale=world/max(hi-lo)/building_scale
        radius=max(math.hypot(p.x-centre.x,p.y-centre.y)*scale for p in points);margin=minimum-radius;assert margin>.035,(rel,margin)
        for heading in range(256):
            angle=heading*math.tau/256;co=math.cos(angle);si=math.sin(angle)
            # Extremal actual vertex determines a rotation-invariant bound;
            # a sampled heading calculation independently checks the transform.
            q=max(points,key=lambda p:math.hypot(p.x-centre.x,p.y-centre.y));x=(q.x-centre.x)*scale;y=(q.y-centre.y)*scale
            assert math.hypot(x*co-y*si,x*si+y*co)<minimum-.035
        rows.append(dict(model=path.relative_to(ROOT).as_posix(),sha256=sha(path),world_size=world,scale_source=source,maximum_horizontal_radius_local=radius,minimum_radial_margin_local=margin,minimum_radial_margin_world_units=margin*building_scale,headings=256))
        for obj in new:bpy.data.objects.remove(obj,do_unlink=True)
    return dict(aperture_radius_authored=.78,minimum_actual_surface_radius=minimum,limiting_mesh=limiter,ground_cell_world_units=32,closed_bind_horizontal_span=span,building_scale_world_per_local=building_scale,vertical_corridor=[-1.25,2.0],ships=rows,game_client_accepted=False)


def setup():
    # Each view set receives exactly the same studio. Repeated calls must not
    # accumulate the previous open-pose lights in the closed-pose comparison.
    for obj in list(bpy.context.scene.objects):
        if obj.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.film_transparent=True;s.world=bpy.data.worlds.new('Review studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO'
    for loc,power,size in [((4,-6,8),950,5),((-4,-2,5),700,4),((2,5,7),1100,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.3))-o.location).to_track_quat('-Z','Y').to_euler()
    return s

def review_ground(holdout=False):
    vertices=[];faces=[];n=128
    for radius in [.78,8]:
        for i in range(n):a=i*math.tau/n;vertices.append((radius*math.cos(a),radius*math.sin(a),0))
    for i in range(n):faces.append((i,(i+1)%n,n+(i+1)%n,n+i))
    mesh=bpy.data.meshes.new('Non-exported review ground with exact shaft opening');mesh.from_pydata(vertices,[],faces);o=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(o);m=bpy.data.materials.new('Review ground');m.diffuse_color=(.025,.03,.035,1);o.data.materials.append(m)
    if holdout:
        m.use_nodes=True;m.node_tree.nodes.clear();out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');mask=m.node_tree.nodes.new('ShaderNodeHoldout');m.node_tree.links.new(mask.outputs[0],out.inputs['Surface'])
    return o

def render(label,media):
    s=setup();meshes=[o for o in s.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes if 'underground' not in o.name and 'shaft floor' not in o.name for v in o.bound_box];centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);renders={}
    ground=review_ground(True)
    for view,direction in [('front-quarter',(4,-14,10)),('front',(0,-16,9)),('rear-quarter',(7,12,9))]:
        v=Vector(direction).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];midpoint=Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0));s.camera.location+=s.camera.rotation_euler.to_matrix()@midpoint;s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;p=media/f'{label}-{view}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));renders[p.name]=sha(p)
    bpy.data.objects.remove(ground,do_unlink=True)
    return renders

def main():
    folder=ROOT/'sources/objects/artemian/launch-pads';media=ROOT/'gallery/media/objects/artemian/launch-pads';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_artemian_launch_pads.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_artemian_launch_pads.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/ar09-concept-review.json'
    assert json.loads((ROOT/meta['concept_review']).read_bytes())['id']==meta['id']
    for ext,h in meta['binaries'].items():assert sha(folder/f'model.{ext}')==h
    poses=[(1,0,0),(5,0,.17),(9,0,.34),(13,.25,.34),(17,.5,.34),(21,.75,.34),(25,1,.34),(49,1,.34),(73,1,.34),(77,.75,.34),(81,.5,.34),(85,.25,.34),(89,0,.34),(93,0,.17),(97,0,0)]
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False);native_samples=[]
    for frame,openness,lift in poses:
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();sample,images,root=snapshot(openness,lift);native_samples.append(sample)
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();native,ni,nr=snapshot();renders=render('native',media)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'));bpy.context.scene.render.fps=24;error=0
    for index,(frame,openness,lift) in enumerate(poses):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();sample,images,root=snapshot(openness,lift);previous=native_samples[index]
        for name,n in previous.items():
            other=sample[name];assert n['triangles']==other['triangles'] and n['materials']==other['materials'];assert max(abs(a-b) for a,b in zip(n['matrix'],other['matrix']))<1e-5
            error=max(error,max(other['tree'].find_nearest(p)[3] for p in n['points']),max(n['tree'].find_nearest(p)[3] for p in other['points']))
    bpy.context.scene.frame_set(49);bpy.context.view_layer.update();opened,_,_=snapshot(1,.34);clearance=clearance_geometry(opened,meta,native_samples[0])
    renders.update(render('imported-open',media))
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();imported,ii,ir=snapshot();assert nr==ir
    assert sorted((v['size'],v['pixels']) for v in ni.values())==sorted((v['size'],v['pixels']) for v in ii.values())
    assert error<1e-5;raw=(folder/'model.glb').read_bytes();gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values());assert tri<30000;assert [clip['name'] for clip in gltf['animations']]==['HangarExitCycle'];assert len(gltf['materials'])==5;assert all('bufferView' in i for i in gltf['images']);renders.update(render('imported',media))
    s=bpy.context.scene
    for label,centre,scale in [('brass-frame-and-copper-fittings-detail',Vector((-.30,-.58,.61)),1.7),('recessed-well-and-four-baffles-detail',Vector((.08,.20,.46)),.95)]:
        direction=Vector((4,-16,10)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    s=bpy.context.scene
    wire=bpy.data.materials.new('Technical diagram from canonical geometry');wire.use_nodes=True
    node=wire.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.04,.3,.07,1)
    node.inputs['Emission Color'].default_value=(.04,.3,.07,1);node.inputs['Emission Strength'].default_value=.4
    # Render the actual canonical edge coordinates as thin curves. Wireframe
    # face offset on very slender Boolean triangles can create miter spikes.
    points=[obj.matrix_world@Vector(v) for obj in s.objects if obj.type=='MESH' for v in obj.bound_box]
    centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)])
    curve=bpy.data.curves.new('Exact canonical edge coordinates','CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=.0014;curve.bevel_resolution=0
    for obj in list(s.objects):
        if obj.type!='MESH':continue
        for edge in obj.data.edges:
            line=curve.splines.new('POLY');line.points.add(1)
            for point,index in zip(line.points,edge.vertices):point.co=(*(obj.matrix_world@obj.data.vertices[index].co),1)
        obj.hide_render=True
    edge_object=bpy.data.objects.new('Technical edges from actual canonical mesh',curve);s.collection.objects.link(edge_object);curve.materials.append(wire)
    direction=Vector((4,-14,10)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    s.camera.data.ortho_scale=3.3;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=260,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=['HangarExitCycle'],animation_samples=len(poses),clearance=clearance,renders=renders,scope='Actual saved native/imported GLB11door poses,closed positive surfaces,fixed fittings,moving attached source-shaped roof,texture pixels and renders. Full-open geometric cylindrical corridor is checked against independent canonical ship vertices at256headings using explicit game/proposed scales. Asset-only scale contract;no client/state/FPS acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('AR09_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
