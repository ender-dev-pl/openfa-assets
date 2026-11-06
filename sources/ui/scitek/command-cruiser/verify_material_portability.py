"""Compare exported new-part image pixels, UV bindings and roughness."""
from pathlib import Path
from PIL import Image,ImageChops
from io import BytesIO
import sys,json,struct,hashlib
out=Path(sys.argv[1]);bindings=json.loads((out/'paint-input-bindings.json').read_text());raw=(out/'command-cruiser.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);offset=28+n
def pixels(texture):
 image=d['images'][d['textures'][texture['index']]['source']];view=d['bufferViews'][image['bufferView']];start=offset+view.get('byteOffset',0);return Image.open(BytesIO(raw[start:start+view['byteLength']])).convert('RGBA')
checks=[]
for node in d['nodes']:
 name=node.get('name');expected=bindings.get(name)
 if not expected:continue
 primitive=d['meshes'][node['mesh']]['primitives'][0];pbr=d['materials'][primitive['material']]['pbrMetallicRoughness'];textured='image' in expected['Base Color'];rough_error=0
 if textured:
  assert 'TEXCOORD_0' in primitive['attributes'];a=pixels(pbr['baseColorTexture']);b=Image.open(out/'packed-paint-inputs'/expected['Base Color']['image']).convert('RGBA');assert a.size==b.size and not ImageChops.difference(a,b).getbbox(alpha_only=False),name
 else:assert max(abs(a-b) for a,b in zip(pbr.get('baseColorFactor',[1,1,1,1]),expected['Base Color']['value']))<1e-6
 if 'image' in expected['Roughness']:
  a=pixels(pbr['metallicRoughnessTexture']).getchannel('G');b=Image.open(out/'packed-paint-inputs'/expected['Roughness']['image']).convert('RGB').getchannel('R');assert a.size==b.size;rough_error=ImageChops.difference(a,b).getextrema()[1];assert rough_error<=1
 else:assert abs(pbr.get('roughnessFactor',1)-expected['Roughness']['value'])<1e-6
 checks.append(dict(node=name,textured=textured,base_colour_verified=True,roughness_max_byte_error=rough_error))
assert len(checks)==15 and sum(x['textured'] for x in checks)==13
(out/'material-portability-verification.json').write_text(json.dumps(dict(glb_sha256=hashlib.sha256(raw).hexdigest(),new_part_materials=checks),indent=2)+'\n',encoding='utf-8');print('COMMAND_PORTABLE_MATERIALS_VERIFIED',len(checks))
