"""Git integration tools."""

from typing import Any, Dict, List, Optional
import subprocess
from pathlib import Path
from datetime import datetime
from app.tools.base import BaseTool, ToolMetadata


class GitStatusTool(BaseTool):
    """Get git status."""
    
    metadata = ToolMetadata(
        name="git_status",
        category="git",
        description="Get repository status",
        parameters={
            "repo_path": {"type": "string", "description": "Repository path"},
        },
        returns={"status": {"type": "string"}, "changes": {"type": "array"}},
        permissions=["git.read"],
    )
    
    async def execute(self, repo_path: str, **kwargs: Any) -> Dict[str, Any]:
        """Get git status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            changes = [line for line in result.stdout.split("\n") if line.strip()]
            
            return {
                "success": True,
                "repo": repo_path,
                "change_count": len(changes),
                "changes": changes[:50],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "repo_path" in kwargs and Path(kwargs["repo_path"]).exists()


class GitLogTool(BaseTool):
    """Get commit history."""
    
    metadata = ToolMetadata(
        name="git_log",
        category="git",
        description="Get commit history",
        parameters={
            "repo_path": {"type": "string", "description": "Repository path"},
            "limit": {"type": "integer", "description": "Number of commits to show"},
        },
        returns={"commits": {"type": "array"}},
        permissions=["git.read"],
    )
    
    async def execute(self, repo_path: str, limit: int = 10, **kwargs: Any) -> Dict[str, Any]:
        """Get git log."""
        try:
            result = subprocess.run(
                ["git", "log", f"--max-count={limit}", "--pretty=format:%h|%an|%ae|%ai|%s"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            commits = []
            for line in result.stdout.split("\n"):
                if line.strip():
                    parts = line.split("|")
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": parts[4],
                        })
            
            return {
                "success": True,
                "repo": repo_path,
                "commit_count": len(commits),
                "commits": commits,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "repo_path" in kwargs and Path(kwargs["repo_path"]).exists()


class GitBranchesTool(BaseTool):
    """List branches."""
    
    metadata = ToolMetadata(
        name="git_branches",
        category="git",
        description="List all branches",
        parameters={
            "repo_path": {"type": "string", "description": "Repository path"},
        },
        returns={"branches": {"type": "array"}, "current": {"type": "string"}},
        permissions=["git.read"],
    )
    
    async def execute(self, repo_path: str, **kwargs: Any) -> Dict[str, Any]:
        """List branches."""
        try:
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            branches = []
            current = None
            
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line:
                    is_current = line.startswith("*")
                    branch_name = line[2:] if is_current else line
                    branches.append({"name": branch_name, "current": is_current})
                    if is_current:
                        current = branch_name
            
            return {
                "success": True,
                "repo": repo_path,
                "branch_count": len(branches),
                "current_branch": current,
                "branches": branches,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "repo_path" in kwargs and Path(kwargs["repo_path"]).exists()


class GitDiffTool(BaseTool):
    """Show git diff."""
    
    metadata = ToolMetadata(
        name="git_diff",
        category="git",
        description="Show differences between revisions",
        parameters={
            "repo_path": {"type": "string", "description": "Repository path"},
            "rev1": {"type": "string", "description": "First revision"},
            "rev2": {"type": "string", "description": "Second revision"},
        },
        returns={"diff": {"type": "string"}},
        permissions=["git.read"],
    )
    
    async def execute(self, repo_path: str, rev1: str = "HEAD", rev2: str = "HEAD~1", **kwargs: Any) -> Dict[str, Any]:
        """Get diff."""
        try:
            result = subprocess.run(
                ["git", "diff", rev2, rev1],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            lines = result.stdout.split("\n")[:100]
            
            return {
                "success": True,
                "repo": repo_path,
                "rev1": rev1,
                "rev2": rev2,
                "diff": "\n".join(lines),
                "lines": len(lines),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "repo_path" in kwargs and Path(kwargs["repo_path"]).exists()


class GitCommitTool(BaseTool):
    """Create commit."""
    
    metadata = ToolMetadata(
        name="git_commit",
        category="git",
        description="Create a new commit",
        parameters={
            "repo_path": {"type": "string", "description": "Repository path"},
            "message": {"type": "string", "description": "Commit message"},
            "all": {"type": "boolean", "description": "Stage all changes"},
        },
        returns={"success": {"type": "boolean"}, "hash": {"type": "string"}},
        permissions=["git.write"],
    )
    
    async def execute(self, repo_path: str, message: str, all: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """Create commit."""
        try:
            if all:
                subprocess.run(["git", "add", "-A"], cwd=repo_path, check=True, timeout=5)
            
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "success": result.returncode == 0,
                "repo": repo_path,
                "message": message,
                "output": result.stdout or result.stderr,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "repo_path" in kwargs and "message" in kwargs and Path(kwargs["repo_path"]).exists()


class GitMergeTool(BaseTool):
    """Merge branches."""
    
    metadata = ToolMetadata(
        name="git_merge",
        category="git",
        description="Merge branches",
        parameters={
            "repo_path": {"type": "string", "description": "Repository path"},
            "branch": {"type": "string", "description": "Branch to merge"},
            "no_ff": {"type": "boolean", "description": "No-fast-forward merge"},
        },
        returns={"success": {"type": "boolean"}, "conflicts": {"type": "integer"}},
        permissions=["git.write"],
    )
    
    async def execute(self, repo_path: str, branch: str, no_ff: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """Merge branch."""
        try:
            cmd = ["git", "merge"]
            if no_ff:
                cmd.append("--no-ff")
            cmd.append(branch)
            
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            conflicts = result.stdout.count("conflict")
            
            return {
                "success": result.returncode == 0,
                "repo": repo_path,
                "branch": branch,
                "conflicts": conflicts,
                "output": result.stdout or result.stderr,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "repo_path" in kwargs and "branch" in kwargs and Path(kwargs["repo_path"]).exists()


class GitCreateBranchTool(BaseTool):
    """Create new branch."""
    
    metadata = ToolMetadata(
        name="git_create_branch",
        category="git",
        description="Create and optionally checkout new branch",
        parameters={
            "repo_path": {"type": "string", "description": "Repository path"},
            "branch_name": {"type": "string", "description": "New branch name"},
            "checkout": {"type": "boolean", "description": "Checkout after creating"},
        },
        returns={"success": {"type": "boolean"}, "branch": {"type": "string"}},
        permissions=["git.write"],
    )
    
    async def execute(self, repo_path: str, branch_name: str, checkout: bool = True, **kwargs: Any) -> Dict[str, Any]:
        """Create branch."""
        try:
            cmd = ["git", "checkout", "-b"] if checkout else ["git", "branch"]
            cmd.append(branch_name)
            
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "success": result.returncode == 0,
                "repo": repo_path,
                "branch": branch_name,
                "checked_out": checkout,
                "output": result.stdout or result.stderr,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "repo_path" in kwargs and "branch_name" in kwargs and Path(kwargs["repo_path"]).exists()


class GitStashTool(BaseTool):
    """Stash changes."""
    
    metadata = ToolMetadata(
        name="git_stash",
        category="git",
        description="Stash or pop stashed changes",
        parameters={
            "repo_path": {"type": "string", "description": "Repository path"},
            "operation": {"type": "string", "description": "Operation: stash, pop, list"},
        },
        returns={"success": {"type": "boolean"}, "output": {"type": "string"}},
        permissions=["git.write"],
    )
    
    async def execute(self, repo_path: str, operation: str = "stash", **kwargs: Any) -> Dict[str, Any]:
        """Manage git stash."""
        try:
            result = subprocess.run(
                ["git", "stash", operation],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "success": result.returncode == 0,
                "repo": repo_path,
                "operation": operation,
                "output": result.stdout or result.stderr,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def validate(self, **kwargs: Any) -> bool:
        """Validate parameters."""
        return "repo_path" in kwargs and Path(kwargs["repo_path"]).exists()
