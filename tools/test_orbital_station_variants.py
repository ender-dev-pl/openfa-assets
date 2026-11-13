"""Regression checks for accidental retirement or misbinding of finished stations."""
import copy,hashlib,json,struct,tempfile,unittest
from pathlib import Path
from verify_orbital_station_variants import verify

class OrbitalStationRoles(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);(self.root/'project').mkdir();self.registry=dict(models=[],catalogue=[]);self.rows=[]
        for race in ['achaean','artemian','braccatian','mauna','mikotaj','rigellian']:
            states={};identity=race+':station'
            for role,frame,purpose in [('finished',0,'canonical-definition'),('construction',1,'construction-animation')]:
                state=dict(legacy_sprite_frame=frame)
                for kind in ['blend','glb']:
                    path=f'sources/{race}/{role}/model.{kind}';target=self.root/path;target.parent.mkdir(parents=True,exist_ok=True)
                    data=json.dumps(dict(animations=[dict(name='ConstructionActivity')] if frame else [])).encode() if kind=='glb' else (race+role).encode()
                    if kind=='glb':data=b'glTF'+struct.pack('<IIII',2,len(data)+20,len(data),0x4e4f534a)+data
                    target.write_bytes(data);digest=hashlib.sha256(data).hexdigest();state[kind]=path;state[kind+'_sha256']=digest;self.registry['models'].append(dict(path=path,sha256=digest,purpose=purpose))
                states[role]=state
            states['construction']['clip']='ConstructionActivity';self.rows.append(dict(id=identity,culture=race,**states));source=states['finished'];metadata=dict(variant='construction',legacy_sprite_frame=1,source_study=source['blend'],source_blend_sha256=source['blend_sha256'],source_glb_sha256=source['glb_sha256']);(self.root/states['construction']['glb']).with_suffix('.json').write_text(json.dumps(metadata));self.registry['catalogue'].append(dict(id=identity,studies=[dict(blend=source['blend'],glb=source['glb'],animation_sources=[states['construction']])]))
        (self.root/'project/orbital-station-variants.json').write_text(json.dumps(dict(stations=self.rows)))
    def test_accepts_distinct_finished_and_construction_states(self):self.assertEqual(verify(self.root,self.registry),6)
    def test_rejects_construction_as_primary_finished_model(self):
        self.registry['catalogue'][0]['studies'][0]['glb']=self.rows[0]['construction']['glb']
        with self.assertRaisesRegex(ValueError,'Primary station'):verify(self.root,self.registry)
    def test_rejects_missing_finished_payload(self):
        (self.root/self.rows[0]['finished']['blend']).unlink()
        with self.assertRaisesRegex(ValueError,'Missing functional'):verify(self.root,self.registry)
    def test_rejects_removed_construction_animation(self):
        self.registry['catalogue'][0]['studies'][0]['animation_sources']=[]
        with self.assertRaisesRegex(ValueError,'animation missing'):verify(self.root,self.registry)

if __name__=='__main__':unittest.main()
