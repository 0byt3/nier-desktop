-- Credit: Adapted from Omarchy
-- Learn how to configure Hyprland: https://wiki.hypr.land/Configuring/Start/

-- Nier's bootstrap keeps path setup out of this user config.
dofile((os.getenv("NIER_PATH") or "/usr/local/share/nier") .. "/default/hypr/bootstrap.lua")

-- Disable all Nier default bindings. Add your own in hypr/bindings.lua.
-- nier_default_bindings = false
--
-- Or disable only bindings for Nier's preinstalled apps/web apps while
-- keeping core window-manager bindings:
-- nier_preinstalled_bindings = false

-- Load Nier defaults.
require("default.hypr.nier")

-- Put your personal overrides in these files. They're loaded after Nier's
-- defaults so package updates can improve the defaults without rewriting your
-- ~/.config/hypr files.
require("hypr.monitors")
require("hypr.input")
require("hypr.bindings")
require("hypr.looknfeel")
require("hypr.autostart")

-- Toggle config flags dynamically.
require("default.hypr.toggles")

-- Add any other personal Hyprland configuration below.
-- o.window("qemu", { workspace = "5" })
