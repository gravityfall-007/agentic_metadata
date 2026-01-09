"""
Event emitter for the Agentic Metadata SDK.

This module handles sending tracking events to the central ingestion service.
"""

import requests

INGEST_URL = "http://localhost:8000/ingest"

def emit_event(event: dict):
    """
    Emit a tracking event to the ingestion API.

    Args:
        event (dict): The event data payload.
    """
    try:
        requests.post(INGEST_URL, json=event, timeout=1)
    except Exception:
        # fallback if API not up
        print("EMITTED (fallback):", event)
