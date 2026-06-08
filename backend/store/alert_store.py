import uuid

from store.firestore_client import get_firestore_client
from schemas.alert import Alert

COLLECTION = "alerts"


class AlertStore:
    def __init__(self):
        self.db = get_firestore_client()

    def save(self, alert: Alert) -> Alert:
        if not alert.alert_id:
            alert.alert_id = str(uuid.uuid4())
        doc_ref = self.db.collection(COLLECTION).document(alert.alert_id)
        doc_ref.set(alert.to_dict())
        return alert

    def list_by_watch(self, watch_id: str) -> list[Alert]:
        docs = (
            self.db.collection(COLLECTION)
            .where("watch_id", "==", watch_id)
            .order_by("created_at", direction="DESCENDING")
            .stream()
        )
        return [Alert.from_dict(doc.to_dict()) for doc in docs]

    def list_by_user(self, user_id: str) -> list[Alert]:
        docs = (
            self.db.collection(COLLECTION)
            .where("user_id", "==", user_id)
            .order_by("created_at", direction="DESCENDING")
            .stream()
        )
        return [Alert.from_dict(doc.to_dict()) for doc in docs]

    def mark_as_read(self, alert_id: str) -> None:
        self.db.collection(COLLECTION).document(alert_id).update(
            {
                "is_read": True,
            }
        )

    def delete_by_watch(self, watch_id: str) -> None:
        docs = self.db.collection(COLLECTION).where("watch_id", "==", watch_id).stream()
        for doc in docs:
            doc.reference.delete()

    def delete(self, alert_id: str) -> None:
        self.db.collection(COLLECTION).document(alert_id).delete()
