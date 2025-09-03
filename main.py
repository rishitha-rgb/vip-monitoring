# backend/app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.monitoring_service import start_monitoring, get_alerts, get_posts
from app.models.schemas import Post
import asyncio

app = FastAPI(
    title="VIP Threat & Misinformation Monitoring",
    description="API backend for monitoring threats and misinformation about VIPs.",
    version="1.0.0"
)

# Allow frontend access (CORS)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Startup event
# ------------------------
@app.on_event("startup")
async def startup_event():
    """
    Start the monitoring service when backend launches.
    This will continuously run scrapers and detection in background.
    """
    loop = asyncio.get_event_loop()
    loop.create_task(start_monitoring())  # Non-blocking background task


# ------------------------
# API Endpoints
# ------------------------

@app.get("/")
def root():
    return {"message": "VIP Threat Monitoring Backend is Running"}


@app.get("/alerts")
async def read_alerts():
    """
    Returns high-risk alerts detected by the system
    """
    try:
        alerts = await get_alerts()
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/posts")
async def read_posts():
    """
    Returns all monitored posts (VIP mentions) with risk scores
    """
    try:
        posts = await get_posts()
        return {"posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

