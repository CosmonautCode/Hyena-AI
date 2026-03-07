import json
from datetime import datetime


class AITools:
    """AI-accessible tools for file operations."""
    
    def __init__(self, workspace_manager):
        """Initialize AI tools with workspace manager."""
        self.workspace_manager = workspace_manager
        self.tools = {
            "read_file": self.read_file_tool,
            "write_file": self.write_file_tool,
            "list_files": self.list_files_tool
        }
    
    def read_file_tool(self, filepath):
        """AI tool to read file content."""
        result = self.workspace_manager.read_file(filepath)
        if "error" in result:
            return f"Error reading file: {result['error']}"
        
        if result["type"] == "json":
            return f"File content (JSON):\n{json.dumps(result['content'], indent=2)}"
        else:
            return f"File content:\n{result['content']}"
    
    def write_file_tool(self, filepath, content, file_type='text'):
        """AI tool to write content to file."""
        result = self.workspace_manager.write_file(filepath, content, file_type)
        if "error" in result:
            return f"Error writing file: {result['error']}"
        return f"Success: {result['message']}"
    
    def list_files_tool(self, pattern="*"):
        """AI tool to list files in workspace."""
        result = self.workspace_manager.list_files(pattern)
        if "error" in result:
            return f"Error listing files: {result['error']}"
        
        output = f"Files in workspace {result['path']}:\n"
        for item in result["files"]:
            type_indicator = "[DIR]" if item["type"] == "directory" else "[FILE]"
            size_info = f" ({item['size']} bytes)" if item["size"] else ""
            output += f"{type_indicator} {item['name']}{size_info}\n"
        
        return output
    
    def parse_tool_call(self, message):
        """Parse AI messages for tool calls."""
        # Simple pattern matching for tool calls
        # Format: @tool_name(arguments)
        import re
        
        pattern = r'@(\w+)\((.*?)\)'
        matches = re.findall(pattern, message)
        
        results = []
        for tool_name, args in matches:
            if tool_name in self.tools:
                try:
                    # Parse arguments - handle quoted strings and simple args
                    if args:
                        # Split on commas but respect quotes
                        parts = [p.strip() for p in args.split(',')]
                        parsed_args = []
                        for part in parts:
                            # Remove quotes if present
                            if (part.startswith('"') and part.endswith('"')) or (part.startswith("'") and part.endswith("'")):
                                parsed_args.append(part[1:-1])
                            else:
                                parsed_args.append(part)
                    else:
                        parsed_args = []
                    
                    # Call the tool
                    if tool_name == "read_file":
                        result = self.tools[tool_name](parsed_args[0] if parsed_args else "")
                    elif tool_name == "write_file":
                        if len(parsed_args) >= 2:
                            result = self.tools[tool_name](parsed_args[0], parsed_args[1])
                        else:
                            result = "Error: write_file requires filepath and content"
                    elif tool_name == "list_files":
                        pattern_arg = parsed_args[0] if parsed_args else "*"
                        # Handle empty string pattern
                        if pattern_arg == "''" or pattern_arg == '""' or pattern_arg == "":
                            pattern_arg = "*"
                        result = self.tools[tool_name](pattern_arg)
                    else:
                        result = "Unknown tool"
                    
                    results.append(f"@{tool_name} result:\n{result}")
                    
                except Exception as e:
                    results.append(f"@{tool_name} error: {str(e)}")
        
        return results
