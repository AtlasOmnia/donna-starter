# LM Studio Model Storage Operations

Use this when locating, relocating, or deleting LM Studio models to recover disk space.

## macOS default location

```text
~/.lmstudio/models
```

Installed models are normally nested by publisher and repository, for example:

```text
~/.lmstudio/models/<publisher>/<model-repository>/
```

Do not confuse Mac-local models with models installed on a remote LM Studio host. Inspect the filesystem on the machine whose storage is being managed.

## Safe deletion sequence

1. Inventory exact model directories and sizes:

 ```bash
 du -sh ~/.lmstudio/models/* ~/.lmstudio/models/*/* 2>/dev/null | sort -h
 ```

2. Check whether a model is loaded before removing its files:

 ```bash
 ~/.lmstudio/bin/lms ps
 ```

 If a target is loaded, unload it or stop its server first.

3. Delete only the explicitly named model repository directories. Never remove `~/.lmstudio`, the entire `models` directory, runtime backends, credentials, presets, or application state when the request only concerns model weights.

4. Verify every requested path is absent, then measure remaining model storage and Data-volume free space:

 ```bash
 du -sh ~/.lmstudio/models
 df -h /System/Volumes/Data
 ```

5. Report the before/after model storage and actual free-space change. macOS APFS reporting may not match a simple sum exactly, so use live `df` output rather than promising a calculated figure.

## Relocating models to external storage

- Ordinary GGUF and safetensors model files can live on external storage, but LM Studio must be pointed to or import from the new location.
- The external drive must remain mounted whenever those models are needed.
- ExFAT is adequate for static model weight files but is a poor home for active databases, Unix-permission-sensitive application state, Git repositories with symlinks, or a complete `~/.lmstudio` directory.
- For Mac-only external storage, APFS is the safer general-purpose format. Reformatting erases the drive and requires explicit user authorization.

## Common safety boundaries

- A running LM Studio application does not necessarily mean a model is loaded; check `lms ps` rather than guessing.
- Keep deletion scope path-specific and verify before and after.
- Do not delete remote-host models while cleaning the Mac unless the user explicitly requests remote cleanup.
