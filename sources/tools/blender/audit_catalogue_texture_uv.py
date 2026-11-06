"""Audit reachable image dependencies and UV availability; never edits saved assets."""
import hashlib
import json
import math
from pathlib import Path
import struct
import bpy

REPO=Path(__file__).resolve().parents[2]
OUTPUT=REPO/'docs/assets/reconstruction/evidence/catalogue-texture-uv'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def reachable_images(material):
    if not material.use_nodes: return [],[]
    pending=[n for n in material.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
    seen=set();images=[];unknown=[]
    while pending:
        node=pending.pop()
        if node in seen: continue
        seen.add(node)
        if node.type=='TEX_IMAGE': images.append(node)
        if node.type=='GROUP': unknown.append('uninspected node group '+node.name)
        pending.extend(link.from_node for socket in node.inputs for link in socket.links)
    return images,unknown


def coordinate_sources(socket,seen=None):
    seen=set() if seen is None else seen
    if not socket.is_linked: return {('uv','')}
    result=set()
    for link in socket.links:
        node=link.from_node
        if node in seen: continue
        seen.add(node)
        if node.type=='UVMAP': result.add(('uv',node.uv_map))
        elif node.type=='TEX_COORD': result.add(('uv','') if link.from_socket.name=='UV' else ('non_uv',link.from_socket.name))
        elif node.type in ['MAPPING','VECT_MATH','REROUTE']:
            linked=[s for s in node.inputs if s.is_linked]
            if not linked: result.add(('unknown',node.type))
            for upstream in linked: result.update(coordinate_sources(upstream,seen))
        else: result.add(('unknown',node.type))
    return result or {('unknown','cycle or unresolved source')}


def native_dependencies(folder):
    graph=bpy.context.evaluated_depsgraph_get();objects={};images={};issues=[];unknown=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or obj.get('preview_only'): continue
        evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
        active=next((u.name for u in mesh.uv_layers if u.active_render),mesh.uv_layers.active.name if mesh.uv_layers.active else None)
        layers={u.name:dict(loops=len(u.data),nonfinite=sum(not all(math.isfinite(v) for v in item.uv) for item in u.data)) for u in mesh.uv_layers}
        for name,data in layers.items():
            if data['loops']!=len(mesh.loops) or data['nonfinite']: issues.append(obj.name+': malformed UV '+name)
        required=set();used_materials=[]
        for index in sorted({p.material_index for p in mesh.polygons}):
            if index>=len(mesh.materials) or mesh.materials[index] is None:
                issues.append(obj.name+': missing assigned material');continue
            material=mesh.materials[index];used_materials.append(material.name)
            nodes,unresolved=reachable_images(material);unknown.extend(material.name+': '+v for v in unresolved)
            for node in nodes:
                image=node.image
                if image is None: issues.append(material.name+': connected image node has no image');continue
                if image.name not in images:
                    packed=image.packed_file
                    item=dict(source=image.source,packed=bool(packed),size=list(image.size),filepath=image.filepath)
                    if packed: item['packed_sha256']=hashlib.sha256(packed.data).hexdigest()
                    if image.source=='FILE' and not packed: issues.append('External unembedded native image '+image.name)
                    elif image.source not in ['FILE','GENERATED','VIEWER']: unknown.append('Uninspected native image source '+image.source)
                    candidate=folder/Path(image.filepath).name
                    if candidate.is_file() and packed:
                        item['source_file']=str(candidate.relative_to(REPO)).replace('\\','/')
                        item['source_file_sha256']=sha(candidate)
                        item['source_bytes_match_packed']=item['source_file_sha256']==item['packed_sha256']
                        if not item['source_bytes_match_packed']: issues.append('Packed/source image mismatch '+image.name)
                    images[image.name]=item
                for kind,name in coordinate_sources(node.inputs['Vector']):
                    if kind=='uv': required.add(name or active or '<missing active UV>')
                    elif kind=='unknown': unknown.append(material.name+': unresolved image coordinates '+name)
        for name in required:
            if name not in layers: issues.append(obj.name+': required UV absent '+name)
        objects[obj.name]=dict(materials=used_materials,uv_layers=layers,active_render_uv=active,required_uv_layers=sorted(required))
        evaluated.to_mesh_clear()
    return dict(objects=objects,images=images,issues=sorted(set(issues)),uninspected=sorted(set(unknown)))


def parse_glb(path):
    raw=path.read_bytes();magic,version,length=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and version==2 and length==len(raw)
    offset=12;document=None;binary=b''
    while offset<len(raw):
        size,kind=struct.unpack_from('<II',raw,offset);offset+=8
        chunk=raw[offset:offset+size];assert len(chunk)==size;offset+=size
        if kind==0x4e4f534a: document=json.loads(chunk)
        elif kind==0x004e4942: binary=chunk
    assert document is not None
    return document,binary


def uv_accessor(document,binary,index):
    accessor=document['accessors'][index]
    if 'sparse' in accessor or 'bufferView' not in accessor: return dict(status='uninspected sparse/implicit accessor')
    view=document['bufferViews'][accessor['bufferView']]
    if view.get('buffer',0)!=0: return dict(status='uninspected nonprimary buffer')
    formats={5126:'f',5123:'H',5121:'B'};component=accessor['componentType']
    if accessor['type']!='VEC2' or component not in formats: return dict(status='unsupported UV representation')
    fmt='<2'+formats[component];width=struct.calcsize(fmt);stride=view.get('byteStride',width)
    relative=accessor.get('byteOffset',0);start=view.get('byteOffset',0)+relative;count=accessor['count']
    needed=relative+(count-1)*stride+width if count else relative
    assert stride>=width and needed<=view['byteLength'] and start+(needed-relative)<=len(binary),'UV accessor outside embedded buffer'
    bad=sum(not all(math.isfinite(v) for v in struct.unpack_from(fmt,binary,start+i*stride)) for i in range(count))
    return dict(status='inspected',count=count,nonfinite=bad,component_type=component,normalized=accessor.get('normalized',False))


def texture_infos(value):
    if isinstance(value,dict):
        for key,child in value.items():
            if key.lower().endswith('texture') and isinstance(child,dict) and 'index' in child: yield child
            else: yield from texture_infos(child)
    elif isinstance(value,list):
        for child in value: yield from texture_infos(child)


def glb_dependencies(path):
    document,binary=parse_glb(path);issues=[];unknown=[];uvs={};requirements=0;primitive_uvs=[]
    for index,buffer in enumerate(document.get('buffers',[])):
        if buffer.get('uri') and not buffer['uri'].startswith('data:'): issues.append('External GLB buffer '+str(index))
        elif not buffer.get('uri') and buffer['byteLength']>len(binary): issues.append('Truncated GLB buffer '+str(index))
    for index,image in enumerate(document.get('images',[])):
        if 'bufferView' in image:
            view=document['bufferViews'][image['bufferView']]
            if view.get('buffer',0)!=0 or view.get('byteOffset',0)+view['byteLength']>len(binary): issues.append('Image outside primary embedded buffer '+str(index))
        elif not image.get('uri','').startswith('data:'): issues.append('External or missing GLB image '+str(index))
    for mesh_index,mesh in enumerate(document.get('meshes',[])):
        names=[n.get('name','<unnamed>') for n in document.get('nodes',[]) if n.get('mesh')==mesh_index]
        for primitive_index,primitive in enumerate(mesh['primitives']):
            needed_uvs=set();label=', '.join(names)+' primitive '+str(primitive_index)
            if 'material' not in primitive: continue
            material=document['materials'][primitive['material']]
            for texture in texture_infos(material):
                requirements+=1;tex=document['textures'][texture['index']]
                sources=[tex['source']] if 'source' in tex else [v['source'] for v in tex.get('extensions',{}).values() if isinstance(v,dict) and 'source' in v]
                if not sources: unknown.append('Unmapped GLB texture image source')
                for source in sources:
                    if not 0<=source<len(document.get('images',[])): issues.append('Texture references missing GLB image')
                uv=texture.get('extensions',{}).get('KHR_texture_transform',{}).get('texCoord',texture.get('texCoord',0))
                name='TEXCOORD_'+str(uv);needed_uvs.add(name)
                if name not in primitive['attributes']: issues.append(label+': required GLB '+name+' absent');continue
                index=primitive['attributes'][name]
                if str(index) not in uvs: uvs[str(index)]=uv_accessor(document,binary,index)
            if needed_uvs: primitive_uvs.append(dict(objects=names,primitive=primitive_index,required=sorted(needed_uvs),available=[k for k in primitive['attributes'] if k.startswith('TEXCOORD_')]))
    for index,data in uvs.items():
        if data['status']!='inspected': unknown.append('UV '+index+': '+data['status'])
        elif not data['count'] or data['nonfinite']: issues.append('Empty/nonfinite GLB UV '+index)
    return dict(materials=len(document.get('materials',[])),images=len(document.get('images',[])),
        texture_requirements=requirements,uv_accessors=uvs,primitive_uv_requirements=primitive_uvs,issues=sorted(set(issues)),uninspected=sorted(set(unknown)))


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True);inventory_path=REPO/'docs/reconstruction/models/inventory.json'
    records=json.loads(inventory_path.read_text())['records'];assert len(records)==303;rows=[]
    for index,record in enumerate(records):
        study=[s for s in record['available_studies'] if s['present']][-1]
        source=REPO/study['blend'];export=source.with_suffix('.glb');before=dict(blend_sha256=sha(source),glb_sha256=sha(export))
        assert before['blend_sha256']==study['sha256']
        bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1)
        native=native_dependencies(source.parent);gltf=glb_dependencies(export)
        assert before==dict(blend_sha256=sha(source),glb_sha256=sha(export))
        path=OUTPUT/f'{index:03}.json';data=dict(issue=1110,id=record['id'],category=record['category'],blend=study['blend'],
            **before,native=native,glb=gltf,source_assets_unchanged=True,final_visual_acceptance=False)
        path.write_text(json.dumps(data,indent=2)+'\n');rows.append(dict(id=record['id'],report=path.name,sha256=sha(path),
            native_images=len(native['images']),glb_images=gltf['images'],issues=len(native['issues'])+len(gltf['issues']),
            uninspected=len(native['uninspected'])+len(gltf['uninspected'])))
        print('CATALOGUE_TEXTURE_UV_INSPECTED',record['id'],rows[-1]['issues'],rows[-1]['uninspected'],flush=True)
    (OUTPUT/'summary.json').write_text(json.dumps(dict(issue=1110,blender=bpy.app.version_string,auditor_sha256=sha(Path(__file__)),
        inventory_sha256=sha(inventory_path),definitions=len(rows),records=rows,final_visual_acceptance=False,
        scope='Reachable native image dependencies, finite required UVs and embedded GLB texture/UV layout. No decoded pixel/material/render parity, UV distortion/seam quality or final art acceptance.'),indent=2)+'\n')
    print('CATALOGUE_TEXTURE_UV_AUDIT_OK',len(rows),flush=True)


if __name__=='__main__': main()
