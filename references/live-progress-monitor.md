# Live terminal progress monitor

Read this whenever selecting a DVD workspace. Use one visible read-only monitor
across phase changes. If the assistant has a visible task terminal, use it;
otherwise use the current shell or give the resolved command to the user. Do not
open a separate terminal app without a request. Never interrupt healthy media
work to start, attach, repair, or stop a monitor.

The public scripts require Python 3.9+. Both original zsh entry-point names remain
available; direct Python invocation avoids needing zsh. Resolve `skill_root` from
the actual installed `SKILL.md` location. The commands below are examples to adapt;
in live chat, provide fully resolved and safely quoted paths.

## Persistent workspace monitor

From the repository or installed skill directory:

```sh
skill_root="$PWD"
workspace="$HOME/Movies/DVD_Archive_Synthetic_Demo"
python3 "$skill_root/scripts/monitor.py" "$workspace"
```

Or:

```zsh
zsh "$skill_root/scripts/live_project_monitor.zsh" "$workspace"
```

It observes aggregate workspace size and regular-file count, recent growth speed,
free space, and best-effort process association. It never starts, signals, or stops
a media process, never reads an optical device, never reads media contents, and
never writes inside the workspace. Stopping it stops only the display. Restart it
after the assistant, terminal or operating system restarts.

Directory symlinks are not traversed; file symlinks are not measured. Files changing
while measured may give a partial sample. Aggregate size includes logs, working
copies and quarantine, so it is not a media byte count or completion denominator.
A large directory tree can take longer to scan than the refresh interval. This
implementation is intended for local filesystems and a single archive workspace.

Process detection uses `ps` metadata and known executable names plus the selected
absolute workspace path. Relative paths, wrappers and arguments with unusual
formatting may not be recognized. Only process IDs and executable names are shown,
not complete command lines. No discovered process is treated as proof of drive
ownership or completion. Check actual readers separately before accessing a drive.

Automatic physical-disc-size estimation was removed: disc capacity is not a reliable
size for every selected-title extraction, and process strings cannot safely identify
all output paths. The default display therefore reports an unknown denominator and
no ETA. It does not infer a title, disc number, or processing phase.

## One fixed acquisition

Only when the user wants a single acquisition view, select a dedicated rip directory
and log inside the workspace. `EXPECTED_BYTES` must describe exactly that directory's
expected acquisition data. Do not use whole-disc capacity for a selected-title rip
or a directory that already contains other outputs. Supply zero for an unknown total.

```zsh
skill_root="$PWD"
workspace="$HOME/Movies/Example_DVD_Archive"
rip_dir="$workspace/.work/DVD_01"
rip_log="$workspace/Logs/DVD_01_rip.log"
zsh "$skill_root/scripts/live_rip_monitor.zsh" \
  "$workspace" "$rip_dir" 0 "$rip_log" "DVD 1 lossless mirror"
```

The fixed monitor rejects paths resolving outside the workspace. It summarizes
recognized read-error terms in the last 64 KB of the specified log, not the entire
log. A size ratio is labelled as a user-supplied acquisition ratio, not completion;
it may exceed 100% if the premise is wrong. Both monitors persist until closed.
They cannot verify reader exit status, successful acquisition, or correct structure.

## Display and safe test controls

Use English phase names and operational text. Sizes and throughput use decimal
`B`, `KB`, `MB`, `GB`, `TB`. Raw bytes are accepted only as a technical denominator.
The display refreshes about every two seconds plus scan time. A no-growth warning
after 60 seconds is advisory; some legitimate phases do not grow files continuously.

```sh
python3 scripts/monitor.py "$workspace" --once
python3 scripts/monitor.py "$workspace" --interval 5
```

`DVD_MONITOR_ONCE=1` also selects a single sample for either zsh entry point.
`DVD_MONITOR_INTERVAL` accepts 0.1 through 3600 seconds; invalid values fail with a
clear argument error. Non-interactive output contains no terminal clearing codes.

## Evidence and chat reporting

The monitor does not replace progress updates. Provide the exact resolved adaptive
command at task start. Report phase changes, read errors, material stalls, and
about every five minutes during sustained work. Use percentages only when another
reliable phase-specific source provides them; never invent project completion.

Completion still requires real process exit status, complete local reading,
structural checks, IFO/BUP comparison and reproducible disc identity where applicable,
stream/container verification, and the required actual player checks. Do not eject
or ask for the next disc based solely on this monitor.
