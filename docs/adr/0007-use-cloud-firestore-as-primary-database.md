# ADR-0007: Use Cloud Firestore as Primary Database

**Status:** Accepted
**Date:** 2026-04

## Context

Sievy needs to persist watches and alerts. Both have variable-shape fields: `criteria` and `extracted_fields` are arbitrary key-value maps. Requirements include no schema migrations during rapid iteration, Firebase Auth UID as the primary access control dimension, and low operational overhead for a hackathon-scale project.

## Decision

Use Cloud Firestore (Native mode) as the sole application database. Two top-level collections: `watches` and `alerts`.

## Alternatives Considered

| Option                     | Reason rejected                                                                                                                         |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| PostgreSQL (Cloud SQL)     | Requires schema management, migrations, and connection pooling. Variable-shape fields require JSONB columns. Additional setup overhead. |
| Firebase Realtime Database | Older product. Firestore Native mode is preferred for new projects and has better query capabilities.                                   |
| SQLite                     | Not suitable for multi-user cloud deployment.                                                                                           |
| MongoDB Atlas              | Additional cloud account and infrastructure. Firestore integrates directly with Firebase Auth.                                          |

## Consequences

**Accepted tradeoffs:**

- No complex queries (joins, aggregations). All filtering is done in Python after fetching by `user_id` or `watch_id`.
- Firestore's `where()` with positional arguments produces deprecation warnings. The `filter=` keyword argument syntax should be adopted in future updates.
- `baseline_post_ids` is stored as an array field in the Watch document. At ~100 bytes per post ID, a document with 10,000 baseline IDs would approach Firestore's 1MB document size limit. Not a current concern but becomes relevant for long-running watches on high-volume sites.
- Cascade deletion of alerts when a watch is deleted must be implemented explicitly in application code. Firestore does not enforce foreign key constraints.

**Benefits:**

- Document model matches the application's data shape exactly. No ORM or schema mapping needed.
- Native Firebase Auth integration. UID-based access control is straightforward.
- Managed infrastructure. No database administration.
- Free tier covers hackathon usage volume.
