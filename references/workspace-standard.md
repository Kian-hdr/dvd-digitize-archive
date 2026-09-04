# Workspace standard

Use this layout for a new title. Add further season folders only when established. Keep temporary working data inside the workspace while active and quarantine it before deletion.

```text
Title_Name/
├── WORKFLOW.md
├── STATUS.md
├── manifest.json
├── Original_MKV/
│   └── Season_01/
├── Compatible_MP4/
│   └── Season_01/
└── Logs/
    ├── DVD_01.md
    └── technical.log
```

For a film, files may live directly under `Original_MKV/` and `Compatible_MP4/`. Do not create a season label for a film.

Generic starting points are bundled in `templates/`. Copy them only into a new
workspace, replace unknown fields with verified evidence, and use paths relative
to the workspace root where possible. The empty manifest is a starting structure,
not a validator or evidence that a disc has been processed.

## Required records

`WORKFLOW.md` is the durable local policy. Record title scope, paths, actual tool versions, archive and MP4 settings, language and naming rules, verification, read-error handling, progress reporting, and the confirmation gate for a new disc.

`STATUS.md` is the concise human-readable state. For every disc use only: `Not started`, `In progress`, `Partially completed`, `Completed and verified`, `Failed`, `Blocked`, or `Unclear`. Do not mark completion before checks pass.

`manifest.json` is the machine-readable source of disc and title state. At minimum retain:

- schema version, root, and update timestamp
- disc number, ID, label, detection/completion timestamps, and status
- DVD title/title-set identity and classification
- season/episode or film identity plus confidence
- source duration and video geometry/interlace data
- every verified audio and subtitle stream with language
- archive and compatible paths, sizes, durations, hashes when calculated, and verification booleans
- read errors, verification notes, and remaining work

Use `null`, empty values, or explicit `Unknown` state for missing evidence. Never fabricate a value to satisfy the schema. Write JSON atomically and validate it after every update.

`Logs/DVD_NN.md` is the chronological disc record: start/end times, identity, titles, exclusions, streams, commands/settings, created files, sizes/durations, warnings/retries, decode and sample checks, QuickTime result, uncertainty, and next step. Put detailed program output in `Logs/technical.log`; never store secrets.

## Naming

Use underscores, two-digit numbering, official English titles, series/film identity, and year only when verified:

```text
S01E01_Official_English_Title_Series_Name_1978.mkv
S01E01_Official_English_Title_Series_Name_1978.mp4
Film_Title_1982.mkv
Film_Title_1982.mp4
```

Use a factual provisional name when identification is uncertain. Preserve official archive parts only when boundaries are established. A verified joined story MP4 may omit part suffixes while archive MKVs retain source release structure.

## Resumption and cleanup

On every invocation, compare records with the actual filesystem. Correct stale paths and contradictory active instructions. Preserve logs, disc IDs, verification evidence, unfinished sources, and verified outputs. Before permanent cleanup, list exact candidates and reasons, confirm no item is the sole retained copy of needed media or evidence, move candidates to a quarantine folder inside the workspace, recheck remaining outputs and records, and obtain explicit approval before deleting quarantine.
