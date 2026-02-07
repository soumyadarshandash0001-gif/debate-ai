from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from pathlib import Path
from datetime import datetime
import requests
import time
import psutil

from .debate_engine import run_debate_fast

# Data storage
DATA_DIR = Path("/app/data") if Path("/app").exists() else Path.home() / ".trillm_arena"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEBATES_FILE = DATA_DIR / "debates.json"

# Load existing debates
def load_debates():
    if DEBATES_FILE.exists():
        return json.loads(DEBATES_FILE.read_text())
    return []

def save_debate(debate_result: dict):
    debates = load_debates()
    debates.append({
        "timestamp": datetime.now().isoformat(),
        **debate_result
    })
    DEBATES_FILE.write_text(json.dumps(debates, indent=2))

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(
    title="TriLLM Arena API",
    description="Production-grade multi-LLM debate engine",
    version="1.0.0",
)

# Add CORS middleware for Safari & cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Request / Response Schemas
# -----------------------------
class DebateRequest(BaseModel):
    topic: str
    deep_review: Optional[bool] = False


class DebateResponse(BaseModel):
    model_a: dict
    model_b: dict
    fast_verdict: str
    heavy_verdict: Optional[str]
    meta: dict


# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# Run debate
# -----------------------------
@app.post("/debate", response_model=DebateResponse)
def run_debate(req: DebateRequest):
    if not req.topic or len(req.topic.strip()) < 3:
        raise HTTPException(status_code=400, detail="Invalid debate topic")

    try:
        result = run_debate_fast(
            topic=req.topic,
            deep_review=req.deep_review,
        )
        # Save to persistent storage
        save_debate(result)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Debate execution failed: {str(e)}",
        )


# Get all stored debates
@app.get("/debates")
def get_debates():
    return {"debates": load_debates(), "count": len(load_debates())}


# Clear all debates
@app.delete("/debates")
def clear_debates():
    DEBATES_FILE.write_text(json.dumps([]))
    return {"status": "cleared"}


# ===== Model Monitoring =====
OLLAMA_BASE_URL = "http://localhost:11434"

def get_ollama_status() -> Dict[str, Any]:
    """Check if Ollama is running"""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            return {"running": True, "models": resp.json().get("models", [])}
    except:
        pass
    return {"running": False, "models": []}

def get_system_metrics() -> Dict[str, Any]:
    """Get system resource usage"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "memory_gb": psutil.virtual_memory().used / (1024**3),
        "memory_total_gb": psutil.virtual_memory().total / (1024**3),
    }

@app.get("/monitor/models")
def monitor_models():
    """Get Ollama models status"""
    ollama_status = get_ollama_status()
    models = []
    
    if ollama_status["running"] and ollama_status["models"]:
        for model in ollama_status["models"]:
            models.append({
                "name": model.get("name", "unknown"),
                "size_gb": model.get("size", 0) / (1024**3),
                "modified": model.get("modified_at", "unknown"),
            })
    
    return {
        "ollama_running": ollama_status["running"],
        "models_count": len(models),
        "models": models,
    }

@app.get("/monitor/system")
def monitor_system():
    """Get system metrics"""
    return get_system_metrics()

@app.get("/monitor/health")
def monitor_health():
    """Complete health check with all metrics"""
    ollama_status = get_ollama_status()
    system_metrics = get_system_metrics()
    debates_count = len(load_debates())
    
    # Determine overall status
    is_healthy = (
        ollama_status["running"] and 
        system_metrics["cpu_percent"] < 90 and 
        system_metrics["memory_percent"] < 90
    )
    
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy" if is_healthy else "degraded",
        "ollama": {
            "running": ollama_status["running"],
            "models_loaded": len(ollama_status["models"]),
            "models": [m.get("name", "unknown") for m in ollama_status["models"]],
        },
        "system": system_metrics,
        "debates_total": debates_count,
        "api": {
            "version": "1.0.0",
            "endpoints_active": 8,
        }
    }

@app.get("/monitor/debates")
def monitor_debates():
    """Get debate statistics"""
    debates = load_debates()
    
    stats = {
        "total": len(debates),
        "last_7_days": 0,
        "last_24_hours": 0,
        "today": 0,
    }
    
    now = datetime.now()
    for debate in debates:
        try:
            ts = datetime.fromisoformat(debate["timestamp"])
            age_hours = (now - ts).total_seconds() / 3600
            
            if age_hours < 24:
                stats["last_24_hours"] += 1
                if ts.date() == now.date():
                    stats["today"] += 1
            if age_hours < 168:  # 7 days
                stats["last_7_days"] += 1
        except:
            pass
    
    return stats
