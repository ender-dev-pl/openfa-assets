"""Editable modular RIS2 scaffold prototype with explicit stage/tier roots."""
import hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene,box,material,finish
from build_refined_terran import stage_path,publish,save_blend_to,render_to
from catalogue_rendering import evaluated_points,fit_camera
from terran_light_ship_parts import orient_and_chamfer
from analyse_scaffold_stacking import scaffold_chain
REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/scaffolds/rigellian/size-2'
# Provisional pitch: source repeat 8px / body width 44px, diagonal square projection.
PITCH=8/44*(1.8*math.sqrt(2))/math.sqrt(2/3)
LIMITS_PATH=REPO/'docs/reconstruction/models/scaffold-stage-limits.json'
LIMITS=json.loads(LIMITS_PATH.read_text())
FAMILY_LIMITS=next(item for item in LIMITS['families'] if item['family']=='RIS2')
CASES=list(range(1,FAMILY_LIMITS['max_required_stage']+1))


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def export_glb_to(target):
    stage=stage_path('.glb')
    bpy.ops.export_scene.gltf(filepath=str(stage),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    publish(stage,target)


def tube(name,location,width,inner,height,surface):
    vertices=[]
    for z in [-height/2,height/2]:
        for radius in [width/2,inner/2]:
            vertices += [(x*radius,y*radius,z) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    faces=[]
    for i in range(4):
        j=(i+1)%4
        faces += [(i,j,j+8,i+8),(i+4,i+12,j+12,j+4),(i,i+4,j+4,j),(i+8,j+8,j+12,i+12)]
    mesh=bpy.data.meshes.new(name+' hollow section');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.location=location
    uv=mesh.uv_layers.new(name='Authored metal wear')
    for face in mesh.polygons:
        for index,coord in zip(face.loop_indices,[(0,0),(1,0),(1,1),(0,1)]): uv.data[index].uv=coord
    return finish(obj,name,surface,.001)


def painted(name,colour,kind):
    result=material(name,colour,.62,.58);nodes=result.node_tree.nodes;links=result.node_tree.links;shader=nodes.get('Principled BSDF')
    for suffix,input_name,space in [('colour','Base Color','sRGB'),('roughness','Roughness','Non-Color')]:
        texture=nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(ROOT/f'{kind}-{suffix}.png'));texture.image.colorspace_settings.name=space;texture.image.pack()
        links.new(texture.outputs['Color'],shader.inputs[input_name])
    return result


def share_evaluated_geometry(meshes):
    # These meshes come from the same constrained tube/box authoring functions.
    # Include local geometry, polygon flags, materials, UVs and bevel settings.
    cache={};graph=bpy.context.evaluated_depsgraph_get()
    for obj in meshes:
        mesh=obj.data
        key=(tuple(tuple(v.co) for v in mesh.vertices),tuple((tuple(p.vertices),p.use_smooth,p.material_index) for p in mesh.polygons),
             tuple(m.name for m in mesh.materials),tuple((layer.name,tuple(tuple(item.uv) for item in layer.data)) for layer in mesh.uv_layers),
             tuple((modifier.type,getattr(modifier,'width',None),getattr(modifier,'segments',None)) for modifier in obj.modifiers))
        if key not in cache:
            cache[key]=bpy.data.meshes.new_from_object(obj.evaluated_get(graph),preserve_all_data_layers=True,depsgraph=graph)
        obj.data=cache[key]
        obj.modifiers.clear()
    return len(cache)


def main():
    records=[]
    for stage in CASES:
        print('RIS2_BUILD_STAGE',stage,'of',CASES[-1],flush=True)
        scene=setup_scene(900,64)
        green=painted('RIS2 | worn green frame',(.12,.29,.22),'green');copper=painted('RIS2 | oxidised copper ties',(.38,.22,.10),'copper')
        root=bpy.data.objects.new('PlacementRoot',None);scene.collection.objects.link(root)
        root['family']='RIS2';root['footprint_width']=root['footprint_height']=2;root['construction_stage']=stage;root['physical_pitch_calibrated']=False
        chain=scaffold_chain(stage-1,0,255,2);positions=[]
        for side in range(4):
            for n in range(6):
                t=-.84+n*.28
                positions.append([(t,-.84),(.84,t),(-t,.84),(-.84,-t)][side])
        positions += [(x,y) for x in [-.56,0,.56] for y in [-.56,0,.56]]
        for level,item in enumerate(chain):
            tier=bpy.data.objects.new(f'Tier {level}',None);scene.collection.objects.link(tier);tier.parent=root;tier.location.z=level*PITCH;tier['stage_frame']=item['frame']
            for name,z in [('BottomSocket',0),('TopSocket',PITCH)]:
                socket=bpy.data.objects.new(f'Tier {level} {name}',None);scene.collection.objects.link(socket);socket.parent=tier;socket.location.z=z
            height=PITCH*item['frame']/2
            for i,(x,y) in enumerate(positions):
                post=tube(f'Tier {level} upright {i}',(x,y,height/2),.075,.059,height,green);post.parent=tier
                if level==0:
                    foot=box(f'Ground foot {i}',(x,y,.025),(.12,.12,.05),copper,.004);foot.parent=root
                else:
                    sleeve=tube(f'Tier {level} joint sleeve {i}',(x,y,.015),.092,.070,.060,copper);sleeve.parent=tier
            for side in range(4):
                for n in range(1):
                    t=0
                    for fraction in ([.25] if item['frame']==1 else [.25,.75]):
                        xyz=[(t,-.84,height*fraction),(.84,t,height*fraction),(-t,.84,height*fraction),(-.84,-t,height*fraction)][side]
                        dims=(1.70,.040,.040) if side%2==0 else (.040,1.70,.040)
                        rail=box(f'Tier {level} tie {side}-{n}-{fraction}',xyz,dims,copper,.002);rail.parent=tier
            for axis in range(2):
                for row in [-.56,0,.56]:
                    for n in range(1):
                        t=0
                        for fraction in ([.25] if item['frame']==1 else [.25,.75]):
                            # Stagger crossing ties into an overlapping lap joint; avoid coincident coplanar top faces.
                            z=height*fraction+(-.012 if axis==0 else .012)
                            xyz=(t,row,z) if axis==0 else (row,t,z)
                            dims=(1.70,.040,.040) if axis==0 else (.040,1.70,.040)
                            rail=box(f'Tier {level} internal tie {axis}-{row}-{n}-{fraction}',xyz,dims,copper,.002);rail.parent=tier
        meshes=[o for o in scene.objects if o.type=='MESH'];orient_and_chamfer(meshes);bpy.context.view_layer.update()
        unique_meshes=share_evaluated_geometry(meshes);bpy.context.view_layer.update()
        target=ROOT/f'stage-{stage:02}';target.mkdir(parents=True,exist_ok=True)
        points=evaluated_points(meshes)
        for view,direction in [('front-quarter',(10,-10,10)),('rear-quarter',(-10,10,10))]:
            fit_camera(scene,points,direction);render_to(scene,target/(view+'.png'))
        fit_camera(scene,points,(10,-10,10));bpy.ops.object.select_all(action='DESELECT')
        for obj in [o for o in scene.objects if o.type in ['MESH','EMPTY']]: obj.select_set(True)
        bpy.context.view_layer.objects.active=root;export_glb_to(target/'model.glb');save_blend_to(target/'model.blend')
        records.append(dict(total_stage=stage,frames=[r['frame'] for r in chain],mesh_objects=len(meshes),unique_meshes=unique_meshes,blend_sha256=sha(target/'model.blend'),glb_sha256=sha(target/'model.glb')))
    metadata=dict(issue=983,family='RIS2',revision=2,required_max_stage=FAMILY_LIMITS['max_required_stage'],required_max_tiers=FAMILY_LIMITS['max_required_tiers'],stage_limits_sha256=sha(LIMITS_PATH),kind='modular-scaffolding-prototype',uprights_per_tier=33,pitch=PITCH,pitch_status='Provisional diagonal orthographic calibration, not recovered world units',
        pitch_derivation='8/44 * (1.8*sqrt(2))/sqrt(2/3); source descriptor body width 44px; nominal footprint envelope 1.8; elevation atan(1/sqrt(2))',
        observed=['Two erection stages','Green vertical structure with copper/brass horizontal ties including visible interior structure','Same XY footprint with a four-pixel difference in body height'],
        inferred=['24 perimeter and nine interior uprights; exact lattice, sections, joint sleeves, foot design and hidden surfaces','Detailed physical structure, wear and exact placement/pitch'],
        cases=records,generator_sha256=sha(Path(__file__)),wear_sha256=sha(ROOT/'authored-wear.json'),
        reference_sha256=sha(REPO/'docs/reconstruction/models/shared-construction-references.json'),final_visual_acceptance=False,
        unresolved=['Original ownership-based family selection','Projection/world height calibration','Per-stage final art refinement','Game presentation integration'])
    assert [r['total_stage'] for r in records]==CASES
    (ROOT/'model.json').write_text(json.dumps(metadata,indent=2)+'\n');print('RIS2_MODULAR_PROTOTYPE_OK',len(records),flush=True)


if __name__=='__main__': main()
