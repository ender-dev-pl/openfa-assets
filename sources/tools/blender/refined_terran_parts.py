"""Manufactured geometry vocabulary for independently authored Terran detail studies."""
import math

import bpy
from mathutils import Vector

from build_openfa_assets import box, beam, material, finish
from build_legacy_buildings import pipe_network


class Detailer:
    def __init__(self, collection):
        self.collection = collection
        self.head = bpy.data.objects.get('DirectionalHead')
        self.base = bpy.data.objects.get('StaticBase')
        self.role = 'base'
        self.created = []
        self.features = []
        colours = {
            'alloy':((0.24,0.29,0.27),0.65,0.40),
            'edge':((0.34,0.39,0.37),0.72,0.32),
            'bronze':((0.34,0.23,0.105),0.72,0.39),
            'gold':((0.48,0.36,0.18),0.70,0.34),
            'dark':((0.025,0.035,0.034),0.40,0.54),
            'violet':((0.16,0.14,0.23),0.58,0.38),
            'red':((0.34,0.065,0.045),0.42,0.44),
            'blue':((0.035,0.15,0.22),0.55,0.29),
            'glass':((0.055,0.16,0.17),0.45,0.23),
            'light':((0.70,0.63,0.34),0.30,0.30),
        }
        self.m = {name:material('Refined | '+name,*values) for name,values in colours.items()}
        self.m['light'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0.65

    def keep(self, obj):
        obj['detail_role'] = self.role
        parent = self.head if self.role == 'head' else self.base
        if parent:
            bpy.context.view_layer.update()
            world = obj.matrix_world.copy()
            obj.parent = parent
            obj.matrix_world = world
        self.created.append(obj)
        return obj

    def box(self, name, p, size, mat='alloy', rotation=(0,0,0), bevel=0.009):
        obj = box(name,p,size,self.m[mat],bevel)
        obj.rotation_euler = rotation
        # box() starts without a parent; set orientation before preserving world transform.
        return self.keep(obj)

    def rod(self, name, a, b, radius=0.018, mat='edge'):
        return self.keep(beam(name,a,b,radius,self.m[mat]))

    def pipe(self, name, points, radius=0.025, mat='edge'):
        return self.keep(pipe_network(name,[points],radius,self.m[mat]))

    def ring(self, name, p, radius, tube=0.016, mat='edge', normal=(0,0,1)):
        bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=8,
            location=p,major_radius=radius,minor_radius=tube)
        obj = bpy.context.object
        obj.rotation_euler = Vector(normal).to_track_quat('Z','Y').to_euler()
        finish(obj,name,self.m[mat],0)
        for face in obj.data.polygons:
            face.use_smooth = True
        return self.keep(obj)

    def disc(self, name, p, radius, height=0.035, mat='edge', normal=(0,0,1)):
        direction = Vector(normal).normalized()*height/2
        return self.rod(name,Vector(p)-direction,Vector(p)+direction,radius,mat)

    def shell(self, name, profile, count=20, mat='alloy', centre=(0,0), gap=0.022):
        """Closed individually spaced armour panels, with real thickness and material variation."""
        vertices,faces,indices = [],[],[]
        for band,((z0,r0),(z1,r1)) in enumerate(zip(profile,profile[1:])):
            if z1-z0 < 0.012:
                continue
            for index in range(count):
                a0 = math.tau*(index+gap)/count
                a1 = math.tau*(index+1-gap)/count
                zs = (z0+0.004,z1-0.004)
                rs = (r0+0.013,r1+0.013)
                offset = len(vertices)
                for inset in [0,0.012]:
                    for z,radius in zip(zs,rs):
                        for angle in [a0,a1]:
                            vertices.append((centre[0]+(radius-inset)*math.cos(angle),
                                centre[1]+(radius-inset)*math.sin(angle),z))
                faces.extend(tuple(offset+i for i in face) for face in
                    [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)])
                indices.extend([(index+band*3)%3]*6)
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(vertices,[],faces)
        mesh.update()
        obj = bpy.data.objects.new(name,mesh)
        self.collection.objects.link(obj)
        original = self.m[mat]
        for factor in [0.94,1.0,1.05]:
            surface = original.copy()
            surface.name = name+' | plate tone '+str(factor)
            colour = original.diffuse_color
            rgb = [min(1,c*factor) for c in colour[:3]]
            surface.diffuse_color = (*rgb,1)
            surface.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*rgb,1)
            mesh.materials.append(surface)
        for polygon,index in zip(mesh.polygons,indices):
            polygon.material_index = index
        return self.keep(obj)

    def dome(self, name, r, h, z, mat='alloy', centre=(0,0), rings=5, sectors=24):
        # Curved tiles must follow the ellipsoid: flat chords intersect the smooth underlay.
        vertices,faces,tones=[],[],[]
        steps=6
        for band in range(rings):
            for sector in range(sectors):
                offset=len(vertices)
                for row in range(steps+1):
                    phi=(band+.012+(1-.024)*row/steps)*math.pi/(2*rings)
                    for column in range(steps+1):
                        theta=(sector+.022+(1-.044)*column/steps)*math.tau/sectors
                        vertices.append((centre[0]+(r+.016)*math.cos(phi)*math.cos(theta),
                            centre[1]+(r+.016)*math.cos(phi)*math.sin(theta),z+(h+.016)*math.sin(phi)))
                for row in range(steps):
                    for column in range(steps):
                        a=offset+row*(steps+1)+column
                        faces.append((a,a+1,a+steps+2,a+steps+1))
                        tones.append((band+sector)%3)
        mesh=bpy.data.meshes.new(name)
        mesh.from_pydata(vertices,[],faces)
        mesh.update()
        obj=bpy.data.objects.new(name,mesh)
        self.collection.objects.link(obj)
        for factor in [.96,1,1.035]:
            surface=self.m[mat].copy()
            rgb=tuple(c*factor for c in surface.diffuse_color[:3])
            surface.diffuse_color=(*rgb,1)
            surface.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*rgb,1)
            mesh.materials.append(surface)
        for face,tone in zip(mesh.polygons,tones):
            face.material_index=tone
            face.use_smooth=True
        solid=obj.modifiers.new('Individual tile skin thickness','SOLIDIFY')
        solid.thickness=.012
        solid.offset=-1
        return self.keep(obj)

    def bolts(self, name, r, z, count=16, centre=(0,0), size=0.022):
        for index in range(count):
            angle = index*math.tau/count
            self.disc(name,(centre[0]+r*math.cos(angle),centre[1]+r*math.sin(angle),z),size,.018)

    def hatch(self, name, p, radius=.20, normal=(0,0,1), mat='alloy'):
        self.disc(name+' dark gasket',p,radius+.025,.035,'dark',normal)
        self.disc(name+' lid',Vector(p)+Vector(normal)*.025,radius,.035,mat,normal)
        self.ring(name+' rim',Vector(p)+Vector(normal)*.046,radius,.012,'edge',normal)
        tangent = Vector(normal).cross(Vector((0,1,0)))
        if tangent.length < .1:
            tangent = Vector((1,0,0))
        tangent.normalize()
        centre = Vector(p)+Vector(normal)*.075
        self.rod(name+' locking handle',centre-tangent*radius*.30,centre+tangent*radius*.30,.018,'dark')

    def vent(self, name, p, width=.4, height=.3, count=6, rotation=0):
        self.box(name+' recessed housing',p,(width,.045,height),'dark',(0,0,rotation))
        tangent = Vector((math.cos(rotation),math.sin(rotation),0))
        centre = Vector(p)
        front = Vector((math.sin(rotation),-math.cos(rotation),0))*.032
        for index in range(count):
            z = -height*.38+height*.76*index/max(1,count-1)
            a = centre-tangent*width*.43+front+Vector((0,0,z))
            b = centre+tangent*width*.43+front+Vector((0,0,z))
            self.rod(name+' louvre',a,b,.011,'edge')

    def radial_windows(self, radius, z, count=20, centre=(0,0), height=.075):
        for index in range(count):
            a = math.tau*index/count
            p = (centre[0]+radius*math.cos(a),centre[1]+radius*math.sin(a),z)
            self.box('Flush window metal frame',p,(.14,.026,height+.035),'dark',(0,0,a+math.pi/2))
            p = (centre[0]+(radius+.016)*math.cos(a),centre[1]+(radius+.016)*math.sin(a),z)
            self.box('Glazed window inset',p,(.105,.012,height),'light',(0,0,a+math.pi/2),.002)

    def ladder(self, x, y, z0, z1, width=.17):
        for dx in [-width/2,width/2]:
            self.rod('Service ladder rail',(x+dx,y,z0),(x+dx,y,z1),.013)
        for index in range(int((z1-z0)/.14)+1):
            z = z0+index*.14
            self.rod('Service ladder rung',(x-width/2,y,z),(x+width/2,y,z),.012)

    def roof_rail(self, x0, x1, y, z):
        for i in range(6):
            x = x0+(x1-x0)*i/5
            self.rod('Safety stanchion',(x,y,z),(x,y,z+.18),.012)
        self.rod('Safety handrail',(x0,y,z+.18),(x1,y,z+.18),.014)

    def feature(self, text):
        self.features.append(text)


def reduce_toy_materials():
    """Use subdued manufactured metal on the coarse underlays, without external textures."""
    for surface in list(bpy.data.materials):
        if not surface.use_nodes:
            continue
        shader = surface.node_tree.nodes.get('Principled BSDF')
        if not shader:
            continue
        name = surface.name.lower()
        colour = shader.inputs['Base Color'].default_value[:3]
        if any(word in name for word in ['light','window','emission']):
            continue
        grey = sum(colour)/3
        rgb = tuple(c*.72+grey*.18 for c in colour)
        shader.inputs['Base Color'].default_value = (*rgb,1)
        surface.diffuse_color = (*rgb,1)
        shader.inputs['Metallic'].default_value = .63
        shader.inputs['Roughness'].default_value = .39
