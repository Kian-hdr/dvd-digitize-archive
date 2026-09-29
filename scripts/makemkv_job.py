#!/usr/bin/env python3
"""Preview or run a logged MakeMKV scan, info, title extraction, or Blu-ray backup."""

import argparse
import csv
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def within(path, root):
    return os.path.commonpath((str(path), str(root))) == str(root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True, help="new disc-specific log path")
    parser.add_argument("--run", action="store_true", help="execute after disc and paths are confirmed")
    jobs = parser.add_subparsers(dest="job", required=True)
    jobs.add_parser("scan", help="list current drives without acquiring titles")
    info = jobs.add_parser("info", help="inspect one current disc or verified local backup")
    info_source = info.add_mutually_exclusive_group(required=True)
    info_source.add_argument("--disc", type=int)
    info_source.add_argument("--backup-dir", type=Path, help="verified local Blu-ray backup inside workspace")
    title = jobs.add_parser("title", help="extract one selected title from disc or verified local backup")
    title_source = title.add_mutually_exclusive_group(required=True)
    title_source.add_argument("--disc", type=int)
    title_source.add_argument("--backup-dir", type=Path, help="verified local Blu-ray backup inside workspace")
    title.add_argument("--title", type=int, required=True)
    title.add_argument("--output-dir", type=Path, required=True)
    backup = jobs.add_parser("backup", help="create a separate Blu-ray full-disc backup")
    backup.add_argument("--disc", type=int, required=True)
    backup.add_argument("--output-dir", type=Path, required=True)
    backup.add_argument("--decrypt", action="store_true", help="ask MakeMKV to decrypt backup streams")
    args = parser.parse_args()

    root = args.workspace.resolve()
    log = args.log.resolve()
    if not root.is_dir() or not log.parent.is_dir() or not within(log, root) or log.exists():
        parser.error("workspace must exist and log must be a new path inside it")
    if args.job in {"info", "title", "backup"} and args.disc is not None and args.disc < 0:
        parser.error("disc index must be nonnegative and checked against the current drive scan")

    if args.job in {"info", "title"} and args.backup_dir is not None:
        backup_source = args.backup_dir.resolve()
        if not within(backup_source, root) or not (backup_source / "BDMV" / "index.bdmv").is_file():
            parser.error("backup source must be a verified Blu-ray folder inside the workspace")
        source_name = f"file:{backup_source}"
    elif args.job in {"info", "title", "backup"}:
        source_name = f"disc:{args.disc}"

    command = ["makemkvcon", "-r", "--messages=-stdout", "--progress=-same"]
    if args.job == "scan":
        command += ["info", "disc:9999"]
    elif args.job == "info":
        command += ["--minlength=0", "info", source_name]
    else:
        output = args.output_dir.resolve()
        if not output.parent.is_dir() or not within(output, root) or output.exists():
            parser.error("output directory must be a new path inside the workspace")
        if args.job == "title":
            if args.title < 0:
                parser.error("title ID must be nonnegative and checked against disc info")
            command += ["--minlength=0", "mkv", source_name, str(args.title), str(output)]
        else:
            command += ["backup"]
            if args.decrypt:
                command += ["--decrypt"]
            command += [source_name, str(output)]

    print(shlex.join(command))
    if not args.run:
        return 0
    if not shutil.which("makemkvcon"):
        print("makemkvcon is unavailable; use an official installation", file=sys.stderr)
        return 69
    if args.job == "title":
        try:
            output.mkdir()
        except OSError as error:
            print(f"Could not create title output directory: {error}", file=sys.stderr)
            return 73
    with log.open("x", encoding="utf-8") as target:
        target.write(f"UTC start: {datetime.now(timezone.utc).isoformat()}\nCommand: {shlex.join(command)}\n\n")
        target.flush()
        try:
            completed = subprocess.run(command, stdout=target, stderr=subprocess.STDOUT, check=False)
        except OSError as error:
            target.write(f"\nExecution error: {error}\n")
            print(f"MakeMKV execution failed: {error}", file=sys.stderr)
            return 69
        target.write(f"\nExit code: {completed.returncode}\n")
    if args.job == "title" and completed.returncode == 0:
        saved = failed = None
        title_failed = False
        with log.open(encoding="utf-8") as source:
            for line in source:
                if line.startswith("MSG:5003,"):
                    title_failed = True
                elif line.startswith("MSG:5004,"):
                    fields = next(csv.reader([line.removeprefix("MSG:").strip()]))
                    if len(fields) >= 7:
                        saved, failed = int(fields[-2]), int(fields[-1])
        output_files = [p for p in output.glob("*.mkv") if p.is_file() and p.stat().st_size > 0]
        if title_failed or (saved is not None and (saved != 1 or failed != 0)) or len(output_files) != 1:
            with log.open("a", encoding="utf-8") as target:
                target.write("Post-check: FAILED; expected one saved, nonempty MKV and no failed title.\n")
            print(f"MakeMKV reported success but title output failed verification; log {log}", file=sys.stderr)
            return 74
    print(f"MakeMKV {args.job} exit {completed.returncode}; log {log}")
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
