"""Decode gallery videos and check coverage, frame counts and authored timing."""
import json
import shutil
import subprocess

from gallery_animation_assets import ROOT,animation_previews


def main():
    probe=shutil.which('ffprobe');decoder=shutil.which('ffmpeg')
    assert probe and decoder,'ffmpeg and ffprobe are required'
    clips=0
    for row in json.loads((ROOT/'gallery/catalogue.json').read_text()):
        for study in row['studies']:
            for clip in animation_previews(study['blend'],study['glb'],(ROOT/study['image']).parent):
                path=ROOT/clip['video']
                result=subprocess.run([probe,'-v','error','-count_frames','-select_streams','v:0','-show_entries',
                    'stream=codec_name,width,height,nb_read_frames:format=duration','-of','json',str(path)],check=True,capture_output=True,text=True)
                data=json.loads(result.stdout);stream=data['streams'][0]
                assert stream['codec_name']=='vp9' and stream['width']==384 and stream['height']==384,str(path)
                assert int(stream['nb_read_frames'])==clip['frames'],(path,'Incomplete video')
                assert abs(float(data['format']['duration'])-clip['duration'])<.05,(path,'Authored timing changed')
                subprocess.run([decoder,'-v','error','-i',str(path),'-f','null','-'],check=True,capture_output=True)
                clips+=1
    print('GALLERY_VIDEO_DECODE_OK',clips,'complete authored clips',flush=True)


if __name__=='__main__':main()
