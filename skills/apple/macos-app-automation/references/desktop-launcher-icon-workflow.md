# macOS Desktop Launcher with Custom Icon

Use this reference when a user wants a custom-icon Desktop shortcut to an installed `.app` without altering the signed target bundle.

## Design and icon conversion

1. Generate or obtain a square PNG with no text, a strong silhouette, and high contrast at 32 px.
2. Build a multi-size iconset from the PNG:

```bash
iconset=/tmp/App.iconset
rm -rf "$iconset"
mkdir -p "$iconset"
# Create icon_16x16.png, icon_16x16@2x.png, ... icon_512x512@2x.png
# with sips from the selected square PNG.
iconutil -c icns "$iconset" -o "$HOME/Desktop/App Icon.icns"
```

Include 1x/2x sizes for 16, 32, 128, 256, and 512 px. Keep the source PNG and final `.icns` only if the user wants the design delivered separately.

## Launcher bundle

A real launcher bundle gives Finder a reliable custom icon while leaving the installed application signed and unchanged. A minimal AppleScript launcher can run:

```applescript
do shell script "/usr/bin/open -a " & quoted form of "/Applications/App.app"
```

Compile it with `osacompile`, copy the `.icns` into `Contents/Resources/`, and set these launcher-only Info.plist values:

- `CFBundleName`: app display name
- `CFBundleDisplayName`: app display name
- `CFBundleIdentifier`: distinct launcher ID, not the target app ID
- `CFBundleIconFile`: icon resource name without `.icns`

Set the Finder custom-icon flag with `SetFile -a C` when needed. Do not replace the target app’s `Contents/Resources` icon or resign it solely for shortcut cosmetics.

## Safe replacement and verification

- If an existing Desktop symlink was created by the assistant, replace only that symlink with the launcher; do not overwrite an unrelated Desktop app.
- Verify the launcher bundle and icon resource exist.
- Open the launcher and verify the target app process path/bundle ID.
- Quit the test instance and verify the target PID is gone.
- If the target app is signed, independently confirm its executable hash and deep-strict codesign before and after launcher work; the target hash must not change.

## Spotlight duplicate warning

`mdfind 'kMDItemCFBundleIdentifier == "com.example.app"'` returns indexed development builds, backups, packages on external volumes, and the installed app. To determine what is installed, inspect `/Applications` directly. Spotlight results are discovery evidence, not installation state.
