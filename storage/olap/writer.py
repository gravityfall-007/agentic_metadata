"""
OLAP storage writer for ClickHouse.

This module handles the insertion of agent events into the ClickHouse database.
"""

import clickhouse_connect
from datetime import datetime

client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password='password'
)

def write_event(event: dict):
    """
    Write an event to the ClickHouse 'agent_events' table.

    Args:
        event (dict): The event data dictionary containing all required fields.
    """
    client.insert(
        table='agent_events',
        data=[[
            event["event_id"],
            event["agent_id"],
            event["step_type"],
            event.get("model") or "",
            event.get("tokens_in", 0) or 0,
            event.get("tokens_out", 0) or 0,
            event.get("cost_usd", 0.0) or 0.0,
            event["duration_ms"],
            event["status"],
            event.get("error_type") or "",
            event.get("input_data") or "",
            event.get("output_data") or "",
            datetime.fromtimestamp(event["timestamp"]),
            datetime.fromisoformat(event["received_at"])
        ]],
        column_names=[
            "event_id",
            "agent_id",
            "step_type",
            "model",
            "tokens_in",
            "tokens_out",
            "cost_usd",
            "duration_ms",
            "status",
            "error_type",
            "input_data",
            "output_data",
            "timestamp",
            "received_at"
        ]
    )
