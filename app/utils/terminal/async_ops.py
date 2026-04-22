"""Asynchronous execution methods for TerminalExecutor."""

from typing import Dict, Optional, Callable, Any
import subprocess
import os
import threading
import time


class AsyncMixin:
    """Mixin for asynchronous execution functionality."""
    
    def execute_async(self, command: str, cwd: Optional[str] = None,
                     output_handler: Optional[Callable] = None,
                     completion_handler: Optional[Callable] = None,
                     env: Optional[Dict[str, str]] = None) -> str:
        """Execute a terminal command asynchronously."""
        process_id = f"proc_{self.process_id_counter}"
        self.process_id_counter += 1
        
        try:
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Start process
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=process_env,
                bufsize=1,
                universal_newlines=True
            )
            
            # Store process info
            self.running_processes[process_id] = {
                "process": process,
                "command": command,
                "cwd": cwd,
                "start_time": time.time(),
                "output_handler": output_handler,
                "completion_handler": completion_handler,
                "thread": None
            }
            
            # Start output monitoring thread
            if output_handler:
                thread = threading.Thread(
                    target=self._monitor_output,
                    args=(process_id, process, output_handler),
                    daemon=True
                )
                thread.start()
                self.running_processes[process_id]["thread"] = thread
            
            # Start completion monitoring thread
            completion_thread = threading.Thread(
                target=self._monitor_completion,
                args=(process_id, process, completion_handler),
                daemon=True
            )
            completion_thread.start()
            
            return process_id
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "cwd": cwd
            }
    
    def _monitor_output(self, process_id: str, process: subprocess.Popen, 
                       output_handler: Callable):
        """Monitor process output and call handler."""
        try:
            while process.poll() is None:
                line = process.stdout.readline()
                if line:
                    output_handler(process_id, line.strip())
                time.sleep(0.01)  # Small delay to prevent busy waiting
        except Exception:
            pass  # Process likely terminated
    
    def _monitor_completion(self, process_id: str, process: subprocess.Popen,
                          completion_handler: Optional[Callable]):
        """Monitor process completion."""
        try:
            process.wait()  # Wait for process to complete
            
            # Get final result
            result = {
                "process_id": process_id,
                "command": self.running_processes[process_id]["command"],
                "return_code": process.returncode,
                "success": process.returncode == 0,
                "end_time": time.time(),
                "duration": time.time() - self.running_processes[process_id]["start_time"]
            }
            
            # Remove from running processes
            if process_id in self.running_processes:
                del self.running_processes[process_id]
            
            # Call completion handler
            if completion_handler:
                completion_handler(result)
                
        except Exception as e:
            if completion_handler:
                completion_handler({
                    "process_id": process_id,
                    "success": False,
                    "error": str(e)
                })
