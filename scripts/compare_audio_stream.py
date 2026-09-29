#!/usr/bin/env python3
"""Compare one source and exported audio stream by codec, channels, and packet hash."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def checked(command):
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {result.stderr.strip()[:400]}")
    return result.stdout


def evidence(path, index):
    probe = json.loads(checked(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)]))
    stream = next((s for s in probe.get("streams", []) if s.get("index") == index), None)
    if not stream or stream.get("codec_type") != "audio":
        raise ValueError(f"audio stream {index} not found in {path}")
    lines = checked(["ffmpeg", "-v", "error", "-i", str(path), "-map", f"0:{index}",
                     "-c", "copy", "-f", "streamhash", "-hash", "SHA256", "-"]).splitlines()
    hashes = [line.removeprefix("0,a,SHA256=") for line in lines
              if line.startswith("0,a,SHA256=")]
    if len(hashes) != 1 or len(hashes[0]) != 64:
        raise ValueError(f"could not read one SHA-256 stream hash for {path}")
    return {"path": str(path), "index": index, "codec": stream.get("codec_name"),
            "channels": stream.get("channels"), "channel_layout": stream.get("channel_layout"),
            "sample_rate": stream.get("sample_rate"), "packet_sha256": hashes[0]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("source_stream", type=int)
    parser.add_argument("export", type=Path)
    parser.add_argument("export_stream", type=int)
    parser.add_argument("--report", type=Path, required=True, help="new JSON evidence path")
    args = parser.parse_args()
    source, export, report = args.source.resolve(), args.export.resolve(), args.report.resolve()
    if not source.is_file() or not export.is_file() or not report.parent.is_dir() or report.exists():
        parser.error("source/export must exist and report must be a new path in an existing directory")
    try:
        before = evidence(source, args.source_stream)
        after = evidence(export, args.export_stream)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"audio comparison failed: {error}", file=sys.stderr)
        return 1
    fields = ("codec", "channels", "channel_layout", "sample_rate", "packet_sha256")
    differences = [field for field in fields if before[field] != after[field]]
    result = {"schema_version": 1, "source": before, "export": after,
              "bitstream_copy_verified": not differences, "differences": differences}
    try:
        with report.open("x", encoding="utf-8") as target:
            json.dump(result, target, indent=2)
            target.write("\n")
    except OSError as error:
        print(f"could not save report: {error}", file=sys.stderr)
        return 1
    print(f"audio stream copy {'PASS' if not differences else 'FAIL'}; report {report}")
    return 0 if not differences else 2


if __name__ == "__main__":
    sys.exit(main())
