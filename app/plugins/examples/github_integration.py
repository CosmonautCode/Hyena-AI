"""GitHub Integration plugin - example of combined commands and tools."""

import logging
from ..base import BasePlugin, PluginMetadata, PluginStatus


logger = logging.getLogger(__name__)


class GitHubIntegrationPlugin(BasePlugin):
    """Plugin that integrates with GitHub for repository operations."""

    def __init__(self):
        """Initialize GitHub integration plugin."""
        metadata = PluginMetadata(
            name="github_integration",
            version="1.0.0",
            description="GitHub integration plugin for repository operations",
            author="Hyena AI",
            author_email="team@hyena.ai",
            url="https://github.com/hyena-ai/github-plugin",
            keywords=["github", "git", "integration", "repository"],
            dependencies=["requests>=2.28.0"],
            permissions=["tools.http", "tools.file.read"],
            commands=["repo_info", "search_repos"],
            tools=["fetch_user_repos", "get_repo_details", "search_code"],
        )
        super().__init__(metadata)
        self.github_api_base = "https://api.github.com"

    def init(self) -> None:
        """Initialize plugin - register commands and tools."""
        logger.info("GitHub Integration plugin initializing")
        
        # Register commands
        self.register_command("repo_info", self._cmd_repo_info)
        self.register_command("search_repos", self._cmd_search_repos)
        
        # Register tools
        self.register_tool("fetch_user_repos", self._tool_fetch_user_repos)
        self.register_tool("get_repo_details", self._tool_get_repo_details)
        self.register_tool("search_code", self._tool_search_code)
        
        self.set_status(PluginStatus.INITIALIZED)
        logger.info("GitHub Integration plugin initialized with 2 commands and 3 tools")

    def load(self) -> None:
        """Load plugin."""
        logger.info("GitHub Integration plugin loading")
        self.set_status(PluginStatus.LOADED)
        logger.info("GitHub Integration plugin loaded")

    def enable(self) -> None:
        """Enable plugin."""
        logger.info("GitHub Integration plugin enabling")
        self.set_status(PluginStatus.ENABLED)
        logger.info("GitHub Integration plugin enabled")

    def disable(self) -> None:
        """Disable plugin."""
        logger.info("GitHub Integration plugin disabling")
        self.set_status(PluginStatus.DISABLED)
        logger.info("GitHub Integration plugin disabled")

    def unload(self) -> None:
        """Unload plugin."""
        logger.info("GitHub Integration plugin unloading")
        self.set_status(PluginStatus.UNLOADED)
        logger.info("GitHub Integration plugin unloaded")

    # Commands
    def _cmd_repo_info(self, owner: str, repo: str) -> dict:
        """Get repository information.
        
        Args:
            owner: Repository owner username
            repo: Repository name
            
        Returns:
            Dictionary with repository info
        """
        try:
            # Simulate API call
            return {
                "success": True,
                "owner": owner,
                "repo": repo,
                "url": f"https://github.com/{owner}/{repo}",
                "api_endpoint": f"{self.github_api_base}/repos/{owner}/{repo}",
                "description": f"Repository {repo} by {owner}",
                "note": "This is a simulated response. Use with real GitHub API in production.",
                "plugin": self.metadata.name,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "plugin": self.metadata.name,
            }

    def _cmd_search_repos(self, query: str, language: str = None) -> dict:
        """Search for repositories.
        
        Args:
            query: Search query
            language: Optional programming language filter
            
        Returns:
            Dictionary with search results
        """
        try:
            # Simulate search
            filters = []
            if language:
                filters.append(f"language:{language}")
            
            search_url = f"{self.github_api_base}/search/repositories?q={query}"
            if filters:
                search_url += " " + " ".join(filters)
            
            return {
                "success": True,
                "query": query,
                "language": language,
                "search_url": search_url,
                "results_count": 0,  # Simulated
                "note": "This is a simulated response. Use with real GitHub API in production.",
                "plugin": self.metadata.name,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "plugin": self.metadata.name,
            }

    # Tools
    def _tool_fetch_user_repos(self, username: str) -> dict:
        """Fetch repositories for a user.
        
        Args:
            username: GitHub username
            
        Returns:
            Dictionary with user repositories
        """
        try:
            endpoint = f"{self.github_api_base}/users/{username}/repos"
            return {
                "success": True,
                "username": username,
                "endpoint": endpoint,
                "repos": [],  # Simulated empty list
                "total": 0,
                "note": "This is a simulated response. Use with real GitHub API in production.",
                "plugin": self.metadata.name,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "plugin": self.metadata.name,
            }

    def _tool_get_repo_details(self, owner: str, repo: str) -> dict:
        """Get detailed repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary with detailed repo info
        """
        try:
            endpoint = f"{self.github_api_base}/repos/{owner}/{repo}"
            return {
                "success": True,
                "owner": owner,
                "repo": repo,
                "endpoint": endpoint,
                "details": {
                    "stars": 0,
                    "forks": 0,
                    "watchers": 0,
                    "open_issues": 0,
                    "language": "Unknown",
                },
                "note": "This is a simulated response. Use with real GitHub API in production.",
                "plugin": self.metadata.name,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "plugin": self.metadata.name,
            }

    def _tool_search_code(self, query: str, repo: str = None) -> dict:
        """Search for code snippets.
        
        Args:
            query: Search query for code
            repo: Optional specific repository to search in
            
        Returns:
            Dictionary with search results
        """
        try:
            search_url = f"{self.github_api_base}/search/code?q={query}"
            if repo:
                search_url += f" repo:{repo}"
            
            return {
                "success": True,
                "query": query,
                "repo": repo,
                "search_url": search_url,
                "results": [],  # Simulated empty results
                "total": 0,
                "note": "This is a simulated response. Use with real GitHub API in production.",
                "plugin": self.metadata.name,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "plugin": self.metadata.name,
            }
