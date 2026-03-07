"""Shell execution tools for ToolManager."""

from typing import Dict, Any
import subprocess
import os
import time
from app.utils.common import create_error_response, create_success_response, validate_command


class ShellToolsMixin:
    """Mixin for shell execution tools."""
    
    def _run_command(self, command: str, cwd: str = None) -> Dict[str, Any]:
        """Execute a shell command in the workspace."""
        if not validate_command(command):
            return create_error_response("Command blocked for safety")
        
        try:
            # Use provided cwd or workspace directory
            work_dir = cwd or self.workspace_manager.get_workspace()
            if not work_dir:
                return create_error_response("No working directory specified")
            
            # Execute command with timeout
            start_time = time.time()
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                return create_success_response("Command executed successfully", {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "execution_time": execution_time,
                    "command": command,
                    "working_directory": work_dir
                })
            else:
                return create_error_response(f"Command failed with exit code {result.returncode}", {
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                
        except subprocess.TimeoutExpired:
            return create_error_response("Command timed out after 30 seconds")
        except Exception as e:
            return create_error_response(str(e))
