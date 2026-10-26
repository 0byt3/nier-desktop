# Credit: Adapted from Omarchy
# Real newlines, not a literal \n: the card renders the body as it arrives, and
# elides past three lines.
nier-notification-send -u critical -g  "Learn Keybindings" \
  $'Super + K for cheatsheet.\nSuper + Space for Nier Menu.' \
  --exec nier-menu-keybindings
