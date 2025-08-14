"""
API Server for can_analyze_our_agent
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import json
from datetime import datetime
from can_analyze_our_agent import CanAnalyzeOurAgent


app = FastAPI(title="can_analyze_our_agent API", version="1.0.0")

# Initialize agent
with open("config.json") as f:
    config = json.load(f)

agent = CanAnalyzeOurAgent(config)


class ProcessRequest(BaseModel):
    data: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


class ProcessResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "can_analyze_our_agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/process", response_model=ProcessResponse)
async def process(request: ProcessRequest):
    """Main processing endpoint"""
    try:
        result = await agent.process(request.data)
        return ProcessResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status():
    """Get agent status"""
    return agent.get_status()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return agent.health_check()


@app.get("/metrics")
async def metrics():
    """Get agent metrics"""
    return agent.metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
