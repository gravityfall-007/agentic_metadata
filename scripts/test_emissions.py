"""
Test script for verifying event emissions.

This script sends a sample event payload to the ingestion API to verify connectivity and validation.
"""

import requests
import time
import json

event = {
    "event_id": "test-id-3",
    "agent_id": "test-agent-3",
    "step_type": "test",
    "model": "test-model_3",
    "tokens_in": 200,
    "tokens_out": 5087,
    "cost_usd": 0.0010,
    "duration_ms": 190,
    "status": "success",
    "timestamp": time.time(),
}

try:
    print("Sending event:", json.dumps(event))
    resp = requests.post("http://localhost:8000/ingest", json=event, timeout=2)
    print("Status Code:", resp.status_code)
    print("Response:", resp.text)
except Exception as e:
    print("Error:", e)
