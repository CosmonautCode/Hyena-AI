"""Execution history management for AgenticLoop."""

from typing import Dict, List, Any
import time
import json


class HistoryMixin:
    """Mixin for execution history management."""
    
    def add_to_history(self, execution_result: Dict[str, Any]):
        """Add execution result to history."""
        history_entry = {
            "timestamp": time.time(),
            "plan": execution_result.get("plan", []),
            "results": execution_result.get("results", []),
            "verification": execution_result.get("verification", {}),
            "success": execution_result.get("success", False),
            "execution_time": execution_result.get("verification", {}).get("total_execution_time", 0.0)
        }
        
        self.execution_history.append(history_entry)
        
        # Keep history size manageable
        MAX_HISTORY = 100
        if len(self.execution_history) > MAX_HISTORY:
            self.execution_history = self.execution_history[-MAX_HISTORY:]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_execution_time": 0.0,
                "total_execution_time": 0.0
            }
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for entry in self.execution_history if entry["success"])
        failed_executions = total_executions - successful_executions
        total_time = sum(entry["execution_time"] for entry in self.execution_history)
        average_time = total_time / total_executions if total_executions > 0 else 0.0
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0.0,
            "average_execution_time": average_time,
            "total_execution_time": total_time
        }
    
    def get_recent_executions(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history."""
        return self.execution_history[-count:] if self.execution_history else []
    
    def clear_history(self):
        """Clear execution history."""
        self.execution_history.clear()
        return {"success": True, "message": "Execution history cleared"}
