"""Decode every engine-rendered construction clip and verify its lifecycle/provenance."""
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
MEDIA=ROOT/'gallery/media/construction-cycles'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    index=json.loads((MEDIA/'index.json').read_text())
    assert {r['culture'] for r in index['clips']}=={'terran','rigellian','braccatian','mikotaj','artemian','mauna','achaean'}
    for record in index['clips']:
        folder=MEDIA/record['culture'];plan=json.loads((folder/'sequence.json').read_text())
        evidence=json.loads((folder/'runtime-evidence.json').read_text())
        assert json.loads((folder/'video.json').read_text())==record
        for name,key in [('construction.webm','video_sha256'),('poster.png','poster_sha256'),('complete.png','complete_sha256'),('sequence.json','sequence_sha256'),('runtime-evidence.json','runtime_evidence_sha256')]:assert sha(folder/name)==record[key]
        assert evidence['planSha256']==record['sequence_sha256']
        assert record['encoder_sha256']==sha(ROOT/'tools/build_construction_videos.py')
        assert record['host_source_sha256']==sha(ROOT/'tools/ConstructionPreview/Program.cs')
        assert record['host_project_sha256']==sha(ROOT/'tools/ConstructionPreview/ConstructionPreview.csproj')
        assert plan['generator_sha256']==sha(ROOT/'sources/tools/blender/prepare_construction_previews.py')
        assert plan['source_integration_sha256']==sha(ROOT/'sources/docs/assets/reconstruction/scaffolds/culture-kits/integration.json')
        assert evidence['renderer']=='OpenFA.Client.MonoGameSurfaceModelRenderer' and not evidence['gameplayIntegration']
        for path,digest in plan['sources'].items():assert sha(ROOT/path)==digest
        n=plan['ceiling'];entries=plan['timeline']
        assert [e['stage'] for e in entries if e['phase']=='erection']==list(range(1,n+1))
        assert [e['stage'] for e in entries if e['phase']=='dismantling']==list(range(n,0,-1))
        frames={f['image']:f for f in plan['frames']}
        assert len(evidence['frames'])==len(frames)==2*n+2
        assert {f['image'] for f in evidence['frames']}==set(frames)
        assert len(record['timeline'])==len(entries)
        for entry,encoded in zip(entries,record['timeline']):
            frame=frames[entry['image']]
            assert frame['stage']==entry['stage']
            assert frame['building_visible']==(entry['phase'] in ['reveal','dismantling','complete'])
            assert (entry['phase'],entry['stage'],entry['image'])==(encoded['phase'],encoded['stage'],encoded['image'])
        for frame in plan['frames']:
            assert (frame['building_meshes']>0)==frame['building_visible']
            assert (frame['scaffold_meshes']>0)==(frame['stage']>0)
        for image in ['poster.png','complete.png']:
            with Image.open(folder/image) as im:assert im.size==(640,720)
        result=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,nb_read_frames:format=duration','-of','json',str(folder/'construction.webm')],check=True,capture_output=True,text=True)
        probe=json.loads(result.stdout);stream=probe['streams'][0]
        assert (stream['codec_name'],stream['width'],stream['height'])==('vp9',640,720)
        assert int(stream['nb_read_frames'])==record['frames']==450
        assert abs(float(probe['format']['duration'])-record['duration'])<.05
        subprocess.run(['ffmpeg','-v','error','-i',str(folder/'construction.webm'),'-f','null','-'],check=True,capture_output=True)
        print('CONSTRUCTION_VIDEO_VERIFIED',record['culture'],record['frames'],flush=True)


if __name__=='__main__':main()
