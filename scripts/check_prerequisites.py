#!/usr/bin/env python3
"""Read-only local dependency report; installs nothing and does not access DVDs."""
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
    for name in ('git', 'zsh', 'brew', 'dvdbackup', 'makemkvcon', 'mkvmerge',
                 'mkvextract', 'tesseract', 'whisper'):
        print(name + ': ' + ('found' if shutil.which(name) else 'not on PATH (optional)'))
    print('Optical drive, reader license, disc permissions, OCR and GUI playback: NOT TESTED')
    print('macOS is the primary workflow. Linux is experimental; native Windows is unsupported.')
    return 0 if okay else 1


if __name__ == '__main__':
    sys.exit(main())
