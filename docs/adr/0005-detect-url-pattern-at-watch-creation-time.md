# ADR-0005: Detect URL Pattern at Watch Creation Time (Rule-Based + LLM Hybrid)

**Status:** Accepted
**Date:** 2026-05

## Context

Sievy supports arbitrary public listing pages. Each site structures its post URLs differently: query parameters, path slugs, base36 IDs, UTM parameters for external links. The scraper must reliably extract only individual post links — not navigation, pagination, or advertisement links. This is impossible to solve with a single hardcoded heuristic because URL structures vary arbitrarily across sites.

## Decision

Use a hybrid approach:

1. **At `create_watch` time (once):** Run Gemini to classify the URL structure of up to 100 sampled links from the listing page. Gemini returns a typed pattern dict (one of five types). Store the result in `Watch.post_url_pattern`.
2. **On every scan:** Use the stored pattern with rule-based `_matches_pattern` filtering. No Gemini call needed.
3. **Fallback:** If the stored pattern yields 0 results, `_fallback_filter` reverts to heuristic filtering using known ID query params and path depth thresholds.

## Alternatives Considered

| Option                            | Reason rejected                                                                                                                         |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Pure heuristics (no LLM)          | Works for a small set of known sites. Fails on novel URL structures without manual pattern authoring for each new site.                 |
| LLM on every `fetch_listing` call | Adds one Gemini call per scan on every watch. Unnecessary — site URL structures do not change between scans. Slower and more expensive. |
| Site-by-site manual config        | Does not scale. Requires developer intervention for every new supported site.                                                           |

## Consequences

**Accepted tradeoffs:**

- If a site changes its URL structure after watch creation, the stored pattern becomes stale. Users must delete and recreate the watch.
- Gemini classification is non-deterministic. Occasionally returns suboptimal patterns. The fallback mitigates this.
- Five pattern types must be maintained in `_matches_pattern`. New URL structures not covered by these types require adding a new type.

**Implementation notes:**

- `rstrip("/")` must not be applied to link paths before regex matching — trailing-slash anchors (`/$`) in `path_regex` patterns will fail.
- Fragment cleanup (`#more-xxx`) is applied to all extracted links before matching.
- When Firecrawl returns an empty `links` array, markdown link extraction via regex is used as a fallback.
- UTM parameter links skip domain equality checks because they link to external domains.
