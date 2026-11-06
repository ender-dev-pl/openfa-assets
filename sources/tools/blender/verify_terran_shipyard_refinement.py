"""Verify the actual native and independent rigid GLB for Terran PB25 (#225)."""
import hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'sources/objects/terran/ship-yard/refined'
MEDIA=ROOT/'gallery/media/objects/terran/ship-yard/refined'
FRAMES=[1,26,40,60,75,90,100,110,120,135,145,165,185,205,230,245,260,280,300]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def pose(frame):
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
    rows={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        evaluated=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
        points=[evaluated.matrix_world@v.co for v in evaluated.data.vertices]
        rows[o.name]=dict(low=[min(p[i] for p in points) for i in range(3)],high=[max(p[i] for p in points) for i in range(3)])
    return rows

def geometry_points():
    deps=bpy.context.evaluated_depsgraph_get()
    return {o.name:[o.evaluated_get(deps).matrix_world@v.co for v in o.evaluated_get(deps).data.vertices] for o in bpy.context.scene.objects if o.type=='MESH'}


def point_distance(a,b):
    tree=KDTree(len(b))
    for i,p in enumerate(b):tree.insert(p,i)
    tree.balance()
    return max(tree.find(p)[2] for p in a)


def glb_document():
    raw=(OUT/'model.glb').read_bytes();n=int.from_bytes(raw[12:16],'little');return json.loads(raw[20:20+n])

def world_bvh(obj,deps):
    e=obj.evaluated_get(deps)
    return BVHTree.FromPolygons([e.matrix_world@v.co for v in e.data.vertices],[tuple(p.vertices) for p in e.data.polygons])


def platform_clashes(crane,deck,deps,frame):
    hits=[];plane=.905*.3;epsilon=.000005
    dv=world_bvh(deck,deps)
    for c in crane:
        for a,b in world_bvh(c,deps).overlap(dv):
            cp=[c.matrix_world@c.data.vertices[i].co for i in c.data.polygons[a].vertices]
            dp=[deck.matrix_world@deck.data.vertices[i].co for i in deck.data.polygons[b].vertices]
            contact=(115<=frame<=225 and c.name=='CraneSlewGeometry' and
                     min(p.z for p in cp)>=plane-epsilon and max(p.z for p in dp)<=plane+epsilon)
            if not contact:hits.append((c.name,deck.name,b))
    return hits


def support_gaps(deps):
    # Probe actual support vertices and actual boom faces, not a nominal animation key.
    deck=bpy.data.objects['FabricationDeckGeometry'];boom=bpy.data.objects['CraneSlewGeometry'];bv=world_bvh(boom,deps);rows=[]
    points=[deck.matrix_world@v.co for v in deck.data.vertices]
    for x in [-.45,.55]:
        for y in [-.20,.20]:
            sx,sy=x*.3,y*.3
            top=max(p.z for p in points if abs(p.x-sx)<.031 and abs(p.y-sy)<.035)
            hit,normal,index,distance=bv.ray_cast(Vector((sx,sy,top-.15)),Vector((0,0,1)))
            assert hit is not None,(x,y,'No beam over support')
            rows.append(dict(x=sx,y=sy,support_top=top,boom_bottom=hit.z,gap=hit.z-top))
    return rows


def native_collisions():
    results=[]
    for frame in range(1,301):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        static=[bpy.data.objects[n] for n in ['StaticBaseGeometry','FabricationDeckGeometry']]
        covers=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Shutter_')]
        crane=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Crane','Trolley','Hoist','Antenna'))]
        trees={o.name:world_bvh(o,deps) for o in static+crane};hits=[]
        for o in covers:
            ov=world_bvh(o,deps)
            for fixed in static:
                for a,b in ov.overlap(trees[fixed.name]):
                    pts=[fixed.matrix_world@fixed.data.vertices[i].co for i in fixed.data.polygons[b].vertices]
                    if fixed.name=='StaticBaseGeometry' and all(math.hypot(p.x,p.y)>1.245 for p in pts):continue
                    hits.append((o.name,fixed.name,b))
            for c in crane:
                if ov.overlap(trees[c.name]):hits.append((o.name,c.name,'interior'))
        deck_hits=platform_clashes(crane,static[1],deps,frame)
        results.append(dict(frame=frame,interior_collision_count=len(hits)+len(deck_hits),crane_platform_collision_count=len(deck_hits),examples=(hits+deck_hits)[:3]))
    bpy.context.scene.frame_set(120);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    rest=support_gaps(deps);assert all(abs(r['gap'])<.00001 for r in rest),rest
    lift=bpy.data.objects['CraneLift'];lift.location.z-=.20;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    negative=platform_clashes(crane,static[1],deps,120)
    assert negative,'Negative control failed to detect beam/platform penetration'
    bpy.context.scene.frame_set(121);bpy.context.scene.frame_set(120)
    return results,rest,len(negative)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'model.blend'),load_ui=False,use_scripts=False)
    native={str(f):pose(f) for f in FRAMES};bpy.context.scene.frame_set(1);native_points=geometry_points();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
    assert triangles<85000 and len(meshes)<=32
    assert not any(o.type=='ARMATURE' for o in bpy.context.scene.objects)
    missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).is_file()]
    assert not missing,missing
    doc=glb_document();assert not doc.get('skins');assert len(doc['materials'])==1
    assert all(p.get('mode',4)==4 for m in doc['meshes'] for p in m['primitives'])
    assert len(doc.get('animations',[]))==1
    assert {'translation','rotation','scale'}>={ch['target']['path'] for a in doc['animations'] for ch in a['channels']}
    assert all('uri' not in im for im in doc['images'])
    mat=doc['materials'][0];assert mat.get('alphaMode','OPAQUE')=='OPAQUE';assert not mat.get('doubleSided',False)
    assert mat['pbrMetallicRoughness'].get('baseColorTexture') and mat['pbrMetallicRoughness'].get('metallicRoughnessTexture')
    assert mat.get('emissiveTexture')
    collisions,rest_contacts,negative_control_hits=native_collisions()
    # Record every clearance result; never conceal clashes by only checking endpoints.
    collision_frames=[r for r in collisions if r['interior_collision_count']]
    bpy.context.scene.frame_set(1)
    for o in list(bpy.context.scene.objects):
        if o.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(OUT/'model.glb'))
    imported={str(f):pose(f) for f in FRAMES}
    bpy.context.scene.frame_set(1);imported_points=geometry_points()
    geometry_drift=max(max(point_distance(points,imported_points[name]),point_distance(imported_points[name],points)) for name,points in native_points.items())
    assert geometry_drift<.00001,geometry_drift
    differences=[]
    for f in native:
        assert set(native[f])==set(imported[f]),(f,set(native[f])^set(imported[f]))
        for name in native[f]:
            for bound in ['low','high']:
                differences.extend((abs(a-b),f,name,bound,i,a,b) for i,(a,b) in enumerate(zip(native[f][name][bound],imported[f][name][bound])))
    differences.sort(reverse=True);drift=differences[0][0];print('LARGEST_POSE_DIFFERENCES',differences[:8],flush=True);assert drift<.002,differences[:8]
    scene=bpy.context.scene;scene.render.resolution_x=scene.render.resolution_y=1200;scene.cycles.samples=48
    for name,frame in ([] if '--no-render' in sys.argv else [('imported-front-quarter',1),('imported-closed',165),('imported-crane-rest',120)]):
        scene.frame_set(frame);scene.render.filepath=str(MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True)
    sys.path.insert(0,str(ROOT/'tools'))
    from publication_support import clean_png
    for image in MEDIA.glob('imported-*.png'):image.write_bytes(clean_png(image.read_bytes()))
    report=dict(issue=225,blender=bpy.app.version_string,native_reopened=True,independent_glb_import=True,blend_sha256=sha(OUT/'model.blend'),glb_sha256=sha(OUT/'model.glb'),verifier_sha256=sha(Path(__file__)),triangles=triangles,mesh_nodes=len(meshes),materials=len(doc['materials']),glb_bytes=(OUT/'model.glb').stat().st_size,skin_count=0,animation_clips=len(doc['animations']),sampled_poses=len(FRAMES),max_per_object_bounds_drift=drift,max_bidirectional_vertex_distance=geometry_drift,backface_culling=True,missing_external_dependencies=missing,clearance_samples=collisions,interior_collision_frames=collision_frames,rest_contacts=rest_contacts,negative_control_penetration_hits=negative_control_hits,scope='Native/GLB geometry and rigid animation; all 300 integer frames checked for covers and crane/platform clashes; four actual rest contacts verified; client runtime integration remains separate')
    (OUT/'runtime-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    assert not collision_frames,collision_frames[:4]
    print('SHIPYARD_NATIVE_GLB_VERIFIED',triangles,len(meshes),drift)

if __name__=='__main__':main()
