# ADR-0002: Use Google ADK + Gemini Flash for Agent Orchestration

**Status:** Accepted
**Date:** 2026-05

## Context

The scan pipeline requires an agent that can perform multi-step tool use in sequence: search Elasticsearch via MCP to find semantically relevant posts, judge each result against the user's criteria, and call `create_alert` for matching posts. The agent must handle variable numbers of results and integrate with the Google Cloud ecosystem required by the hackathon.

## Decision

Use Google Agent Development Kit (ADK) with `Gemini Flash (configured via GEMINI_MODEL env var)` as the model. ADK handles the agent loop, tool call dispatch, and session management. Gemini Flash is the default model, configurable via the GEMINI_MODEL environment variable. It is used for both the scan judgment agent and URL pattern detection (one-shot inference).

## Alternatives Considered

| Option                                  | Reason rejected                                                                                             |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| LangChain                               | Not Google-native. Does not integrate with ADK runner or session management. More boilerplate for tool use. |
| Direct Gemini API with function calling | Requires manual multi-turn loop management. ADK handles this automatically.                                 |
| Gemini Pro / Ultra                      | Higher cost and latency. Flash is sufficient for structured judgment tasks with short prompts.              |
| OpenAI GPT-4                            | Not part of Google Cloud ecosystem. Excluded by hackathon context.                                          |

## Consequences

**Accepted tradeoffs:**

- ADK is experimental (v0.x). Breaking changes between versions are possible.
- Each ADK agent turn that calls a tool incurs one Gemini API call. With MCP search + N `create_alert` calls, total Gemini calls per scan = 2–4 in practice.
- `fetch_and_index` was intentionally removed from ADK agent tools. See ADR-0006.

**Benefits:**

- ADK manages the tool call loop without manual state management.
- Gemini Flash is fast (< 2s per call) and handles structured judgment reliably.
- Native integration with Google Cloud and Gemini API.
