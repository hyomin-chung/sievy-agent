from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import watches, alerts
from config import FRONTEND_URL
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Sievy API")

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
