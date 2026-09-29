# Target-player playback gate

Read this for every MP4 prepared for a particular TV or other player. A successful FFmpeg decode, codec table, or computer-player session does not establish actual playback or audible language switching on that device. Record its exact model and firmware when available, source route (such as direct USB), audio output chain, file hash, and observed result. Check the current manufacturer specifications for the exact model before selecting a codec profile.

## Choose a pilot

- For an 8-bit SDR 4:2:0 source, preview HEVC Main 8-bit (`hvc1`) in MP4. For a 10-bit SDR 4:2:0 source, preserve 10-bit with HEVC Main10 (`hvc1`). Start with a short **real-title** excerpt at x265 CRF 18/preset medium, preserving source resolution and frame rate. Compare its quality and size with the original. Use H.264 only as a documented 8-bit fallback for a device that needs it.
- Keep source audio in the original-stream MKV until the user's retention policy is met. The helper's default English/German profile puts one verified primary mix per available language in MP4 as AAC-LC at the source channel count. For other policies, select explicit languages and verify the resulting map. Do not invent a missing dub or treat AAC as a copy of a lossless/immersive original.
- Use `scripts/media_audit.py FILE --report REPORT.json --decode --tv-baseline --compare-source SOURCE --source-video-stream N` for technical checks. Add `--allow-surround-default` only for a multichannel first/default track, or `--allow-silent-source` only for a genuinely audio-less source. Those flags check stream mapping; they never prove physical player support.

Play the pilot from the actual intended route on **each target device**. Check opening, middle, seek, and ending; listen for dialogue level, centering and sync. Switch every requested language in the device menu and verify its audible identity. If surround or an immersive original matters, confirm the actual receiver/output signal on a capable chain; channel metadata alone does not prove physical playback. Record success or `player playback pending` per device and profile before batching.

If playback fails, compare codec profile, pixel format, color tags, audio codec, channels, default flags, and the device's selected track and output mode. Make a short corrected candidate under a new path, then retest on the same device before re-encoding a collection. Keep the original source and failed evidence until the cause is resolved.

On some ExFAT USB transfers, macOS may create `._*.mp4` AppleDouble metadata files that a player lists as videos. Inspect the destination for these companions after copying and hash checking. Quarantine only confirmed AppleDouble companions of real MP4s through the user's recoverable deletion mechanism, then recheck file count and playback. Never remove an unexpected `._*` file by name alone.
