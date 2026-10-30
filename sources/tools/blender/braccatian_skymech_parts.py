"""First BR4C station: ribbed axial stack with independently authored lateral modules."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,beam,box,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus

PROFILES={'SkyMech dark axial core':[(-1.5,.30),(-1.25,.34),(-.40,.32),(-.15,.46),(.05,.46),(.1875,.34),(1.125,.34),(1.3125,.46)],
 'SkyMech upper gold dome':[(1.125,.50),(1.3125,.72),(1.5,.77),(1.6875,.69),(1.875,.48),(2.0,.17)],
 'SkyMech lower gold cone':[(-2.125,.08),(-2.0,.20),(-1.75,.53),(-1.5625,.76),(-1.4375,.79),(-1.3125,.60)]}
DENTS={'SkyMech upper gold dome':(-math.pi/2,1.62,.006),'SkyMech lower gold cone':(-math.pi/2,-1.70,.006)}
CAP_BANDS=[('SkyMech upper rose rim','SkyMech upper gold dome',1.42,1.50),('SkyMech lower rose rim','SkyMech lower gold cone',-1.50,-1.38)]
CORE_BANDS=[(.30,.35,.415,.30),(.88,.93,.415,.30),(-1.12,-1.065,.40,.28)]
POD_PROFILE=[(-.1875,.12),(-.125,.36),(-.03125,.49),(.0625,.50),(.125,.44),(.1875,.22)]
POD_FACE=[(.109375,.34),(.125,.35),(.1875,.26),(.21875,.16),(.234375,.10)]
POD_DENT=(-math.pi/2,.12,.003)
POD_RADIUS=1.55
POD_Z=.05
SOCKETS={'AlignmentAxis':((0,0,2.45),(0,0,1))}
PATCHES=[]


def surface(name,phi,z,offset=0):
    radius=profile_radius(PROFILES[name],z)
    if name in DENTS:
        angle,height,depth=DENTS[name];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle))
        radius-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2))
    radius+=offset;return Vector((radius*math.cos(phi),radius*math.sin(phi),z))


def pod_axis(i):return Vector((math.cos(i*math.pi/2),math.sin(i*math.pi/2),0))


def pod_centre(i):return pod_axis(i)*POD_RADIUS+Vector((0,0,POD_Z))


def fit_radial(obj,i):
    obj.location=pod_centre(i);obj.rotation_euler=pod_axis(i).to_track_quat('Z','Y').to_euler();return obj


def patch(name,owner,z0,z1,phi,width,surface_material,top=.008,back=-.018,support=None):
    spec=dict(name=name,owner=owner,z0=z0,z1=z1,phi=phi,width=width,top=top,back=back,support=support or owner)
    columns=17;steps=max(8,math.ceil((z1-z0)/.022));heights=[z0+(z1-z0)*i/steps for i in range(steps+1)]
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
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,0);PATCHES.append(spec);return obj


def build():
    PATCHES.clear()
    m=dict(gold=material('SkyMech | worn gold shell',(.33,.23,.09),.72,.59),hull=material('SkyMech | worn rose copper',(.30,.13,.115),.68,.61),
        edge=material('SkyMech | oxidized service alloy',(.23,.20,.17),.78,.60),dark=material('SkyMech | carbon dark recesses',(.015,.018,.014),.40,.80),amber=material('SkyMech | amber inserts',(.40,.075,.012),.35,.67))
    for name,profile in PROFILES.items():vessel(name,profile,m['dark' if 'core' in name else 'gold'],[DENTS[name]] if name in DENTS else [])
    for name,owner,low,high in CAP_BANDS:
        heights=sorted(set([low,high]+[z for z,_ in PROFILES[owner] if low<z<high]));rows=[(z,profile_radius(PROFILES[owner],z)+.02,profile_radius(PROFILES[owner],z)-.026) for z in heights]
        annulus(name,(0,0),rows,m['hull'],(0,(low+high)/2,0))
    annulus('SkyMech rose equatorial collar',(0,0),[(-.09375,.56,.32),(0,.61,.32),(.09375,.54,.32)],m['hull'],(0,0,0))
    for i,(low,high,outside,inside) in enumerate(CORE_BANDS):annulus('SkyMech core gold band '+str(i),(0,0),[(low,outside,inside),(high,outside,inside)],m['gold'],(0,(low+high)/2,0))
    for i in range(8):
        phi=i*math.tau/8;n=Vector((math.cos(phi),math.sin(phi),0))
        beam('SkyMech upper column rib '+str(i),n*.35+Vector((0,0,.15)),n*.35+Vector((0,0,1.29)),.035,m['hull'])
        beam('SkyMech lower column rib '+str(i),n*.33+Vector((0,0,-1.39)),n*.33+Vector((0,0,-.15)),.035,m['hull'])
    for i in range(4):
        n=pod_axis(i);phi=i*math.pi/2
        fit_radial(vessel('SkyMech rose radial module '+str(i),POD_PROFILE,m['hull'],[POD_DENT]),i)
        fit_radial(vessel('SkyMech gold module face '+str(i),POD_FACE,m['gold'],[]),i)
        heights=sorted(set([-.04,.04]+[z for z,_ in POD_PROFILE if -.04<z<.04]));rows=[(z,profile_radius(POD_PROFILE,z)+.008,profile_radius(POD_PROFILE,z)-.016) for z in heights]
        fit_radial(annulus('SkyMech module gold rim '+str(i),(0,0),rows,m['gold'],(0,0,0)),i)
        cylinder('SkyMech module face fitting '+str(i),pod_centre(i)+n*.24,.05,.04,m['edge'],vertices=32,rotation=n.to_track_quat('Z','Y').to_euler())
        beam('SkyMech radial arm '+str(i),n*.28+Vector((0,0,.05)),n*1.42+Vector((0,0,.05)),.075,m['gold'])
        housing=box('SkyMech arm service housing '+str(i),n*.94+Vector((0,0,.05)),(.50,.19,.20),m['gold'],.01);housing.rotation_euler.z=phi
        inset=box('SkyMech arm dark inset '+str(i),n*.94+Vector((0,0,.152)),(.32,.105,.022),m['dark'],.002);inset.rotation_euler.z=phi
        for j,distance in enumerate([-.11,0,.11]):
            tile=box('SkyMech arm amber tile '+str(i)+' '+str(j),n*(.94+distance)+Vector((0,0,.166)),(.055,.07,.012),m['amber'],.001);tile.rotation_euler.z=phi
    owner='SkyMech upper gold dome';panel='SkyMech upper dark panel'
    patch(panel,owner,1.35,1.49,-math.pi/2,.40,m['dark'])
    for i in range(5):patch('SkyMech upper amber tile '+str(i),owner,1.395,1.455,-math.pi/2+(i-2)*.14,.045,m['amber'],top=.016,back=.003,support=panel)
    beam('SkyMech upper aerial',(0,0,1.97),(0,0,2.45),.012,m['edge'])
    beam('SkyMech lower aerial',(0,0,-2.10),(0,0,-2.50),.010,m['edge'])
    cylinder('SkyMech crown hatch',(0,0,2.005),.13,.03,m['dark'],vertices=64)
    return m
