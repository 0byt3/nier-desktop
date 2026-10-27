# Nier Desktop

Fedora desktop configuration and helpers built around Hyprland, UWSM, GDM, and
Quickshell. The RPM specification is maintained in the sibling `nier-copr`
repository at `packages/nier-desktop/nier-desktop.spec`.

## Deployment

The RPM installs `/usr/local/bin/nier` and `/usr/local/share/nier`. Its post-install
script runs `nier apply --system`, which installs system/session integration and,
on supported Btrfs installations, snapshot boot support.

- `nier apply`: seed missing user configuration files.
- `sudo nier apply --system`: install system/session integration.
- `sudo nier apply --system-wide`: also seed `/etc/skel` and configure the default
  GDM session for current and future users.
- `nier commands`: discover supported commands.

Existing user configs are preserved by default. The deployment command's explicit
`--force` option replaces them with backups; it is intended for deliberate
deployment, not an automatic config reset workflow.

## Desktop appearance

Applications use their own appearance settings. Nier does not ship Omarchy's
theme switching, template generation, application recoloring, or Plymouth/SDDM
themes.

Use the desktop Background menu to choose a wallpaper, or run:

```bash
nier background set ~/Pictures/wallpaper.png
nier background current
```

`nier background select` opens a file picker and prints the selected path.
The generic shell image picker defaults to `~/Pictures/Wallpapers`.

Quickshell has a built-in palette. Optional user configuration is read directly
from `~/.config/nier/colors.toml` and `~/.config/nier/shell.toml`; changes are watched
without generating configs for other applications. For example:

```toml
# ~/.config/nier/colors.toml
foreground = "#cacccc"
background = "#101315"
accent = "#88c0d0"
```

Edit Hyprland's appearance in `~/.config/hypr/looknfeel.lua` and application colors
in each application's own settings.

## Deliberately excluded features

- Browser installation helpers. Browser launching, web apps, and default-browser
  selection remain available; install browsers through the normal package tools.
- Omarchy theme management and boot/login theme customization.
- Config reset/reinstall commands and the inherited Arch package reinstall flow.
- Release channels, Pacman mirror switching, and the inherited Quattro upgrade.

Updates use DNF, Flatpak, and Mise through `nier update`. Other inherited helpers
are still being adapted to Fedora; command discovery alone does not establish
Fedora runtime compatibility.
