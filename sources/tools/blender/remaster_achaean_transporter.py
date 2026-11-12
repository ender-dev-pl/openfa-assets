"""AC2C remaster: full warm hull and two open upright crescents, issue 234.

Legacy headings/concept constrain visible form. Hidden service structures,
mechanical details and exact scale are authored; no weapon sockets are calibrated.
Run Blender --background --python-exit-code 1 --python this-file -- [--no-render].
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector,Matrix

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'sources/objects/achaean/dedicated-ore-transporter'
MEDIA=ROOT/'gallery/media/objects/achaean/dedicated-ore-transporter'
ID='openfa:ship/achaean/dedicated-ore-transporter'
GROUPS={}
TAU=math.tau
# y, half-width, half-height: full transport body, not a thin generic cone.
PROFILE=[(-3.02,.055,.050),(-2.70,.17,.14),(-2.20,.34,.25),(-1.65,.63,.46),
         (-1.0,.86,.63),(-.30,.94,.70),(.40,.85,.62),(1.0,.58,.44),
         (1.60,.31,.25),(2.10,.14,.13),(2.64,.062,.055)]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(group,vertices,faces,tile):
    row=GROUPS.setdefault(group,{'v':[],'f':[],'t':[],'chart':[]});offset=len(row['v'])
    row['v'].extend(vertices);row['f'].extend(tuple(offset+i for i in f) for f in faces);row['t'].extend([tile]*len(faces))
    low=tuple(min(p[a] for p in vertices) for a in range(3));high=tuple(max(p[a] for p in vertices) for a in range(3))
    row['chart'].extend([(low,high)]*len(faces))


def box(group,centre,size,tile=2,bevel=.018,rotation=None):
    a,b,h=[s/2 for s in size];c=min(bevel,a*.3,b*.3,h*.35)
    vs=[]
    for z,inset in [(-h,c),(-h+c,0),(h-c,0),(h,c)]:
        aa,bb=a-inset,b-inset;cut=min(c,aa*.3,bb*.3)
        for x,y in [(-aa+cut,-bb),(aa-cut,-bb),(aa,-bb+cut),(aa,bb-cut),
                    (aa-cut,bb),(-aa+cut,bb),(-aa,bb-cut),(-aa,-bb+cut)]:
            v=Vector((x,y,z));v=rotation@v if rotation else v;vs.append(tuple(Vector(centre)+v))
    fs=[tuple(range(7,-1,-1)),tuple(range(24,32))]
    fs.extend((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i) for j in range(3) for i in range(8))
    emit(group,vs,fs,tile)


def rod(group,start,end,r,tile=2,n=12):
    axis=Vector(end)-Vector(start);q=axis.to_track_quat('Z','Y')
    vs=[tuple(Vector(p)+q@Vector((r*math.cos(TAU*i/n),r*math.sin(TAU*i/n),0))) for p in [start,end] for i in range(n)]
    emit(group,vs,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],tile)


def section(y):
    for (ya,wa,ha),(yb,wb,hb) in zip(PROFILE,PROFILE[1:]):
        if ya-1e-7<=y<=yb+1e-7:
            t=(y-ya)/(yb-ya);return wa+(wb-wa)*t,ha+(hb-ha)*t
    raise ValueError(y)


def hull_base(y,angle):
    w,h=section(y);c,s=math.cos(angle),math.sin(angle)
    lower=max(0,-s)**1.5
    # A long upper deck above a shorter, fuller lower pressure body.
    yy=y+lower*((-.20+.64*(y+.20))-y)
    return Vector((w*c,yy,h*s*(.62 if s>=0 else 1)))


def hull(y,angle,offset=0):
    p=hull_base(y,angle)
    if not offset:return p
    lo=max(PROFILE[0][0],y-.0001);hi=min(PROFILE[-1][0],y+.0001)
    normal=(hull_base(hi,angle)-hull_base(lo,angle)).cross(
        hull_base(y,angle+.0001)-hull_base(y,angle-.0001)).normalized()
    return p+normal*offset


def frame(y,angle,offset=0):
    point=hull(y,angle,offset)
    forward=(hull(y+.001,angle)-hull(y-.001,angle)).normalized()
    tangent=(hull(y,angle+.001)-hull(y,angle-.001)).normalized()
    normal=forward.cross(tangent).normalized();x=forward.cross(normal).normalized();forward=normal.cross(x).normalized()
    return point,Matrix((x,forward,normal)).transposed(),normal


def hull_panel(name,y0,y1,a0,a1,tile,raise_by=.012,ny=10,na=7):
    vs=[];count=(ny+1)*(na+1)
    for layer in [0,1]:
        for j in range(ny+1):
            y=y0+(y1-y0)*j/ny
            for i in range(na+1):
                a=a0+(a1-a0)*i/na
                edge=min(j,ny-j,i,na-i)
                offset=raise_by*(.6 if edge==0 else 1) if layer==0 else -.007
                # Very shallow isolated plate dents, not dense surface noise.
                if name=='BellyCargoHatches' and layer==0:
                    offset-=.004*math.exp(-((j/ny-.45)/.16)**2-((i/na-.6)/.14)**2)
                vs.append(tuple(hull(y,a,offset)))
    n=na+1;fs=[]
    for j in range(ny):
        for i in range(na):
            q=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i);fs.extend([q,tuple(v+count for v in reversed(q))])
    boundary=list(range(n))+[j*n+na for j in range(1,ny+1)]
    boundary += [ny*n+i for i in range(na-1,-1,-1)]+[j*n for j in range(ny-1,0,-1)]
    fs.extend((a,a+count,b+count,b) for a,b in zip(boundary,boundary[1:]+boundary[:1]))
    emit(name,vs,fs,tile)


def body():
    ys=sorted(set([PROFILE[0][0]+(PROFILE[-1][0]-PROFILE[0][0])*i/80 for i in range(81)]+[p[0] for p in PROFILE]))
    vs=[tuple(hull(y,TAU*i/48)) for y in ys for i in range(48)]
    fs=[tuple(range(47,-1,-1)),tuple((len(ys)-1)*48+i for i in range(48))]
    fs.extend((j*48+i,j*48+(i+1)%48,(j+1)*48+(i+1)%48,(j+1)*48+i) for j in range(len(ys)-1) for i in range(48))
    emit('PressureHull',vs,fs,0)
    # Sparse broad plates follow curved skin, with localized fields from the sprite.
    for j,(y0,y1) in enumerate([(-2.88,-2.24),(-2.21,-1.50),(-1.47,-.64),(-.61,.25),(.28,1.18),(1.21,1.94),(1.97,2.54)]):
        for side in [-1,1]:
            centre=math.pi/2+side*.49
            hull_panel('FormedHullSkins',y0,y1,centre-.44,centre+.44,1 if j in (0,2,3,5) else 7)
        hull_panel('BellyCargoHatches',y0,y1,math.pi*1.07,math.pi*1.93,6 if j%3 else 0,.015,8,12)
    for y0 in [1.90,2.08]:hull_panel('OchreAftMarks',y0,y0+.07,.12,math.pi-.12,5,.020,3,14)
    rod('ForeTerminal',(0,-3.16,0),(0,-2.94,0),.088,4,32)
    rod('ForeTerminal',(0,-3.22,0),(0,-3.12,0),.071,11,28)
    rod('AftTerminal',(0,2.58,0),(0,2.80,0),.046,5,24)
    for y in [-.56,-.32]:hull_panel('DorsalStructure',y,y+.11,.08,math.pi-.08,2,.055,4,30)
    for side in [-1,1]:
        for y in [-1.0,.46]:
            a=.20 if side==1 else math.pi-.20
            p,rot,n=frame(y,a,.018)
            box('ServiceEquipment',p,(.24,.51,.07),3,.012,rot)
            for j in range(6):
                box('ServiceEquipment',p+rot@Vector((0,-.205+j*.082,.043)),(.19,.026,.025),9,.006,rot)
            for x in [-.13,.13]:box('ServiceEquipment',p+rot@Vector((x,0,.025)),(.025,.55,.045),2,.006,rot)
        for y in [-1.76,.92]:
            a=math.pi/2+side*.62;p,rot,n=frame(y,a,.022)
            box('ServiceEquipment',p,(.19,.28,.035),12,.008,rot)
            box('ServiceEquipment',p+n*.023,(.10,.10,.008),3,.002,rot)
        for y in [-.9,.1]:
            a=math.pi*1.5+side*.40;p,rot,n=frame(y,a,.025)
            box('ServiceEquipment',p,(.25,.36,.055),9,.010,rot)
            for x in [-.08,.08]:
                for yy in [-.11,.11]:
                    point=p+rot@Vector((x,yy,.036));rod('Fasteners',point,point+n*.012,.011,11,8)
    for y in [-1.35,-.50,.40,1.12]:
        p,rot,n=frame(y,math.pi*1.5,.028)
        box('ServiceEquipment',p,(.23,.12,.018),3,.006,rot)
        for x in [-.07,.07]:
            a=p+rot@Vector((x,0,.018));b=p+rot@Vector((x,0,.052));rod('ServiceEquipment',a,b,.012,2,8)
        a=p+rot@Vector((-.07,0,.052));b=p+rot@Vector((.07,0,.052));rod('ServiceEquipment',a,b,.014,2,10)


def crescent_point(side,t,v,depth=0):
    a=abs(t);s=math.sin(t*math.pi/2);taper=1-a**2.5
    # Broader fore shield around the hub, as in the concept/legacy root.
    # Grow the leading edge only; keep the inner mouth and distal tips intact.
    fore_shield=(.48*math.exp(-(a/.42)**2)
                 +.80*math.exp(-((a-.30)/.15)**2)
                 -.08*math.exp(-(a/.10)**2))
    y=-.45+2.95*a**1.65+(.5-v)*.64*taper-v*fore_shield*taper
    # Legacy/concept arms curl back towards the mouth instead of flaring apart.
    # Keep the structural root and lateral mounts; converge the distal tips.
    z=1.06*s*(1-.58*a*a)+(v-.5)*.32*s*taper
    x=side*(2.0+.055*a+.024*math.sin(math.pi*v)*taper+depth)
    return Vector((x,y,z))


def crescent_patch(group,side,t0,t1,v0,v1,tile,depth=0,nt=18,nv=5):
    count=(nt+1)*(nv+1);vs=[]
    for layer in [0,1]:
        for j in range(nt+1):
            t=t0+(t1-t0)*j/nt
            for i in range(nv+1):
                v=v0+(v1-v0)*i/nv
                skin=(.075*(1-abs(t)**2)+.015+depth)*(1 if layer==0 else -1)
                # Outer face is shallowly inset on a few service panels.
                if group=='CrimsonCrescentInsets' and layer==0:skin-=.004*math.exp(-(t/.12)**2-((v-.45)/.12)**2)
                vs.append(tuple(crescent_point(side,t,v,skin)))
    n=nv+1;fs=[]
    for j in range(nt):
        for i in range(nv):
            q=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i);fs.extend([q,tuple(v+count for v in reversed(q))])
    boundary=list(range(n))+[j*n+nv for j in range(1,nt+1)]
    boundary += [nt*n+i for i in range(nv-1,-1,-1)]+[j*n for j in range(nt-1,0,-1)]
    fs.extend((a,a+count,b+count,b) for a,b in zip(boundary,boundary[1:]+boundary[:1]))
    emit(group,vs,fs,tile)


def x_ring(group,x,y,z,profile,tile=2,n=40):
    vs=[(x+xx,y+r*math.cos(TAU*i/n),z+r*math.sin(TAU*i/n)) for xx,r in profile for i in range(n)]
    fs=[(j*n+i,j*n+(i+1)%n,((j+1)%len(profile))*n+(i+1)%n,((j+1)%len(profile))*n+i) for j in range(len(profile)) for i in range(n)]
    emit(group,vs,fs,tile)


def wings():
    for side in [-1,1]:
        crescent_patch('CrescentStructure',side,-.998,.998,0,1,9,0,88,8)
        # Narrow rims and restrained long curved inset plates; preserve the empty mouth.
        for j,(a,b) in enumerate([(-.995,-.70),(-.697,-.40),(-.397,-.12),(-.117,.117),(.12,.397),(.40,.697),(.70,.995)]):
            crescent_patch('CrimsonCrescentInsets',side,a,b,.12,.75,1 if j%3 else 15,.010,14,5)
            # Stay inside the core outline: coplanar outer caps caused striped z-fighting.
            crescent_patch('SilverCrescentRims',side,a,b,.76,.985,2,.014,14,3)
            crescent_patch('SilverCrescentRims',side,a,b,.015,.10,2,.014,14,3)
        rod('TransverseStructure',(side*.62,-.28,0),(side*2.06,-.28,0),.145,1,24)
        rod('TransverseStructure',(side*1.12,-.28,0),(side*1.38,-.28,0),.212,2,32)
        rod('TransverseStructure',(side*1.10,-.28,0),(side*1.13,-.28,0),.223,3,32)
        for j in range(6):
            a=TAU*j/6;n=Vector((0,math.cos(a),math.sin(a)));axis=Vector((side,0,0));tangent=axis.cross(n).normalized()
            rotation=Matrix((tangent,axis,n)).transposed();p=Vector((side*1.25,-.28,0))+n*.210
            box('ServiceEquipment',p,(.075,.16,.014),3,.004,rotation)
        x=side*2.08
        x_ring('RootServiceCollars',x,-.28,0,[(side*-.04,.38),(side*.03,.40),(side*.08,.36),(side*.08,.28),(side*-.04,.28)],2)
        rod('RootServiceCollars',(x,-.28,0),(x+side*.09,-.28,0),.275,1,40)
        for j in range(8):
            a=TAU*j/8;y=-.28+.32*math.cos(a);z=.32*math.sin(a)
            rod('Fasteners',(x+side*.076,y,z),(x+side*.095,y,z),.014,11,8)
        # A few root louvers and fitted maintenance strips follow the actual U shape.
        for t in [-.29,.29]:
            for v in [.26,.48]:
                p=crescent_point(side,t,v,.095)
                rotation=Vector((side,0,0)).to_track_quat('Z','Y').to_matrix()
                box('ServiceEquipment',p,(.12,.21,.035),2,.006,rotation)
                box('ServiceEquipment',p+Vector((side*.023,0,0)),(.065,.14,.012),3,.004,rotation)
        for t in [-.72,.72]:
            for v in [.27,.63]:
                # Match the inset skin at this station, rather than floating at
                # a fixed offset above a shell that tapers towards the tips.
                p=crescent_point(side,t,v,.075*(1-t*t)+.015+.010)
                rod('Fasteners',p,p+Vector((side*.012,0,0)),.010,4,8)


def material():
    mat=bpy.data.materials.new('Achaean | worn copper crimson and silver');mat.use_nodes=True
    tree=mat.node_tree;bs=tree.nodes.get('Principled BSDF')
    nodes=[]
    for name in ['base-colour','occlusion-roughness-metallic']:
        image=bpy.data.images.load(str(ROOT/'sources/materials/achaean/dedicated-ore-transporter'/f'{name}.png'),check_existing=True)
        if name!='base-colour':image.colorspace_settings.name='Non-Color'
        image.pack();node=tree.nodes.new('ShaderNodeTexImage');node.image=image;nodes.append(node)
    tree.links.new(nodes[0].outputs['Color'],bs.inputs['Base Color'])
    sep=tree.nodes.new('ShaderNodeSeparateColor');tree.links.new(nodes[1].outputs['Color'],sep.inputs['Color'])
    tree.links.new(sep.outputs['Green'],bs.inputs['Roughness']);tree.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
    return mat


def deck_height(x,y):
    w,h=section(y)
    return .62*h*math.sqrt(max(0,1-(x/w)**2))


def bridge_domes():
    # Four roof blisters interpreted as glazed crew/bridge stations by request.
    # Their precise 2x2 layout and interiors are authored, never equipment slots.
    for cx in [-.42,.42]:
        for cy in [-.90,.60]:
            rx,ry,height=.22,.28,.25;n=32;steps=12
            def point(t,a,lift=.018):
                x=cx+rx*math.cos(t)*math.cos(a);y=cy+ry*math.cos(t)*math.sin(a)
                return Vector((x,y,deck_height(x,y)+height*math.sin(t)+lift))
            vs=[tuple(point(math.pi/2*j/steps,TAU*i/n)) for j in range(steps+1) for i in range(n)]
            fs=[tuple(range(n-1,-1,-1))]
            fs.extend((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(steps) for i in range(n))
            emit('BridgeGlass',vs,fs,13)
            rings=[]
            for scale,lift in [(1.10,.004),(1.10,.048),(.98,.048),(.98,.004)]:
                for i in range(n):
                    a=TAU*i/n;x=cx+rx*scale*math.cos(a);y=cy+ry*scale*math.sin(a)
                    rings.append((x,y,deck_height(x,y)+lift))
            faces=[(j*n+i,j*n+(i+1)%n,((j+1)%4)*n+(i+1)%n,((j+1)%4)*n+i) for j in range(4) for i in range(n)]
            emit('BridgeFrames',rings,faces,9)
            for a in [0,math.pi/2]:
                arc=[point(math.pi*j/16,a) if j<=8 else point(math.pi*(16-j)/16,a+math.pi) for j in range(17)]
                for start,end in zip(arc,arc[1:]):rod('BridgeFrames',start,end,.008,2,8)
            z=deck_height(cx,cy)
            box('BridgeFrames',(cx,cy,z+.04),(.24,.27,.035),3,.008)
            box('BridgeFrames',(cx,cy-.06,z+.10),(.15,.055,.045),9,.008)
            box('BridgeFrames',(cx,cy+.05,z+.085),(.075,.08,.065),3,.008)


def glass_material():
    mat=bpy.data.materials.new('Achaean | tinted bridge glazing');mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(.10,.14,.16,1)
    bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.12
    bs.inputs['IOR'].default_value=1.46;bs.inputs['Transmission Weight'].default_value=.85
    mat['interpretation']='User-directed bridge/crew glazing, not recovered equipment or proven legacy material'
    return mat


def finalize(mat,root):
    result=[]
    smooth={'PressureHull','FormedHullSkins','BellyCargoHatches','OchreAftMarks','DorsalStructure',
            'CrescentStructure','CrimsonCrescentInsets','SilverCrescentRims','RootServiceCollars','TransverseStructure','ForeTerminal','AftTerminal','BridgeGlass'}
    glazing=glass_material()
    for name,row in GROUPS.items():
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(row['v'],[],row['f']);mesh.update()
        uv=mesh.uv_layers.new(name='Authored PBR atlas')
        for face,tile,(low,high) in zip(mesh.polygons,row['t'],row['chart']):
            dominant=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3) if a!=dominant]
            for loop in face.loop_indices:
                p=mesh.vertices[mesh.loops[loop].vertex_index].co
                u,v=[(p[a]-low[a])/max(1e-6,high[a]-low[a]) for a in axes]
                uv.data[loop].uv=((tile%4+.02+.96*u)/4,1-(tile//4+.02+.96*v)/4)
            face.use_smooth=name in smooth
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();mesh.set_sharp_from_angle(angle=.75)
        obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.parent=root
        mesh.materials.append(glazing if name=='BridgeGlass' else mat)
        if name=='BridgeGlass':obj['crew_domes']=4;obj['equipment_socket']=False
        obj['catalogue_id']=ID;obj['functional_detail_status']='authored structure, not calibrated gameplay equipment';result.append(obj)
    return result


def studio():
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
    scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
    scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.25
    scene.world=bpy.data.worlds.new('Neutral orbital studio');scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.19,.23,.29,1);bg.inputs[1].default_value=.32
    for name,p,power,colour,size in [('Key',(-10,-12,19),8500,(1,.95,.88),8),('Fill',(14,-1,11),4200,(.73,.85,1),10),('Rim',(-3,16,8),9000,(1,.90,.78),8)]:
        bpy.ops.object.light_add(type='AREA',location=p);lamp=bpy.context.object;lamp.name=name;lamp.data.energy=power;lamp.data.size=size;lamp.data.color=colour
        lamp.rotation_euler=(-lamp.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add();scene.camera=bpy.context.object;scene.camera.data.type='ORTHO'
    return scene


def aim(scene,direction,objects=None,margin=1.13):
    objects=objects or [o for o in scene.objects if o.type=='MESH']
    bpy.context.view_layer.update();points=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
    low=Vector(tuple(min(p[a] for p in points) for a in range(3)));high=Vector(tuple(max(p[a] for p in points) for a in range(3)))
    centre=(low+high)/2;offset=Vector(direction).normalized()*40;cam=scene.camera
    cam.location=centre+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();inv=cam.rotation_euler.to_matrix().transposed()
    projected=[inv@(p-centre) for p in points];width=max(p.x for p in projected)-min(p.x for p in projected);height=max(p.y for p in projected)-min(p.y for p in projected)
    cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*margin


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--no-render',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;GROUPS.clear()
    root=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root)
    root['catalogue_id']=ID;root['forward_axis']='-Y';root['up_axis']='Z';root['world_size_is_authored_recommendation']=True;root['proposed_world_size']=180
    root['equipment_slots']=4;root['calibrated_weapon_sockets']=0;root['source']='_S/AC2C.256; sixteen nonempty even headings'
    body();wings();bridge_domes();objects=finalize(material(),root)
    points=[Vector(p) for o in objects for p in o.bound_box];low=Vector(tuple(min(p[a] for p in points) for a in range(3)));high=Vector(tuple(max(p[a] for p in points) for a in range(3)))
    centre=(low+high)/2;factor=18/max(high-low)
    for obj in objects:
        for vert in obj.data.vertices:vert.co=(vert.co-centre)*factor
        obj.data.update()
    helper=bpy.data.objects.new('AlignmentForward',None);bpy.context.collection.objects.link(helper);helper.parent=root;helper.location=(Vector((0,-3.30,0))-centre)*factor
    helper['status']='uncalibrated authored alignment, not a recovered equipment socket'
    triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects)
    assert triangles<100000,triangles
    assert len(objects)<=20,len(objects)
    OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    scene=studio();aim(scene,(1.15,-1.25,.85))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects+[root,helper]:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(OUT/'model.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True,relative_remap=True)
    if not args.no_render:
        for name,direction in [('front-quarter',(1.15,-1.25,.85)),('rear-quarter',(-1.0,1.2,.70)),('top',(0,-.001,1)),('front',(0,-1,.15)),('side',(1,0,.12)),('underside',(1,-1,-.8))]:
            aim(scene,direction,margin=1.20)
            if name=='underside':
                for lamp in [o for o in scene.objects if o.type=='LIGHT']:
                    lamp.location.z=-lamp.location.z;lamp.rotation_euler=(-lamp.location).to_track_quat('-Z','Y').to_euler()
            scene.render.filepath=str(MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True)
    data={'id':ID,'issue':234,'triangles':triangles,'mesh_batches':len(objects),'materials':2,'packed_maps':2,
          'crew_domes':4,'glazing_status':'User-directed interpretation; precise layout/interiors authored, not hardpoints',
          'native_dimensions':[round(v*factor,6) for v in high-low],'normalization_factor':factor,'normalization_centre':list(centre),
          'proposed_world_size':180,'scale_status':'Authored transporter-class recommendation; not recovered metres or applied game override',
          'blend_sha256':sha(OUT/'model.blend'),'glb_sha256':sha(OUT/'model.glb'),'generator_sha256':sha(Path(__file__)),
          'legacy_source_pixels_used_as_textures':False,'calibrated_weapon_sockets':0,'hidden_mechanisms':'Authored service structures; no operational animation claimed'}
    (OUT/'generation.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print('ACHAEAN_TRANSPORTER_GENERATED '+json.dumps(data),flush=True)


if __name__=='__main__':main()
