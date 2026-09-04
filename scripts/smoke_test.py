#!/usr/bin/env python3
"""Generate and validate two seconds of synthetic media. Never reads a DVD."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError(f'{Path(command[0]).name} failed:\n{result.stderr[-3000:]}')
    return result.stdout


def smoke(root):
    package = Path(__file__).resolve().parents[1]
    for name in ('Original_MKV', 'Compatible_MP4', 'Logs', '.work'):
        (root / name).mkdir()
    for name in ('WORKFLOW.md', 'STATUS.md', 'manifest.json'):
        shutil.copy2(package / 'templates' / name, root / name)
    source = root / '.work' / 'synthetic.mkv'
    archive = root / 'Original_MKV' / 'synthetic_archive.mkv'
    playback = root / 'Compatible_MP4' / 'synthetic_playback.mp4'
    ff = ['ffmpeg', '-hide_banner', '-v', 'error', '-nostdin', '-n']
    run(ff + ['-f', 'lavfi', '-i', 'testsrc2=size=320x240:rate=25',
              '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000',
              '-t', '2', '-c:v', 'mpeg2video', '-c:a', 'ac3', str(source)])
    run(ff + ['-i', str(source), '-map', '0', '-c', 'copy', str(archive)])
    run(ff + ['-i', str(archive), '-map', '0:v:0', '-map', '0:a:0',
              '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
              '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', str(playback)])
    checks = []
    for path, video, audio in ((archive, 'mpeg2video', 'ac3'), (playback, 'h264', 'aac')):
        info = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                              '-of', 'json', str(path)]))
        streams = info['streams']
        v = next(s for s in streams if s['codec_type'] == 'video')
        a = next(s for s in streams if s['codec_type'] == 'audio')
        if len(streams) != 2 or (v['codec_name'], a['codec_name']) != (video, audio):
            raise RuntimeError('Unexpected streams or codecs')
        if (v['width'], v['height'], v['pix_fmt']) != (320, 240, 'yuv420p'):
            raise RuntimeError('Unexpected geometry or pixel format')
        if v['r_frame_rate'] != '25/1' or v.get('sample_aspect_ratio') != '1:1':
            raise RuntimeError('Unexpected frame rate or aspect ratio')
        if not 1.9 <= float(info['format']['duration']) <= 2.2:
            raise RuntimeError('Unexpected duration')
        run(ff + ['-xerror', '-i', str(path), '-map', '0:v', '-map', '0:a', '-f', 'null', '-'])
        checks.append({'path': str(path.relative_to(root)), 'decode': 'passed',
                       'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    # Compare compressed packet payload hashes across the stream-copy archive.
    def packets(path):
        obj = json.loads(run(['ffprobe', '-v', 'error', '-show_packets', '-show_data_hash',
                              'sha256', '-show_entries', 'packet=stream_index,data_hash',
                              '-of', 'json', str(path)]))
        return [(p['stream_index'], p['data_hash']) for p in obj['packets']]
    if packets(source) != packets(archive):
        raise RuntimeError('Archive packet payloads changed')
    monitor = run([sys.executable, str(package / 'scripts' / 'monitor.py'), str(root), '--once'])
    if 'no reliable denominator' not in monitor:
        raise RuntimeError('Monitor did not produce expected safe output')
    report = {'synthetic_only': True, 'archive_packet_hashes': 'passed', 'files': checks,
              'monitor_once': 'passed', 'real_disc': 'not tested', 'subtitles': 'not tested',
              'gui_playback': 'not tested'}
    (root / 'Logs' / 'smoke-report.json').write_text(json.dumps(report, indent=2) + '\n')
    (root / 'STATUS.md').write_text('# Synthetic setup test\n\nTechnical smoke test passed. '
                                   'No real disc or player compatibility was verified.\n')
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, help='new, non-existing directory; retained after test')
    args = parser.parse_args()
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        parser.exit(1, 'FFmpeg and ffprobe are required; run check_prerequisites.py.\n')
    try:
        if args.workspace:
            root = args.workspace.expanduser().absolute()
            root.mkdir(parents=True, exist_ok=False)
            smoke(root)
            print('Retained synthetic workspace: ' + str(root))
        else:
            with tempfile.TemporaryDirectory(prefix='dvd-archive-smoke-') as temporary:
                smoke(Path(temporary))
            print('Disposable synthetic workspace cleaned up.')
        return 0
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print('Smoke test failed: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
