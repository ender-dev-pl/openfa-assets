"""Independent native/GLB evidence for supplied-concept asset-only proposals."""
import argparse,hashlib,json,math,struct,sys
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tools'));from publication_support import clean_png
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def snapshot(meta,check_textures=True):
    root=bpy.data.objects['ProposalRoot'];assert root['status']=='proposal-awaiting-mechanics' and not root['runtime_integration'] and not root['legacy_unit']
    result={};images=set();material_set=set()
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        assert obj.parent and not obj.animation_data
        points=[obj.matrix_world@v.co for v in obj.data.vertices];faces=[tuple(f.vertices) for f in obj.data.polygons]
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.free()
        assert obj.data.uv_layers.active and all(math.isfinite(v) for uv in obj.data.uv_layers.active.data for v in uv.uv)
        materials=[]
        for m in obj.data.materials:
            p=m.node_tree.nodes.get('Principled BSDF');assert p.inputs['Alpha'].default_value==1 and p.inputs['Transmission Weight'].default_value==0
            assert max(abs(p.inputs['Emission Color'].default_value[i]*p.inputs['Emission Strength'].default_value) for i in range(3))<1e-7
            assert all(p.inputs[key].is_linked for key in ['Roughness','Metallic','Normal']),('Missing portable PBR map',m.name)
            assert not m.animation_data,('Unexpected animated material',m.name)
            material_set.add(m);materials.append(m.name)
            images.update(n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
        result[obj.name]=dict(points=points,tree=BVHTree.FromPolygons(points,faces),triangles=len(faces),materials=sorted(materials))
    assert len(result)==meta['meshes'] and sum(x['triangles'] for x in result.values())==meta['triangles']<40000
    texture_pixels={}
    if check_textures:
        signatures={}
        for im in images:
            values=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(values)
            pixels=np.rint(np.clip(values.astype(np.float64),0,1)*255).astype(np.uint8).tobytes()
            signatures[im]=(tuple(im.size),hashlib.sha256(pixels).hexdigest())
        def inputs(socket):
            found=set();pending=[link.from_node for link in socket.links];seen=set()
            while pending:
                node=pending.pop()
                if node in seen:continue
                seen.add(node)
                if node.type=='TEX_IMAGE':found.add(signatures[node.image])
                else:pending.extend(link.from_node for inp in node.inputs for link in inp.links)
            return sorted(found)
        texture_pixels['images']=sorted(signatures.values())
        texture_pixels['bindings']=sorted((m.name,slot,inputs(m.node_tree.nodes.get('Principled BSDF').inputs[slot])) for m in material_set for slot in ['Base Color','Roughness','Metallic','Normal'])
    # Physical support graph includes surface intersections and contained parts.
    def inside(t,p):
        q,n,_,_=t.find_nearest(p);return q is not None and n.dot(p-q)<-1e-5
    names=list(result)
    bounds={name:([min(p[a] for p in result[name]['points']) for a in range(3)],[max(p[a] for p in result[name]['points']) for a in range(3)]) for name in names}
    graph={n:set() for n in names}
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if any(bounds[a][1][axis]<bounds[b][0][axis]-1e-7 or bounds[b][1][axis]<bounds[a][0][axis]-1e-7 for axis in range(3)):continue
            x=result[a];y=result[b]
            if x['tree'].overlap(y['tree']) or any(inside(y['tree'],p) for p in x['points']) or any(inside(x['tree'],p) for p in y['points']):graph[a].add(b);graph[b].add(a)
    reached={names[0]};pending=[names[0]]
    while pending:
        for name in graph[pending.pop()]-reached:reached.add(name);pending.append(name)
    assert len(reached)==len(names),('Unsupported geometry',set(names)-reached)
    if meta['culture']=='terran':
        if meta['role']=='terraform':assert sum('coarse cutter tooth' in n for n in names)==12 and sum('one horizontal milling drum' in n for n in names)==1
        else:assert sum('broad lifting jaw' in n for n in names)==2 and sum('bronze welding tip' in n for n in names)==1
    return result,texture_pixels

def render(label,media):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.device='CPU';scene.cycles.use_denoising=True;scene.cycles.denoising_use_gpu=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.render.film_transparent=True
    scene.world=bpy.data.worlds.new('Proposal review studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    bpy.ops.object.camera_add();scene.camera=bpy.context.object;scene.camera.data.type='ORTHO'
    for location,power,size in [((4,-6,8),1000,5),((-5,-2,4),650,4),((2,5,7),1000,4)]:
        bpy.ops.object.light_add(type='AREA',location=location);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    points=[o.matrix_world@Vector(v) for o in scene.objects if o.type=='MESH' for v in o.bound_box];centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)]);renders={}
    for view,direction in [('front-quarter',(8,-10,7)),('rear-quarter',(-8,10,7)),('top',(0,-.01,12))]:
        d=Vector(direction).normalized();scene.camera.location=centre+d*15;scene.camera.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[scene.camera.matrix_world.inverted()@p for p in points];mid=Vector(((max(p.x for p in q)+min(p.x for p in q))/2,(max(p.y for p in q)+min(p.y for p in q))/2,0));scene.camera.location+=scene.camera.rotation_euler.to_matrix()@mid;scene.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2
        path=media/(label+'-'+view+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()));renders[path.name]=sha(path)
    return renders

def motion_samples(meta):
    samples={}
    for frame in [1,13,25,49,73,97]:
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();samples[frame]=snapshot(meta,False)[0]
    moving=[]
    for name,part in samples[1].items():
        displacement=max((p-q).length for frame in samples for p,q in zip(part['points'],samples[frame][name]['points']))
        if displacement>1e-4:moving.append(name)
    assert moving,'No geometry moves during ToolOperation'
    assert any(n not in moving for n in samples[1]),'Hull must remain stationary'
    endpoint=max((p-q).length for name in samples[1] for p,q in zip(samples[1][name]['points'],samples[97][name]['points']))
    assert endpoint<1e-5,('Non-looping preview',endpoint)
    bpy.context.scene.frame_set(1)
    return samples,moving


def compare_samples(native,imported):
    error=0
    for frame in native:
        for name,x in native[frame].items():
            y=imported[frame][name]
            error=max(error,max(y['tree'].find_nearest(p)[3] for p in x['points']),max(x['tree'].find_nearest(p)[3] for p in y['points']))
    assert error<1e-5,('Native/import animation mismatch',error)
    return error


def playback(label,media):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8
    scene.render.resolution_x=scene.render.resolution_y=256
    # Use the already verified front-quarter camera and studio, with fixed framing.
    render_camera=scene.camera;d=Vector((8,-10,7)).normalized()
    points=[o.matrix_world@Vector(v) for o in scene.objects if o.type=='MESH' for v in o.bound_box]
    centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)])
    render_camera.location=centre+d*15;render_camera.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();render_camera.data.ortho_scale=max((max(p[a] for p in points)-min(p[a] for p in points)) for a in range(3))*1.5
    frames=media/(label+'-frames');frames.mkdir(exist_ok=True)
    for i,frame in enumerate(range(1,97,4)):
        scene.frame_set(frame);scene.render.filepath=str(frames/(str(i).zfill(3)+'.png'));bpy.ops.render.render(write_still=True)
    scene.frame_set(1)


def main():
    p=argparse.ArgumentParser();p.add_argument('--culture',required=True);p.add_argument('--role',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);folder=ROOT/'sources/proposals/engineering-ships'/a.culture/a.role;media=ROOT/'gallery/media/proposals/engineering-ships'/a.culture/a.role;media.mkdir(parents=True,exist_ok=True);meta=json.loads((folder/'model.json').read_text())
    assert meta['status']=='proposed-assets-awaiting-mechanics' and not any(meta[k] for k in ['legacy_unit','runtime_integration','mechanics_available','blueprint_registered','package_registered'])
    assert meta['revision']==2 and sha(ROOT/meta['refinement_helper'])==meta['refinement_helper_sha256']
    assert sha(ROOT/meta['author'])==meta['author_sha256'] and sha(ROOT/meta['helper'])==meta['helper_sha256'] and sha(ROOT/meta['concept']['image'])==meta['concept']['sha256']
    for ext,h in meta['binaries'].items():assert sha(folder/('model.'+ext))==h
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False);native,ni=snapshot(meta);native_samples,native_moving=motion_samples(meta);renders=render('native',media);playback('native',media)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'));imported,ii=snapshot(meta);imported_samples,imported_moving=motion_samples(meta);motion_error=compare_samples(native_samples,imported_samples);assert set(native_moving)==set(imported_moving);assert ni==ii,('PBR image pixels differ',ni,ii);assert native.keys()==imported.keys();error=0
    for name,x in native.items():
        y=imported[name];assert x['triangles']==y['triangles'] and x['materials']==y['materials'];error=max(error,max(y['tree'].find_nearest(p)[3] for p in x['points']),max(x['tree'].find_nearest(p)[3] for p in y['points']))
    assert error<1e-5;renders.update(render('imported',media));playback('imported',media);raw=(folder/'model.glb').read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]]);assert len(doc.get('animations',[]))==1 and doc['animations'][0]['name']=='ToolOperation' and all('bufferView' in i for i in doc['images']);assert len(doc['animations'][0]['channels'])==len(meta['clips'][0]['motion'])
    report=dict(issue=265,culture=a.culture,role=a.role,binaries=meta['binaries'],metadata_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),revision=2,pbr_texture_pixels_equal=True,positive_closed_meshes=len(native),triangles=meta['triangles'],connected_support_graph=True,texture_pixels_equal=True,embedded_images=len(doc['images']),maximum_bidirectional_surface_error=error,opaque_nonemissive=True,motion_frames=list(native_samples),moving_parts=native_moving,maximum_animation_surface_error=motion_error,exported_animation_channels=len(doc['animations'][0]['channels']),renders=renders,runtime_integration=False,final_user_artistic_acceptance=False,limitations='Animated authored proposal;not a recovered legacy unit. ToolOperation is an asset demonstration. Game scale,production,blueprints,hangar transit and game mechanics are not certified. Visual comparison with supplied concept remains a separate review.')
    (folder/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n');print('PROPOSAL_RUNTIME_OK',a.culture,a.role,error,flush=True)

if __name__=='__main__':main()
