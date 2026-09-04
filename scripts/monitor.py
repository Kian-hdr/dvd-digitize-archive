#!/usr/bin/env python3
"""Read-only workspace growth monitor. No media commands or process signals."""
import argparse
from collections import deque
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

MEDIA_TOOLS = {'dvdbackup', 'makemkvcon', 'ffmpeg', 'mkvmerge', 'mkvextract',
               'tesseract', 'whisper'}


def inside(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def measure(path):
    """Count regular files without following symlinks out of the workspace."""
    if path.is_symlink():
        return 0, 0
    if path.is_file():
        return path.stat().st_size, 1
    size = count = 0
    for directory, dirs, files in os.walk(path, followlinks=False):
        dirs[:] = [d for d in dirs if not (Path(directory) / d).is_symlink()]
        for name in files:
            item = Path(directory) / name
            try:
                if not item.is_symlink() and item.is_file():
                    size += item.stat().st_size
                    count += 1
            except OSError:
                pass  # A concurrently moved file is not a monitor failure.
    return size, count


def human_bytes(value):
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if abs(value) < 1000 or unit == 'TB':
            return f'{value:.2f} {unit}'
        value /= 1000


def process_summaries(root):
    """Heuristic only: ps loses argument quoting. Never infer progress from it."""
    try:
        output = subprocess.run(['ps', '-ax', '-o', 'pid=,comm=,args='],
                                capture_output=True, text=True, timeout=5,
                                check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return ['process inspection unavailable']
    results = []
    for line in output.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) != 3 or Path(parts[1]).name not in MEDIA_TOOLS:
            continue
        # Reject sibling-prefix matches; do not print arbitrary command arguments.
        prefix = str(root)
        tail = parts[2].partition(prefix)
        if tail[1] and (not tail[2] or tail[2][0] in '/ \t\'"'):
            results.append(f'PID {parts[0]} {Path(parts[1]).name}')
    return results


def error_summary(path):
    if path is None or not path.is_file():
        return 'not supplied'
    try:
        # Bounded read so a large rip log cannot exhaust memory.
        with path.open('rb') as log:
            log.seek(0, 2)
            length = log.tell()
            log.seek(max(0, length - 65536))
            lines = log.read().decode('utf-8', errors='replace').splitlines()
        terms = ('read error', 'i/o error', 'failed', 'cannot read')
        count = sum(any(term in line.lower() for term in terms) for line in lines)
        return f'{count} recognized lines in last 64 KB (not a full log audit)'
    except OSError:
        return 'log unavailable'


def positive(value):
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError('interval must be a positive number')
    if not 0.1 <= number <= 3600:
        raise argparse.ArgumentTypeError('interval must be between 0.1 and 3600 seconds')
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workspace', type=Path)
    parser.add_argument('--watch', type=Path, help='one acquisition directory inside workspace')
    parser.add_argument('--expected-bytes', type=int, default=0,
                        help='trusted expected size for exactly the watched acquisition')
    parser.add_argument('--log', type=Path)
    parser.add_argument('--phase', default='Workspace observation')
    parser.add_argument('--interval', type=positive,
                        default=os.environ.get('DVD_MONITOR_INTERVAL', '2'))
    parser.add_argument('--once', action='store_true',
                        default=os.environ.get('DVD_MONITOR_ONCE') == '1')
    args = parser.parse_args()
    root = args.workspace.expanduser().resolve()
    if not root.is_dir():
        parser.error('workspace must be an existing directory')
    target = args.watch.expanduser().resolve() if args.watch else root
    if not inside(target, root):
        parser.error('watch path must be inside workspace')
    if args.log:
        args.log = args.log.expanduser().resolve()
        if not inside(args.log, root):
            parser.error('log must be inside workspace')
    if args.expected_bytes < 0 or (args.expected_bytes and not args.watch):
        parser.error('a nonnegative expected size requires an explicit --watch path')
    previous, _ = measure(target)
    previous_time = growth_time = time.monotonic()
    samples = deque(maxlen=15)
    try:
        while True:
            # Recheck containment in case directories were replaced with symlinks.
            if not inside(target, root) or (args.log and not inside(args.log, root)):
                parser.error('observed path now resolves outside workspace')
            now = time.monotonic()
            size, count = measure(target)
            delta = size - previous
            speed = max(0, delta) / max(0.001, now - previous_time)
            if delta > 0:
                growth_time = now
            if delta < 0:
                samples.clear()
            samples.append(speed)
            processes = process_summaries(root)
            if sys.stdout.isatty():
                print('\033[2J\033[H', end='')
            print('DVD archive project monitor')
            print(f'Workspace: {root}\nWatched path: {target}\nPhase: {args.phase}')
            print(f'Observed size: {human_bytes(size)}\nFiles: {count}')
            print(f'Current speed: {human_bytes(speed)}/s')
            print(f'Smoothed speed: {human_bytes(sum(samples)/len(samples))}/s')
            if args.expected_bytes:
                print(f'Acquisition size ratio: {100*size/args.expected_bytes:.1f}% '
                      '(user-supplied denominator; not completion)')
            else:
                print('Progress: no reliable denominator for this phase')
            print('Estimated remaining: not measurable')
            print('Associated processes (heuristic): ' + (', '.join(processes) or 'none detected'))
            print(f'Last growth: {int(now-growth_time)}s ago')
            if processes and now-growth_time >= 60:
                print('STALL WARNING: no observed growth for at least 60 seconds; inspect before acting')
            print('Read errors: ' + error_summary(args.log))
            print('Project free space: ' + human_bytes(shutil.disk_usage(root).free))
            print('Control-C stops only this display. Growth and process exit do not verify media.', flush=True)
            if args.once:
                return 0
            previous, previous_time = size, now
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
    except OSError as exc:
        print(f'Monitor cannot observe workspace: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
