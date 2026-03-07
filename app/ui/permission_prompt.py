"""Permission prompt handling - Modern approval system."""

from rich.console import Console
from rich.panel import Panel
from .panels import PanelRenderer


class PermissionPrompt:
    """Render and handle permission requests for tool execution."""
    
    async def request_approval(
        self, 
        console: Console, 
        tool_name: str, 
        args: dict
    ) -> str:
        """
        Show permission prompt and return user decision.
        
        Returns one of: 'yes', 'no', 'always', 'never'
        """
        # First show the tool call panel
        renderer = PanelRenderer()
        console.print()
        console.print(renderer.render_tool_call(tool_name, args))
        
        # Show permission prompt
        console.print()
        console.print(
            "Allow this action? [Y] Yes  [N] No  [A] Always  [D] Deny",
            style='bold'
        )
        console.print()
        
        # Get response
        response = await self._get_choice(console)
        return response
    
    async def _get_choice(self, console: Console) -> str:
        """Get and validate user choice."""
        valid_choices = {
            'y': 'yes', 'yes': 'yes',
            'n': 'no', 'no': 'no',
            'a': 'always', 'always': 'always',
            'd': 'deny', 'deny': 'deny'
        }
        
        while True:
            try:
                # Use simple input for permission prompt
                user_input = input("Your choice [Y/N/A/D]: ").strip().lower()
                
                if not user_input:
                    continue
                
                choice = user_input[0] if len(user_input) == 1 else user_input
                
                if choice in valid_choices:
                    result = valid_choices[choice]
                    # Map 'deny' to 'never' for consistency
                    if result == 'deny':
                        result = 'never'
                    return result
                
                console.print("[dim]Please enter Y, N, A, or D[/dim]")
                
            except (EOFError, KeyboardInterrupt):
                return 'no'
    
    def request_approval_sync(
        self, 
        console: Console, 
        tool_name: str, 
        args: dict
    ) -> str:
        """Synchronous version for non-async contexts."""
        import asyncio
        try:
            return asyncio.run(self.request_approval(console, tool_name, args))
        except RuntimeError:
            # Already in async context
            renderer = PanelRenderer()
            console.print()
            console.print(renderer.render_tool_call(tool_name, args))
            console.print()
            console.print(
                "Allow this action? [Y] Yes  [N] No  [A] Always  [D] Deny",
                style='bold'
            )
            console.print()
            
            valid_choices = {
                'y': 'yes', 'yes': 'yes',
                'n': 'no', 'no': 'no',
                'a': 'always', 'always': 'always',
                'd': 'deny', 'deny': 'deny'
            }
            
            while True:
                user_input = input("Your choice [Y/N/A/D]: ").strip().lower()
                if not user_input:
                    continue
                
                choice = user_input[0] if len(user_input) == 1 else user_input
                
                if choice in valid_choices:
                    result = valid_choices[choice]
                    if result == 'deny':
                        result = 'never'
                    return result
                
                console.print("[dim]Please enter Y, N, A, or D[/dim]")
