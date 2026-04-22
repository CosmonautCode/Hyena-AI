"""Conversation handling methods for ChatSystem."""

import asyncio
from pathlib import Path


class ConversationMixin:
    """Mixin for conversation handling functionality."""
    
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
        # Show welcome banner
        self.tui.show_welcome_banner()
        
        # Choose first agent
        self.choose_agent(0)
        
        while self.running:
            try:
                # Get user input
                workspace = self.get_workspace()
                user_input = await self.tui.get_input(workspace)
                
                # Handle empty input
                if not user_input.strip():
                    continue
                
                # Handle exit commands
                if user_input.lower() in {'exit', 'quit'}:
                    self.running = False
                    break
                
                # Handle commands with lock protection
                if user_input.startswith('/'):
                    async with self._processing_lock:
                        result = self.process_command(user_input)
                    if not self.running:
                        break
                    if result:
                        await asyncio.sleep(0.5)
                    continue
                
                # Regular chat message with lock protection
                async with self._processing_lock:
                    await self._handle_chat_turn(user_input)
                
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break
            except Exception as e:
                self.tui.show_error(str(e))
    
    async def _handle_chat_turn(self, user_input: str):
        """Handle a single chat turn with auto-memory integration."""
        # Add to history (user already sees their input at the prompt)
        self.history.append(("user", user_input))
        
        # Notify auto-memory (is_first = was history empty before this message?)
        if self.auto_memory:
            is_first = len(self.history) == 1
            self.auto_memory.on_user_message(user_input, is_first)
        
        # Show thinking spinner
        self.tui.start_thinking("Thinking")
        
        try:
            # Check if we have an LLM loaded
            if self.llm is None:
                self.tui.stop_thinking()
                self.tui.show_error("No LLM loaded. Please load a model first.")
                return
            
            # Build enhanced system prompt with context from memories
            enhanced_system_prompt = self.system_prompt
            if self.auto_memory:
                context = self.auto_memory.get_context_for_prompt(user_input)
                if context:
                    enhanced_system_prompt += context
            
            # Prepare messages
            messages = [{"role": "system", "content": enhanced_system_prompt}]
            messages += [{"role": role, "content": text} for role, text in self.history]
            
            # Get LLM response
            output = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=1028,
                temperature=0.2,
                top_p=0.9,
                repeat_penalty=1.15,
            )
            
            # Stop thinking spinner
            self.tui.stop_thinking()
            
            response = output["choices"][0]["message"]["content"].strip()
            
            # Notify auto-memory of assistant response
            if self.auto_memory:
                self.auto_memory.on_assistant_message(response)
            
            # Check for AI tool calls in response
            tool_results = self.ai_tools.parse_tool_call(response)
            if tool_results:
                # Add original response
                self.history.append(("assistant", response))
                
                # Show tool results
                for tool_result in tool_results:
                    self.tui.show_assistant_panel(tool_result, "Assistant")
                    self.history.append(("assistant", tool_result))
            else:
                # Show regular response
                self.tui.show_assistant_panel(response, "Assistant")
                self.history.append(("assistant", response))
            
            # Keep history concise
            MAX_HISTORY = 50
            if len(self.history) > MAX_HISTORY:
                del self.history[:-MAX_HISTORY]
        
        except Exception as e:
            self.tui.stop_thinking()
            self.tui.show_error(str(e))
            self.history.append(("assistant", f"Error: {str(e)}"))
