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

## Automated checks

[GitHub Actions](https://github.com/Kian-hdr/dvd-digitize-archive/actions/workflows/validate.yml)
runs the prerequisite check, 30 regression tests and synthetic media smoke test on
macOS and Ubuntu with Python 3.9. Consult the actual run result before treating
another operating system as tested. CI does not access an optical drive or GUI.

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
