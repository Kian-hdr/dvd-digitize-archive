---
name: dvd-digitize-archive
description: Digitize locally inserted DVDs into verified archival MKV and compatible MP4 files, show live terminal rip progress, safely resume documented workspaces, and coordinate parallel post-rip and selectable-subtitle processing. Use for DVD ripping, remuxing, transcoding, episode identification, subtitle OCR or translation, disc-by-disc continuation, preservation logging, and bounded DVD worker orchestration; do not use for Blu-ray, streaming downloads, or general video editing.
---

# DVD Digitize and Archive

Create a repeatable, evidence-based local DVD archive. Preserve source streams in MKV, create compatible H.264/AAC playback copies where appropriate, verify every output, and leave a workspace another task can resume safely.

## Public package and host adaptation

Read `README.md` for installation and `VALIDATION.md` for evidence boundaries.
Resolve the skill root from this file's actual location. No creator-specific
workspace, helper, account, terminal integration, or credential is required.
The complete scripts and generic templates are bundled alongside this file.
Use only media the user is authorized to process.

Use the current assistant's visible terminal if supported. Otherwise run the
read-only monitor in the current shell or provide the resolved command for the
user; do not invent access to an app terminal. On non-macOS hosts, substitute a
named available target player for playback checks and record QuickTime as untested.
If a required independent reviewer or GUI is unavailable, leave that gate pending.

The bundled Python helpers require Python 3.9+. The zsh entry points require zsh
and invoke the same Python monitor; `python3 scripts/monitor.py` also works directly.
Setup and synthetic validation never authorize physical-disc acquisition.

## Start safely

1. Identify the mounted optical disc and candidate workspace without altering either.
2. If the user supplies a workspace, use it. Otherwise search the user's Movies directory for a workspace whose manifest disc IDs or title match the disc. Never merge based on title alone when identity is uncertain.
3. When a candidate exists, read `WORKFLOW.md`, `STATUS.md`, `manifest.json`, and all relevant disc logs, then inspect actual files. Files on disk outrank recorded status.
4. If no matching workspace exists, identify the film or series only from disc evidence and reliable sources. Ask for a title or destination only if it cannot be established safely. Create a filesystem-safe English folder under the user's Movies directory by default.
5. Before reading a new disc, report the detected disc label and ID, selected workspace, planned disc number, and intended next action. Begin the rip only after explicit confirmation that the correct disc is inserted.

Read [references/workspace-standard.md](references/workspace-standard.md) when creating or repairing a workspace. Read [references/processing-and-verification.md](references/processing-and-verification.md) before ripping, remuxing, transcoding, identifying titles, or marking outputs verified.

For every new or resumed DVD workspace, also read [references/live-progress-monitor.md](references/live-progress-monitor.md). At the beginning of the task, start or attach one bundled read-only project monitor in the current visible assistant task terminal. Use `scripts/live_project_monitor.zsh` by default. It stays alive while idle and observes workspace growth across later phases without being tied to one disc number. Process detection is advisory and does not establish the exact phase or output path. Never open Terminal.app or another external terminal unless the user explicitly requests it. Never restart or interrupt healthy work merely to add or repair the monitor.

Immediately after starting or attaching the monitor, also post a copy-ready `zsh` code block in chat that runs the same adaptive monitor from any local terminal. Resolve the actual absolute workspace and do not give placeholders. Use the fixed-disc monitor only when the user explicitly asks for a monitor limited to one acquisition.

When the user requests optional MP4 subtitles, subtitle OCR, audio transcription, or translated subtitle tracks, read both [references/selectable-subtitles.md](references/selectable-subtitles.md) and [references/parallel-orchestration.md](references/parallel-orchestration.md). Use the coordinated subtitle workflow by default, including source reconstruction and requested translation; use sequential roles if delegation is unavailable. Treat derived translations as new authored metadata with documented provenance, not as evidence that the DVD contained that language.

When the user requests a swarm, concurrent discs, or parallel processing of independent titles, read [references/parallel-orchestration.md](references/parallel-orchestration.md). Keep optical-disc acquisition single-reader even when later phases run concurrently.

## Core invariants

- Use English for every operational surface created by this skill, regardless of the language of the user's request. This includes terminal labels and phase values, live-monitor output, chat progress reports, workspace documentation, manifests, logs, filenames, descriptions, verification reports, warnings, and handoff messages. Non-English text is allowed only inside media-specific content whose language is verified or explicitly derived, such as a documented German subtitle translation. Do not localize the terminal monitor or operational status messages into German.
- Present storage sizes and throughput in automatically selected decimal SI units: `B`, `KB`, `MB`, `GB`, or `TB`, using powers of 1000. Do not show long raw-byte counts or binary `KiB`, `MiB`, `GiB`, or `TiB` values in normal user-facing terminal or chat progress. Raw byte counts may remain in machine-readable manifests and technical evidence when exactness is required.
- Work only inside the selected media workspace, except for safe installation of an explicitly authorized required application from an official source.
- Never delete or overwrite source material or a verified output. Create corrected files separately and quarantine obsolete items before permanent deletion.
- Prefer MakeMKV when safely available from its official source. A lossless `dvdbackup`/`libdvdcss` extraction followed by a stream-copy Matroska remux is an acceptable local alternative.
- Archive MKVs retain original video, relevant audio, subtitles, chapters, and verified language tags without re-encoding.
- Compatible MP4 uses H.264 `CRF 18`, `preset medium`, `yuv420p`, and AAC unless existing workspace instructions establish another verified setting.
- Preserve confirmed frame rate and display geometry. Deinterlace only after actual interlacing is technically confirmed. Never stretch or crop merely to fill a screen.
- Preserve bitmap DVD subtitles in MKV. Put selectable subtitles in MP4 only after reliable conversion and verification; never silently invent OCR or burn subtitles into the picture.
- Label source audio and subtitle languages only when verified directly from the disc or source files. English is the default for folders, filenames, descriptions, metadata, documentation, and logs. A user-requested translated subtitle may use its target language only when clearly recorded as a derived translation; it must never be represented as an original DVD track, dub, or official-language release.
- Do not identify episodes, story parts, extras, or order from filename, duration, or alphabetical order alone. Use DVD IFO/PGC/cell structure, visible content, runtimes, supplied packaging, and reliable episode sources together.
- Stop at ambiguity that could cause a wrong title, order, language, join, split, or destructive action. Record the specific uncertainty.

## Operating modes

### Resume

Reconcile documentation and files, verify existing claimed outputs before trusting them, continue only incomplete work, and never re-encode a verified deliverable merely to reorganize it.

### New title

Create the standard workspace and documentation before the first rip. Record the first disc ID immediately. For a series, use season folders only after the season is established; otherwise use a factual provisional folder and update it without inventing metadata.

### Next disc

Compare the inserted disc ID against every manifest entry. Refuse accidental duplicates unless the user explicitly requests a controlled re-read. Only one process may read the optical drive at a time. A completed local mirror from an earlier disc may be analyzed, converted, or verified while the next confirmed disc is acquired, provided workers have non-overlapping paths and shared records remain serialized. Stop and ask before every new physical disc.

### Parallel orchestration

Use bounded parallelism only for independent work with explicit ownership. One coordinator owns the dependency graph, output-path reservations, progress synthesis, and all writes to shared status, manifest, and disc logs. Workers return structured evidence and never claim completion or edit shared records themselves. Prefer process-level concurrency for FFmpeg and other heavy media work; agents are most useful for coordinating independent analysis, identification, verification, and exception handling. If delegation is unavailable, apply the same ownership and concurrency rules locally.

### Selectable subtitles

Add optional subtitles only to compatible playback copies unless the user explicitly requests otherwise. Preserve archival MKVs and existing verified video/audio streams. Prefer original text subtitles, then verified OCR of original bitmap subtitles, and use audio transcription only when no reliable source subtitle exists. Embed verified text tracks as selectable MP4 subtitles without burning them into the image.

Use coordinator-led roles for every subtitle workflow, with agents when available and sequential work otherwise. Split OCR review, source-language correction, and translation at verified chapter or scene boundaries into uniquely owned clusters. Give each cluster limited adjacent context and a shared glossary, but never let overlapping context create duplicate output cues. Start with at most two simultaneous model-intensive clusters, measure throughput and system pressure, and raise or lower concurrency only when evidence supports it. A healthy process already in progress keeps running; do not restart it merely to adopt the swarm. The coordinator alone merges clusters, reserves final paths, writes shared documentation, and decides whether the result passes verification.

Pilot one episode before batch processing. Use separate workers for source extraction or OCR, source-language review, target-language translation, timing and continuity checks, and container/QuickTime verification. No worker may verify its own authored cluster as the sole reviewer. Batch remaining episodes only after the pilot passes timing, language metadata, switching, disabling, chapters, unchanged video/audio, and actual QuickTime playback.

## Progress and completion

Send compact progress at start, about every five minutes, at roughly each measured 10-point increase, at phase changes, and immediately on errors or stalls. Base percentages and time ranges on selected-title data size, output growth, completed titles, measured recent speed, converted runtime, and remaining verification. Present sizes and speeds with automatically selected decimal units. Say when progress is not measurable; never invent precision or interrupt a process just to measure it.

Keep the adaptive project monitor visible in the current assistant task terminal and updating about every two seconds throughout the task, including idle gaps and phase changes. It may observe only process metadata, paths inside the selected workspace, output growth, and free storage. Stopping or closing it must never stop or signal a rip, conversion, OCR, translation, or verification process. Chat updates remain required even while the display is running.

Include the exact copy-ready adaptive-monitor command in the task-start or rip-start chat update so the user can paste it into the ChatGPT terminal or another local shell. Repeat it on request. A disc, phase, or output-path change must not require a new command.

Pass an English phase description to the live monitor, for example `DVD 6 lossless mirror`. Keep every displayed label, warning, unit description, and completion message in English.

Treat analysis, extraction, technical joining, identification, archive creation, compatible conversion, geometry checks, stream/transition checks, and QuickTime playback as separate phases. Report 100% only when every required phase for that disc is verified. Cross-disc stories may leave a compatible joined output pending while the current disc's source and archive work are complete.

At handoff, state retained outputs, languages, durations, verification performed, warnings, unresolved work, and whether the user may insert the next disc. Update the workspace records before waiting.
