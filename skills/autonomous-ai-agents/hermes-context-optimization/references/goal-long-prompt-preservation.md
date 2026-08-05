# Preserving Long `/goal` Prompts

## Use when

A long Hermes `/goal` prompt is displayed as a compact form such as:

```text
[[ Prepare the curr.. [77 lines] .. or public repository review. ]]
```

## Failure signature

The goal worker may receive the compact display text literally. If it then loads Obsidian or searches for a note matching the shortened label, it does not have the actual task. Hermes' `GoalManager.set()` stores the string it receives; it does not resolve wiki-style `[[...]]` references or reconstruct omitted lines. A goal judge may incorrectly mark this blocked/missing-input turn as achieved.

Relevant implementation boundaries:

- `hermes_cli/goals.py`: `GoalManager.set()` persists the received goal string.
- `tui_gateway/methods_tools.py`: `/goal` passes the stored goal back as the kickoff message.
- The display summary is not evidence that the full task reached the worker.

## Reliable workflow

1. Put the complete goal specification in a Markdown file outside the live runtime state, for example:
 `~/Desktop/hermes-public-prep-goal.md`.
2. Verify that the file exists and contains the complete text before starting the goal.
3. Start `/goal` with a short instruction that names the absolute file path:

 ```text
 Read and execute the complete goal specification at ~/Desktop/hermes-public-prep-goal.md. Treat that file as authoritative. Do not act on truncated display text or summaries.
 ```

4. Require the first worker turn to read the file and acknowledge the real scope before editing.
5. If the first turn loads Obsidian, searches for a shortened note title, or repeats the `[[... [N lines] ...]]` token, pause or clear the goal. Do not let it edit.
6. Require concrete artifact, test, or command evidence before accepting `Goal achieved`.

## Safety boundary

Do not solve this by manually embedding a long prompt inside `[[...]]`. The brackets are the failure signature, not a file reference mechanism. Keep the full specification in the file and keep the standing goal short.
