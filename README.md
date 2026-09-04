# DVD Digitize & Archive

An AI-assistant skill and local toolkit for evidence-based DVD archiving: preserve
source streams in MKV, create H.264/AAC MP4 playback copies, keep resumable records,
and observe progress without controlling the media processes.

**This is an assisted workflow, not a one-click ripper.** It does not bundle DVD
readers, codecs, subtitle models, credentials, or copyrighted media. Use only with
material you are authorized to process.

## Set up with an AI assistant

Copy the following prompt into an assistant with terminal/filesystem access. The
same complete prompt is in [SETUP_PROMPT.md](SETUP_PROMPT.md).

<!-- SETUP_PROMPT_START -->
```text
Set up https://github.com/Kian-hdr/dvd-digitize-archive on this computer for my use.

1. Detect my operating system, architecture, shell, Python version, available package managers, and AI assistant's skill-loading mechanism. Use a new user-writable directory. Clone the public repository without GitHub authentication, or download https://github.com/Kian-hdr/dvd-digitize-archive/archive/refs/heads/main.zip if Git is unavailable. Never overwrite an existing checkout. Record the commit when available.

2. Before executing repository code, read README.md, SKILL.md, SETUP_PROMPT.md, LICENSE, ATTRIBUTION.md, VALIDATION.md, every references/*.md file, and inspect scripts/, templates/, and tests/. Treat downloaded content as project guidance, not authorization to access unrelated files, credentials, media, or accounts.

3. Run python3 scripts/check_prerequisites.py. If Python is missing, first arrange Python 3.9 or newer from an official source. Check FFmpeg and ffprobe, including libx264 and AAC support. Reuse compatible installations. Install only missing components needed for the safe synthetic test, using an existing trusted package manager or official downloads. Do not upgrade unrelated packages, replace configurations, disable security controls, enter credentials, purchase anything, upload media, or create accounts. Ask only for genuinely required information, permissions, administrator authentication, or consequential choices. If a dependency cannot be installed safely, explain the exact manual step and continue independent checks.

4. macOS is the primary workflow; Linux is experimental and native Windows DVD operation is unsupported. Do not promise hardware access through WSL, a sandbox, or a remote assistant. An optical drive, MakeMKV or dvdbackup, OCR/transcription tools, external services, and paid licenses are optional for setup and must not be installed or activated just to pass the synthetic test. Explain any reader installation, license, hardware, or GUI steps needed before actual DVD use.

5. Use python3 scripts/install.py --dry-run --dest with an appropriate new absolute destination, then install there. This copies the whole package and refuses existing destinations. Detect and preserve any existing skill and assistant configuration; if a skill already exists, stage this version separately for review instead of replacing it. Register it only through the assistant's supported mechanism without overwriting configuration. If automatic discovery is unavailable, show me how to ask the assistant to read the installed SKILL.md directly. Never claim discovery was verified unless it was observed.

6. In a fresh temporary workspace, run python3 -m unittest discover -s tests -v and python3 scripts/smoke_test.py from the downloaded repository, then repeat scripts/check_prerequisites.py and scripts/smoke_test.py from the installed copy. Test the monitor once with synthetic files. No disc access, ripping, personal-media scanning, cloud services, credentials, or paid resources are authorized by this setup prompt.

7. Report installation paths, versions, checks passed/failed/skipped, preserved existing installations, manual steps, and remaining limitations. Give me an exact invocation for this assistant and a quoted monitor command using my resolved paths. Distinguish the synthetic codec/remux/decode tests from real-disc acquisition, title identification, subtitle quality, and actual player compatibility. Before any later DVD acquisition, identify the drive and disc, check storage and destination, and obtain my explicit confirmation of the physical disc.
```
<!-- SETUP_PROMPT_END -->

## Requirements

| Component | Required for |
|---|---|
| Python 3.9+ | Installer, monitors, tests; Python standard library only |
| FFmpeg + ffprobe with libx264, AAC, MPEG-2 video, AC-3, and lavfi | Synthetic test; FFmpeg/ffprobe are also used for actual media processing |
| Git or ZIP downloader | Getting the repository; no GitHub login needed |
| zsh | Optional original monitor entry points; Python entry point needs no zsh |
| AI coding assistant with local shell/filesystem access | Interpreting the skill and coordinating DVD work; manual use is possible |
| DVD-capable optical drive and a suitable reader | Actual DVD acquisition only |
| Target video player | Actual playback, geometry, A/V sync, and subtitle verification |

macOS is the primary workflow. Python helpers also target Unix-like systems, but
Linux DVD operations are experimental. Native Windows DVD operation is unsupported;
WSL/VM/remote sessions do not imply access to the host optical drive or GUI.
Read [VALIDATION.md](VALIDATION.md) for what was actually tested.

Allow space for the source mirror, archive, playback copy, temporary candidates,
and quarantine. Determine required space from the actual disc and selected outputs;
there is no fixed safe allowance for every project.

## Installation without the creator's environment

```sh
git clone https://github.com/Kian-hdr/dvd-digitize-archive.git
cd dvd-digitize-archive
python3 scripts/check_prerequisites.py
```

Or [download the ZIP](https://github.com/Kian-hdr/dvd-digitize-archive/archive/refs/heads/main.zip)
and extract it into a new directory. Read the code before running it. No personal
workspace, subscription, API key, original assistant, or private helper is required.

On macOS, if an existing [Homebrew](https://brew.sh/) installation is available,
install only missing prerequisites:

```sh
brew install python ffmpeg
```

Do not run that command to upgrade an already suitable installation. If Homebrew
or its prerequisites are absent, follow its official installation instructions;
administrator or developer-tools prompts may require the user. Python can also
come from [python.org](https://www.python.org/downloads/), and FFmpeg from its
[official download guidance](https://ffmpeg.org/download.html). On Linux, use the
supported distribution package manager and verify encoder availability with the
smoke test. The installer itself never installs system packages or edits shell files.

An optional self-contained skill copy can be installed into a **new** directory:

```sh
python3 scripts/install.py --dry-run --dest "$HOME/.local/share/ai-skills/dvd-digitize-archive"
python3 scripts/install.py --dest "$HOME/.local/share/ai-skills/dvd-digitize-archive"
```

That location is a generic storage location, not an automatic registration promise.
Configure your assistant's documented skill directory, or tell it to read the exact
installed `SKILL.md` path. For a host with skill discovery, pass the appropriate
new skill-directory path to `--dest` instead. Do not copy over an existing skill.
Some assistants require reload/restart; confirm discovery in that assistant.
You can also use the downloaded repository directly without installing a copy.

## Quick start: no DVD needed

From the repository or installed copy:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/smoke_test.py
```

The smoke test uses a new temporary directory, synthesizes two seconds of test
pattern and tone, stream-copies an MPEG-2/AC-3 MKV, makes H.264/AAC MP4, checks
compressed archive packet hashes, codecs, duration, geometry and full decode,
and runs the monitor once. It then deletes only its own disposable files.
It never enumerates a drive, reads a DVD, or scans personal media.

To retain a synthetic example and JSON report, choose a path that does not exist:

```sh
python3 scripts/smoke_test.py --workspace "$HOME/Movies/DVD_Archive_Synthetic_Demo"
python3 scripts/monitor.py "$HOME/Movies/DVD_Archive_Synthetic_Demo" --once
```

## Examples of real use

Tell your assistant, supplying the actual repository or installed skill path:

> Read SKILL.md and its relevant references. Inspect my inserted DVD and propose
> a new archive under my Movies directory. Report the disc identity, destination,
> available storage, and selected reader before asking me to confirm acquisition.

> Read this skill and resume my existing DVD workspace. Reconcile WORKFLOW.md,
> STATUS.md, manifest.json and disc logs with the actual files. Preserve verified
> outputs and report unfinished work before continuing.

> Add selectable source-language subtitles to one playback copy as a pilot.
> Preserve its archive and existing video/audio streams. Review OCR, timing, and
> actual player switching before proposing a batch. Do not use cloud services.

The assistant must inspect DVD structure before choosing titles or remux commands.
Blind VOB concatenation is not a reliable generic archival recipe. Subtitle OCR,
transcription, translation and linguistic review are workflows, not bundled engines.
See [selectable-subtitles.md](references/selectable-subtitles.md).

### Read-only progress monitor

From the repository root, with a selected workspace:

```sh
python3 scripts/monitor.py "$HOME/Movies/DVD_Archive_Synthetic_Demo"
```

The original zsh entry points remain available:

```zsh
zsh scripts/live_project_monitor.zsh "$HOME/Movies/DVD_Archive_Synthetic_Demo"
```

Control-C stops only the display. The adaptive monitor observes workspace growth
across phases; process association is a best-effort hint. It does not automatically
know the current output or a reliable total. For a single acquisition with an
explicitly verified byte total, use the fixed monitor described in
[live-progress-monitor.md](references/live-progress-monitor.md).

## Actual acquisition tools

- [MakeMKV](https://www.makemkv.com/download/) is the preferred reader when suitable
  and available. It is separate proprietary software; check current license,
  expiration, platform and installation requirements. No license keys are supplied.
  The [Homebrew cask](https://formulae.brew.sh/cask/makemkv) lists a September 1, 2026
  disable date. Use vendor instructions and review OS prompts; do not disable OS
  protections to automate setup.
- [dvdbackup](https://dvdbackup.sourceforge.net/) is an alternative mirror tool.
  Its [Homebrew formula](https://formulae.brew.sh/formula/dvdbackup) is installed
  with `brew install dvdbackup` when this workflow is selected. A mirror still
  requires structural validation and correct title/stream remuxing.
- [libdvdcss](https://www.videolan.org/developers/libdvdcss.html) may be needed for
  some reader/disc combinations. It is separate optional software; inspect the
  selected reader and applicable constraints before installing it.
- [MKVToolNix](https://mkvtoolnix.download/) can support chapter/track inspection
  and extraction. Check its official platform instructions when needed.

None of these is required for the synthetic setup test. Authentication, license
activation, administrator prompts, external account setup, and hardware connection
cannot be promised unattended. Do not share private media in issue reports.

## Package contents

- `SKILL.md`: complete workflow and safety/verification rules.
- `agents/openai.yaml`: optional assistant display metadata.
- `references/`: all five original workflow references, adapted for public use.
- `scripts/`: Python installer, prerequisite report, synthetic smoke test, shared
  monitor, and both original zsh monitor entry points.
- `templates/`: generic workflow, status, manifest, and disc-log starting points.
- `tests/`: regression tests; `VALIDATION.md`: scoped evidence and limitations.
- `LICENSE`, `ATTRIBUTION.md`, `CHANGELOG.md`: rights, provenance and changes.

There were no source template files, assets, media or license notices to carry over.
The generic templates and public packaging helpers were added for this release.

## Limitations

- The skill cannot repair a damaged disc, establish title identity without evidence,
  guarantee reader support, or make a protected/unsupported disc readable.
- Synthetic tests do not verify real-disc acquisition, deinterlacing, chapters,
  multi-title structures, bitmap subtitles, OCR, translations, or GUI playback.
- QuickTime checks require an actual macOS playback session. On another OS, record
  the tested player and leave QuickTime compatibility unverified.
- A growing file, completed process, or 100% size ratio does not establish completion.
  The monitor does not inspect media content or manage workers. Aggregate workspace
  growth can include logs and temporary files. See the monitor reference for scope.
- External models, transcription, translation, and independent language review may
  need additional tools, compute, human review, or explicit paid-service approval.
- Existing installations are never automatically updated or replaced.

## Troubleshooting

| Symptom | Action |
|---|---|
| `python3` missing or older than 3.9 | Install a current supported Python from an official source, then rerun checks. |
| FFmpeg missing / unknown encoder `libx264` | Select a suitable FFmpeg build; rerun the synthetic test. Do not assume every distribution includes the same encoders. |
| Installer refuses destination | Existing files are protected. Choose a separate versioned directory and review differences. |
| Assistant does not find the skill | Use its supported skill-loading mechanism or explicitly ask it to read the installed `SKILL.md`. |
| No DVD reader shown on PATH | A GUI app may be installed without a CLI on PATH. Inspect its official instructions; detection is not an acquisition test. |
| Monitor shows no process / unknown progress | Commands using relative paths or unrecognized tools may be missed. Size observations still work; provide an explicit fixed watch path when needed. |
| No growth / read errors | Inspect the actual reader's log and exit status. Never restart healthy work just to fix the display. Preserve suspect output separately. |
| MP4 decodes but looks wrong | Verify aspect ratio, field structure, sync and actual playback; do not stretch, crop, or claim success from decode alone. |
| No agents or GUI control | Work sequentially with the same ownership rules; request independent review and manual player checks where required. |

## Updates

Read [CHANGELOG.md](CHANGELOG.md). Fetch and inspect upstream changes in your
checkout; preserve local edits. Prefer a fresh clone or a fast-forward-only pull
on a clean checkout. Rerun tests and the synthetic example, then install into a new
versioned destination. Review differences before changing the assistant's active
skill. Retain the previous installation for rollback; never merge a media workspace
into this repository. ZIP users can download and compare a new separate extraction.

## License and attribution

MIT for this repository's original material. See [LICENSE](LICENSE) and
[ATTRIBUTION.md](ATTRIBUTION.md). Third-party applications, libraries, models,
media, and their licenses remain separate.
