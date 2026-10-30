"""First independent PH10 spherical/tapered assembly; originals reference-only."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
CORE='Deflector spherical shell'
NOSE='Deflector ribbed taper'
TUBE='Deflector red rear pin'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={CORE:[(y,math.sqrt(.47**2-y*y)) for y in [-.46875+.9375*i/40 for i in range(41)]],NOSE:[(-1.0625,.008),(-1.02,.025),(-.80,.08),(-.55,.16),(-.35,.23),(-.25,.25)],TUBE:[(.43,.035),(.60,.035),(.6875,.025)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES}
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={CORE:(math.pi,.05,.006),NOSE:(math.pi,-.70,.002),TUBE:(0,.59,.001)}
PANELS=[(CORE,-.13,.13,math.pi/2),(CORE,-.13,.13,math.pi*1.5)]
RIBS=[-.94+i*.065 for i in range(8)]
PATCHES=[]
BOSSES=[]
PIPE_ENDPOINTS=[]
SOCKETS={'AlignmentForward':((0,-1.16,0),(0,-1,0))}

def surface(owner,phi,z,offset=0):
    r=profile_radius(PROFILES[owner],z);angle,height,depth=DENTS[owner];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle));r-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));r+=offset
    return LOCATIONS[owner]+ROTATIONS[owner] @ Vector((r*math.cos(phi),r*math.sin(phi),z))


def hull_frame(owner,phi,z):
    obj=bpy.data.objects[owner];p=surface(owner,phi,z);n=ROTATIONS[owner] @ Vector((math.cos(phi),math.sin(phi),0));inv=obj.matrix_world.inverted();hit,p,normal,_=obj.ray_cast(inv @ (p+n*3),(inv.to_3x3() @ -n).normalized());assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ normal).normalized()


def orient(obj,rotation,origin=(0,0,0)):
    for v in obj.data.vertices:v.co=Vector(origin)+rotation @ v.co
    obj.data.update();return obj


def patch(name,owner,z0,z1,phi,width,surface_material,top=.008,back=-.018,support=None):
    spec=dict(name=name,owner=owner,z0=z0,z1=z1,phi=phi,width=width,top=top,back=back,support=support or owner)
    columns=65 if 'dome sector' in name else 17;steps=max(8,math.ceil((z1-z0)/.022));heights=[z0+(z1-z0)*i/steps for i in range(steps+1)]
    for z,_ in PROFILES[owner]:
        if z0<z<z1:heights=[h for h in heights if abs(h-z)>1e-8]+[z]
    heights.sort();height=len(heights);size=columns*height;vertices=[]
    for offset in [top,back]:vertices.extend(surface(owner,phi+width*(-1+2*i/(columns-1)),z,offset) for z in heights for i in range(columns))
    faces=[]
    for row in range(height-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,height)]+list(reversed(range((height-1)*columns,(height-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,height-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]))
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,0);PATCHES.append(spec)
    skin_faces=2*(height-1)*(columns-1)
    for face in data.polygons:face.use_smooth=face.index<skin_faces
    # Preserve the finite edge wall as a sharp boundary of each curved skin.
    uses={}
    for face in data.polygons:
        for edge in face.edge_keys:uses.setdefault(tuple(sorted(edge)),[]).append(face.use_smooth)
    for edge in data.edges:edge.use_edge_sharp=len(set(uses[tuple(sorted(edge.vertices))]))>1
    return obj





def pipe(name,start,end,surface,side):
    a=Vector(start);d=Vector(end);b=Vector((side*.30,.30,-.45));c=Vector((side*.30,.60,-.42))
    points=[a*(1-t)**3+3*b*(1-t)**2*t+3*c*(1-t)*t*t+d*t**3 for t in [i/48 for i in range(49)]]
    count=32;vertices=[];faces=[]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();rotation=tangent.to_track_quat('Z','Y').to_matrix()
        vertices.extend(p+rotation @ Vector((.016*math.cos(j*math.tau/count),.016*math.sin(j*math.tau/count),0)) for j in range(count))
    for i in range(len(points)-1):
        for j in range(count):faces.append((i*count+j,i*count+(j+1)%count,(i+1)*count+(j+1)%count,(i+1)*count+j))
    start=len(vertices);vertices.extend([points[0],points[-1]]);end=(len(points)-1)*count
    faces.extend((start,(j+1)%count,j) for j in range(count));faces.extend((start+1,end+j,end+(j+1)%count) for j in range(count))
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0)
    PIPE_ENDPOINTS.append(dict(name=name,start=list(a),end=list(d)));return obj


def axial(name,y,radius,depth,mat,x=0,z=0,vertices=48):
    return cylinder(name,(x,y,z),radius,depth,mat,vertices,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())


def build():
    PATCHES.clear();BOSSES.clear();PIPE_ENDPOINTS.clear()
    m=dict(hull=material('Deflector | worn warm shell alloy',(.28,.25,.18),.72,.70),red=material('Deflector | worn red rear pin',(.31,.085,.07),.52,.73),copper=material('Deflector | worn copper taper and conduits',(.22,.12,.075),.76,.70),edge=material('Deflector | oxidized service alloy',(.16,.20,.22),.78,.65),dark=material('Deflector | dark service slots',(.012,.016,.018),.40,.80))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['hull' if owner==CORE else 'copper' if owner==NOSE else 'red'],[DENTS[owner]]),Y_AXIS)
    for i,y in enumerate(RIBS):
        rows=[(z,profile_radius(PROFILES[NOSE],z)+.005,profile_radius(PROFILES[NOSE],z)-.008) for z in [y-.006,y+.006]]
        orient(annulus('Deflector taper rib '+str(i),(0,0),rows,m['hull'],(0,y,0)),Y_AXIS)
    box('Deflector rear bracket',(0,.48,0),(.56,.12,.64),m['hull'],.016)
    axial('Deflector rear pin socket',.535,.070,.075,m['edge'])
    for i,side in enumerate([-1,1]):
        pipe('Deflector rear conduit '+str(i),(side*.16,.30,-.27),(side*.20,.47,-.28),m['copper'],side)
        axial('Deflector bracket bolt '+str(i),.546,.024,.040,m['edge'],side*.21,-.25,24)
    bpy.context.view_layer.update()
    for i,(phi,y,radius) in enumerate([(0,0,.075),(math.pi,0,.075),(math.pi/2,-.23,.025),(math.pi*1.5,-.23,.025)]):
        p,n=hull_frame(CORE,phi,y);BOSSES.append(dict(position=list(p),normal=list(n)))
        cylinder('Deflector side boss '+str(i),p+n*.006,radius,.034,m['hull'],48,rotation=n.to_track_quat('Z','Y').to_euler())
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Deflector service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Deflector service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Deflector fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
