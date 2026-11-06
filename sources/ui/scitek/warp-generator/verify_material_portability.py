"""Compare GLB base-colour and roughness image pixels to packed native maps."""
import json,struct,hashlib,sys
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageChops
out=Path(sys.argv[1]);proof=json.loads((out/'anatomy-verification.json').read_text());raw=(out/'warp-generator.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);offset=28+n
def pixels(texture):
 im=d['images'][d['textures'][texture['index']]['source']];v=d['bufferViews'][im['bufferView']];start=offset+v.get('byteOffset',0);return Image.open(BytesIO(raw[start:start+v['byteLength']])).convert('RGBA')
checks=[]
for node in d['nodes']:
 name=node.get('name');expected=proof['new_part_paint_bindings'].get(name)
 if not expected:continue
 primitive=d['meshes'][node['mesh']]['primitives'][0];assert 'TEXCOORD_0' in primitive['attributes'];pbr=d['materials'][primitive['material']]['pbrMetallicRoughness']
 colour=pixels(pbr['baseColorTexture']);native=Image.open(out/'packed-paint-inputs'/expected['Base Color']).convert('RGBA');assert colour.size==native.size and not ImageChops.difference(colour,native).getbbox(alpha_only=False),name
 rough=pixels(pbr['metallicRoughnessTexture']).getchannel('G');native_rough=Image.open(out/'packed-paint-inputs'/expected['Roughness']).convert('RGB').getchannel('R');assert rough.size==native_rough.size;error=ImageChops.difference(rough,native_rough).getextrema()[1];assert error<=1,(name,error)
 checks.append(dict(node=name,base_colour_pixels_identical=True,roughness_max_byte_error=error,uv_binding_present=True))
assert len(checks)==9
(out/'material-portability-verification.json').write_text(json.dumps(dict(glb_sha256=hashlib.sha256(raw).hexdigest(),textured_nodes=checks),indent=2)+'\n',encoding='utf-8');print('WARP_PORTABLE_WEAR_VERIFIED',len(checks))
