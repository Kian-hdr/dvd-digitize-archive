#!/bin/zsh
set -eu
if (( $# != 1 )); then
  print -u2 'usage: live_project_monitor.zsh WORKSPACE'
  exit 64
fi
exec python3 "${0:A:h}/monitor.py" "$1"
