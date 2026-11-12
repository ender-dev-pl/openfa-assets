"""AC13 twin minarets and permanently open seven-field launcher chamber."""
import math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cut,cleanup,worn_coral_pbr
PORTS=[(-.16,.70),(.16,.70),(-.28,.48),(0,.48),(.28,.48),(-.16,.24),(.16,.24)]


def cylinder(name,centre,radius,depth,mat,axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=centre)
    o=bpy.context.object;o.name=name;o.data.materials.append(mat)
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    return o


def surface_y(body,x,z):
    tree=BVHTree.FromPolygons([body.matrix_world@v.co for v in body.data.vertices],[tuple(f.vertices) for f in body.data.polygons])
    hit=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None
    return hit[0].y


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='missile-launcher'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Slate twin heads',(.16,.24,.29),.7,.4);dark=material(folder,'Dark recessed fields',(.015,.020,.025),0,.87);red=material(folder,'Red source optics',(.26,.004,.001),.12,.3,.12)
    dark.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.1;worn_coral_pbr(coral,folder)
    left=lathe('AC13 left twin-post chamber',(-.55,.04),[(0,.50),(.06,.62),(.28,.67),(.52,.62),(.76,.45),(.88,.22),(.93,.07)],coral)
    right=lathe('AC13 seven-field launcher chamber',(.55,-.20),[(0,.51),(.06,.62),(.32,.66),(.57,.63),(.78,.50),(.93,.29),(.98,.25),(1.05,.25)],coral)
    for i,(dx,z) in enumerate(PORTS):
        x=.55+dx;y=surface_y(right,x,z)
        cut(right,cylinder('temporary dark field bore',(x,y-.02,z),.068,.25,dark,'Y'),'Actual front circular recess '+str(i))
        cylinder('AC13 dark field floor '+str(i),(x,y+.090,z),.066,.018,dark,'Y')
    # Preserve the prior refinement's useful exposed .17-radius mouth and .05 floor.
    cut(right,cylinder('temporary permanently open bore',(.55,-.20,.75),.17,1.40,dark),'Permanently open emitter')
    cylinder('AC13 recessed launch well floor',(.55,-.20,.052),.169,.008,dark)
    for i,x in enumerate([-.75,-.35]):
        profile=[(.68,.115),(.82,.105)]
        for j in range(6):
            z=.86+j*.19;profile.extend([(z,.10),(z+.025,.112),(z+.065,.112),(z+.09,.10)])
        profile.extend([(1.99,.10),(2.03,.13)])
        lathe('AC13 coral post '+str(i),(x,.15),profile,coral)
        head=lathe('AC13 slate post head '+str(i),(x,.15),[(1.99,.125),(2.04,.17),(2.26,.18),(2.34,.15),(2.40,.15),(2.46,.10),(2.49,.055),(2.69,.045)],slate)
        y=surface_y(head,x,2.17)
        cut(head,box('temporary slate head slot',(x,y-.02,2.17),(.085,.15,.15),dark,.01),'Head slot '+str(i))
        box('AC13 slate head dark slot '+str(i),(x,y+.045,2.17),(.08,.012,.14),dark,.008);cleanup(head)
    for i,x in enumerate([-.70,-.43]):
        z=.20;y=surface_y(left,x,z)
        cut(left,box('temporary red optic pocket',(x,y-.02,z),(.13,.18,.13),dark,.012),'Red source field '+str(i))
        box('AC13 low red optic '+str(i),(x,y+.055,z),(.12,.012,.12),red,.01)
    for o in [left,right]:cleanup(o)
    finish(folder,dict(issue=256,id='openfa:building/legacy/163',key='AC13',name='Missile Launcher',culture='achaean',footprint=[2,2],definition_class=14,construction_updates=34,triangle_budget=30000,materials=4,structure_checks='checks_achaean_missile_launcher',state_contract='Static exposed Achaean launcher: two grounded connected coral chambers,two parallel ringed posts with slate heads,seven recessed front fields and two red source optics. Actual surface has only shadow/body; fixed-view catalogue reveal does not establish a lid cycle. Retains useful prior permanent .17-radius emitter opening and .05-height dark floor. No invented lid animation. Dark front recess purpose,hidden rear and dimensions remain interpreted. Shared ACS2 construction and client missile/mode/state/scale mapping remain separate.',scale_contract='PlacementRoot at groundZ0; Blender-Y front/+Zup. Exposed emitter dimensions are authored; client rocket fit and tile/world calibration remain separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),Path(__file__).with_name('remaster_achaean_shipyard.py'),Path(__file__).with_name('checks_achaean_shipyard.py'),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/reconstruction/launch-facilities/achaean/ac13/model.blend'])
if __name__=='__main__':main()
