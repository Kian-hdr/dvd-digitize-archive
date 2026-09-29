#!/usr/bin/env python3
"""Read-only local dependency report; installs nothing and does not access discs."""
import platform
import shutil
import subprocess
import sys


def main():
    print(f'Environment: {platform.system()} {platform.release()} {platform.machine()}')
    print(f'Python: {platform.python_version()}')
    okay = sys.version_info >= (3, 9)
    print('Python >= 3.9: ' + ('PASS' if okay else 'MISSING'))
    for name in ('ffmpeg', 'ffprobe'):
        executable = shutil.which(name)
        if not executable:
            print(name + ': MISSING (required for synthetic media validation)')
            okay = False
            continue
        try:
            result = subprocess.run([executable, '-version'], capture_output=True,
                                    text=True, timeout=15, check=True)
            print(result.stdout.splitlines()[0])
        except (OSError, subprocess.SubprocessError, IndexError):
            print(name + ': FAILED to run')
            okay = False
    if shutil.which('ffmpeg'):
        try:
            encoders = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'],
                                      capture_output=True, text=True, timeout=15, check=True).stdout
            print('HEVC libx265 encoder: ' + ('found' if 'libx265' in encoders else
                                             'not found (optional for setup; required for HEVC candidates)'))
        except (OSError, subprocess.SubprocessError):
            print('HEVC libx265 encoder: unverified')
    for name in ('git', 'zsh', 'brew', 'dvdbackup', 'makemkvcon', 'mkvmerge',
                 'mkvextract', 'tesseract', 'whisper'):
        print(name + ': ' + ('found' if shutil.which(name) else 'not on PATH (optional)'))
    print('Optical drive, DVD/Blu-ray/UHD access, reader license, OCR and player playback: NOT TESTED')
    print('macOS is the primary workflow. Linux is experimental; native Windows is unsupported.')
    return 0 if okay else 1


if __name__ == '__main__':
    sys.exit(main())
