-- Credit: Adapted from Omarchy
-- Restore workspace layouts saved by nier-hyprland-workspace-layout-toggle.

local paths = require("default.hypr.paths")
local require_all = require("default.hypr.require_all")

local layouts_dir = paths.state_home .. "/nier/workspace-layouts"

require_all.files(layouts_dir, "nier.workspace-layouts", { reload = true })
