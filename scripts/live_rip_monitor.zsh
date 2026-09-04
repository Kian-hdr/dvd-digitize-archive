#!/bin/zsh
set -eu
if (( $# < 2 || $# > 5 )); then
  print -u2 'usage: live_rip_monitor.zsh WORKSPACE RIP_DIR [EXPECTED_BYTES] [RIP_LOG] [PHASE]'
  exit 64
fi
typeset -a monitor_args
monitor_args=( --watch "$2" --expected-bytes "${3:-0}" --phase "${5:-Lossless DVD mirror}" )
[[ -n ${4:-} ]] && monitor_args+=( --log "$4" )
exec python3 "${0:A:h}/monitor.py" "$1" "${monitor_args[@]}"
