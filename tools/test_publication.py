"""Regression checks for metadata removal, binary invariants and publication guard."""
import io
from pathlib import Path
import tempfile
import unittest
from contextlib import contextmanager
import uuid
from PIL import Image, PngImagePlugin
from publication_support import blend_bytes, clean_blend, clean_png, clean_jpeg, clean_text, zstd
from verify_publication import problems


@contextmanager
def fixture_directory():
    root = Path(__file__).resolve().parents[1] / 'artifacts'
    root.mkdir(exist_ok=True)
    folder = root / ('publication-test-' + uuid.uuid4().hex)
    folder.mkdir()
    try:
        yield folder
    finally:
        assert folder.resolve().is_relative_to(root.resolve())
        for path in folder.iterdir():
            path.unlink()
        folder.rmdir()


class PublicationTests(unittest.TestCase):
    def test_compressed_native_path_removal_preserves_nonpath_payload(self):
        private = b'C' + b':' + b'/Us' + b'ers/example/private/model.blend'
        before = b'BLENDER-v304' + b'geometry-before\0' + private + b'\0geometry-after\0'
        cleaned, edits, _, _ = clean_blend(zstd(before, compress=True))
        after = blend_bytes(cleaned)
        self.assertEqual(edits, 1)
        self.assertEqual(len(before), len(after))
        self.assertEqual(before[:before.index(private)], after[:before.index(private)])
        self.assertTrue(after.endswith(b'\0geometry-after\0'))
        self.assertNotIn(private, after)

    def test_binary_geometry_that_resembles_drive_prefix_is_unchanged(self):
        before = b'BLENDER-v304' + bytes([107, 58, 92, 175, 1, 2, 3])
        cleaned, edits, _, _ = clean_blend(before)
        self.assertEqual(edits, 0)
        self.assertEqual(blend_bytes(cleaned), before)

    def test_png_removal_preserves_rgba_pixels_and_alpha(self):
        image = Image.new('RGBA', (4, 3), (31, 92, 180, 73))
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('File', 'private source')
        stream = io.BytesIO()
        image.save(stream, 'PNG', pnginfo=metadata)
        after = clean_png(stream.getvalue())
        with Image.open(io.BytesIO(after)) as actual:
            self.assertNotIn('File', actual.info)
            self.assertEqual(actual.tobytes(), image.tobytes())

    def test_jpeg_removal_does_not_reencode_pixels(self):
        image = Image.new('RGB', (8, 8), (31, 92, 180))
        exif = Image.Exif()
        exif[315] = 'Private author'
        stream = io.BytesIO()
        image.save(stream, 'JPEG', exif=exif)
        before = stream.getvalue()
        after = clean_jpeg(before)
        with Image.open(io.BytesIO(before)) as a, Image.open(io.BytesIO(after)) as b:
            self.assertEqual(a.tobytes(), b.tobytes())
            self.assertFalse(b.getexif())

    def test_guard_checks_compressed_models_utf16_logs_and_secret_values(self):
        private = b'C' + b':' + b'/Us' + b'ers/example/private/model.blend'
        with fixture_directory() as folder:
            root = Path(folder)
            model = root / 'model.blend'
            model.write_bytes(zstd(b'BLENDER-v304\0' + private + b'\0', compress=True))
            self.assertTrue(problems(model))
            log = root / 'render.log'
            log.write_bytes(private.decode().encode('utf-16'))
            self.assertTrue(problems(log))
            log.write_bytes(clean_text(log.read_bytes()))
            self.assertFalse(problems(log))
            token = root / 'config.json'
            token.write_bytes(b'{"token":"' + b'gh' + b'p_' + b'x' * 30 + b'"}')
            self.assertTrue(problems(token))

    def test_path_redaction_keeps_command_arguments(self):
        before = b'C' + b':' + b'/tools/blender/blender.exe --background --python build.py'
        self.assertEqual(clean_text(before), b'[local]/blender.exe --background --python build.py')


if __name__ == '__main__':
    unittest.main()
