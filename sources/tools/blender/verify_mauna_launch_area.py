"""Verify saved MN09 and independent GLB import, including real review renders."""
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
    assert len(result)==17
    meta=json.loads((ROOT/'sources/objects/mauna/launch-area/model.json').read_bytes());assert meta['definition_class']==26 and meta['construction_updates']==18
    parts={}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        for group in obj.vertex_groups:
            indices={v.index for v in obj.data.vertices if any(g.group==group.index and g.weight>.5 for g in v.groups)};faces=[tuple(p.vertices) for p in obj.data.polygons if set(p.vertices).issubset(indices)];assert faces
            parts[group.name]=BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],faces)
    def tree(name):return parts[name] if name in parts else result[meta['part_batches'].get(name,name)]['tree']
    def inside(t,p):
        surface,normal,_,_=t.find_nearest(p);return surface is not None and normal.dot(p-surface)<-1e-5
    if parts:
        for name in meta['part_batches']:assert name in parts
    assert len(meta['rectangular_recesses'])==5
    for field in meta['rectangular_recesses']:
        q=Vector(field['point']);n=Vector(field['normal']);floor=tree(field['body']).ray_cast(q+n*.1,-n)[0];assert floor and abs((q-floor).dot(n)-field['depth'])<1e-5,('Blind recess',field['object'])
        witness=q-n*field['contact_depth'];assert inside(tree(field['body']),witness) and inside(tree(field['object']),witness),('Seated field',field['object'])
    for contact in meta['attachment_contacts']:
        q=Vector(contact['point']);assert inside(tree(contact['object']),q) and inside(tree(contact['support']),q),('Attached part',contact['object'],contact['support'])
    body=result['Launch Area sloping concrete shell'];plinth=result['Launch Area cast foot plinth'];shaft=result['Launch Area maroon underground shaft']
    for side in [-1,1]:
        pivot=bpy.data.objects['LaunchDoorNorth' if side>0 else 'LaunchDoorSouth'];basis=pivot.matrix_world.to_3x3();angle=math.atan2(basis[2][1],basis[1][1]);assert abs(angle-side*expected*math.pi/2)<2e-5,('Actual downward rotation',angle,expected)
        assert (pivot.matrix_world.translation-Vector((0,side*.805,.55))).length<1e-5,'Fixed hinge axis'
        for name in ['Launch Area downward door '+str(side),'Launch Area red moving roof band '+str(side)]+['Launch Area moving hinge lug '+str(side)+' '+str(i) for i in range(2)]:
            assert bpy.data.objects[name].parent==pivot
            for fixed in [body,plinth,shaft]:assert not fixed['tree'].overlap(result[name]['tree']),('Leaf/paint/lug must avoid fixed shell',name,expected)
        leaf=tree('Launch Area downward door '+str(side));paint=tree('Launch Area red moving roof band '+str(side));q=pivot.matrix_world@Vector((0,side*(.405-.805),.028));assert inside(leaf,q) and inside(paint,q),'Moving red band seated in leaf'
        for i,x in enumerate([-.53,.53]):
            lug=tree('Launch Area moving hinge lug '+str(side)+' '+str(i));axle=tree('Launch Area hinge axle '+str(side)+' '+str(i));q=pivot.matrix_world@Vector((x,-side*.008,.008));assert inside(lug,q) and inside(axle,q),'Moving lug stays captive on fixed axle'
            q=Vector((x,side*.813,.55));assert inside(axle,q) and inside(tree('Launch Area fixed hinge bearing '+str(side)+' '+str(i)),q),'Axle seated in fixed bearing'
        if expected>.999:
            pts=result['Launch Area downward door '+str(side)]['points'];assert max(p.z for p in pts)<.555 and min(p.z for p in pts)<-.17,'Open door folds below rim into shaft'
    if expected<1e-6:
        for x in [-.60,-.3,0,.3,.60]:
            for y in [-.50,-.25,.25,.50]:assert any(result['Launch Area downward door '+str(side)]['tree'].ray_cast(Vector((x,y,2)),Vector((0,0,-1)))[0] is not None for side in [-1,1]),'Closed roof covers flight opening'
    assert not result['Launch Area downward door -1']['tree'].overlap(result['Launch Area downward door 1']['tree']),'Opposite leaves avoid each other'
    assert max(p.z for p in result['Launch Area black deep shaft floor']['points'])< -1.49
    assert inside(body['tree'],Vector((.86,.86,.08))) and inside(plinth['tree'],Vector((.86,.86,.08))),'Cast shell seated in plinth'
    for chip in meta['physical_chips']:
        q=Vector(chip['point']);n=Vector(chip['normal']);hit=tree(chip['body']).ray_cast(q+n*.1,-n)[0];assert hit and .003<(q-hit).dot(n)<.012,'Measured shallow chip'
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/138' and list(root['footprint'])==[2,2] and root['preserve_ground_origin'] and root['ground_level']==0
    assert all(o.parent==root or o.parent.name in ['LaunchDoorNorth','LaunchDoorSouth'] for o in bpy.context.scene.objects if o.type=='MESH')
    reachable={node.image for obj in bpy.context.scene.objects if obj.type=='MESH' for mat in obj.data.materials if mat and mat.use_nodes for node in mat.node_tree.nodes if node.type=='TEX_IMAGE' and node.image}
    images={i.name:dict(size=list(i.size),pixels=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in i.pixels)).hexdigest()) for i in reachable if bpy.context.scene.frame_current==1 and i.users and i.size[0] and i.source!='VIEWER'}
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
    minimum=10.;square_minimum=10.;limiter=None
    for name,obj in opened.items():
        mesh=bpy.data.objects[name].data;points=obj['points'];mesh.calc_loop_triangles()
        for triangle in mesh.loop_triangles:
            a,b,c=[points[i] for i in triangle.vertices]
            if max(a.z,b.z,c.z)< -1.25:continue
            distance=radial(a,b,c)
            candidates=[]
            for p,q in [(a,b),(b,c),(c,a)]:
                d=q-p;ts=[0.,1.]
                for numerator,denominator in [(-p.x,d.x),(-p.y,d.y),(p.y-p.x,d.x-d.y),(-p.y-p.x,d.x+d.y)]:
                    if abs(denominator)>1e-12:
                        t=numerator/denominator
                        if 0<=t<=1:ts.append(t)
                candidates.extend(max(abs((p+d*t).x),abs((p+d*t).y)) for t in ts)
            square_distance=0. if distance==0 else min(candidates)
            square_minimum=min(square_minimum,square_distance)
            if distance<minimum:minimum=distance;limiter=name
    assert minimum>.69,(minimum,limiter)
    root=bpy.context.scene;rows=[]
    fixed=[p for obj in closed.values() for p in obj['points']];span=max(max(p[a] for p in fixed)-min(p[a] for p in fixed) for a in [0,1]);building_scale=64/span
    fixtures=[('mauna/surveillance-craft-type-5',40,0,True),('mauna/combat-craft-type-1-5',56,45,True),('terran/assault-fighter',30,0,False),('terran/combat-eagle',32,0,False),('terran/scoutship',28,0,False)]
    for rel,world,yaw,own_culture in fixtures:
        path=ROOT/'sources/objects'/rel/'model.glb';before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=[o for o in bpy.data.objects if o not in before];bpy.context.view_layer.update()
        points=[o.matrix_world@v.co for o in new if o.type=='MESH' for v in o.data.vertices];lo=Vector([min(p[a] for p in points) for a in range(3)]);hi=Vector([max(p[a] for p in points) for a in range(3)]);centre=(lo+hi)/2;scale=world/max(hi-lo)/building_scale
        radius=max(math.hypot(p.x-centre.x,p.y-centre.y)*scale for p in points)
        headings=list(range(256)) if yaw==0 else [32]
        extents=[]
        for heading in headings:
            angle=heading*math.tau/256;co=math.cos(angle);si=math.sin(angle)
            extent=max(max(abs((p.x-centre.x)*co-(p.y-centre.y)*si),abs((p.x-centre.x)*si+(p.y-centre.y)*co))*scale for p in points)
            extents.append(extent)
            assert square_minimum-extent>.035,(rel,heading,square_minimum-extent)
        extent=max(extents);margin=square_minimum-extent
        fallback_extent=extent*96/world
        if own_culture:assert fallback_extent>square_minimum,'Unconfigured96 must not be accepted'
        rows.append(dict(model=path.relative_to(ROOT).as_posix(),sha256=sha(path),world_size=world,scale_source='Authored asset proposal;not installed game scale' if own_culture else 'Supplementary Terran package scale',same_culture_authoritative=own_culture,maximum_horizontal_radius_local=radius,maximum_required_square_extent_local=extent,minimum_radial_margin_local=minimum-radius,minimum_square_margin_local=margin,minimum_square_margin_world_units=margin*building_scale,headings=len(headings),required_yaw_degrees=yaw if yaw else None,all_headings=yaw==0,maximum_world_size_with_safety_margin=(square_minimum-.035)*world/extent,unconfigured_game_fallback_world_size=96 if own_culture else None,unconfigured_fallback_fits=fallback_extent<square_minimum-.035 if own_culture else None))
        for obj in new:bpy.data.objects.remove(obj,do_unlink=True)
    return dict(aperture_half_extent_authored=.805,minimum_actual_surface_radius=minimum,minimum_actual_square_half_extent=square_minimum,limiting_mesh=limiter,ground_cell_world_units=32,closed_bind_horizontal_span=span,building_scale_world_per_local=building_scale,vertical_corridor=[-1.25,2.0],ships=rows,game_client_accepted=False,game_production_roster_verified=False,scale_limit='Same-culture geometry at explicit asset proposals only. Game currently lacks Mauna size overrides and confirmed production recipes;fallback96 fails. Type1.5 requires45degree alignment before vertical transit.')



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
    verts=[(x*r,y*r,0) for r in [.805,8] for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]];faces=[(i,(i+1)%4,4+(i+1)%4,4+i) for i in range(4)]
    mesh=bpy.data.meshes.new('Non-exported square terrain-cutout review ground');mesh.from_pydata(verts,[],faces);o=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(o)
    m=bpy.data.materials.new('Review ground holdout');m.use_nodes=True;m.node_tree.nodes.clear();out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');mask=m.node_tree.nodes.new('ShaderNodeHoldout');m.node_tree.links.new(mask.outputs[0],out.inputs['Surface']);o.data.materials.append(m);return o

def render(label,media):
    s=setup();meshes=[o for o in s.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes if 'underground' not in o.name and 'shaft floor' not in o.name for v in o.bound_box];centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);renders={}
    ground=review_ground(True)
    for view,direction in [('front-quarter',(10,-10,8)),('front',(0,-16,9)),('rear-quarter',(7,12,9))]:
        v=Vector(direction).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];midpoint=Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0));s.camera.location+=s.camera.rotation_euler.to_matrix()@midpoint;s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2;p=media/f'{label}-{view}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);p.write_bytes(clean_png(p.read_bytes()));renders[p.name]=sha(p)
    bpy.data.objects.remove(ground,do_unlink=True)
    return renders

def main():
    folder=ROOT/'sources/objects/mauna/launch-area';media=ROOT/'gallery/media/objects/mauna/launch-area';media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
    assert meta['author']=='sources/tools/blender/remaster_mauna_launch_area.py'
    assert meta['author_sha256']==sha(Path(__file__).with_name('remaster_mauna_launch_area.py'))
    assert meta['concept_review']=='sources/docs/reconstruction/models/mn09-concept-review.json'
    assert json.loads((ROOT/meta['concept_review']).read_bytes())['id']==meta['id']
    for ext,h in meta['binaries'].items():assert sha(folder/f'model.{ext}')==h
    poses=[(frame,min(1,(frame-1)/24,(97-frame)/24),0) for frame in range(1,98)]
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
    bpy.context.scene.frame_set(49);bpy.context.view_layer.update();opened,_,_=snapshot(1,0);clearance=clearance_geometry(opened,meta,native_samples[0])
    renders.update(render('imported-open',media))
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();imported,ii,ir=snapshot();assert nr==ir
    assert sorted((v['size'],v['pixels']) for v in ni.values())==sorted((v['size'],v['pixels']) for v in ii.values())
    assert error<1e-5;raw=(folder/'model.glb').read_bytes();gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);tri=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives']);assert tri==meta['triangles']==sum(o['triangles'] for o in imported.values());assert tri<30000;assert [clip['name'] for clip in gltf['animations']]==['LaunchFacilityCycle'];assert len(gltf['materials'])==8;assert all('bufferView' in i for i in gltf['images']);renders.update(render('imported',media))
    s=bpy.context.scene
    detail_ground=review_ground(True)
    for label,centre,scale in [('braced-mast-and-source-markings-detail',Vector((-.30,.10,1.10)),2.0),('downward-doors-and-hinge-bearings-detail',Vector((0,0,.25)),1.9)]:
        s.frame_set(49 if label.startswith('downward') else 1);bpy.context.view_layer.update();direction=Vector((8,-10,10)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;path=media/(label+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    bpy.data.objects.remove(detail_ground,do_unlink=True)
    s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
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
    s.camera.data.ortho_scale=4.2;s.render.filepath=str(media/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    path=media/'technical-wireframe.png';path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    allpoints=[p for n in native.values() for p in n['points']];bounds=[min(p[a] for p in allpoints) for a in range(3)]+[max(p[a] for p in allpoints) for a in range(3)]
    report=dict(issue=261,id=meta['id'],blender=bpy.app.version_string,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),triangles=tri,meshes=len(native),materials=len(gltf['materials']),embedded_images=len(gltf['images']),maximum_bidirectional_surface_error=error,positive_closed_meshes=dict(native=len(native),imported=len(imported)),native_world_bounds=bounds,native_root_matrix=nr,texture_pixels_equal=True,clips=['LaunchFacilityCycle'],animation_samples=len(poses),clearance=clearance,renders=renders,scope='Actual saved native/imported GLB97integer-frame door poses,closed positive surfaces,fixed fittings,moving attached source-shaped roof,texture pixels and renders. Full-open geometric cylindrical corridor is checked against independent canonical ship vertices at256headings using explicit same-culture proposals40/56,with Type1.5 aligned45degrees. Terran rows are supplementary;installed Mauna fallback96 is rejected and game production is not established. Asset-only scale contract;no client/state/FPS acceptance.',final_artistic_acceptance=False,game_client_integration=False)
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('MN09_RUNTIME_OK',tri,len(native),error,flush=True)
if __name__=='__main__':main()
