"""Authored, open-volume scaffold kits; culture prose guides ambiguous details."""
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_refined_rigellian_scaffold import box, tube, share_evaluated_geometry
from build_openfa_assets import material
from terran_light_ship_parts import orient_and_chamfer

STYLES = {
    'terran': dict(main=(.22,.28,.32), trim=(.58,.36,.055), kind='braced steel access gantry', technique='Bolted trusses and removable service decks'),
    'rigellian': dict(main=(.065,.18,.12), trim=(.23,.105,.045), kind='green precision frame', technique='Indexed copper rail clamps'),
    'braccatian': dict(main=(.40,.29,.13), trim=(.16,.095,.045), kind='sandstone-like perforated load screen', technique='Reusable porous mineral-composite cassettes; user material interpretation'),
    'mikotaj': dict(main=(.27,.34,.36), trim=(.075,.18,.10), kind='organic-shaped heavy metallic focus cradle', technique='Ore-like metallic lifting ribs with organic contours; CDB colony materials take precedence over biological appearance'),
    'artemian': dict(main=(.24,.39,.29), trim=(.13,.22,.17), kind='vented matte alloy shell', technique='Segmented advanced-alloy shield petals; CDB metal preference takes precedence over ceramic appearance'),
    'mauna': dict(main=(.17,.21,.235), trim=(.45,.11,.035), kind='utility box gantry', technique='Straight bolted beams and lifting lugs'),
    'achaean': dict(main=(.40,.31,.12), trim=(.13,.075,.028), kind='bamboo-like lashed framework', technique='Reusable composite canes and fibre lashings; user material interpretation'),
}


def empty(name, parent=None, z=0):
    obj=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(obj)
    obj.parent=parent
    obj.location.z=z
    return obj


def surface(culture, kind, texture_root):
    base=STYLES[culture][kind]
    metallic=.58 if kind=='main' else .7
    if culture in ['braccatian','achaean']:metallic=.06 if kind=='main' else .18
    if culture in ['mikotaj','artemian']:metallic=.72 if kind=='main' else .58
    result=material(f'{culture} scaffold {kind}',base,metallic,.62)
    nodes=result.node_tree.nodes
    shader=nodes.get('Principled BSDF')
    for suffix, input_name, space in [('colour','Base Color','sRGB'),('roughness','Roughness','Non-Color')]:
        texture=nodes.new('ShaderNodeTexImage')
        texture.image=bpy.data.images.load(str(texture_root/culture/f'{kind}-{suffix}.png'))
        texture.image.colorspace_settings.name=space
        texture.image.pack()
        result.node_tree.links.new(texture.outputs['Color'],shader.inputs[input_name])
    return result


class Kit:
    def __init__(self,culture,size,pitch,capacity,main,trim):
        self.culture=culture
        self.size=size
        self.half=size*.45
        self.pitch=pitch
        self.capacity=capacity
        self.unit=pitch/capacity
        self.main=main
        self.trim=trim
        self.objects=[]

    def tag(self,obj,parent,role):
        obj.parent=parent
        obj['scaffold_role']=role
        obj['reveal_visible']=role not in ['temporary-crown','interior-shoring']
        self.objects.append(obj)
        return obj

    def block(self,name,centre,dims,surface,parent,role='perimeter',bevel=.006):
        obj=box(name,centre,dims,surface,bevel)
        # A shallow handling dent on a corner; endpoints/sockets remain exact.
        if len(obj.data.vertices)==8:
            obj.data.vertices[6].co.x-=min(dims)*.035
            obj.data.vertices[6].co.y-=min(dims)*.025
        return self.tag(obj,parent,role)

    def beam(self,name,a,b,width,surface,parent,role='perimeter'):
        a,b=Vector(a),Vector(b)
        obj=self.block(name,(a+b)/2,(width,width,(b-a).length),surface,parent,role)
        obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
        return obj

    def rod(self,name,a,b,width,surface,parent,role='perimeter',organic=False):
        a,b=Vector(a),Vector(b);height=(b-a).length
        vertices=[];faces=[];segments=10;rings=5
        for row in range(rings):
            t=row/(rings-1)
            bulge=1+(.24 if organic else .055)*math.sin(math.pi*t)
            for i in range(segments):
                angle=2*math.pi*i/segments
                radius=width*.5*bulge*(.95 if row==2 and i==3 else 1)
                vertices.append((radius*math.cos(angle),radius*math.sin(angle),(t-.5)*height))
        for row in range(rings-1):
            for i in range(segments):
                j=(i+1)%segments
                faces.append((row*segments+i,row*segments+j,(row+1)*segments+j,(row+1)*segments+i))
        faces.extend([tuple(reversed(range(segments))),tuple((rings-1)*segments+i for i in range(segments))])
        mesh=bpy.data.meshes.new(name+' curved section');mesh.from_pydata(vertices,[],faces);mesh.update()
        uv=mesh.uv_layers.new(name='Authored material wear')
        for face in mesh.polygons:
            face.use_smooth=len(face.vertices)==4
            for index in face.loop_indices:
                vertex=mesh.vertices[mesh.loops[index].vertex_index].co
                uv.data[index].uv=((math.atan2(vertex.y,vertex.x)/(2*math.pi))%1,vertex.z/height+.5)
        mesh.materials.append(surface)
        obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
        obj.location=(a+b)/2;obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
        return self.tag(obj,parent,role)

    def side(self,side,t,z,inset=0):
        h=self.half-inset
        return [(t,-h,z),(h,t,z),(-t,h,z),(-h,-t,z)][side]

    def rail(self,name,side,a,b,z,width,surface,parent,role='perimeter'):
        return self.beam(name,self.side(side,a,z),self.side(side,b,z),width,surface,parent,role)

    def arch(self,name,side,left,right,bottom,rise,width,surface,parent):
        # Barrel arch with planar rise; its outer support line stays on the perimeter.
        points=[self.side(side,left+(right-left)*i/8,bottom+rise*math.sin(math.pi*i/8)) for i in range(9)]
        for i in range(8):
            method=self.rod if self.culture=='achaean' else self.beam
            method(f'{name} segment {i}',points[i],points[i+1],width,surface,parent)

    def footing(self,root):
        for i,(x,y) in enumerate([(-self.half,-self.half),(self.half,-self.half),(self.half,self.half),(-self.half,self.half)]):
            self.block(f'Foundation {i}',(x,y,.022),(.15,.15,.044),self.trim,root,'foundation')
            for n in [-1,1]:
                self.block(f'Foundation anchor {i}-{n}',(x+n*.048,y,.049),(.018,.025,.013),self.main,root,'foundation',.002)

    def tier(self,root,level,frame):
        tier=empty(f'Tier {level}',root,level*self.pitch)
        tier['stage_frame']=frame
        empty(f'Tier {level} BottomSocket',tier)
        empty(f'Tier {level} TopSocket',tier,self.pitch)
        h=frame*self.unit
        count=max(2,self.size*2)
        step=2*self.half/count
        post_width=.065 if self.culture in ['terran','rigellian','achaean'] else .09
        for side in range(4):
            for n in range(count):
                t=-self.half+n*step
                x,y,_=self.side(side,t,0)
                if self.culture in ['achaean','mikotaj']:
                    self.rod(f'Tier {level} side {side} post {n}',(x,y,0),(x,y,h),post_width,self.main,tier,organic=self.culture=='mikotaj')
                else:
                    post=tube(f'Tier {level} side {side} post {n}',(x,y,h/2),post_width,post_width*.7,h,self.main)
                    self.tag(post,tier,'perimeter')
                if level:
                    self.tag(tube(f'Tier {level} sleeve {side}-{n}',(x,y,.018),post_width+.026,post_width+.004,.065,self.trim),tier,'joint')
                for row in range(frame):
                    z=(row+.5)*self.unit
                    self.tag(tube(f'Tier {level} clamp {side}-{n}-{row}',(x,y,z),post_width+.018,post_width+.002,.032,self.trim),tier,'perimeter')
            for row in range(frame):
                z0=row*self.unit
                z1=(row+1)*self.unit
                for n in range(count):
                    a=-self.half+n*step
                    b=a+step
                    label=f'Tier {level} bay {side}-{row}-{n}'
                    self.rail(label+' sill',side,a,b,z0+.04,.038,self.main,tier)
                    if self.culture=='terran':
                        self.beam(label+' diagonal',self.side(side,a+.035,z0+.045),self.side(side,b-.035,z1-.025),.024,self.main,tier)
                        self.rail(label+' service deck',side,a+.02,b-.02,z0+.045,.075,self.trim,tier)
                    elif self.culture=='rigellian':
                        self.rail(label+' copper tie',side,a,b,z0+self.unit*.55,.047,self.trim,tier)
                    elif self.culture=='braccatian':
                        # Perforated cassette: rails and broad mullions leave real openings.
                        self.rail(label+' cassette top',side,a,b,z1-.035,.065,self.main,tier)
                        self.rail(label+' cassette belt',side,a,b,z0+self.unit*.45,.052,self.main,tier)
                        for q in [.25,.75]:
                            self.beam(label+f' broad mullion {q}',self.side(side,a+step*q,z0+.04),self.side(side,a+step*q,z1-.035),.062,self.main,tier)
                        self.block(label+' clasp',self.side(side,(a+b)/2,z0+self.unit*.45),(.055,.055,.055),self.trim,tier)
                    elif self.culture=='mikotaj':
                        # Organic contours with the heavy ore-like colony metal
                        # explicitly required by the CDB architecture record.
                        for q in [.20,.50,.80]:
                            points=[self.side(side,a+step*q+math.sin(math.pi*k/4)*step*.08,z0+.035+(self.unit-.06)*k/4) for k in range(5)]
                            for k in range(4):
                                self.rod(label+f' organic rib {q}-{k}',points[k],points[k+1],.075,self.main,tier,organic=True)
                        self.arch(label+' grown collar',side,a,b,z0+self.unit*.5,self.unit*.35,.055,self.trim,tier)
                        self.block(label+' field index',self.side(side,(a+b)/2,z1-.022),(.037,.037,.027),self.trim,tier)
                    elif self.culture=='artemian':
                        # Matte metal segments with genuine vent slots;
                        # an open crown avoids repeated closed roofs.
                        for q in [.12,.40,.68,.94]:
                            self.beam(label+f' shield edge {q}',self.side(side,a+step*q,z0+.04),self.side(side,a+step*q,z1-.015),.055,self.main,tier)
                        self.rail(label+' alloy belt',side,a,b,z0+self.unit*.68,.075,self.trim,tier)
                        self.rail(label+' shield lower edge',side,a,b,z0+.045,.085,self.main,tier)
                    elif self.culture=='mauna':
                        self.rail(label+' box girder',side,a,b,z1-.04,.065,self.main,tier)
                        self.beam(label+' vertical lifting bar',self.side(side,(a+b)/2,z0+.04),self.side(side,(a+b)/2,z1-.04),.04,self.trim,tier)
                        self.block(label+' lifting lug',self.side(side,a,z0+self.unit*.55),(.065,.065,.06),self.trim,tier)
                    elif self.culture=='achaean':
                        self.arch(label+' barrel arch',side,a+.025,b-.025,z0+.04,self.unit*.76,.035,self.main,tier)
                        self.rod(label+' cane ledger',self.side(side,a,z0+self.unit*.22),self.side(side,b,z0+self.unit*.22),.04,self.main,tier)
                        for fraction in [.18,.78]:
                            for band in range(3):
                                zz=z0+self.unit*fraction+band*.009
                                self.rod(label+f' fibre binding {fraction}-{band}',self.side(side,a-.049,zz),self.side(side,a+.049,zz+.015),.012,self.trim,tier)
        return tier

    def crown(self,root,stage):
        if self.culture not in ['artemian','mikotaj','achaean']:
            return
        z=stage*self.unit
        # Temporary crown belongs only to the top assembly, never to every tier.
        crown=empty('Temporary crown',root)
        for side in range(4):
            count=max(2,self.size*2)
            for n in range(count):
                t=-self.half+(n+.5)*2*self.half/count
                start=self.side(side,t,z-.025)
                end=self.side(side,t*.88,z+.10,self.size*.10)
                if self.culture=='artemian':
                    a,b=Vector(start),Vector(end)
                    plate=self.block(f'Crown alloy petal {side}-{n}',(a+b)/2,(self.size*.9/count*.76,.026,(b-a).length),self.main,crown,'temporary-crown')
                    plate.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
                else:
                    self.beam(f'Crown petal {side}-{n}',start,end,.065,self.main,crown,'temporary-crown')
                if self.culture=='mikotaj':
                    self.block(f'Crown focus index {side}-{n}',end,(.065,.065,.035),self.trim,crown,'temporary-crown')

    def finish(self):
        orient_and_chamfer(self.objects)
        bpy.context.view_layer.update()
        return share_evaluated_geometry(self.objects)
