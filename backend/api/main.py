from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import watches, alerts
from config import FRONTEND_URL
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from agents.pipeline import scan
    from store.watch_store import WatchStore

    def run_all_scans():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            watch_store = WatchStore()
            watches_list = watch_store.list_all_active()
            for watch in watches_list:
                try:
                    loop.run_until_complete(scan(watch.watch_id))
                    logging.info(f"Scheduled scan completed: {watch.watch_id}")
                except Exception as e:
                    logging.error(f"Scheduled scan failed for {watch.watch_id}: {e}")
        finally:
            loop.close()

    scheduler.add_job(
        run_all_scans,
        trigger="interval",
        hours=1,
        id="hourly_scan",
        replace_existing=True,
        next_run_time=datetime.now() + timedelta(hours=1),
    )
    scheduler.start()
    logging.info("Scheduler started: first scan in 1 hour")

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
