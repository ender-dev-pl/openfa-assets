"""Independent surface construction for PS01/PS02 reference-based ship studies."""
import math

import bmesh
import bpy
from mathutils import Vector

from build_openfa_assets import beam,box,cylinder,finish,material
from build_assault_fighter import nozzle,plate


def palette():
    return dict(hull=material('Terran | violet titanium',(.12,.11,.18),.55,.43),
                panel=material('Terran | warm service alloy',(.22,.20,.28),.55,.40),
                red=material('Terran | vermilion bands',(.48,.018,.012),.35,.40),
                edge=material('Terran | machined titanium',(.32,.33,.39),.7,.32),
                dark=material('Terran | deep graphite',(.012,.014,.022),.4,.53),
                gold=material('Terran | bronze thermal liner',(.44,.25,.07),.75,.36),
                glow=material('Terran | amber standby lamp',(.9,.19,.018),.1,.4,.5))


def loft(name,sections,surface,rings=32):
    # Sections: Y, half width, centre Z, half height. Elliptical rings keep
    # a deliberate cross-section progression rather than scaled sphere proxies.
    vertices=[(w*math.cos(i*math.tau/rings),y,z+h*math.sin(i*math.tau/rings))
              for y,w,z,h in sections for i in range(rings)]
    faces=[tuple(reversed(range(rings))),tuple(range((len(sections)-1)*rings,len(sections)*rings))]
    faces += [(j*rings+i,j*rings+(i+1)%rings,(j+1)*rings+(i+1)%rings,(j+1)*rings+i)
              for j in range(len(sections)-1) for i in range(rings)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj,name,surface,0)
    for polygon in mesh.polygons:
        polygon.use_smooth=len(polygon.vertices)==4
    return obj


def fastener(position,m):
    cylinder('Captive service fastener',position,.018,.012,m['edge'],vertices=8)


def scoop(name,position,size,m):
    x,y,z=position
    w,d,h=size
    box(name+' inset graphite',(x,y,z),(w,d,h),m['dark'],.006)
    for i in range(6):
        box(name+' exchanger fin',(x,y-d*.4+i*d*.16,z+h*.6),(w*.84,.018,.013),m['edge'],.002)


def surface_point(sections,y,u,lift=0):
    for a,b in zip(sections,sections[1:]):
        if a[0]<=y<=b[0]:
            t=(y-a[0])/(b[0]-a[0])
            w,z,h=[a[i]+(b[i]-a[i])*t for i in [1,2,3]]
            return (w*u,y,z+h*math.sqrt(max(0,1-u*u))+lift)
    raise ValueError(y)


def skin_patch(name,sections,y0,y1,u0,u1,surface):
    # Thin solid patch follows elliptical pressure skin in both directions.
    # Multiple transverse segments prevent flat strips cutting through the dome.
    top=[surface_point(sections,y,u0+(u1-u0)*i/12,.009)
         for y in [y0,(y0+y1)/2,y1] for i in range(13)]
    vertices=top+[(x,y,z-.018) for x,y,z in top]
    faces=[]
    for row in range(2):
        for i in range(12):
            p=row*13+i
            faces += [(p,p+1,p+14,p+13),(p+39,p+52,p+53,p+40)]
    border=list(range(13))+[25,38]+list(range(37,25,-1))+[13]
    faces += [(a,a+39,b+39,b) for a,b in zip(border,border[1:]+border[:1])]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj,name,surface,0)
    return obj


def wing(sign,m):
    # Two swept rear arms, not transverse aircraft wings. Their inner edges
    # diverge from a short central body to leave the source's deep Y-shaped bay.
    stations=[(.36,-.20,.48,.12),(.55,-.04,1.35,.12),(.75,.10,2.15,.11),
              (.95,.27,2.72,.10),(1.50,.88,2.72,.06),
              (2.25,1.55,2.72,.02),(2.48,1.80,2.72,.01),(2.65,2.01,2.55,0)]
    def half_height(x):
        return .28-(x-.36)/2.29*.16
    vertices=[]
    for x,leading,trailing,z in stations:
        h=half_height(x)
        vertices += [(sign*x,leading,z+h),(sign*x,trailing,z+h),
                     (sign*x,trailing,z-h),(sign*x,leading,z-h)]
    last=(len(stations)-1)*4
    faces=[(3,2,1,0),tuple(range(last,last+4))]
    faces += [(j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i) for j in range(len(stations)-1) for i in range(4)]
    mesh=bpy.data.meshes.new('Swept wing spar skin')
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new('Swept structural wing',mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj,obj.name,m['hull'],.012)
    def interp(x,t):
        for i in range(len(stations)-1):
            a,b=stations[i:i+2]
            if a[0]<=x<=b[0]:
                u=(x-a[0])/(b[0]-a[0])
                leading=a[1]+(b[1]-a[1])*u
                trailing=a[2]+(b[2]-a[2])*u
                return (sign*x,leading+(trailing-leading)*t,a[3]+(b[3]-a[3])*u+half_height(x)+.010)
        raise ValueError(x)
    for i,(lo,hi) in enumerate([(1.08,1.48),(1.50,1.96),(1.98,2.43)]):
        for t0,t1 in [(0.08,.68),(.72,.94)]:
            points=[interp(lo,t0),interp(hi,t0),interp(hi,t1),interp(lo,t1)]
            plate('Segmented wing identification enamel' if t0<.1 else 'Wing trailing service panel',
                  points,.015,m['red'] if t0<.1 and i!=1 else m['panel'],.003)
        for t in [.15,.88]:
            fastener(interp((lo+hi)/2,t),m)
    for lo,hi in [(.50,.90),(.90,1.50),(1.50,2.25),(2.25,2.52)]:
        beam('Swept leading edge rail',interp(lo,.015),interp(hi,.015),.018,m['edge'])
        beam('Y notch inner edge rail',interp(lo,.985),interp(hi,.985),.014,m['hull'])


def eagle(m):
    loft('Eagle continuous pressure hull',[(-2.33,.025,.02,.025),(-1.95,.24,.07,.10),
         (-1.35,.51,.12,.25),(-.55,.68,.14,.38),(.10,.64,.14,.40),(.42,.47,.13,.30),
         (.55,.12,.10,.10),(.60,.025,.10,.025)],m['hull'])
    spine=[(-1.40,.08,.25,.03),(-.90,.25,.36,.09),
           (-.20,.30,.41,.13),(.18,.24,.42,.11),(.46,.07,.31,.03)]
    spine=[(y,w,z+.11,h) for y,w,z,h in spine]
    loft('Eagle dorsal service spine',spine,m['panel'])
    for sign in [-1,1]:
        wing(sign,m)
        drive=loft('Eagle underslung drive',[(-.1,.12,-.10,.12),(.35,.20,-.12,.17),(.94,.17,-.11,.14)],m['hull'])
        drive.location.x=sign*.53
        nozzle('Eagle drive '+str(sign),sign*.53,.91,-.11,.145,m)
        scoop('Wing root cooling pack',(sign*.68,.40,.39),(.23,.30,.025),m)
        for y in [-1.2,-.9,-.6]:
            beam('Eagle longitudinal hull seam',(sign*.26,y,.27),(sign*.36,y+.18,.32),.005,m['dark'])
        for y in [-.35,-.05,.18]:
            fastener(surface_point(spine,y,sign*.67,.006),m)
        box('Eagle wingtip navigation lamp',(sign*2.45,2.56,.075),(.07,.035,.028),m['glow'],.006)
    cylinder('Eagle dorsal inspection hatch',(0,.15,.65),.14,.018,m['hull'],vertices=32)
    for i in range(5):
        box('Eagle aft spine radiator',(0,-.35+i*.06,.658),(.20,.018,.02),m['dark'],.002)
    beam('Eagle nose sensor',(0,-2.25,.04),(0,-2.48,.04),.015,m['edge'])
    cylinder('Eagle nose lamp',(0,-2.28,.075),.027,.018,m['glow'],vertices=16)


def scout(m):
    fan=[(-1.30,.18,.02,.05),(-1.02,.62,.05,.10),
         (-.65,1.08,.08,.16),(-.10,1.48,.10,.22),(.55,1.80,.08,.25),
         (1.25,1.93,.04,.22),(1.78,1.78,.02,.17),(1.88,1.55,.02,.13)]
    loft('Scout fan pressure hull',fan,m['hull'],48)
    # Source-backed long raised oval crown; authored elliptical section dimensions.
    crown=[(-1.02,.03,.13,.03),(-.72,.32,.23,.13),
         (-.12,.64,.34,.24),(.60,.77,.36,.27),(1.18,.58,.30,.22),
         (1.56,.22,.16,.10),(1.62,.04,.12,.03)]
    crown_obj=loft('Scout raised oval crown',crown,m['panel'],48)
    # Inventory rotation resolves a large dark inset, not a solid convex dome.
    # Hidden equipment within it remains independently authored interpretation.
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=1,depth=1.0,location=(0,.30,.92))
    cutter=bpy.context.object
    cutter.name='Temporary oval crown cavity cutter'
    cutter.scale=(.49,.82,1)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.context.view_layer.objects.active=crown_obj
    boolean=crown_obj.modifiers.new('Actual recessed oval equipment well','BOOLEAN')
    boolean.operation='DIFFERENCE'
    boolean.solver='EXACT'
    boolean.object=cutter
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    floor=cylinder('Scout recessed oval bay floor',(0,.30,.427),1,.012,m['dark'],vertices=96)
    floor.scale=(.475,.79,1)
    for y in [-.28,.12,.52,.92]:
        box('Scout inset equipment cartridge',(0,y,.444),(.32,.24,.025),m['hull'],.008)
        for i in range(4):
            box('Scout inset cartridge cooling slot',(0,y-.075+i*.05,.46),(.23,.012,.008),m['dark'],.002)
    for sign in [-1,1]:
        for y in [-.30,-.10,.10,.30,.50,.70,.90]:
            # Silver blocks correspond to the bright inner edge strip; dimensions authored.
            x=sign*.49*math.sqrt(max(0,1-((y-.30)/.82)**2))
            block=box('Scout inner rim silver element',(x,y,.49),(.055,.12,.045),m['edge'],.007)
            block.rotation_euler.z=-sign*math.atan2((y-.26)*.24,1.02)
    for sign in [-1,1]:
        # Curved red belt is segmented along the fan's outer shoulder.
        for a,b in zip([-.98,-.62,-.10,.54,1.18],[ -.62,-.10,.54,1.18,1.70]):
            skin_patch('Scout conformal red shoulder belt',fan,a+.006,b-.006,sign*.80,sign*.94,m['red'])
            skin_patch('Scout conformal silver rail',fan,a+.006,b-.006,sign*.76,sign*.785,m['edge'])
        nozzle('Scout main drive '+str(sign),sign*1.08,1.83,.015,.22,m)
        for i in range(7):
            x=sign*(.82+i*.095)
            box('Scout aft cooling louvre',(x,1.38,.19),(.035,.28,.018),m['dark'],.003)
        for y in [-.05,.40,.85]:
            skin_patch('Scout side equipment access cover',fan,y,y+.29,sign*.45,sign*.70,m['panel'])
            fastener(surface_point(fan,y+.14,sign*.65,.018),m)
        # Two clear antenna bulbs beside the neck are visible in the rotation.
        beam('Scout forward antenna mast',(sign*.52,-.96,.14),(sign*.62,-1.06,.44),.021,m['edge'])
        cylinder('Scout antenna cap',(sign*.62,-1.06,.46),.048,.07,m['gold'],vertices=16)
        beam('Scout neck side outrigger',(sign*.30,-1.20,.05),(sign*.44,-1.45,.06),.055,m['hull'])
    loft('Scout recessed neck',[(-1.80,.20,.02,.08),(-1.20,.29,.04,.09)],m['dark'])
    pod=[(-2.40,.025,.02,.025),(-2.22,.21,.03,.08),
         (-1.92,.37,.06,.16),(-1.65,.30,.07,.13),(-1.55,.13,.06,.07)]
    loft('Scout separate forward sensor pod',pod,m['hull'])
    skin_patch('Scout conformal nose service plate',pod,-2.12,-1.82,-.52,.52,m['panel'])
    beam('Scout forward whisker',(0,-2.36,.03),(0,-2.58,.03),.012,m['edge'])
    # Narrow side covers follow the rim, leaving the central well unobstructed.
    for y in [-.05,.35,.75]:
        for sign in [-1,1]:
            skin_patch('Scout conformal crown rim cover',crown,y,y+.20,sign*.84,sign*.97,m['hull'])
            fastener(surface_point(crown,y+.10,sign*.91,.018),m)


def orient_and_chamfer(meshes):
    for obj in meshes:
        extent=[max(v.co[a] for v in obj.data.vertices)-min(v.co[a] for v in obj.data.vertices) for a in range(3)]
        for modifier in obj.modifiers:
            if modifier.type=='BEVEL':
                modifier.width=min(modifier.width,min(extent)*.15)
        bm=bmesh.new()
        bm.from_mesh(obj.data)
        if obj.name=='Scout raised oval crown':
            # The cutter crosses section boundaries. Resolve its large Boolean
            # faces here, removing sub-micron slivers before GLB triangulation.
            bmesh.ops.triangulate(bm,faces=list(bm.faces))
            bmesh.ops.dissolve_degenerate(bm,dist=.00001,edges=list(bm.edges))
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        if all(edge.is_manifold for edge in bm.edges) and bm.calc_volume(signed=True)<0:
            bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
