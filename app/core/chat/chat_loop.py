"""Chat loop functionality for ChatSystem."""

import asyncio
from typing import Optional


class ChatLoopMixin:
    """Mixin for chat loop functionality."""
    
    def chat_display(self):
        """Main chat loop with modern terminal interface."""
        # Use async version
        try:
            asyncio.run(self._chat_loop_async())
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.tui.show_error(f"Error in chat loop: {e}")
        finally:
            self.tui.show_info("Goodbye!")
    
    async def _chat_loop_async(self):
        """Async chat loop with modern terminal interface."""
        self.tui.show_welcome()
        
        while self.running:
            try:
                # Get user input
                user_input = await self.tui.get_user_input_async()
                
                if not user_input:
                    continue
                
                # Check for commands
                if user_input.startswith('/'):
                    if self.command_manager.process_command(user_input):
                        continue
                    else:
                        self.tui.show_error("Unknown command. Use /help for available commands.")
                        continue
                
                # Add to history
                self.history.append(("user", user_input))
                
                # Get AI response
                response = await self._get_ai_response_async(user_input)
                
                # Add to history
                self.history.append(("assistant", response))
                
                # Display response
                self.tui.show_assistant_response(response)
                
            except Exception as e:
                self.tui.show_error(f"Error in chat loop: {e}")
    
    async def _get_ai_response_async(self, user_input: str) -> str:
        """Get AI response asynchronously."""
        if not self.llm:
            return "AI not loaded"
        
        # Build conversation context
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add recent history (limit to prevent context overflow)
        recent_history = self.history[-10:]  # Last 10 exchanges
        for role, content in recent_history:
            messages.append({"role": role, "content": content})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Get response from LLM
            response = self.llm.create_completion(
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"Error getting AI response: {e}"
