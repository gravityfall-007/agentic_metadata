"""
Test script for verifying event emissions.

This script sends a sample event payload to the ingestion API to verify connectivity and validation.
"""

import requests
import time
import json

event = {
    "event_id": "test-id-2",
    "agent_id": "test-agent",
    "step_type": "test",
    "model": "test-model_1",
    "tokens_in": 20,
    "tokens_out": 50,
    "cost_usd": 0.001,
    "duration_ms": 100,
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
