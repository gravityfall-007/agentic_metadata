"""
High-level Enterprise Client.

This module provides a unified interface for interacting with the enterprise SDK features.
"""

from ..llm import call_llm
from ..decorators import trace_step
from .security import PIIRedactor, SecurityAuditor
from .reliability import RetryHandler, HallucinationGuard
from .cost import BudgetManager
from .cost import BudgetManager
from .context import ContextManager
from typing import Dict, Any

class EnterpriseClient:
    """
    Unified client for enterprise LLM operations.
    """
    
    def __init__(self, agent_id: str, budget_limit: float = 10.0):
        self.agent_id = agent_id
        self.context = ContextManager(agent_id=agent_id)
        self.budget = BudgetManager()
        self.budget.set_budget(budget_limit)
        
    @trace_step("enterprise_chat")
    @RetryHandler.with_retries(max_retries=2)
    def chat(self, user_input: str, model: str = "llama-3.1-8b-instant") -> Dict[str, Any]:
        """
        Send a message to the LLM and get a response, handling:
        - PII Redaction
        - Context management
        - Budget checks
        - Reliability checks
        """
        # 1. Redact Input
        safe_input = PIIRedactor.redact(user_input)
        if safe_input != user_input:
            SecurityAuditor.log_event("pii_redacted_input", {"original_len": len(user_input)})
        
        # 2. Add to Memory
        self.context.add_message("user", safe_input)
        
        # 3. Construct Prompt (Simple Concatenation)
        history = self.context.get_context()
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        
        # 4. Check Budget (Handled by decorator or manual check here too)
        self.budget.check_pre_flight()
        
        # 5. Call LLM
        # Note: call_llm is raw, but if we wrap it or use the decorator 
        # normally, it logs costs. Here we assume call_llm returns the dict.
        result = call_llm(prompt, model=model)
        
        # 6. Record Cost (if not already handled by decorator on call_llm)
        # Since call_llm is not decorated in llm.py, we record here manually for the client usage.
        self.budget.record_cost(result["cost_usd"])
        
        response_text = result["response"]
        
        # 7. Validate Response
        validation = HallucinationGuard.validate_response(response_text)
        if not validation["is_safe"]:
            SecurityAuditor.log_event("hallucination_warning", validation)
            # In strict mode, we might reject. Here we just log.
        
        # 8. Redact Output
        safe_response = PIIRedactor.redact(response_text)
        
        # 9. Add to Memory
        self.context.add_message("assistant", safe_response)
        
        # Return full metadata so the decorator can log it properly
        return {
            "response": safe_response,
            "model": model,
            "tokens_in": result["tokens_in"],
            "tokens_out": result["tokens_out"],
            "cost_usd": result["cost_usd"],
            "duration_ms": result["duration_ms"],
            "validation": validation
        }
