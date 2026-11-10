"""AC0A Hunter/Prospector, issue238: central green hull and paired upright crescents.

Original tiny sprites constrain broad silhouette/colour; sections, hidden fittings
and scale remain authored. Reuses unchanged copper/red material primitives only.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
import bpy
from mathutils import Vector, Matrix

sys.path.insert(0, str(Path(__file__).parent))
import remaster_achaean_transporter as shared

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'sources/objects/achaean/hunter-prospector'
MEDIA = ROOT/'gallery/media/objects/achaean/hunter-prospector'
ID = 'openfa:ship/achaean/hunter-prospector'
BODY = [(-1.62, 0, .012, .012), (-1.20, 0, .13, .10),
        (-.70, 0, .27, .19), (-.15, 0, .34, .26),
        (.35, 0, .32, .24), (.75, 0, .22, .17), (.92, 0, .035, .045)]


def crescent(side, t, v, depth=0):
    # Two upright plates: full C profile from the side, thin rails from above.
    a=abs(t);s=math.sin(t*math.pi/2);taper=1-a*a
    return Vector((side*(.67+.025*a+depth),
                   -.48+2.08*a**1.7+(v-.5)*.68*taper,
                   1.10*s+(v-.5)*.12*s*taper))


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def sample(profile, t):
    """Local Hermite interpolation keeps a smooth continuous loft section."""
    t = max(0, min(len(profile)-1, t))
    i = min(int(t), len(profile)-2); u = t-i
    p0, p1 = Vector(profile[i]), Vector(profile[i+1])
    m0 = (Vector(profile[i+1])-Vector(profile[max(0, i-1)]))/(2 if i else 1)
    m1 = (Vector(profile[min(len(profile)-1, i+2)])-Vector(profile[i]))/(2 if i+2 < len(profile) else 1)
    return (2*u**3-3*u*u+1)*p0+(u**3-2*u*u+u)*m0+(-2*u**3+3*u*u)*p1+(u**3-u*u)*m1


def surface(profile, t, a, side=1, offset=0):
    y, x, w, h = sample(profile, t)
    tangent = sample(profile, min(len(profile)-1, t+.0001))-sample(profile, max(0, t-.0001))
    radial = Vector((tangent[0], -tangent[1], 0)).normalized()
    c, s = math.cos(a), math.sin(a)
    dent = .006*math.exp(-((t-2.5)/.25)**2-((a-1.7)/.22)**2)
    p = Vector((x, y, 0))+radial*(w*c)+Vector((0, 0, h*s-dent))
    n = (radial*(c/w)+Vector((0, 0, s/h))).normalized()
    p += n*offset
    p.x *= side
    return p


def loft(name, profile, side, tile, rings=80, around=40):
    vs = [tuple(surface(profile, (len(profile)-1)*j/rings, math.tau*i/around, side))
          for j in range(rings+1) for i in range(around)]
    fs = [tuple(range(around-1, -1, -1)), tuple(rings*around+i for i in range(around))]
    fs.extend((j*around+i, j*around+(i+1)%around, (j+1)*around+(i+1)%around, (j+1)*around+i)
              for j in range(rings) for i in range(around))
    shared.emit(name, vs, fs, tile)


def patch(name, profile, side, t0, t1, a0, a1, tile, lift=.008, nt=12, na=8):
    count = (nt+1)*(na+1); vs = []
    for layer in [0, 1]:
        for j in range(nt+1):
            for i in range(na+1):
                t=t0+(t1-t0)*j/nt; a=a0+(a1-a0)*i/na
                vs.append(tuple(surface(profile,t,a,side,lift if layer==0 else -.004)))
    n=na+1; fs=[]
    for j in range(nt):
        for i in range(na):
            q=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i)
            fs.extend([q,tuple(v+count for v in reversed(q))])
    boundary=list(range(n))+[j*n+na for j in range(1,nt+1)]
    boundary += [nt*n+i for i in range(na-1,-1,-1)]+[j*n for j in range(nt-1,0,-1)]
    fs.extend((a,a+count,b+count,b) for a,b in zip(boundary,boundary[1:]+boundary[:1]))
    shared.emit(name,vs,fs,tile)


def fitting(profile, side, t, angle, length=.26):
    p=surface(profile,t,angle,side,.012)
    along=(surface(profile,t+.01,angle,side)-surface(profile,t-.01,angle,side)).normalized()
    across=(surface(profile,t,angle+.01,side)-surface(profile,t,angle-.01,side)).normalized()
    normal=along.cross(across).normalized()*side
    rot=Matrix((across,normal.cross(across),normal)).transposed()
    shared.box('RecessedServiceCovers',p,(.16,length,.018),3,.006,rot)
    for x in [-.095,.095]:
        shared.box('ServiceRims',p+rot@Vector((x,0,.008)),(.018,length+.035,.025),9,.004,rot)
    for y in [-length*.27,0,length*.27]:
        shared.box('ServiceLouvers',p+rot@Vector((0,y,.018)),(.13,.026,.022),9,.006,rot)
    for x in [-.095,.095]:
        for y in [-length*.42,length*.42]:
            q=p+rot@Vector((x,y,.021));shared.rod('Fasteners',q,q+normal*.006,.008,11,8)


def crescent_plate(side):
    # One watertight shell with coloured edge faces, not overlapping rim skins.
    # Keeping rims in the same topology prevents tip self-intersection stripes.
    nt,nv=120,12;count=(nt+1)*(nv+1);vertices=[]
    for layer in [0,1]:
        for j in range(nt+1):
            t=-.998+1.996*j/nt
            for i in range(nv+1):
                v=i/nv;depth=(.075*(1-t*t)+.015)*(1 if layer==0 else -1)
                if layer==0:depth-=.003*math.exp(-((t-.25)/.14)**2-((v-.48)/.2)**2)
                vertices.append(tuple(crescent(side,t,v,depth)))
    n=nv+1;faces=[];tiles=[]
    for j in range(nt):
        for i in range(nv):
            q=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i)
            faces.extend([q,tuple(v+count for v in reversed(q))])
            tiles.extend([9 if i==0 else (2 if i==nv-1 else 15)]*2)
    boundary=list(range(n))+[j*n+nv for j in range(1,nt+1)]
    boundary += [nt*n+i for i in range(nv-1,-1,-1)]+[j*n for j in range(nt-1,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):
        faces.append((a,a+count,b+count,b));tiles.append(9)
    shared.emit('UprightCrescentCore',vertices,faces,15)
    shared.GROUPS['UprightCrescentCore']['t'][-len(tiles):]=tiles


def geometry():
    loft('GreenPressureHull',BODY,1,0)
    for lo,hi in [(1.15,2.6),(2.64,4.6)]:
        patch('GreenFormedSkins',BODY,1,lo,hi,.18,1.40,1)
        patch('GreenFormedSkins',BODY,1,lo,hi,1.74,math.pi-.18,2)
    patch('GreenBellyHatch',BODY,1,2.2,4.1,3.7,5.7,3,.010)
    fitting(BODY,1,3.10,math.pi/2,.31)
    fitting(BODY,1,3.15,math.pi*1.5,.28)
    # Warm fields belong to the hull/fittings; no detached third spar.
    for side in [-1,1]:
        crescent_plate(side)
        shared.rod('LateralHullLinks',(side*.26,-.40,0),(side*.72,-.40,0),.070,9,24)
        shared.x_ring('RootCollars',side*.69,-.40,0,
                      [(side*-.018,.16),(side*.022,.17),(side*.04,.15),(side*.04,.10),(side*-.018,.10)],2,32)
        for t in [-.42,.42]:
            skin=.075*(1-t*t)+.015+.012
            point=crescent(side,t,.45,skin)
            rot=Vector((side,0,0)).to_track_quat('Z','Y').to_matrix()
            shared.box('RecessedServiceCovers',point,(.075,.15,.016),3,.004,rot)
            for u in [-.05,0,.05]:
                shared.box('ServiceLouvers',point+rot@Vector((0,u,.012)),(.055,.014,.014),9,.003,rot)
        angle=.20 if side==1 else math.pi-.20
        patch('OchreHullFields',BODY,1,3.7,4.4,angle-.18,angle+.18,5,.009)
    # Small alloy nose cap; no invented emitter or weapon function.
    patch('NoseCap',BODY,1,.01,.20,0,math.tau,11,.004,5,32)


def green_material():
    mat=bpy.data.materials.new('Achaean | worn green pressure shell');mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');nodes=[]
    for name in ['green-base-colour','green-occlusion-roughness-metallic']:
        im=bpy.data.images.load(str(ROOT/'sources/materials/achaean/hunter-prospector'/f'{name}.png'))
        if 'roughness' in name:im.colorspace_settings.name='Non-Color'
        im.pack();node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;nodes.append(node)
    tree=mat.node_tree;tree.links.new(nodes[0].outputs['Color'],bs.inputs['Base Color'])
    sep=tree.nodes.new('ShaderNodeSeparateColor');tree.links.new(nodes[1].outputs['Color'],sep.inputs['Color'])
    tree.links.new(sep.outputs['Green'],bs.inputs['Roughness']);tree.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
    return mat


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    shared.GROUPS.clear();shared.ID=ID;shared.crescent_point=crescent
    root=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root)
    root['catalogue_id']=ID;root['forward_axis']='-Y';root['up_axis']='Z'
    root['equipment_slots']=2;root['calibrated_weapon_sockets']=0;root['proposed_world_size']=40
    root['interpretation']='AC0A user-corrected upright aft-opening paired crescents and continuous green hull; sections authored'
    geometry();objects=shared.finalize(shared.material(),root);green=green_material()
    for o in objects:
        if o.name.startswith('Green'):o.data.materials.clear();o.data.materials.append(green)
        if o.name not in {'Fasteners','ServiceLouvers','ServiceRims','RecessedServiceCovers','UndersideServicePads'}:
            for f in o.data.polygons:f.use_smooth=True
    pts=[Vector(p) for o in objects for p in o.bound_box]
    low=Vector(tuple(min(p[a] for p in pts) for a in range(3)));high=Vector(tuple(max(p[a] for p in pts) for a in range(3)))
    centre=(low+high)/2;factor=18/max(high-low)
    for o in objects:
        for v in o.data.vertices:v.co=(v.co-centre)*factor
        o.data.update()
    helper=bpy.data.objects.new('AlignmentForward',None);bpy.context.collection.objects.link(helper);helper.parent=root
    helper.location=(Vector((0,-1.3,0))-centre)*factor;helper['status']='authored alignment, not equipment socket'
    triangles=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in objects)
    assert triangles<60000 and len(objects)<=20
    OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    scene=shared.studio();shared.aim(scene,(1,-1,.85),margin=1.20)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects+[root,helper]:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(OUT/'model.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True,relative_remap=True)
    for name,direction in [('front-quarter',(1,-1,.85)),('rear-quarter',(1,1,.65)),('front',(0,-1,.14)),('side',(1,0,.14)),('top',(0,.001,1)),('underside',(1,-1,-.7))]:
        shared.aim(scene,direction,margin=1.20)
        if name=='underside':
            for lamp in [o for o in scene.objects if o.type=='LIGHT']:
                lamp.location.z=-lamp.location.z;lamp.rotation_euler=(-lamp.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True)
    report=dict(id=ID,issue=238,triangles=triangles,mesh_batches=len(objects),materials=2,packed_maps=4,
        native_dimensions=list((high-low)*factor),normalization_factor=factor,normalization_centre=list(centre),
        blend_sha256=sha(OUT/'model.blend'),glb_sha256=sha(OUT/'model.glb'),generator_sha256=sha(Path(__file__)),
        shared_authoring_helper_sha256=sha(Path(shared.__file__)),proposed_world_size=40,current_client_fallback_size=96,
        scale_status='authored scout size proposal; not recovered metres or applied override',calibrated_sockets=0,
        legacy_source_pixels_used_as_textures=False)
    (OUT/'generation.json').write_text(json.dumps(report,indent=2)+'\n');print('HUNTER_GENERATED',json.dumps(report))


if __name__=='__main__':main()
