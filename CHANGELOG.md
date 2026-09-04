# Changelog

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
