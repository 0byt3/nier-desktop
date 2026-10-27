# Automation Hooks

Read this before setting up scripts that run on system events (updates, boot, low battery, etc.).

Hooks live in `~/.config/nier/hooks/<name>.d/` — one directory per event,
holding any number of independent scripts. Install with
`nier hook install <name> <script>` (copies the script in and makes it
executable). The runner also executes a flat `~/.config/nier/hooks/<name>`
file first, if one exists.

```
~/.config/nier/hooks/
├── battery-low.d/          # Low battery (percentage in $1)
├── font-set.d/             # After font change (font name in $1)
├── post-boot.d/            # After the desktop starts
└── post-update.d/          # During `nier update`, after package updates
```

Example hook script:
```bash
#!/bin/bash
echo "Package updates finished"
# Add custom actions here
```
