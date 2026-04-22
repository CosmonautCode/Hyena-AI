"""CLI parser and command router for Hyena-AI."""

import sys
import asyncio
from typing import Optional, List, Dict, Any
from app.cli.commands.registry import get_registry, CommandContext, CommandResult


class CLIParser:
    """Parse and route CLI commands."""
    
    def __init__(self):
        self.registry = get_registry()
        self.running = False
    
    def parse_input(self, user_input: str) -> tuple[str, Dict[str, Any]]:
        """
        Parse user input into command name and arguments.
        
        Format: /command_name [--arg1 value1] [--arg2 value2] [positional_args]
        """
        parts = user_input.strip().split()
        if not parts:
            return "", {}
        
        # Extract command (first word, may start with /)
        command = parts[0].lstrip('/')
        
        args = {}
        positionals = []
        i = 1
        
        while i < len(parts):
            part = parts[i]
            if part.startswith('--'):
                # Named argument
                key = part[2:]
                if i + 1 < len(parts) and not parts[i + 1].startswith('--'):
                    args[key] = parts[i + 1]
                    i += 2
                else:
                    args[key] = True
                    i += 1
            else:
                positionals.append(part)
                i += 1
        
        # Add positional arguments with keys
        if positionals:
            args['_positionals'] = positionals
        
        return command, args
    
    async def execute_command(self, user_input: str) -> CommandResult:
        """Execute a command from user input."""
        if not user_input.strip():
            return CommandResult(success=False, message="Empty command")
        
        command_name, args = self.parse_input(user_input)
        ctx = CommandContext(user_input, args)
        
        return await self.registry.execute(command_name, ctx)
    
    def show_prompt(self) -> None:
        """Show interactive prompt."""
        print("\n=== Hyena-AI CLI ===")
        print("Type '/help' for commands, 'exit' to quit\n")
    
    async def run_interactive(self) -> None:
        """Run interactive CLI session."""
        self.show_prompt()
        self.running = True
        
        while self.running:
            try:
                user_input = input("hyena> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    self.running = False
                    break
                
                result = await self.execute_command(user_input)
                print(str(result))
                
                if result.data:
                    print(f"Data: {result.data}")
                
                if result.warnings:
                    for warning in result.warnings:
                        print(f"⚠ {warning}")
                
                if result.errors:
                    for error in result.errors:
                        print(f"✗ {error}")
            
            except KeyboardInterrupt:
                print("\nInterrupted.")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")
    
    def show_info(self) -> None:
        """Show CLI information."""
        stats = self.registry.get_stats()
        print("\n=== Hyena-AI CLI Information ===")
        print(f"Commands: {stats['unique_commands']}")
        print(f"Categories: {stats['categories']}")
        print(f"Aliases: {stats['aliases']}")
        print("\nUse '/help' for command list")


# Global parser instance
_global_parser: Optional[CLIParser] = None


def get_parser() -> CLIParser:
    """Get or create the global CLI parser."""
    global _global_parser
    if _global_parser is None:
        _global_parser = CLIParser()
    return _global_parser


def run_cli() -> None:
    """Run the CLI."""
    parser = get_parser()
    asyncio.run(parser.run_interactive())


if __name__ == "__main__":
    run_cli()
