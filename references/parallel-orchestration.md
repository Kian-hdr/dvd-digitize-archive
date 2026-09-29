# Parallel optical-disc orchestration

Use this mode when the user requests concurrent work, wants independent titles processed concurrently, or wants a verified local source from one disc processed while the next disc is acquired.

## Scheduling boundary

Treat optical acquisition as an exclusive resource. Never run multiple MakeMKV, `dvdbackup`, `libdvdcss`, or equivalent readers against the same optical drive. Before asking for the next disc:

1. Verify the previous disc has a complete, structurally readable local source or no longer needs the drive. A title MKV does not establish a full-disc backup.
2. Confirm no active process still accesses the optical device or mounted disc.
3. Report the previous disc's local state and the proposed next disc number.
4. Ask the user to insert and explicitly confirm the next disc.
5. Read the new disc label and identity evidence without modification and compare it with every manifest entry before acquisition.

Once a disc has the required verified local source, its local analysis, remuxing, conversion, and verification may overlap with acquisition or processing of another disc. Do not eject a disc that lacks a verified local source needed for unfinished work.

## Coordinator ownership

Use one coordinator as the sole owner of:

- the dependency graph and worker assignments
- unique working and final output paths
- optical-drive access
- CPU, memory, storage, and process-health monitoring
- writes to `WORKFLOW.md`, `STATUS.md`, `manifest.json`, active disc logs, and shared technical logs
- completion decisions and user-facing progress

Workers must not edit shared records. They return structured results containing inputs, outputs, commands/settings, sizes, durations, streams, warnings, checks performed, exit statuses, and remaining uncertainty. The coordinator validates actual files before committing those results to records.

Reserve every output path before starting work. Never let two workers target the same file, directory, title, story join, or log. Do not give a worker authority to overwrite a verified deliverable or permanently delete an artifact.

## Useful worker boundaries

Assign workers only independent, bounded tasks such as:

- analyze one locally acquired title
- identify one title from DVD IFO or Blu-ray playlist/segment structure, visible evidence, and reliable sources
- prepare one temporary lossless source for an established episode or film
- analyze interlacing and display geometry for one title
- transcode one verified local source to an MP4 candidate for exactly one official episode or film
- fully decode and inspect one completed output
- prepare structured evidence for the coordinator
- extract or OCR one uniquely reserved subtitle cue cluster
- correct one source-language subtitle cluster against local source evidence
- translate one reviewed subtitle cluster using the coordinator-owned glossary
- independently review a subtitle cluster's language, timing, or boundary continuity

Keep dependency-sensitive work serialized. A same-episode join waits for all required pieces, verified episode identity/order, compatible streams, and normalized timestamps. Separately numbered `Part I/II/III` episodes remain separate. QuickTime UI checks may run sequentially when only one visible application session is reliable.

For subtitle work, the coordinator assigns each authored cue to exactly one cluster, provides adjacent cues only as read-only context, and serializes glossary changes, cluster assembly, cue renumbering, final remux, shared documentation, and QuickTime UI verification. Start with at most two simultaneous model-intensive subtitle workers and scale only from measured aggregate cue throughput and system capacity. Do not interrupt a healthy sequential subtitle job already in progress; use the swarm for remaining clusters or later episodes after that job completes.

## Media-process concurrency

Use agents for coordination and judgment, not as a substitute for media-process parallelism. Run independent FFmpeg jobs directly under coordinator supervision.

Start conservatively with no more than one or two simultaneous HEVC encodes unless observed system capacity supports more. Adjust using measured aggregate throughput, CPU saturation, memory pressure, thermal behavior when observable, free storage, and output growth. Reduce concurrency when:

- aggregate frames per second stops improving
- memory pressure or swapping rises
- output files stop growing unexpectedly
- the system becomes thermally constrained
- disk throughput becomes the bottleneck
- verification competes materially with active encodes

Do not interrupt a healthy process merely to rebalance concurrency. Stop a worker on a verified stall, invalid timestamps, repeated muxing errors, path collision, insufficient storage, or evidence that its premise is wrong. Preserve failed output under a clearly marked working or quarantine path and record the reason.

## Parallel multi-disc example

A safe overlap may be:

```text
Coordinator
├── Disc 2 worker: finish MP4 conversion from temporary local sources
├── Disc 2 worker: verify a different completed output
└── Disc 3 acquisition worker: exclusively read the optical drive once
```

After disc 3 acquisition completes, release the optical drive and schedule independent title workers. Do not start disc 4 without a new explicit confirmation and identity comparison.

## Progress synthesis

Report each disc separately and include system-level concurrency:

```yaml
Disc 2:
  phase:
  measured_progress:
  active_work:
  estimated_remaining:

Disc 3:
  phase:
  measured_progress:
  active_work:
  estimated_remaining:

System:
  optical_drive_owner:
  active_encodes:
  free_storage:
  constraints_or_stalls:
```

Use actual selected data size, output growth, processed duration, smoothed throughput, completed checks, and remaining dependencies. Show user-facing sizes and speeds with automatically selected decimal `B`, `KB`, `MB`, `GB`, or `TB` units; reserve exact raw bytes for technical evidence and machine-readable records. Never add worker percentages blindly; weight progress by measured work. Report 100 percent for a disc only after every required MP4 and verification for that disc is complete, except a documented single episode whose pieces span discs.

## Completion and handoff

Before declaring the parallel run complete:

1. Confirm no worker or media process remains active unintentionally.
2. Reconcile worker reports with actual files.
3. Validate manifest JSON and all final paths.
4. Verify shared records contain no conflicting or stale status.
5. Report per-disc outputs, languages, durations, checks, warnings, failed artifacts, and cross-disc dependencies.
6. Ask before the next physical disc and before any permanent quarantine deletion.
