"""Verify MK2C's revised topology and real saved-native/imported render feedback."""
from pathlib import Path
import json,math,sys
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
import remaster_mikotaj_mobile_ships as author
from verify_mikotaj_mobile_remasters import geometry,render


def main():
    out,media=author.folders('falari-lourn');meta=json.loads((out/'model.json').read_text());patch=meta['geometry_refinement'];before={k:author.sha(out/('model.'+k)) for k in ['blend','glb']}
    assert patch['generator_sha256']==author.sha(author.ROOT/patch['generator'])
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False)
    native=geometry();assert len(native)==4
    body=bpy.data.objects['ParallelGreenModules'];pods=[];centres=[];ends=[]
    for i in range(4):
        group=body.vertex_groups['ParallelGreenModule'+str(i)];ids={v.index for v in body.data.vertices if any(w.group==group.index for w in v.groups)}
        points=[body.matrix_world@body.data.vertices[j].co for j in ids];low=[min(p[a] for p in points) for a in range(3)];high=[max(p[a] for p in points) for a in range(3)]
        centre=Vector(((low[0]+high[0])/2,0,(low[2]+high[2])/2));target=Vector((math.cos(i*math.pi/2)*.42,0,math.sin(i*math.pi/2)*.42))
        assert (centre-target).length<1e-5 and abs(low[1]+2.8)<1e-5 and abs(high[1]-2.8)<1e-5
        assert high[1]-low[1]>15*max(high[0]-low[0],high[2]-low[2])
        faces=[tuple(f.vertices) for f in body.data.polygons if all(v in ids for v in f.vertices)]
        pods.append(BVHTree.FromPolygons([body.matrix_world@v.co for v in body.data.vertices],faces));centres.append(list(centre));ends.append([low[1],high[1]])
    mounts=bpy.data.objects['ModuleMountsAndFixtures'];tree=author.core.tree(mounts)
    assert all(tree.overlap(pod) for pod in pods),'module detached from its mounts'
    assert tree.overlap(author.core.tree(bpy.data.objects['GlassyPressureSphere'])),'mounts detached from sphere'
    sphere=bpy.data.objects['GlassyPressureSphere'];assert max(abs(v.co.length-.4) for v in sphere.data.vertices)<1e-5
    shader=sphere.data.materials[0].node_tree.nodes.get('Principled BSDF');assert shader.inputs['Transmission Weight'].default_value>.7
    render(media/'verified-native.png',author.VIEWS['front-quarter'])
    for o in list(bpy.context.scene.objects):
        if o.type in ['MESH','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/'model.glb'));imported=geometry();assert native.keys()==imported.keys();error=0
    for name in native:
        assert len(native[name]['faces'])==len(imported[name]['faces'])
        for a,b in [(native[name]['points'],imported[name]['points']),(imported[name]['points'],native[name]['points'])]:
            kd=KDTree(len(a))
            for i,p in enumerate(a):kd.insert(p,i)
            kd.balance();error=max(error,max(kd.find(p)[2] for p in b))
    assert error<1e-5
    imported_glass=bpy.data.objects['GlassyPressureSphere'].data.materials[0].node_tree.nodes.get('Principled BSDF');assert imported_glass.inputs['Transmission Weight'].default_value>.7
    render(media/'verified-imported.png',author.VIEWS['front-quarter'])
    for label,direction in author.VIEWS.items():render(media/(label+'.png'),direction)
    for frame,direction in [(0,(1,-1,.40)),(4,(1,0,0)),(8,(1,1,.40)),(16,(-1,1,.40)),(28,(0,-1,0))]:render(media/f'heading-{frame:02}.png',direction)
    render(media/'axial-front.png',(0,-1,0));render(media/'axial-rear.png',(0,1,0))
    for o in author.meshes():
        mat=bpy.data.materials.new('Actual imported wireframe');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();w=n.new('ShaderNodeWireframe');w.use_pixel_size=True;w.inputs['Size'].default_value=.5
        mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(0,0,0,1);mix.inputs[2].default_value=(.03,.55,.13,1);mat.node_tree.links.new(w.outputs[0],mix.inputs[0]);e=n.new('ShaderNodeEmission');mat.node_tree.links.new(mix.outputs[0],e.inputs[0]);output=n.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(e.outputs[0],output.inputs[0]);o.data.materials.clear();o.data.materials.append(mat)
    render(media/'technical-wireframe.png',author.VIEWS['front-quarter'])
    assert before=={k:author.sha(out/('model.'+k)) for k in before}
    report=dict(id=meta['id'],binaries=before,generator_sha256=meta['generator_sha256'],verifier_path=Path(__file__).relative_to(author.ROOT).as_posix(),verifier_sha256=author.sha(Path(__file__)),revision_generator_sha256=patch['generator_sha256'],source_import_position_error=error,relative_surface_deviation=None,baseline_retention='Not applicable: user requested replacement of the incorrect continuous wing/opaque dome topology.',geometry_revision=meta['geometry_revision'],parallel_modules=4,module_centres=centres,common_longitudinal_extents=ends,spacing_degrees=90,seated_modules=4,sphere_radius=.4,imported_glass_transmission_verified=True,triangles=sum(len(r['faces']) for r in native.values()),mesh_batches=4,material_count=2,blender=bpy.app.version_string,renders={p.name:author.sha(p) for p in media.glob('*.png')},scope='Actual saved source and independent imported GLB, geometry/attachments/glass checked. Three rejected concepts remain recorded; artistic and game scaling/socket acceptance separate.')
    (out/'runtime-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('FALARI_RUNTIME_VERIFIED',json.dumps(report),flush=True)


if __name__=='__main__':main()
