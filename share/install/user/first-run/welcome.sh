# Credit: Adapted from Omarchy
set -e

# Keep the invitation independent of the full setup: an unrelated failed step
# must not resend it. Existing completed installs have already seen the welcome.
if nier-done check keybindings-invitation || nier-done check first-run-user; then
  exit 0
fi

# Real newlines, not a literal backslash-n: the card renders the body as it arrives.
nier-notification-send -u normal -t 15000 -g  "Learn Keybindings" \
  $'Super + K for cheatsheet.\nSuper + Space for Nier Menu.' \
  --exec nier-menu-keybindings
nier-done mark keybindings-invitation
