"""Portable PBR colour export; procedural new-surface wear remains native."""
import bpy

def export_solid(root, meshes, output):
    links=[];defaults=[]
    for mat in set(m for ob in meshes for m in ob.data.materials if m):
        if not mat.use_nodes or not mat.name.startswith('Research '):continue
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if not bs:continue
        if mat.name.startswith('Research '):
            defaults.append((bs.inputs['Base Color'],bs.inputs['Base Color'].default_value[:]))
            # Representative worn base value, not a claimed procedural bake.
            bs.inputs['Base Color'].default_value=tuple(c*.72 for c in mat.diffuse_color[:3])+(1,)
        for slot in ['Base Color','Normal']:
            for link in list(bs.inputs[slot].links):
                links.append((mat.node_tree,link.from_socket,link.to_socket));mat.node_tree.links.remove(link)
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for ob in meshes:
        ob.select_set(True);parent=ob.parent
        while parent is not None:parent.select_set(True);parent=parent.parent
    bpy.ops.export_scene.gltf(filepath=str(output),use_selection=True,export_apply=True,
        export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
    for nt,a,b in links:nt.links.new(a,b)
    for socket,value in defaults:socket.default_value=value

if __name__=='__main__':
    import sys,json
    from pathlib import Path
    source=Path(sys.argv[sys.argv.index('--')+1]).resolve()
    bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1)
    model=json.loads((source.parent/'model.json').read_text())
    export_solid(bpy.data.objects['ShieldX40Root'],[bpy.data.objects[n] for ns in model['components'].values() for n in ns],source.with_suffix('.glb'))
