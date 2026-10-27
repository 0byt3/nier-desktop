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

Updates use DNF, Flatpak, and Mise through `nier update`. Supported maintenance
helpers use DNF/RPM and Fedora's dracut/GRUB/BLS boot integration. Command
discovery alone does not establish graphical or hardware compatibility.

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

## Fedora helper audit

The remaining executable Pacman, AUR, Limine, and mkinitcpio paths were reviewed
and retired or replaced. Original attribution and asset-provenance links remain.

| Workflow | Fedora behavior |
| --- | --- |
| System updates | `nier update system-pkgs` runs `dnf upgrade --refresh`; enabled COPRs participate normally. DNF errors propagate. |
| Update availability | DNF's status 100 means updates; repository failures report an error rather than “up to date.” |
| Unused dependencies | `nier update orphan-pkgs` queries `repoquery --unneeded`; removal requires an interactive DNF transaction review. |
| Cache cleanup | `nier update pkg-prune` runs `dnf clean packages`; it does not remove installed kernels or pretend to retain a versioned rollback cache. |
| Repository keys | `nier update keyring` updates `fedora-gpg-keys`/`fedora-repos`. COPR and vendor keys stay with DNF repository configuration; no arbitrary keyserver imports. |
| Package timestamp | `nier version pkgs` reads RPM install timestamps, including direct RPM transactions. |
| Migrations | Wait briefly on RPM's actual POSIX transaction lock. A permanent lock file alone does not block login migrations. |
| Emacs | Install Fedora's `emacs`; the former AUR package and theme installer are gone. |
| PHP / Symfony | Fedora PHP extension RPMs use `/etc/php.d`; Symfony CLI uses Mise's explicit GitHub backend. Existing PHP configuration is preserved. |
| Steam / Heroic / Lutris / RetroArch | User Flatpaks from Flathub; runtimes supply their graphics/Wine/core dependencies. RetroArch's cores are selected in its Online Updater. |
| VS Code / Zed / Spotify / Signal | User Flatpaks from Flathub; existing editor settings are preserved and no Omarchy theme adapter is installed. |
| Native 32-bit graphics | Fedora `.i686` Mesa packages; NVIDIA `.i686` libraries only when its native driver is already installed. |
| Local desktop package testing | `nier dev pkg-test` builds an RPM unprivileged with `rpm-build`, then installs it with DNF. It needs the sibling packaging spec and Fedora BuildRequires. Development releases use `999.dev.*`; `dnf distro-sync nier-desktop` returns to repository builds. |
| Hibernation | A Nier-owned Btrfs subvolume at `/swap/nier`, physical resume offset, dracut `resume`, and GRUB/BLS arguments. Removal preserves pre-existing swap and unrelated kernel settings. |
| Hardware boot configuration | Fedora dracut driver snippets and `nier kernel args`, which updates existing BLS entries and `/etc/kernel/cmdline` for future kernels. |

Flatpak app removal matches the installer's user scope and preserves app data,
game libraries and saves. System-wide installations can be managed using the
package picker or Flatpak directly. The helper adds the standard Flathub user
remote when installing an application. Sandbox behavior (especially editor
access to host development tools) follows the corresponding Flathub package.

The AUR-only package picker/updater, Pacman conflict takeover/upgrade guard,
libalpm hook, Limine assets, old Arch ISO package lists, factory-reset helper,
and deferred first-boot owner provisioner are removed. They are not Fedora
deployment paths. Install Fedora normally, then use `nier apply`; deferred ISO
provisioning flags fail with an explanation.

Hibernation setup refuses kernel lockdown, non-Btrfs roots, unowned swap paths,
and existing foreign resume settings. It does not change Secure Boot policy.
It calculates the Btrfs physical offset, rebuilds initramfs, and then installs
resume arguments. `--no-rebuild` requires a manual dracut rebuild before reboot.
Setup/removal do not reboot or hibernate automatically. Suspend/resume still
requires a separate real hardware or VM test; simulated boot-command tests
establish configuration behavior only. Do not run setup/removal during an RPM
transaction or concurrent boot configuration change.

Hardware-specific external drivers remain conditional: NVIDIA requires a
successful akmods/Secure Boot setup; matching devices enable the Nier-scoped
RPM Fusion hardware repositories during system application;
T2 Macs require a separately maintained Fedora-compatible kernel and firmware.
Out-of-tree hardware packages need a Fedora RPM/repository provider; an
inherited name is not a promise that a package exists in Fedora or the Nier
COPRs. Missing providers are reported by DNF and are never substituted with
AUR installation.

Implementation references: [DNF autoremove](https://dnf5.readthedocs.io/en/stable/commands/autoremove.8.html),
[RPM transaction locking](https://github.com/rpm-software-management/rpm/blob/master/lib/rpmlock.cc),
[Fedora kernel arguments](https://fedoraproject.org/wiki/GRUB_2),
[Btrfs swapfile offsets](https://btrfs.readthedocs.io/en/stable/btrfs-inspect-internal.html),
and the [dracut resume module](https://dracut-ng.github.io/dracut/modules/core.html).

## Optional application scope

Nier no longer supplies optional installation/removal/launch integrations for
1Password, NordVPN, Dropbox, Sunshine, ONCE, T3 Code, the inherited ChatGPT
desktop installer, OpenClaw, Hermes Desktop, or Tailscale. Their corresponding
bar widgets, services, agent choices and application-specific window rules have
also been removed. Codex CLI and the other supported Mise-backed agents remain.
LocalSend remains the file-sharing integration.

The inherited bulk preinstalled-app restoration/removal helpers and their
Omarchy-only package list (`aether`, `omacut`, `omacalc`, `omawrite`, etc.) are
removed. This does not remove the desktop's Fedora package dependencies, such
as Pinta and Xournal++, or uninstall applications/data already on a machine.

## Hardware helper options researched on 2026-10-27

These are candidates for the next hardware-support changes. Research queried
native Fedora 44 metadata and temporary command-line repository definitions;
it did not enable persistent repositories, install drivers, alter firmware or
change Secure Boot settings. Except for the already-documented Fedora ports,
the remaining hardware helpers have not yet been switched to these candidates.
TUXEDO and Motorcomm support below is implemented in the hardware apply path.

| Hardware | Verified option and remaining work |
| --- | --- |
| NVIDIA | Use RPM Fusion's [`nvidia-kmod`](https://github.com/rpmfusion/nvidia-kmod) / `akmod-nvidia` packaging and matching userspace libraries. Choose the driver branch for the GPU; validate akmods and Secure Boot signing. Nier enables its scoped RPM Fusion hardware repositories before the detected NVIDIA helper installs these packages. Legacy driver families are exposed by the scope, but automatic legacy GPU branch selection is not implemented. |
| ASUS | The [ASUS Linux Fedora guide](https://asus-linux.org/guides/fedora-guide/) now recommends Terra. A temporary Fedora 44 query found `asusctl` / `asusctl-rog-gui` 6.5.0 and `cardwire` 0.12.3. The guide deprecates supergfxd and calls Cardwire experimental; retain the existing GPU-switching helper until a replacement is tested. |
| Xbox Bluetooth | [Upstream xpadneo](https://github.com/atar-axis/xpadneo) documents Fedora builds. The [`neovi/xpadneo` COPR](https://download.copr.fedorainfracloud.org/results/neovi/xpadneo/) currently publishes Fedora 44 `xpadneo` and `akmod-xpadneo` 0.10.4. Candidate packaging needs review/signing and actual controller testing; it is not automatically enabled. |
| Broadcom BCM4360 / BCM4331 | Review RPM Fusion's [`broadcom-wl` guidance](https://github.com/rpmfusion/broadcom-wl/blob/master/fedora.readme) and [`wl-kmod`](https://github.com/rpmfusion/wl-kmod) / `akmod-wl` packaging against the exact PCI ID. The helper now enables the scoped RPM Fusion hardware repositories and installs `akmod-wl` plus `broadcom-wl` for its existing exact PCI IDs. |
| TUXEDO keyboard/backlight | The [vendor's Fedora repository](https://www.tuxedocomputers.com/en/Add-TUXEDO-software-package-sources) publishes `tuxedo-drivers` 4.25.0 and `tuxedo-control-center` 3.1.2 in its [Fedora 44 repository](https://rpm.tuxedocomputers.com/fedora/44/x86_64/base/). Some published noarch releases carry fc43 tags. Validate dependencies/kernel builds and exact supported chassis before using them on Slimbook/Clevo hardware. `nier apply --system` now adds the signed vendor repository on detected TUXEDO/Slimbook systems and installs `tuxedo-drivers` plus `tuxedo-control-center`. Existing repository settings are preserved; vendor hardware compatibility checks remain. The old compatibility bypass and unmanaged module deletion are gone. |
| Motorcomm YT6801 Ethernet | Prefer the [upstream `dwmac-motorcomm` driver](https://github.com/torvalds/linux/blob/master/drivers/net/ethernet/stmicro/stmmac/dwmac-motorcomm.c). Fedora VM107's installed 7.2.12 kernel contains it and advertises PCI alias `1f0a:6801`. The helper matches PCI ID `1f0a:6801` and checks the running kernel driver's alias. Only if native support is absent does it add the signed TUXEDO repository and install `tuxedo-yt6801`. Actual Ethernet operation still needs hardware validation. |
| Framework 16 keyboard | The exact upstream tool is [`FrameworkComputer/qmk_hid`](https://github.com/FrameworkComputer/qmk_hid), not the unrelated similarly named raw-HID utility. A small Nier RPM could package the tool plus model-scoped udev permissions. Fedora has `hidapi` and `python3-hidapi`; these are dependencies rather than substitutes for the CLI. Existing keyboard udev rules remain. QMK's [`qmk_udev`](https://github.com/qmk/qmk_udev) is another permissions helper, not a replacement for Framework's controls. |
| Intel IPU7 camera | [Intel's driver project](https://github.com/intel/ipu7-drivers) requires coordinated kernel/sensor drivers, firmware/binary processing libraries, HAL and GStreamer integration. No ready native Fedora 44 `intel-ipu7-camera` provider was found in enabled repositories. The community [`xps-fedora` project](https://github.com/onuralpszr/xps-fedora) is a possible packaging reference, but its documented current target is Fedora 45; do not mix those binaries into Fedora 44. This needs a dedicated Fedora 44 packaging/test effort. |
| Dell XPS haptic touchpad | The [maintainer's MIT-licensed package source](https://github.com/omacom/omarchy-pkgs/tree/master/pkgbuilds/dell-xps-touchpad-haptics) contains a Python daemon, CLI, udev rules and a systemd service. It is a reasonable Nier RPM candidate after checking controller IDs, permissions and service behavior; no Fedora provider was confirmed. |
| Dell Cirrus speakers | Fedora supplies [`cirrus-audio-firmware`](https://packages.fedoraproject.org/pkgs/linux-firmware/cirrus-audio-firmware/index.html), with 20261019 available in the VM's Fedora 44 updates metadata. Check the exact codec/subsystem firmware filename requested by the target DX13260 before replacing its custom firmware helper. Package availability alone does not prove that machine's amplifier firmware is included. |

### Scoped RPM Fusion repositories

`nier apply --system` first ensures `fedora-workstation-repositories` and
`dnf5-plugins` are installed. The desktop RPM also requires them, so RPM system
activation already has these packages before its post-install script runs.
Fedora's Steam repository is enabled by default through a DNF configuration
override; its NVIDIA driver repository is enabled when NVIDIA graphics are
detected. Other Fedora-provided definitions and existing administrator choices
are preserved.

Nier then adds filtered RPM Fusion Free/Nonfree release and update repositories
to extend that Fedora foundation. Steam, Discord, VLC/Freeworld
plugins, FFmpeg, GStreamer codecs, common audio/video codecs, aptX, and related
multimedia libraries are available by default. Availability does not install
these applications or replace the existing Flatpak installers.

Hardware detection extends the scope by device family:

| Detected device | Additional scope |
| --- | --- |
| NVIDIA display/3D controller | NVIDIA driver families, libraries and utilities; module build tools |
| Intel display/3D controller | Intel VA-API drivers and Mesa Freeworld acceleration |
| AMD display/3D controller | Mesa Freeworld acceleration |
| Broadcom Wi-Fi PCI IDs `14e4:43a0` / `14e4:4331` | `akmod-wl`, `kmod-wl*`, `broadcom-wl`; module build tools |
| Ricoh USB IDs represented by the `r5u87x-firmware` package | Ricoh firmware |

Hybrid graphics combine the applicable scopes. Intel network controllers do not
trigger Intel graphics packages, and an unrelated Broadcom/Ricoh device does
not trigger those drivers. The Nier-owned repo file is regenerated on application
from the default scope plus current hardware, rather than retaining previously
detected hardware indefinitely. Existing broader administrator repositories keep
their independent scope. Fedora Workstation's packaged repo files are preserved;
enablement uses DNF overrides.

`share/lib/nier-rpmfusion.py` renders the scope, using the packaged
`share/default/dnf/nier-rpmfusion-hardware.repo` as its default template. The
installed file keeps that name for continuity. Signing keys come from Fedora's
`distribution-gpg-keys`, pulled in by
`fedora-workstation-repositories`; no separate Nier key copies are needed.
Package signature checking stays enabled. The upstream sources are the
[RPM Fusion Free](https://github.com/rpmfusion/rpmfusion-free-release) and
[Nonfree](https://github.com/rpmfusion/rpmfusion-nonfree-release) release projects.

No automatic FFmpeg or Mesa replacement is performed. Full RPM Fusion FFmpeg
requires replacing Fedora's split FFmpeg packages through a reviewed DNF
transaction; Nier's RPM requires `/usr/bin/ffmpeg` so either provider satisfies
it. Mesa Vulkan Freeworld likewise requires an explicit swap from Fedora's
`mesa-vulkan-drivers`. Existing hardware helpers select the driver packages they
install. Legacy NVIDIA families are available when NVIDIA is detected, but
choosing the compatible legacy branch is not automated.
