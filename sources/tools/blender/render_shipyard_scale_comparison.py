"""Compare actual configured game dimensions using authored yard and fighter GLBs (#225)."""
import argparse,hashlib,json,math,re,subprocess,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'sources/objects/terran/ship-yard/refined'
MEDIA=ROOT/'gallery/media/objects/terran/ship-yard/refined'
FIGHTER='sources/docs/assets/reconstruction/ships/terran/assault-fighter/model.glb'

def digest(b):return hashlib.sha256(b).hexdigest()

def points(objects):
    return [o.matrix_world@v.co for o in objects if o.type=='MESH' for v in o.data.vertices]

def bounds(objects):
    p=points(objects);return Vector([min(v[i] for v in p) for i in range(3)]),Vector([max(v[i] for v in p) for i in range(3)])

def find_id(x,id):
    if isinstance(x,dict):
        if x.get('id')==id:return x
        for v in x.values():
            result=find_id(v,id)
            if result:return result
    elif isinstance(x,list):
        for v in x:
            result=find_id(v,id)
            if result:return result
    return None

def fit(scene,objects):
    lo,hi=bounds(objects);centre=(lo+hi)/2;direction=Vector((6,-10,8)).normalized();c=scene.camera
    c.location=centre+direction*300;c.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    local=[c.matrix_world.inverted()@p for p in points(objects)];c.data.type='ORTHO'
    aspect=scene.render.resolution_x/scene.render.resolution_y
    c.data.ortho_scale=max(max(v.x for v in local)-min(v.x for v in local),(max(v.y for v in local)-min(v.y for v in local))*aspect)*1.15
    c.data.clip_end=1000

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--game-root',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);game=args.game_root.resolve()
    inputs={name:(game/name).read_bytes() for name in ['content/openfa3d/catalogue.json','content/standard/catalogues/legacy-buildings.json','src/OpenFA.Core/Presentation/AsteroidSurfaceCameraContext.cs','src/OpenFA.Client/Models/MonoGameSurfaceModelRenderer.cs']}
    cfg=json.loads(inputs['content/openfa3d/catalogue.json']);size=float(cfg['modelWorldSizes']['openfa:assault-fighter'])
    cell=int(re.search(rb'surfaceCellWorldUnitsRaw16:\s*(\d+)\s*<<\s*16',inputs['src/OpenFA.Core/Presentation/AsteroidSurfaceCameraContext.cs']).group(1))
    yard=find_id(json.loads(inputs['content/standard/catalogues/legacy-buildings.json']),'terran:ship-yard');fw,fh=yard['footprintWidth'],yard['footprintHeight']
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'model.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(1)
    yard_objects=[o for o in scene.objects if o.type=='MESH'];lo,hi=bounds(yard_objects);yard_scale=min(fw*cell/(hi.x-lo.x),fh*cell/(hi.y-lo.y))
    placement=bpy.data.objects['PlacementRoot'];placement.location.x-=((lo.x+hi.x)/2)*yard_scale;placement.location.y-=((lo.y+hi.y)/2)*yard_scale;placement.scale*=yard_scale
    for o in scene.objects:
        if o.type=='LIGHT':o.location*=yard_scale;o.data.energy*=yard_scale**2;o.data.size*=yard_scale
    original=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/FIGHTER));new=[o for o in scene.objects if o not in original]
    ships=[o for o in new if o.type=='MESH'];bpy.context.view_layer.update();slo,shi=bounds(ships);ssize=shi-slo;ship_scale=size/max(ssize);centre=(slo+shi)/2
    carrier=bpy.data.objects.new('Comparison fighter placement',None);scene.collection.objects.link(carrier)
    for o in new:
        if o.parent is None:
            world=o.matrix_world.copy();o.parent=carrier;o.matrix_world=world
    yaw=cfg.get('modelYawDegrees',{}).get('openfa:assault-fighter',0)
    rotation=Matrix.Rotation(math.pi/2+math.radians(yaw),4,'Z')
    def place(x,y,bottom):
        carrier.matrix_world=Matrix.Translation((x,y,bottom+ssize.z*ship_scale/2))@rotation@Matrix.Scale(ship_scale,4)@Matrix.Translation(-centre)
        bpy.context.view_layer.update()
    scene.render.resolution_x=1280;scene.render.resolution_y=960;scene.render.resolution_percentage=100;scene.cycles.samples=40
    deck_top=.845*.3*yard_scale;place(0,-.35*.3*yard_scale,deck_top+1.0)
    fit(scene,yard_objects+ships);scene.render.filepath=str(MEDIA/'scale-fighter-in-yard.png');bpy.ops.render.render(write_still=True)
    inyardlo,inyardhi=bounds(ships)
    assert abs(max(inyardhi-inyardlo)-size)<.0001,(inyardlo,inyardhi,size)
    place(fw*cell/2+size/2+8,0,0);fit(scene,yard_objects+ships);scene.render.filepath=str(MEDIA/'scale-fighter-beside-yard.png');bpy.ops.render.render(write_still=True)
    # A top view makes the configured horizontal proportion immediately measurable.
    lo,hi=bounds(yard_objects+ships);centre_view=(lo+hi)/2;c=scene.camera;c.location=(centre_view.x,centre_view.y-.001,250);c.rotation_euler=(Vector((centre_view.x,centre_view.y,0))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=(hi.x-lo.x)*1.15
    scene.render.filepath=str(MEDIA/'scale-fighter-top.png');bpy.ops.render.render(write_still=True)
    for o in new:o.hide_render=True
    scene.frame_set(120);c=scene.camera;c.location=Vector((.7,-2.6,1.8))*yard_scale;c.rotation_euler=(Vector((0,0,.45))*yard_scale-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=1.8*yard_scale
    scene.render.filepath=str(MEDIA/'crane-rest-detail.png');bpy.ops.render.render(write_still=True)
    sys.path.insert(0,str(ROOT/'tools'));from publication_support import clean_png
    for p in list(MEDIA.glob('scale-fighter-*.png'))+[MEDIA/'crane-rest-detail.png']:p.write_bytes(clean_png(p.read_bytes()))
    report=dict(issue=225,game_commit=subprocess.check_output(['git','-C',str(game),'rev-parse','HEAD'],text=True).strip(),input_hashes={k:digest(v) for k,v in inputs.items()},game_inputs_match_commit=all(subprocess.check_output(['git','-C',str(game),'show','HEAD:'+k])==v for k,v in inputs.items()),building_id='terran:ship-yard',ship_id='openfa:assault-fighter',surface_cell_world_units=cell,footprint=[fw,fh],yard_world_dimensions=[fw*cell,fh*cell],ship_world_size=size,longest_ship_axis_to_yard_width=size/(fw*cell),yard_scale=yard_scale,ship_scale=ship_scale,ship_heading=0,ship_yaw_degrees=yaw,in_yard_ship_bounds=[list(inyardlo),list(inyardhi)],yard_blend_sha256=digest((OUT/'model.blend').read_bytes()),fighter_glb_sha256=digest((ROOT/FIGHTER).read_bytes()),renderer_sha256=digest(Path(__file__).read_bytes()),images={p.name:digest(p.read_bytes()) for p in MEDIA.glob('scale-fighter-*.png')},scope='Same configured size normalization as client Placement/MobilePlacement; neutral comparison camera, not a client screenshot. Fighter shown 1 world unit above the deck for size comparison; this does not define a calibrated docking socket.')
    (OUT/'scale-comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('GAME_SCALE_COMPARISON_RENDERED',fw*cell,size,size/(fw*cell))

if __name__=='__main__':main()
