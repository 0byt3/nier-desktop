# shellcheck shell=bash
# Nier owns these filtered definitions; administrator RPM Fusion repos are untouched.
nier_rpmfusion_hardware_repo() {
  local pci temporary status=0
  local -a workstation_options=(rpmfusion-nonfree-steam.enabled=1)
  # Also works for manual application; the RPM requires these before %post.
  nier-pkg-add fedora-workstation-repositories dnf5-plugins || return
  pci=$(LC_ALL=C lspci -nn) || return
  if grep -qiE '(VGA|3D|Display).*\[10de:[[:xdigit:]]{4}\]' <<< "$pci"; then
    workstation_options+=(rpmfusion-nonfree-nvidia-driver.enabled=1)
  fi
  temporary=$(mktemp) || return
  if printf '%s\n' "$pci" | python3 "$NIER_PATH/lib/nier-rpmfusion.py" \
    "$NIER_PATH/default/dnf/nier-rpmfusion-hardware.repo" > "$temporary"; then
    install -Dm644 "$temporary" /etc/yum.repos.d/nier-rpmfusion-hardware.repo || status=$?
    if (( status == 0 )); then
      # DNF writes an override, preserving Fedora's packaged repository files.
      dnf config-manager setopt --create-missing-dir "${workstation_options[@]}" || status=$?
    fi
  else
    status=$?
  fi
  rm -f "$temporary"
  return "$status"
}

nier_rpmfusion_detect_hardware() {
  # Always deploy the default apps/codecs; add only the detected hardware families.
  nier_rpmfusion_hardware_repo
}
