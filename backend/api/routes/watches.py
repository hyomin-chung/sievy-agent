from datetime import datetime
from typing import Any
import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel

from agents.pipeline import create_watch, scan
from store.watch_store import WatchStore
from store.alert_store import AlertStore

router = APIRouter(prefix="/watches", tags=["watches"])
logger = logging.getLogger(__name__)


class CreateWatchRequest(BaseModel):
    source_url: str
    category: str
    criteria: dict[str, Any]
    note: str = ""


class WatchResponse(BaseModel):
    watch_id: str
    user_id: str
    source_url: str
    category: str
    criteria: dict
    baseline_post_ids: list[str]
    status: str = "active"
    created_at: datetime | None = None
    last_scanned_at: datetime | None = None
    note: str = ""


async def _run_scan(watch_id: str) -> None:
    try:
        result = await scan(watch_id)
        logger.info(f"Scan completed: {result}")
    except Exception as e:
        logger.error(f"Scan error for watch {watch_id}: {e}", exc_info=True)


def _get_watch_store() -> WatchStore:
    return WatchStore()


def _to_response(w) -> WatchResponse:
    return WatchResponse(
        watch_id=w.watch_id,
        user_id=w.user_id,
        source_url=w.source_url,
        category=w.category,
        criteria=w.criteria,
        baseline_post_ids=w.baseline_post_ids,
        status=w.status,
        created_at=w.created_at,
        last_scanned_at=w.last_scanned_at,
        note=w.note,
    )


@router.post("", status_code=201)
async def create_watch_endpoint(
    body: CreateWatchRequest,
    x_user_id: str = Header(...),
) -> WatchResponse:
    watch = await create_watch(
        user_id=x_user_id,
        source_url=body.source_url,
        category=body.category,
        criteria=body.criteria,
        note=body.note,
    )
    return _to_response(watch)


@router.get("")
async def list_watches_endpoint(
    x_user_id: str = Header(...),
) -> list[WatchResponse]:
    watches = _get_watch_store().list_by_user(x_user_id)
    watches.sort(key=lambda w: w.last_scanned_at or w.created_at, reverse=True)
    return [_to_response(w) for w in watches]


@router.get("/{watch_id}")
async def get_watch_endpoint(
    watch_id: str,
    x_user_id: str = Header(...),
) -> WatchResponse:
    watch = _get_watch_store().get(watch_id)
    if not watch or watch.user_id != x_user_id:
        raise HTTPException(status_code=404, detail="Watch not found")
    return _to_response(watch)


@router.delete("/{watch_id}", status_code=204)
async def delete_watch_endpoint(
    watch_id: str,
    x_user_id: str = Header(...),
) -> None:
    store = _get_watch_store()
    watch = store.get(watch_id)
    if not watch or watch.user_id != x_user_id:
        raise HTTPException(status_code=404, detail="Watch not found")
    AlertStore().delete_by_watch(watch_id)
    store.delete(watch_id)


@router.patch("/{watch_id}/status")
async def update_watch_status(
    watch_id: str,
    body: dict,
    x_user_id: str = Header(...),
):
    store = _get_watch_store()
    watch = store.get(watch_id)
    if not watch or watch.user_id != x_user_id:
        raise HTTPException(status_code=404, detail="Watch not found")
    status = body.get("status")
    if status not in ("active", "paused"):
        raise HTTPException(status_code=400, detail="Invalid status")
    store.update_status(watch_id, status)
    return {"status": status}


@router.post("/{watch_id}/scan")
async def scan_endpoint(
    watch_id: str,
    background_tasks: BackgroundTasks,
    x_user_id: str = Header(...),
) -> dict:
    watch = _get_watch_store().get(watch_id)
    if not watch or watch.user_id != x_user_id:
        raise HTTPException(status_code=404, detail="Watch not found")
    background_tasks.add_task(_run_scan, watch_id)
    return {"status": "scan started", "watch_id": watch_id}
