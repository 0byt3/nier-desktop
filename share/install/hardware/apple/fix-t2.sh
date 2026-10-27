# Credit: Adapted from Omarchy
if lspci -nn | grep '106b:180[12]' >/dev/null; then
  echo 'T2 Macs require a separately maintained Fedora-compatible kernel and firmware.' >&2
  echo 'Nier does not install an Arch kernel or change disk-unlock configuration.' >&2
fi
