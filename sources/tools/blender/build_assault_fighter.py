"""Independently authored PS00 silhouette study; no original pixels or meshes loaded."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_openfa_assets import beam, box, cylinder, finish, material, setup_scene
from build_refined_terran import export_glb_to, render_to, save_blend_to
from catalogue_rendering import evaluated_points, fit_camera
from fighter_plate_topology import repair_plate

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / 'docs/assets/reconstruction/ships/terran/assault-fighter'


def plate(name, points, thickness, surface, bevel=.012):
    count = len(points)
    vertices = [tuple(point) for point in points]
    vertices += [(x, y, z-thickness) for x, y, z in points]
    faces = [tuple(range(count)), tuple(reversed(range(count, count*2)))]
    faces += [(i, i+count, (i+1)%count+count, (i+1)%count) for i in range(count)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, surface, bevel)


def nozzle(name, x, y, z, radius, m):
    # Hollow, axis +Y exhaust. Front lip, internal throat and rear taper are actual geometry.
    sections = [(0, radius), (.13, radius*1.04), (.30, radius*.85),
                (.30, radius*.65), (.08, radius*.54), (-.12, radius*.42)]
    vertices = [(x+r*math.cos(a*math.tau/48), y+depth, z+r*math.sin(a*math.tau/48))
                for depth, r in sections for a in range(48)]
    faces = [(ring*48+i, ring*48+(i+1)%48, (ring+1)*48+(i+1)%48, (ring+1)*48+i)
             for ring in range(len(sections)-1) for i in range(48)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj, name, m['gold'], 0)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    cylinder(name+' recessed core', (x, y-.14, z), radius*.42, .025, m['dark'], rotation=(math.pi/2, 0, 0))
    cylinder(name+' pilot glow', (x, y-.12, z), radius*.17, .026, m['glow'], rotation=(math.pi/2, 0, 0))
    for i in range(12):
        a = i*math.tau/12
        beam(name+' cooling rib', (x+radius*.94*math.cos(a), y+.05, z+radius*.94*math.sin(a)),
             (x+radius*.84*math.cos(a), y+.28, z+radius*.84*math.sin(a)), .012, m['edge'])


def dorsal_shell(surface):
    sections=[(-2.73,.025,.18),(-1.50,.29,.34),(-.60,.64,.50),(.48,.73,.64),(.95,.70,.64),(1.60,.45,.32)]
    vertices=[]
    for y,w,z in sections:
        vertices.extend([(w*x,y,.15+(z-.15)*height) for x,height in
                         [(-1,0),(-1,.42),(-.65,.90),(0,1),(.65,.90),(1,.42),(1,0)]])
    faces=[tuple(reversed(range(7))),tuple(range((len(sections)-1)*7,len(sections)*7))]
    faces += [(r*7+i,r*7+(i+1)%7,(r+1)*7+(i+1)%7,(r+1)*7+i)
              for r in range(len(sections)-1) for i in range(7)]
    mesh=bpy.data.meshes.new('Faceted pressure shell')
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new('Raised central dorsal shell',mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj,obj.name,surface,.008)
    return obj


def wing_panels(sign,m):
    # A ruled surface split into separate manufactured plates. Shared edge gaps
    # replace the previous overlapping, partly buried access-panel rectangles.
    inner0=(.34,-1.48,.17)
    inner1=(.79,1.48,.18)
    outer0=(.65,-.44,.34)
    outer1=(1.67,1.39,.17)
    def point(u,v):
        inner=[a+(b-a)*v for a,b in zip(inner0,inner1)]
        outer=[a+(b-a)*v for a,b in zip(outer0,outer1)]
        p=[a+(b-a)*u for a,b in zip(inner,outer)]
        return (sign*p[0],p[1],p[2])
    substrate=[point(0,0),point(1,0),point(1,1),point(0,1)]
    substrate=[(x,y,z-.012) for x,y,z in substrate]
    if sign<0:
        substrate.reverse()
    plate('Continuous wing load-bearing web',substrate,.24,m['hull'],.003)
    for row in range(6):
        v0=row/6+.003
        v1=(row+1)/6-.003
        points=[point(.012,v0),point(.988,v0),point(.988,v1),point(.012,v1)]
        if sign<0:
            points.reverse()
        panel=plate('Swept tessellated wing armour',points,.043,m['panel'] if row%3==0 else m['hull'],.003)
        repair_plate(panel)
        if row in [2,4]:
            for u in [.12,.88]:
                p=point(u,(v0+v1)/2)
                cylinder('Wing captive fastener',(p[0],p[1],p[2]+.006),.018,.012,m['edge'],vertices=8)


def auxiliary_fairing(sign,m):
    # PS00 frames 5/20/40/50 show silver pods around the small outer drives.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(sign*1.90,1.30,.10))
    obj=bpy.context.object
    obj.scale=(.26,.40,.24)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(obj,'Outer drive silver fairing',m['edge'],0)
    for face in obj.data.polygons:
        face.use_smooth=True
    # A restrained segmented belt and two service clamps are authored detail.
    for x in [-.17,.17]:
        beam('Auxiliary fairing clamp',(sign*1.90+x,1.12,.26),(sign*1.90+x,1.43,.25),.018,m['hull'])


def build():
    m = dict(hull=material('Fighter | violet titanium', (.15,.14,.21), .6,.38),
             panel=material('Fighter | service alloy', (.24,.23,.31), .55,.43),
             red=material('Fighter | vermilion enamel', (.55,.025,.018), .3,.37),
             dark=material('Fighter | recessed graphite', (.012,.014,.022), .4,.55),
             edge=material('Fighter | machined edges', (.31,.33,.38), .75,.31),
             gold=material('Fighter | heat shield bronze', (.42,.28,.095), .7,.38),
             glow=material('Fighter | standby drive', (.95,.22,.025), .1,.4,.6))
    # Planform from PS00 rotation: pointed triangular nose, broad rear and raised centre.
    plate('Continuous triangular pressure hull', [(0,-3,.12),(2.28,1.55,.12),(.85,1.80,.12),
          (-.85,1.80,.12),(-2.28,1.55,.12)], .23, m['hull'])
    shell=dorsal_shell(m['hull'])
    plate('Ventral keel', [(0,-2.75,-.10),(.57,-.40,-.19),(.56,1.50,-.17),
          (-.56,1.50,-.17),(-.57,-.40,-.19)], .12, m['dark'])
    for sign in [-1, 1]:
        def pts(items):
            result = [(sign*x,y,z) for x,y,z in items]
            return result if sign == 1 else list(reversed(result))
        plate('Swept red edge band', pts([(.08,-2.72,.142),(2.22,1.51,.142),(1.83,1.45,.142),(.17,-1.99,.142)]), .018, m['red'], .004)
        wing_panels(sign,m)
        plate('Outer wingtip guard', pts([(1.99,1.02,.17),(2.32,1.51,.17),(2.05,1.61,.17),(1.78,1.20,.17)]), .11, m['edge'])
        # Recesses visible in rotation are modelled as bordered wells with inset louvres.
        for y in [-.22,.48]:
            cutter=cylinder('Temporary recess cutter',(sign*.34,y,.70),.157,.54,m['dark'],vertices=48)
            cutter.scale.y=1.45
            bpy.context.view_layer.objects.active=cutter
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
            bpy.context.view_layer.objects.active=shell
            modifier=shell.modifiers.new('True elliptical dorsal well','BOOLEAN')
            modifier.operation='DIFFERENCE'
            modifier.object=cutter
            bpy.ops.object.modifier_move_to_index(modifier=modifier.name,index=0)
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.data.objects.remove(cutter,do_unlink=True)
            inner = cylinder('Dorsal well shadow', (sign*.34,y,.437), .151,.012,m['dark'],vertices=48)
            inner.scale.y = 1.45
            for step in range(5):
                box('Recessed heat exchanger fin',(sign*.34,y+(step-2)*.056,.453),(.22,.016,.018),m['edge'],.003)
        # Rear drive fairings with bronze open throats.
        plate('Drive shoulder',pts([(.63,.75,.30),(1.20,1.12,.26),(1.25,1.80,.13),(.61,1.83,.29)]),.30,m['hull'])
        nozzle('Main exhaust '+str(sign),sign*.87,1.69,-.005,.33,m)
        nozzle('Outer auxiliary exhaust '+str(sign),sign*1.90,1.47,.005,.19,m)
        auxiliary_fairing(sign,m)
        cylinder('Shoulder inspection cap',(sign*1.02,1.17,.30),.15,.06,m['panel'],vertices=16)
        for i in range(3):
            box('Rear heat discharge slot',(sign*1.02, .91+i*.095,.322),(.18,.035,.018),m['dark'],.003)
        for y in [-.62,.87]:
            cylinder('Flush armour fastener',(sign*.61,y,.345 if y<0 else .39),.026,.012,m['edge'],vertices=8)
        beam('Wingtip sensor', (sign*2.10,1.40,.17),(sign*2.38,1.64,.20),.018,m['edge'])
    # Rear hump is visible in several rotation views; ellipsoid uses authored dimensions.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=(0,1.02,.46))
    cap=bpy.context.object
    cap.scale=(.39,.46,.24)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(cap,'Raised aft pressure fairing',m['panel'],0)
    for face in cap.data.polygons:
        face.use_smooth=True
    for sign in [-1,1]:
        for i in range(5):
            box('Aft radiator bank',(sign*.52,1.0+i*.065,.41),(.10,.022,.024),m['dark'],.003)
    beam('Nose probe',(0,-2.93,.12),(0,-3.22,.12),.014,m['edge'])
    cylinder('Nose sensor jewel',(0,-2.61,.208),.045,.018,m['glow'],vertices=16)
    # Hidden belly geometry is explicitly authored, not established by available top rotations.
    for sign in [-1,1]:
        plate('Inferred belly maintenance cover',[(sign*.15,-.70,-.318),(sign*.47,-.28,-.318),
              (sign*.47,.67,-.318),(sign*.15,.83,-.318)],.02,m['panel'])
    # Broader delta proportion follows the inventory rotation rather than the tiny surface icon.
    for obj in list(bpy.context.collection.objects):
        if obj.type=='MESH':
            obj.matrix_world=Matrix.Diagonal((1,.83,1,1)) @ obj.matrix_world
            # Thin inset disks need a proportionate chamfer; oversized bevels
            # collapse faces during GLB triangulation.
            extent=[max(v.co[a] for v in obj.data.vertices)-min(v.co[a] for v in obj.data.vertices) for a in range(3)]
            for modifier in obj.modifiers:
                if modifier.type=='BEVEL':
                    modifier.width=min(modifier.width,min(extent)*.15)
            bm=bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            if all(edge.is_manifold for edge in bm.edges) and bm.calc_volume(signed=True)<0:
                bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
            bm.to_mesh(obj.data)
            bm.free()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    scene=setup_scene(768,48)
    scene.name='Assault Fighter | independent reconstruction study'
    bpy.context.preferences.filepaths.save_version=0
    collection=bpy.data.collections.new('Terran Assault Fighter')
    scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    build()
    collection.asset_mark()
    collection.asset_data.description='PS00 reference-based independent study; hidden surfaces inferred; no sockets established'
    meshes=[obj for obj in collection.objects if obj.type=='MESH']
    points=evaluated_points(meshes)
    views=[('front-quarter',(8,-12,10)),('rear-quarter',(-8,12,10)),('top',(0,0,20)),
           ('side',(14,0,4)),('rear',(0,14,4)),('belly',(7,-10,-12))]
    for name,direction in views:
        fit_camera(scene,points,direction)
        render_to(scene,OUT/(name+'.png'))
    fit_camera(scene,points,views[0][1])
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    export_glb_to(OUT/'model.glb')
    save_blend_to(OUT/'model.blend')
    manifest=dict(id='openfa:assault-fighter',issue=953,revision=4,blender=bpy.app.version_string,
                  generator='tools/blender/build_assault_fighter.py',generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  blend_sha256=hashlib.sha256((OUT/'model.blend').read_bytes()).hexdigest(),
                  glb_sha256=hashlib.sha256((OUT/'model.glb').read_bytes()).hexdigest(),
                  helper_sha256={'fighter_plate_topology.py':hashlib.sha256(Path(__file__).with_name('fighter_plate_topology.py').read_bytes()).hexdigest()},
                  mesh_objects=len(meshes),faces=sum(len(obj.data.polygons) for obj in meshes),
                  forward='-Y',up='+Z',views=[name for name,_ in views],resolution=768,
                  imported_geometry_or_textures=[],reference_only=['PS00.VID frames 0,15,30,45,59','PS0A.256 frames 0,8,16,24'],
                  inferred=['Belly maintenance covers','Nozzle internal baffles and ribs','Panel segmentation and fasteners'],
                  unresolved=['Exact physical dimensions','3D hardpoint sockets','Gameplay scale and registration'],
                  acceptance='study; visual review and refinement required')
    (OUT/'model.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('ASSAULT_FIGHTER_GENERATION_OK',len(meshes),flush=True)


if __name__=='__main__':
    main()
