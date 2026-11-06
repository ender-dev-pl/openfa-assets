"""Mutation controls for direct exported station geometry and activity audit."""
import json
from pathlib import Path
import struct
import tempfile
import unittest
import numpy as np
from audit_orbital_station_pairs import Glb,compare_finished,validate_activity


class AuditTests(unittest.TestCase):
    def fixture(self,construction=False,mutate=None):
        binary=bytearray();views=[];accessors=[]
        def accessor(values,dtype,kind,component):
            while len(binary)%4:binary.append(0)
            a=np.array(values,dtype=dtype);offset=len(binary);binary.extend(a.tobytes());views.append(dict(buffer=0,byteOffset=offset,byteLength=a.nbytes));accessors.append(dict(bufferView=len(views)-1,componentType=component,count=len(a),type=kind));return len(accessors)-1
        position=accessor([[0,0,0],[1,0,0],[0,1,0]],'<f4','VEC3',5126);normal=accessor([[0,0,1]]*3,'<f4','VEC3',5126);uv=accessor([[0,0],[1,0],[0,1]],'<f4','VEC2',5126);indices=accessor([0,1,2],'<u2','SCALAR',5123)
        data=dict(asset=dict(version='2.0'),nodes=[dict(name='PlacementRoot',children=[1]),dict(name='Body',mesh=0)],meshes=[dict(primitives=[dict(attributes=dict(POSITION=position,NORMAL=normal,TEXCOORD_0=uv),indices=indices,material=0)])],materials=[dict(name='Metal')],bufferViews=views,accessors=accessors)
        if construction:
            data['nodes'][0]['children'].append(2);data['nodes'].append(dict(name='ConstructionWorkCarriage',children=[3,4,5]));data['nodes'] += [dict(name=f'Carriage part {i}',mesh=0) for i in range(3)]
            times=accessor([0,3,6],'<f4','SCALAR',5126);values=accessor([[0,0,0],[.2,0,0],[0,0,0]],'<f4','VEC3',5126);data['animations']=[dict(name='ConstructionActivity',channels=[dict(sampler=0,target=dict(node=2,path='translation'))],samplers=[dict(input=times,output=values,interpolation='LINEAR')])]
        if mutate:mutate(data,binary)
        data['buffers']=[dict(byteLength=len(binary))];j=json.dumps(data).encode();j+=b' '*((-len(j))%4);binary+=b'\0'*((-len(binary))%4);raw=b'glTF'+struct.pack('<II',2,12+8+len(j)+8+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup);path=Path(directory.name)/'fixture.glb';path.write_bytes(raw);return Glb(path)

    def test_preserved_world_geometry_and_actor_only_activity(self):
        a=self.fixture();b=self.fixture(True);self.assertEqual(compare_finished(a,b),(1,0));self.assertEqual(len(validate_activity(b)),3)

    def test_displaced_finished_body_is_rejected(self):
        b=self.fixture(True,lambda d,b:d['nodes'][1].update(translation=[.02,0,0]))
        with self.assertRaises(AssertionError):compare_finished(self.fixture(),b)

    def test_finished_uv_mutation_is_rejected(self):
        def mutate(d,b):struct.pack_into('<f',b,d['bufferViews'][2]['byteOffset'],.5)
        with self.assertRaises(AssertionError):compare_finished(self.fixture(),self.fixture(True,mutate))

    def test_finished_normal_mutation_is_rejected(self):
        def mutate(d,b):struct.pack_into('<f',b,d['bufferViews'][1]['byteOffset'],.5)
        with self.assertRaises(AssertionError):compare_finished(self.fixture(),self.fixture(True,mutate))

    def test_topology_mutation_is_rejected(self):
        def mutate(d,b):struct.pack_into('<HHH',b,d['bufferViews'][3]['byteOffset'],0,2,1)
        with self.assertRaises(AssertionError):compare_finished(self.fixture(),self.fixture(True,mutate))

    def test_station_animation_is_rejected(self):
        b=self.fixture(True,lambda d,b:d['animations'][0]['channels'][0]['target'].update(node=0))
        with self.assertRaises(AssertionError):validate_activity(b)

    def test_nonclosing_service_cycle_is_rejected(self):
        def mutate(d,b):struct.pack_into('<f',b,d['bufferViews'][-1]['byteOffset']+24,.2)
        with self.assertRaises(AssertionError):validate_activity(self.fixture(True,mutate))

    def test_static_activity_is_rejected(self):
        def mutate(d,b):struct.pack_into('<f',b,d['bufferViews'][-1]['byteOffset']+12,0)
        with self.assertRaises(AssertionError):validate_activity(self.fixture(True,mutate))


if __name__=='__main__':unittest.main()
