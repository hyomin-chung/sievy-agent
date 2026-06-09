from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import watches, alerts
from config import FRONTEND_URL
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logging.basicConfig(level=logging.INFO)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from agents.pipeline import scan
    from store.watch_store import WatchStore

    async def run_all_scans():
        watch_store = WatchStore()
        watches_list = watch_store.list_all_active()
        for watch in watches_list:
            try:
                await scan(watch.watch_id)
                logging.info(f"Scheduled scan completed: {watch.watch_id}")
            except Exception as e:
                logging.error(f"Scheduled scan failed for {watch.watch_id}: {e}")

    scheduler.add_job(
        run_all_scans,
        trigger="interval",
        hours=1,
        id="hourly_scan",
        replace_existing=True,
    )
    scheduler.start()
    logging.info("Scheduler started: hourly scan enabled")

    yield

    scheduler.shutdown()
    logging.info("Scheduler stopped")


app = FastAPI(title="Sievy API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "https://sievy-agent.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(watches.router)
app.include_router(alerts.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
