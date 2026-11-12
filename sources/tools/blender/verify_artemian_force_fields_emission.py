"""Verify steady AR19 emission in actual imported-GLB low-light renders."""
import hashlib,json
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    folder=ROOT/'sources/objects/artemian/force-fields';media=ROOT/'gallery/media/objects/artemian/force-fields';meta=json.loads((folder/'model.json').read_bytes());runtime=json.loads((folder/'runtime-review.json').read_bytes())
    assert meta['binaries']==runtime['binaries']
    for ext,digest in meta['binaries'].items():assert sha(folder/('model.'+ext))==digest
    images={}
    for label in ['on','off']:
        path=media/('emission-review-'+label+'.png');assert sha(path)==runtime['renders'][path.name];images[label]=bpy.data.images.load(str(path),check_existing=False);assert tuple(images[label].size)==(512,512)
    scene=bpy.context.scene;scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100
    bpy.ops.object.camera_add();scene.camera=bpy.context.object;scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=2.8;direction=Vector((7,-12,8)).normalized();target=Vector((-.02,0,.95));scene.camera.location=target+direction*15;scene.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    samples=[]
    for i,pillar in enumerate(meta['pillars']):
        for name,z in [('segment0',.81),('segment1',1.06),('segment2',1.31),('tip',1.84)]:
            point=Vector((pillar['x'],pillar['y'],z));uv=world_to_camera_view(scene,scene.camera,point);x=round(uv.x*512);y=round(uv.y*512);assert 2<x<510 and 2<y<510;means={}
            for label,image in images.items():
                pixels=image.pixels;values=[pixels[4*((y+dy)*512+x+dx)+channel] for dy in [-1,0,1] for dx in [-1,0,1] for channel in range(3)];means[label]=sum(values)/len(values)
            assert means['on']>means['off']+.03,('Steady emission must be visible at each actual core and cap',i,name,means)
            samples.append(dict(pillar=i,part=name,world_point=list(point),pixel_top_left=[x,511-y],mean_linear_rgb=means,increase=means['on']-means['off']))
    report=dict(id=meta['id'],binaries=meta['binaries'],runtime_report_sha256=sha(folder/'runtime-review.json'),verifier=Path(__file__).relative_to(ROOT).as_posix(),verifier_sha256=sha(Path(__file__)),image_sha256={label:sha(media/('emission-review-'+label+'.png')) for label in images},samples=samples,scope='Actual rendered low-light on/off contrast at6segment and2tip positions;portable steady authored emission,not recovered Artemian pulse or client state/bloom acceptance.',game_client_integration=False)
    (folder/'emission-review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('AR19_EMISSION_CONTRAST_OK',len(samples),min(s['increase'] for s in samples))
if __name__=='__main__':main()
