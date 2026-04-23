from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend import state
from src.backend.services.demo_runner import DemoRunner

app = FastAPI(title="Water Multi-Agent Backend", version="0.1.0")
@app.get("/")
def root():
    return {
        "message": "Water Multi-Agent Backend is running.",
        "docs": "/docs",
        "health": "/health",
        "latest": "/dashboard/latest",
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runner = DemoRunner()


@app.get("/health")
def health():
    return {"status": "ok", "demo_running": state.DEMO_RUNNING}


@app.get("/dashboard/latest")
def dashboard_latest():
    if not state.LATEST_RESULT:
        return {
            "message": "No result yet. Start demo first.",
            "demo_running": state.DEMO_RUNNING,
        }
    return state.LATEST_RESULT


@app.get("/dashboard/history")
def dashboard_history():
    return {
        "items": state.HISTORY[-50:],
        "count": len(state.HISTORY),
    }


@app.post("/demo/start")
def demo_start():
    started = runner.start(speed_seconds=1.0)
    return {"started": started, "demo_running": state.DEMO_RUNNING}


@app.post("/demo/stop")
def demo_stop():
    runner.stop()
    return {"stopped": True, "demo_running": state.DEMO_RUNNING}