---
name: hermes-context-optimization
description: hermes-context-optimization — Optimize Hermes startup/context payloads, compression, tool-schema loading, memory/skill injection, and visual-context experiments.
version: 1.0.0
license: MIT
platforms:
- macos
- linux
- windows
metadata:
 hermes:
 tags:
 - hermes
 - context
 - compression
 - prompt
 - tool-schemas
 - memory
 - skills
 - multimodal
 related_skills:
 - hermes-agent
 - hermes-config-editing
---
# Hermes Context Optimization

Use this when the user asks about Hermes prompt/context size, “hello” startup cost, compression behavior, memory/profile bloat, tool-schema overhead, skill loading, session-store/search-index storage, or multimodal/visual-context approaches such as Snapcompact.

For large `state.db` search-index maintenance, resumable `optimize-storage --no-vacuum` runs, foreground timeout handling, and post-run verification, follow `references/session-store-optimization.md`.

When bounded workers repeatedly fail with `session_persistence_failed` because a live profile DB is lock-contended, preserve the worktree handoff and use the non-disruptive isolated-`HERMES_HOME` workflow in `references/isolated-worker-state-store.md`. Diagnose the profile-specific DB and lock owners first; never terminate a user's live TUI or optimize its store merely to unblock a coding worker.

## Operating style for the user

- Be concise first. If he asks for the savings, give the numbers, not a lecture.
- Separate **hard blockers** from **engineering choices**.
- Prefer token/accounting estimates grounded in actual provider/runtime data when available; use ratios only when clearly labeled.
- Do not imply that all startup prompt text is interchangeable. Bucket it by runtime role.

### Long standing-goal payloads

When a long `/goal` prompt is displayed as a compact token such as `[[ … [77 lines] … ]]`, treat that representation as potentially lossy rendered text, not as the authoritative goal body. Hermes' goal state stores the string it receives and does not dereference wiki-style links or recover omitted lines. Before allowing a goal worker to edit anything, require it to read the complete authoritative specification from a file and verify that the first turn contains the expected task scope. Use a short file-backed goal such as: `Read and execute the complete goal specification at /absolute/path/goal.md; treat that file as authoritative; do not act on truncated display text.` If the worker loads Obsidian or searches for a note matching the compact label, pause/clear the goal: it received the display placeholder, not the task. Do not accept a “goal achieved” result caused only by missing input; require artifact or test evidence.

Reference: `references/goal-long-prompt-preservation.md`.

## Native first-turn inspection

When the question is what Hermes loads or sends on the first message of a fresh session, start with the native surfaces rather than reconstructing the prompt manually:

- **Preflight fixed payload:** `hermes prompt-size --platform <cli|telegram|discord|...>`; add `--json` for machine-readable output. It runs offline and reports system-prompt tiers, skills, memory/profile, and tool-schema bytes/count using platform-resolved tools.
- **Live request after the first turn:** `/usage`; it separates system prompt, built-in tools, rules, skills, MCP schemas, subagent definitions, memory, and conversation.
- Treat the displayed token categories as estimates (`chars / 4`), not exact provider-tokenizer counts. Use provider-reported input tokens for the exact total. Do not present proportionally scaled category estimates as exact tokenizer measurements; label them as approximations if used.
- Start from the fixed-payload basics: memory block, user-profile block, skills index, core system prompt, built-in tool schemas, delegation schema, MCP schemas, then conversation. If the user asks specifically how large `user.md` or `memory.md` is under Mnemosyne, report the live generated prompt blocks even when no literal Markdown files exist.
- Do not blame an intentionally isolated/test Tool Router merely because the default profile exposes a broad tool surface. First establish the normal baseline composition. Inspect router policy or logs only when the question is about routing, an unexpected regression, or whether schemas should have been narrowed.
- For finer offline categories, construct the same inspection agent and call `agent.context_breakdown.compute_session_context_breakdown(agent, messages=[])`. This separates core system prompt, built-in tool definitions, skills, MCP, delegation schema, and combined memory/profile. Remember that this command also uses the rough `chars / 4` estimator.
- In Docker, run the same command through `docker exec -it <container> hermes prompt-size ...` or `docker compose exec <service> hermes prompt-size ...`.
- Distinguish a composition report from a raw wire dump: `prompt-size` does not print the complete prompt contents, and live MCP registration is best verified through `/usage`.

Full command matrix, Docker examples, and interpretation pitfalls: `references/native-context-inspection.md`.

### Explain schema growth correctly

Tool definitions do not grow merely because a conversation gets older. They are a fixed schema surface for that session/request. The baseline grows when Hermes updates, enabled toolsets, plugins, MCP servers, Office integrations, or dynamic provider tools register additional callable schemas. Prompt caching may reduce repeat billing and latency, but it does not return the occupied context window. State these distinctions before recommending pruning, profile specialization, consolidation, or dynamic routing.

## Initial payload triage

When analyzing Hermes startup cost, split the payload into these buckets:

| Bucket | Can be compressed/lazy-loaded? | Notes |
|---|---:|---|
| Core system/developer rules | Partly, but keep authoritative text | Identity, safety, tool policy, authority hierarchy, injection handling, platform rules need reliable system-channel text. |
| Tool schemas | No, unless tools are pruned | Provider needs machine-readable JSON schemas to expose function calls. A screenshot of schemas is not a callable tool registry. |
| Memory/user profile | Yes | Good candidate for tiering, retrieval, or visual appendix. |
| Skill directory/index | Yes | Prefer tiny router/index at startup; load skills on demand. |
| Environment/project notes | Yes | Reference context; retrieve or attach only when relevant. |
| Prior sessions/compressed history | Yes | Good candidate for summary + artifact fallback. |

## Preferred optimization order

1. **Measure the payload composition** if tools/logs are available: system text, memory/profile, skill directory, tool schemas, platform metadata.
2. **Prune/gate tool schemas** first. Tool schemas often dominate startup cost and cannot be replaced by images.
3. **Shrink the authoritative bootloader** to core identity/rules only.
4. **Tier memory/profile** into always-loaded core facts vs domain/project facts retrieved on demand.
5. **Gate skill directory** behind a tiny class-level index and explicit `skill_view` loading.
6. **Use visual context/Snapcompact only for reference material**, not for authority or tool registration.

## Live latency attribution

For gateway or voice latency, measure one clean tool-free turn first and inspect logs from a separate controller afterward. Never have the measured agent call log/file tools inside its own latency probe; those calls add model round trips and invalidate the sample. Break the result into model time, actual tool execution, framework overhead, client-to-gateway transport, STT endpointing, and TTS synthesis/playback. Label boundaries that the current build does not timestamp as unmeasured rather than estimating them.

Tool-heavy turns commonly spend most of their time in the repeated model calls around tools, not in tool execution. Compare single-call turns at several input-token sizes to prove context-pressure effects. Tool Router can reduce schemas and unnecessary tool selection, but it does not shrink accumulated conversation history; pair it with an explicit compression/context policy when history is the bottleneck.

Full calculation method and voice-specific acceptance shape: `references/gateway-voice-latency-attribution.md`.

## Snapcompact / visual-context guidance

Snapcompact-style image context can reduce reference-text tokens by roughly the article’s observed ratio:

```text
10,000 text tokens -> 3,279 image tokens ≈ 67.2% reduction
```

Quick estimate:

```text
image_tokens ≈ text_tokens * 0.3279
saved_tokens ≈ text_tokens * 0.6721
```

For Hermes startup, report realistic savings only for the imageable portion:

- 4k imageable reference tokens -> saves ~2.7k
- 8k imageable reference tokens -> saves ~5.4k
- 12k imageable reference tokens -> saves ~8.1k

Do not claim the entire initial payload can become an image unless tool schemas and authoritative rules are separately handled.

## Safe architecture

Recommended shape:

```text
minimal authoritative text bootloader
+ typed user prompt
+ minimal/gated tool schemas
+ optional visual reference appendix
+ retrieval/lazy loading for memory, skills, and project/domain context
```

For local-first setups, consider:

```text
snapcompact image -> local vision model extracts relevant section -> main model receives extracted text
```

This avoids forcing the primary model to OCR every appendix on every turn, but adds latency and OCR risk.

## Memory compaction pattern (for reducing initial prompt)

When shrinking always-loaded memory/user_profile:
- Remove entries that duplicate existing skills, AGENTS.md, or vault docs.
- Merge overlapping preferences into single compact bullets.
- Drop stale/session-specific notes and auto-captured noise.
- Keep only durable behavioral facts that materially affect how the agent acts on every turn.

## Operational pitfalls

- **Vague profile labels cause downstream hallucination.** A label like "20 years HK experience" is too broad — a model can't tell if it means finance, hospitality, teaching, or import/export, so it guesses. When the user corrects a mistaken extrapolation, trace back to the SOURCE label and make it specific (e.g., "20 years Hong Kong housekeeping/hospitality experience"). Don't just correct the session output — fix the underlying profile data. See `references/profile-data-accuracy.md`.
- Memory tool loop trap: calling the memory tool without specifying a valid operation causes repeated identical failures and hard-stops further calls to it in that turn. Always include an explicit action field with concrete old_text/new content; if unsure, use terminal or file inspection first instead of guessing entries. Never ping it as “read current state”; rely on last known list or external checks.
- Repeated-call guardrail: the same tool call (identical arguments) failing 3 times triggers repeated_exact_failure_block and blocks that tool until you change strategy. When a tool fails:
 - Do NOT retry with identical arguments hoping it will work next time.
 - Read the error message; adjust parameters, shape, or approach before calling again.
 - If the tool does not support what you’re trying (e.g., “read” when only add/replace/remove exist), stop using it for that purpose and switch to an alternative method.
- Do not over-explain when the user asks for a numerical answer; compute or estimate and answer directly.

## Memory compaction (proven batch workflow)

When shrinking memory or user_profile:

1) Inspect current entries via terminal if possible:
 - python3 -c "import yaml; c=yaml.safe_load(open('~/.hermes/config.yaml')); print(c.get('mnemosyne',{}).get('memory',[]))"
 - If that is empty but you see injected MEMORY/USER PROFILE at startup, those are in mnemosyne's DB (not config.yaml). You must work from the text already injected into your context — there is no read-only memory() call.

2) Use a single operations batch instead of many small calls:
 - Build one operations list with add/replace/remove entries only for facts you can match as substrings in what's currently injected.
 - Batch rules:
 - Remove: domain notes already covered by skills (business, work, community, browser, content-style).
 - Replace: verbose environment/model/provider notes → compact bullets.
 - Add: only durable behavioral facts that affect every turn.
 - Watch for all-or-nothing behavior: if one replace/remove fails due to a mismatched old_text, the entire batch is rejected — ensure exact substring matches against what you see injected.

3) Avoid tool-loop traps:
 - memory() has no read-only mode; calling it with action=None or identical arguments repeatedly will trigger repeated_exact_failure_block and halt further calls.
 - If blocked, stop retrying unchanged; switch to terminal inspection or file reads instead.

4) Expected savings:
 - A well-maintained system memory can be 1–2K chars (around 300–600 tokens). Anything above ~3K is usually hoarding stale task notes that belong in skills, vault files, or session history.

## Pitfalls

- Do not put mandatory behavior rules only inside an image; image text is reference content, not a reliable system-channel control surface.
- Do not put tool schemas only inside an image; providers require structured schemas for tool calling.
- Do not attach large visual appendices to trivial greetings unless the provider's image-token accounting and latency justify it.
- Compression routing pitfall: `auxiliary.compression` overrides `compression.summary_model`. If compression seems stuck on an unexpected provider (e.g., DeepSeek), check `auxiliary.compression` first — it is usually the actual source of truth.

## Displayed output vs model-visible context

When the user asks whether a long tool result shown on screen is also fully reread by the model, distinguish the presentation layer from the active prompt. The UI/gateway may display the complete tool output, while Hermes later compacts the model-visible transcript. During context cleanup, the compressor receives the full transcript including tool messages, then performs a cheap pre-pass before any LLM summary: older tool results are replaced with informative one-line records (tool name, operation, exit status or size), identical results are deduplicated while the newest full copy is retained, and old tool-call arguments are truncated. Recent tool results remain verbatim. This is context pruning, not merely a JSON transport separator; JSON is used for message/tool structure and structured summaries, while the token savings come from replacing old content. The original full session remains available in the session store.

Use this concise explanation when asked: “The screen and model context are separate. Hermes can show the full result, but older tool output is later replaced internally with a compact record; recent output stays full.” Do not incorrectly imply that every long result is immediately omitted or that JSON encoding itself causes the reduction.

## Compression model requirements (from official behavior)

- Hermes sends the entire selected middle section in one `call_llm(task="compression")` request; it does not map-reduce or chunk the middle automatically.
- **Conservative default:** give the compressor at least the parent model's effective compression trigger/window. This avoids auto-lowering, truncation, and hidden instruction/summary overhead.
- **Measured narrow exception:** a smaller compressor can be valid when the actual middle is calculated and live-proven. Approximate the first-cycle payload as:

```text
usable_prompt = parent_context - parent_max_tokens
trigger = usable_prompt × compression.threshold
middle ≈ trigger × (1 - compression.target_ratio)
```

 Then add headroom for the structured-summary instructions, prior summaries, tool metadata, and token-estimation variance. Never describe the raw middle estimate as the whole request size.
- **Shared-compressor rule:** size the compressor for the largest active parent plane it serves. A Gemma instance that compresses both an 80K local worker and a 184K cloud orchestrator must satisfy the cloud parent's trigger, not merely the worker's smaller requirement.
- Keep `providers.<custom>.models.<exact-id>.context_length`, `auxiliary.compression.context_length`, and the backend's live loaded context truthful and aligned. Do not advertise a larger context merely to bypass a conservative guard; either load the larger slot or accept an earlier trigger.
- Verify near the boundary with a real compression-shaped request and inspect returned model, prompt tokens, finish reason, content, and elapsed time.

Ref: https://hermes-agent.nousresearch.com/docs/developer-guide/context-compression-and-caching

## Compression runtime behavior

How Hermes actually routes compression requests:

- The ContextCompressor calls `call_llm(task="compression")`.
- This is handled by `auxiliary_client`, which prioritizes the config under:
 - `auxiliary.compression.provider`
 - `auxiliary.compression.model`
- If those are set, they override any `compression.summary_model` / `compression.summary_provider` values. This is a common source of confusion: your "compression" block may look correct but be ignored because `auxiliary.compression` takes precedence.

So the effective path is:

 Compression → call_llm(task="compression")
 → auxiliary_client reads auxiliary.compression.*
 → uses that provider/model for the summary call

Implication: to debug "compression still using main model", check BOTH:

- `auxiliary.compression` (primary routing; this one often wins)
- `compression.summary_model` / `compression.summary_provider` (fallback/legacy; may be ignored)

A frequent scenario:
- You set a local summary model in `compression.*`, restart, but you still see traffic on DeepSeek or another cloud provider.
- Cause: `auxiliary.compression.provider` is set to that cloud provider and overrides your intent.
- Fix: align `auxiliary.compression` with your desired endpoint (e.g., custom:lmstudio-windows), not just the `compression.*` block.

## Compression troubleshooting (silent failures)

If compression appears stuck, still hitting a previous provider, or silently falling back:

1) Confirm auxiliary.compression is what you expect:
 - Run: python3 -c "import yaml; c=yaml.safe_load(open('~/.hermes/config.yaml')); print(c.get('auxiliary',{}).get('compression',{}))"
 - If provider is not your desired endpoint (e.g., it's deepseek), that is why compression isn't using your local model.

2) Confirm config:
 - Run: python3 -c "import yaml; c=yaml.safe_load(open('~/.hermes/config.yaml')); print(c.get('compression',{}))"
 - Ensure summary_provider/summary_model are set (e.g., custom:lmstudio-windows), but remember they may be overridden by auxiliary.compression.

3) Check if compression.summary_model is wired into agent_init.py:
 - Bug (fixed): agent_init.py historically passed summary_model_override=None, ignoring compression.summary_model from config.yaml — so compression always used the main model.
 - Verify fix present: grep "summary_model_override=_summary_model" ~/.hermes/hermes-agent/agent/agent_init.py should return a match. If not, the patch is missing and compression will silently use the main (expensive) model.

4) Verify the provider block is NOT empty:
 - Run: python3 -c "import yaml; c=yaml.safe_load(open('~/.hermes/config.yaml')); print(c.get('providers',{}).get('lmstudio-windows',{}))"
 - If this prints {} or missing base_url/api_key, compression will silently fail to reach your local endpoint and may fall back to an older/default provider.

5) Fix empty provider:
 - Use Python YAML read/write (not patch tool on config.yaml).
 - Ensure base_url and api_key are set, e.g.:
 providers:
 lmstudio-windows:
 base_url: http://127.0.0.1:1234/v1
 api_key: lm-studio

6) Restart gateway:
 - launchctl stop ai.hermes.gateway && sleep 3 && launchctl start ai.hermes.gateway

7) Confirm live:
 - Trigger /compress in a large session.
 - Check logs: grep "2026-06" ~/.hermes/logs/gateway.log | grep -iE "compression|127.0.0.1"
 - If you see 127.0.0.1 in compression lines, it is using the local model.
- With 148+ skills registered, the skills index alone contributes ~5k tokens to the initial prompt. Before suggesting Snapcompact or memory tiering, prune unused skills — it is the highest-ROI first step. See `references/prompt-composition-baseline.md` for the measured breakdown and `references/skill-pruning-workflow.md` for the end-to-end procedure.
- **Post-pruning reality:** Even after removing unused tools, disabling 84+ skills, and trimming the index to ~2k tokens, initial prompt is still ~21–22k tokens because tool schemas (~11–13k) dominate. Do not claim further large savings without disabling actual tools or reducing loaded toolsets.
- **Always use live measurements over stale baselines.** When asked about context size: run the measurement commands in `references/prompt-composition-baseline.md` instead of relying on old numbers. Hermes updates frequently change prompt_builder, guidance blocks, and tool wiring — assumptions age fast.
- **Tool-router pattern for reducing initial payload**:**
 - Plugin lives at ~/.hermes/plugins/hermes-token-router/ (update-safe).
 - **Status: OPERATIONAL.** Router predicts toolsets with a separately configured lightweight model and an 8s fallback timeout; inspect the live router policy before naming its current provider/model.
 - a test profile is an isolated test harness, but its current model/provider must be read live. Do not restore a retired model from this historical example.
 - Conservative settings: confidence_threshold=0.0, long_message_decline_chars=2000, floor_toolsets=[terminal,file,web], short_message_bypass_chars=0.
 - Supported router providers: openrouter, deepseek, openai-codex. Provider choice is configuration-dependent; validate API compatibility and latency rather than preserving a historical default.
 - Key pitfalls: curly braces in ROUTER_SYSTEM_PROMPT must be escaped (`{{` `}}`), print() inside docstrings doesn't execute, external routing variability requires timeout wrapper.
 - See `references/tool-router-architecture.md` for full architecture, config, pitfalls, and testing commands.

See `references/prompt-composition-baseline.md` for measured breakdowns; use those to decide whether enabling the router justifies added latency vs token savings for a given profile.
- **Do NOT use `patch` tool on `~/.hermes/config.yaml`** — the agent refuses with "security-sensitive configuration." Use Python to read/write YAML directly, or `sed` for simple single-line inserts. For multiline `sed` inserts on macOS, prefer Python — macOS `sed -i ''` chokes on `\n` in the replacement string.
- **After modifying config.yaml disabled list, verify with YAML parsing** — check for duplicate `disabled:` keys (YAML silently uses the last one) and confirm the count matches expectations: `grep -n "disabled:" ~/.hermes/config.yaml` must return exactly one line.
- **Gateway restart required** after config changes: `launchctl stop ai.hermes.gateway && sleep 2 && launchctl start ai.hermes.gateway`. Do NOT restart from within a Hermes session that depends on the gateway — restart in a separate terminal call.

## Silent fallback to main model during compression (IMPORTANT)

Hermes will silently fall back to the main (often expensive/cloud) model for context compression when the configured summary model fails, times out, or returns invalid JSON. This is implemented as `_fallback_to_main_for_compression` in `agent/context_compressor.py`.

Behavior:
- On first failure of the summary model, Hermes logs a warning and sets `summary_model = ""`, meaning "use main model from now on."
- This fallback persists for the rest of the session — all subsequent compressions use the main model until the session ends or is restarted.
- You may see messages like "📦 Preflight compression: ~116,065 tokens >= 108,800 threshold" and assume it's using your cheap/local summary model — but if fallback fired, it is actually hitting your main model (often at much higher cost).

Common triggers:
- LM Studio or local endpoint is slow under large-context loads (100k+ tokens) → timeout.
- Transient network error between Hermes and summary endpoint.
- Summary model returns malformed/empty JSON.

How to detect:
- Check gateway logs:
 - `grep -E "Fallback.*compression|Summary model" ~/.hermes/logs/gateway.log`
 - Look for lines like:
 - `Summary model '...' timed out/unavailable. Falling back to main model '...' for compression.`

How to mitigate (without patching Hermes core):
- Use a faster, smaller summary model that can handle large context without timing out (e.g., 9B-class tuned for instruction).
- Ensure summary endpoint is on a reliable local machine and not competing with heavy workloads.
- Consider setting `compression.abort_on_summary_failure: true` if you prefer Hermes to abort compression with a simple continuity note instead of burning expensive tokens on the main model.

If you need to prevent fallback entirely, that requires patching `_fallback_to_main_for_compression` in `context_compressor.py`. Prefer adjusting model choice or timeout behavior first.

## Skill pruning workflow

When reducing initial prompt size by disabling unused skills:

1. **Extract actually-used skill names** from session history via `state.db`. The raw query returns category-prefixed names (`apple:imessage`, `productivity:some-domain-skill`) — strip prefixes with `sed` to match directory names:
 ```bash
 sqlite3 ~/.hermes/state.db "
 SELECT DISTINCT json_extract(args, '\$.name')
 FROM (
 SELECT json_extract(tool_calls, '\$[0].function.arguments') as args
 FROM messages
 WHERE tool_calls LIKE '%skill_view%' OR tool_calls LIKE '%skill_manage%'
 )
 WHERE args IS NOT NULL
 AND json_extract(args, '\$.name') IS NOT NULL
 AND json_extract(args, '\$.name') != ''
 " | sed 's|^[a-z]*:||; s|.*/||' | sort -u > /tmp/used_skills.txt
 ```
2. **Get all installed skill names**:
 ```bash
 find ~/.hermes/skills -name "SKILL.md" -exec dirname {} \; | xargs -I{} basename {} | sort > /tmp/all_skills.txt
 ```
3. **Diff to find unused skills**:
 ```bash
 comm -23 /tmp/all_skills.txt /tmp/used_skills.txt > /tmp/unused_skills.txt
 ```
4. **Check cron jobs** for skill references before disabling — a skill may be loaded by cron even if never called interactively. Search actual YAML config files, not log output:
 ```bash
 find ~/.hermes/cron -name "*.yaml" -exec grep -l "skills:" {} \; 2>/dev/null
 for f in $(find ~/.hermes/cron -name "*.yaml" 2>/dev/null); do
 if grep -q "skills:" "$f"; then
 echo "=== $f ===" && grep -A5 "skills:" "$f"
 fi
 done
 ```
5. **Add `skills.disabled` list** to `~/.hermes/config.yaml` under the top-level `skills:` key (same level as `external_dirs`). The `patch` tool refuses config.yaml — use Python instead:
 ```python
   import yaml
   with open('~/.hermes/config.yaml') as f:
       content = f.read()
   # Insert before '  config:' or append to existing disabled list
   content = content.replace(
       '    - last-skill\n  config:',
       '    - last-skill\n    - new-skill\n  config:'
   )
   with open('~/.hermes/config.yaml', 'w') as f:
       f.write(content)
   ```
 Alternatively use `sed` for single-line inserts: `sed -i '' '/ - last-skill/a\ - new-skill' ~/.hermes/config.yaml`. Avoid multiline `\n` in macOS sed — it breaks.
6. **Verify** with Python YAML parsing — watch for duplicate `disabled:` keys (YAML silently uses the last one):
 ```bash
 grep -n "disabled:" ~/.hermes/config.yaml # must be exactly one
 python3 -c "import yaml; c=yaml.safe_load(open('~/.hermes/config.yaml')); print(len(c['skills']['disabled']))"
 ```
7. **Restart gateway** for changes to take effect:
 ```bash
 launchctl stop ai.hermes.gateway && sleep 2 && launchctl start ai.hermes.gateway
 ```

See `references/skill-pruning-workflow.md` for the full session transcript and rationale.

## Jinja chat-template auditing

When reviewing a custom Jinja chat-template (e.g., for llama.cpp, vLLM, or Hermes gateway), check for these recurring issues:

1. **Hardcoded overrides block caller params** — `{%- set enable_thinking = false %}` at top level always wins over any external `enable_thinking` passed in. Fix: wrap in `{%- if enable_thinking is not defined %}` guard.
2. **Image/video items emit no data** — detecting the item type but only outputting `\n\n` without passing through `item.image_url`, `item.url`, or `item.image`. The model receives a placeholder with no reference to act on. Fix: add `.get()` fallbacks for common key names.
3. **Double-counting from multi-pass rendering** — if `render_content` is called both in a reverse-scan pass and the main forward loop, ensure the scan pass uses `do_vision_count=false` so namespace counters stay correct.
4. **Tool arguments as JSON string** — OpenAI-format tool calls often send `arguments` as a JSON string, not a dict. Calling `|items` on a string iterates characters. Fix: branch on `{%- if args is string %}` and `json.loads(args)` first.
5. **Reverse-scan heuristics are fragile** — checking `content.startswith('...')` for tool-result boundaries breaks if user messages coincidentally match. Prefer explicit role-based checks where possible.
6. **Unknown roles crash silently** — always include the actual role in the error: `'Unexpected message role: ' + message.role`.
7. **Test with representative payloads** — use Jinja2's `DictLoader` + `env.globals['raise_exception']` to validate before deploying. Cover: basic conversation, multi-modal content, tool calls with string args, consecutive tool results, reasoning_content, and edge cases (None content, unknown roles).

See `references/jinja-chat-template-audit.md` for the full audit checklist and test harness pattern.

## Recovery from an unrecoverable session context

When a CLI or messaging session reports that context length was exceeded and Hermes cannot compress further, treat the failure as **session-scoped**, not as evidence that the gateway, topic, project files, or external application are corrupted.

1. Confirm the failure boundary from the live logs or status surface. A message such as `Max compression attempts reached` or `cannot compress further` means another `/compress` retry is unlikely to recover the in-memory conversation.
2. Preserve the old session. Do not delete it, and do not restore it with `/resume` or `/topic <session-id>` merely to continue the task; those paths can reload the same oversized history.
3. Start a fresh session in the same messaging topic with `/new` (or the equivalent new-session command for the client). In Telegram topics, `/new` resets only the current topic's session and leaves other topics untouched.
4. Continue with a **short, authoritative handoff**: current checkout/writer ownership, last verified artifact or acceptance boundary, remaining gate, exclusions, and the evidence required before claiming success. Prefer a file-backed handoff for long work; never ferry the entire transcript into the new session.
5. Keep the first fresh-session turn narrow and verification-first. Reconcile the checkout and incumbent writer before any write-capable resume, then work only the remaining gate.
6. Use `/context` or `/usage` after several turns. If the new session is again approaching its compression threshold, close it at a clean handoff boundary and hand off again instead of repeatedly forcing compression.

## Thin control planes for multi-profile work

A dedicated specialist Telegram bot is not the default fix for context overflow. Keep the assistant as the single user-facing control plane and route long Dev work into tracked profile processes or Kanban instead:

```text
the user → assistant intake/status → domain controller → owning specialist worker
```

The coordinator topic should carry scope, approvals, compact status, and final evidence—not the worker's full implementation transcript. The domain controller owns architecture/integration and may route bounded child work to specialist profiles; workers return short, file-backed handoffs rather than screenshots, accessibility trees, raw logs, or copied conversation history. Create the durable root card before launch when work outlives the turn, spans profiles, has dependencies/review, or needs restart recovery. Use a separate specialist bot only for deliberate direct access or independent notifications; it adds another gateway/session surface and does not repair delegation by itself.

When a session overflows, do not bypass the control plane by restoring the old transcript in a specialist surface. Start a fresh session, preserve the old history, and resume from a concise handoff after reconciling the exact profile, checkout, and writer owner.

For the Telegram-specific recovery recipe, official command behavior, and the verified incident boundary, see `references/context-overflow-recovery.md`.

## References

- `references/compression-runtime-fallback-notes.md` — how the compressor chooses models, when it falls back to main, and how to debug "still using main model".
- `references/context-overflow-recovery.md` — recover a session after Hermes exhausts context compression without deleting history or reloading the oversized transcript.
- `references/snapcompact-hermes-boot-analysis.md` — session-derived notes on applying Snapcompact to Hermes startup payloads and realistic savings estimates.
- `references/jinja-chat-template-audit.md` — 7-point audit checklist for custom Jinja chat-templates with test harness pattern.
- `references/profile-data-accuracy.md` — why vague user profile labels (\"20 years HK experience\") cause downstream model hallucination, and the rule for fixing them.
## Public support files

- `references/compression-runtime-fallback-notes.md`
- `references/context-overflow-recovery.md`
- `references/gateway-voice-latency-attribution.md`
- `references/goal-long-prompt-preservation.md`
- `references/isolated-worker-state-store.md`
- `references/jinja-chat-template-audit.md`
- `references/native-context-inspection.md`
- `references/profile-data-accuracy.md`
- `references/prompt-composition-baseline.md`
- `references/session-store-optimization.md`
- `references/skill-pruning-workflow.md`
- `references/snapcompact-hermes-boot-analysis.md`
- `references/tool-router-architecture.md`
