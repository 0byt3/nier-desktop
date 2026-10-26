# Shared Btrfs helpers. Functions take every needed value as a parameter.

nier_fstype() {
  local mountpoint=$1
  findmnt -n -o FSTYPE --target "${mountpoint}" 2>/dev/null
}

nier_is_btrfs() {
  local mountpoint=$1
  [[ $(nier_fstype "${mountpoint}") == btrfs ]]
}

nier_fsroot() {
  local mountpoint=$1
  findmnt -n -o FSROOT --target "${mountpoint}" 2>/dev/null
}

nier_btrfs_subvol_name() {
  local mountpoint=$1
  local fsroot
  fsroot=$(nier_fsroot "${mountpoint}")
  fsroot=${fsroot#/}
  printf '%s' "${fsroot}"
}

nier_var_is_separate_btrfs() {
  local root_sub var_sub
  nier_is_btrfs / || return 1
  nier_is_btrfs /var || return 1
  root_sub=$(nier_fsroot /)
  var_sub=$(nier_fsroot /var)
  [[ -n ${var_sub} && ${var_sub} != "${root_sub}" ]]
}

nier_snapper_configs_file() {
  if [[ -d /etc/sysconfig ]]; then
    printf '%s' /etc/sysconfig/snapper
    return
  fi
  printf '%s' /etc/conf.d/snapper
}

nier_warn_not_btrfs() {
  local action=$1
  printf '%s\n' "Warning: / is not Btrfs; ${action} skipped." >&2
}
