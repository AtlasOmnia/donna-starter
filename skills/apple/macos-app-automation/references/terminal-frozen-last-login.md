# Terminal.app frozen new-window / stuck "Last login" recovery

When this pattern appears:
- the user opens a fresh Terminal window.
- The window shows `Last login: ...` and then appears frozen.
- `ps` shows `Terminal -> login -pf user -> -zsh` for the new TTY, but the shell does not look interactive.

## Verified indicators

1. Direct zsh startup can still be healthy in a clean PTY, so the issue may be specific to the live Terminal TTY state rather than general shell startup.
2. The affected TTY may show broken line discipline via:
 - `stty -a < /dev/ttysNNN`
 - Look for flags such as `-echo` or `-icanon` on the stuck Terminal TTY.
3. The active Hermes/TUI Terminal may intentionally have different TTY flags; do not "normalize" the Hermes TTY blindly.

## Recovery sequence

1. Identify the stuck Terminal-backed TTY with `ps`.
2. Inspect it:
 - `stty -a < /dev/ttysNNN`
3. Recover the current stuck window:
 - `stty sane < /dev/ttysNNN`
4. If needed, send a harmless newline/command to wake the prompt:
 - `printf 'reset\n' > /dev/ttysNNN`
5. Prevent recurrence by adding this guarded block near the top of `~/.zshrc`:

```zsh
if [[ -t 0 ]]; then
 case "$(stty -a 2>/dev/null)" in
 *"-echo"*|*"-icanon"*) stty sane 2>/dev/null ;;
 esac
fi
```

6. If the banner itself is undesirable, create `~/.hushlogin`.
 - This suppresses `Last login...` output.
 - It is cosmetic and should be treated as separate from the TTY repair.

## Why this belongs in app automation

This issue presents as a Terminal.app freeze, but the practical fix spans:
- shell-side TTY inspection and repair,
- GUI/window discrimination so Hermes does not kill the active TUI session,
- and a durable per-user startup guard.

## Pitfall

Do not conclude "Terminal is frozen" from the banner alone.
Verify whether the shell exists on the TTY first; if it does, the problem may be inherited terminal mode rather than a crashed shell or bad zsh config.
