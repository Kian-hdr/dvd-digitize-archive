# Workspace standard

Use this layout for a new title. Add further season folders only when established. Keep lossless acquisition and joins under `.work/`, and make each complete, verified original-stream MKV watchable under `Original_MKV/` until its final MP4 passes every required check.

```text
Title_Name/
├── WORKFLOW.md
├── STATUS.md
├── manifest.json
├── .work/
│   └── Disc_01/
├── Original_MKV/
│   ├── Specials/
│   ├── Season_01/
│   └── Bonus_Material/Disc_01/
├── Compatible_MP4/
│   └── Season_01/
└── Logs/
    ├── DVD_01.md or BD_01.md
    └── technical.log
```

For a film, the final file may live directly under `Compatible_MP4/`. Do not create a season label for a film. Create only the `Original_MKV/` subfolders supported by the acquired content: `Season_NN/` for established episodes, `Specials/` for specials, `Films/` for films, and `Bonus_Material/DVD_NN/` or `Bonus_Material/BD_NN/` for disc-numbered extras. Use same-volume hardlinks from verified `.work/` title MKVs when possible; otherwise verify copied bytes before exposing the file. Keep `.work/` source paths intact for processing and never show interrupted encodes or test clips as originals. Existing verified MKV archives remain under their current retention policy.

## Required records

`WORKFLOW.md` is the durable local policy. Record title scope, paths, actual tool versions, temporary-source and final MP4 settings, language and naming rules, verification, read-error handling, progress reporting, and the confirmation gate for a new disc.

`STATUS.md` is the concise human-readable state. For every disc use only: `Not started`, `In progress`, `Partially completed`, `Completed and verified`, `Failed`, `Blocked`, or `Unclear`. Do not mark completion before checks pass.

`manifest.json` is the machine-readable source of disc and title state. At minimum retain:

- schema version, root, and update timestamp
- disc number, format (`DVD`, `Blu-ray`, or `UHD Blu-ray` when verified), label, structural fingerprint and its method, other available identity evidence, detection/completion timestamps, and status
- DVD title/title-set/PGC/cell or Blu-ray MakeMKV title/playlist/segment/angle identity and classification, as applicable
- one official season/episode or film identity per final MP4, plus confidence; for split sources, ordered part paths, trims/boundaries, and evidence that they belong to this episode only
- source duration, video geometry/scan and color/HDR data when applicable
- every disc/source audio and subtitle stream with language, channel count/layout, codec, default/role/forced flags, and immersive format evidence when present; record the user-selected retained languages and distinguish verified tags from package claims
- a source-to-MP4 audio mapping for each requested primary language and a verified original-bitstream sidecar or retained-MKV mapping for every source stream the user chose to preserve; record indices, language/role labels, codec, channels, packet hashes and unresolved streams
- final MP4 path, size, duration, hash when calculated, retained-language and multichannel switchability result, audio-copy/derived-track results, TV fallback check, physical TV playback result, and verification booleans
- original MKV paths under `Original_MKV/`, their `.work/` sources, hardlink or copy relationship, remaining dependencies and cleanup status; do not mark a source disposable while a required track, join, playback check or verification is unresolved
- read errors, verification notes, and remaining work

Use `null`, empty values, or explicit `Unknown` state for missing evidence. Never fabricate a value to satisfy the schema. Write JSON atomically and validate it after every update.

For a mixed film/series franchise, keep one `watch_order.json`, a generated `WATCH_ORDER.txt`, and a numbered playback view per continuity as described in [franchise watch order](franchise-watch-order.md). The manifest may include relevant missing titles with dated region-specific offers; the playback view stays bounded. Reference the order file from `STATUS.md` and retain each episode's own identity; the display ordinal never replaces its `SxxExx` number.

`Logs/DVD_NN.md` or `Logs/BD_NN.md` is the chronological disc record: start/end times, identity, title/playlist selection evidence, exclusions, streams, commands/settings, created files, sizes/durations, warnings/retries, decode and sample checks, applicable player results, uncertainty, and next step. Keep disc-specific raw scans and audit reports under `Logs/`; put large program output in technical logs, never in chat or manifest. Never store secrets.

## Naming

For new episode exports, an episode-first underscore pattern such as `S01E01_Official_Episode_Title_Series_Name_Year.mp4` helps ordering. Use the same stem for sources and subtitle sidecars; append a variant or language when needed. Keep two-digit minimum season/episode numbers, verified official wording, and a verified series year if known. Reuse `scripts/media_filename.py`. Do not rename existing verified files solely to apply this convention.

Use the same episode/film stem for original-audio sidecars and append the verified language plus source stream index, for example `S01E01_Title_Series_Year_German_Source03_Original.mka`. Keep sidecars with the final MP4 in an identified audio-preservation folder and record exact relative paths in the manifest; the MP4 retains its own selectable version of that language.

Name each watchable original MKV with the established episode, film or special stem and `.mkv`. Preserve official continuation labels such as `Part_1` and `Part_2` as separate files. When a technical title still lacks an official name or spans more than one official episode, give it a factual provisional description with its verified disc title number until the content boundaries are established, such as `T06_Observed_Production_Footage.mkv` under the disc's bonus folder. The visible name must not turn a partial source or unverified bonus label into an official episode.

```text
S01E01_Opening_Episode_Series_Name_2024.mp4
S01E01_Opening_Episode_Series_Name_2024_English.srt
Film_Title_2024.mp4
```

Use a factual provisional name when identification is uncertain. `Season_00` and `S00E01` are for identified specials when the chosen metadata source assigns them; keep unclassified extras under a factual `Extras` path. Never use a multi-episode filename such as `S01E01-E02` for a final file: split official episodes into separately numbered MP4s. Conversely, merge multiple technical files of one episode into one MP4. Films use `Film_Title_1982.mp4` with a verified year.

## Resumption and cleanup

On every invocation, compare records with the actual filesystem. Correct stale paths and preserve logs, disc identity evidence, unfinished sources and verified outputs. Keep each `Original_MKV/` title available until its MP4 passes content, source/output comparison, stream, subtitle, decode and required player gates. Source cleanup requires this user’s explicit authorization and the [cleanup gate](processing-and-verification.md#temporary-mkv-cleanup-gate). Check all same-inode hardlinks and copied aliases, remove only authorized paths through recoverable handling, verify the result, and update records. Never treat a prior verified archive or user-provided source as disposable by default.
