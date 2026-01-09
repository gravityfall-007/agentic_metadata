import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sdk.decorators import trace_step

# Decorator to trace a step
from sdk.llm import call_llm

@trace_step("llm_call")
def agent_step():
    return call_llm(
        prompt="Explian the benefits of Clickhouse db instead of Postgres",
        model="llama-3.1-8b-instant"
    )

if __name__ == "__main__":
    result = agent_step()
    print("\nLLM RESPONSE:\n", result["response"])
