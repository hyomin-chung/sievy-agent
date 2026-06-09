# Architecture

## Component Overview

```mermaid
graph TD
    FE[Frontend\nReact 18 · TypeScript · Vite · Tailwind v4\nMobile-first PWA]
    BE[Backend\nFastAPI · Python 3.13]
    FC[FirecrawlConnector]
    FD[FeedDetector]
    SO[ScanOrchestrator\nGoogle ADK]
    ES[Elastic Cloud Serverless\nsievy_posts\nsemantic_text · ELSER]
    MCP[Elastic Agent Builder MCP\nKibana endpoint]
    GEM[Gemini Flash]
    FS[Firestore\nwatches · alerts]
    AUTH[Firebase Auth\nGoogle OAuth]

    FE -->|REST API| BE
    AUTH -.->|X-User-Id header| BE
    BE --> FC
    BE --> FD
    BE --> SO
    SO -->|asyncio.gather| FC
    FC -->|body markdown| SO
    SO -->|PUT sievy_posts/_doc| ES
    SO -->|MCPToolset| MCP
    MCP -->|_search| ES
    ES -->|matching docs| MCP
    MCP -->|results| GEM
    GEM -->|create_alert| SO
    SO --> FS
    BE --> FS
```

## Data Flow: create_watch

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant FC as FirecrawlConnector
    participant Gemini
    participant FS as Firestore

    Client->>API: POST /watches {url, category, criteria, note}
    API->>FC: detect_post_url_pattern(url)
    FC->>FC: scrape(url, formats=[markdown, links])
    FC->>Gemini: classify URL structure (sample of 100 links)
    Gemini-->>FC: pattern dict {type, key/pattern/...}
    FC-->>API: post_url_pattern
    API->>FC: fetch_listing(url, url_pattern)
    FC-->>API: [PostCandidate, ...]
    API->>FS: save Watch {watch_id, criteria, baseline_post_ids, post_url_pattern, ...}
    API-->>Client: Watch object
```

## Data Flow: scan

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant FS as Firestore
    participant FC as FirecrawlConnector
    participant ES as Elastic Cloud
    participant MCP as Agent Builder MCP
    participant Gemini

    Client->>API: POST /watches/:id/scan
    API-->>Client: 200 OK (scan runs in background)
    API->>FS: get Watch (criteria, baseline, url_pattern)

    API->>FC: fetch_listing(url, url_pattern)
    FC-->>API: current posts
    API->>API: detect_new_posts = current - baseline

    par asyncio.gather — one thread per new post
        API->>FC: fetch_detail(post.url)
        FC-->>API: body markdown
        API->>ES: PUT sievy_posts/_doc/{watch_id}_{post_id}
        Note over ES: ELSER generates sparse embedding automatically
    end

    API->>Gemini: start ADK agent (via MCPToolset)
    Gemini->>MCP: search(index_pattern, query DSL)
    Note over Gemini: chooses semantic / match / bool based on criteria
    MCP->>ES: POST /sievy_posts/_search
    ES-->>MCP: matching documents
    MCP-->>Gemini: {post_id, post_url, body, title}

    loop for each matching document
        Gemini->>Gemini: judge body vs criteria
        Gemini->>API: create_alert(post_id, post_url, title, verdict, extracted_fields, summary)
        API->>FS: save Alert
    end

    API->>FS: update baseline_post_ids + last_scanned_at
```

## URL Pattern Detection

Runs once at `create_watch` time. The result is stored in `Watch.post_url_pattern` and reused on every scan.

```mermaid
flowchart TD
    A[source_url] --> B[Firecrawl scrape\nformats: markdown + links]
    B --> C{links empty?}
    C -->|yes| D[Extract from markdown\nregex on link syntax]
    C -->|no| E[Use links array]
    D --> F[Sample up to 100 links, strip fragments, deduplicate]
    E --> F
    F --> G[Gemini: classify URL structure]
    G --> H{Pattern type returned}
    H --> I[query_param\ne.g. ?uid=123]
    H --> J[path_regex\ne.g. /event/slug/]
    H --> K[path_depth\ne.g. /posts/title/]
    H --> L[base36\ne.g. /comments/abc123/]
    H --> M[utm_source\ne.g. ?utm_source=mlh]
    I & J & K & L & M --> N[Store in Watch.post_url_pattern]
    N --> O[fetch_listing applies _matches_pattern filter]
    O --> P{results == 0?}
    P -->|yes| Q[_fallback_filter\nheuristic id params + path depth]
    P -->|no| R[baseline_post_ids saved to Firestore]
```

**Pattern types:**

| Type          | Match logic                       | Example                               |
| ------------- | --------------------------------- | ------------------------------------- |
| `query_param` | Presence of a specific query key  | `?uid=935922`                         |
| `path_regex`  | Path matches a regex              | `/event/[^/]+/`                       |
| `path_depth`  | Path deeper than listing URL      | `/scholarships/stem-2025`             |
| `base36`      | Segment after a keyword is base36 | `/comments/abc123/`                   |
| `utm_source`  | `utm_source` param equals a value | `?utm_source=mlh&utm_campaign=events` |

## ELSER Semantic Search

The `body` field is mapped as `semantic_text` in Elasticsearch. When a document is indexed, Elastic Cloud automatically runs ELSER to generate sparse vector embeddings. No external embedding step is required.

At search time, the Gemini agent (via Elastic Agent Builder MCP) selects the most appropriate query type:

| Criteria language / content      | Query                | Reason                         |
| -------------------------------- | -------------------- | ------------------------------ |
| Korean criteria, English content | `semantic`           | ELSER bridges the language gap |
| Same language, specific values   | `match`              | Exact keyword matching         |
| Mixed                            | `bool` with `should` | Combines both                  |

The `semantic` query uses ELSER's learned semantic space. Korean input "페더럴웨이" will match English content "Federal Way" because ELSER learns cross-lingual semantic relationships.

## Firestore–Elasticsearch Sync

| Event                        | Firestore                                     | Elasticsearch                               |
| ---------------------------- | --------------------------------------------- | ------------------------------------------- |
| `create_watch`               | Save Watch doc with baseline                  | —                                           |
| `scan` (each new post)       | —                                             | PUT `sievy_posts/_doc/{watch_id}_{post_id}` |
| `scan` completed (no errors) | Update `baseline_post_ids`, `last_scanned_at` | —                                           |
| `delete watch`               | Delete Watch → cascade delete Alerts          | `delete_by_query` on `watch_id`             |

Baseline and Elasticsearch index are independent stores. If a scan fails with errors, the baseline is not updated — the same posts will be processed again on the next scan.
