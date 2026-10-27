# Nier Desktop

Fedora desktop configuration and helpers built around Hyprland, UWSM, greetd, and
Quickshell. The RPM specification is maintained in the sibling `nier-copr`
repository at `packages/nier-desktop/nier-desktop.spec`.

## Deployment

The RPM installs `/usr/local/bin/nier` and `/usr/local/share/nier`. Its post-install
script runs `nier apply --system`, which installs system/session integration and,
on supported Btrfs installations, snapshot boot support.

- `nier apply`: seed missing user configuration files.
- `sudo nier apply --system`: install system/session integration.
- `sudo nier apply --system-wide`: also seed `/etc/skel` and configure the default
  Nier defaults for current and future users.
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

Quickshell ships static defaults matching the reference Omarchy machine: the
Catppuccin Mocha palette, compact monospace type, and blue focus outlines.
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

## Login manager

`nier apply --system` installs and enables greetd with Nier's Quickshell greeter,
using Cage as its small Wayland compositor. This replaces GDM/SDDM as the next
boot's login manager; applying or updating the RPM does not terminate an existing
graphical session. Existing GNOME packages are not automatically removed.

The greeter launches only the Nier Hyprland/UWSM session. Authentication uses
Fedora's greetd PAM configuration and Quickshell's greetd integration, including
multiple prompts and cancellation. Passwords are never logged or persisted.
Local desktop usernames are discovered from NSS; other usernames can be entered
manually. Restart and shutdown require confirmation.

Root can customize the login screen's static colors, font, and radius in
`/etc/nier/greeter.json`. Initial activation seeds that file from
`share/greeter/style.json` and preserves an existing file on later runs. The
root-owned greetd config at `/etc/greetd/config.toml` is managed by Nier; changed
configs are backed up before replacement. The greeter never reads user home
configuration or imports the desktop's plugins before authentication.

An optional `display` object in `/etc/nier/greeter.json` selects a monitor mode
inside Cage using `wlr-randr`. For example:

```json
"display": {"name": "Virtual-1", "mode": "2560x1440", "scale": 1}
```

Without it, the compositor selects the preferred display mode. Invalid or
unavailable modes fall back to the compositor default so the UI still starts.

The packaged session launcher is `share/bin/nier-session`. System and user
appearance defaults are plain config files, independent of the removed Omarchy
theme system. The greeter uses Nier branding and the reference machine's style;
it does not copy the reference machine's employer-branded wallpaper.

Validation:

```bash
node tests/test_greeter_auth.js
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
NIER_PATH="$PWD/share" bash bin/nier commands --check
```

The update logger uses Fedora's `util-linux-script` package (`/usr/bin/script`),
which is a separate RPM from `util-linux`. Floating command windows preserve the
command's exit status and display failures instead of an unconditional success.

Dictation setup installs Fedora's `voxtype` and `wtype` packages and preserves an
existing Voxtype user config. It downloads the selected model, installs
`vulkan-tools`, and tests hardware Vulkan inference using generated audio and
that model before enabling acceleration. No microphone recording is needed.
Software Vulkan drivers, missing drivers, crashes, timeouts, and silent CPU
fallback select the best working CPU variant (AVX-512, AVX2, or baseline).
Selection is saved in the user's `voxtype.service.d/20-nier-backend.conf`;
the packaged launcher is preserved. Rerun dictation setup after changing GPU
drivers or hardware. Diagnostics are in `~/.local/state/nier/voxtype-vulkan.log`
(or under `$XDG_STATE_HOME`). Other transcription engines and remote Whisper
configurations retain their existing backend selection.
VM testing needs a forwarded microphone (SPICE audio in Proxmox).
