"""New-part paint wear remains actual base-colour texture data in runtime GLB."""
from pathlib import Path
from PIL import Image,ImageChops
from io import BytesIO
import sys,json,struct,hashlib
out=Path(sys.argv[1]);inputs=Path(sys.argv[2]);raw=(out/'stasis-missile.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+length]);binary=20+length+8;expected={'Tachyon dispersion pod':'pod-maroon.png','Guidance fin':'fin-green.png'};checks=[]
for node in d['nodes']:
 prefix=next((p for p in expected if node.get('name','').startswith(p)),None)
 if prefix is None:continue
 mesh=d['meshes'][node['mesh']];assert len(mesh['primitives'])==1;primitive=mesh['primitives'][0];assert 'TEXCOORD_0' in primitive['attributes']
 material=d['materials'][primitive['material']];texture=material['pbrMetallicRoughness']['baseColorTexture'];image=d['images'][d['textures'][texture['index']]['source']];view=d['bufferViews'][image['bufferView']];start=binary+view.get('byteOffset',0);pixels=Image.open(BytesIO(raw[start:start+view['byteLength']])).convert('RGBA');source=Image.open(inputs/expected[prefix]).convert('RGBA');assert source.size==pixels.size and not ImageChops.difference(source,pixels).getbbox(alpha_only=False)
 checks.append(dict(node=node['name'],input=expected[prefix],exported_wear_pixels_identical=True))
assert sum(x['node'].startswith('Tachyon') for x in checks)==6 and sum(x['node'].startswith('Guidance') for x in checks)==4
(out/'material-portability-verification.json').write_text(json.dumps(dict(glb_sha256=hashlib.sha256(raw).hexdigest(),verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),texture_input_sha256={n:hashlib.sha256((inputs/n).read_bytes()).hexdigest() for n in expected.values()},textured_nodes=checks),indent=2)+'\n',encoding='utf-8');print('STASIS_PORTABLE_WEAR_VERIFIED',len(checks))
