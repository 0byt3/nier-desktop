# Capture and Sharing

Read this before taking screenshots or screen recordings, extracting text from
the screen, or sharing files with other machines.

## Screenshots

```bash
nier screenshot                            # Interactive smart-region flow
nier capture screenshot region             # Select a region
nier capture screenshot windows            # Pick a window
nier capture screenshot fullscreen save    # Full screen, straight to disk (no editor)
```

The first argument picks the mode (`smart|region|windows|fullscreen`), the
second what happens with it (`slurp|copy|save`). `save` skips the annotation
editor and prints the saved path. Screenshots land in the configured Pictures
directory (override with `NIER_SCREENSHOT_DIR`).

## Screen Recording

```bash
nier screenrecord --fullscreen             # Start recording the full screen
# ...exercise whatever you want on film...
nier screenrecord --stop-recording         # Stop; prints the saved path
```

Optional flags: `--with-desktop-audio`, `--with-microphone-audio`,
`--with-webcam` (plus `--webcam-device=` and `--webcam-size=`), and
`--resolution=<size>`. Without `--fullscreen` a region picker opens first.
Recordings land in the configured Videos directory (override with
`NIER_SCREENRECORD_DIR`). Resize a live webcam overlay with
`nier capture webcam resize <smaller|larger|reset|small|medium|large>`.

If recording fails to start, rerun with `NIER_SCREENRECORD_DEBUG=true` to
collect a log at `/tmp/nier-screenrecord.log` worth attaching to a bug
report.

## Text Capture (OCR)

```bash
nier capture text    # Select a region; extracted text goes to the clipboard
```

## Sharing Files

```bash
nier share clipboard               # Share the clipboard via LocalSend
nier share file <path...>          # Share files with nearby devices
nier share folder <path>           # Share a folder

nier tailscale send <machine> <file...>    # Taildrop to a tailnet machine
nier tailscale receive [directory]         # Save incoming Taildrop files
```

Shrink large captures before sharing them:

```bash
nier transcode <input> [format] [resolution]   # Re-encode pictures/videos for sharing
```
