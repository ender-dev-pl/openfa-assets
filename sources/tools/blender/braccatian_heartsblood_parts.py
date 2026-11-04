"""First BR2C assembly: preserve authored common geometry and add radial pod machinery."""
import hashlib,json,math
from pathlib import Path
import bpy
from mathutils import Vector
from build_openfa_assets import cylinder,beam
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from braccatian_widowmaker_parts import surface as inherited_surface,section as inherited_section

REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'docs/assets/reconstruction/ships/braccatian/widowmaker/model.blend'
INHERITED=['WidowMaker gold pressure hull','WidowMaker rose nose','WidowMaker central nose bezel','WidowMaker central nose face']+[
 prefix+str(i) for i in range(4) for prefix in ['WidowMaker aft duct housing ','WidowMaker recessed duct floor ','WidowMaker gold nose stud ']]+[
 'WidowMaker rose neck accent '+str(i)+' '+str(side) for i in range(4) for side in [-1,1]]
POD_PROFILE=[(-1.0,.05),(-.9375,.16),(-.75,.23),(-.4375,.25),(.50,.25),(.875,.22),(1.0625,.14),(1.125,.08)]
BAND_CENTRES=[-.30,-.08,.14]
CRADLE_Y=[-.30,.30]
SOCKETS={'AlignmentForward':((0,-2.14,0),(0,-1,0))}


def renamed(name):return name.replace('WidowMaker','HeartsBlood')


def geometry_signature(obj):
    data=dict(vertices=[list(v.co) for v in obj.data.vertices],faces=[list(p.vertices) for p in obj.data.polygons])
    return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()


def main_surface(phi,y,offset=0):return inherited_surface('WidowMaker gold pressure hull',phi,y,offset)


def pod_centre(i):
    phi=i*math.pi/2;return Vector((.80*math.cos(phi),0,.80*math.sin(phi)))


def append_inherited():
    meta=json.loads(SOURCE.with_name('model.json').read_text());assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==meta['blend_sha256']
    with bpy.data.libraries.load(str(SOURCE),link=False) as (available,loaded):
        assert set(INHERITED)<=set(available.objects);loaded.objects=list(INHERITED)
    for obj in loaded.objects:
        obj.parent=None;obj.name=renamed(obj.name);obj.data.name=renamed(obj.data.name);bpy.context.collection.objects.link(obj)
    # Library dependencies may bring an unlinked placement root; use a fresh root later.
    for obj in list(bpy.data.objects):
        if obj.name=='PlacementRoot':bpy.data.objects.remove(obj,do_unlink=True)
    materials={m for obj in loaded.objects for m in obj.data.materials}
    for surface in materials:
        surface.name=renamed(surface.name)
        # Reused independent geometry gets new maps in this new model. The source file is unchanged.
        for node in list(surface.node_tree.nodes):
            if node.type in ['TEX_IMAGE','UVMAP']:surface.node_tree.nodes.remove(node)
    for image in list(bpy.data.images):
        if image.source=='FILE' and image.users==0:bpy.data.images.remove(image)
    bpy.context.view_layer.update()


def build():
    append_inherited()
    m={key:bpy.data.materials[name] for key,name in [('gold','HeartsBlood | worn gold hull'),('hull','HeartsBlood | worn rose copper'),('slate','HeartsBlood | worn grey armour'),('edge','HeartsBlood | oxidized titanium'),('dark','HeartsBlood | carbon dark recesses')]}
    for i in range(4):
        phi=i*math.pi/2;centre=pod_centre(i)
        # The local radial angle maps to the outward world X/Z direction after the Y-axis rotation.
        obj=vessel('HeartsBlood radial pod '+str(i),POD_PROFILE,m['hull'],[(-phi,.20,.004)]);obj.location=centre;obj.rotation_euler=(-math.pi/2,0,0)
        for j,y in enumerate(BAND_CENTRES):
            rows=[(z,profile_radius(POD_PROFILE,z)+.014,profile_radius(POD_PROFILE,z)-.024) for z in [y-.03,y+.03]]
            obj=annulus('HeartsBlood pod clamp '+str(i)+' '+str(j),(0,0),rows,m['gold'],(0,y,0));obj.location=centre;obj.rotation_euler=(-math.pi/2,0,0)
        for side,y in [('fore',-.98),('aft',1.11)]:
            cylinder('HeartsBlood pod '+side+' cap '+str(i),centre+Vector((0,y,0)),.10,.08 if side=='fore' else .07,m['slate'],vertices=48,rotation=(-math.pi/2,0,0))
        n=Vector((math.cos(phi),0,math.sin(phi)))
        for j,y in enumerate(CRADLE_Y):
            w,_,_=inherited_section('WidowMaker gold pressure hull',y)
            a=n*(w-.05)+Vector((0,y,0));b=n*.68+Vector((0,y,0))
            beam('HeartsBlood pod cradle '+str(i)+' '+str(j),a,b,.045,m['gold'])
    return m
