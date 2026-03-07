"""Result verification methods for AgenticLoop."""

from typing import Dict, List, Any


class VerifyMixin:
    """Mixin for result verification functionality."""
    
    def _verify_results(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify execution results."""
        verification = {
            "overall_success": True,
            "successful_steps": 0,
            "failed_steps": 0,
            "total_execution_time": 0.0,
            "issues": []
        }
        
        total_time = 0.0
        
        for result in results:
            if result.get("success", False):
                verification["successful_steps"] += 1
            else:
                verification["failed_steps"] += 1
                verification["overall_success"] = False
                verification["issues"].append({
                    "tool": result.get("tool"),
                    "action": result.get("action"),
                    "error": result.get("error")
                })
            
            total_time += result.get("execution_time", 0.0)
        
        verification["total_execution_time"] = total_time
        
        # Add verification summary
        verification["summary"] = f"Executed {len(results)} steps: {verification['successful_steps']} successful, {verification['failed_steps']} failed"
        
        return verification
