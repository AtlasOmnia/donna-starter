# Qwen-AgentWorld field notes

Session source: discussion with the user on local auxiliary/tool-use models, June 2026.

## What AgentWorld is

Qwen-AgentWorld-35B-A3B is not simply a standard agent-instruct model. The model card describes it as a language world model: it simulates agentic environments and predicts the next environment state given an agent action and interaction history.

Official intent: environment/world-state simulation across domains including MCP/tool calling, search, terminal, SWE, Android, web, and OS.

## Community signal observed

Hugging Face discussions around `Qwen/Qwen-AgentWorld-35B-A3B` showed early positive but anecdotal reports:

- Users reported it works well in OpenClaw / Hermes-style loops despite not being trained primarily as a normal coding agent.
- One user described it as better than Qwen3.6-35B-A3B in OpenClaw, with fewer grammar/weirdness issues in German.
- Another claimed it was better than Qwen3.6-27B for long-term non-coding agent tasks.
- Coding feedback was mixed: one report said it beat Qwen3.6-35B-A3B but was still worse than Qwen3.6-27B dense by a noticeable margin.

Treat these as promising field reports, not benchmark proof.

## Practical Hermes interpretation

Best candidate role:

- Local ops / agent-worker profile
- Web browsing workflows
- Terminal exploration
- Local email summarization
- AppleScript/macOS operation interpretation
- Tool-result interpretation
- Long state-tracking tasks
- Secondary profile/subagent work

Avoid treating it as an automatic replacement for Qwen3.6-27B dense as the main Hermes brain for:

- serious coding
- config surgery
- deep reasoning
- final judgment calls
- complicated Hermes debugging

## Chat template warning

A recurring practical issue is chat-template quality. HF discussion #10 recommended a fixed `chat_template.jinja` for agent loops, based on Qwen-Fixed-Chat-Templates. A user reported that replacing the default template in LM Studio dramatically improved OpenCode behavior.

For Hermes testing, check tool-call/role formatting before judging model quality. A bad template can make an otherwise capable model appear unreliable.

## Runtime notes

- Default context length is listed as 262,144 tokens.
- Qwen recommends at least 128K context for intended long simulation behavior.
- vLLM text-only serving may require `--language-model-only` because the architecture includes visual component definitions while this checkpoint contains only language weights.
- MTP/mmproj compatibility was being explored by users, but should be treated as test-first, not assumed production-stable.

## Recommendation summary

Use AgentWorld as a test candidate for fast, long-context, tool-heavy local worker duty. Keep Qwen3.6-27B dense as the safer main orchestrator until AgentWorld passes repeated Hermes tool-loop tests in the user's own workflows.
