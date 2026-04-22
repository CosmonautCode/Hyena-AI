"""Tool execution methods for AgenticLoop."""

from typing import Dict, List, Any
import time


class ExecuteMixin:
    """Mixin for tool execution functionality."""
    
    def _execute_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute the plan with metrics tracking."""
        results = []
        metrics_collector = getattr(self, 'metrics_collector', None)
        
        for step in plan:
            tool_name = step.get("tool")
            action = step.get("action")
            operation_id = None
            
            try:
                # Start operation tracking
                if metrics_collector:
                    operation_id = metrics_collector.start_operation(f"tool_execution_{tool_name}", {
                        "action": action,
                        "step_index": len(results)
                    })
                
                start_time = time.time()
                
                # Execute based on tool type
                if tool_name == "file_operations":
                    result = self._execute_file_operation(action)
                elif tool_name == "shell_operations":
                    result = self._execute_shell_operation(action)
                else:
                    result = self._execute_general_operation(action)
                
                execution_time = time.time() - start_time
                success = result.get("success", False)
                
                results.append({
                    "tool": tool_name,
                    "action": action,
                    "success": success,
                    "data": result.get("data"),
                    "error": result.get("error"),
                    "execution_time": execution_time
                })
                
                # Record successful operation
                if metrics_collector and operation_id:
                    metrics_collector.end_operation(operation_id, success, {
                        "execution_time": execution_time,
                        "data_size": len(str(result.get("data", "")))
                    })
                
            except Exception as e:
                results.append({
                    "tool": tool_name,
                    "action": action,
                    "success": False,
                    "error": str(e),
                    "execution_time": 0.0
                })
                
                # Record failed operation
                if metrics_collector and operation_id:
                    metrics_collector.end_operation(operation_id, False, {
                        "error": str(e)
                    })
        
        return results
    
    def _execute_file_operation(self, action: str) -> Dict[str, Any]:
        """Execute file operation."""
        # Placeholder for file operation logic
        return {"success": True, "data": f"File operation '{action}' executed"}
    
    def _execute_shell_operation(self, action: str) -> Dict[str, Any]:
        """Execute shell operation."""
        # Placeholder for shell operation logic
        return {"success": True, "data": f"Shell operation '{action}' executed"}
    
    def _execute_general_operation(self, action: str) -> Dict[str, Any]:
        """Execute general operation."""
        # Placeholder for general operation logic
        return {"success": True, "data": f"General operation '{action}' executed"}
