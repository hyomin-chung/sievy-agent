import firebase_admin
from firebase_admin import credentials, firestore
from config import GOOGLE_APPLICATION_CREDENTIALS, FIREBASE_PROJECT_ID
import os

_db = None


def get_firestore_client():
    global _db
    if _db is None:
        if not firebase_admin._apps:
            if os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
                cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
                firebase_admin.initialize_app(cred, {"projectId": FIREBASE_PROJECT_ID})
            else:
                firebase_admin.initialize_app(
                    options={"projectId": FIREBASE_PROJECT_ID}
                )
        _db = firestore.client()
    return _db
