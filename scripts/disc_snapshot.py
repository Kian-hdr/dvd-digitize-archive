#!/usr/bin/env python3
"""Read-only DVD/Blu-ray structure snapshot; fingerprint is not a disc serial."""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def child(parent, name):
    return next((p for p in parent.iterdir() if p.name.casefold() == name.casefold()), None)


def hash_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def snapshot(path):
    root = path.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("mount path must be a directory")
    if root.name.casefold() in {"bdmv", "video_ts"}:
        root = root.parent

    bdmv = child(root, "BDMV")
    video_ts = child(root, "VIDEO_TS")
    if bool(bdmv) == bool(video_ts):
        raise ValueError("expected exactly one BDMV or VIDEO_TS directory")
    selected = bdmv or video_ts
    if selected.is_symlink() or not selected.is_dir():
        raise ValueError("disc control directory must be a real directory")

    if bdmv:
        disc_format = "Blu-ray"
        uhd_status = "unverified"
        control = [p for p in bdmv.rglob("*") if p.is_file() and p.suffix.casefold() in {".bdmv", ".mpls", ".clpi"}]
        media = [p for p in bdmv.rglob("*") if p.is_file() and p.suffix.casefold() == ".m2ts"]
    else:
        disc_format = "DVD"
        uhd_status = "not applicable"
        control = [p for p in video_ts.rglob("*") if p.is_file() and p.suffix.casefold() in {".ifo", ".bup"}]
        media = [p for p in video_ts.rglob("*") if p.is_file() and p.suffix.casefold() == ".vob"]

    if not control:
        raise ValueError("no expected control files found")
    if any(item.is_symlink() for item in control + media):
        raise ValueError("disc snapshot refuses symlinked control or media files")
    digest = hashlib.sha256()
    for item in sorted(control, key=lambda p: str(p.relative_to(root)).casefold()):
        relative = item.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(str(item.stat().st_size).encode("ascii") + b"\0")
        digest.update(bytes.fromhex(hash_file(item)))

    largest = sorted(media, key=lambda p: p.stat().st_size, reverse=True)[:8]
    return {
        "schema_version": 1,
        "mount_path": str(root),
        "volume_label": root.name,
        "format": disc_format,
        "uhd_status": uhd_status,
        "structural_fingerprint_sha256": digest.hexdigest(),
        "fingerprint_method": "sorted relative control-file paths, sizes, and SHA-256 contents; not a physical-disc serial",
        "control_file_count": len(control),
        "media_file_count": len(media),
        "media_file_bytes": sum(p.stat().st_size for p in media),
        "largest_media_files": [
            {"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size} for p in largest
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mount_path", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(snapshot(args.mount_path), indent=2, ensure_ascii=False))
    except (OSError, ValueError) as error:
        print(f"disc snapshot failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
