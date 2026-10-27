# Desktop Appearance

Nier does not provide Omarchy theme switching, theme templates, Plymouth themes,
or automatic application recoloring. Applications use their own settings.

Use `nier background set <image-path>` to set a wallpaper. `nier background select`
opens a file picker and prints the selected path; `nier background current` prints
the current wallpaper name. The desktop Background menu also selects and applies
an image. The generic image picker defaults to `~/Pictures/Wallpapers`.

The shell has a built-in palette. Optional user settings are read directly from
`~/.config/nier/colors.toml` (foreground, background, accent, muted, and red) and
`~/.config/nier/shell.toml` (per-surface colors, font sizes, and spacing). These
settings affect the shell; they do not generate application configs. Both files
are watched for changes. Use `nier font --help` for font commands.

Edit Hyprland appearance in `~/.config/hypr/looknfeel.lua` and terminal settings in
the terminal's own user configuration. Packaged defaults are under
`/usr/local/share/nier`; customize the user's configuration instead.
