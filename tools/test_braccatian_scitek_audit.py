"""Guard VID held-frame accounting and malformed-container rejection without codec emulation."""
from pathlib import Path
import struct
import tempfile
import unittest

from audit_braccatian_scitek_references import ROOT,container


def chunk(tag,payload=b''):return tag+struct.pack('<I',8+len(payload))+payload


def video(body,declared=3):
    data=b'Vide'+struct.pack('<I',28+len(body))+b'Head'+struct.pack('<I',20)
    return data+struct.pack('<6H',8,2,2,declared,0,0)+body


class TimelineTests(unittest.TestCase):
    def parse(self,data):
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts') as tmp:
            path=Path(tmp)/'test.VID';path.write_bytes(data);return container(path)

    def test_held_frames_are_not_image_updates(self):
        result=self.parse(video(chunk(b'Inte')+chunk(b'Fram',b'opaque')+chunk(b'Same')+chunk(b'Same')+chunk(b'Stop')))
        self.assertEqual(result['head'],dict(width=2,height=2,image_updates=1,timeline_frames=3))
        self.assertEqual(result['chunks'][1]['index'],0)

    def test_invalid_timeline_and_boundaries_are_rejected(self):
        valid=chunk(b'Fram')+chunk(b'Same')+chunk(b'Same')+chunk(b'Stop')
        cases=[video(valid,2),video(chunk(b'Same')+chunk(b'Stop'),1),
          video(chunk(b'Fram')+chunk(b'Same',b'bad')+chunk(b'Stop'),2),
          video(chunk(b'Fram'),1),video(chunk(b'Fram')+chunk(b'Stop')+chunk(b'Same'),2),
          video(chunk(b'Fram')+chunk(b'Bad!')+chunk(b'Stop'),1),video(valid)[:-1]]
        for data in cases:
            with self.subTest(data=data),self.assertRaises(AssertionError):self.parse(data)


if __name__=='__main__':unittest.main()
