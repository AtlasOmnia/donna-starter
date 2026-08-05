# Jinja Chat Template Patches for Local Model Tool-Calling

Use this reference when a local model emits malformed function calls, leaks template tokens, repeats tools after success, or fails only after a tool result is appended.

## Diagnose before patching

1. Query the live runtime model metadata (`/api/v1/models` in LM Studio) and record the exact loaded model, quant, context, parallelism, and `trained_for_tool_use` capability.
2. Run a one-tool, two-turn probe: request one exact function call, append a successful tool result, and require a short final answer.
3. Run the same probe with the application's complete tool schema set. If one-tool passes but the full set drifts or loops, the model/template is not reliable enough for that agent surface even if isolated function calling works.
4. Distinguish model output from application containment: malformed names/arguments and template-token leakage originate in the model/template; repeated side effects after a successful result also expose loop-guard or deterministic-completion weaknesses in the client.

## Gemma 4 + LM Studio

Gemma 4 tool templates have had documented function-call formatting defects, including failures after assistant `content + tool_calls + tool result` turns. Common symptoms include:

- leaked control/template fragments such as `thought`, `call:`, `<|...|>`, or malformed quote tokens;
- correct tool name with drifting aliases (`sheet_name` vs `sheet`, `range` vs `address`);
- hallucinated tools not present in the schema;
- repeated calls after a successful tool result;
- Jinja errors such as `Cannot call something that is not a function: got UndefinedValue` or a missing `format_type_argument` macro.

Authoritative/current leads:

- Google Gemma 4 26B-A4B discussion #20, function-calling template formatting: https://huggingface.co/google/gemma-4-26B-A4B-it/discussions/20
- LM Studio bug #1927, Gemma 4 26B-A4B tool template failures: https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/1927

Do not paste an unverified community Jinja template into a production preset. Prefer, in order:

1. an LM Studio/community model package whose live metadata says `trained_for_tool_use: true`;
2. the model author's corrected template on a current runtime;
3. a different tool-trained model family for mutation-heavy agent work.

For Hermes Office add-ins, Gemma 4 26B-A4B Q4 may succeed with one isolated tool but become unstable with the full Office schema set. Treat that differential as a failed agent-reliability gate, not proof that all function calling is broken.

## Qwen guidance

Qwen3.6 tool-trained builds are generally the safer local Hermes agent choice when the live runtime reports `trained_for_tool_use: true`. Keep the native chat template, leave LM Studio's system prompt blank, enable thinking for agent work, and prefer one parallel request. Re-test the exact two-turn tool-result loop after any model, quant, runtime, or template change.

## Client-side containment still required

A stronger model does not replace loop safety:

- canonicalize tool arguments recursively;
- block a repeated mutation on its second appearance;
- group semantically equivalent mutations even when sheet/address qualification differs;
- reject unknown fields/tools before Office.js execution;
- stop deterministically after a successful single-mutation fast path;
- keep a low absolute iteration cap for workbook mutations;
- verify that tool results remain in the next model turn.
