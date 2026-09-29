#!/usr/bin/env python3
"""Save ffprobe evidence and optional full decode, printing one compact result."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compact_stream(stream):
    keys = (
        "index", "codec_type", "codec_name", "profile", "width", "height", "pix_fmt",
        "sample_aspect_ratio", "display_aspect_ratio", "avg_frame_rate", "field_order",
        "color_range", "color_space", "color_transfer", "color_primaries", "channels",
        "channel_layout", "sample_rate", "bits_per_raw_sample",
    )
    result = {key: stream[key] for key in keys if key in stream}
    result["language"] = stream.get("tags", {}).get("language")
    result["title"] = stream.get("tags", {}).get("title")
    result["default"] = stream.get("disposition", {}).get("default", 0)
    result["forced"] = stream.get("disposition", {}).get("forced", 0)
    return result


def write_new_json(path, value):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=str(path.parent),
                                     prefix=f".{path.name}.", delete=False) as target:
        temp_name = target.name
        json.dump(value, target, indent=2, ensure_ascii=False)
        target.write("\n")
        target.flush()
        os.fsync(target.fileno())
    try:
        os.link(temp_name, path)  # Fails rather than replacing existing evidence.
    finally:
        os.unlink(temp_name)


def compare_source_video(source, source_index, output_streams):
    command = ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(source)]
    probe = subprocess.run(command, text=True, capture_output=True, check=False)
    if probe.returncode:
        raise ValueError(f"source ffprobe failed: {probe.stderr.strip()[:300]}")
    streams = json.loads(probe.stdout).get("streams", [])
    before = next((stream for stream in streams if stream.get("index") == source_index), None)
    after_video = [stream for stream in output_streams if stream.get("codec_type") == "video"]
    if not before or before.get("codec_type") != "video" or len(after_video) != 1:
        raise ValueError("expected the selected source video stream and exactly one output video stream")
    after = after_video[0]
    issues, unknowns = [], []
    for field in ("width", "height", "pix_fmt", "sample_aspect_ratio", "field_order"):
        original = before.get(field)
        encoded = after.get(field)
        if original in (None, "unknown", "0:1"):
            unknowns.append(f"source {field} is unknown")
        elif original != encoded:
            issues.append(f"{field} changed: {original} -> {encoded}")
    try:
        original_rate = Fraction(before.get("avg_frame_rate", "0/0"))
        encoded_rate = Fraction(after.get("avg_frame_rate", "0/0"))
        if original_rate <= 0 or encoded_rate <= 0:
            unknowns.append("frame rate is unknown")
        elif original_rate != encoded_rate:
            issues.append(f"average frame rate changed: {original_rate} -> {encoded_rate}")
    except (TypeError, ValueError, ZeroDivisionError):
        unknowns.append("frame rate is unknown")
    for field in ("color_range", "color_space", "color_transfer", "color_primaries"):
        original = before.get(field)
        encoded = after.get(field)
        if original in (None, "unknown", "unspecified", "reserved"):
            unknowns.append(f"source {field} is unknown")
        elif original != encoded:
            issues.append(f"{field} changed: {original} -> {encoded}")
    source_audio_channels = {}
    for stream in streams:
        if stream.get("codec_type") == "audio":
            language = str(stream.get("tags", {}).get("language") or "und").lower()
            language = {"en": "eng", "de": "deu", "ger": "deu"}.get(language, language)
            source_audio_channels.setdefault(language, []).append(stream.get("channels"))
    return {"source_path": str(source), "source_video_stream": source_index,
            "source_audio_stream_count": sum(len(channels) for channels in source_audio_channels.values()),
            "source_audio_channels_by_language": source_audio_channels,
            "passed": not issues and not unknowns, "issues": issues, "unknowns": unknowns,
            "scope": "geometry, pixel format, frame rate and signalled color only; not perceptual image identity"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--report", type=Path, required=True, help="new JSON path inside the media workspace")
    parser.add_argument("--decode", action="store_true", help="fully decode every video and audio stream")
    parser.add_argument("--count-subtitles", action="store_true", help="count subtitle packets with a full ffprobe pass")
    parser.add_argument("--tv-baseline", action="store_true", help="check MP4/HEVC Main or Main10, or legacy H.264, with AAC-LC; physical TV playback remains required")
    parser.add_argument("--allow-silent-source", action="store_true",
                        help="with --tv-baseline and --compare-source, accept zero output audio only when the source also has zero audio")
    parser.add_argument("--allow-surround-default", action="store_true",
                        help="with --tv-baseline and --compare-source, verify one full-channel AAC track per expected language; physical playback remains pending")
    parser.add_argument("--expected-audio-language", action="append",
                        help="ordered language for surround-default audit (repeatable; default: eng then deu where present)")
    parser.add_argument("--compare-source", type=Path,
                        help="check output geometry, frame rate and color tags against this source")
    parser.add_argument("--source-video-stream", type=int,
                        help="global source video stream index, required with --compare-source")
    parser.add_argument("--hash", action="store_true", help="calculate source SHA-256")
    args = parser.parse_args()
    source = args.file.resolve()
    report = args.report.resolve()
    decode_log = report.with_name(report.stem + ".decode.log")
    if not source.is_file() or source.stat().st_size == 0:
        parser.error("input must be an existing nonempty file")
    if not report.parent.is_dir():
        parser.error("report parent directory must already exist")
    if report.exists() or (args.decode and decode_log.exists()):
        parser.error("report or decode log already exists; choose a new evidence path")
    if (args.compare_source is None) != (args.source_video_stream is None):
        parser.error("--compare-source and --source-video-stream must be supplied together")
    if args.allow_silent_source and (not args.tv_baseline or args.compare_source is None):
        parser.error("--allow-silent-source requires --tv-baseline and --compare-source with --source-video-stream")
    if args.allow_surround_default and (not args.tv_baseline or args.compare_source is None):
        parser.error("--allow-surround-default requires --tv-baseline and --compare-source with --source-video-stream")
    if args.expected_audio_language and not args.allow_surround_default:
        parser.error("--expected-audio-language requires --allow-surround-default")
    if args.allow_silent_source and args.allow_surround_default:
        parser.error("silent-source and surround-default exceptions are mutually exclusive")

    command = ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-show_chapters", "-of", "json", str(source)]
    try:
        probe = subprocess.run(command, text=True, capture_output=True, check=False)
    except OSError as error:
        print(f"ffprobe unavailable: {error}", file=sys.stderr)
        return 69
    if probe.returncode != 0:
        print(f"ffprobe failed ({probe.returncode}): {probe.stderr.strip()[:500]}", file=sys.stderr)
        return 1
    try:
        raw = json.loads(probe.stdout)
    except json.JSONDecodeError as error:
        print(f"invalid ffprobe JSON: {error}", file=sys.stderr)
        return 1

    result = {
        "schema_version": 1,
        "source": str(source),
        "size_bytes": source.stat().st_size,
        "duration_seconds": raw.get("format", {}).get("duration"),
        "streams": [compact_stream(s) for s in raw.get("streams", [])],
        "chapter_count": len(raw.get("chapters", [])),
        "ffprobe": raw,
    }
    exit_code = 0
    if args.compare_source is not None:
        comparison_source = args.compare_source.resolve()
        if not comparison_source.is_file() or comparison_source == source:
            parser.error("--compare-source must be a different existing source file")
        try:
            result["source_match"] = compare_source_video(
                comparison_source, args.source_video_stream, raw.get("streams", []))
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"source video comparison failed: {error}", file=sys.stderr)
            return 1
        if not result["source_match"]["passed"]:
            exit_code = 2
    if args.tv_baseline:
        video = [s for s in raw.get("streams", []) if s.get("codec_type") == "video"]
        audio = [s for s in raw.get("streams", []) if s.get("codec_type") == "audio"]
        issues = []
        warnings = []
        if source.suffix.casefold() != ".mp4" or "mp4" not in raw.get("format", {}).get("format_name", ""):
            issues.append("container is not MP4")
        if len(video) != 1:
            issues.append("expected exactly one video stream")
        else:
            primary = video[0]
            if primary.get("codec_name") == "hevc":
                profile_format = {"Main": "yuv420p", "Main 10": "yuv420p10le"}
                profile = primary.get("profile")
                if (profile not in profile_format or primary.get("pix_fmt") != profile_format.get(profile)
                        or primary.get("codec_tag_string") != "hvc1"):
                    issues.append("HEVC TV profile needs matching Main 8-bit or Main10 10-bit 4:2:0 and hvc1")
                result["tv_video_profile"] = "HEVC Main10 10-bit" if profile == "Main 10" else "HEVC Main 8-bit"
                if profile == "Main 10":
                    warnings.append("Main10 needs a separate physical TV playback pilot")
            elif primary.get("codec_name") == "h264":
                if primary.get("pix_fmt") != "yuv420p":
                    issues.append("H.264 TV profile needs yuv420p")
                result["tv_video_profile"] = "legacy H.264"
            else:
                issues.append("expected HEVC Main/Main10 or legacy H.264 video")
        if args.allow_silent_source and result["source_match"]["source_audio_stream_count"]:
            issues.append("claimed silent source contains audio streams")
        if not audio and not args.allow_silent_source:
            issues.append("audio stream missing")
        elif audio and args.allow_silent_source:
            issues.append("silent-source MP4 unexpectedly has audio streams")
        elif audio and args.allow_surround_default:
            configured_languages = args.expected_audio_language or ["eng", "deu"]
            configured_languages = [{"en": "eng", "de": "deu", "ger": "deu"}.get(
                value.strip().lower(), value.strip().lower()) for value in configured_languages]
            if len(set(configured_languages)) != len(configured_languages):
                issues.append("expected audio languages must be unique")
            expected_languages = [language for language in configured_languages
                                  if language in result["source_match"]["source_audio_channels_by_language"]]
            actual_languages = []
            if not expected_languages or len(audio) != len(expected_languages):
                issues.append("expected one primary AAC track per configured source language")
            for position, stream in enumerate(audio):
                language = str(stream.get("tags", {}).get("language") or "und").lower()
                language = {"en": "eng", "de": "deu", "ger": "deu"}.get(language, language)
                actual_languages.append(language)
                if (stream.get("codec_name") != "aac" or stream.get("profile") != "LC"
                        or str(stream.get("sample_rate")) != "48000"):
                    issues.append(f"audio stream {stream.get('index')} is not AAC-LC 48 kHz")
                channels = stream.get("channels")
                if (not isinstance(channels, int) or channels <= 2 or channels > 8
                        or channels not in result["source_match"]["source_audio_channels_by_language"].get(language, [])):
                    issues.append(f"audio stream {stream.get('index')} does not preserve source surround channels")
                if bool(stream.get("disposition", {}).get("default")) != (position == 0):
                    issues.append(f"audio stream {stream.get('index')} has incorrect default selection")
            if actual_languages != expected_languages:
                issues.append(f"audio languages/order {actual_languages} differ from {expected_languages}")
            warnings.append("AAC surround default and language switching require physical TV playback checks")
        elif audio:
            fallback = audio[0]
            if (fallback.get("codec_name") != "aac" or fallback.get("profile") != "LC"
                    or fallback.get("channels") not in {1, 2}
                    or str(fallback.get("sample_rate")) != "48000"):
                issues.append("first audio stream is not AAC-LC mono/stereo 48 kHz")
            if fallback.get("disposition", {}).get("default", 0) != 1:
                issues.append("first audio stream is not default")
            for stream in audio[1:]:
                if stream.get("codec_name") not in {"aac", "ac3", "eac3"}:
                    warnings.append(f"secondary audio stream {stream.get('index')} needs device-specific playback testing")
                if stream.get("disposition", {}).get("default", 0):
                    issues.append(f"secondary audio stream {stream.get('index')} is unexpectedly default")
        result["tv_baseline"] = {"passed": not issues, "issues": issues, "warnings": warnings,
                                 "scope": ("verified silent source and video profile only; physical TV playback untested"
                                           if args.allow_silent_source else
                                           "one full-channel AAC track per configured source language; physical TV support untested"
                                           if args.allow_surround_default else
                                           "primary fallback profile only; secondary surround and physical TV playback untested")}
        if issues:
            exit_code = 2
    if args.hash:
        result["sha256"] = sha256(source)

    if args.count_subtitles:
        count_command = ["ffprobe", "-v", "error", "-count_packets", "-select_streams", "s",
                         "-show_entries", "stream=index,nb_read_packets", "-of", "json", str(source)]
        counted = subprocess.run(count_command, text=True, capture_output=True, check=False)
        if counted.returncode != 0:
            print(f"subtitle packet count failed ({counted.returncode}): {counted.stderr.strip()[:500]}", file=sys.stderr)
            return 1
        result["subtitle_packet_counts"] = {
            str(s["index"]): int(s.get("nb_read_packets", 0))
            for s in json.loads(counted.stdout).get("streams", [])
        }

    if args.decode:
        decode_command = ["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-v", "warning", "-i", str(source),
                          "-map", "0:v?", "-map", "0:a?", "-f", "null", "-"]
        try:
            with decode_log.open("x", encoding="utf-8") as log:
                decoded = subprocess.run(decode_command, stdout=subprocess.DEVNULL, stderr=log, check=False)
            if decoded.returncode != 0:
                exit_code = decoded.returncode
            with decode_log.open(encoding="utf-8", errors="replace") as saved_log:
                warning_lines = sum(1 for line in saved_log if line.strip())
            result["decode"] = {"exit_code": decoded.returncode, "log": str(decode_log),
                                "nonempty_log_lines": warning_lines}
        except OSError as error:
            result["decode"] = {"exit_code": None, "error": str(error)}
            exit_code = 69

    try:
        write_new_json(report, result)
    except OSError as error:
        print(f"could not save audit report: {error}", file=sys.stderr)
        return 1

    stream_text = ", ".join(f"{s.get('codec_type', '?')}:{s.get('codec_name', '?')}:{s.get('language') or '?'}"
                             for s in result["streams"])
    decode_text = "not run"
    if args.decode:
        decode_text = f"exit {result['decode']['exit_code']}, log lines {result['decode'].get('nonempty_log_lines', '?')}"
    subtitle_text = f"; subtitle packets {result['subtitle_packet_counts']}" if args.count_subtitles else ""
    tv_text = f"; TV baseline {'pass' if result['tv_baseline']['passed'] else 'fail'}" if args.tv_baseline else ""
    match_text = ""
    if args.compare_source is not None:
        match = result["source_match"]
        match_text = (f"; source video {'match' if match['passed'] else 'review needed'}"
                      f" ({len(match['issues'])} differences, {len(match['unknowns'])} unknowns)")
    print(f"{source.name}: {result['duration_seconds'] or '?'} s; {len(result['streams'])} streams [{stream_text}]; "
          f"{result['chapter_count']} chapters; decode {decode_text}{subtitle_text}{tv_text}{match_text}; report {report}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
