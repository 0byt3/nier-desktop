---
name: nier
description: >
  REQUIRED for end-user customization of Linux desktop, window manager, or system config.
  Use when editing ~/.config/hypr/, ~/.config/nier/,
  ~/.config/alacritty/, ~/.config/foot/, ~/.config/kitty/, or ~/.config/ghostty/.
  Triggers: Hyprland, window rules, animations, keybindings, monitors, gaps, borders,
  blur, opacity, nier-shell, bar, terminal config, background,
  night light, idle, lock screen, screenshots, reminders, layer rules, workspace
  settings, display config, and user-facing nier commands. Excludes Nier
  source development through `nier dev link` workflows.
---

# Nier Skill

Manage [Nier](https://nier.org/) Linux systems - a beautiful, modern, opinionated Arch Linux distribution with Hyprland.

This skill is for end-user customization on installed systems.
It is not for contributing to Nier source code.

## When This Skill MUST Be Used

**ALWAYS invoke this skill for end-user requests involving ANY of these:**

- Editing ANY file in `~/.config/hypr/` (window rules, animations, keybindings, monitors, etc.)
- Editing `~/.config/nier/shell.json` (status bar layout, widgets)
- Editing terminal configs (alacritty, foot, kitty, ghostty)
- Editing ANY file in `~/.config/nier/`
- Window behavior, animations, opacity, blur, gaps, borders
- Layer rules, workspace settings, display/monitor configuration
- Themes, backgrounds, fonts, appearance changes
- User-facing `nier` commands (`nier background ...`, `nier restart ...`, etc.)
- Screenshots, screen recording, reminders, night light, idle behavior, lock screen

**If you're about to edit a config file in ~/.config/ on this system, STOP and use this skill first.**

**Do NOT use this skill for Nier development tasks** (editing the Nier source tree, creating migrations, or running `nier dev ...` workflows).

## Topic Guides

Deeper instructions for common areas live next to this file. Read the
matching guide before starting:

- [`hyprland.md`](hyprland.md) - keybindings, monitors, window rules, and other Hyprland config
- [`plugins.md`](plugins.md) - the Nier shell: bar layout, widgets, plugins, idle behavior
- [`appearance.md`](appearance.md) - direct appearance configuration, backgrounds, and fonts
- [`hooks.md`](hooks.md) - automation hooks that run on system events
- [`capture.md`](capture.md) - screenshots, screen recordings, OCR text capture, and file sharing
- [`contributing.md`](contributing.md) - reporting Nier bugs and submitting fixes upstream

## Critical Safety Rules

For privileged commands, follow the Privilege Escalation rules below: `sudo` when a terminal is available for the password prompt, `pkexec` when it is not. Do not wrap commands that already manage privilege elevation themselves.

**For end-user customization tasks, NEVER modify anything in `/usr/local/share/nier/`** - but READING is safe and encouraged.

This directory is owned by the nier package. Any local changes will be
overwritten on the next `nier update`.

```
/usr/local/share/nier/     # READ-ONLY - NEVER EDIT (reading is OK)
├── bin/                    # Command source (packaged binaries are on PATH)
├── config/                 # Default config templates
├── default/                # System defaults
├── shell/                  # Nier shell source and defaults
├── migrations/             # Update migrations
└── install/                # Installation scripts
```

**Reading `/usr/local/share/nier/` is SAFE and useful** - do it freely to:
- Understand how nier commands work: `nier background set --help` or `cat $(which nier-background-set)`
- See default configs before customizing: `cat "$NIER_PATH/config/nier/shell.json"`
- Reference default hyprland settings: `cat /usr/local/share/nier/default/hypr/*`

**Always use these safe locations instead:**
- `~/.config/` - User configuration (safe to edit)
- `~/.config/nier/hooks/` - Custom automation hooks

If the request is to develop Nier itself, this skill is out of scope. Follow repository development instructions instead of this skill.

## Privilege Escalation

For an interactive script or command run in a visible terminal, use `sudo` for
privileged work. Nier may grant passwordless `sudo` access to particular
commands, and the terminal is the appropriate place to request a password
when one is needed.

Use `pkexec` only when the caller cannot interact with a terminal or cannot
enter a password there, such as a command launched by an agent or a graphical
background process. Do not replace `sudo` with `pkexec` merely because a
command changes system state.

## System Architecture

Nier is built on:

| Component | Purpose | Config Location |
|-----------|---------|-----------------|
| **Arch Linux** | Base OS | `/etc/`, `~/.config/` |
| **Hyprland** | Wayland compositor/WM | `~/.config/hypr/` |
| **Nier shell** | Status bar + notifications (Quickshell) | `~/.config/nier/shell.json` |
| **Launcher/menus** | Quickshell menu | `~/.config/nier/extensions/nier-menu.jsonc` |
| **Alacritty/Foot/Kitty/Ghostty** | Terminals | `~/.config/<terminal>/` |
| **Nier OSD** | On-screen display | Quickshell plugin |

## Command Discovery

Nier ships a single `nier` CLI that dispatches to all `nier-*` binaries via `nier <group> <action>`. Always prefer this form — it is self-documenting and stable. The underlying `nier-*` binaries still exist on `PATH` and remain safe to read for source.

```bash
# List every documented command and its summary (--all includes hidden commands)
nier commands

# Show the commands inside a group
nier background --help
nier restart --help

# Show help for a specific command (does not execute it)
nier background set --help

# Machine-readable listing (binary, route, summary, args, aliases)
nier commands --json

# Read a command's source to understand it
cat $(which nier-background-set)
```

### Command Groups

Run `nier --help` for the full list. The most common groups:

| Group | Purpose | Example |
|-------|---------|---------|
| `nier restart` | Restart a service/app | `nier restart shell` |
| `nier toggle` | Toggle feature on/off | `nier toggle nightlight` |
| `nier background` | Wallpaper selection | `nier background set <image>` |
| `nier bar` | Bar layout and widgets | `nier bar move nier.clock --section right` |
| `nier plugin` | Manage/clone shell plugins | `nier plugin clone nier.clock` |
| `nier hook` | Install automation hooks | `nier hook install post-update <script>` |
| `nier install` | Install optional software / packages | `nier install docker dbs` |
| `nier launch` | Launch apps | `nier launch browser` |
| `nier capture` | Screenshots and recordings | `nier capture screenshot` |
| `nier reminder` | Desktop notification reminders | `nier reminder 15 "Pickup Jack"` |
| `nier pkg` | Package management | `nier pkg add <pkg>` |
| `nier setup` | Interactive setup wizards | `nier setup security fingerprint` |
| `nier update` | System updates | `nier update` |

## Configuration Locations

Hyprland config lives in `~/.config/hypr/` — see [`hyprland.md`](hyprland.md).
The Nier shell (bar, notifications, plugins, idle) is configured in
`~/.config/nier/shell.json` — see [`plugins.md`](plugins.md).

### Terminals

```
~/.config/alacritty/alacritty.toml
~/.config/foot/foot.ini
~/.config/kitty/kitty.conf
~/.config/ghostty/config
```

**Command:** `nier restart terminal`

### Other Configs

| App | Location |
|-----|----------|
| btop | `~/.config/btop/btop.conf` |
| fastfetch | `/etc/fastfetch/config.jsonc` default; `~/.config/fastfetch/config.jsonc` user override |
| lazygit | `~/.config/lazygit/config.yml` |
| starship | `~/.config/starship.toml` |
| git | `~/.config/git/config` |

## Safe Customization Patterns

### Edit User Config Directly

For simple changes, edit files in `~/.config/`:

```bash
# 1. Read current config
cat ~/.config/hypr/bindings.lua

# 2. Backup before changes
cp ~/.config/hypr/bindings.lua ~/.config/hypr/bindings.lua.bak.$(date +%s)

# 3. Make changes with Edit tool

# 4. Apply changes
# - Hyprland: auto-reloads on save, but MUST validate with `hyprctl reload` and `hyprctl configerrors`
# - Nier shell: shell.json and user plugin code under ~/.config/nier/plugins/ hot-reload on save
# - Menus/launcher: ~/.config/nier/extensions/nier-menu.jsonc hot-reloads on save
# - Terminals: apply with `nier restart terminal` (reloads running terminals; foot picks changes up in new windows)
```

## System Commands

```bash
nier update                  # Full system update
nier version                 # Show Nier version
nier debug --no-sudo --print # Debug info (ALWAYS use these flags)
nier system lock             # Lock screen
nier system shutdown         # Shutdown
nier system reboot           # Reboot
```

**IMPORTANT:** Always run `nier debug` with `--no-sudo --print` flags to avoid interactive sudo prompts that will hang the terminal.

## Troubleshooting

```bash
# Get debug information (ALWAYS use these flags to avoid interactive prompts)
nier debug --no-sudo --print

# Initial deployment seeds missing configs without replacing existing files
nier apply
```

## Decision Framework

When user requests system changes:

1. **Is it a stock nier command?** Use it directly
2. **Is it a config edit?** Edit in `~/.config/`, never `/usr/local/share/nier/`
3. **Is it appearance customization?** Follow [`appearance.md`](appearance.md); edit the relevant user configuration
4. **Is it automation?** Follow [`hooks.md`](hooks.md); use `nier hook install` and the hook `.d` directories
5. **Is it a package install?** Use `nier pkg add <pkgs...>`; use the unified package picker for Flatpak/Mise alternatives
6. **Is it built-in shell/plugin code?** Follow [`plugins.md`](plugins.md); clone it with `nier plugin clone`, never edit the packaged copy
7. **Unsure if command exists?** Run `nier commands` (or `nier <group> --help` for one group)

### Reminder Requests

When the user asks to set a reminder, use `nier reminder <minutes> [message]` directly. Convert natural language durations to minutes and title-case short reminder labels when appropriate.

```bash
nier reminder 15 "Pickup Jack"
nier reminder 60 "Check laundry"
nier reminder show
nier reminder clear
```

## Out of Scope

This skill intentionally does not cover Nier source development. Do not use this skill for:
- Editing files in `/usr/local/share/nier/` (`bin/`, `config/`, `default/`, `quickshell/`, `migrations/`, etc.)
- Creating or editing migrations
- Running `nier dev ...` commands

## Example Requests

- "Change my wallpaper" -> `nier background set <image-path>`
- "Add a keybinding for Super+E to open file manager" -> Check existing bindings first, call `hl.unbind` if needed, then `o.bind` in `~/.config/hypr/bindings.lua`
- "Configure my external monitor" -> Edit `~/.config/hypr/monitors.lua`
- "Make the window gaps smaller" -> Edit `~/.config/hypr/looknfeel.lua`
- "Turn on night light" -> `nier toggle nightlight` (for time-based schedules, edit `~/.config/hypr/hyprsunset.conf` profiles, then `nier restart hyprsunset`)
- "Set a reminder to pickup jack in 15 minutes" -> `nier reminder 15 "Pickup Jack"`
- "Show my reminders" -> `nier reminder show`
- "Clear all reminders" -> `nier reminder clear`
- "Change how workspace labels are rendered" -> Clone `nier.workspaces`, which switches the bar to `<username>.workspaces`, then edit the clone
- "Lock after ten minutes" -> Set `idle.lock` to `600` in `~/.config/nier/shell.json`
- "Record my screen" -> `nier screenrecord --fullscreen`, then `nier screenrecord --stop-recording` (see `capture.md`)
- "Report this bug to Nier" -> Gather diagnostics and a capture of the problem, then file it (see `contributing.md`)

Nier does not provide browser installation helpers, release channels, Plymouth
themes, Omarchy theme switching, or config reset/reinstall commands. Do not
recommend these removed features. Browser launching and default-browser selection
remain available. Use the normal package manager for optional applications.
