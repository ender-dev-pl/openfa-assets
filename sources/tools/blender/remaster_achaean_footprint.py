"""Author AC01 from reviewed paletted legacy anatomy and ImageGen concept."""
import argparse, hashlib, json, math, random, sys, tempfile, uuid
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_blend, clean_png

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def lathe(name, centre, profile, material, lobes=0):
    verts=[];faces=[];n=64
    for j,(z,r) in enumerate(profile):
        for i in range(n):
            a=2*math.pi*i/n; dent=.002*math.sin(7*a+j*.8)*math.sin(j*1.7)
            radius=max(.001,r*(1+lobes*math.cos(8*a))+dent)
            verts.append((centre[0]+radius*math.cos(a),centre[1]+radius*math.sin(a),z))
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(material)
    uv=mesh.uv_layers.new(name='Authored wear UV')
    for p in mesh.polygons:
        p.use_smooth=len(p.vertices)==4
        for li in p.loop_indices:
            vi=mesh.loops[li].vertex_index;uv.data[li].uv=(vi%n/(n-1),(vi//n)/(len(profile)-1))
    return obj

def box(name,loc,size,mat,bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        m=o.modifiers.new('Small worn edge radii','BEVEL');m.width=bevel;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
    return o

def material(name,colour,metal,rough,emission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*colour,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough
    if emission:s.inputs['Emission Color'].default_value=(*(c*emission for c in colour),1);s.inputs['Emission Strength'].default_value=1
    else:
        texture=ROOT/'sources/materials/achaean/footprint'/f'{name}.png';texture.parent.mkdir(parents=True,exist_ok=True);image=bpy.data.images.new(name+' authored weathering',width=256,height=256);rng=random.Random(name);pixels=[]
        for y in range(256):
            for x in range(256):
                u=x/255;v=y/255;stain=.37*math.exp(-((v-.06)/.12)**2)+.22*math.exp(-((u-.55)/.13)**2)*math.exp(-((v-.6)/.3)**2);grain=rng.uniform(-.045,.045);scratch=.46 if (x*73+y*19)%997<2 else 0
                pixels.extend([max(0,min(1,c*(1-stain+grain+scratch))) for c in colour]+[1])
        image.pixels.foreach_set(pixels);image.filepath_raw=str(texture);image.file_format='PNG';image.save();texture.write_bytes(clean_png(texture.read_bytes()));image.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;m.node_tree.links.new(t.outputs['Color'],s.inputs['Base Color'])
    return m

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    out=ROOT/'sources/objects/achaean/footprint';out.mkdir(parents=True,exist_ok=True)
    coral=material('Coral alloy',(.43,.19,.13),.48,.51);gold=material('Aged brass',(.49,.34,.13),.72,.42);slate=material('Blue gray fittings',(.16,.24,.29),.7,.38);dark=material('Dark recess',(.016,.021,.026),.35,.5);glass=material('Optical blue glass',(.015,.06,.105),.8,.14);red=material('Red status lenses',(.34,.018,.009),.4,.3,.35)
    back=(-.43,.24);front=(.43,-.26)
    profile=[(0,.39),(.08,.54),(.24,.64),(.48,.67),(.7,.61),(.89,.49),(1.02,.27),(1.04,.12)]
    lathe('Rear support chamber',back,profile,coral)
    lathe('Front service chamber',front,[(0,.38),(.08,.53),(.24,.62),(.48,.65),(.65,.61)],coral)
    lathe('Tower lower neck',back,[(.78,.27),(1,.25),(1.43,.25),(1.53,.32)],coral)
    lathe('Tower lower console drum',back,[(1.46,.31),(1.53,.41),(1.66,.42),(1.93,.42),(2.02,.36)],coral)
    lathe('Tower upper column',back,[(1.97,.35),(2.02,.36),(2.87,.36),(2.99,.33)],coral)
    lathe('Tower crown',back,[(2.96,.33),(3.02,.36),(3.08,.34),(3.16,.25),(3.24,.12),(3.27,.06)],gold,.035)
    lathe('Tower finial',back,[(3.23,.045),(3.46,.045),(3.49,.012)],slate)
    lathe('Service chamber onion cap',front,[(.64,.625),(.72,.60),(.80,.53),(.91,.38),(1,.21),(1.07,.07)],gold,.035)
    lathe('Service chamber finial',front,[(1.03,.038),(1.2,.038),(1.22,.01)],slate)
    for name,c,z,r in [('Rear lower seam',back,.27,.643),('Rear crown collar',back,2.98,.345),('Console collar',back,1.52,.405),('Service lower seam',front,.24,.623)]:
        lathe(name,c,[(z-.009,r),(z+.009,r)],gold if 'collar' in name else dark)
    # Front inset instruments sit against the curved casing, with a dark recessed
    # backing and raised rim rather than free-floating markings.
    for name,z,w,h in [('Upper red port',2.78,.14,.14),('Optic housing',2.51,.22,.22),('Console blank',2.27,.2,.11),('Lower instrument',1.81,.17,.2)]:
        y=back[1]-(.365 if z>2 else .425)
        box(name+' surround',(back[0],y,z),(w+.055,.04,h+.055),slate,.014);box(name+' recess',(back[0],y-.026,z),(w,.016,h),dark,.007)
        if 'red' in name:box(name+' lens',(back[0],y-.039,z),(w*.8,.014,h*.62),red,.007)
    # Optical lens is a closed lathed component turned to face -Y.
    o=lathe('Blue observation optic',(0,0),[(0,.085),(.025,.085),(.05,.065),(.062,.012)],glass);o.rotation_euler[0]=math.pi/2;o.location=(back[0],back[1]-.398,2.51)
    for sign in [-1,1]:
        box('Tower side fin '+str(sign),(back[0]+sign*.373,back[1],2.51),(.075,.25,.48),slate)
        for j in range(3):box(f'Side fin rib {sign} {j}',(back[0]+sign*.42,back[1]-.025,2.35+j*.14),(.04,.29,.035),slate,.006)
    for x in [-.23,0,.23]:
        box('Console vertical relief '+str(x),(back[0]+x,back[1]-.40,1.72),(.075,.065,.31),coral)
    for j in range(4):
        box('Upper column side recess '+str(j),(back[0]+.20,back[1]-.31,2.12+j*.15),(.07,.022,.065),dark,.005)
    box('Service grille frame',(front[0],front[1]-.625,.46),(.26,.045,.38),slate,.018)
    box('Service grille recess',(front[0],front[1]-.655,.46),(.205,.025,.325),dark,.008)
    for j in range(4):box('Service grille louvre '+str(j),(front[0],front[1]-.673,.35+j*.075),(.19,.028,.026),red,.006)
    for x in [-1,1]:
        box('Service inspection plate '+str(x),(front[0]+x*.34,front[1]-.56,.49),(.15,.035,.21),gold,.02)
    # Source-backed technical finish: sparse casting seams, servicing panels,
    # visible fasteners and vent depth; no invented dense panel tessellation.
    for z,r in [(2.06,.36),(2.92,.35),(1.96,.39)]:
        lathe('Tower seam band '+str(z),back,[(z-.008,r+.004),(z+.008,r+.004)],dark)
    for side in [-1,1]:
        o=box('Rear tower maintenance surround '+str(side),(back[0]+side*.18,back[1]+.315,2.43),(.17,.04,.50),slate,.012)
        box('Rear tower maintenance inset '+str(side),(back[0]+side*.18,back[1]+.341,2.43),(.12,.017,.44),coral,.008)
        for j in range(5):
            box('Rear cooling louvre '+str(side)+' '+str(j),(back[0]+side*.18,back[1]+.356,2.28+j*.06),(.10,.02,.014),dark,.003)
    for j in range(8):
        a=2*math.pi*j/8
        x=back[0]+.33*math.cos(a);y=back[1]+.33*math.sin(a)
        lathe('Crown collar fastener '+str(j),(x,y),[(2.98,.014),(3.008,.014)],slate)
    # Bolt heads use closed octagonal prisms (shared material batch later).
    for z,y,w,h in [(2.51,back[1]-.397,.23,.23),(2.78,back[1]-.397,.18,.18),(.46,front[1]-.663,.27,.39)]:
        cx=back[0] if z>1 else front[0]
        for dx in [-w/2,w/2]:
            for dz in [-h/2,h/2]:
                bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.013,depth=.009,location=(cx+dx,y-.015,z+dz),rotation=(math.pi/2,0,0));bpy.context.object.name='Housing fastener';bpy.context.object.data.materials.append(gold)
    for c,z,r in [(back,.28,.642),(front,.25,.622)]:
        for j in range(12):
            a=j*math.pi/6
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.014,location=(c[0]+r*math.cos(a),c[1]+r*math.sin(a),z));bpy.context.object.name='Chamber seam fastener';bpy.context.object.data.materials.append(slate)
    # Short service conduits are seated in the two chambers, never floating.
    for sign in [-1,1]:
        c=(front[0]+sign*.49,front[1]-.21)
        lathe('Service conduit '+str(sign),c,[(.17,.025),(.57,.025)],slate)
    # Fewer draw nodes: retain principal silhouette meshes, consolidate small
    # fixtures by material. All still editable; no duplicate state copies.
    small=[o for o in bpy.context.scene.objects if o.type=='MESH' and ('rib' in o.name or 'recess ' in o.name or 'louvre' in o.name or 'relief' in o.name or 'fastener' in o.name or 'maintenance' in o.name)]
    groups=[(mat,[o for o in small if o.data.materials[0]==mat]) for mat in [coral,gold,slate,dark,red]]
    for mat,group in groups:
        if not group:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in group:o.select_set(True)
        bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name='Consolidated '+mat.name+' fixtures'
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root);root['catalogue_id']='openfa:building/legacy/151';root['footprint']=[3,3];root['forward_axis']='-Y';root['dorsal_axis']='+Z'
    for o in meshes:
        o.parent=root;bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Stable export triangulation','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=m.name)
        # Freeze split shading explicitly. The glTF importer uses smooth faces
        # with split corner normals; matching that representation avoids a
        # Cycles shadow-terminator difference at otherwise identical flat caps.
        normals=[tuple(n.vector) for n in o.data.corner_normals]
        for face in o.data.polygons:face.use_smooth=True
        o.data.normals_split_custom_set(normals)
    bpy.context.view_layer.update();tri=sum(len(o.data.polygons) for o in meshes);assert tri<30000
    # Export using task-local inherited-ACL folders, then remove only those folders.
    temp=ROOT/'artifacts/achaean-building-export-temp';temp.mkdir(parents=True,exist_ok=True);old=tempfile.mkdtemp
    def mk(*a,**k):
        p=temp/uuid.uuid4().hex;p.mkdir();return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);p=out/'model.blend';p.write_bytes(clean_blend(p.read_bytes())[0])
    meta=dict(issue=256,id='openfa:building/legacy/151',name='Footprint',culture='achaean',footprint=[3,3],definition_class=20,construction_updates=50,mesh_nodes=len(meshes),triangles=tri,materials=6,binaries={k:sha(out/f'model.{k}') for k in ['blend','glb']},author_sha256=sha(Path(__file__)),state_contract='Static support facility; catalogue reveal/highlight is presentation, not an established operating cycle. Construction/damage are not authored here.',scale_contract='Local origin at footprint centre and ground Z=0; -Y front, +Z up. Game tile/world scale requires integration calibration.',final_artistic_acceptance=False,game_client_integration=False)
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print('AC01_AUTHORED',tri,len(meshes),flush=True)
if __name__=='__main__':main()
