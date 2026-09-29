# Changelog

## 1.1.0 - 2026-09-29

- Extend the public workflow to DVD, Blu-ray and UHD Blu-ray with structural
  disc snapshots, explicit MakeMKV title/backup jobs, playlist and feature gates.
- Add source-matched SDR HEVC Main/Main10 candidates, configurable MP4 audio
  languages, verified original-audio sidecars, video-only source handling,
  source/output audits, and same-episode join preflight.
- Add optional franchise watch-order and numbered playback-view guidance.
- Preserve the non-overwriting installer, read-only monitor and original DVD
  synthetic smoke test; add targeted synthetic checks for the new helpers.
- Remove local drive paths, project names, device observations and local source
  deletion permission from the public guidance. Source cleanup requires each
  user's explicit authorization and complete verification.

## 1.0.0 - 2026-09-04

- Publish the complete original skill structure with all five references and
  assistant metadata; remove creator-specific paths and host requirements.
- Preserve both monitor entry points with a shared Python, read-only backend.
  Reject paths outside the workspace, avoid following media symlinks, validate
  refresh intervals, and use conservative unknown-progress reporting. The fixed
  monitor now persists until closed rather than inferring completion from a reader.
- Add generic templates, a non-overwriting installer, a prerequisite report,
  synthetic-media smoke testing, regression tests, documentation, and MIT license.
- Add a complete setup prompt using the public repository URL.
