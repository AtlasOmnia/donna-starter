# Native first-turn context inspection

Use this when someone asks what Hermes sends to the model on the first message of a fresh session, especially in Docker.

## Preflight: fixed fresh-session payload

Run the native offline diagnostic:

```bash
hermes prompt-size --platform cli
hermes prompt-size --platform telegram
hermes prompt-size --platform telegram --json
```

`prompt-size` constructs a real inspection agent using the platform-resolved toolsets, builds the same fresh-session system-prompt tiers, and inspects the agent's tool-schema JSON without making a provider API call. It reports:

- total system-prompt bytes/chars
- skills-index bytes
- memory and user-profile bytes
- stable, working-directory/rules, and volatile prompt tiers
- tool-schema count and serialized bytes

It is a byte/character composition report, not an exact provider-tokenizer count and not a raw full-prompt dump.

## Live session: after the first turn

Send:

```text
/usage
```

On current builds, the live context breakdown estimates the next request by category:

- system prompt
- built-in tool definitions
- rules / working-directory context
- skills
- MCP tool schemas
- subagent definitions
- memory
- conversation

The category estimator uses the `chars / 4` heuristic. Prefer the provider's reported input-token usage when exact billing/token accounting matters.

## Docker forms

Named container:

```bash
docker exec -it hermes hermes prompt-size --platform cli
```

Docker Compose service:

```bash
docker compose exec hermes hermes prompt-size --platform cli
```

Choose the platform that matches the real session (`cli`, `telegram`, `discord`, etc.), because enabled tools can differ by platform. If the command is absent in an older image, update/recreate from the current official image rather than inventing an internal script.

## Answering users accurately

Distinguish these questions:

1. **What is loaded before the first API call?** Use `hermes prompt-size`.
2. **What will the next live request contain after the first exchange?** Use `/usage`.
3. **What are the exact raw prompt contents?** Neither command is a raw wire-payload dump; use the saved session/system-prompt snapshot or a deliberate provider-request capture only when raw inspection is truly required.

Do not call the `chars / 4` result exact. Do not imply `prompt-size` alone proves the live MCP category; `/usage` reads the live agent and explicitly separates registered `mcp_` tools.