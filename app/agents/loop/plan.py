"""Planning methods for AgenticLoop."""

from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger("hyena.agents.loop.plan")


class PlanMixin:
    """Mixin for planning functionality."""
    
    def _create_plan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create an execution plan using AI analysis.
        
        Uses the LLM to analyze the request and create an intelligent,
        step-by-step plan for execution.
        """
        user_input = context["user_input"]
        available_tools = context.get("available_tools", [])
        
        # Build prompt for LLM to create plan
        plan_prompt = f"""You are a task planner for an AI assistant. Analyze the user request and create a step-by-step plan.

User Request: {user_input}

Available Tools:
{json.dumps(available_tools, indent=2)}

Recent Context:
{json.dumps(context.get('conversation_history', [])[-3:], indent=2)}

Create a JSON plan with steps in this format:
[
  {{"step": 1, "tool": "tool_name", "action": "action_description", "description": "what_to_do"}},
  {{"step": 2, "tool": "tool_name", "action": "action_description", "description": "what_to_do"}}
]

Only include necessary steps. Return ONLY valid JSON, no other text."""
        
        try:
            # Get plan from LLM
            response = self.llm.create_completion(
                messages=[{"role": "user", "content": plan_prompt}],
                max_tokens=500,
                temperature=0.3  # Lower temperature for more structured output
            )
            
            response_text = response["choices"][0]["message"]["content"].strip()
            
            # Try to extract JSON from response
            try:
                plan = json.loads(response_text)
                if isinstance(plan, list):
                    logger.info(f"AI created plan with {len(plan)} steps")
                    return plan
            except json.JSONDecodeError:
                logger.warning("LLM response was not valid JSON, using fallback")
        except Exception as e:
            logger.warning(f"Error getting plan from LLM: {e}")
        
        # Fallback: Use simple pattern matching
        return self._create_fallback_plan(user_input, available_tools)
    
    def _create_fallback_plan(self, user_input: str, available_tools: List[str]) -> List[Dict[str, Any]]:
        """Create a fallback plan using simple heuristics.
        
        Used when LLM planning fails or returns invalid data.
        """
        user_lower = user_input.lower()
        plan = []
        step = 1
        
        # File operations
        if any(kw in user_lower for kw in ["read", "write", "file", "save", "load", "edit"]):
            plan.append({
                "step": step,
                "tool": "file_operations",
                "action": "handle_file_request",
                "description": f"Handle file operation: {user_input[:50]}"
            })
            step += 1
        
        # Shell commands
        if any(kw in user_lower for kw in ["run", "execute", "command", "shell", "script"]):
            plan.append({
                "step": step,
                "tool": "shell_operations",
                "action": "handle_command",
                "description": f"Execute command: {user_input[:50]}"
            })
            step += 1
        
        # Search/list operations
        if any(kw in user_lower for kw in ["list", "find", "search", "show", "view"]):
            plan.append({
                "step": step,
                "tool": "file_operations",
                "action": "handle_search",
                "description": f"Search/list: {user_input[:50]}"
            })
            step += 1
        
        # Default: general analysis
        if not plan:
            plan.append({
                "step": 1,
                "tool": "general_analysis",
                "action": "analyze_request",
                "description": f"Analyze: {user_input[:50]}"
            })
        
        return plan
