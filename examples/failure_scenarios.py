"""
Failure Scenarios for LLM Observability.

This script demonstrates various failure modes (Safety Refusal, API Errors, 
Budget Exhaustion, and Minimal Output) to showcase how the SDK captures 
and reports these events.
"""

import sys
import os
import time

# Ensure we can import the sdk module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sdk.decorators import trace_step
from sdk.llm import call_llm
from sdk.enterprise.cost import BudgetManager

@trace_step("llm_call")
def safe_agent_call(prompt: str, model="llama-3.1-8b-instant"):
    """
    Execute an LLM call and return results.
    Traced by the @trace_step decorator.
    """
    return call_llm(prompt=prompt, model=model)

def run_scenarios():
    print("=== STARTING FAILURE SCENARIOS ===\n")

    # 1. Safety Refusal / Content Moderation
    # This might trigger a refusal string or a specific API error depending on the provider.
    print("Scenario 1: Safety Refusal")
    try:
        # Prompting for something that usually triggers safety filters
        result = safe_agent_call("Provide a detailed plan on how to illegally bypass government security systems.")
        print(f"Outcome: {result.get('response', 'Refused')[:50]}...")
    except Exception as e:
        print(f"Handled Error: {e}")
    print("-" * 30)

    # 2. Invalid Parameters (API Error)
    print("\nScenario 2: Invalid Model (API Error)")
    try:
        # Using a model name that doesn't exist
        result = safe_agent_call("Hello", model="invalid-model-name-12345")
        print(f"Outcome: {result}")
    except Exception as e:
        print(f"Captured Expected Error: {e}")
    print("-" * 30)

    # 3. Budget Exhaustion (Policy Block)
    print("\nScenario 3: Budget Exhaustion (Enterprise Policy)")
    budget = BudgetManager()
    budget.reset()
    budget.set_budget(0.01) # Set a small budget
    
    try:
        print("Call 1: Consuming some budget...")
        safe_agent_call("What is 2+2?")
        
        print(f"Current Cost: ${budget.get_status()['current_cost']:.6f}")
        print("Setting budget to be lower than current cost to trigger block...")
        budget.set_budget(0.000001) 
        
        print("Call 2: This should be blocked by pre-flight check.")
        result = safe_agent_call("This call should not happen.")
        print(f"Outcome: {result}")
    except Exception as e:
        print(f"Blocked by Budget: {e}")
    print("-" * 30)

    # 4. Minimal / Empty Output
    print("\nScenario 4: Minimal Output")
    budget.reset() # Reset budget for last call
    try:
        result = safe_agent_call("Reply with exactly one word: 'Ping'")
        print(f"Outcome: {result['response']}")
        print(f"Tokens Out: {result['tokens_out']}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 30)

    print("\n=== SCENARIOS COMPLETE ===")
    print("Check the dashboard at http://localhost:8501 (if running) to see these events.")

if __name__ == "__main__":
    run_scenarios()
