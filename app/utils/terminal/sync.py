"""Synchronous execution methods for TerminalExecutor."""

from typing import Dict, Optional, Any
import subprocess
import os
import time


class SyncMixin:
    """Mixin for synchronous execution functionality."""
    
    def execute(self, command: str, cwd: Optional[str] = None, 
                timeout: Optional[int] = 60, capture_output: bool = True,
                env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute a terminal command synchronously."""
        try:
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                env=process_env
            )
            
            # Record command in history
            self.command_history.append({
                "command": command,
                "cwd": cwd,
                "return_code": result.returncode,
                "timestamp": time.time(),
                "success": result.returncode == 0
            })
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "return_code": result.returncode,
                "command": command,
                "cwd": cwd,
                "timeout": timeout
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "command": command,
                "cwd": cwd
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "cwd": cwd
            }
