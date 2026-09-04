# Validation

## Local release validation: 2026-09-04

Environment: macOS 26.6.2 (Darwin 25.6.0), Apple Silicon, Python 3.9.6,
FFmpeg/ffprobe 9.0.1, zsh. The original installed skill's nine file hashes were
compared before and after packaging and remained unchanged.

Passed:

- All 30 standard-library regression tests, including non-overwriting installation,
  dry run, installed-copy execution, incomplete-package rejection, paths containing
  spaces, traversal/symlink boundaries, unknown-progress reporting, both zsh entry
  points, and an existing disposable process remaining alive during observation.
- A fresh temporary source-copy rehearsal of the setup prompt's executable steps:
  prerequisite check, tests, synthetic smoke test, dry-run installation, actual
  installation into a separate new directory, installed-copy prerequisites,
  installed-copy smoke test and tests, and refusal to overwrite that installation.
- Two seconds of generated test pattern and tone: MPEG-2/AC-3 source, stream-copy
  MKV with matching compressed packet hashes, and H.264/AAC MP4 at CRF 18 / medium.
  Both outputs passed codec, stream count, duration, 320x240 geometry, yuv420p,
  25 fps, square pixels, and full video/audio decode checks.
- A single read-only monitor sample in each synthetic media test. Default temporary
  fixtures were removed by the test; no personal media was examined.
- Python compilation, zsh syntax, matching complete README/setup prompt text, all
  relative Markdown links, original package inventory, and a targeted privacy scan
  of every public text file. No source media or private project records are shipped.

The rehearsal ran the prompt's steps with existing prerequisites on the maintainer's
Mac in isolated temporary directories. It did not simulate an unauthenticated user
installing Python/Homebrew from scratch or prove another assistant's discovery UI.
System dependencies and the existing global skill/configuration were preserved.

## Public distribution and setup rehearsal

The repository page and main-branch ZIP returned HTTP 200 without authentication.
ZIP CRC validation passed and all 26 packaged file contents matched commit
`26963b56144bdf2db8c27547e2a200e933405866`.

A fresh HTTPS clone with Git credential helpers disabled succeeded. From that
public clone, the setup prompt's prerequisite checks, 30 tests, synthetic smoke
example, dry-run install and actual new-directory install all passed. The
installed copy passed its prerequisite check, smoke example and 30 tests; a repeat
installation was refused without changing the existing skill. The anonymously
downloaded ZIP also passed prerequisite and synthetic-media checks after extraction.
All of this used temporary directories, which were removed after validation.

This is an executed rehearsal of the prompt's local commands, not a claim that an
arbitrary AI assistant followed the prompt autonomously or that assistant discovery
was verified. Public download checks are point-in-time evidence.

## Automated checks

[GitHub Actions](https://github.com/Kian-hdr/dvd-digitize-archive/actions/workflows/validate.yml)
runs the prerequisite check, 30 regression tests and synthetic media smoke test on
macOS and Ubuntu with Python 3.9. [Release run 33918738918](https://github.com/Kian-hdr/dvd-digitize-archive/actions/runs/33918738918)
passed both jobs at commit `26963b56144bdf2db8c27547e2a200e933405866`:

| Runner | Python | FFmpeg | Result |
|---|---|---|---|
| macOS, Darwin 25.5.0, arm64 | 3.9.13 | 8.1.2 | 30 tests and synthetic media smoke passed |
| Ubuntu, Linux x86_64 | 3.9.25 | 6.1.1 | 30 tests and synthetic media smoke passed |

The helper/toolchain tests are verified on both CI hosts; Linux physical-DVD work
remains experimental. CI does not access an optical drive or GUI. Later changes to
this validation record do not alter the tested scripts or workflow.

## Not verified by these tests

- Real DVD reading, encrypted/damaged discs, drive access or MakeMKV activation.
- Disc-ID reproduction, IFO/PGC interpretation, chapter preservation or correct
  selection/order of DVD titles; the synthetic fixture has no DVD structure.
- Deinterlacing, mixed-format joins, bitmap subtitle preservation, OCR,
  transcription, translation quality or independent linguistic review.
- QuickTime or television playback, A/V synchronization as perceived by a person,
  selectable subtitle switching/off, Windows/WSL drive access, or GUI discovery.
- Unattended installation of system prerequisites or tools requiring administrator
  access, authentication, licenses, paid compute or external accounts.

The smoke test establishes a limited local media toolchain, not DVD readiness or
end-to-end archive correctness. Required real-media verification gates remain in
SKILL.md and the references.
