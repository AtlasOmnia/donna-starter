# Desktop model-picker plugin pattern

Use this pattern only for a native Hermes Desktop picker that selects the active session model or the profile-global default without modifying Hermes core.

> Surface gate: this does **not** implement a terminal/TUI command and does not satisfy requests mentioning TUI, terminal, SSH, or opening the picker from another computer over SSH. A Python backend plugin command can only return text; it cannot open a prompt_toolkit modal. For TUI work, use `references/tui-model-picker-slash-command.md`.

## Runtime surface

- Install at `$HERMES_HOME/desktop-plugins/<id>/plugin.js`; folder name must equal `plugin.id`.
- Register a `statusBar.right` contribution whose render function opens a `Popover`.
- Use native SDK controls (`Select`, `SelectTrigger`, `SelectContent`, `SelectItem`, `Button`, `ConfirmDialog`) so the UI follows Hermes themes and interaction conventions.
- Runtime files are plain ESM with `jsx()` / `jsxs()`, not JSX. Supported imports are `@hermes/plugin-sdk`, `react`, and `react/jsx-runtime`.

## Live inventory

Read the same inventory used by `/model`:

```js
host.request('model.options', {
 ...(sessionId ? { session_id: sessionId } : {}),
 explicit_only: true,
 ...(force ? { refresh: true } : {})
})
```

Provider rows have `{ slug, name, models: string[] }`. Normalize malformed rows, deduplicate model IDs, and filter the model selector by the selected provider. Do not maintain a second hardcoded model catalog.

Recommended refresh policy:

- On mount/profile/session change: ordinary inventory read (`refresh` omitted).
- Manual Refresh: forced refresh (`refresh: true`).
- Periodic refresh: forced refresh at a conservative interval such as 15 minutes. A non-forced timer may reread cached inventory without discovering catalog changes.
- Clear the interval on unmount and ignore late async responses after unmount.

## Session versus global application

Use a separate Scope dropdown and explain the consequence beside it.

Session-scoped switch:

```js
host.request('config.set', {
 session_id: activeSessionId,
 key: 'model',
 value: `${model} --provider ${provider} --session`
})
```

Global profile-default switch:

```js
host.request('config.set', {
 key: 'model',
 value: `${model} --provider ${provider} --global`
})
```

Rules:

- Default to Session when an active session exists; otherwise default to Global.
- Disable Session and Apply when Session is selected without an active session.
- Global must state that future sessions use the new profile default while existing sessions remain unchanged.
- Do not touch auxiliary, vision, compression, delegation, credentials, or provider setup unless separately requested.
- Read `host.state.*` imperatively with `.get()` inside handlers so rapid session/profile changes cannot use stale render closures.

## Confirmation and errors

`config.set` may return:

```js
{
 confirm_required: true,
 confirm_message: '...'
}
```

Show the backend message in `ConfirmDialog`. Only after explicit user confirmation, repeat the identical request with `confirm_expensive_model: true`. Refresh inventory and show a success notification only after a completed switch. Surface busy-session and remote-backend errors; never silently retarget or persist another scope.

## Desktop-only `/switch` command bridge

A Desktop runtime plugin cannot register a backend slash command or extend the backend command inventory by itself. The following bridge is appropriate only when the requested UX is explicitly Hermes Desktop. Do not use it as a substitute for a TUI/SSH command.

1. **Desktop-local behavior:** register `COMPOSER_AREAS.middleware` and intercept the exact command before it reaches the agent.
2. **Command inventory/autocomplete and non-Desktop fallback:** install an enabled Python backend plugin whose `register(ctx)` calls `ctx.register_command("switch", ...)`.

The composer middleware contract is object-shaped, not string-shaped:

```js
export function handleComposerDraft(draft) {
 if (draft?.text?.trim().toLowerCase() !== '/switch') return draft

 const editor = activeComposerEditor()
 window.dispatchEvent(new CustomEvent('model-picker:open'))
 window.setTimeout(() => clearRestoredSwitchDraft(editor), 50)
 return null
}

ctx.register({
 id: 'switch-command',
 area: COMPOSER_AREAS.middleware,
 data: { handler: handleComposerDraft }
})
```

**Critical pitfall:** test middleware with realistic `{ text, attachments }` drafts. A test that passes raw strings can go green while the real Desktop handler never matches anything.

Returning `null` cancels submission, but the composer deliberately restores rejected/cancelled drafts. To keep `/switch` from reappearing:

- Capture only the currently focused `[data-slot="composer-rich-input"]`, optionally resolving through its nearest `[data-slot="composer-root"]`.
- Clear it after the restore microtask with a short bounded timer.
- Before clearing, verify the editor is still connected and its current text still equals `/switch`; never erase text the user typed meanwhile.
- Dispatch a bubbling `input` event after setting `textContent = ''` so Hermes state matches the DOM.

Make the picker `Popover` controlled (`open` / `onOpenChange`) and subscribe its component to the plugin-local browser event. This lets both the status-bar trigger and `/switch` open the same UI without duplicating picker state.

Companion backend plugin pattern:

```python
def _switch_fallback(_raw_args: str = "") -> str:
 return "The model picker opens in Hermes Desktop. On other surfaces, use /model."

def register(ctx):
 ctx.register_command(
 "switch",
 _switch_fallback,
 description="Open the model picker",
 args_hint="",
 )
```

Enable the backend plugin explicitly. Its command inventory entry takes effect in a fresh backend session/process; the Desktop runtime plugin itself normally hot-reloads. The Desktop middleware should consume `/switch` locally, so the fallback output is used only on non-Desktop surfaces.

## Test strategy for uncompiled runtime plugins

A standalone `node:test` suite can import `plugin.js` without launching Electron:

1. Read `plugin.js` as text.
2. Replace the three allowed bare import specifiers with `data:` URL modules that provide minimal SDK/React/JSX shims.
3. Dynamically import the transformed source.
4. Test exported pure helpers and plugin registration.

Cover at least:

- Exact session/global RPC payloads.
- Inventory normalization and provider-to-model filtering.
- Scope defaults and global consequence text.
- Expensive-model two-step confirmation.
- Error notification behavior.
- Forced periodic refresh plus interval cleanup.
- Supported imports and absence of JSX syntax.
- Presence of Scope, Provider, Model, Refresh, Apply, and confirmation controls.

Run `node --check plugin.js` and `node --test plugin.test.mjs`. Then verify in Hermes Desktop: no load-error toast, status-bar contribution appears, dropdowns populate from the live backend, and a session-scoped switch changes only that session. Do not perform a global switch merely for testing unless the user authorizes the model change.
