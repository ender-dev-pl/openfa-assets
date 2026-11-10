"""AC18 three supported coral tiers and source-visible open slate conduit spans."""
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cleanup,worn_coral_pbr
from remaster_achaean_manoeuvring_device import field
CENTRES=[(-.36,.02),(.36,.02),(0,-.38)]

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='reactor-cores'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Slate conduits',(.13,.21,.26),.65,.43);brass=material(folder,'Ochre coupling',(.39,.26,.10),.65,.45);dark=material(folder,'Dark inset backs',(.015,.020,.025),0,.83);red=material(folder,'Red instrument fields',(.24,.009,.003),.16,.35);blue=material(folder,'Pale blue conduit fields',(.24,.40,.53),.12,.30,.10);amber=material(folder,'Amber source slit',(.85,.39,.075),.12,.30,.25)
    worn_coral_pbr(coral,folder)
    tiers=[]
    for level,z in enumerate([0,2.35]):
        row=[]
        for i,xy in enumerate(CENTRES):
            profile=[(z,.19),(z+.06,.27),(z+.18,.32),(z+.40,.34),(z+.65,.30),(z+.79,.20),(z+.83,.10)]
            row.append(lathe(f'AC18 tier {level} chamber {i}',xy,profile,coral))
        tiers.append(row)
    for i,xy in enumerate(CENTRES):
        rod=lathe('AC18 lower exposed conduit '+str(i),xy,[(.70,.11),(.77,.13),(.83,.11),(1.25,.11),(1.70,.11),(2.15,.11),(2.42,.11),(2.49,.13),(2.55,.10)],slate)
        bpy.context.view_layer.objects.active=rod;tri=rod.modifiers.new('Conduit base triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
        for j,z in enumerate([1.02,1.47,1.92]):field(rod,f'AC18 lower blue field {i} {j}',xy[0],z,.075,.20,blue,dark)
        bpy.context.view_layer.objects.active=rod;tri=rod.modifiers.new('Conduit cut triangulation','TRIANGULATE');tri.ngon_method='CLIP';bpy.ops.object.modifier_apply(modifier=tri.name);cleanup(rod)
    top=lathe('AC18 upper onion chamber',(0,.02),[(3.60,.23),(3.72,.40),(3.91,.55),(4.18,.63),(4.42,.61),(4.66,.49),(4.86,.30),(5.04,.18),(5.19,.12),(5.25,.11)],coral)
    lathe('AC18 short ochre tip',(0,.02),[(5.18,.10),(5.29,.10),(5.32,.065),(5.58,.065)],brass)
    for i,xy in enumerate(CENTRES[:2]):
        rod=lathe('AC18 upper exposed conduit '+str(i),xy,[(3.02,.11),(3.10,.13),(3.18,.11),(3.45,.11),(3.90,.11),(3.94,.12)],slate)
        bpy.context.view_layer.objects.active=rod;tri=rod.modifiers.new('Conduit base triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
        for j,z in enumerate([3.31,3.62]):field(rod,f'AC18 upper blue field {i} {j}',xy[0],z,.075,.14,blue,dark)
        bpy.context.view_layer.objects.active=rod;tri=rod.modifiers.new('Conduit cut triangulation','TRIANGULATE');tri.ngon_method='CLIP';bpy.ops.object.modifier_apply(modifier=tri.name);cleanup(rod)
    profile=[(3.04,.09)]
    for z in [3.06,3.18,3.30]:profile.extend([(z,.14),(z+.06,.14),(z+.075,.09)])
    profile.append((3.40,.09));lathe('AC18 ribbed ochre middle coupling',(0,-.55),profile,brass)
    instrument=lathe('AC18 front slate instrument',(0,-.38),[(3.34,.10),(3.39,.17),(3.59,.17),(3.66,.11),(4.05,.08),(4.10,.045)],slate)
    field(instrument,'AC18 instrument red field',0,3.52,.16,.16,red,dark)
    field(tiers[0][2],'AC18 lower red field',0,.30,.23,.13,red,dark)
    field(top,'AC18 top red field',.28,3.99,.13,.16,red,dark)
    field(top,'AC18 neck dark aperture',0,5.10,.06,.12,dark,dark)
    for name,z,w in [('AC18 lower amber slit',.30,.11),('AC18 instrument amber slit',3.52,.09)]:
        owner=bpy.data.objects['AC18 lower red field' if z<1 else 'AC18 instrument red field'];o=box(name,owner.location,(w,.015,.035),amber,.004);o.rotation_mode='QUATERNION';o.rotation_quaternion=owner.rotation_quaternion;o.location+=owner.rotation_quaternion@__import__('mathutils').Vector((0,-.012,0))
    for row in tiers:
        for o in row:cleanup(o)
    cleanup(top);cleanup(instrument)
    helpers=['achaean_remaster_geometry.py','remaster_achaean_shipyard.py','remaster_achaean_manoeuvring_device.py','remaster_achaean_missile_launcher.py','checks_achaean_shipyard.py']
    finish(folder,dict(issue=256,id='openfa:building/legacy/168',key='AC18',name='Reactor Cores',culture='achaean',footprint=[2,2],definition_class=28,construction_updates=40,triangle_budget=30000,materials=7,structure_checks='checks_achaean_reactor_cores',state_contract='Static power-generating Reactor Cores from actual body/shadow,all41 fixed-view reveal/highlight phases and additional zoom sprite. Three coral tiers,three lower and two upper exposed slate conduits,pale blue fields,ribbed ochre middle coupling,red/amber front instruments and short upper tip. No mechanical movement,emission pulse or beam inferred. Shared ACS2 construction and client activity/power/damage states separate. Exact hidden depth and field/conduit engineering interpreted.',scale_contract='PlacementRoot identity at groundZ0; Blender-Yfront/+Zup;2x2footprint. Slender three-tier silhouette retained; exact client scale,camera and frame time separate.'),__file__,[*(Path(__file__).with_name(n) for n in helpers),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac18/model.blend'])
if __name__=='__main__':main()




