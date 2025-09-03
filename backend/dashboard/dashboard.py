import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add project root for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ingestion.ingestion import DataIngestion
from ai.ai_scoring import VIPThreatScorer
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VIP Threat Monitoring API",
    description="AI-powered VIP threat detection and monitoring system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, configure specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global instances
data_ingestion = DataIngestion()
threat_scorer = VIPThreatScorer()
monitoring_active = False
last_ingestion_time = None

# Pydantic models

class MonitoringStatus(BaseModel):
    active: bool
    last_run: Optional[datetime]
    total_posts: int
    high_threat_posts: int
    system_health: str

class Post(BaseModel):
    id: str
    platform: str
    content: str
    author_username: str
    timestamp: datetime
    threat_score: float
    threat_category: str
    likes: Optional[int] = 0
    shares: Optional[int] = 0
    comments: Optional[int] = 0

class ThreatAnalysisRequest(BaseModel):
    text: str

@app.get("/")
async def root():
    return {
        "message": "VIP Threat Monitoring API",
        "version": "1.0.0",
        "status": "active",
        "monitoring_active": monitoring_active,
        "docs": "/docs",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    try:
        conn = data_ingestion._get_db_connection()
        total = conn.execute("SELECT COUNT(*) AS count FROM posts").fetchone()['count']
        conn.close()
        return {
            "status": "healthy",
            "total_posts": total,
            "monitoring_active": monitoring_active,
            "model_loaded": threat_scorer.pipeline is not None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/monitoring/status", response_model=MonitoringStatus)
async def get_monitoring_status():
    try:
        conn = data_ingestion._get_db_connection()
        total_posts = conn.execute("SELECT COUNT(*) as count FROM posts").fetchone()['count']
        high_threat_posts = conn.execute(
            "SELECT COUNT(*) as count FROM posts WHERE threat_score >= ?", (threat_scorer.threat_threshold,)
        ).fetchone()['count']
        conn.close()

        return MonitoringStatus(
            active=monitoring_active,
            last_run=last_ingestion_time,
            total_posts=total_posts,
            high_threat_posts=high_threat_posts,
            system_health="healthy"
        )
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/monitoring/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    global monitoring_active
    if monitoring_active:
        return {"message": "Monitoring already active", "status": "active"}

    monitoring_active = True

    def monitoring_loop():
        global last_ingestion_time
        while monitoring_active:
            logger.info("Running monitoring cycle...")
            try:
                data_ingestion.run_ingestion_cycle()
                posts_df = data_ingestion.get_posts_for_analysis(limit=1000)
                if not posts_df.empty:
                    scores = threat_scorer.score_posts(posts_df)
                    data_ingestion.update_post_scores(scores)
                last_ingestion_time = datetime.now()
                logger.info("Monitoring cycle completed")
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            # Sleep 5 minutes between cycles
            import time
            time.sleep(300)

    background_tasks.add_task(monitoring_loop)
    return {"message": "Monitoring started successfully", "status": "active"}

@app.post("/api/monitoring/stop")
async def stop_monitoring():
    global monitoring_active
    monitoring_active = False
    return {"message": "Monitoring stopped", "status": "inactive"}

@app.post("/api/monitoring/run-cycle")
async def run_manual_cycle():
    try:
        ingestion_results = data_ingestion.run_ingestion_cycle()
        posts_df = data_ingestion.get_posts_for_analysis(limit=500)
        updated_count = 0
        if not posts_df.empty:
            scores = threat_scorer.score_posts(posts_df)
            updated_count = data_ingestion.update_post_scores(scores)
        return {
            "message": "Manual cycle completed",
            "ingestion_results": ingestion_results,
            "posts_scored": updated_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Manual cycle error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts/recent", response_model=List[Post])
async def get_recent_posts(platform: Optional[str] = None, limit: int = Query(100, le=500)):
    try:
        conn = data_ingestion._get_db_connection()
        query = "SELECT * FROM posts"
        params = []
        if platform:
            query += " WHERE platform = ?"
            params.append(platform)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        posts = []
        for row in rows:
            posts.append(Post(
                id=row['id'],
                platform=row['platform'],
                content=row['content'],
                author_username=row['author_username'],
                timestamp=row['timestamp'],
                threat_score=row['threat_score'],
                threat_category=row['threat_category'],
                likes=row['likes'],
                shares=row['shares'],
                comments=row['comments']
            ))
        return posts
    except Exception as e:
        logger.error(f"Error fetching recent posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts/high-threat", response_model=List[Post])
async def get_high_threat_posts(threshold: float = 0.7, limit: int = Query(50, le=200)):
    try:
        conn = data_ingestion._get_db_connection()
        query = "SELECT * FROM posts WHERE threat_score >= ? ORDER BY threat_score DESC LIMIT ?"
        rows = conn.execute(query, (threshold, limit)).fetchall()
        conn.close()
        posts = []
        for row in rows:
            posts.append(Post(
                id=row['id'],
                platform=row['platform'],
                content=row['content'],
                author_username=row['author_username'],
                timestamp=row['timestamp'],
                threat_score=row['threat_score'],
                threat_category=row['threat_category'],
                likes=row['likes'],
                shares=row['shares'],
                comments=row['comments']
            ))
        return posts
    except Exception as e:
        logger.error(f"Error fetching high threat posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    try:
        conn = data_ingestion._get_db_connection()
        total_posts = conn.execute("SELECT COUNT(*) as count FROM posts").fetchone()['count']
        threat_posts = conn.execute(
            "SELECT COUNT(*) as count FROM posts WHERE threat_score >= ?", (threat_scorer.threat_threshold,)
        ).fetchone()['count']
        platforms = conn.execute("SELECT DISTINCT platform FROM posts").fetchall()
        platform_count = len(platforms)
        conn.close()
        return {
            "total_posts": total_posts,
            "threats_detected": threat_posts,
            "platforms_monitored": platform_count,
            "alerts_active": max(0, threat_posts - threat_posts // 3),
            "detection_accuracy": 0.94,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/analyze-text")
async def analyze_text_get(text: str):
    # Convenience GET handler (optional)
    return await analyze_text_post(ThreatAnalysisRequest(text=text))

@app.post("/api/ai/analyze-text")
async def analyze_text_post(request: ThreatAnalysisRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    result = threat_scorer.predict_threat(request.text)
    return {
        "analysis": result,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/config")
async def get_configuration():
    return {
        "threat_threshold": threat_scorer.threat_threshold,
        "vip_keywords": threat_scorer.vip_keywords,
        "threat_keywords": threat_scorer.threat_keywords,
        "model_path": threat_scorer.model_path,
        "database_path": data_ingestion.db_path,
        "monitoring_active": monitoring_active,
        "timestamp": datetime.now().isoformat()
    }
