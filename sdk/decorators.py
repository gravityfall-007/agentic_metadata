"""
Decorators for tracing agent steps.

This module provides decorators to automatically trace execution steps, capture metadata,
measure duration, and emit events to the ingestion service.
"""

import time
import uuid
import json
from .emitter import emit_event

def trace_step(step_type: str):
    """
    Decorator to trace a function execution as a step in the agent workflow.

    Args:
        step_type (str): The type of the step (e.g., 'llm_call', 'retrieval').

    Returns:
        Callable: The decorated function.
    """
    def wrapper(fn):
        def inner(*args, **kwargs):
            event_id = str(uuid.uuid4())
            start = time.time()
            status = "success"
            llm_meta = {}

            try:
                # Execute the wrapped function
                result = fn(*args, **kwargs)
                if isinstance(result, dict):
                    llm_meta = result
                return result
            except Exception as e:
                status = "error"
                llm_meta["error"] = str(e)
                raise
            finally:
                # Emit the event with collected metadata
                emit_event({
                    "event_id": event_id,
                    "agent_id": "demo-agent",
                    "step_type": step_type,
                    "model": llm_meta.get("model"),
                    "tokens_in": llm_meta.get("tokens_in"),
                    "tokens_out": llm_meta.get("tokens_out"),
                    "cost_usd": llm_meta.get("cost_usd"),
                    "duration_ms": llm_meta.get("duration_ms")
                        or int((time.time() - start) * 1000),
                    "status": status,
                    "input_data": json.dumps({"args": args, "kwargs": kwargs}, default=str),
                    "output_data": json.dumps(llm_meta if llm_meta else result, default=str),
                    "timestamp": time.time()
                })
        return inner
    return wrapper
