# Processing and verification

## Disc analysis

Record disc ID/label, DVD norm, titles, title sets, PGCs, cells, chapters, VOB segments, timecodes, durations, resolution, frame rate, stored SAR/DAR, field order, audio, and subtitles. Treat IFO structure as the primary technical source for program structure and intended aspect ratio, then compare it with stream metadata and representative images.

Exclude menus, logos, trailers, and extras only with positive evidence. Technical VOB/cell segments from one title belong in IFO order; official story parts are a separate editorial question. Never join merely because files are adjacent or similarly sized.

## Archive creation

Remux without video or audio re-encoding. Preserve original geometry flags, chapters, relevant audio, and bitmap subtitles. If source metadata is demonstrably wrong, preserve the original stream and document any corrected container metadata in a new file. Do not conceal the correction.

## Compatible creation

Use H.264 CRF 18, preset medium, yuv420p, and AAC. Preserve relevant verified audio tracks and make English default only when appropriate. Preserve the confirmed source frame rate.

For anamorphic DVD sources, prefer square-pixel output when that improves QuickTime and television reliability. Examples, only after confirming source norm and 4:3 DAR:

- PAL 4:3: 768x576, SAR 1:1
- NTSC 4:3: 640x480, SAR 1:1

Calculate 16:9 or mixed-format output proportionally. Do not upscale unnecessarily, stretch, or crop content. Deinterlace before final scaling only when repeated representative analysis confirms genuine interlacing; a field-order header alone is insufficient.

Join official parts only when their relationship and order are established. Preserve credits, recaps, intros, and repetitions unless removal is separately authorized. If joined parts differ technically, normalize proportionally and use neutral black padding as needed. Add chapters at original part boundaries where possible.

## Verification gate

For each final file:

1. Confirm path, nonzero size, readable container, and expected duration.
2. Inspect codecs, stream count, verified language tags/default flags, chapters, resolution, frame rate, SAR/DAR, and interlace result.
3. Fully decode video and audio; record exit status and every warning timestamp.
4. Count subtitle packets and verify track selectability when present.
5. Compare archive duration with DVD title and joined MP4 duration with the sum of confirmed parts.
6. Inspect beginning, middle, end, each part transition, and every warning location. Check audio continuity and synchronization.
7. Visually check faces, circles, planets, text, and logos for horizontal or vertical distortion.
8. Open every final MP4 in QuickTime Player and actually play multiple positions. Decoder success alone is not QuickTime verification.
9. Record hashes when useful for reorganization or duplicate detection.

Decoder warnings aligned with known cell/chapter timestamp discontinuities may be recoverable, but classify them only after correlation and playback inspection. Re-read suspected physical errors to a new path and compare results. Never replace a suspect source silently.

## Progress model

Report current-phase and estimated overall-disc progress separately. Estimate read, conversion, verification, and total remaining time as ranges. Smooth recent throughput rather than extrapolating from a momentary rate. Widen estimates during retries, speed variation, or error correction. State how long no progress has been observed when a phase stalls.

Use automatically selected decimal units for every user-facing size and speed: `B`, `KB`, `MB`, `GB`, or `TB`, based on powers of 1000. Do not expose long raw-byte counts or binary `KiB`, `MiB`, `GiB`, or `TiB` values in normal progress reports. Exact byte counts remain appropriate in manifests, hashes, and technical verification evidence.
