# Credit: Adapted from Omarchy
# Display fix for ASUS ExpertBook B9406 (Panther Lake / Xe3 iGPU).
#
# Panel Replay is Xe3-new, default-on in the xe driver, and has a broken
# exit/wake path on this eDP panel: the panel latches the last-presented
# frame in self-refresh and never wakes for subsequent atomic commits, so
# the screen only updates on a full modeset (e.g. a VT switch). The older
# xe.enable_psr=0 knob does not cover Panel Replay.

if nier-hw-asus-expertbook-b9406; then
  nier-kernel-args add xe.enable_panel_replay=0
fi
