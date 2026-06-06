from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel
from typing import Any
from datetime import datetime

from store.alert_store import AlertStore

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertResponse(BaseModel):
    alert_id: str
    watch_id: str
    user_id: str
    post_id: str
    post_url: str
    title: str
    verdict: str
    extracted_fields: dict[str, Any]
    summary: str
    is_read: bool
    created_at: datetime


def _to_alert_response(a) -> AlertResponse:
    return AlertResponse(
        alert_id=a.alert_id,
        watch_id=a.watch_id,
        user_id=a.user_id,
        post_id=a.post_id,
        post_url=a.post_url,
        title=a.title,
        verdict=a.verdict,
        extracted_fields=a.extracted_fields,
        summary=a.summary,
        is_read=a.is_read,
        created_at=a.created_at,
    )


@router.get("")
async def list_alerts(
    x_user_id: str = Header(...),
    watch_id: str | None = Query(None),
) -> list[AlertResponse]:
    store = AlertStore()
    if watch_id:
        alerts = store.list_by_watch(watch_id)
        alerts = [a for a in alerts if a.user_id == x_user_id]
    else:
        alerts = store.list_by_user(x_user_id)
    return [_to_alert_response(a) for a in alerts]


@router.get("/{alert_id}")
async def get_alert_endpoint(
    alert_id: str,
    x_user_id: str = Header(...),
) -> AlertResponse:
    store = AlertStore()
    alerts = store.list_by_user(x_user_id)
    alert = next((a for a in alerts if a.alert_id == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _to_alert_response(alert)


@router.patch("/{alert_id}/read", status_code=204)
async def mark_alert_read_endpoint(
    alert_id: str,
    x_user_id: str = Header(...),
) -> None:
    store = AlertStore()
    alerts = store.list_by_user(x_user_id)
    alert = next((a for a in alerts if a.alert_id == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    store.mark_as_read(alert_id)
