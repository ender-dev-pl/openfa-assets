"""Rebuild MK2C from explicit legacy/user geometry constraints, not rejected stars."""
from pathlib import Path
import json,math,sys
import bpy,bmesh
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
import remaster_mikotaj_mobile_ships as author
core=author.core


def batch(name,items,root):
    bpy.ops.object.select_all(action='DESELECT')
    for o in items:
        group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
    bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
    transform=o.matrix_world.copy()
    for v in o.data.vertices:v.co=transform@v.co
    o.matrix_world=Matrix.Identity(4);o.parent=root
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for face in o.data.polygons:face.use_smooth=True
    return o


def pod(index,mat):
    angle=index*math.pi/2;radial=Vector((math.cos(angle),0,math.sin(angle)));tangent=Vector((-math.sin(angle),0,math.cos(angle)))
    # All four full pods use exactly the same fore/aft profile and point toward -Y.
    profile=[(-2.8,.003),(-2.65,.18),(-2.2,.65),(-1.5,.93),(-.5,1),(0,1),(1,.87),(2,.5),(2.65,.16),(2.8,.03)]
    vertices=[];n=24
    for y,f in profile:
        for j in range(n):
            t=j*math.tau/n;p=radial*.42+Vector((0,y,0))+tangent*(math.cos(t)*.115*f)+radial*(math.sin(t)*.045*f);vertices.append(tuple(p))
    faces=[]
    for i in range(len(profile)-1):
        for j in range(n):a=i*n+j;b=i*n+(j+1)%n;faces.append((a,b,b+n,a+n))
    faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+j for j in range(n))])
    mesh=bpy.data.meshes.new('Longitudinal pod '+str(index));mesh.from_pydata(vertices,[],faces);mesh.update()
    o=bpy.data.objects.new('ParallelGreenModule'+str(index),mesh);bpy.context.scene.collection.objects.link(o);core.assign_uv(o,mat,1)
    return o,radial,tangent


def main():
    out,media=author.folders('falari-lourn');meta=json.loads((out/'model.json').read_text());old={k:author.sha(out/('model.'+k)) for k in ['blend','glb']}
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False);bpy.context.preferences.filepaths.save_version=0
    # Preserve the existing lighting/camera, not the incorrect continuous-wing hull.
    for o in list(bpy.context.scene.objects):
        if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
    root=bpy.data.objects['PlacementRoot'];core.MAPS=author.MAPS;mat=core.material();mat.name='Mikotaj | worn green brass and structural alloy'
    pods=[];mounts=[];frame=[];axes=[]
    for index in range(4):
        o,radial,tangent=pod(index,mat);pods.append(o)
        axes.append(dict(index=index,azimuth_degrees=index*90,centre=list(radial*.42),forward=[0,-1,0],nose=list(radial*.42+Vector((0,-2.8,0))),aft=list(radial*.42+Vector((0,2.8,0)))))
        for y in [-.14,.14]:
            a=radial*.30+Vector((0,y,0));b=radial*.435+Vector((0,y,0));o=core.rod('Seated module bracket '+str(index),a,b,.024,mat,12);core.assign_uv(o,mat,5);mounts.append(o)
        p=radial*.466;rotation=Matrix((tangent,Vector((0,1,0)),radial)).transposed()
        o=core.box('Gold module fixture '+str(index),p,(.105,.30,.018),mat,rotation);core.assign_uv(o,mat,3);mounts.append(o)
        # Legacy side headings resolve brass regions flanking the central blue body.
        for y in [-.70,.70]:
            p=radial*.463+Vector((0,y,0));o=core.box('Flanking brass module fitting '+str(index),p,(.10,.17,.025),mat,rotation);core.assign_uv(o,mat,3);mounts.append(o)
        for y in [-1.35,1.35]:
            p=radial*.460+Vector((0,y,0));o=core.box('Sparse longitudinal service inset '+str(index),p,(.040,.46,.010),mat,rotation);core.assign_uv(o,mat,4);mounts.append(o)
        for y in [-.10,.10]:
            p=radial*.482+Vector((0,y,0));o=core.rod('Fixture pin '+str(index),p-radial*.009,p+radial*.009,.012,mat,10);core.assign_uv(o,mat,5);mounts.append(o)
        # Short internal load paths, visible through the sphere; no invented cockpit.
        o=core.rod('Internal radial load path '+str(index),radial*.06,radial*.32,.014,mat,12);core.assign_uv(o,mat,5);frame.append(o)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.075);o=bpy.context.object;o.name='Internal structural hub';core.assign_uv(o,mat,4);frame.append(o)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.40);o=bpy.context.object;o.name='Blue glass pressure sphere'
    glass=bpy.data.materials.new('Mikotaj | bluish glass sphere');glass.use_nodes=True;shader=glass.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(.10,.22,.52,1);shader.inputs['Roughness'].default_value=.13;shader.inputs['Metallic'].default_value=0;shader.inputs['Transmission Weight'].default_value=.72;shader.inputs['IOR'].default_value=1.46
    o.data.materials.append(glass);o.data.uv_layers.active.name='BraccatianWearAtlas'
    glass_batch=batch('GlassyPressureSphere',[o],root)
    batch('ParallelGreenModules',pods,root);batch('ModuleMountsAndFixtures',mounts,root);batch('InternalLoadFrame',frame,root)
    root['module_count']=4;root['module_axis']='All local -Y, positions every90 degrees around longitudinal axis';root['geometry_revision']='glass-sphere-parallel-modules'
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in author.meshes());assert triangles<55000 and len(author.meshes())==4
    bpy.context.scene.cycles.samples=40;bpy.context.scene.render.film_transparent=True
    author.fit_camera(bpy.context.scene,author.evaluated_points(author.meshes()),author.VIEWS['front-quarter'])
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.type in ['MESH','EMPTY']:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True,relative_remap=True)
    meta.update(triangles=triangles,final_bounds=author.bounds(author.meshes()),material_count=2,geometry_revision='glass-sphere-parallel-modules',attachments=[],blend_sha256=author.sha(out/'model.blend'),glb_sha256=author.sha(out/'model.glb'))
    meta['geometry_refinement']=dict(generator=Path(__file__).relative_to(author.ROOT).as_posix(),generator_sha256=author.sha(Path(__file__)),superseded_binary_hashes=old,module_axes=axes,sphere_radius=.40,radial_offset=.42,forward=[0,-1,0],legacy_target='MK2C frame28 and user corrections: glassy sphere and four elongated green modules at90 degrees, all parallel and pointing the same direction',concept_feedback='Three previous ImageGen concepts rejected as geometric authority; they do not override the explicit user/legacy constraints. No fourth generation.',interpretation='Module profiles, brackets, glass shader and internal support hub authored; no recovered hidden engineering or socket calibration claimed')
    meta['concept']='Retrospective ImageGen iterations1-3 reviewed and rejected geometrically; canonical correction follows explicit legacy/user constraints.'
    meta['editable_part_vertex_groups']={o.name:[g.name for g in o.vertex_groups] for o in author.meshes()}
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('FALARI_PARALLEL_MODULES',triangles,meta['final_bounds'],flush=True)


if __name__=='__main__':main()
