"""
Main entry point for the Agentic Metadata Ingestion Service.

This FastAPI application receives agent events and stores them in the OLAP database.
"""

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
    """
    Pydantic model representing an agent event.

    Attributes:
        event_id (str): Unique identifier for the event.
        agent_id (str): Identifier of the agent producing the event.
        step_type (str): Type of the step (e.g., 'llm_call').
        model (str, optional): LLM model used, if applicable.
        tokens_in (int, optional): Number of input tokens.
        tokens_out (int, optional): Number of output tokens.
        cost_usd (float, optional): Cost of the operation in USD.
        duration_ms (int): Duration of the step in milliseconds.
        status (str): Status of the execution (e.g., 'success', 'error').
        input_data (str, optional): JSON string of input arguments.
        output_data (str, optional): JSON string of output result or metadata.
        timestamp (float): Unix timestamp of when the event occurred.
    """
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
    """
    Ingest a new agent event.

    Args:
        event (Event): The event data payload.

    Returns:
        dict: Status message indicating success.
    """
    record = event.dict()
    record["received_at"] = datetime.utcnow().isoformat()

    write_event(record)

    return {"status": "stored"}
