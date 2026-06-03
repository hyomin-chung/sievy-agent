from fastapi import APIRouter, Header, HTTPException
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


@router.get("")
async def list_alerts_endpoint(
    x_user_id: str = Header(...),
) -> list[AlertResponse]:
    alert_store = AlertStore()
    alerts = alert_store.list_by_user(x_user_id)
    return [
        AlertResponse(
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
        for a in alerts
    ]


@router.get("/{alert_id}")
async def get_alert_endpoint(
    alert_id: str,
    x_user_id: str = Header(...),
) -> AlertResponse:
    alert_store = AlertStore()
    alerts = alert_store.list_by_user(x_user_id)
    alert = next((a for a in alerts if a.alert_id == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse(
        alert_id=alert.alert_id,
        watch_id=alert.watch_id,
        user_id=alert.user_id,
        post_id=alert.post_id,
        post_url=alert.post_url,
        title=alert.title,
        verdict=alert.verdict,
        extracted_fields=alert.extracted_fields,
        summary=alert.summary,
        is_read=alert.is_read,
        created_at=alert.created_at,
    )


@router.patch("/{alert_id}/read", status_code=204)
async def mark_alert_read_endpoint(
    alert_id: str,
    x_user_id: str = Header(...),
) -> None:
    alert_store = AlertStore()
    alerts = alert_store.list_by_user(x_user_id)
    alert = next((a for a in alerts if a.alert_id == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert_store.mark_as_read(alert_id)
