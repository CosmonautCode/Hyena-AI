"""Chat loop functionality for ChatSystem."""

import asyncio
from typing import Optional
import logging

logger = logging.getLogger("hyena.core.chat_loop")


class ChatLoopMixin:
    """Mixin for chat loop functionality."""
    
    def chat_display(self):
        """Main chat loop with modern terminal interface."""
        # Use async version
        try:
            asyncio.run(self._chat_loop_async())
        except KeyboardInterrupt:
            logger.info("Chat interrupted by user")
            pass
        except Exception as e:
            self.tui.show_error(f"Error in chat loop: {e}")
            logger.error(f"Chat loop error: {e}", exc_info=True)
        finally:
            self.tui.show_info("Goodbye!")
    
    async def _chat_loop_async(self):
        """Async chat loop with modern terminal interface."""
        self.tui.show_welcome_banner()
        
        while self.running:
            try:
                # Get user input
                user_input = await self.tui.get_input()
                
                if not user_input:
                    continue
                
                # Check for commands
                if user_input.startswith('/'):
                    if self.command_manager.process_command(user_input):
                        continue
                    else:
                        self.tui.show_error("Unknown command. Use /help for available commands.")
                        continue
                
                # Show user message
                self.tui.show_user_message(user_input)
                
                # Add to history
                self.history.append(("user", user_input))
                
                # Store in memory system if available
                if self.auto_memory:
                    self.auto_memory.on_user_message(user_input)
                
                # Get AI response with memory-enhanced context
                response = await self._get_ai_response_async(user_input)
                
                # Add to history
                self.history.append(("assistant", response))
                
                # Display response
                self.tui.show_assistant_panel(response, "Assistant")
                
                # Store response in memory if available
                if self.auto_memory:
                    self.auto_memory.on_assistant_message(response)
                
            except Exception as e:
                logger.error(f"Error in chat loop iteration: {e}", exc_info=True)
                self.tui.show_error(f"Error: {e}")
    
    async def _get_ai_response_async(self, user_input: str) -> str:
        """Get AI response asynchronously with memory context injection.
        
        Retrieves relevant memories and injects them into the system prompt
        for better context-aware responses. Tracks metrics for performance monitoring.
        """
        if not self.llm:
            return "AI not loaded. Please wait or restart."
        
        # Get metrics collector if available
        metrics_collector = getattr(self, 'metrics_collector', None)
        operation_id = None
        
        try:
            # Start operation tracking
            if metrics_collector:
                operation_id = metrics_collector.start_operation("ai_response_generation", {
                    "user_input_length": len(user_input),
                    "history_size": len(self.history)
                })
            
            # Build base system prompt
            system_prompt = self.system_prompt or "You are a helpful AI assistant."
            
            # Inject memory context if available
            if self.auto_memory:
                memory_context = self._get_memory_context(user_input)
                if memory_context:
                    system_prompt = f"{system_prompt}\n\n## Context from Memory:\n{memory_context}"
            
            # Build conversation context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent history (limit to prevent context overflow)
            recent_history = self.history[-10:]  # Last 10 exchanges
            for role, content in recent_history:
                messages.append({"role": role, "content": content})
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Get response from LLM
            logger.info(f"Generating response for: {user_input[:50]}...")
            
            response = self.llm.create_completion(
                messages=messages,
                max_tokens=self.system_prompt and 1000 or 1000,
                temperature=0.7
            )
            
            result = response["choices"][0]["message"]["content"]
            logger.info("Response generated successfully")
            
            # Record successful operation
            if metrics_collector and operation_id:
                metrics_collector.end_operation(operation_id, True, {
                    "response_length": len(result),
                    "message_count": len(messages)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}", exc_info=True)
            
            # Record failed operation
            if metrics_collector and operation_id:
                metrics_collector.end_operation(operation_id, False, {
                    "error": str(e)
                })
            
            return f"Error generating response: {str(e)}"
    
    def _get_memory_context(self, user_input: str) -> str:
        """Get relevant memory context for the current query.
        
        Retrieves up to 3 relevant memories based on the current input.
        """
        if not self.auto_memory:
            return ""
        
        try:
            # Get relevant memories
            relevant = self.auto_memory.get_relevant_memories(user_input, limit=3)
            
            if not relevant:
                return ""
            
            # Format memories as context
            context_lines = []
            for i, memory in enumerate(relevant, 1):
                if isinstance(memory, dict):
                    context_lines.append(f"- {memory.get('content', str(memory))}")
                else:
                    context_lines.append(f"- {memory}")
            
            return "\n".join(context_lines) if context_lines else ""
        except Exception as e:
            logger.warning(f"Error retrieving memory context: {e}")
            return ""
