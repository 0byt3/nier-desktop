-- Credit: Adapted from Omarchy
-- Essential application bindings.
o.bind("SUPER + RETURN", "Terminal", { nier = "terminal" })
o.bind("SUPER + SHIFT + RETURN", "Browser", { nier = "browser" })
o.bind("SUPER + SHIFT + F", "File manager", { nier = "nautilus" })
o.bind("SUPER + ALT + SHIFT + F", "File manager (cwd)", { nier = "nautilus-cwd" })
o.bind("SUPER + SHIFT + B", "Browser", { nier = "browser" })
o.bind("SUPER + SHIFT + ALT + B", "Browser (private)", { nier = "browser --private" })
o.bind("SUPER + SHIFT + N", "Editor", { nier = "editor" })

if o.preinstalled_bindings_enabled() then
  -- Bindings for preinstalled Nier applications, TUIs, and web apps.
  o.bind("SUPER + ALT + RETURN", "Tmux", { nier = "terminal-tmux" })
  o.bind("SUPER + CTRL + RETURN", "Herdr", { nier = "terminal-herdr" })
  o.bind("SUPER + SHIFT + O", "Obsidian", { launch = "flatpak run md.obsidian.Obsidian", focus = "^obsidian$" })
  o.bind("SUPER + SHIFT + SLASH", "Passwords", { launch = "bitwarden", focus = "^Bitwarden$" })
  o.bind("SUPER + SHIFT + Y", "YouTube", { webapp = "https://youtube.com/" })
end
