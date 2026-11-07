"""Audit decoded motion and select complete 3D films in yard and ship gallery cards."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'sources/objects/terran/ship-yard/hangar'
SHIPS=['assault-fighter','combat-eagle','scoutship']


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def main():
    ffmpeg=shutil.which('ffmpeg');assert ffmpeg
    clips=[];inputs={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))};downloads={};audit=[]
    for ship in SHIPS:
        path=SOURCE/('complete-3d-'+ship+'.json');data=json.loads(path.read_text(encoding='utf-8'))
        for source,digest in data['inputs'].items():assert sha(ROOT/source)==digest,source
        clip=data['clips'][0];video=ROOT/clip['mp4']['path'];assert sha(video)==clip['mp4']['sha256']
        result=subprocess.check_output([ffmpeg,'-v','error','-i',str(video),'-vf','scale=128:128','-f','framemd5','-'],text=True)
        hashes=[line.split(',')[-1].strip() for line in result.splitlines() if line and not line.startswith('#')]
        assert len(hashes)==480 and len(set(hashes))>360,(ship,len(hashes),len(set(hashes)))
        audit.append(dict(ship=ship,mp4_sha256=sha(video),decoded_frames=len(hashes),distinct_decoded_frames=len(set(hashes)),distinct_evaluated_3d_states=clip['distinct_pose_count'],per_frame_rig_checks=data['per_frame_attachment_and_sling_checks']))
        clips.append(clip);inputs.update(data['inputs']);inputs[path.relative_to(ROOT).as_posix()]=sha(path)
        downloads.update({ship+'-'+key:value for key,value in data['downloads'].items()})
        # Replace each individual ship's former still-stage player with the full cycle.
        ship_path=ROOT/'sources/objects/terran'/ship/'construction/showcase.json';old=json.loads(ship_path.read_text(encoding='utf-8'))
        earlier=old.get('earlier_still_preview') if old['clips'][0].get('kind')=='complete-3d' else old
        new=dict(issue=227,inputs={**data['inputs'],path.relative_to(ROOT).as_posix():sha(path),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},clips=[clip],downloads=data['downloads'],method=data['method'],earlier_still_preview=earlier)
        write(ship_path,new)
    audit_path=SOURCE/'complete-motion-audit.json';write(audit_path,dict(renderer='Blender per-frame rendering, 24 fps',movies=audit))
    inputs[audit_path.relative_to(ROOT).as_posix()]=sha(audit_path)
    path=SOURCE/'showcase.json';old=json.loads(path.read_text(encoding='utf-8'))
    earlier=old.get('earlier_previews',old['clips'])
    write(path,dict(issue=227,inputs=inputs,clips=clips,downloads=downloads,earlier_previews=earlier,scope='Complete 20-second per-frame 3D assembly and crane/hangar cycles. Canonical models are unchanged; assembly batch placement is an offline preview controller requiring client binding. Former static-stage clips are retained only as historical previews.'))
    print('COMPLETE_3D_MOVIES_SELECTED',json.dumps(audit),flush=True)


if __name__=='__main__':main()
