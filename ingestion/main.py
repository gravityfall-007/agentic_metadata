from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.olap.writer import write_event

app = FastAPI(title="Agentic Metadata Ingestion")

class Event(BaseModel):
    event_id: str
    agent_id: str
    step_type: str
    model: Optional[str]
    tokens_in: Optional[int]
    tokens_out: Optional[int]
    cost_usd: Optional[float]
    duration_ms: int
    status: str
    input_data: Optional[str]
    output_data: Optional[str]
    timestamp: float

@app.post("/ingest")
async def ingest(event: Event):
    record = event.dict()
    record["received_at"] = datetime.utcnow().isoformat()

    write_event(record)

    return {"status": "stored"}
