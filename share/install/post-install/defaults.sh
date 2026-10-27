# Credit: Adapted from Omarchy
# Install the packaged CUPS defaults after package installation.
if [[ -f $NIER_PATH/etc-overrides/cups-cups-files.conf && -f /etc/cups/cups-files.conf ]]; then
  install -m 0640 -o root -g cups "$NIER_PATH/etc-overrides/cups-cups-files.conf" /etc/cups/cups-files.conf
fi
