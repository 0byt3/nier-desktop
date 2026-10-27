# Credit: Adapted from Omarchy
product_name="$(cat /sys/class/dmi/id/product_name 2>/dev/null)"
if [[ $product_name =~ MacBook[89],1|MacBook1[02],1|MacBookPro13,[123]|MacBookPro14,[123] ]]; then
  if modinfo applespi >/dev/null 2>&1; then
    mkdir -p /etc/dracut.conf.d
    printf '%s\n' 'add_drivers+=" applespi intel_lpss_pci spi_pxa2xx_platform "' > /etc/dracut.conf.d/nier-apple-spi.conf
  else
    echo 'This Fedora kernel has no applespi driver; install a compatible kernel before configuring the keyboard.' >&2
  fi
fi
