"""Memory and compaction commands."""

from rich.panel import Panel
from rich.text import Text


class MemoryCommandsMixin:
    """Mixin for memory-related commands."""
    
    def _handle_compact_command(self):
        """Handle compact command."""
        if self.chat_system.context_compactor:
            try:
                compacted = self.chat_system.context_compactor.compact_history(self.chat_system.history)
                self.chat_system.history = compacted
                message = f"Conversation compacted from {len(self.chat_system.history)} messages"
            except Exception as e:
                message = f"Failed to compact: {str(e)}"
        else:
            message = "Context compactor not available"
        
        self.chat_system.tui.console.print(Panel(Text(message, style="bold white"), title="[bold green]Compact[/bold green]", border_style="green"))
        return True
    
    def _handle_memory_command(self, args):
        """Handle memory command."""
        if not args:
            # Show memory status
            if self.chat_system.auto_memory:
                memory_text = Text()
                memory_text.append("Auto-Memory System\n\n", style="bold cyan")
                
                # Get memory stats
                try:
                    stats = self.chat_system.auto_memory.get_stats()
                    conv_stats = stats.get('conversations', {})
                    memory_text.append(f"Auto-saved conversations: {conv_stats.get('total_conversations', 0)}\n", style="white")
                    memory_text.append(f"Extracted insights: {stats.get('insights', 0)}\n", style="white")
                    memory_text.append(f"Next memory extraction: {stats.get('next_extraction', 'N/A')} messages\n", style="white")
                    
                    current_session = stats.get('current_session', 'Unknown')
                    memory_text.append(f"\nCurrent: {current_session}\n\n", style="yellow")
                    
                    recent = []
                    if hasattr(self.chat_system.auto_memory, 'conversation_store'):
                        recent = self.chat_system.auto_memory.conversation_store.list_conversations(limit=5)
                    if recent:
                        memory_text.append("Recent Conversations:\n", style="white")
                        for conv in recent[:5]:  # Show last 5
                            # conv is a dict with 'filename', 'date', 'preview', etc.
                            filename = conv.get('filename', 'Unknown')
                            preview = conv.get('preview', '')[:40]
                            memory_text.append(f"  • {filename} - {preview}...\n", style="dim")
                    
                    memory_text.append("\nCommands:\n", style="white")
                    memory_text.append("  /memory save - Force save current conversation\n", style="green")
                    memory_text.append("  /memory extract - Force memory extraction\n", style="green")
                    memory_text.append("  /memory clear - Clear all memory\n", style="red")
                    
                    self.chat_system.tui.console.print(Panel(memory_text, title="[bold magenta]Memory[/bold magenta]", border_style="magenta"))
                except Exception as e:
                    error_text = Text()
                    error_text.append(f"Memory system error: {str(e)}", style="red")
                    self.chat_system.tui.console.print(Panel(error_text, title="[bold red]Memory Error[/bold red]", border_style="red"))
            else:
                self.chat_system.tui.console.print(Panel(Text("Auto-memory system not active", style="yellow"), title="[bold yellow]Memory[/bold yellow]", border_style="yellow"))
        else:
            action = args[0].lower()
            if action == "save" and self.chat_system.auto_memory:
                try:
                    self.chat_system.auto_memory.force_save()
                    message = "Current conversation saved to memory"
                except Exception as e:
                    message = f"Failed to save: {str(e)}"
            elif action == "extract" and self.chat_system.auto_memory:
                try:
                    self.chat_system.auto_memory.force_extraction()
                    message = "Memory extraction completed"
                except Exception as e:
                    message = f"Failed to extract: {str(e)}"
            elif action == "clear":
                if self.chat_system.project_memory.clear_memory():
                    message = "Project memory cleared"
                else:
                    message = "Failed to clear project memory"
            else:
                message = "Invalid memory command. Use: save, extract, or clear"
            
            self.chat_system.tui.console.print(Panel(Text(message, style="bold white"), title="[bold green]Memory[/bold green]", border_style="green"))
        
        return True
