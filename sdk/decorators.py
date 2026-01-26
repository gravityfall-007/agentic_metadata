"""
Decorators for tracing agent steps.

This module provides decorators to automatically trace execution steps, capture metadata,
measure duration, and emit events to the ingestion service.
"""

import time
import uuid
import json
from .emitter import emit_event
from .enterprise.cost import BudgetManager, BudgetExceededError
from .enterprise.security import SecurityAuditor

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
            # Enterprise Hook: Check Budget
            try:
                BudgetManager().check_pre_flight()
            except BudgetExceededError as e:
                SecurityAuditor.log_event("budget_blocked", {"error": str(e)})
                raise

            event_id = str(uuid.uuid4())
            start = time.time()
            status = "success"
            llm_meta = {}
            result = None # Ensure result is initialized for finally block

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
                # Sanitize args to remove 'self' or complex objects
                sanitized_args = []
                for arg in args:
                    s_arg = str(arg)
                    if s_arg.startswith("<") and "object at" in s_arg:
                        continue # Skip self/objects
                    sanitized_args.append(arg)

                # Ensure output is always a dict structure
                final_output = llm_meta
                if not final_output:
                     final_output = {"response": result} if result is not None else {"error": "Execution failed, no result"}

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
                    "input_data": json.dumps({"args": sanitized_args, "kwargs": kwargs}, default=str),
                    "output_data": json.dumps(final_output, default=str),
                    "timestamp": time.time()
                })
                
                # Enterprise Hook: Record Cost
                if llm_meta.get("cost_usd"):
                    try:
                        BudgetManager().record_cost(llm_meta.get("cost_usd"))
                    except BudgetExceededError as e:
                        # e.g. Log it, but the call already succeeded so we don't block return
                        SecurityAuditor.log_event("budget_exceeded_post_call", {"error": str(e)})

        return inner
    return wrapper
