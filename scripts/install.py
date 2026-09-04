#!/usr/bin/env python3
"""Install a self-contained copy into a NEW exact destination. Never overwrite."""
import argparse
from pathlib import Path
import shutil
import sys

FILES = ('SKILL.md', 'README.md', 'SETUP_PROMPT.md', 'LICENSE', 'ATTRIBUTION.md',
         'CHANGELOG.md', 'VALIDATION.md')
DIRS = ('agents', 'references', 'scripts', 'templates', 'tests')


def install(source, destination, dry_run=False):
    source = source.resolve()
    destination = destination.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError('destination already exists; preserved unchanged; choose a new directory')
    if destination.resolve() == source or source in destination.resolve().parents:
        raise ValueError('destination must be outside the source repository')
    for name in FILES + DIRS:
        item = source / name
        if not item.exists():
            raise ValueError('incomplete package: ' + name)
        if item.is_symlink() or (item.is_dir() and any(p.is_symlink() for p in item.rglob('*'))):
            raise ValueError('unexpected symlink in package: ' + name)
    if dry_run:
        print('Would install complete skill into: ' + str(destination))
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()  # exclusive creation; no existing installation is replaced
    for name in FILES:
        shutil.copy2(source / name, destination / name)
    for name in DIRS:
        shutil.copytree(source / name, destination / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
    print('Installed into: ' + str(destination))
    print('Existing assistant configuration was not changed. Reload your assistant if needed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True, type=Path, help='exact new skill directory')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        install(Path(__file__).resolve().parents[1], args.dest, args.dry_run)
        return 0
    except (ValueError, OSError) as exc:
        print('Installation stopped: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
