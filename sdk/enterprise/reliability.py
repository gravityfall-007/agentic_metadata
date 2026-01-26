"""
Reliability module for Enterprise SDK.

This module provides tools for ensuring system stability and output validity.
"""

import time
import functools
import logging
from typing import Callable, Any, Dict, List

logger = logging.getLogger(__name__)

class RetryHandler:
    """
    Handles retries for operations with exponential backoff.
    """

    @staticmethod
    def with_retries(max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0):
        """
        Decorator to add retry logic to a function.
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                retries = 0
                delay = base_delay
                last_exception = None

                while retries <= max_retries:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        retries += 1
                        if retries > max_retries:
                            break
                        
                        logger.warning(
                            f"Operation failed with error: {e}. "
                            f"Retrying ({retries}/{max_retries}) in {delay:.2f}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                
                logger.error(f"Operation failed after {max_retries} retries.")
                raise last_exception
            return wrapper
        return decorator


class HallucinationGuard:
    """
    Simulates a guardrail against hallucinations.
    
    In a real enterprise system, this would call a smaller "critic" model
    or check against a knowledge graph.
    """

    @staticmethod
    def validate_response(response: str, context: str = "") -> Dict[str, Any]:
        """
        Validate the response for potential hallucinations or inconsistencies.
        
        Args:
            response (str): The model's response.
            context (str): The context provided to the model.
            
        Returns:
            dict: Validation result with 'is_safe' (bool) and 'confidence' (float).
        """
        # Placeholder logic: Check for "I don't know" or conflicting statements
        # This is where you'd plug in a deterministic checker or a second model call.
        
        warnings = []
        is_safe = True
        confidence = 1.0

        if not response:
            is_safe = False
            warnings.append("Empty response received.")
            confidence = 0.0
        
        # Simple heuristic: heavily redundant text usually indicates a loop/failure
        if len(response) > 50 and len(set(response.split())) < 5:
            is_safe = False
            warnings.append("Response appears repetitive/looping.")
            confidence = 0.2

        if warnings:
            logger.info(f"validation warnings: {warnings}")

        return {
            "is_safe": is_safe,
            "confidence": confidence,
            "warnings": warnings
        }
