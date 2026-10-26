# Credit: Adapted from Omarchy
# Upgrades must not delete the version a running process is executing from:
# mise up would prune the old install dir out from under a live session.
mise settings set upgrade.auto_prune false

nier-mise-install codex
nier-mise-install gh
nier-mise-install npm:playwright playwright
nier-cmd-missing cursor-agent && nier-mise-install cursor-agent
nier-mise-install npm:@kitlangton/ghui ghui
nier-mise-install aqua:modem-dev/hunk hunk
nier-mise-install aqua:bitwarden/clients bw
nier-mise-install aqua:herdrdev/herdr herdr
nier-mise-install aqua:jdx/usage usage
