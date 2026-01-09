import requests

INGEST_URL = "http://localhost:8000/ingest"

# Emit an event to the ingestion API
def emit_event(event: dict):
    try:
        requests.post(INGEST_URL, json=event, timeout=1)
    except Exception:
        # fallback if API not up
        print("EMITTED (fallback):", event)
