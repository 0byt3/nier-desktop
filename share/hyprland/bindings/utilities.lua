-- Credit: Adapted from Omarchy
o.bind("SUPER + SPACE", "Nier menu", "nier-menu toggle")
o.bind("SUPER + ALT + SPACE", "Apps menu", "nier-menu toggle apps")
o.bind("SUPER + CTRL + E", "Emojis", "nier-shell shell toggle nier.emojis")
o.bind("SUPER + CTRL + C", "Capture menu", "nier-menu toggle capture")
o.bind("SUPER + CTRL + O", "Toggle menu", "nier-menu toggle toggle")
o.bind("SUPER + CTRL + H", "Hardware menu", "nier-menu toggle hardware")
o.bind("SUPER + SHIFT + code:201", "Nier menu", "nier-menu toggle root")
o.bind("SUPER + ESCAPE", "System menu", "nier-menu toggle system")
o.bind("XF86PowerOff", "Power menu", "nier-menu toggle system", { locked = true })
o.bind("SUPER + K", "Keybindings", "nier-menu-keybindings")
o.bind("SUPER + ALT + K", "Tmux keybindings", "nier-menu-tmux-keybindings")
o.bind("SUPER + CTRL + K", "Herdr keybindings", "nier-menu-herdr-keybindings")

o.bind_toggle("SUPER + SHIFT + SPACE", "Toggle top bar", "bar")
o.bind("SUPER + CTRL + SPACE", "Background switcher", "nier-menu toggle background")
o.bind("SUPER + BACKSPACE", "Toggle window transparency", "nier-hyprland-window-transparency-toggle")
o.bind("SUPER + SHIFT + BACKSPACE", "Toggle window gaps", "nier-hyprland-window-gaps-toggle")
o.bind("SUPER + CTRL + BACKSPACE", "Toggle single-window square aspect", "nier-hyprland-window-single-square-aspect-toggle")

-- xkbcommon names the comma keysym "comma"; the upper-case "COMMA" does not match.
o.bind("SUPER + comma", "Dismiss last notification", "nier-shell notifications dismissOne")
o.bind("SUPER + SHIFT + comma", "Dismiss all notifications", "nier-shell notifications dismissAll")
o.bind_toggle("SUPER + CTRL + comma", "Toggle silencing notifications", "notification-silencing")
o.bind("SUPER + ALT + comma", "Invoke last notification", "nier-shell notifications invokeLast")
o.bind("SUPER + SHIFT + ALT + comma", "Open notification history", "nier-shell notifications showHistory")

o.bind_toggle("SUPER + CTRL + I", "Toggle locking on idle", "idle")
o.bind_toggle("SUPER + CTRL + N", "Toggle nightlight", "nightlight")
o.bind("SUPER + CTRL + Delete", "Toggle laptop display", "nier-hyprland-monitor-internal toggle")
o.bind("SUPER + CTRL + ALT + Delete", "Toggle laptop display mirroring", "nier-hyprland-monitor-internal-mirror toggle")
o.bind("switch:on:Lid Switch", nil, "nier-system-lid-close", { locked = true })
o.bind("switch:off:Lid Switch", nil, "nier-hyprland-monitor-clamshell", { locked = true })

o.bind("PRINT", "Screenshot", "nier-capture-screenshot")
o.bind("ALT + PRINT", "Screenrecording", "nier-capture-screenrecording --stop-recording || nier-menu toggle trigger.capture.screenrecord")
o.bind("SUPER + ALT + code:34", "Make webcam overlay smaller", "nier-capture-webcam-resize smaller")
o.bind("SUPER + ALT + code:35", "Make webcam overlay larger", "nier-capture-webcam-resize larger")
o.bind("SUPER + PRINT", "Color picker", "pkill hyprpicker || hyprpicker -a")
o.bind("SUPER + CTRL + PRINT", "Extract text (OCR) from screenshot", "nier-capture-text")

local selection_layers = 0
local selection_binds = {}

hl.on("layer.opened", function(layer)
  if layer.namespace == "selection" then
    selection_layers = selection_layers + 1
    if selection_layers == 1 then
      selection_binds = {
        hl.bind("RETURN", hl.dsp.exec_cmd("nier-capture-region --take-window"), { description = "Capture highlighted window" }),
        hl.bind("CTRL + RETURN", hl.dsp.exec_cmd("nier-capture-region --take-fullscreen"), { description = "Capture entire screen" }),
        hl.bind("TAB", hl.dsp.exec_cmd("nier-capture-region --select-window next"), { description = "Select next window to capture" }),
        hl.bind("CTRL + TAB", hl.dsp.exec_cmd("nier-capture-region --select-window prev"), { description = "Select previous window to capture" }),
      }
      for _, direction in ipairs({ "left", "right", "up", "down" }) do
        table.insert(
          selection_binds,
          hl.bind(direction:upper(), hl.dsp.exec_cmd("nier-capture-region --select-window " .. direction), { description = "Select window to capture" })
        )
      end
    end
  end
end)

hl.on("layer.closed", function(layer)
  if layer.namespace == "selection" and selection_layers > 0 then
    selection_layers = selection_layers - 1
    if selection_layers == 0 then
      for _, keybind in ipairs(selection_binds) do
        keybind:unbind()
      end
      selection_binds = {}
    end
  end
end)

o.bind("SUPER + CTRL + S", "Share", "nier-menu toggle share")
o.bind("SUPER + CTRL + PERIOD", "Transcode", "nier-transcode")

o.bind("SUPER + CTRL + ALT + T", "Show time", "nier-notification-time")
o.bind("SUPER + CTRL + ALT + B", "Show battery remaining", "nier-notification-battery")
o.bind("SUPER + CTRL + ALT + W", "Toggle weather", "nier-notification-weather")

o.bind("SUPER + SHIFT + CTRL + A", "Agent", "nier-agent --pick")
o.bind("SUPER + CTRL + A", "Audio", "nier-shell shell toggle nier.audio")
o.bind("SUPER + CTRL + B", "Bluetooth", "nier-shell shell toggle nier.bluetooth")
o.bind("SUPER + CTRL + D", "Display", "nier-shell shell toggle nier.monitor")
o.bind("SUPER + CTRL + ALT + D", "Calendar", "nier-shell shell toggle nier.clock")
o.bind("SUPER + CTRL + W", "Network", "nier-shell shell toggle nier.network")
o.bind("SUPER + CTRL + P", "Power", "nier-shell shell toggle nier.power")
o.bind("SUPER + CTRL + T", "Activity", { tui = "btop" })

for panel = 1, 9 do
  o.bind(
    "SUPER + CTRL + code:" .. tostring(panel + 9),
    "Bar panel " .. panel,
    "nier-shell -q shell togglePanelAt right " .. panel
  )
end

o.bind("SUPER + CTRL + Z", "Zoom in", function()
  local zoom = hl.get_config("cursor.zoom_factor") or 1
  hl.config({ cursor = { zoom_factor = zoom + 1 } })
end)

o.bind("SUPER + CTRL + ALT + Z", "Reset zoom", function()
  hl.config({ cursor = { zoom_factor = 1 } })
end)

o.bind("SUPER + CTRL + L", "Lock system", "nier-system-lock")
