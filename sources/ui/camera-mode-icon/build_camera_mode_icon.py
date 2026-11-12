"""Author a standalone camera orbit/pitch extension using the existing HUD system."""
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy

ROOT=Path(__file__).resolve().parents[3]
SOURCE=Path(__file__).resolve().parent
MEDIA=ROOT/'gallery/media/ui/camera-mode-icon'
sys.path.insert(0,str(SOURCE.parent/'legacy-icon-set'))
import legacy_shapes as g
import icon_recipes as r
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_blend,clean_png


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def render(path):
    g.scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    path.write_bytes(clean_png(path.read_bytes()))


def main():
    MEDIA.mkdir(parents=True,exist_ok=True)
    g.scene.render.resolution_x=384;g.scene.render.resolution_y=320
    g.scene.render.resolution_percentage=100;g.scene.cycles.samples=64
    # Distinct from reset's wire globe/return motif: camera + two motion axes.
    g.box('Worn silver camera body',(-.20,.22,.22),(1.40,.88,.25),g.silver,.09)
    g.box('Raised viewfinder',(-.42,.77,.22),(.52,.22,.22),g.white,.045)
    g.box('Camera grip',(-.81,.20,.39),(.15,.61,.055),g.dark,.025)
    g.tube('Dark lens seat',(-.12,.22,.35),(-.12,.22,.41),.335,g.dark)
    g.tube('Silver lens bezel',(-.12,.22,.42),(-.12,.22,.48),.282,g.white)
    g.tube('Blue optical lens',(-.12,.22,.49),(-.12,.22,.52),.205,g.blue)
    g.box('Lens reflection',(-.18,.31,.54),(.09,.055,.015),g.silver,.012)
    # Horizontal orbit, deliberately broad arrowheads readable at 48x40.
    r.ellipse(-.20,-.42,1.13,.38,g.blue,.082,.08,start=.10,end=math.pi-.10)
    r.ellipse(-.20,-.42,1.13,.38,g.blue,.082,.48,start=math.pi+.10,end=math.tau-.10)
    g.poly('Yaw right arrow',[(.66,-.66),(1.12,-.42),(.67,-.20)],g.blue,.52,.11)
    g.poly('Yaw left arrow',[(-1.10,-.20),(-1.55,-.42),(-1.10,-.65)],g.blue,.12,.11)
    # Separate vertical, curved pitch axis beside the camera.
    r.ellipse(1.15,.16,.24,.79,g.gold,.083,.56,start=-math.pi/2+.16,end=math.pi/2-.16)
    g.poly('Pitch upper arrow',[(.91,.68),(1.18,1.10),(1.43,.69)],g.gold,.57,.10)
    g.poly('Pitch lower arrow',[(.91,-.39),(1.18,-.81),(1.43,-.39)],g.gold,.57,.10)
    source_objects=list(g.parts)
    for material in bpy.data.materials:
        if material.use_nodes:
            bs=material.node_tree.nodes.get('Principled BSDF')
            if bs:bs.inputs['Base Color'].default_value=material.diffuse_color
    native=MEDIA/'native-render.png';render(native)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in source_objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=source_objects[0]
    glb=SOURCE/'camera-mode-icon.glb'
    # glTF cannot encode the procedural colour ramp. Export explicit constant
    # PBR colours, then restore the native wear graph before saving the Blend.
    colour_links=[]
    for material in bpy.data.materials:
        if not material.use_nodes:continue
        bs=material.node_tree.nodes.get('Principled BSDF')
        if not bs:continue
        for link in list(bs.inputs['Base Color'].links):
            colour_links.append((material,link.from_socket,link.to_socket))
            material.node_tree.links.remove(link)
    bpy.ops.export_scene.gltf(filepath=str(glb),use_selection=True,export_format='GLB',export_apply=True,export_animations=False)
    for material,source_socket,target_socket in colour_links:
        material.node_tree.links.new(source_socket,target_socket)
    g.scene.render.filepath='//camera-mode-icon.png'
    blend=SOURCE/'camera-mode-icon.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
    blend.write_bytes(clean_blend(blend.read_bytes())[0])
    for obj in source_objects:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    imported=[o for o in g.scene.objects if o.type=='MESH']
    assert len(imported)==len(source_objects)
    render(MEDIA/'imported-glb.png')
    bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False,use_scripts=False)
    g.scene=bpy.context.scene
    render(MEDIA/'reopened-blend.png')
    inputs=[Path(__file__),Path(g.__file__),Path(r.__file__),SOURCE.parent/'legacy-icon-set/assemble_icon_set.py']
    report=dict(issue=230,id='openfa:camera-mode-icon',native_size=[48,40],hires_size=[384,320],transparent=True,button_chrome=False,text=False,semantics='Toggle camera orbit/yaw and pitch interaction mode. Not camera reset, zoom, pan, or a recovered legacy command.',style_reference=dict(set='sources/ui/legacy-icon-set',legacy_frames=['ICONS.256/006','ICONS.256/019','ICONS.256/059'],palette='BLUE.256',interpretation='Palette/material/raised-sign language only; new camera motif authored from geometry. No legacy pixels or contours used.'),inputs={p.relative_to(ROOT).as_posix():sha(p) for p in inputs},blend=dict(path=blend.relative_to(ROOT).as_posix(),sha256=sha(blend)),glb=dict(path=glb.relative_to(ROOT).as_posix(),sha256=sha(glb)),renders={name:sha(MEDIA/name) for name in ['native-render.png','imported-glb.png','reopened-blend.png']},runtime=dict(blender=bpy.app.version_string,engine='Cycles',samples=64,source_objects=len(source_objects),imported_objects=len(imported),glb_materials='Portable constant PBR approximation; procedural wear is in the native model and PNGs.'))
    (SOURCE/'runtime-proof.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('CAMERA_MODE_GEOMETRY_RENDERED',len(imported),flush=True)


if __name__=='__main__':main()
