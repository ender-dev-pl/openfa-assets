"""Author the separate Sci-Tek screen plaque from inspected SCITEK.256 geometry."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
s=g.scene;s.cycles.samples=32;s.view_settings.view_transform='AgX'
def xy(x,y,z=0):return ((x-160)*.02,(80-y)*.02,z)
def polygon(name,points,mat,z):return g.poly(name,[xy(x,y)[:2] for x,y in points],mat,z,.025)
steel=g.material('Used blue-grey brushed logo plate',(.16,.22,.33),.72,.44)
for n in steel.node_tree.nodes:
    if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=240
    if n.type=='VALTORGB':n.color_ramp.elements[0].color=(.12,.165,.2475,1)
    if n.type=='BUMP':n.inputs['Strength'].default_value=.04;n.inputs['Distance'].default_value=.0015
black=g.material('Deep black recessed logo inlay',(.001,.002,.003),.0,.7)
for n in black.node_tree.nodes:
    if n.type=='BSDF_PRINCIPLED':n.inputs['Specular IOR Level'].default_value=.08
g.box('Sci-Tek plaque - original drawn rectangle 234x115',xy(117,57.5,-.10),(4.68,2.30,.12),steel,.012)
top=[(4,8),(229,8),(229,33),(99,33),(93,27),(194,27),(194,25),(42,25),(36,18),(204,18),(204,16),(10,16)]
bottom=[(4,104),(229,104),(229,80),(99,80),(93,85),(194,85),(194,88),(42,88),(36,94),(204,94),(204,97),(10,97)]
for name,points in [('Upper stepped inlay',top),('Lower stepped inlay',bottom)]:polygon(name,points,black,.015)
for x0,x1,y in [(4,229,8),(36,204,18),(93,194,27),(4,204,98),(36,194,89),(93,229,80)]:
    g.tube('Narrow polished bevel',xy(x0,y,.035),xy(x1,y,.035),.009,g.silver)
font=bpy.data.fonts.load('C:/Windows/Fonts/arialbd.ttf')
def label(body,left,right):
    d=bpy.data.curves.new('Sci-Tek engraved lettering','FONT');d.body=body;d.font=font;d.size=.7;d.extrude=.009;d.bevel_depth=.002
    o=bpy.data.objects.new(body+' black inlay',d);s.collection.objects.link(o);g.finish(o,black,o.name)
    bpy.context.view_layer.update();o.scale=(.02*(right-left)/o.dimensions.x,.02*22/o.dimensions.y,1);o.location=xy(left,66,.07)
label('SCI',9,90);label('TEK',130,225)
star=[(114,38),(117,41),(119,53),(130,51),(132,54),(126,58),(135,59),(136,62),(124,63),(130,70),(128,73),(120,69),(118,75),(115,74),(113,65),(101,72),(97,72),(96,69),(106,63),(92,62),(91,59),(99,57),(108,57),(100,49),(99,46),(102,45),(112,52),(112,42)]
polygon('Continuous silver Sci-Tek device emblem',star,g.silver,.105)
centre=(114,59)
inner=[(centre[0]+(x-centre[0])*.85,centre[1]+(y-centre[1])*.85) for x,y in star]
polygon('Brushed emblem inset',inner,steel,.145)
g.tube('Red diagonal probe',xy(99,71,.185),xy(128,54,.185),.035,g.red,.010)
g.uv('Red probe round cap',xy(99,71,.185),(.047,.047,.035),g.red)
g.camera.location=(0,0,12);g.camera_data.ortho_scale=6.4;s.render.resolution_x=1280;s.render.resolution_y=640
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scitek-screen-logo.blend'))
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
render('logo.png')
# Explicit portable PBR export; native procedural wear remains in the Blend.
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if not bs:continue
    for slot in ['Base Color','Normal','Metallic','Roughness']:
        for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=mat.diffuse_color
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
    if o.type in ['MESH','CURVE','FONT']:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'scitek-screen-logo.glb'),use_selection=True,export_apply=True,export_format='GLB')
for o in list(s.objects):
    if o.type in ['MESH','CURVE','FONT']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'scitek-screen-logo.glb'));render('imported-logo.png')
assert any(o.type=='MESH' for o in s.objects)
bpy.ops.wm.open_mainfile(filepath=str(out/'scitek-screen-logo.blend'));s=bpy.context.scene;render('reload-logo.png')
proof=dict(issue=208,legacy_reference='_MS/SCITEK.256 frame 0, BUTTONS.256 runtime palette',canvas=[320,160],drawn_rectangle=[0,0,234,115],render_scale=4,source_geometry='Authored plaque, inlay polygons, lettering and continuous emblem. Reference pixels are not textures.',limitations=['Font outlines are an authored approximation of the original typeface.','GLB uses constant PBR colors; editable Blend preserves procedural wear.'],blender=bpy.app.version_string,checks=['saved Blend reopen/render','independent GLB import/render'])
proof['hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.suffix in ['.png','.blend','.glb']}
(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('SCITEK_LOGO_RUNTIME_VERIFIED')
