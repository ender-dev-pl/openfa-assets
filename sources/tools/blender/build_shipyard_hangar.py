"""Authored PB25 construction extension: full-size hatch and rigid crane transfer (#227)."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
import refine_terran_shipyard as g
from build_ship_construction_layers import save_clean,sha,SHIPS
OUT=ROOT/'sources/objects/terran/ship-yard/hangar'
MEDIA=ROOT/'gallery/media/objects/terran/ship-yard/hangar'
HALF=1.85
MAST=-2.85
DECK=.32
FPS=30
END=480
TIMELINE=dict(build=[1,120],approach=[120,150],attach=150,lift=[150,190],open=[195,235],lower=[245,330],release=335,return_crane=[340,410],close=[415,465],ready=480)


def ship_placement(ship):
    path=ROOT/'sources/objects/terran'/ship/'construction/model.json'
    data=json.loads(path.read_text(encoding='utf-8'));lo,hi=map(Vector,data['shell_bounds']);size=hi-lo
    # Yard is 9 local units / 96 game units. The mobile model uses max(X,Y,Z).
    scale=SHIPS[ship]*9/96/max(size)
    transform=Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-(lo+hi)/2)
    corners=[transform@Vector((x,y,z)) for x in [lo.x,hi.x] for y in [lo.y,hi.y] for z in [lo.z,hi.z]]
    minimum=min(p.z for p in corners)
    transform=Matrix.Translation((0,0,DECK+.012-minimum))@transform
    eye=transform@Vector(data['lift_socket']);contacts=[transform@Vector(p) for p in data['lifting_contacts']]
    return dict(ship=ship,scale=scale,matrix=[list(r) for r in transform],socket=list(eye),contacts=[list(p) for p in contacts],half_width=max(abs(p.x) for p in corners),half_length=max(abs(p.y) for p in corners),top=max(p.z for p in corners)+DECK+.012-minimum,source_glb_sha256=data['glb_sha256'])


def static_geometry():
    original=g.facegroup
    def filter_component(group,vertices,faces,tile=1):
        if group=='FabricationDeck':return
        if group=='StaticBase':
            lo=[min(p[i] for p in vertices) for i in range(3)];hi=[max(p[i] for p in vertices) for i in range(3)]
            # Replace the solid foundation disk by an annulus with a square void.
            if hi[0]-lo[0]>8 and hi[1]-lo[1]>8 and hi[2]<.30:return
            if lo[0]<HALF+.12 and hi[0]>-HALF-.12 and lo[1]<HALF+.12 and hi[1]>-HALF-.12:return
        original(group,vertices,faces,tile)
    g.facegroup=filter_component
    g.make_static()
    g.facegroup=original
    # Exact square hole through the foundation, rather than a black texture over a slab.
    for k in range(96):
        angles=[math.tau*k/96,math.tau*(k+1)/96];vertices=[]
        for z in [0,.26]:
            for radius in [0,1]:
                for a in angles:
                    r=4.49 if radius else (HALF+.13)/max(abs(math.cos(a)),abs(math.sin(a)))
                    vertices.append((r*math.cos(a),r*math.sin(a),z))
        g.facegroup('StaticBase',vertices,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],1)
    # Underground walls and receiver floor are real geometry; the terrain must mask them.
    for side in [-1,1]:
        g.box('HangarWell',(side*(HALF+.30),0,-1.80),(.14,(HALF+.37)*2,3.68),2)
        g.box('HangarWell',(0,side*(HALF+.30),-1.80),(HALF*2+.46,.14,3.68),2)
        for t in range(7):
            z=-3.4+t*.5
            g.box('HangarWell',(side*(HALF+.18),0,z),(.055,HALF*2,.08),8)
            g.box('HangarWell',(0,side*(HALF+.18),z),(HALF*2,.055,.08),8)
        g.box('StaticBase',(side*(HALF+.10),0,.305),(.14,HALF*2+.20,.065),10)
        g.box('StaticBase',(0,side*(HALF+.10),.305),(HALF*2,.14,.065),10)
    g.box('HangarWell',(0,0,-3.73),(HALF*2,HALF*2,.16),7)
    # The load is released onto a receiver, rather than left suspended in the void.
    g.box('HangarWell',(0,0,DECK+.012-3.05-.055),(3.35,3.35,.11),8)
    for side in [-1,1]:
        name=f'HangarDoor_{"Left" if side<0 else "Right"}'
        g.empty(name,g.PARENTS['PlacementRoot'],(side*HALF,0,DECK))
        g.box(name,(-side*HALF/2,0,-.055),(HALF,HALF*2,.11),1)
        for i in range(4):
            for j in range(8):
                g.box(name,(-side*(i+.5)*HALF/4,-HALF+(j+.5)*HALF/4,.006),(HALF/4-.014,HALF/4-.014,.012),12)
        for y in [-HALF+.05,HALF-.05]:g.box(name,(-side*HALF/2,y,.019),(HALF-.06,.04,.012),3)
        for y in [-1.50,-.75,0,.75,1.5]:
            g.rod(name,(0,y-.13,-.055),(0,y+.13,-.055),.072,8,10)
        g.box(name,(-side*(HALF-.025),0,.020),(.035,HALF*2-.06,.015),10)
    # Replacement foundation outside the hatch sweep, with a mast receiving sleeve.
    g.box('StaticBase',(MAST,0,.39),(.94,.94,.20),10)
    for x in [MAST-.30,MAST+.30]:
        for y in [-.30,.30]:g.box('StaticBase',(x,y,.63),(.13,.13,.46),1)
    g.box('StaticBase',(MAST,0,.86),(.72,.72,.08),8)
    # Low work lights surround the opening without obstructing the downward leaves.
    for x in [-HALF-.22,HALF+.22]:
        for y in [-HALF+.20,HALF-.20]:g.box('StaticBase',(x,y,.42),(.10,.14,.16),6)


def animate(config):
    socket=Vector(config['socket']);rise=.85
    lift=g.PARENTS['CraneLift'];slew=g.PARENTS['CraneSlew'];trolley=g.PARENTS['Trolley'];hoist=g.PARENTS['Hoist'];cables=g.PARENTS['HoistCables']
    g.key(lift,1,(MAST,0,.43));g.key(lift,END,(MAST,0,.43))
    g.key(slew,1,rotation=(0,0,0));g.key(slew,END,rotation=(0,0,0))
    # J-hook bottom meets the suspension eye. All load travel is vertical at x=y=0.
    beam_cable_top=.43+2.75+.38
    eye_to_hoist=.37
    def length(z):return beam_cable_top-z-eye_to_hoist
    for f,x in [(1,1.2),(120,1.2),(145,-MAST),(340,-MAST),(405,1.2),(END,1.2)]:g.key(trolley,f,(x,0,.38))
    frames=[(1,beam_cable_top-.4),(145,socket.z+.4),(150,socket.z),(190,socket.z+rise),(245,socket.z+rise),(330,socket.z-3.05),(335,socket.z-3.05),(395,beam_cable_top-.4),(END,beam_cable_top-.4)]
    for f,z in frames:
        value=length(z);assert value>0
        g.key(hoist,f,(0,0,-value));g.key(cables,f,scale=(1,1,value))
    for side in [-1,1]:
        door=g.PARENTS[f'HangarDoor_{"Left" if side<0 else "Right"}']
        for f,a in [(1,0),(195,0),(235,-side*math.pi/2),(415,-side*math.pi/2),(465,0),(END,0)]:g.key(door,f,rotation=(0,a,0))
    socket_obj=g.empty('LoadAttachment',hoist,(0,0,-eye_to_hoist))
    # Explicit reference carrier, never a duplicate ship mesh inside the yard GLB.
    carrier=g.empty('ShipConstructionPlacement',g.PARENTS['PlacementRoot'])
    for f,z in [(1,0),(150,0),(190,rise),(245,rise),(330,-3.05),(END,-3.05)]:g.key(carrier,f,(0,0,z))
    for o in g.PARENTS.values():
        if o.animation_data and o.animation_data.action:
            o.animation_data.action.name='Shipyard crane and hangar transfer'
            for fc in o.animation_data.action.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'
    return socket_obj


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--no-render',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    bpy.context.scene.world=bpy.data.worlds.new('Hangar preview world')
    g.GROUPS.clear();g.PARENTS.clear();g.COUNTS.clear()
    root=g.empty('PlacementRoot');root.scale=(g.SCALE,)*3;root['preserve_ground_origin']=True;root['catalogue_id']='terran:ship-yard'
    for name in ['StaticBase','HangarWell']:g.empty(name,root)
    lift=g.empty('CraneLift',root);slew=g.empty('CraneSlew',lift,(0,0,2.75));trolley=g.empty('Trolley',slew);g.empty('Hoist',trolley);g.empty('HoistCables',trolley);g.empty('Antenna',slew,(.14,.04,.76))
    static_geometry();g.make_crane()
    # The exterior circular roof stays fully retracted during ship transfer.
    g.make_shutters()
    for name,o in list(g.PARENTS.items()):
        if name.startswith('Shutter_'):
            o.location=(o['piece']*.12,o['side']*(3.19+o['band']*.012),1.55+(3-o['band'])*.08+o['piece']*.025)
    configs={ship:ship_placement(ship) for ship in SHIPS}
    for row in configs.values():
        assert max(row['half_width'],row['half_length'])+.25<HALF, row
    attachment=animate(configs['assault-fighter'])
    config=configs['assault-fighter'];eye=Vector(config['socket'])
    for index,contact in enumerate(config['contacts']):
        name=f'LoadSling_{index}';direction=Vector(contact)-eye
        obj=g.empty(name,attachment);obj.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
        g.rod(name,(0,0,0),(0,0,1),.009,8,8)
        g.box(name,(0,0,.98),(.055,.055,.045),10)
        for f,s in [(1,.0001),(145,.0001),(150,1),(335,1),(340,.0001),(END,.0001)]:g.key(obj,f,scale=(s,s,s*direction.length))
        if obj.animation_data:
            for fc in obj.animation_data.action.fcurves:
                for point in fc.keyframe_points:point.interpolation='LINEAR'
    mat,images=g.materials();g.finalize_geometry(mat)
    scene=g.setup_scene(True);scene.frame_end=END;scene.render.resolution_x=scene.render.resolution_y=1000;scene.cycles.samples=32;scene.frame_set(1)
    meshes=[o for o in scene.objects if o.type=='MESH'];triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons)
    assert triangles<85000;assert len(meshes)<40
    bpy.ops.object.select_all(action='DESELECT')
    for o in scene.objects:
        if o.type in ['MESH','EMPTY']:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(OUT/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=True,export_animation_mode='SCENE',export_anim_scene_split_object=False,export_frame_range=True,export_force_sampling=True,export_extras=True)
    scene.render.filepath='//front-quarter.png';save_clean(OUT/'model.blend')
    if not args.no_render:
        for name,frame in [('front-quarter',1),('hatch-open',240),('hatch-closed',END)]:
            scene.frame_set(frame);scene.render.filepath=str(MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True)
        sys.path.insert(0,str(ROOT/'tools'));from publication_support import clean_png
        for path in MEDIA.glob('*.png'):path.write_bytes(clean_png(path.read_bytes()))
    report=dict(issue=227,id='terran:ship-yard',stage='layered-construction-hangar',blend_sha256=sha(OUT/'model.blend'),glb_sha256=sha(OUT/'model.glb'),generator_sha256=sha(Path(__file__)),geometry_helper_sha256=sha(Path(g.__file__)),triangles=triangles,mesh_nodes=len(meshes),fps=FPS,frame_range=[1,END],timeline=TIMELINE,hatch=dict(half_extent_local=HALF,clear_width_world=HALF*2*96/9,deck_height_local=DECK,lowest_floor_local=-3.65),ships=configs,ship_carrier_node='ShipConstructionPlacement',load_attachment_node='LoadAttachment',limitations=['Authored extension, not a recovered legacy production sequence.','Use terrain cutout/masking for underground well; below-ground exterior is not a floating building silhouette.','Drive build phase from simulation progress; play completion transfer only after completion.','The supplied transfer clip is calibrated to Assault Fighter; apply per-ship socket height offsets and sling contacts from this metadata for the other ship types.','The yard export contains no ship geometry; resolve the unique canonical ship GLB by catalogue id.'])
    (OUT/'model.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('SHIPYARD_HANGAR_BUILT',triangles,len(meshes),flush=True)


if __name__=='__main__':main()
