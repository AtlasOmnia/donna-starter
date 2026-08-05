# TUI model-picker slash commands

Use this reference when a user asks for a slash command that opens an interactive model picker in the terminal, especially over SSH.

## Surface decision

Treat these words as hard routing signals: **TUI**, **terminal**, **SSH**, **Windows over SSH**, **prompt_toolkit**. The implementation must run inside the classic Hermes CLI on the host reached by SSH. Hermes Desktop plugins are a different renderer and are not a substitute.

Backend plugin commands are also insufficient for opening TUI UI: `ctx.register_command()` handlers resolve to text output. They can populate command inventories, but they cannot open a prompt_toolkit modal.

## Alias choices

Hermes has two alias surfaces:

1. `CommandDef.aliases` in `hermes_cli/commands.py` — central, discoverable by help/autocomplete, and preserves the originally typed command when `process_command()` dispatches the canonical handler.
2. `quick_commands.<name>: {type: alias, target: /model}` in profile config — update-safe and useful when exact `/model` behavior is enough.

A quick alias to bare `/model` is **not** enough when the user asks for an explicit Session/Global choice. It rewrites the command to `/model`, losing the alias identity, and the standard picker applies `model.persist_switch_by_default` when selection completes.

For an explicit-scope command, add a central alias such as `switch` to the `model` command and let `_handle_model_switch(cmd_original)` detect `/switch` from the original first token.

## Picker state machine

Keep one model picker and add an optional scope stage rather than cloning provider/model logic.

Recommended state fields:

```python
{
 "stage": "scope", # scope -> provider -> model
 "choose_scope": True,
 "persist_global": None, # False=session, True=global
 "default_provider_index": 0,
 "providers": providers,
 "selected": 0,
}
```

Flow:

1. Bare `/switch` opens at `scope`.
2. **Session** sets `persist_global=False`, then advances to provider.
3. **Global** sets `persist_global=True`, then advances to provider.
4. Provider and model remain dropdown/list stages using the live `/model` inventory.
5. Back from provider returns to scope; Escape/Cancel closes without changing anything.
6. Final model selection reads the scope stored in picker state. Do not recompute persistence from `model.persist_switch_by_default` after the user made an explicit choice.
7. The final `switch_model(..., is_global=<explicit scope>)` and apply/confirmation path must receive the same boolean.

Ordinary bare `/model` should retain its existing behavior and begin at provider selection. Explicit `/switch --session` or `/switch --global` may skip the scope stage because the scope is already stated.

## Rendering and navigation

The scope panel should explain consequences, not merely show two labels:

- `Session — change only this running session`
- `Global — update the profile default for future sessions`
- `Cancel`

Update arrow-key bounds for every stage:

- Scope: 3 rows.
- Provider: provider rows plus Back and Cancel when scope selection is enabled.
- Model: model rows plus Back and Cancel.

Use the existing prompt_toolkit picker widget and live provider inventory. Do not build a second static model catalog.

## Tests

Start with failing tests for:

- `resolve_command("switch").name == "model"`.
- `/switch` opening the picker with `choose_scope=True` and `persist_global=None`.
- Session advancing to provider with `persist_global=False`.
- Global advancing to provider with `persist_global=True`.
- Final selection using picker-state scope even if the caller passes the opposite default.
- Existing `/model` behavior remaining unchanged.
- Back/Cancel and arrow bounds for scope/provider/model stages.

Run the focused picker tests plus command-registry and quick-command regression suites. Include the async pytest plugin when those suites contain `@pytest.mark.asyncio`; a missing test dependency is setup state, not a product failure.

## Runtime verification

- Start a **fresh** Hermes CLI process after source changes; an already-running process has the old command registry and method definitions loaded.
- Type `/switch` and require a visible `Model Switch — Select Scope` panel with Session and Global choices.
- Cancel before changing a model when verification is not authorized to mutate routing.
- For automated interactive verification, prefer **tmux** over repeatedly driving a bare subprocess PTY. `prompt_toolkit` behaves most reliably when the child has a genuine controlling terminal; tmux provides that and lets the verifier use `send-keys` plus `capture-pane` without stealing the user's active terminal.
- Minimal tmux smoke pattern:

 ```bash
 tmux new-session -d -s hermes-switch-smoke -x 140 -y 45 'hermes'
 # Wait until the composer prompt is visible before sending input.
 tmux send-keys -t hermes-switch-smoke '/switch' Enter
 tmux capture-pane -t hermes-switch-smoke -p -S -120
 # Require the captured pane to contain the scope title and both choices.
 tmux send-keys -t hermes-switch-smoke Escape
 tmux send-keys -t hermes-switch-smoke '/quit' Enter
 tmux kill-session -t hermes-switch-smoke 2>/dev/null || true
 ```

- Synchronize on visible prompt text rather than fixed sleeps when scripting the smoke. Capture after each state transition and verify the exact scope/provider/model labels.
- A raw PTY transcript containing repaint fragments, row numbers, or missing modal text is inconclusive; it may be a capture/synchronization artifact. Change harness strategy instead of repeating the same timed-out call or declaring the picker broken.
- After the local tmux smoke passes, verify over the same SSH path the user will use when possible. No Windows-specific picker implementation is needed: Windows is only the SSH client; the Mac-hosted TUI owns the interaction.

## Update safety

A `quick_commands` alias survives Hermes updates but cannot add an explicit scope stage by itself. A core TUI change should either be upstreamed or represented in the installation's existing update-safe patch/reapply mechanism. Never claim permanence until reapply behavior is verified.
