"""Synthetic checks for public optical-disc helpers; no drive or media access."""

from contextlib import ExitStack, redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


class DiscSnapshotTests(unittest.TestCase):
    def test_structural_fingerprint_changes_with_control_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bdmv = root / 'BDMV'
            bdmv.mkdir()
            control = bdmv / 'index.bdmv'
            control.write_bytes(b'first')
            command = [sys.executable, str(ROOT / 'scripts/disc_snapshot.py'), str(root)]
            first = subprocess.run(command, capture_output=True, text=True, timeout=15)
            self.assertEqual(first.returncode, 0, first.stderr)
            snapshot = json.loads(first.stdout)
            self.assertEqual(snapshot['format'], 'Blu-ray')
            self.assertEqual(snapshot['uhd_status'], 'unverified')
            self.assertIn('not a physical-disc serial', snapshot['fingerprint_method'])
            control.write_bytes(b'second')
            second = subprocess.run(command, capture_output=True, text=True, timeout=15)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertNotEqual(snapshot['structural_fingerprint_sha256'],
                                json.loads(second.stdout)['structural_fingerprint_sha256'])

    def test_unknown_structure_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/disc_snapshot.py'),
                                     temporary], capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)

    def test_symlinked_control_file_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'BDMV').mkdir()
            external = root / 'unrelated.txt'
            external.write_text('leave alone')
            (root / 'BDMV' / 'index.bdmv').symlink_to(external)
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/disc_snapshot.py'),
                                     str(root)], capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(external.read_text(), 'leave alone')


class HelperTests(unittest.TestCase):
    def test_makemkv_scan_preview_does_not_touch_drive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / 'scan.log'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/makemkv_job.py'),
                                     '--workspace', str(root), '--log', str(log), 'scan'],
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('info disc:9999', result.stdout)
            self.assertFalse(log.exists())

    def test_watch_view_preserves_prior_view_and_guide(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / 'episode.mp4'
            media.write_bytes(b'synthetic placeholder for path and hardlink test')
            (root / 'watch_order.json').write_text(json.dumps({
                'schema_version': 1, 'title': 'Synthetic watch order',
                'entries': [{'id': 'episode-1', 'status': 'owned',
                             'title': 'Episode 1', 'verified': True,
                             'source_path': 'episode.mp4'}],
            }))
            prior_view = root / 'Watch_Order'
            prior_view.mkdir()
            (prior_view / 'prior.txt').write_text('keep prior view')
            (root / 'WATCH_ORDER.txt').write_text('keep prior guide')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/build_watch_view.py'),
                                     str(root), '--run'], capture_output=True, text=True,
                                    timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            new_media = root / 'Watch_Order' / '0001_episode.mp4'
            self.assertTrue(new_media.is_file())
            self.assertEqual(os.stat(new_media).st_ino, os.stat(media).st_ino)
            self.assertIn('Episode 1', (root / 'WATCH_ORDER.txt').read_text())
            retained_views = list(root.glob('.Watch_Order_previous_*'))
            retained_guides = list(root.glob('.WATCH_ORDER_previous_*.txt'))
            self.assertEqual(len(retained_views), 1)
            self.assertEqual(len(retained_guides), 1)
            self.assertEqual((retained_views[0] / 'prior.txt').read_text(), 'keep prior view')
            self.assertEqual(retained_guides[0].read_text(), 'keep prior guide')

    def test_malformed_watch_offer_leaves_existing_view_and_guide(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'episode.mp4').write_bytes(b'synthetic placeholder')
            (root / 'watch_order.json').write_text(json.dumps({
                'schema_version': 1,
                'entries': [{'id': 'episode-1', 'status': 'owned',
                             'verified': True, 'source_path': 'episode.mp4',
                             'streaming_offers': [42]}],
            }))
            view = root / 'Watch_Order'
            view.mkdir()
            (view / 'prior.txt').write_text('keep prior view')
            guide = root / 'WATCH_ORDER.txt'
            guide.write_text('keep prior guide')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/build_watch_view.py'),
                                     str(root), '--run'], capture_output=True, text=True,
                                    timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('streaming_offers', result.stderr)
            self.assertEqual((view / 'prior.txt').read_text(), 'keep prior view')
            self.assertEqual(guide.read_text(), 'keep prior guide')
            self.assertFalse(list(root.glob('.Watch_Order_previous_*')))
            self.assertFalse(list(root.glob('.WATCH_ORDER_previous_*.txt')))

    def test_dangling_watch_view_symlink_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'episode.mp4').write_bytes(b'synthetic placeholder')
            (root / 'watch_order.json').write_text(json.dumps({
                'schema_version': 1,
                'entries': [{'id': 'episode-1', 'status': 'owned',
                             'verified': True, 'source_path': 'episode.mp4'}],
            }))
            target = root / 'Watch_Order'
            target.symlink_to(root / 'missing-view', target_is_directory=True)
            guide = root / 'WATCH_ORDER.txt'
            guide.write_text('keep prior guide')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/build_watch_view.py'),
                                     str(root), '--run'], capture_output=True, text=True,
                                    timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.readlink(), root / 'missing-view')
            self.assertEqual(guide.read_text(), 'keep prior guide')
            self.assertFalse(list(root.glob('.Watch_Order_previous_*')))

    def test_dangling_retention_symlinks_are_not_replaced(self):
        spec = importlib.util.spec_from_file_location('dvd_watch_view_test',
                                                      ROOT / 'scripts/build_watch_view.py')
        module = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(ROOT / 'scripts'))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)

        class FixedDatetime:
            @staticmethod
            def now(tz):
                return datetime(2026, 9, 29, 0, 0, tzinfo=timezone.utc)

        for retained_name in ('.Watch_Order_previous_20260929T000000Z',
                              '.WATCH_ORDER_previous_20260929T000000Z.txt'):
            with self.subTest(retained_name=retained_name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / 'episode.mp4').write_bytes(b'synthetic placeholder')
                (root / 'watch_order.json').write_text(json.dumps({
                    'schema_version': 1,
                    'entries': [{'id': 'episode-1', 'status': 'owned',
                                 'verified': True, 'source_path': 'episode.mp4'}],
                }))
                view = root / 'Watch_Order'
                view.mkdir()
                (view / 'prior.txt').write_text('keep prior view')
                guide = root / 'WATCH_ORDER.txt'
                guide.write_text('keep prior guide')
                collision = root / retained_name
                collision.symlink_to(root / 'missing-retention-target')
                with ExitStack() as stack:
                    stack.enter_context(mock.patch.object(module, 'datetime', FixedDatetime))
                    stack.enter_context(mock.patch.object(sys, 'argv',
                                    ['build_watch_view.py', str(root), '--run']))
                    stack.enter_context(redirect_stdout(io.StringIO()))
                    stack.enter_context(redirect_stderr(io.StringIO()))
                    result = module.main()
                self.assertNotEqual(result, 0)
                self.assertTrue(collision.is_symlink())
                self.assertEqual(collision.readlink(), root / 'missing-retention-target')
                self.assertEqual((view / 'prior.txt').read_text(), 'keep prior view')
                self.assertEqual(guide.read_text(), 'keep prior guide')

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),
                         'FFmpeg and ffprobe are needed for the synthetic audio map')
    def test_explicit_language_overrides_default_and_keeps_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'two_languages.mkv'
            output = root / 'german_candidate.mp4'
            generated = subprocess.run([
                'ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y',
                '-f', 'lavfi', '-i', 'testsrc2=size=160x120:rate=25',
                '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000',
                '-f', 'lavfi', '-i', 'sine=frequency=660:sample_rate=48000',
                '-t', '1', '-map', '0:v', '-map', '1:a', '-map', '2:a',
                '-c:v', 'mpeg2video', '-c:a', 'ac3',
                '-metadata:s:a:0', 'language=eng',
                '-metadata:s:a:1', 'language=deu', str(source),
            ], capture_output=True, text=True, timeout=30)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            rejected = subprocess.run([
                sys.executable, str(ROOT / 'scripts/compatible_encode.py'),
                str(source), str(output), '--video-stream', '0', '--video-only',
            ], capture_output=True, text=True, timeout=15)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertFalse(output.exists())
            encoded = subprocess.run([
                sys.executable, str(ROOT / 'scripts/compatible_encode.py'),
                str(source), str(output), '--video-stream', '0', '--audio-stream', '2',
                '--audio-language', 'deu', '--video-codec', 'h264',
                '--sdr-confirmed', '--run',
            ], capture_output=True, text=True, timeout=60)
            self.assertEqual(encoded.returncode, 0, encoded.stderr)
            self.assertTrue(source.is_file())
            self.assertTrue(output.is_file())
            probe = subprocess.run(['ffprobe', '-v', 'error', '-show_streams',
                                    '-of', 'json', str(output)], capture_output=True,
                                   text=True, timeout=15, check=True)
            audio = [stream for stream in json.loads(probe.stdout)['streams']
                     if stream.get('codec_type') == 'audio']
            self.assertEqual(len(audio), 1)
            self.assertEqual(audio[0]['tags']['language'], 'deu')
            self.assertEqual(audio[0]['disposition']['default'], 1)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),
                         'FFmpeg and ffprobe are needed for the synthetic HEVC pilot')
    def test_hevc_main8_candidate_decodes(self):
        encoders = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'],
                                  capture_output=True, text=True, timeout=15, check=True).stdout
        if 'libx265' not in encoders:
            self.skipTest('libx265 is unavailable')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'source.mkv'
            output = root / 'hevc_candidate.mp4'
            generated = subprocess.run([
                'ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y',
                '-f', 'lavfi', '-i', 'testsrc2=size=160x120:rate=25',
                '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000',
                '-t', '1', '-map', '0:v', '-map', '1:a', '-c:v', 'mpeg2video',
                '-c:a', 'ac3', '-metadata:s:a:0', 'language=eng', str(source),
            ], capture_output=True, text=True, timeout=30)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            encoded = subprocess.run([
                sys.executable, str(ROOT / 'scripts/compatible_encode.py'),
                str(source), str(output), '--video-stream', '0', '--audio-stream', '1',
                '--preset', 'fast', '--sdr-confirmed', '--run',
            ], capture_output=True, text=True, timeout=90)
            self.assertEqual(encoded.returncode, 0, encoded.stderr)
            probed = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json',
                                     str(output)], capture_output=True, text=True,
                                    timeout=15, check=True)
            video = next(stream for stream in json.loads(probed.stdout)['streams']
                         if stream.get('codec_type') == 'video')
            self.assertEqual(video['codec_name'], 'hevc')
            self.assertEqual(video['codec_tag_string'], 'hvc1')
            self.assertEqual(video['pix_fmt'], 'yuv420p')
            decoded = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(output),
                                      '-f', 'null', '-'], capture_output=True, text=True,
                                     timeout=30)
            self.assertEqual(decoded.returncode, 0, decoded.stderr)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),
                         'FFmpeg and ffprobe are needed for the synthetic Main10 pilot')
    def test_hevc_main10_preserves_depth_and_signalled_color(self):
        encoders = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'],
                                  capture_output=True, text=True, timeout=15, check=True).stdout
        if 'libx265' not in encoders:
            self.skipTest('libx265 is unavailable')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'ten_bit_source.mp4'
            output = root / 'main10_candidate.mp4'
            report = root / 'main10_audit.json'
            generated = subprocess.run([
                'ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y',
                '-f', 'lavfi', '-i', 'testsrc2=size=160x120:rate=25',
                '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000',
                '-t', '1', '-map', '0:v', '-map', '1:a', '-c:v', 'libx265',
                '-pix_fmt', 'yuv420p10le', '-color_range', 'tv',
                '-color_primaries', 'bt709', '-color_trc', 'bt709',
                '-colorspace', 'bt709', '-x265-params',
                'colorprim=bt709:transfer=bt709:colormatrix=bt709', '-tag:v', 'hvc1',
                '-c:a', 'aac',
                '-metadata:s:a:0', 'language=eng', str(source),
            ], capture_output=True, text=True, timeout=30)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            encoded = subprocess.run([
                sys.executable, str(ROOT / 'scripts/compatible_encode.py'),
                str(source), str(output), '--video-stream', '0', '--audio-stream', '1',
                '--preset', 'fast', '--sdr-confirmed', '--run',
            ], capture_output=True, text=True, timeout=90)
            self.assertEqual(encoded.returncode, 0, encoded.stderr)
            probed = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json',
                                     str(output)], capture_output=True, text=True,
                                    timeout=15, check=True)
            video = next(stream for stream in json.loads(probed.stdout)['streams']
                         if stream.get('codec_type') == 'video')
            self.assertEqual(video['profile'], 'Main 10')
            self.assertEqual(video['pix_fmt'], 'yuv420p10le')
            self.assertEqual(video['codec_tag_string'], 'hvc1')
            for field in ('color_primaries', 'color_transfer', 'color_space'):
                self.assertEqual(video[field], 'bt709')
            audited = subprocess.run([
                sys.executable, str(ROOT / 'scripts/media_audit.py'), str(output),
                '--report', str(report), '--decode', '--tv-baseline',
                '--compare-source', str(source), '--source-video-stream', '0',
            ], capture_output=True, text=True, timeout=45)
            self.assertEqual(audited.returncode, 0,
                             audited.stderr + audited.stdout + report.read_text())
            evidence = json.loads(report.read_text())
            self.assertTrue(evidence['source_match']['passed'])
            self.assertTrue(evidence['tv_baseline']['passed'])


if __name__ == '__main__':
    unittest.main()
