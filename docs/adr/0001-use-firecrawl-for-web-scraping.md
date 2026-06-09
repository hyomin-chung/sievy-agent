# ADR-0001: Use Firecrawl for Web Scraping

**Status:** Accepted
**Date:** 2026-05

## Context

Sievy must scrape arbitrary public web pages and return both structured links and readable markdown body content. Sites vary significantly: some are static HTML, some render with JavaScript, some use infinite scroll, some block bots. Two operations are required:

1. **Listing scrape** — extract all links from a listing page to detect individual post URLs
2. **Detail scrape** — extract the full body content of an individual post

A reliable, managed scraping service is needed that handles JavaScript rendering, anti-bot measures, and rate limiting without requiring infrastructure maintenance.

## Decision

Use Firecrawl as the sole scraping provider for both listing page link extraction (`fetch_listing`) and individual post body fetching (`fetch_detail`).

## Alternatives Considered

| Option                   | Reason rejected                                                                                     |
| ------------------------ | --------------------------------------------------------------------------------------------------- |
| BeautifulSoup + requests | No JavaScript rendering. Fails on modern sites.                                                     |
| Playwright / Puppeteer   | Requires a managed browser instance per request. Complex deployment, high memory, slow cold starts. |
| Custom scraper per site  | High maintenance burden. Every site requires custom parsing logic.                                  |

## Consequences

**Accepted tradeoffs:**

- Firecrawl API costs apply per scrape call. Each scan that processes N new posts incurs N Firecrawl calls.
- Some sites are explicitly blocked by Firecrawl (e.g. Craigslist) and cannot be supported.
- The `links` format returns empty on some JavaScript-heavy pages (e.g. myballard.com). A markdown link extraction fallback using regex on `[text](url)` patterns is required.
- Timeout errors on slow pages are caught per-post. A single post timeout does not abort the entire scan.

**Benefits:**

- Zero infrastructure for scraping. No browser management.
- Consistent markdown output regardless of site structure.
- Handles anti-bot measures, rendering delays, and content normalization automatically.
