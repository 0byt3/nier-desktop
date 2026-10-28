# Credit: Adapted from Omarchy
notify_update() {
  local status=0
  # DNF uses a distinct failure status: an unavailable repository must not be
  # mistaken for either pending updates or a successfully checked system.
  nier-update-available >/dev/null || status=$?
  case ${status} in
    0) ;;
    1)
      nier-notification-dismiss "Update System" || true
      return 0
      ;;
    *) return "${status}" ;;
  esac

  nier-notification-send -u critical -g  "Update System" "Click to update the system." \
    --exec nier-launch-floating-terminal-with-presentation nier-update
}

notify_wifi() {
  nier-notification-send -u critical -g 󰖩 "Setup Wi-Fi" "Click to configure the wireless network." \
    --exec nier-shell shell toggle nier.network
}

announce_network() {
  # Ethernet is still negotiating DHCP when the session starts, so probing
  # right away calls a working machine offline. NetworkManager reports startup
  # complete once it has tried every connection it could auto-activate, which
  # is the first moment the answer means anything.
  nm-online -q -s -t 30

  # -x takes that answer as it stands rather than waiting out the timeout, so
  # a laptop with nothing to connect to gets prompted immediately.
  if ! nm-online -q -x -t 30; then
    notify_wifi
    # Nothing to update against until a link lands, so hold that prompt.
    nm-online -q -t 3600 || return
  fi

  notify_update
}

# Detached, so a slow or absent connection never holds up the rest of first run.
announce_network &
