#!/usr/bin/env python3
"""Build one SDR HEVC (or legacy H.264) MP4 with reviewed audio tracks, or a verified silent source."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


ROLE_FLAGS = ("dub", "original", "comment", "hearing_impaired", "visual_impaired", "descriptions")


def normalized_language(stream):
    value = str(stream.get("tags", {}).get("language", "")).strip().lower()
    return {"en": "eng", "de": "deu", "ger": "deu"}.get(value, value)


def audio_label(stream):
    tags = stream.get("tags", {})
    title = str(tags.get("title", "")).strip().replace("\n", " ")
    language_code = normalized_language(stream)
    language = {"eng": "English", "deu": "German"}.get(language_code,
                                                        language_code or "Unknown language")
    profile = stream.get("profile")
    codec_name = stream.get("codec_name") or "unknown codec"
    codec = (profile if profile and profile not in {"unknown", "LC"} else
             {"ac3": "AC-3", "eac3": "E-AC-3", "dts": "DTS", "aac": "AAC"}.get(codec_name,
                                                                                         codec_name.upper()))
    layout = stream.get("channel_layout") or ""
    channels = ("5.1" if layout.startswith("5.1") else
                "7.1" if layout.startswith("7.1") else
                "stereo" if stream["channels"] == 2 else
                "mono" if stream["channels"] == 1 else f"{stream['channels']}ch")
    source_index = stream.get("index")
    roles = [flag.replace("_", " ") for flag in ROLE_FLAGS
             if stream.get("disposition", {}).get(flag) == 1]
    detail = title if title and title.casefold() not in {"stereo", "mono", "surround 5.1", "surround 7.1"} else ""
    suffix = " - " + ", ".join(filter(None, [detail, *roles])) if detail or roles else ""
    return f"{language} {codec} {channels} (source {source_index}){suffix}"


def audio_disposition(stream, default=False):
    flags = (["default"] if default else []) + [flag for flag in ROLE_FLAGS
                                                  if stream.get("disposition", {}).get(flag) == 1]
    return "+".join(flags) if flags else "0"


def primary_audio_rank(stream):
    """Prefer the main, highest-fidelity mix without treating a core as an alternate."""
    profile = str(stream.get("profile") or "").casefold()
    codec = str(stream.get("codec_name") or "").casefold()
    title = str(stream.get("tags", {}).get("title") or "").casefold()
    special = any(stream.get("disposition", {}).get(flag) for flag in
                  ("comment", "hearing_impaired", "visual_impaired", "descriptions"))
    special = special or any(word in title for word in ("commentary", "descriptive", "description"))
    fidelity = (6 if any(word in profile for word in ("dts-hd ma", "truehd", "lossless"))
                or codec in {"flac", "pcm_bluray", "pcm_s24le"} else
                4 if "dts-hd hra" in profile else
                3 if codec == "dts" else
                2 if codec in {"eac3", "ac3"} else 1)
    bitrate = str(stream.get("bit_rate") or "")
    return (not special, fidelity, stream.get("channels") or 0,
            int(bitrate) if bitrate.isdigit() else 0, -stream["index"])


def verify_audio_mapping(output, source_streams, audio_streams, copied, derived,
                         primary_only=False):
    try:
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(output)],
                               capture_output=True, text=True, check=True)
        actual = [stream for stream in json.loads(probe.stdout).get("streams", [])
                  if stream.get("codec_type") == "audio"]
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"could not verify output audio streams: {error}", file=sys.stderr)
        return False
    if primary_only:
        expected = [(index, "aac", source_streams[index]["channels"]) for index in audio_streams]
        expected_labels = [f"{audio_label(source_streams[index])} - AAC-LC "
                           f"{source_streams[index]['channels']}ch" for index in audio_streams]
    else:
        expected = ([(index, "aac", min(source_streams[index]["channels"], 2)) for index in audio_streams]
                    + [(index, source_streams[index]["codec_name"], source_streams[index]["channels"])
                       for index in copied]
                    + [(index, "aac", source_streams[index]["channels"]) for index in derived])
        expected_labels = (
            [f"{audio_label(source_streams[index])} - TV AAC-LC "
             f"{'mono' if source_streams[index]['channels'] == 1 else 'stereo'}" for index in audio_streams]
            + [f"{audio_label(source_streams[index])} - original bitstream" for index in copied]
            + [f"{audio_label(source_streams[index])} - AAC-LC "
               f"{source_streams[index]['channels']}ch surround" for index in derived]
        )
    if len(actual) != len(expected):
        print(f"audio mapping mismatch: expected {len(expected)} tracks, found {len(actual)}; "
              "candidate retained for inspection", file=sys.stderr)
        return False
    if not expected:
        print("Video-only output verified: no audio streams")
        return True
    for position, ((index, codec, channels), stream) in enumerate(zip(expected, actual)):
        language = normalized_language(source_streams[index]) or "und"
        got_language = normalized_language(stream) or "und"
        role_mismatch = [flag for flag in ROLE_FLAGS
                         if bool(source_streams[index].get("disposition", {}).get(flag))
                         != bool(stream.get("disposition", {}).get(flag))]
        if (stream.get("codec_name") != codec or stream.get("channels") != channels
                or got_language != language
                or stream.get("tags", {}).get("handler_name") != expected_labels[position]
                or role_mismatch
                or bool(stream.get("disposition", {}).get("default")) != (position == 0)):
            print(f"audio mapping mismatch at output track {position}: source {index}, "
                  f"expected {codec}/{channels}ch/{language}, got "
                  f"{stream.get('codec_name')}/{stream.get('channels')}ch/{got_language}; "
                  f"role differences {role_mismatch}; label "
                  f"{stream.get('tags', {}).get('handler_name')!r}, expected "
                  f"{expected_labels[position]!r}; "
                  "candidate retained for inspection", file=sys.stderr)
            return False
    if primary_only:
        print(f"Audio mapping verified: exactly {len(audio_streams)} primary language tracks, "
              "each AAC with the source channel count; no extra MP4 audio tracks")
    else:
        print(f"Audio mapping verified: {len(audio_streams)} retained source tracks have selectable AAC versions; "
              f"{len(copied)} original copies and {len(derived)} full-channel AAC tracks")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path, help="new candidate MP4 path; never a verified final")
    parser.add_argument("--video-stream", type=int, required=True, help="global ffprobe stream index")
    audio_choice = parser.add_mutually_exclusive_group(required=True)
    audio_choice.add_argument("--audio-stream", type=int, action="append",
                              help="preferred source stream per language; English is first/default when present")
    audio_choice.add_argument("--video-only", action="store_true",
                              help="encode without audio only when ffprobe confirms the source has no audio streams")
    parser.add_argument("--audio-language", action="append", dest="audio_languages",
                        help="requested MP4 language (repeatable; overrides default eng/deu); use 'all' only when explicitly requested")
    parser.add_argument("--all-source-streams", action="store_true",
                        help="explicitly retain every requested-language source mix as separate MP4 tracks; never use for the two-track TV default")
    parser.add_argument("--video-codec", choices=("hevc", "h264"), default="hevc",
                        help="HEVC Main/Main10 follows source depth; h264 is for 8-bit legacy targets")
    parser.add_argument("--crf", type=int, default=18,
                        help="quality target; compare a real source pilot before changing the default")
    parser.add_argument("--preset", choices=("fast", "medium", "slow"), default="medium")
    parser.add_argument("--experimental-truehd-mp4", action="store_true",
                        help="copy TrueHD into MP4 for a device-specific pilot; TV support is unverified")
    parser.add_argument("--allow-derived-surround", action="store_true",
                        help="deprecated compatibility flag; full-channel AAC is automatic for retained multichannel streams")
    parser.add_argument("--allow-pending-original-audio", action="store_true",
                        help="make AAC tracks for retained languages while unsupported original bitstreams remain in the MKV; blocks source cleanup")
    parser.add_argument("--vf", help="reviewed video filter for geometry/deinterlace; no filter by default")
    parser.add_argument("--sdr-confirmed", action="store_true", help="confirm source is SDR after inspection")
    parser.add_argument("--run", action="store_true", help="execute; default prints the reviewed command")
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if not source.is_file() or source.stat().st_size == 0:
        parser.error("source must be a nonempty file")
    if output.suffix.casefold() != ".mp4" or not output.parent.is_dir() or output.exists():
        parser.error("output must be a new .mp4 path in an existing working directory")
    if source == output:
        parser.error("source and output must differ")
    if not 1 <= args.crf <= 51:
        parser.error("--crf must be between 1 and 51; lossless output needs a separate plan")

    try:
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(source)],
                               capture_output=True, text=True, check=True)
        streams = {s["index"]: s for s in json.loads(probe.stdout).get("streams", [])}
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as error:
        print(f"could not inspect source streams: {error}", file=sys.stderr)
        return 1

    video = streams.get(args.video_stream)
    if not video or video.get("codec_type") != "video":
        parser.error("--video-stream must identify a video stream")
    preferred_audio = args.audio_stream or []
    all_audio = sorted(index for index, stream in streams.items() if stream.get("codec_type") == "audio")
    if args.video_only and all_audio:
        parser.error(f"--video-only requires a source with no audio streams; found {all_audio}")
    if args.video_only and args.audio_languages:
        parser.error("--audio-language cannot be used with --video-only")
    if len(set(preferred_audio)) != len(preferred_audio):
        parser.error("audio stream indices must be distinct")
    for index in preferred_audio:
        if not streams.get(index) or streams[index].get("codec_type") != "audio":
            parser.error(f"audio stream {index} is missing or not audio")
    requested_languages = {str(value).strip().lower() for value in (args.audio_languages or ["eng", "deu"])}
    retain_all_languages = "all" in requested_languages
    if retain_all_languages:
        requested_languages = set()
    else:
        requested_languages = {
            normalized_language({"tags": {"language": value}})
            for value in requested_languages
        }
        excluded_preferred = [index for index in preferred_audio
                              if normalized_language(streams[index]) not in requested_languages]
        if excluded_preferred:
            parser.error(f"preferred audio streams {excluded_preferred} are outside the retained languages; "
                         "name their language with --audio-language or use --audio-language all "
                         "only when that broader retention is explicitly requested")
    full_stream_mode = args.all_source_streams or retain_all_languages
    if args.video_only:
        audio_streams = []
    elif full_stream_mode:
        audio_streams = preferred_audio + [
            index for index in all_audio
            if index not in preferred_audio
            and (retain_all_languages or normalized_language(streams[index]) in requested_languages)
        ]
    else:
        preferred_by_language = {}
        for index in preferred_audio:
            language = normalized_language(streams[index])
            if language in preferred_by_language:
                parser.error(f"two preferred streams are both {language}; use --all-source-streams "
                             "only when multiple mixes in the MP4 are explicitly requested")
            preferred_by_language[language] = index
        language_order = [language for language in ("eng", "deu") if language in requested_languages]
        language_order += sorted(requested_languages - set(language_order))
        audio_streams = []
        for language in language_order:
            candidates = [index for index in all_audio
                          if normalized_language(streams[index]) == language]
            if candidates:
                audio_streams.append(preferred_by_language.get(
                    language, max(candidates, key=lambda index: primary_audio_rank(streams[index]))))
        if not audio_streams:
            parser.error("no requested-language source audio found; request an available language explicitly "
                         "rather than silently dropping source audio")
        if len(audio_streams) > 2 and not args.audio_languages:
            parser.error("the default TV profile permits at most two primary language tracks")
    for index in audio_streams:
        if not isinstance(streams[index].get("channels"), int) or streams[index]["channels"] < 1:
            parser.error(f"audio stream {index} has no confirmed channel count")
    if full_stream_mode:
        appended = audio_streams[len(preferred_audio):]
        if appended:
            label = "all source languages" if retain_all_languages else ", ".join(sorted(requested_languages))
            print(f"Including retained-language audio streams {appended} ({label})", file=sys.stderr)
        mp4_copyable = [index for index in audio_streams
                        if streams[index].get("codec_name") in {"aac", "ac3", "eac3"}
                        or (streams[index].get("codec_name") == "truehd" and args.experimental_truehd_mp4)]
        derived_surround = [index for index in audio_streams if streams[index]["channels"] > 2]
        unsupported = [index for index in audio_streams if index not in mp4_copyable]
        if unsupported and not args.allow_pending_original_audio:
            parser.error(f"original bitstreams {unsupported} cannot be copied in the standard MP4 profile; "
                         "use --allow-pending-original-audio while retaining the MKV")
        if unsupported:
            print(f"WARNING: originals {unsupported} need verified sidecars before MKV cleanup", file=sys.stderr)
        if any(streams[index].get("codec_name") == "truehd" for index in mp4_copyable):
            print("WARNING: TrueHD-in-MP4 muxing is experimental; TV playback remains unverified", file=sys.stderr)
    else:
        mp4_copyable = []
        derived_surround = []
        if audio_streams:
            retained_originals = [index for index in all_audio
                                  if normalized_language(streams[index]) in requested_languages]
            print(f"TV profile: one primary per available language {audio_streams}; "
                  f"preserve original source streams {retained_originals} in verified sidecars "
                  "or keep the MKV until resolved", file=sys.stderr)
    if any(streams[index]["channels"] > 8 for index in audio_streams):
        parser.error("AAC above 8 channels needs a separate reviewed plan")

    hdr_transfer = video.get("color_transfer") in {"smpte2084", "arib-std-b67"}
    wide_color = video.get("color_primaries") in {"bt2020"} or video.get("color_space") in {"bt2020nc", "bt2020c"}
    dolby_vision = any("Dolby Vision" in str(item) or "DOVI" in str(item)
                       for item in video.get("side_data_list", []))
    if hdr_transfer or wide_color or dolby_vision:
        parser.error("HDR/wide-color source requires a reviewed target and tone-mapping workflow")
    source_pix_fmt = video.get("pix_fmt")
    if source_pix_fmt not in {"yuv420p", "yuv420p10le"}:
        parser.error("source must be verified 8- or 10-bit 4:2:0 SDR; "
                     "do not reduce bit depth or chroma without a separate plan")
    if args.video_codec == "h264" and source_pix_fmt == "yuv420p10le":
        parser.error("10-bit source requires HEVC Main10 here; legacy H.264 would lose bit depth")
    if args.run and not args.sdr_confirmed:
        parser.error("--run requires --sdr-confirmed after checking source color information")
    if video.get("field_order") not in {None, "unknown", "progressive"} and not args.vf:
        parser.error("interlaced source requires an explicit reviewed filter or separate analysis")
    sar = video.get("sample_aspect_ratio")
    if sar not in {None, "0:1", "1:1"} and not args.vf:
        parser.error("non-square source pixels require an explicit reviewed geometry filter")

    command = ["ffmpeg", "-nostdin", "-hide_banner", "-n", "-i", str(source),
               "-map", f"0:{args.video_stream}"]
    if args.video_only:
        command += ["-an"]
    for index in audio_streams:
        command += ["-map", f"0:{index}"]
    for index in mp4_copyable:
        command += ["-map", f"0:{index}"]
    for index in derived_surround:
        command += ["-map", f"0:{index}"]
    encoder = "libx265" if args.video_codec == "hevc" else "libx264"
    command += ["-map_metadata", "0", "-map_chapters", "0", "-c:v", encoder,
                "-preset", args.preset, "-crf", str(args.crf), "-pix_fmt", source_pix_fmt]
    if args.video_codec == "hevc":
        command += ["-profile:v", "main10" if source_pix_fmt == "yuv420p10le" else "main",
                    "-tag:v", "hvc1"]
    color_options = (
        ("color_range", "-color_range"),
        ("color_space", "-colorspace"),
        ("color_transfer", "-color_trc"),
        ("color_primaries", "-color_primaries"),
    )
    for field, option in color_options:
        value = video.get(field)
        if value and value not in {"unknown", "unspecified", "reserved"}:
            command += [option, value]
    if args.vf:
        command += ["-vf", args.vf]
    for position, index in enumerate(audio_streams):
        channels = (min(streams[index]["channels"], 2) if full_stream_mode
                    else streams[index]["channels"])
        language = normalized_language(streams[index]) or "und"
        if full_stream_mode:
            kind = "mono" if channels == 1 else "stereo"
            label = f"{audio_label(streams[index])} - TV AAC-LC {kind}"
            bitrate = "96k" if channels == 1 else "192k"
        else:
            label = f"{audio_label(streams[index])} - AAC-LC {channels}ch"
            bitrate = ("96k" if channels == 1 else "192k" if channels == 2 else
                       "640k" if channels <= 6 else "768k")
        command += [f"-c:a:{position}", "aac", f"-profile:a:{position}", "aac_low",
                    f"-ac:a:{position}", str(channels), f"-ar:a:{position}", "48000",
                    f"-b:a:{position}", bitrate,
                    f"-disposition:a:{position}", audio_disposition(streams[index], default=position == 0),
                    f"-metadata:s:a:{position}", f"language={language}",
                    f"-metadata:s:a:{position}", f"title={label}",
                    f"-metadata:s:a:{position}", f"handler_name={label}"]
    for position, index in enumerate(mp4_copyable, start=len(audio_streams)):
        language = streams[index].get("tags", {}).get("language") or "und"
        label = f"{audio_label(streams[index])} - original bitstream"
        command += [f"-c:a:{position}", "copy",
                    f"-disposition:a:{position}", audio_disposition(streams[index]),
                    f"-metadata:s:a:{position}", f"language={language}",
                    f"-metadata:s:a:{position}", f"title={label}",
                    f"-metadata:s:a:{position}", f"handler_name={label}"]
    for position, index in enumerate(derived_surround, start=len(audio_streams) + len(mp4_copyable)):
        channels = streams[index]["channels"]
        language = streams[index].get("tags", {}).get("language") or "und"
        label = f"{audio_label(streams[index])} - AAC-LC {channels}ch surround"
        command += [f"-c:a:{position}", "aac", f"-profile:a:{position}", "aac_low",
                    f"-ac:a:{position}", str(channels), f"-b:a:{position}", "768k" if channels > 6 else "640k",
                    f"-disposition:a:{position}", audio_disposition(streams[index]),
                    f"-metadata:s:a:{position}", f"language={language}",
                    f"-metadata:s:a:{position}", f"title={label}",
                    f"-metadata:s:a:{position}", f"handler_name={label}"]
    if any(streams[index].get("codec_name") == "truehd" for index in mp4_copyable):
        command += ["-strict", "-2"]
    command += ["-movflags", "+faststart", str(output)]

    print(shlex.join(command))
    if not args.run:
        return 0
    try:
        result = subprocess.run(command, check=False)
        if result.returncode:
            return result.returncode
        return 0 if verify_audio_mapping(output, streams, audio_streams, mp4_copyable,
                                         derived_surround, primary_only=not full_stream_mode and
                                         not args.video_only) else 2
    except OSError as error:
        print(f"ffmpeg unavailable: {error}", file=sys.stderr)
        return 69


if __name__ == "__main__":
    sys.exit(main())
