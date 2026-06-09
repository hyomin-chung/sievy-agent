import uuid
from datetime import datetime, timezone

from store.firestore_client import get_firestore_client
from schemas.watch import Watch

COLLECTION = "watches"


class WatchStore:
    def __init__(self):
        self.db = get_firestore_client()

    def save(self, watch: Watch) -> Watch:
        if not watch.watch_id:
            watch.watch_id = str(uuid.uuid4())
        doc_ref = self.db.collection(COLLECTION).document(watch.watch_id)
        doc_ref.set(watch.to_dict())
        return watch

    def get(self, watch_id: str) -> Watch | None:
        doc = self.db.collection(COLLECTION).document(watch_id).get()
        if not doc.exists:
            return None
        return Watch.from_dict(doc.to_dict())

    def update_baseline(self, watch_id: str, baseline_post_ids: list[str]) -> None:
        self.db.collection(COLLECTION).document(watch_id).update(
            {
                "baseline_post_ids": baseline_post_ids,
                "last_scanned_at": datetime.now(timezone.utc),
            }
        )

    def list_by_user(self, user_id: str) -> list[Watch]:
        docs = self.db.collection(COLLECTION).where("user_id", "==", user_id).stream()
        return [Watch.from_dict(doc.to_dict()) for doc in docs]

    def update_status(self, watch_id: str, status: str) -> None:
        self.db.collection(COLLECTION).document(watch_id).update({"status": status})

    def delete(self, watch_id: str) -> None:
        self.db.collection(COLLECTION).document(watch_id).delete()

    def list_all_active(self) -> list[Watch]:
        docs = self.db.collection(COLLECTION).where("status", "==", "active").stream()
        return [self._to_watch(doc) for doc in docs]
