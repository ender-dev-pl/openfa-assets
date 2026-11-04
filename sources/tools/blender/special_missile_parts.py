"""Independent high-detail interpretations of low-resolution PM11/PM12 evidence."""
import math

import bpy

from build_openfa_assets import beam,cylinder,material
from build_shield_equipment import shell
from terran_missile_parts import band,revolved


def palette():
    return dict(silver=material('Special missile | brushed silver',(.29,.33,.37),.72,.38),
        pale=material('Special missile | pale ceramic collar',(.58,.60,.55),.18,.47),
        blue=material('Special missile | blue frame enamel',(.045,.085,.38),.5,.40),
        red=material('Special missile | red couplings',(.40,.045,.035),.42,.43),
        gold=material('Bug Hunter | gold tip',(.51,.27,.055),.65,.38),
        yellow=material('Bug Hunter | yellow identification ring',(.55,.47,.04),.25,.43),
        dark=material('Special missile | recessed graphite',(.012,.016,.025),.3,.50))


def frame(name,profile,half,thickness,m):
    for i in range(4):
        angle=math.pi/2*i
        obj=shell(name,profile,angle-half,angle+half,dict(shell=m['blue'],dark=m['dark']),24,thickness)
        obj.rotation_euler.x=math.pi/2
        # Fasteners at the observed blue region's authored structural ends.
        for z,r in [profile[1],profile[-2]]:
            radial=(math.cos(angle),-math.sin(angle))
            beam(name+' captive fastener',(radial[0]*(r-.012),radial[1]*(r-.012),z),
                 (radial[0]*(r+.018),radial[1]*(r+.018),z),.018,m['pale'])


def nozzle(name,profile,throat_z,m,red=False):
    obj=shell(name,profile,0,math.tau,dict(shell=m['red'] if red else m['silver'],dark=m['dark']),64,.03)
    obj.rotation_euler.x=math.pi/2
    cylinder(name+' recessed throat',(0,0,throat_z),profile[-1][1]-.025,.025,m['dark'],vertices=48)


def bug_hunter(m):
    revolved('Bug Hunter silver pressure shaft',[(.88,.31),(1.2,.34),(2.10,.35),
        (2.55,.37),(3.55,.39),(4.45,.36),(5.24,.30)],m['silver'])
    band('Bug Hunter yellow tip ring',5.26,.31,.12,m['yellow'],.04)
    revolved('Bug Hunter silver tip neck',[(5.26,.29),(5.46,.25),(5.62,.20)],m['pale'])
    revolved('Bug Hunter blunt gold tip',[(5.58,.205),(5.88,.25),(6.07,.24),(6.22,.15),(6.30,.07)],m['gold'])
    smooth=bpy.data.objects['Bug Hunter blunt gold tip'].modifiers.new('Rounded gold probe skin','SUBSURF')
    smooth.levels=2;smooth.render_levels=2
    frame('Bug Hunter blue stabilizer sector',[(1.43,.40),(1.65,.52),(2.13,.55),(2.45,.49),(2.70,.35)],.34,.07,m)
    band('Bug Hunter red tail collar',1.02,.37,.20,m['red'],.055)
    tail=shell('Bug Hunter hollow gray tail casing',[(.14,.29),(.30,.40),(.72,.40),(1.06,.35)],0,math.tau,
        dict(shell=m['silver'],dark=m['dark']),64,.055)
    tail.rotation_euler.x=math.pi/2
    nozzle('Bug Hunter hollow propulsion bell',[(.07,.21),(.18,.24),(.37,.18),(.50,.105)],.56,m)
    support=shell('Bug Hunter annular tail support',[(.40,.35),(.48,.35)],0,math.tau,
        dict(shell=m['silver'],dark=m['dark']),64,.23)
    support.rotation_euler.x=math.pi/2


def meat_eater(m):
    revolved('Meat Eater lower silver pressure casing',[(.66,.29),(.90,.38),(1.45,.43),(2.22,.42),(2.95,.33)],m['silver'])
    band('Meat Eater pale body band',2.55,.402,.20,m['pale'],.045)
    revolved('Meat Eater central silver spine',[(2.90,.16),(4.65,.16)],m['silver'])
    frame('Meat Eater blue open frame sector',[(2.95,.37),(3.18,.42),(3.93,.42),(4.25,.34)],.24,.065,m)
    band('Meat Eater blue lower frame ring',2.99,.38,.10,m['blue'],.12)
    band('Meat Eater blue upper frame ring',4.22,.35,.09,m['blue'],.13)
    revolved('Meat Eater red upper coupling',[(4.20,.25),(4.40,.24),(4.70,.23),(4.84,.27)],m['red'])
    revolved('Meat Eater rounded gray head',[(4.79,.27),(4.96,.39),(5.34,.46),
        (5.77,.43),(6.10,.28),(6.30,.12)],m['silver'])
    band('Meat Eater red tail sleeve',.49,.265,.42,m['red'],.045)
    tail=shell('Meat Eater hollow gray tail seat',[(.43,.29),(.62,.32),(.79,.33)],0,math.tau,
        dict(shell=m['silver'],dark=m['dark']),64,.05)
    tail.rotation_euler.x=math.pi/2
    nozzle('Meat Eater hollow red nozzle',[(.06,.17),(.22,.18),(.48,.11)],.55,m,True)
    support=shell('Meat Eater annular nozzle support',[(.42,.27),(.50,.27)],0,math.tau,
        dict(shell=m['red'],dark=m['dark']),64,.20)
    support.rotation_euler.x=math.pi/2

    # Multi-frame color-region ordering refines the gray head's relative length.
    bpy.context.view_layer.update()
    knots=[(0,0),(.8,.9),(2.95,3.25),(4.25,4.70),(4.79,5.18),(6.31,6.31)]
    for obj in list(bpy.context.collection.objects):
        if obj.type=='MESH':
            inverse=obj.matrix_world.inverted()
            for vertex in obj.data.vertices:
                point=obj.matrix_world @ vertex.co
                point.z=next(b0+(b1-b0)*(point.z-a0)/(a1-a0) for (a0,b0),(a1,b1) in zip(knots,knots[1:]) if a0<=point.z<=a1)
                vertex.co=inverse @ point
    smooth=bpy.data.objects['Meat Eater rounded gray head'].modifiers.new('Rounded interpreted forebody','SUBSURF')
    smooth.levels=2;smooth.render_levels=2
