# ADR-0008: Use Firebase Auth with Google OAuth

**Status:** Accepted
**Date:** 2026-04

## Context

Sievy is a mobile-first PWA where users need to persist their watches and alerts across sessions. Authentication must be low-friction, work reliably on mobile browsers, integrate with Firestore, and require minimal backend implementation.

## Decision

Use Firebase Authentication with Google OAuth as the sole sign-in provider. After sign-in, the Firebase UID is extracted from the Firebase Auth user object on the client and passed to the backend as the `X-User-Id` header on every request. All Firestore queries filter by this UID to enforce data isolation.

## Alternatives Considered

| Option                | Reason rejected                                                                    |
| --------------------- | ---------------------------------------------------------------------------------- |
| Email + password      | Higher friction. Requires password reset flow. More implementation surface area.   |
| JWT-based custom auth | Requires key management, token issuance, and refresh logic. Firebase handles this. |
| Session cookies       | Not suitable for a PWA that may run across multiple browser contexts.              |
| No auth (anonymous)   | Watches and alerts cannot be persisted per-user.                                   |
| GitHub OAuth          | Less universal. Not all target users have GitHub accounts.                         |

## Consequences

**Accepted tradeoffs:**

- The backend does not verify the Firebase ID token on each request. It trusts the `X-User-Id` header value directly. This is a known security limitation for the hackathon prototype. In production, the backend should verify the token with Firebase Admin SDK on every request.
- All data isolation relies on application-level `user_id` filtering in Python. There are no Firestore security rules enforcing this at the database level.
- Users are locked in to Google accounts. Switching to another provider later requires a migration path.

**Benefits:**

- Sign-in is one tap (Google OAuth popup). No friction for new users.
- Firebase Auth handles token refresh, session persistence, and cross-device sync automatically.
- Firebase UID is stable and consistent across sessions and devices.
- Zero backend implementation for auth logic — only UID extraction and header forwarding.
