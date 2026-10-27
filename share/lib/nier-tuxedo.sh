# Fedora repository definition follows https://rpm.tuxedocomputers.com/fedora/tuxedo.repo.
# Source this library from hardware setup; it does nothing on its own.
nier_tuxedo_install() {
  if [[ $(uname -m) != x86_64 ]]; then
    echo 'TUXEDO Fedora packages are available only for x86_64.' >&2
    return 1
  fi
  # Keep existing administrator repository settings and signing policy intact.
  if [[ ! -e /etc/yum.repos.d/tuxedo.repo ]]; then
    install -Dm644 "$NIER_PATH/default/dnf/tuxedo.repo" /etc/yum.repos.d/tuxedo.repo || return
  fi
  dnf --enablerepo=tuxedo install -y -- "$@"
}

nier_tuxedo_backlight() {
  local vendor
  vendor=$(cat "${1:-/sys/class/dmi/id/sys_vendor}" 2>/dev/null) || return 0
  case "${vendor,,}" in
    *tuxedo*|*slimbook*) nier_tuxedo_install tuxedo-drivers tuxedo-control-center ;;
  esac
}

nier_tuxedo_ethernet() {
  local device vendor device_id
  for device in "${1:-/sys/bus/pci/devices}"/*; do
    [[ -r $device/vendor && -r $device/device ]] || continue
    read -r vendor < "$device/vendor"
    read -r device_id < "$device/device"
    [[ $vendor == 0x1f0a && $device_id == 0x6801 ]] || continue
    # Test the running kernel's actual PCI support, not a human-readable lspci label.
    if modinfo -F alias dwmac-motorcomm 2>/dev/null | grep -qi 'pci:v00001F0Ad00006801'; then
      echo 'Motorcomm YT6801: using the native dwmac-motorcomm kernel driver.'
      return 0
    fi
    nier_tuxedo_install tuxedo-yt6801 || return
    return 0
  done
}
