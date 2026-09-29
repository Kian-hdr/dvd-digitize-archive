#!/usr/bin/env python3
"""Join reviewed MP4 pieces of one episode into a new candidate without re-encoding."""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path


def inside(path, root):
    return os.path.commonpath((str(path), str(root))) == str(root)


def probe(path):
    command = ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"ffprobe failed for {path}: {result.stderr.strip()[:300]}")
    data = json.loads(result.stdout)
    keys = ("codec_type", "codec_name", "profile", "time_base", "width", "height",
            "pix_fmt", "sample_aspect_ratio", "avg_frame_rate", "color_transfer",
            "sample_rate", "channels", "channel_layout")
    signature = [{key: stream.get(key) for key in keys}
                 for stream in data.get("streams", [])]
    duration = float(data.get("format", {}).get("duration", 0))
    if not signature or duration <= 0:
        raise ValueError(f"missing streams or duration: {path}")
    return signature, duration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--episode", required=True, help="one established episode ID, e.g. S01E01")
    parser.add_argument("--part", type=Path, action="append", required=True,
                        help="repeat in verified story order; full episode-only parts")
    parser.add_argument("--output", type=Path, required=True, help="new candidate MP4")
    parser.add_argument("--report", type=Path, required=True, help="new JSON evidence path")
    parser.add_argument("--content-reviewed", action="store_true",
                        help="acknowledge that every part belongs to this one episode")
    parser.add_argument("--run", action="store_true", help="execute; default previews the plan")
    args = parser.parse_args()
    root = args.workspace.resolve()
    parts = [path.resolve() for path in args.part]
    output, report = args.output.resolve(), args.report.resolve()
    episode = args.episode.upper()
    if not root.is_dir() or not re.fullmatch(r"S\d{2,}E\d{2,}", episode):
        parser.error("workspace must exist and episode must be like S01E01")
    if len(parts) < 2 or len(set(parts)) != len(parts):
        parser.error("provide at least two distinct parts in verified order")
    if not all(path.is_file() and path.suffix.casefold() == ".mp4" and inside(path, root) for path in parts):
        parser.error("all parts must be local MP4 files inside the workspace")
    if (output.suffix.casefold() != ".mp4" or not re.match(rf"(?:\d{{4,}}_)?{episode}_", output.name.upper())
            or output.exists() or not output.parent.is_dir() or not inside(output, root)):
        parser.error("output must be a new episode-named MP4 inside the workspace")
    if report.exists() or not report.parent.is_dir() or not inside(report, root):
        parser.error("report must be a new path inside the workspace")
    for path in parts:
        codes = re.findall(r"S\d{2,}E\d{2,}", path.name.upper())
        if any(code != episode for code in codes) or re.search(r"S\d{2,}E\d{2,}-E\d{2,}", path.name.upper()):
            parser.error(f"part filename suggests another or multiple episodes: {path.name}")

    try:
        inspected = [probe(path) for path in parts]
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"part preflight failed: {error}", file=sys.stderr)
        return 1
    signature = inspected[0][0]
    if any(item[0] != signature for item in inspected[1:]):
        parser.error("part stream layouts differ; normalize separately before concatenation")
    expected = sum(item[1] for item in inspected)
    print(f"{episode}: {len(parts)} reviewed-order parts; expected {expected:.3f} s; candidate {output}")
    if not args.run:
        return 0
    if not args.content_reviewed:
        parser.error("--run requires --content-reviewed after checking episode identity and boundaries")

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".ffconcat",
                                     prefix=f".{episode}_", dir=str(output.parent), delete=False) as handle:
        list_path = Path(handle.name)
        handle.write("ffconcat version 1.0\n")
        for path in parts:
            escaped = path.as_posix().replace("'", "'\\''")
            handle.write(f"file '{escaped}'\n")
    command = ["ffmpeg", "-nostdin", "-hide_banner", "-n", "-f", "concat", "-safe", "0",
               "-i", str(list_path), "-map", "0", "-c", "copy", "-movflags", "+faststart", str(output)]
    try:
        completed = subprocess.run(command, check=False)
        actual = probe(output)[1] if completed.returncode == 0 else None
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"join failed: {error}", file=sys.stderr)
        completed = None
        actual = None
    finally:
        list_path.unlink(missing_ok=True)
    tolerance = max(1.5, expected * 0.005)
    result = {"schema_version": 1, "episode": episode,
              "parts": [{"path": str(path), "duration_seconds": item[1]} for path, item in zip(parts, inspected)],
              "expected_duration_seconds": expected, "output": str(output),
              "actual_duration_seconds": actual, "duration_tolerance_seconds": tolerance,
              "stream_signature": signature, "content_review_acknowledged": True,
              "ffmpeg_exit_code": completed.returncode if completed else None,
              "command": shlex.join(command),
              "technical_duration_pass": actual is not None and abs(actual - expected) <= tolerance,
              "content_and_playback_verified": False}
    with report.open("x", encoding="utf-8") as target:
        json.dump(result, target, indent=2)
        target.write("\n")
    print(f"candidate join {'PASS' if result['technical_duration_pass'] else 'FAIL'}; report {report}; visual and playback checks pending")
    return 0 if result["technical_duration_pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
