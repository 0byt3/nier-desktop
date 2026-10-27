# Credit: Adapted from Omarchy
if lspci | grep -iE '(VGA|Display|3D).*NVIDIA' >/dev/null; then
  source "$NIER_PATH/lib/nier-rpmfusion.sh"
  nier_rpmfusion_hardware_repo || exit $?
  nier-pkg-add akmod-nvidia xorg-x11-drv-nvidia-cuda || exit $?
  mkdir -p /etc/modprobe.d /etc/dracut.conf.d
  printf '%s\n' 'options nvidia_drm modeset=1' > /etc/modprobe.d/nier-nvidia.conf
  printf '%s\n' 'add_drivers+=" nvidia nvidia_modeset nvidia_uvm nvidia_drm "' > /etc/dracut.conf.d/nier-nvidia.conf
  echo 'NVIDIA installed. Complete RPM Fusion akmods/Secure Boot enrollment before rebooting.'
fi
