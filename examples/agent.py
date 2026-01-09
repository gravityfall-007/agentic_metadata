"""
Example agent implementation using the SDK.

This script demonstrates how to define an agent step, trace it, and emit events
to the observability platform.
"""

import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sdk.decorators import trace_step
from sdk.llm import call_llm

@trace_step("llm_call")
def agent_step():
    """
    Execute a step in the agent workflow.

    This function calls the LLM with a specific prompt and returns the result.
    The execution is traced by the @trace_step decorator.

    Returns:
        dict: The LLM response and metadata.
    """
    return call_llm(
        prompt="Explain the benefits of Clickhouse db instead of Postgres",
        model="llama-3.1-8b-instant"
    )

if __name__ == "__main__":
    result = agent_step()
    print("\nLLM RESPONSE:\n", result["response"])
