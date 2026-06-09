# ADR-0004: Use Elastic Agent Builder MCP over Deprecated MCP Server

**Status:** Accepted
**Date:** 2026-06

## Context

The hackathon requires demonstrating MCP (Model Context Protocol) integration with Elasticsearch. Two Elastic MCP options exist:

1. `docker.elastic.co/mcp/elasticsearch` — the original Docker image, now officially deprecated
2. Elastic Agent Builder MCP — a Kibana-native MCP endpoint available on Elastic Cloud Serverless

Both expose the same core tools: `search`, `list_indices`, `get_mappings`, `esql`, `get_shards`.

## Decision

Use the Elastic Agent Builder MCP endpoint exposed via Kibana (`{KIBANA_URL}/api/agent_builder/mcp`). Authentication is via a Kibana API key with `feature_agentBuilder.read` and `feature_actions.read` application privileges. Connection uses `StreamableHTTPConnectionParams` via Google ADK's `MCPToolset`.

## Alternatives Considered

| Option                                             | Reason rejected                                                                                                                                                                                     |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docker.elastic.co/mcp/elasticsearch` (deprecated) | Officially deprecated with no future feature updates. `ES_API_KEY` environment variable did not propagate correctly from Docker Compose `env_file`, causing persistent 401 authentication failures. |
| Custom MCP server                                  | Builds MCP protocol from scratch. Unnecessary given Elastic provides a production-ready managed MCP server.                                                                                         |

## Consequences

**Accepted tradeoffs:**

- Requires two separate API keys: one for direct Elasticsearch access (read/write, for indexing), one for the Agent Builder MCP (Kibana privileges, for search). Key management is more complex.
- Agent Builder MCP requires Kibana application privileges (`kibana-.kibana` application, `feature_agentBuilder.read`). Standard Elasticsearch API keys do not have these privileges.
- Local `elastic-mcp` Docker service removed from `docker-compose.yml`. Local development must connect to Elastic Cloud for MCP-based search.

**Benefits:**

- Officially supported and actively maintained.
- Kibana-native: no Docker service required.
- Compatible with Google Cloud's Elastic partnership referenced in the hackathon documentation.
- Negotiates `2025-11-25` MCP protocol version, the latest available.
