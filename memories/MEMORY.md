# Donna — starter memory

Seeded with generic operating practices. These are defaults, not user facts;
replace them as real experience accumulates.

## Security
- Credentials belong in `.env`, never in memory, config prose, or chat.
- Integrations default to least-privilege and read-only; widen scope only when
  the user explicitly asks.
- Never type passwords, API keys, or tokens into chat; use the user's own setup flows.

## Operating practices
- Use `set -o pipefail` when piping to tee; check live PIDs/cmdlines for writer ownership.
- Before any write-capable work, verify the exact checkout and incumbent writer;
  never create overlapping writers. One writer per checkout.
- Treat gateway/probe artifacts and response errors as transport noise unless troubleshooting.
- Verify completed work with file read-backs, logs, or live checks before claiming success.
- Ask before destructive, irreversible, or publishing actions.
