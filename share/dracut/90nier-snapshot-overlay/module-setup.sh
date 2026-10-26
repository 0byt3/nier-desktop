#!/usr/bin/bash

# called by dracut
check() {
  return 0
}

# called by dracut
depends() {
  echo btrfs
  return 0
}

# called by dracut
installkernel() {
  instmods overlay btrfs
}

# called by dracut
install() {
  inst_multiple -o findmnt mount umount mkdir mktemp grep sed awk btrfs
  inst_hook pre-pivot 90 "${moddir}/nier-snapshot-pre-pivot.sh"
}
