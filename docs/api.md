# API Reference

## Authentication

All endpoints require a Firebase Auth UID passed as a request header.

```
X-User-Id: <firebase_uid>
```

The frontend sends this header automatically after Google OAuth sign-in. The backend does not verify the Firebase ID token — it trusts the UID value directly. This is a known limitation for the hackathon prototype.

**Base URL:** `http://localhost:8000` (development)

## Watches

### `GET /watches`

Returns all watches owned by the authenticated user, sorted by `last_scanned_at` descending (fallback: `created_at` descending).

**Response 200:**

```json
[
  {
    "watch_id": "a84fafa3-1fd6-4891-bf56-2702bbd27e98",
    "user_id": "Xk9mQ3rTpLvWuYnBcDfGhJ2sE5iA",
    "source_url": "https://www.myballard.com/events/",
    "category": "events",
    "criteria": { "type": "free", "location": "Ballard" },
    "note": "MyBallard weekend events",
    "post_url_pattern": { "type": "path_regex", "pattern": "/event/[^/]+/" },
    "baseline_post_ids": ["moomins-sea-adventures"],
    "status": "active",
    "last_scanned_at": "2026-06-07T22:30:10Z",
    "created_at": "2026-06-06T07:39:04Z"
  }
]
```

### `POST /watches`

Creates a new watch. Triggers URL pattern detection via Gemini and baseline creation via Firecrawl. Takes 5–15 seconds depending on the site.

**Request body:**

```json
{
  "source_url": "https://www.myballard.com/events/",
  "category": "events",
  "criteria": {
    "type": "free",
    "location": "Ballard",
    "description": "family-friendly outdoor events on weekends"
  },
  "note": "MyBallard weekend events"
}
```

**Response 200:** Full Watch object

**Errors:**

- `400` — invalid `source_url`, Firecrawl failure, or site not supported

### `GET /watches/{watch_id}`

Returns a single watch by ID.

**Response 200:** Watch object
**Response 404:** Watch not found or does not belong to the authenticated user

### `POST /watches/{watch_id}/scan`

Triggers a scan. Returns after the scan completes with the result.

**Response 200:**

```json
{
  "watch_id": "a84fafa3-1fd6-4891-bf56-2702bbd27e98",
  "source_url": "https://www.myballard.com/events/",
  "new_posts_found": 5,
  "alerts_created": 2,
  "errors": []
}
```

`errors` is a list of error strings. If non-empty, `baseline_post_ids` and `last_scanned_at` are not updated.

### `PATCH /watches/{watch_id}/status`

Updates watch status. Paused watches cannot be scanned.

**Request body:**

```json
{ "status": "active | paused" }
```

**Response 204:** No content

### `DELETE /watches/{watch_id}`

Deletes the watch and cascades in order:

1. Delete all Elasticsearch documents for this `watch_id`
2. Delete all Firestore alerts for this `watch_id`
3. Delete the Firestore watch document

**Response 204:** No content
**Response 404:** Watch not found

## Alerts

### `GET /alerts`

Returns alerts for the authenticated user, optionally filtered by watch.

**Query parameters:**

| Param      | Type              | Description                           |
| ---------- | ----------------- | ------------------------------------- |
| `watch_id` | string (optional) | Filter to alerts for a specific watch |

**Response 200:**

```json
[
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
]
```

### `GET /alerts/{alert_id}`

Returns a single alert by ID.

**Response 200:** Alert object
**Response 404:** Alert not found

### `PATCH /alerts/{alert_id}/read`

Marks an alert as read. Called automatically when the user opens AlertDetail.

**Response 204:** No content
**Response 404:** Alert not found

### `DELETE /alerts/{alert_id}`

Deletes a single alert.

**Response 204:** No content
**Response 404:** Alert not found
