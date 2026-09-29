# Processing and verification

## Disc analysis

Record format, disc identity evidence/label, titles, chapters, timecodes, durations, resolution, frame rate, SAR/DAR, scan mode, audio, and subtitles. For DVDs, include norm, title sets, PGCs, cells, and VOB segments; treat IFO structure as the primary technical source for program structure and intended aspect ratio, then compare it with stream metadata and representative images. For Blu-ray, follow [Blu-ray decisions](blu-ray.md) for playlist, segment, angle, color/HDR, PGS, and UHD details.

Exclude menus, logos, trailers, and extras only with positive evidence. Technical DVD VOB/cell segments from one title belong in IFO order; Blu-ray segments belong in the selected playlist order. Those structures identify source sequence, not necessarily episode boundaries. Never join merely because files are adjacent or similarly sized.

## Temporary source and episode assembly

Keep a lossless local MKV or disc mirror in `.work/` while it is needed for episode mapping, audio/subtitle preservation, re-reads, and final verification. Once a complete original-stream MKV is verified, expose it in the workspace's `Original_MKV/` layout for playback while its MP4 is pending. A same-volume hardlink preserves the `.work/` path without storing a second media copy; otherwise verify a separate copy before presenting it. Record both paths and keep the original available while an episode spans another disc, a requested track remains unresolved, or the corresponding MP4 has not passed all required validation and player checks. An interrupted encode or test clip is not a watchable original.

Define the official episode unit before editing. For every final `SxxExx` MP4, record the ordered source files or chapter/cell/playlist ranges and evidence that they all belong to that episode. When one official episode is split across several technical files, trim only verified non-episode material and join its content in story order. When one source file contains two official episodes, split at verified boundaries and make two MP4s. Episodes officially named `Part I`, `Part II`, or `Part III` retain distinct episode IDs and final files even when one story arc spans them.

Use `scripts/join_episode_parts.py` only on reviewed MP4 pieces with matching streams. Its concat preflight and duration check do not establish episode identity or remove duplicate content. Inspect the opening, each join, and ending for inserted menus or repeated trailers/openings; preserve intentional recaps, credits, and dialogue. If streams differ, normalize in separately named working candidates, then join. Never use a cross-episode concatenation to simplify file count. [FFmpeg's concat demuxer](https://ffmpeg.org/ffmpeg-formats.html#concat-1) requires matching streams and adjusts timestamps, so verify audio/video synchronization after every join.

## Compatible creation

Create one final MP4 per official episode or film, plus each distinct bonus item when complete-disc coverage is requested. For an SDR 4:2:0 source and a capable target player, use `scripts/compatible_encode.py` to preview a source-matched HEVC Main 8-bit or Main10 10-bit (`hvc1`) MP4 at initial CRF 18/preset medium. Its default English/German profile chooses one verified main mix per available language, retains source channel count as AAC-LC, and never invents a missing dub. Confirm or change this language profile for the user before encoding. Preserve other source streams required by that policy as verified `.mka` sidecars or retain the MKV. Use `--all-source-streams` only when every mix should appear in MP4 and `--audio-language all` only when every language is requested. Compare a representative real-source pilot with the source and measured size before a batch. Keep source frame rate and 10-bit depth; make a separate HDR/UHD or 3D plan. Apply the [TV playback gate](tv-playback.md) before claiming device compatibility.

For a verified source title with **zero audio streams**, use `compatible_encode.py SOURCE CANDIDATE.mp4 --video-stream N --video-only` instead of an audio-stream argument. This option rejects any source with audio, and output verification requires zero MP4 audio tracks. Run `media_audit.py` with `--tv-baseline --allow-silent-source --compare-source SOURCE --source-video-stream N`; the silent exception only passes when the source also has zero audio. A silent video still needs visual, full-decode and actual player checks. Do not synthesize audio or use this route to drop a source track.

## Retained audio language gate

Before encoding, enumerate every source audio stream with index, verified language, codec, channels, default and role flags. Choose the best verified main mix for each requested MP4 language. The helper defaults to English and German where present; use explicit language options for another policy. Record source-to-MP4 mappings and source-to-sidecar or retained-MKV mappings for every original stream the user wants preserved. Inspect handler labels and sample actual language; unknown or incorrect tags require review.

For each original audio bitstream the user wants to retain, including selected primaries, cores, commentary and alternate mixes, keep the source MKV or extract that single stream losslessly to a separately verified `.mka` sidecar when supported. Preview and record the exact stream index and destination; never overwrite a sidecar. For example, after checking paths and indices:

```bash
ffmpeg -nostdin -hide_banner -n -i SOURCE.mkv -map 0:STREAM_INDEX -c copy EPISODE_STEM_Language_SourceNN_Original.mka
python3 scripts/compare_audio_stream.py SOURCE.mkv STREAM_INDEX EPISODE_STEM_Language_SourceNN_Original.mka 0 --report Logs/Audio_SourceNN_Copy.json
```

Audit and decode the sidecar, verify its codec, channels, language and packet hash, and retain it beside the final MP4. AAC is **not** a bitstream copy of DTS-HD, TrueHD, FLAC, PCM or another original codec. If copying or verification fails, retain the MKV. Do not clear a source until each requested MP4 language is selectable, every required original bitstream is preserved in a verified sidecar or retained MKV, and no requested stream remains unresolved.

For anamorphic DVD sources, prefer square-pixel output when that improves QuickTime and television reliability. Examples, only after confirming source norm and 4:3 DAR:

- PAL 4:3: 768x576, SAR 1:1
- NTSC 4:3: 640x480, SAR 1:1

Calculate 16:9 or mixed-format output proportionally. Do not upscale unnecessarily, stretch, or crop content. Deinterlace before final scaling only when repeated representative analysis confirms genuine interlacing; a field-order header alone is insufficient.

Add chapters at verified same-episode part boundaries where possible. Do not create one chaptered MP4 containing several official episodes.

## Verification gate

For each final file:

1. Confirm path, nonzero size, readable container, and expected duration.
2. Inspect codecs, stream count, **source-to-MP4 audio count and mapping**, audio channel counts/layouts, verified language and role tags/default flags, chapters, resolution, frame rate, SAR/DAR, pixel format/bit depth, color range/primaries/transfer/matrix, and interlace result. Run `media_audit.py --compare-source SOURCE --source-video-stream N` for the encoded MP4. Stop cleanup on a signalled mismatch or unknown source color metadata until its meaning is independently established and documented. Use `scripts/compare_audio_stream.py` on every copied original audio track or sidecar; a derived mono/stereo fallback is not a bitstream copy.
3. Use `scripts/media_audit.py FILE --report REPORT.json --decode` for a full video/audio decode and compact stream report. Record exit status and every warning timestamp from its saved log. Add `--hash` when needed for relocation or duplicate evidence.
4. Count subtitle packets with `scripts/media_audit.py --count-subtitles` and verify track selectability when present. Packet count is not the same as subtitle cue count.
5. Compare final MP4 duration with the confirmed single episode or film and the sum of its included technical parts. Check that no separately numbered episode is present or missing.
6. Compare source and MP4 at the beginning, middle, end, every same-episode join, every warning location, and representative dark, grainy, fast-moving, detailed-text and gradient scenes. Use aligned frames and actual playback to look for lost detail, banding, blocking, motion errors, audio continuity and synchronization. Record inspected timestamps and any differences. A lossy HEVC encode cannot be certified as mathematically identical by sampling or a perceptual score.
7. Visually check faces, circles, planets, text, and logos for horizontal or vertical distortion.
8. Open each final compatible MP4 in the actual target player and play multiple positions. Check every requested audio language, default and alternate selection, audible identity, channel layout and sync. On macOS, check QuickTime separately when it is a target. For a multichannel first/default track, `--tv-baseline --allow-surround-default --compare-source SOURCE --source-video-stream N` checks stream mapping but cannot prove a TV decodes AAC surround. Test a real-source pilot on each target device as described in [TV playback](tv-playback.md). Record per-file physical checks separately; decoder success alone is not playback verification.
9. Record hashes when useful for reorganization or duplicate detection.

Decoder warnings aligned with known cell/chapter timestamp discontinuities may be recoverable, but classify them only after correlation and playback inspection. Re-read suspected physical errors to a new path and compare results. Never replace a suspect source silently.

## Temporary MKV cleanup gate

Delete an original-stream MKV only after this user has explicitly authorized cleanup and the corresponding content and retention gates pass. Confirm the exact episode or cut, source-to-MP4 audio map, every required original stream in a verified sidecar or other retained source, subtitle completion, full decode, visual comparison, and applicable player tests. Check all `.work/`, `Original_MKV/`, and other hardlink or copy paths, plus any pending join, re-read, alternate cut or error investigation. Record the cleanup decision and verify remaining paths and space. Never treat an earlier archive or user-provided source as disposable by default; if a gate is unresolved, retain the original and name the blocker. Inspected scenes cannot prove a lossy MP4 mathematically identical to its source.

## Progress model

Report current-phase and estimated overall-disc progress separately. Estimate read, conversion, verification, and total remaining time as ranges. Smooth recent throughput rather than extrapolating from a momentary rate. Widen estimates during retries, speed variation, or error correction. State how long no progress has been observed when a phase stalls.

Use automatically selected decimal units for every user-facing size and speed: `B`, `KB`, `MB`, `GB`, or `TB`, based on powers of 1000. Do not expose long raw-byte counts or binary `KiB`, `MiB`, `GiB`, or `TiB` values in normal progress reports. Exact byte counts remain appropriate in manifests, hashes, and technical verification evidence.
