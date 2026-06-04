from typing import Any
import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel

from agents.pipeline import create_watch, scan
from store.watch_store import WatchStore

router = APIRouter(prefix="/watches", tags=["watches"])

logger = logging.getLogger(__name__)


class CreateWatchRequest(BaseModel):
    source_url: str
    category: str
    criteria: dict[str, Any]


class WatchResponse(BaseModel):
    watch_id: str
    user_id: str
    source_url: str
    category: str
    criteria: dict[str, Any]
    baseline_post_ids: list[str]


async def _run_scan(watch_id: str) -> None:
    try:
        result = await scan(watch_id)
        logger.info(f"Scan completed: {result}")
    except Exception as e:
        logger.error(f"Scan error for watch {watch_id}: {e}", exc_info=True)


def _get_watch_store() -> WatchStore:
    return WatchStore()


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
    )
    return WatchResponse(
        watch_id=watch.watch_id,
        user_id=watch.user_id,
        source_url=watch.source_url,
        category=watch.category,
        criteria=watch.criteria,
        baseline_post_ids=watch.baseline_post_ids,
    )


@router.get("")
async def list_watches_endpoint(
    x_user_id: str = Header(...),
) -> list[WatchResponse]:
    watch_store = _get_watch_store()
    watches = watch_store.list_by_user(x_user_id)
    return [
        WatchResponse(
            watch_id=w.watch_id,
            user_id=w.user_id,
            source_url=w.source_url,
            category=w.category,
            criteria=w.criteria,
            baseline_post_ids=w.baseline_post_ids,
        )
        for w in watches
    ]


@router.get("/{watch_id}")
async def get_watch_endpoint(
    watch_id: str,
    x_user_id: str = Header(...),
) -> WatchResponse:
    watch_store = _get_watch_store()
    watch = watch_store.get(watch_id)
    if not watch or watch.user_id != x_user_id:
        raise HTTPException(status_code=404, detail="Watch not found")
    return WatchResponse(
        watch_id=watch.watch_id,
        user_id=watch.user_id,
        source_url=watch.source_url,
        category=watch.category,
        criteria=watch.criteria,
        baseline_post_ids=watch.baseline_post_ids,
    )


@router.delete("/{watch_id}", status_code=204)
async def delete_watch_endpoint(
    watch_id: str,
    x_user_id: str = Header(...),
) -> None:
    watch_store = _get_watch_store()
    watch = watch_store.get(watch_id)
    if not watch or watch.user_id != x_user_id:
        raise HTTPException(status_code=404, detail="Watch not found")
    watch_store.db.collection("watches").document(watch_id).delete()


@router.post("/{watch_id}/scan")
async def scan_endpoint(
    watch_id: str,
    background_tasks: BackgroundTasks,
    x_user_id: str = Header(...),
) -> dict:
    watch_store = _get_watch_store()
    watch = watch_store.get(watch_id)
    if not watch or watch.user_id != x_user_id:
        raise HTTPException(status_code=404, detail="Watch not found")

    background_tasks.add_task(_run_scan, watch_id)
    return {"status": "scan started", "watch_id": watch_id}
