#!/bin/sh
# Overlay a read-only Snapper root snapshot and, when requested, mount a
# matching /var snapshot so both volumes boot together.

if ! command -v getarg >/dev/null 2>&1 && [ -f /lib/dracut-lib.sh ]; then
  . /lib/dracut-lib.sh
fi
if ! command -v warn >/dev/null 2>&1; then
  warn() {
    echo "$@" >&2
  }
fi

NEWROOT=${NEWROOT:-/sysroot}

nier_is_snapshot_path() {
  local path=$1
  case "${path}" in
    */.snapshots/*/snapshot | */.snapshots/*/snapshot/)
      return 0
      ;;
  esac
  return 1
}

nier_subvol_from_rootflags() {
  local flags=$1
  local part
  local IFS=,
  for part in ${flags}; do
    case "${part}" in
      subvol=*)
        printf '%s' "${part#subvol=}"
        return 0
        ;;
    esac
  done
  return 1
}

nier_is_ro_btrfs() {
  local mnt=$1
  local prop
  [ -d "${mnt}" ] || return 1
  prop=$(btrfs property get "${mnt}" ro 2>/dev/null) || return 1
  case "${prop}" in
    *ro=true*)
      return 0
      ;;
  esac
  return 1
}

nier_overlay() {
  local mnt=$1
  local tag=$2
  local fstype
  local lower
  local ram

  fstype=$(findmnt -n -o FSTYPE "${mnt}" 2>/dev/null) || return 1
  [ "${fstype}" = btrfs ] || return 1
  nier_is_ro_btrfs "${mnt}" || return 0

  command -v modprobe >/dev/null 2>&1 && modprobe overlay 2>/dev/null || true

  lower=$(mktemp -d -p /run "nier-${tag}-lower.XXXXXX") || return 1
  ram=$(mktemp -d -p /run "nier-${tag}-ram.XXXXXX") || return 1
  # systemd initramfs marks /sysroot shared; mount --move refuses that.
  mount --make-rprivate / 2>/dev/null || true
  mount --make-private "${mnt}" 2>/dev/null || true
  if ! mount --move "${mnt}" "${lower}"; then
    rmdir "${lower}" "${ram}" 2>/dev/null || true
    return 1
  fi
  if ! mount -t tmpfs -o mode=755 "nier-${tag}" "${ram}"; then
    mount --move "${lower}" "${mnt}" || true
    rmdir "${ram}" 2>/dev/null || true
    return 1
  fi
  mkdir -p "${ram}/upper" "${ram}/work"
  if ! mount -t overlay "nier-${tag}" \
    -o "lowerdir=${lower},upperdir=${ram}/upper,workdir=${ram}/work" \
    "${mnt}"; then
    umount "${ram}" 2>/dev/null || true
    mount --move "${lower}" "${mnt}" || true
    return 1
  fi
  return 0
}

nier_comment_fstab_mp() {
  local fstab=$1
  local mp=$2
  local tmp
  local src dest opts dump pass rest

  [ -f "${fstab}" ] || return 0
  tmp="${fstab}.nier-new"
  : >"${tmp}"
  while read -r src dest opts dump pass rest || [ -n "${src}" ]; do
    case "${src}" in
      '' | \#*)
        printf '%s\n' "${src}${dest:+ ${dest}}${opts:+ ${opts}}${dump:+ ${dump}}${pass:+ ${pass}}${rest:+ ${rest}}" >>"${tmp}"
        continue
        ;;
    esac
    if [ "${dest}" = "${mp}" ]; then
      printf '# nier-snapshot-overlay: %s %s %s %s %s %s\n' \
        "${src}" "${dest}" "${opts}" "${dump}" "${pass}" "${rest}" >>"${tmp}"
      continue
    fi
    printf '%s\n' "${src} ${dest} ${opts} ${dump} ${pass}${rest:+ ${rest}}" >>"${tmp}"
  done <"${fstab}"
  mv "${tmp}" "${fstab}"
}

nier_maybe_overlay_root() {
  local fsroot
  local flags
  local subvol

  fsroot=$(findmnt -n -o FSROOT "${NEWROOT}" 2>/dev/null)
  flags=$(getarg rootflags)
  subvol=$(nier_subvol_from_rootflags "${flags}")

  if nier_is_snapshot_path "${fsroot}" || nier_is_snapshot_path "${subvol}"; then
    if nier_overlay "${NEWROOT}" root; then
      nier_comment_fstab_mp "${NEWROOT}/etc/fstab" /
    else
      warn "nier-snapshot-overlay: could not overlay read-only /"
    fi
  fi
}

nier_btrfs_dev() {
  local src

  src=$(getarg root)
  case "${src}" in
    UUID=*)
      printf '%s' "/dev/disk/by-uuid/${src#UUID=}"
      return 0
      ;;
    LABEL=*)
      printf '%s' "/dev/disk/by-label/${src#LABEL=}"
      return 0
      ;;
    /dev/*)
      printf '%s' "${src}"
      return 0
      ;;
  esac

  src=$(findmnt -n -o SOURCE "${NEWROOT}" 2>/dev/null)
  case "${src}" in
    /dev/*)
      printf '%s' "${src}"
      return 0
      ;;
  esac
  return 1
}

nier_maybe_mount_var() {
  local varsubvol
  local root_src
  local fstype

  varsubvol=$(getarg nier.varsubvol)
  [ -n "${varsubvol}" ] || return 0

  # After the root overlay, findmnt SOURCE is "nier-root", not a block device.
  root_src=$(nier_btrfs_dev) || return 0
  [ -n "${root_src}" ] || return 0

  mkdir -p "${NEWROOT}/var"
  if findmnt "${NEWROOT}/var" >/dev/null 2>&1; then
    umount "${NEWROOT}/var" 2>/dev/null || true
  fi
  if ! mount -t btrfs -o "subvol=${varsubvol}" "${root_src}" "${NEWROOT}/var"; then
    warn "nier-snapshot-overlay: could not mount /var snapshot ${varsubvol}"
    return 0
  fi
  fstype=$(findmnt -n -o FSTYPE "${NEWROOT}/var" 2>/dev/null)
  [ "${fstype}" = btrfs ] || return 0
  nier_overlay "${NEWROOT}/var" var || \
    warn "nier-snapshot-overlay: could not overlay read-only /var"
  nier_comment_fstab_mp "${NEWROOT}/etc/fstab" /var
}

nier_maybe_overlay_root
nier_maybe_mount_var

exit 0
