"""
Cost Manager

Manages cost tracking and budget limits for LLM operations.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from unrealon_llm.src.exceptions import CostLimitExceededError

logger = logging.getLogger(__name__)


class CostManager:
    """Real-time cost tracking with limits"""
    
    def __init__(self, daily_limit_usd: float = 10.0):
        self.daily_limit = Decimal(str(daily_limit_usd))
        self.total_cost = Decimal('0.00')
        self.requests_today = 0
        self.last_reset = datetime.now().date()
        
        # Cost breakdown
        self.cost_by_model: Dict[str, Decimal] = {}
        self.cost_by_operation: Dict[str, Decimal] = {}
    
    def track_request(self, cost_usd: float, model: str, operation: str = "completion", llm_logger=None):
        """Track a request cost"""
        # Reset daily counters if new day
        today = datetime.now().date()
        if today != self.last_reset:
            old_total = float(self.total_cost)
            self.total_cost = Decimal('0.00')
            self.requests_today = 0
            self.last_reset = today
            
            # Log daily reset
            if llm_logger and old_total > 0:
                llm_logger.log_cost_tracking(
                    daily_total_usd=old_total,
                    request_cost_usd=0,
                    details={
                        "daily_budget_reset": True,
                        "previous_total": old_total
                    }
                )
        
        cost_decimal = Decimal(str(cost_usd))
        
        # Check limit before adding
        if self.total_cost + cost_decimal > self.daily_limit:
            if llm_logger:
                llm_logger.log_cost_tracking(
                    operation_cost_usd=cost_usd,
                    daily_total_usd=float(self.total_cost + cost_decimal),
                    daily_limit_usd=float(self.daily_limit),
                    model=model,
                )
            raise CostLimitExceededError(
                float(self.total_cost + cost_decimal),
                float(self.daily_limit)
            )
        
        # Track costs
        self.total_cost += cost_decimal
        self.requests_today += 1
        
        # Track by model
        if model not in self.cost_by_model:
            self.cost_by_model[model] = Decimal('0.00')
        self.cost_by_model[model] += cost_decimal
        
        # Track by operation
        if operation not in self.cost_by_operation:
            self.cost_by_operation[operation] = Decimal('0.00')
        self.cost_by_operation[operation] += cost_decimal
        
        # Log cost tracking
        if llm_logger:
            llm_logger.log_cost_tracking(
                operation_cost_usd=cost_usd,
                daily_total_usd=float(self.total_cost),
                daily_limit_usd=float(self.daily_limit),
                model=model,
            )
    
    def can_afford(self, estimated_cost_usd: float) -> bool:
        """Check if we can afford a request"""
        return self.total_cost + Decimal(str(estimated_cost_usd)) <= self.daily_limit
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget"""
        return float(self.daily_limit - self.total_cost)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cost statistics"""
        return {
            "total_cost_usd": float(self.total_cost),
            "remaining_budget_usd": float(self.daily_limit - self.total_cost),
            "requests_today": self.requests_today,
            "daily_limit_usd": float(self.daily_limit),
            "cost_by_model": {k: float(v) for k, v in self.cost_by_model.items()},
            "cost_by_operation": {k: float(v) for k, v in self.cost_by_operation.items()},
        }
