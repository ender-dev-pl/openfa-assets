"""Actual saved-source/import GLB checks and same-heading render feedback."""
from pathlib import Path
import hashlib,json,math,sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
sys.path.insert(0,str(Path(__file__).parent))
import remaster_mikotaj_mobile_ships as author
sys.path.insert(0,str(author.ROOT/'tools'))
from publication_support import clean_png


def geometry():
    rows={};deps=bpy.context.evaluated_depsgraph_get()
    for o in author.meshes():
        eo=o.evaluated_get(deps);m=eo.to_mesh()
        rows[o.name]=dict(points=[o.matrix_world@v.co for v in m.vertices],faces=[tuple(f.vertices) for f in m.polygons])
        eo.to_mesh_clear()
    return rows


def render(path,direction):
    scene=bpy.context.scene;author.fit_camera(scene,author.evaluated_points(author.meshes()),direction)
    scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);path.write_bytes(clean_png(path.read_bytes()))


def main(key):
    out,media=author.folders(key);meta=json.loads((out/'model.json').read_text());before={k:author.sha(out/('model.'+k)) for k in ['blend','glb']}
    assert meta['blend_sha256']==before['blend'] and meta['glb_sha256']==before['glb']
    assert meta['generator_sha256']==author.sha(Path(author.__file__))
    assert meta['shared_primitives_sha256']==author.sha(Path(author.core.__file__))
    # Test source silhouette retention geometrically against actual earlier meshes.
    baseline=author.ROOT/'sources'/meta['source']/'model.blend';assert author.sha(baseline)==meta['baseline_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(baseline),load_ui=False,use_scripts=False)
    scale=meta['z_scale']
    basepoints=[Vector((p.x,p.y,p.z*scale)) for row in geometry().values() for p in row['points']][::8]
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False)
    native=geometry();points=[p for r in native.values() for p in r['points']];faces=[];offset=0
    for r in native.values():faces.extend(tuple(i+offset for i in f) for f in r['faces']);offset+=len(r['points'])
    tree=BVHTree.FromPolygons(points,faces);length=max(meta['baseline_bounds'][1][a]-meta['baseline_bounds'][0][a] for a in range(3))
    distances=[tree.find_nearest(p)[3] for p in basepoints];error=max(distances)
    assert error<length*.012,('silhouette deviation',key,error,length)
    for attachment in meta['attachments']:
        distance=tree.find_nearest(Vector(attachment['point']))[3];assert distance<.012,('detached service machinery',attachment,distance)
    assert len(native)==4
    triangles=sum(len(r['faces']) for r in native.values());assert triangles==meta['triangles'] and triangles<55000
    for o in author.meshes():
        assert len(o.data.materials)==1 and o.data.uv_layers.active.name=='BraccatianWearAtlas'
        assert len(o.vertex_groups)>0
    # Bound imported/source acceptance to rendered source with identical framing.
    render(media/'verified-native.png',author.VIEWS['front-quarter'])
    for o in list(bpy.context.scene.objects):
        if o.type in ['MESH','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/'model.glb'));imported=geometry();assert native.keys()==imported.keys()
    max_error=0
    for name in native:
        for a,b in [(native[name]['points'],imported[name]['points']),(imported[name]['points'],native[name]['points'])]:
            kd=KDTree(len(a))
            for i,p in enumerate(a):kd.insert(p,i)
            kd.balance();max_error=max(max_error,max(kd.find(p)[2] for p in b))
        assert len(native[name]['faces'])==len(imported[name]['faces'])
    assert max_error<1e-5
    render(media/'verified-imported.png',author.VIEWS['front-quarter'])
    # These sheets do not share the same first azimuth. Match the actual nose/
    # aft openings across opposite headings; do not rotate the canonical asset.
    heading_offset=meta['heading_angle']
    # Source metadata holds initial framing estimates. Refine comparison-only
    # elevation after inspecting imported renders, without altering the model.
    comparison_elevation={'hiero':.9,'falari-lourn':.5}.get(key,meta['comparison_elevation'])
    for frame,direction in [(0,(1,-1,.65)),(4,(1,0,.65)),(8,(1,1,.65)),(16,(-1,1,.65))]:
        x,y,z=direction;c=math.cos(heading_offset);s=math.sin(heading_offset);direction=(x*c-y*s,x*s+y*c,comparison_elevation)
        render(media/f'heading-{frame:02}.png',direction)
    # The technical view comes from exactly the imported meshes, not another model.
    for o in author.meshes():
        mat=bpy.data.materials.new('Technical imported '+o.name);mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();wire=nodes.new('ShaderNodeWireframe');wire.use_pixel_size=True;wire.inputs['Size'].default_value=.55
        mix=nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(0,0,0,1);mix.inputs[2].default_value=(.03,.55,.13,1);mat.node_tree.links.new(wire.outputs[0],mix.inputs[0]);em=nodes.new('ShaderNodeEmission');mat.node_tree.links.new(mix.outputs[0],em.inputs[0]);output=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],output.inputs[0]);o.data.materials.clear();o.data.materials.append(mat)
    render(media/'technical-wireframe.png',author.VIEWS['front-quarter'])
    for p in media.glob('*.png'):p.write_bytes(clean_png(p.read_bytes()))
    assert before=={k:author.sha(out/('model.'+k)) for k in before}
    report=dict(id=meta['id'],binaries=before,generator_sha256=author.sha(Path(author.__file__)),verifier_sha256=author.sha(Path(__file__)),baseline_sha256=meta['baseline_sha256'],baseline_surface_samples=len(basepoints),maximum_surface_deviation=error,relative_surface_deviation=error/length,source_import_position_error=max_error,triangles=triangles,mesh_batches=4,attachments_checked=len(meta['attachments']),legacy_comparison_azimuth_offset=heading_offset,blender=bpy.app.version_string,renders={p.name:author.sha(p) for p in media.glob('*.png')},scope='Actual saved native source and imported GLB; legacy comparisons require visual review. Proposed size/hidden details and runtime calibration are not recovered facts.')
    report['legacy_comparison_elevation']=comparison_elevation
    (out/'runtime-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('MIKOTAJ_RUNTIME_VERIFIED',key,report,flush=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--ship',choices=author.CASES,required=True)
    main(p.parse_args(sys.argv[sys.argv.index('--')+1:]).ship)
