# ADR-0006: Run fetch_and_index in Python asyncio.gather, Not Inside ADK Agent

**Status:** Accepted
**Date:** 2026-06

## Context

The original scan design placed `fetch_and_index` as an ADK agent tool alongside `create_alert` and the Elastic MCP toolset. This design had two observed problems:

1. **Double execution:** Even when instructed "do not call `fetch_and_index` again," Gemini re-called it in some runs. Instruction-following for tool suppression after partial completion is unreliable.
2. **Uncontrolled parallelism:** ADK's internal tool call dispatch is opaque. Native `asyncio.gather` gives explicit control over parallelism and error handling per post.

## Decision

Remove `fetch_and_index` from ADK agent tools entirely. Run all `fetch_and_index` calls in Python via `asyncio.gather` before the ADK agent starts. The agent receives only two tools: Elastic Agent Builder MCP toolset and `create_alert`.

The agent's role is: **search → judge → alert**. It does not scrape or index.

## Alternatives Considered

| Option                                                        | Reason rejected                                                                                                                                    |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Keep `fetch_and_index` in ADK tools with stronger instruction | Instruction-following for "do not call this after step N" is unreliable across runs. Inherent to LLM-based orchestration of stateful side effects. |
| Sequential `fetch_and_index` (one at a time)                  | Correct, but N× slower. 20 posts × 2s per Firecrawl call = 40s vs ~5s with asyncio.gather.                                                         |
| Separate microservice for scraping                            | Overkill. asyncio.gather in the same process is sufficient.                                                                                        |

## Consequences

**Accepted tradeoffs:**

- `fetch_and_index` is no longer visible to the agent. All new posts are always scraped regardless of criteria pre-filtering.
- If all `fetch_and_index` calls fail, the agent never starts and no alerts are created. This is correct behavior.

**Benefits:**

- Parallelism is explicit and controllable. `asyncio.gather` runs all Firecrawl calls concurrently.
- Individual post failures are caught per-task. One Firecrawl timeout does not abort the entire scan.
- The ADK agent is now a pure judgment layer. Gemini calls reduced from O(N) to O(1) + O(matches).
- Eliminates the double-execution bug entirely.
