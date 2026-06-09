# ADR-0003: Use Elasticsearch semantic_text + ELSER over Keyword Search

**Status:** Accepted
**Date:** 2026-05

## Context

Sievy users write criteria in their native language (often Korean), while post content is frequently in English or mixed Korean-English. Keyword matching fails in this scenario: "페더럴웨이" does not match "Federal Way". Semantic search is required to bridge language and phrasing gaps.

Additionally, the hackathon requires demonstrating meaningful use of Elasticsearch beyond simple keyword search.

## Decision

Use Elastic Cloud Serverless with `semantic_text` field type for the `body` field. ELSER (Elastic Learned Sparse Encoder) is automatically applied on index, generating sparse vector embeddings without any external model deployment or explicit embedding step.

At search time, the Gemini agent (via Elastic Agent Builder MCP) selects the most appropriate query type: `semantic` for meaning-based and cross-language matching, `match` for exact keyword matching, or `bool` with `should` for combined matching.

## Alternatives Considered

| Option                                        | Reason rejected                                                                                            |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Standard Elasticsearch `match` query          | Fails on cross-language criteria. No semantic expansion.                                                   |
| External embedding model (OpenAI, Gemini)     | Requires embedding at both index time and query time. Additional API cost, latency, and infrastructure.    |
| Local Docker Elasticsearch with nori analyzer | Korean tokenization only. Does not solve the cross-language problem.                                       |
| Pinecone or other vector database             | Additional infrastructure layer. Elastic already provides storage, search, and MCP in one managed service. |

## Consequences

**Accepted tradeoffs:**

- `semantic_text` field type is only available on Elastic Cloud Serverless. Local Docker Elasticsearch 9.x does not support it. Full semantic search requires Elastic Cloud.
- ELSER embedding is generated asynchronously after index. There may be a brief window where a newly indexed document is not yet searchable via `semantic` query.
- Gemini is instructed to select the query type, which introduces non-determinism.

**Benefits:**

- Zero embedding infrastructure. ELSER runs fully managed within Elastic Cloud.
- Cross-language semantic matching out of the box. Korean criteria matches English content.
- Single service for storage, semantic search, and MCP interface.
