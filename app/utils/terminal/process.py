"""Process management methods for TerminalExecutor."""

from typing import Dict, Optional, Any
import signal
import time


class ProcessMixin:
    """Mixin for process management functionality."""
    
    def terminate_process(self, process_id: str) -> Dict[str, Any]:
        """Terminate a running process."""
        if process_id not in self.running_processes:
            return {"success": False, "error": f"Process {process_id} not found"}
        
        try:
            process_info = self.running_processes[process_id]
            process = process_info["process"]
            
            # Try graceful termination first
            process.terminate()
            
            # Wait a bit for graceful termination
            time.sleep(2)
            
            # Check if still running
            if process.poll() is None:
                # Force kill if still running
                process.kill()
                time.sleep(1)
            
            # Remove from running processes
            del self.running_processes[process_id]
            
            return {
                "success": True,
                "message": f"Process {process_id} terminated",
                "command": process_info["command"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_process_status(self, process_id: str) -> Dict[str, Any]:
        """Get status of a running process."""
        if process_id not in self.running_processes:
            return {"success": False, "error": f"Process {process_id} not found"}
        
        try:
            process_info = self.running_processes[process_id]
            process = process_info["process"]
            
            return {
                "success": True,
                "process_id": process_id,
                "command": process_info["command"],
                "cwd": process_info["cwd"],
                "running": process.poll() is None,
                "return_code": process.poll(),
                "start_time": process_info["start_time"],
                "duration": time.time() - process_info["start_time"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_running_processes(self) -> Dict[str, Any]:
        """List all running processes."""
        processes = []
        
        for process_id, process_info in self.running_processes.items():
            process = process_info["process"]
            processes.append({
                "process_id": process_id,
                "command": process_info["command"],
                "cwd": process_info["cwd"],
                "running": process.poll() is None,
                "return_code": process.poll(),
                "start_time": process_info["start_time"],
                "duration": time.time() - process_info["start_time"]
            })
        
        return {
            "success": True,
            "processes": processes,
            "total": len(processes)
        }
    
    def kill_all_processes(self) -> Dict[str, Any]:
        """Kill all running processes."""
        terminated = []
        failed = []
        
        for process_id in list(self.running_processes.keys()):
            result = self.terminate_process(process_id)
            if result["success"]:
                terminated.append(process_id)
            else:
                failed.append({"process_id": process_id, "error": result["error"]})
        
        return {
            "success": len(failed) == 0,
            "terminated": terminated,
            "failed": failed,
            "total": len(terminated) + len(failed)
        }
