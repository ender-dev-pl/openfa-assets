"""Validate heading images and assemble review sheets and animated previews."""
import hashlib
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

from directional_catalogue_rules import requires_rig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', help='Optional completed global types for visual review')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]/'docs/assets/bootstrap-3d/full-catalogue'
    records = [record for record in json.loads((root/'recipes.json').read_text(encoding='utf-8'))['buildings'] if requires_rig(record)]
    if args.ids:
        ids = set(map(int,args.ids.split(',')))
        records = [record for record in records if record['global_type'] in ids]
        assert len(records) == len(ids)
    report = []
    for record in records:
        output = root/record['culture']/record['preview'].lower()
        metadata = json.loads((output/'model.json').read_text(encoding='utf-8'))
        frames, digests = [], []
        sheet = Image.new('RGB',(1024,1024),(14,20,28))
        draw = ImageDraw.Draw(sheet)
        for index in range(16):
            path = output/'directions'/f'{index:02}.png'
            frame = Image.open(path).convert('RGBA')
            assert frame.size == (512,512)
            bounds = frame.getchannel('A').getbbox()
            assert bounds and all(0 < value < 512 for value in bounds),(record['preview'],index,bounds)
            assert frame.getchannel('A').getextrema() == (0,255)
            digests.append(hashlib.sha256(path.read_bytes()).hexdigest())
            composite = Image.alpha_composite(Image.new('RGBA',frame.size,(14,20,28,255)),frame).convert('RGB')
            frames.append(composite.resize((320,320),Image.Resampling.LANCZOS))
            x,y = index%4*256,index//4*256
            sheet.paste(composite.resize((256,256),Image.Resampling.LANCZOS),(x,y))
            draw.text((x+8,y+238),f'{index:02} | {index*22.5:g} deg',fill=(230,235,240))
        assert len(set(digests)) >= 4,record['preview']
        sheet.save(output/'directions.jpg',quality=92)
        frames[0].save(output/'rotation.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
        report.append(dict(global_type=record['global_type'],building_id=record['building_id'],
            preview=record['preview'],kind=metadata['rotation_rig']['kind'],direction_sha256=digests))
    if not args.ids:
        (root/'directional-manifest.json').write_text(json.dumps(dict(model_count=len(report),
            direction_count=len(report)*16,models=report),indent=2)+'\n',encoding='utf-8')
    print('DIRECTIONAL_RENDER_REVIEW_OK',len(report),len(report)*16)


if __name__ == '__main__':
    main()
