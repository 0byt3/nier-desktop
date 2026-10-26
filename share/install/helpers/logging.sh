# Credit: Adapted from Omarchy
nier_log_to_stdout() {
  [[ ${NIER_LOG_TO_STDOUT:-} == "1" || -z ${NIER_INSTALL_LOG_FILE:-} ]]
}

nier_log_line() {
  if nier_log_to_stdout; then
    echo "$1"
  else
    echo "$1" >>"$NIER_INSTALL_LOG_FILE"
  fi
}

start_install_log() {
  if ! nier_log_to_stdout; then
    mkdir -p "$(dirname "$NIER_INSTALL_LOG_FILE")"
    touch "$NIER_INSTALL_LOG_FILE"
    chmod 666 "$NIER_INSTALL_LOG_FILE" 2>/dev/null || true
  fi

  export NIER_START_TIME="${NIER_START_TIME:-$(date '+%Y-%m-%d %H:%M:%S')}"
  export NIER_START_EPOCH="${NIER_START_EPOCH:-$(date +%s)}"

  nier_log_line "=== Nier Setup Started: $NIER_START_TIME ==="
}

stop_install_log() {
  local end_time end_epoch duration mins secs
  end_time=$(date '+%Y-%m-%d %H:%M:%S')
  end_epoch=$(date +%s)

  nier_log_line "=== Nier Setup Completed: $end_time ==="

  if [[ -n ${NIER_START_EPOCH:-} ]]; then
    duration=$((end_epoch - NIER_START_EPOCH))
    mins=$((duration / 60))
    secs=$((duration % 60))
    nier_log_line "Nier setup: ${mins}m ${secs}s"
  fi
}

run_logged() {
  local script="$1"
  local exit_code errexit_was_set=0

  nier_log_line "[$(date '+%Y-%m-%d %H:%M:%S')] Starting: $script"

  case $- in
    *e*)
      errexit_was_set=1
      set +e
      ;;
  esac

  local runner=(bash -eE)
  if [[ ${NIER_INSTALL_DEBUG:-} == "1" ]]; then
    runner=(bash -x -eE)
  fi

  if nier_log_to_stdout; then
    PS4='+ ${BASH_SOURCE[0]##*/}:${LINENO}:${FUNCNAME[0]:-main}: ' \
      "${runner[@]}" -c 'source "$1"' bash "$script" </dev/null 2>&1
  else
    PS4='+ ${BASH_SOURCE[0]##*/}:${LINENO}:${FUNCNAME[0]:-main}: ' \
      "${runner[@]}" -c 'source "$1"' bash "$script" </dev/null >>"$NIER_INSTALL_LOG_FILE" 2>&1
  fi

  exit_code=$?
  (( errexit_was_set )) && set -e

  if (( exit_code == 0 )); then
    nier_log_line "[$(date '+%Y-%m-%d %H:%M:%S')] Completed: $script"
  else
    nier_log_line "[$(date '+%Y-%m-%d %H:%M:%S')] Failed: $script (exit code: $exit_code)"
  fi

  return $exit_code
}
