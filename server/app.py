from fastapi import FastAPI, HTTPException, Body
from .environment import OpenIncidentEnv
from models import ActionEnum, StepResponse, EnvObservation
from typing import Dict, Any, Optional

app = FastAPI(title="OpenIncident — DevOps Incident Response Environment")
env = OpenIncidentEnv()

@app.post("/reset")
async def reset(task_id: str = "easy"):
    try:
        return env.reset(task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step", response_model=StepResponse)
async def step(action: ActionEnum = Body(..., embed=True)):
    try:
        return env.step(action)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def get_state():
    try:
        return env.state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "project": "OpenIncident"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
