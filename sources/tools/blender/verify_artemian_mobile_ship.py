"""Actual native/import geometry, protected form, seated parts and rendered feedback."""
from pathlib import Path
import argparse,json,math,sys
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
sys.path.insert(0,str(Path(__file__).parent))
import remaster_artemian_mobile_ship as author
sys.path.insert(0,str(author.ROOT/'tools'))
from publication_support import clean_png
core=author.core


def geometry():
    result={};deps=bpy.context.evaluated_depsgraph_get()
    for o in core.meshes():
        evaluated=o.evaluated_get(deps);mesh=evaluated.to_mesh()
        result[o.name]=dict(points=[o.matrix_world@v.co for v in mesh.vertices],faces=[tuple(f.vertices) for f in mesh.polygons]);evaluated.to_mesh_clear()
    return result


def part_trees():
    result={}
    for o in core.meshes():
        points=[o.matrix_world@v.co for v in o.data.vertices]
        for group in o.vertex_groups:
            ids={v.index for v in o.data.vertices if any(w.group==group.index for w in v.groups)}
            faces=[tuple(f.vertices) for f in o.data.polygons if all(i in ids for i in f.vertices)]
            if faces:result[group.name]=BVHTree.FromPolygons(points,faces)
    return result


def render(path,direction):
    scene=bpy.context.scene;core.fit_camera(scene,core.evaluated_points(core.meshes()),direction);scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()))


def main(key):
    out,media=author.folders(key);meta=json.loads((out/'model.json').read_text());before={kind:core.sha(out/('model.'+kind)) for kind in ['blend','glb']}
    assert before==dict(blend=meta['blend_sha256'],glb=meta['glb_sha256'])
    assert meta['generator_sha256']==core.sha(Path(author.__file__)) and meta['recipe_sha256']==core.sha(out/'recipe.json')
    assert meta['shared_primitives_sha256']==core.sha(Path(core.__file__))
    baseline=author.ROOT/'sources'/meta['source']/'model.blend';assert core.sha(baseline)==meta['baseline_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(baseline),load_ui=False,use_scripts=False);original=geometry()
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False);native=geometry();trees=part_trees();length=max(b-a for a,b in zip(meta['baseline_bounds'][0],meta['baseline_bounds'][1]))
    errors={}
    for name,row in original.items():
        assert name in trees,('lost editable part',name)
        errors[name]=max(trees[name].find_nearest(author.transformed_reference_point(name,p,meta))[3] for p in row['points'][::8])
        assert errors[name]<length*.012,('source form deviation',name,errors[name],length)
    contacts=[]
    for pair in meta.get('attachment_pairs',[]):
        assert trees[pair['part']].overlap(trees[pair['support']]),('detached component',pair)
        contacts.append(pair)
    dents=[]
    for dent in meta.get('protected_dents',[]):
        if 'undented_point' in dent:
            target=author.transformed_reference_point(dent['part'],Vector(dent['undented_point']),meta);outward=Vector(dent['outward']).normalized()
            p,normal,index,distance=trees[dent['part']].ray_cast(target+outward*3,-outward,6);assert p is not None
            depth=(target-p).dot(outward)
        else:
            target=author.transformed_reference_point(dent['part'],Vector((dent['x'],dent['y'],dent['undented_z'])),meta)
            p,normal,index,distance=trees[dent['part']].ray_cast(Vector((target.x,target.y,3)),Vector((0,0,-1)),6);assert p is not None
            depth=target.z-p.z
        assert depth>=dent['minimum_depth'],('lost physical dent',dent,depth)
        dents.append(dict(part=dent['part'],measured_depth=depth))
    profile_checks=[]
    for constraint in meta.get('profile_constraints',[]):
        obj=next(o for o in core.meshes() if constraint['part'] in o.vertex_groups);group=obj.vertex_groups[constraint['part']]
        points=[obj.matrix_world@v.co for v in obj.data.vertices if any(w.group==group.index for w in v.groups)]
        front=min(p.y for p in points);width=max(p.x for p in points if p.y<front+.001)-min(p.x for p in points if p.y<front+.001);height=max(p.z for p in points)
        assert abs(front-constraint['front_y'])<.002 and abs(width-constraint['front_width'])<.015 and abs(height-constraint['maximum_z'])<.015,(constraint,front,width,height)
        fore_width=max(abs(p.x) for p in points if p.y<=constraint['fore_transition_y'])
        assert fore_width<=constraint['maximum_fore_half_width'],('flared upper prow',fore_width)
        profile_checks.append(dict(part=constraint['part'],front_y=front,front_width=width,maximum_z=height,maximum_fore_half_width=fore_width))
    closed=[]
    for o in core.meshes():
        bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),('open mesh',o.name);assert bm.calc_volume(signed=True)>0;bm.free();closed.append(o.name)
        assert o.data.uv_layers.active.name=='BraccatianWearAtlas'
    triangles=sum(len(r['faces']) for r in native.values());assert triangles==meta['triangles']<meta['max_triangles']
    render(media/'verified-native.png',core.VIEWS['front-quarter'])
    for o in list(bpy.context.scene.objects):
        if o.type in ['MESH','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/'model.glb'));imported=geometry();assert native.keys()==imported.keys();maximum=0
    for name in native:
        assert len(native[name]['faces'])==len(imported[name]['faces'])
        for a,b in [(native[name]['points'],imported[name]['points']),(imported[name]['points'],native[name]['points'])]:
            kd=KDTree(len(a))
            for i,p in enumerate(a):kd.insert(p,i)
            kd.balance();maximum=max(maximum,max(kd.find(p)[2] for p in b))
    assert maximum<1e-5
    render(media/'verified-imported.png',core.VIEWS['front-quarter'])
    for label,direction in core.VIEWS.items():render(media/(label+'.png'),direction)
    angle=meta['comparison_azimuth'];c=math.cos(angle);s=math.sin(angle)
    for frame,(x,y) in [(0,(1,-1)),(4,(1,0)),(8,(1,1)),(12,(0,1)),(16,(-1,1)),(28,(0,-1))]:render(media/f'heading-{frame:02}.png',(x*c-y*s,x*s+y*c,meta['comparison_elevation']))
    for o in core.meshes():
        mat=bpy.data.materials.new('Actual imported technical wireframe');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();wire=n.new('ShaderNodeWireframe');wire.use_pixel_size=True;wire.inputs['Size'].default_value=.5
        mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(0,0,0,1);mix.inputs[2].default_value=(.03,.55,.13,1);mat.node_tree.links.new(wire.outputs[0],mix.inputs[0]);em=n.new('ShaderNodeEmission');mat.node_tree.links.new(mix.outputs[0],em.inputs[0]);output=n.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],output.inputs[0]);o.data.materials.clear();o.data.materials.append(mat)
    render(media/'technical-wireframe.png',core.VIEWS['front-quarter'])
    assert before=={kind:core.sha(out/('model.'+kind)) for kind in before}
    report=dict(id=meta['id'],binaries=before,generator_sha256=meta['generator_sha256'],recipe_sha256=meta['recipe_sha256'],verifier_sha256=core.sha(Path(__file__)),baseline_sha256=meta['baseline_sha256'],relative_surface_deviation=max(errors.values())/length,part_surface_errors=errors,source_import_position_error=maximum,attachments_checked=contacts,protected_dents=dents,profile_checks=profile_checks,closed_native_batches=closed,triangles=triangles,mesh_batches=len(native),material_count=meta['material_count'],blender=bpy.app.version_string,renders={p.name:core.sha(p) for p in media.glob('*.png')},scope='Actual saved native and independent GLB import/render; baseline comparison includes the declared profile refinement. Visual legacy/concept assessment and client calibration separate. Comparative camera is an estimate, not a recovered gameplay heading transform.')
    (out/'runtime-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('ARTEMIAN_RUNTIME_VERIFIED',key,triangles,maximum,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ship',required=True);main(p.parse_args(sys.argv[sys.argv.index('--')+1:]).ship)
