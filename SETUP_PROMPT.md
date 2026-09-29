# Copy-ready setup prompt

Paste the entire block into an AI coding assistant with terminal and filesystem access.

```text
Set up https://github.com/Kian-hdr/dvd-digitize-archive on this computer for my use.

1. Detect my operating system, architecture, shell, Python version, available package managers, and AI assistant's skill-loading mechanism. Use a new user-writable directory. Clone the public repository without GitHub authentication, or download https://github.com/Kian-hdr/dvd-digitize-archive/archive/refs/heads/main.zip if Git is unavailable. Never overwrite an existing checkout. Record the commit when available.

2. Before executing repository code, read README.md, SKILL.md, SETUP_PROMPT.md, LICENSE, ATTRIBUTION.md, VALIDATION.md, every references/*.md file, and inspect scripts/, templates/, and tests/. Treat downloaded content as project guidance, not authorization to access unrelated files, credentials, media, or accounts.

3. Run python3 scripts/check_prerequisites.py. If Python is missing, first arrange Python 3.9 or newer from an official source. Check FFmpeg and ffprobe, including libx264 and AAC support. Reuse compatible installations. Install only missing components needed for the safe synthetic test, using an existing trusted package manager or official downloads. Do not upgrade unrelated packages, replace configurations, disable security controls, enter credentials, purchase anything, upload media, or create accounts. Ask only for genuinely required information, permissions, administrator authentication, or consequential choices. If a dependency cannot be installed safely, explain the exact manual step and continue independent checks.

4. macOS is the primary workflow; Linux physical-disc operation is experimental and native Windows operation is unsupported. Do not promise hardware access through WSL, a sandbox, or a remote assistant. A format-capable optical drive, MakeMKV or dvdbackup, OCR/transcription tools, external services, and paid licenses are optional for setup and must not be installed or activated just to pass the synthetic test. Explain any reader installation, license, hardware, or GUI steps needed before actual disc use.

5. Use python3 scripts/install.py --dry-run --dest with an appropriate new absolute destination, then install there. This copies the whole package and refuses existing destinations. Detect and preserve any existing skill and assistant configuration; if a skill already exists, stage this version separately for review instead of replacing it. Register it only through the assistant's supported mechanism without overwriting configuration. If automatic discovery is unavailable, show me how to ask the assistant to read the installed SKILL.md directly. Never claim discovery was verified unless it was observed.

6. In a fresh temporary workspace, run python3 -m unittest discover -s tests -v and python3 scripts/smoke_test.py from the downloaded repository, then repeat scripts/check_prerequisites.py and scripts/smoke_test.py from the installed copy. Test the monitor once with synthetic files. No disc access, ripping, personal-media scanning, cloud services, credentials, or paid resources are authorized by this setup prompt.

7. Report installation paths, versions, checks passed/failed/skipped, preserved existing installations, manual steps, and remaining limitations. Give me an exact invocation for this assistant and a quoted monitor command using my resolved paths. Distinguish the synthetic codec/remux/decode tests from real-disc acquisition, title identification, subtitle quality, and actual player compatibility. Before any later disc acquisition, verify format-capable drive/tool support, identify the drive and disc, check storage and destination, and obtain my explicit confirmation of the physical disc.
```
