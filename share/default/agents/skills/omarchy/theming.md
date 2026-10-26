# Themes, Backgrounds, and Fonts

Read this before changing themes, backgrounds, fonts, or theme colors.

## Theme Commands

```bash
nier theme list              # Show available themes
nier theme current           # Show current theme
nier theme set <name>        # Apply theme ("Tokyo Night" and "tokyo-night" both work)
nier theme bg next           # Cycle background
nier theme install <url>     # Install from git repo
```

## Making a New Theme

1. Create a directory under `~/.config/nier/themes`.
2. See how an existing theme is done via `/usr/local/share/nier/themes/catppuccin`.
3. Download a matching background (or several) from the internet and put them in `~/.config/nier/themes/<name-of-new-theme>/backgrounds/`.
4. When done with the theme, run `nier theme set "Name of new theme"`.

Additional user backgrounds for any theme (stock or custom) go in
`~/.config/nier/backgrounds/<theme-slug>/`.

## What a Theme Installed From a Repo May Not Contain

A theme the user wrote by hand in `~/.config/nier/themes` is unrestricted, as
are Nier's own themes. From a theme cloned by `nier theme install`, Nier
drops only what runs code: any `*.lua` (Hyprland requires a theme's
`hyprland.lua` and `gum_env.lua` at login, Neovim loads `neovim.lua` at startup),
the terminal configs `alacritty.toml`, `foot.ini`, `ghostty.conf` and
`kitty.conf` (each names the program the terminal launches), and `vscode.json`
(names a VS Code extension to install). Those are regenerated from `colors.toml`
through `$NIER_PATH/default/themed/*.tpl`, and named on stderr.

Everything else a cloned theme ships is kept, including `btop.theme`,
`chromium.theme`, `helix.toml`, `icons.theme`, `keyboard.rgb` and `shell.toml`.
Nier tells a cloned theme from the user's own by the `.git` directory a clone
leaves behind.

To change how Nier themes an app for every theme, write the template rather
than the theme: `~/.config/nier/themed/<config-name>.tpl` overrides the
built-in one. See `docs/theming.md` in the Nier repo.

## Customizing a Stock Theme

Never edit stock themes under `/usr/local/share/nier/themes/` — changes are lost
on update. Two safe options:

Both write into `~/.config/nier/themes`, where a theme the user wrote is
unrestricted — the list above applies only to a theme cloned from a repo.

**Overlay (preferred for small tweaks):** create a user theme directory with
the SAME slug containing only the files you want to change. When the theme is
applied, the stock theme is copied first and your files win on top:

```bash
mkdir -p ~/.config/nier/themes/catppuccin
cp /usr/local/share/nier/themes/catppuccin/colors.toml ~/.config/nier/themes/catppuccin/
# Edit the copied colors.toml, then re-apply:
nier theme set catppuccin
```

**Fork:** copy the whole stock theme under a new name for a fully independent
variant:

```bash
cp -r /usr/local/share/nier/themes/catppuccin ~/.config/nier/themes/catppuccin-custom
# Edit ~/.config/nier/themes/catppuccin-custom/, then:
nier theme set catppuccin-custom
```

## Fonts

```bash
nier font list               # Available fonts
nier font current            # Current font
nier font set <name>         # Change font
```
