"""
Cost management module for Enterprise SDK.

This module provides tools for tracking and limiting token usage and costs.
"""

from threading import Lock

class BudgetExceededError(Exception):
    """Raised when the operation exceeds the allocated budget."""
    pass

class BudgetManager:
    """
    Singleton class to manage token budget and costs.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(BudgetManager, cls).__new__(cls)
                    cls._instance._init_data()
        return cls._instance

    def _init_data(self):
        self.total_cost_usd = 0.0
        self.limit_usd = float('inf')  # Default to no limit
        self.alert_threshold = 0.8     # Alert at 80% usage
        self.alerts_triggered = set()

    def set_budget(self, limit_usd: float):
        """Set the maximum budget in USD."""
        self.limit_usd = limit_usd

    def record_cost(self, cost_usd: float):
        """
        Record a cost and check against budget.
        
        Raises:
            BudgetExceededError: If the new cost would exceed the limit.
        """
        with self._lock:
            if self.total_cost_usd + cost_usd > self.limit_usd:
                raise BudgetExceededError(
                    f"Cost recording of ${cost_usd:.6f} would exceed remaining budget. "
                    f"Current: ${self.total_cost_usd:.6f}, Limit: ${self.limit_usd:.6f}"
                )
            
            self.total_cost_usd += cost_usd
            self._check_alerts()

    def check_pre_flight(self):
        """
        Check if we are already over budget before making a call.
        """
        with self._lock:
            if self.total_cost_usd >= self.limit_usd:
                raise BudgetExceededError(
                    f"Budget exceeded. Current: ${self.total_cost_usd:.6f}, Limit: ${self.limit_usd:.6f}"
                )

    def _check_alerts(self):
        """Internal method to trigger alerts (logs/events) based on thresholds."""
        ratio = self.total_cost_usd / self.limit_usd if self.limit_usd > 0 else 0
        
        if ratio >= self.alert_threshold and "80_percent" not in self.alerts_triggered:
            # Here we would send a notification 
            # (e.g., Slack, Email, or just a log in this demo)
            print(f"WARNING: Budget usage at {ratio*100:.1f}% (${self.total_cost_usd:.4f} / ${self.limit_usd:.4f})")
            self.alerts_triggered.add("80_percent")

    def get_status(self):
        return {
            "current_cost": self.total_cost_usd,
            "limit": self.limit_usd,
            "remaining": self.limit_usd - self.total_cost_usd
        }
    
    def reset(self):
        """Resets the budget manager (mostly for testing)."""
        with self._lock:
            self._init_data()
