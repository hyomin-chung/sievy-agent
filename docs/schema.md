# Schema Reference

## Firestore

### Collection: `watches`

| Field               | Type              | Required | Description                                                                                                                                                 |
| ------------------- | ----------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `watch_id`          | string            | Yes      | UUID v4, primary key                                                                                                                                        |
| `user_id`           | string            | Yes      | Firebase Auth UID                                                                                                                                           |
| `source_url`        | string            | Yes      | Full URL of the listing page                                                                                                                                |
| `category`          | string            | Yes      | One of: `housing`, `opportunity`, `events`, `recruiting`, `audition`, `other`                                                                               |
| `criteria`          | map               | Yes      | Arbitrary key-value pairs. Special key `description` holds free-text criteria. All other keys are structured criteria fields (e.g. `location`, `max_rent`). |
| `note`              | string            | No       | Short user memo to distinguish watches of the same category                                                                                                 |
| `post_url_pattern`  | map               | Yes      | Detected URL pattern. See pattern types below.                                                                                                              |
| `baseline_post_ids` | array\<string\>   | Yes      | Post IDs seen at create_watch time, extended after each successful scan                                                                                     |
| `status`            | string            | Yes      | `active` or `paused`                                                                                                                                        |
| `last_scanned_at`   | timestamp \| null | No       | Updated after each successful scan (no errors). Null until first scan.                                                                                      |
| `created_at`        | timestamp         | Yes      | Watch creation time (UTC)                                                                                                                                   |

**`post_url_pattern` shapes:**

```json
{ "type": "query_param", "key": "uid" }
{ "type": "path_regex", "pattern": "/event/[^/]+/" }
{ "type": "path_depth", "min_depth": 2 }
{ "type": "base36", "segment": "comments" }
{ "type": "utm_source", "value": "mlh", "campaign": "events" }
```

**Example document:**

```json
{
  "watch_id": "a84fafa3-1fd6-4891-bf56-2702bbd27e98",
  "user_id": "Xk9mQ3rTpLvWuYnBcDfGhJ2sE5iA",
  "source_url": "https://www.myballard.com/events/",
  "category": "events",
  "criteria": {
    "type": "free",
    "location": "Ballard",
    "description": "family-friendly outdoor events on weekends"
  },
  "note": "MyBallard weekend events",
  "post_url_pattern": { "type": "path_regex", "pattern": "/event/[^/]+/" },
  "baseline_post_ids": [
    "moomins-sea-adventures",
    "rosemaling-with-marilyn-hansen"
  ],
  "status": "active",
  "last_scanned_at": "2026-06-07T22:30:10Z",
  "created_at": "2026-06-06T07:39:04Z"
}
```

### Collection: `alerts`

| Field              | Type      | Required | Description                                                                                             |
| ------------------ | --------- | -------- | ------------------------------------------------------------------------------------------------------- |
| `alert_id`         | string    | Yes      | UUID v4, primary key                                                                                    |
| `watch_id`         | string    | Yes      | Parent watch ID                                                                                         |
| `user_id`          | string    | Yes      | Firebase Auth UID                                                                                       |
| `post_id`          | string    | Yes      | Post identifier extracted from URL                                                                      |
| `post_url`         | string    | Yes      | Full URL of the matched post                                                                            |
| `title`            | string    | Yes      | Short title derived from post body by Gemini                                                            |
| `verdict`          | string    | Yes      | `worth_checking` or `needs_checking`                                                                    |
| `extracted_fields` | map       | Yes      | Criteria-relevant fields extracted from body. Excludes internal metadata (post_id, post_url, watch_id). |
| `summary`          | string    | Yes      | One-sentence explanation of why the post matches                                                        |
| `is_read`          | boolean   | Yes      | Whether the user has opened this alert. Default: `false`.                                               |
| `created_at`       | timestamp | Yes      | Alert creation time (UTC)                                                                               |

**Verdict definitions:**

| Verdict          | Meaning                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------- |
| `worth_checking` | All key criteria clearly present and matching in the post body                            |
| `needs_checking` | Related to the criteria but some information is missing, vague, or only partially matches |

**Example document:**

```json
{
  "alert_id": "7f3a1b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "watch_id": "a84fafa3-1fd6-4891-bf56-2702bbd27e98",
  "user_id": "Xk9mQ3rTpLvWuYnBcDfGhJ2sE5iA",
  "post_id": "phinneywood-pride-rainbow-hop",
  "post_url": "https://www.myballard.com/event/phinneywood-pride-rainbow-hop/",
  "title": "PhinneyWood Pride Rainbow Hop",
  "verdict": "worth_checking",
  "extracted_fields": {
    "type": "free",
    "location": "PhinneyWood / Ballard",
    "date": "Saturday June 6"
  },
  "summary": "Free outdoor community event in the Ballard area on a Saturday, matching all criteria.",
  "is_read": false,
  "created_at": "2026-06-07T22:35:00Z"
}
```

## Elasticsearch

### Index: `sievy_posts`

Index name: configured via `ELASTIC_INDEX_NAME` env var. Default: `sievy_posts`.

Document ID format: `{watch_id}_{post_id}`

| Field        | Type            | Description                                                                                                                                                      |
| ------------ | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `post_id`    | `keyword`       | Post identifier extracted from URL                                                                                                                               |
| `watch_id`   | `keyword`       | Parent watch ID. Used as primary filter in all queries.                                                                                                          |
| `post_url`   | `keyword`       | Full URL of the post                                                                                                                                             |
| `title`      | `text`          | Post title. May be empty if not available on the listing page.                                                                                                   |
| `body`       | `semantic_text` | Full post body in markdown format. ELSER automatically generates sparse vector embeddings on index. Supports both `semantic` and `match` queries at search time. |
| `category`   | `keyword`       | Watch category at time of indexing                                                                                                                               |
| `crawled_at` | `date`          | ISO 8601 UTC timestamp of when the document was indexed                                                                                                          |

**Mapping (auto-created on first index):**

```json
{
  "mappings": {
    "properties": {
      "post_id": { "type": "keyword" },
      "watch_id": { "type": "keyword" },
      "post_url": { "type": "keyword" },
      "title": { "type": "text" },
      "body": { "type": "semantic_text" },
      "category": { "type": "keyword" },
      "crawled_at": { "type": "date" }
    }
  }
}
```

**Example document:**

```json
{
  "post_id": "phinneywood-pride-rainbow-hop",
  "watch_id": "a84fafa3-1fd6-4891-bf56-2702bbd27e98",
  "post_url": "https://www.myballard.com/event/phinneywood-pride-rainbow-hop/",
  "title": "PhinneyWood Pride Rainbow Hop",
  "body": "## PhinneyWood Pride Rainbow Hop\n\nThis Pride event celebrates finding oneself and encourages inclusivity...\n\nfree!\n\nSaturday June 6",
  "category": "events",
  "crawled_at": "2026-06-07T22:30:10.087291+00:00"
}
```

**Notes:**

- `semantic_text` is only available on Elastic Cloud Serverless. Local Docker Elasticsearch 9.x does not support this type.
- ELSER embedding is generated automatically on PUT. No additional inference call is needed at index time.
- At search time, the Gemini agent via MCP chooses between `semantic` (meaning-based, cross-language) and `match` (exact keyword) queries depending on the criteria.
