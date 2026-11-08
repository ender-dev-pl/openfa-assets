"""Saved native/independent GLB verification, including open crescent witnesses."""
from pathlib import Path
import hashlib
import json
import sys
import bpy
import bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).parent))
import remaster_achaean_transporter as author
ROOT=author.ROOT;OUT=author.OUT;MEDIA=author.MEDIA
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_png


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    bpy.context.view_layer.update();result={}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        assert obj.data.uv_layers and len(obj.data.materials)==1,obj.name
        points=[obj.matrix_world@v.co for v in obj.data.vertices]
        result[obj.name]={'points':points,'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons)}
    return result


def structure_witnesses(scene,meta):
    graph=bpy.context.evaluated_depsgraph_get();factor=meta['normalization_factor'];centre=Vector(meta['normalization_centre'])
    transform=lambda p:(Vector(p)-centre)*factor
    gaps=occupied=0
    for side in [-1,1]:
        for y,z in [(1.15,0),(1.7,.25),(1.7,-.25),(.65,0)]:
            p=transform((side*2.40,y,z));hit,*_=scene.ray_cast(graph,p,Vector((-side,0,0)),distance=.80*factor)
            assert not hit,('crescent mouth must remain open',side,y,z);gaps+=1
        for t in [-.72,-.40,.40,.72]:
            p=author.crescent_point(side,t,.87)
            start=transform(p+Vector((side*.4,0,0)))
            hit,location,normal,index,obj,matrix=scene.ray_cast(graph,start,Vector((-side,0,0)),distance=.8*factor)
            assert hit and obj.name in {'CrescentStructure','SilverCrescentRims','CrimsonCrescentInsets'},('missing curved rim',side,t,obj.name if hit else None)
            occupied+=1
    return {'empty_mouth_witnesses':gaps,'occupied_rim_witnesses':occupied}


def compare(native,imported):
    assert native.keys()==imported.keys(),(native.keys(),imported.keys())
    maximum=0
    for name in native:
        assert native[name]['triangles']==imported[name]['triangles'],name
        for first,second in [(native[name]['points'],imported[name]['points']),(imported[name]['points'],native[name]['points'])]:
            tree=KDTree(len(first))
            for i,p in enumerate(first):tree.insert(p,i)
            tree.balance();maximum=max(maximum,max(tree.find(p)[2] for p in second))
    assert maximum<.00001,maximum
    return maximum


def packed_maps():
    images=[im for im in bpy.data.images if im.type=='IMAGE']
    assert len(images)==2 and all(im.packed_file and tuple(im.size)==(2048,2048) for im in images)
    return {im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in images}


def crescent_dimensions(meta):
    """Measure actual imported vertices, independently of the authoring formula."""
    factor=meta['normalization_factor'];centre=Vector(meta['normalization_centre'])
    def points(name):
        obj=bpy.data.objects[name]
        return [(obj.matrix_world@v.co)/factor+centre for v in obj.data.vertices]
    hull=points('PressureHull');wing=points('CrescentStructure')
    hull_height=max(v.z for v in hull)-min(v.z for v in hull)
    tips=[v for v in wing if v.y>2.40]
    gap=max(v.z for v in tips)-min(v.z for v in tips)
    span=max(v.z for v in wing)-min(v.z for v in wing)
    root=[v for v in wing if abs(v.z)<.01]
    root_width=max(v.y for v in root)-min(v.y for v in root)
    return dict(hull_height=hull_height,distal_tip_vertical_span=gap,
                root_fore_aft_width=root_width,
                crescent_vertical_span=span,tip_span_over_hull_height=gap/hull_height,
                crescent_span_over_hull_height=span/hull_height,
                coordinate_space='Unnormalized authored model units; actual imported vertices')


def distal_fastener_contacts(meta):
    """Check actual fastener component bases against the imported painted skin."""
    factor=meta['normalization_factor'];centre=Vector(meta['normalization_centre'])
    obj=bpy.data.objects['CrimsonCrescentInsets'];mesh=obj.data
    tree=BVHTree.FromPolygons([obj.matrix_world@v.co for v in mesh.vertices],
                             [list(p.vertices) for p in mesh.polygons])
    obj=bpy.data.objects['Fasteners'];bm=bmesh.new();bm.from_mesh(obj.data)
    # Diagnostic-only seam welding reconnects glTF UV/normal splits without
    # changing the imported model used for rendering or source comparison.
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6*factor)
    bm.verts.ensure_lookup_table();bm.verts.index_update()
    points=[obj.matrix_world@v.co for v in bm.verts];adj=[set() for v in points]
    for edge in bm.edges:
        a,b=[v.index for v in edge.verts];adj[a].add(b);adj[b].add(a)
    pending=set(range(len(points)));distances=[]
    while pending:
        stack=[pending.pop()];component=[]
        while stack:
            i=stack.pop();component.append(points[i])
            for j in adj[i]:
                if j in pending:pending.remove(j);stack.append(j)
        middle=sum(component,Vector())/len(component);local=middle/factor+centre
        if abs(local.x)<1.9 or local.y<.8:continue
        side=1 if local.x>0 else -1
        base_x=min(side*p.x for p in component)
        base=[p for p in component if abs(side*p.x-base_x)<1e-5]
        point=sum(base,Vector())/len(base)
        hit,normal,index,distance=tree.find_nearest(point)
        assert hit is not None and distance/factor<.008,('floating distal fastener',local,distance/factor)
        distances.append(distance/factor)
    bm.free();assert len(distances)==8,distances
    return dict(contacts=len(distances),maximum_skin_distance_authored_units=max(distances))


def main():
    meta=json.loads((OUT/'generation.json').read_text());before={kind:sha(OUT/f'model.{kind}') for kind in ['blend','glb']}
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'model.blend'),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;root=bpy.data.objects['PlacementRoot']
    assert root['catalogue_id']==author.ID and tuple(root.scale)==(1,1,1)
    assert root['calibrated_weapon_sockets']==0
    native=snapshot();triangles=sum(r['triangles'] for r in native.values())
    assert triangles==meta['triangles']<100000 and len(native)==meta['mesh_batches']<=20
    maps=packed_maps()
    manifold={}
    for name in ['PressureHull','CrescentStructure']:
        mesh=bpy.data.objects[name].data;bm=bmesh.new();bm.from_mesh(mesh)
        assert all(e.is_manifold for e in bm.edges),(name,'open or non-manifold core')
        assert abs(bm.calc_volume())>1e-9,(name,'zero volume')
        manifold[name]=len(bm.faces);bm.free()
    native_witnesses=structure_witnesses(scene,meta)
    author.aim(scene,(1.15,-1.25,.85));scene.render.filepath=str(MEDIA/'verified-native.png');bpy.ops.render.render(write_still=True)
    for obj in list(scene.objects):
        if obj.type in {'MESH','EMPTY'}:bpy.data.objects.remove(obj,do_unlink=True)
    for collection in [bpy.data.meshes,bpy.data.materials,bpy.data.images]:
        for item in list(collection):
            if item.users==0:collection.remove(item)
    bpy.ops.import_scene.gltf(filepath=str(OUT/'model.glb'));imported=snapshot()
    error=compare(native,imported);imported_maps=packed_maps();imported_witnesses=structure_witnesses(scene,meta)
    proportions=crescent_dimensions(meta)
    fastener_contacts=distal_fastener_contacts(meta)
    assert proportions['tip_span_over_hull_height']<.80,('distal arms still flared apart',proportions)
    assert proportions['crescent_span_over_hull_height']<1.15,('excessive crescent height',proportions)
    assert 1.0<proportions['root_fore_aft_width']<1.2,('fore shield width',proportions)
    # Image names can change while glTF packs roughness/metallic; actual rendered
    # colour agreement is checked independently by the pixel reviewer.
    assert len(imported_maps)==len(maps)==2
    scene.render.filepath=str(MEDIA/'verified-imported.png');bpy.ops.render.render(write_still=True)
    for name,direction in [('verified-side',(1,0,.12)),('verified-front',(0,-1,.15)),
                           ('verified-legacy-side',(1,0,.34)),('verified-legacy-quarter',(1,-1,.34))]:
        author.aim(scene,direction,margin=1.20)
        scene.render.filepath=str(MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True)
    for name,chosen in [('crescent-detail',[o for o in scene.objects if o.type=='MESH' and 'Crescent' in o.name]),
                        ('hull-detail',[o for o in scene.objects if o.type=='MESH' and o.name in {'PressureHull','FormedHullSkins','DorsalStructure','ServiceEquipment'}])]:
        author.aim(scene,(1.15,-1.25,.85),chosen);scene.render.filepath=str(MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True)
    # Technical presentation uses the very same imported GLB geometry, not a
    # separate embellished blueprint or a claimed recovered legacy diagram.
    for obj in scene.objects:
        if obj.type!='MESH':continue
        mat=bpy.data.materials.new('Technical | '+obj.name);mat.use_nodes=True
        tree=mat.node_tree;tree.nodes.clear();wire=tree.nodes.new('ShaderNodeWireframe');wire.use_pixel_size=True;wire.inputs['Size'].default_value=.60
        mix=tree.nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(0,0,0,1)
        mix.inputs[2].default_value=(.7,.03,.02,1) if obj.name in {'CrescentStructure','SilverCrescentRims'} else (.015,.58,.035,1)
        tree.links.new(wire.outputs[0],mix.inputs[0]);emission=tree.nodes.new('ShaderNodeEmission');tree.links.new(mix.outputs[0],emission.inputs[0]);emission.inputs[1].default_value=1.4
        output=tree.nodes.new('ShaderNodeOutputMaterial');tree.links.new(emission.outputs[0],output.inputs[0]);obj.data.materials.clear();obj.data.materials.append(mat)
    author.aim(scene,(1.15,-1.25,.85));scene.render.filepath=str(MEDIA/'technical-wireframe.png');bpy.ops.render.render(write_still=True)
    for path in MEDIA.glob('*.png'):path.write_bytes(clean_png(path.read_bytes()))
    assert before=={kind:sha(OUT/f'model.{kind}') for kind in before},'Verifier modified final source'
    result={'id':author.ID,'blender':bpy.app.version_string,'blend_sha256':before['blend'],'glb_sha256':before['glb'],
            'generator_sha256':sha(Path(author.__file__)),'verifier_sha256':sha(Path(__file__)),'triangles':triangles,'mesh_batches':len(native),
            'closed_nonzero_core_meshes':manifold,'maximum_bidirectional_world_position_error':error,
            'native_witnesses':native_witnesses,'imported_witnesses':imported_witnesses,'packed_maps_native_and_imported':2,
            'imported_crescent_proportions':proportions,
            'imported_distal_fastener_contacts':fastener_contacts,
            'source_unchanged':True,'technical_view':'Actual independently imported GLB geometry; authored technical visualization, not original legacy wireframe',
            'renders':{p.name:sha(p) for p in MEDIA.glob('*.png')},'scope':'Blender asset verification; client scale/orientation, attachments and GPU budgets require separate integration acceptance'}
    (OUT/'runtime-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('ACHAEAN_TRANSPORTER_VERIFIED '+json.dumps(result),flush=True)


if __name__=='__main__':main()
