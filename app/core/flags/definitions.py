"""Feature flag definitions."""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


class FlagCategory(str, Enum):
    """Feature flag categories."""
    UI = "ui"
    FEATURES = "features"
    TOOLS = "tools"
    MCP = "mcp"
    STATE = "state"
    PERFORMANCE = "performance"
    ADMIN = "admin"


class RolloutStrategy(str, Enum):
    """Rollout strategy types."""
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    GRADUAL = "gradual"
    CANARY = "canary"
    INSTANT = "instant"


class FlagStatus(str, Enum):
    """Flag lifecycle status."""
    PLANNING = "planning"
    DEVELOPMENT = "development"
    BETA = "beta"
    ROLLOUT = "rollout"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


@dataclass
class FlagConfig:
    """Feature flag configuration."""
    flag_id: str
    name: str
    description: str
    category: FlagCategory
    default_value: bool
    status: FlagStatus
    rollout_strategy: RolloutStrategy
    rollout_percentage: int = 0  # 0-100
    target_users: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    enabled_at: Optional[float] = None
    disabled_at: Optional[float] = None
    created_at: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    
    def is_active(self) -> bool:
        """Check if flag is active."""
        return self.enabled_at is not None and (
            self.disabled_at is None or self.disabled_at > datetime.utcnow().timestamp()
        )
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)


# UI/UX Flags (8)
UI_FLAGS = {
    "experimental_ui_v2": FlagConfig(
        flag_id="experimental_ui_v2",
        name="Experimental UI v2",
        description="New experimental UI with updated components",
        category=FlagCategory.UI,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=10
    ),
    "dark_mode": FlagConfig(
        flag_id="dark_mode",
        name="Dark Mode",
        description="Enable dark mode theme",
        category=FlagCategory.UI,
        default_value=False,
        status=FlagStatus.STABLE,
        rollout_strategy=RolloutStrategy.INSTANT,
        rollout_percentage=100
    ),
    "advanced_keyboard_shortcuts": FlagConfig(
        flag_id="advanced_keyboard_shortcuts",
        name="Advanced Keyboard Shortcuts",
        description="Enable advanced keyboard shortcut system",
        category=FlagCategory.UI,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=50
    ),
    "sidebar_navigation_redesign": FlagConfig(
        flag_id="sidebar_navigation_redesign",
        name="Sidebar Navigation Redesign",
        description="New sidebar navigation layout",
        category=FlagCategory.UI,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.CANARY,
        rollout_percentage=5
    ),
    "panel_resizing": FlagConfig(
        flag_id="panel_resizing",
        name="Panel Resizing",
        description="Enable resizable panels",
        category=FlagCategory.UI,
        default_value=True,
        status=FlagStatus.STABLE,
        rollout_strategy=RolloutStrategy.INSTANT,
        rollout_percentage=100
    ),
    "notifications_redesign": FlagConfig(
        flag_id="notifications_redesign",
        name="Notifications Redesign",
        description="Redesigned notification system",
        category=FlagCategory.UI,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=30
    ),
    "custom_themes": FlagConfig(
        flag_id="custom_themes",
        name="Custom Themes",
        description="Allow users to create custom themes",
        category=FlagCategory.UI,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.USER_LIST
    ),
    "accessibility_enhancements": FlagConfig(
        flag_id="accessibility_enhancements",
        name="Accessibility Enhancements",
        description="Enhanced accessibility features",
        category=FlagCategory.UI,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=70
    ),
}

# Features Flags (12)
FEATURES_FLAGS = {
    "ai_v2": FlagConfig(
        flag_id="ai_v2",
        name="AI v2",
        description="New AI engine v2",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=20
    ),
    "semantic_search": FlagConfig(
        flag_id="semantic_search",
        name="Semantic Search",
        description="Enable semantic search",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.ROLLOUT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=60
    ),
    "auto_refactor": FlagConfig(
        flag_id="auto_refactor",
        name="Auto Refactor",
        description="Automatic code refactoring",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=15
    ),
    "code_generation": FlagConfig(
        flag_id="code_generation",
        name="Code Generation",
        description="AI code generation",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.ROLLOUT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=50
    ),
    "intelligent_comments": FlagConfig(
        flag_id="intelligent_comments",
        name="Intelligent Comments",
        description="AI-generated comments",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=40
    ),
    "real_time_collaboration": FlagConfig(
        flag_id="real_time_collaboration",
        name="Real-time Collaboration",
        description="Real-time code collaboration",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.USER_LIST
    ),
    "code_review_assistant": FlagConfig(
        flag_id="code_review_assistant",
        name="Code Review Assistant",
        description="AI code review",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=35
    ),
    "dependency_analyzer": FlagConfig(
        flag_id="dependency_analyzer",
        name="Dependency Analyzer",
        description="Analyze code dependencies",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.STABLE,
        rollout_strategy=RolloutStrategy.INSTANT,
        rollout_percentage=100
    ),
    "performance_profiler": FlagConfig(
        flag_id="performance_profiler",
        name="Performance Profiler",
        description="Built-in performance profiler",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=45
    ),
    "test_generator": FlagConfig(
        flag_id="test_generator",
        name="Test Generator",
        description="Auto-generate tests",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=25
    ),
    "security_scanner": FlagConfig(
        flag_id="security_scanner",
        name="Security Scanner",
        description="Built-in security scanner",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=55
    ),
    "documentation_generator": FlagConfig(
        flag_id="documentation_generator",
        name="Documentation Generator",
        description="Auto-generate documentation",
        category=FlagCategory.FEATURES,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=30
    ),
}

# Tools Flags (8)
TOOLS_FLAGS = {
    "git_v2": FlagConfig(
        flag_id="git_v2",
        name="Git v2",
        description="Git v2 integration",
        category=FlagCategory.TOOLS,
        default_value=False,
        status=FlagStatus.ROLLOUT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=75
    ),
    "github_integration": FlagConfig(
        flag_id="github_integration",
        name="GitHub Integration",
        description="GitHub API integration",
        category=FlagCategory.TOOLS,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=40
    ),
    "docker_support": FlagConfig(
        flag_id="docker_support",
        name="Docker Support",
        description="Docker container support",
        category=FlagCategory.TOOLS,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.USER_LIST
    ),
    "kubernetes_support": FlagConfig(
        flag_id="kubernetes_support",
        name="Kubernetes Support",
        description="Kubernetes integration",
        category=FlagCategory.TOOLS,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.USER_LIST
    ),
    "aws_integration": FlagConfig(
        flag_id="aws_integration",
        name="AWS Integration",
        description="AWS SDK integration",
        category=FlagCategory.TOOLS,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=30
    ),
    "database_tools": FlagConfig(
        flag_id="database_tools",
        name="Database Tools",
        description="Database query tools",
        category=FlagCategory.TOOLS,
        default_value=False,
        status=FlagStatus.STABLE,
        rollout_strategy=RolloutStrategy.INSTANT,
        rollout_percentage=100
    ),
    "rest_api_client": FlagConfig(
        flag_id="rest_api_client",
        name="REST API Client",
        description="Built-in REST client",
        category=FlagCategory.TOOLS,
        default_value=False,
        status=FlagStatus.STABLE,
        rollout_strategy=RolloutStrategy.INSTANT,
        rollout_percentage=100
    ),
    "terminal_integration": FlagConfig(
        flag_id="terminal_integration",
        name="Terminal Integration",
        description="Integrated terminal",
        category=FlagCategory.TOOLS,
        default_value=True,
        status=FlagStatus.STABLE,
        rollout_strategy=RolloutStrategy.INSTANT,
        rollout_percentage=100
    ),
}

# MCP Flags (6)
MCP_FLAGS = {
    "mcp_client": FlagConfig(
        flag_id="mcp_client",
        name="MCP Client",
        description="Model Context Protocol client",
        category=FlagCategory.MCP,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=50
    ),
    "mcp_server": FlagConfig(
        flag_id="mcp_server",
        name="MCP Server",
        description="Model Context Protocol server",
        category=FlagCategory.MCP,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.USER_LIST
    ),
    "mcp_tool_registry": FlagConfig(
        flag_id="mcp_tool_registry",
        name="MCP Tool Registry",
        description="MCP tool registry integration",
        category=FlagCategory.MCP,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=35
    ),
    "mcp_prompt_sync": FlagConfig(
        flag_id="mcp_prompt_sync",
        name="MCP Prompt Sync",
        description="Sync prompts via MCP",
        category=FlagCategory.MCP,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=15
    ),
    "mcp_extensions": FlagConfig(
        flag_id="mcp_extensions",
        name="MCP Extensions",
        description="MCP extension system",
        category=FlagCategory.MCP,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=10
    ),
    "mcp_resource_sync": FlagConfig(
        flag_id="mcp_resource_sync",
        name="MCP Resource Sync",
        description="Sync resources via MCP",
        category=FlagCategory.MCP,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=25
    ),
}

# State Flags (8)
STATE_FLAGS = {
    "redux_like_store": FlagConfig(
        flag_id="redux_like_store",
        name="Redux-like Store",
        description="Use Redux-like state management",
        category=FlagCategory.STATE,
        default_value=True,
        status=FlagStatus.STABLE,
        rollout_strategy=RolloutStrategy.INSTANT,
        rollout_percentage=100
    ),
    "state_persistence": FlagConfig(
        flag_id="state_persistence",
        name="State Persistence",
        description="Persist state to storage",
        category=FlagCategory.STATE,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=60
    ),
    "undo_redo": FlagConfig(
        flag_id="undo_redo",
        name="Undo/Redo",
        description="Enable undo/redo functionality",
        category=FlagCategory.STATE,
        default_value=True,
        status=FlagStatus.STABLE,
        rollout_strategy=RolloutStrategy.INSTANT,
        rollout_percentage=100
    ),
    "time_travel_debugging": FlagConfig(
        flag_id="time_travel_debugging",
        name="Time Travel Debugging",
        description="Debug state at any point in time",
        category=FlagCategory.STATE,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=10
    ),
    "state_snapshots": FlagConfig(
        flag_id="state_snapshots",
        name="State Snapshots",
        description="Save state snapshots",
        category=FlagCategory.STATE,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=40
    ),
    "action_replay": FlagConfig(
        flag_id="action_replay",
        name="Action Replay",
        description="Replay recorded actions",
        category=FlagCategory.STATE,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=20
    ),
    "state_metrics": FlagConfig(
        flag_id="state_metrics",
        name="State Metrics",
        description="Track state management metrics",
        category=FlagCategory.STATE,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=50
    ),
    "immutable_state": FlagConfig(
        flag_id="immutable_state",
        name="Immutable State",
        description="Enforce immutable state",
        category=FlagCategory.STATE,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=25
    ),
}

# Performance Flags (6)
PERFORMANCE_FLAGS = {
    "async_v2": FlagConfig(
        flag_id="async_v2",
        name="Async v2",
        description="New async implementation",
        category=FlagCategory.PERFORMANCE,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=45
    ),
    "lazy_loading": FlagConfig(
        flag_id="lazy_loading",
        name="Lazy Loading",
        description="Enable lazy loading",
        category=FlagCategory.PERFORMANCE,
        default_value=False,
        status=FlagStatus.ROLLOUT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=70
    ),
    "caching_layer": FlagConfig(
        flag_id="caching_layer",
        name="Caching Layer",
        description="Multi-layer caching",
        category=FlagCategory.PERFORMANCE,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=50
    ),
    "virtual_rendering": FlagConfig(
        flag_id="virtual_rendering",
        name="Virtual Rendering",
        description="Virtual rendering for large lists",
        category=FlagCategory.PERFORMANCE,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=30
    ),
    "query_optimization": FlagConfig(
        flag_id="query_optimization",
        name="Query Optimization",
        description="Optimize database queries",
        category=FlagCategory.PERFORMANCE,
        default_value=False,
        status=FlagStatus.BETA,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=55
    ),
    "background_workers": FlagConfig(
        flag_id="background_workers",
        name="Background Workers",
        description="Background worker processes",
        category=FlagCategory.PERFORMANCE,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=20
    ),
}

# Admin Flags (2)
ADMIN_FLAGS = {
    "debug_mode": FlagConfig(
        flag_id="debug_mode",
        name="Debug Mode",
        description="Enable debug mode",
        category=FlagCategory.ADMIN,
        default_value=False,
        status=FlagStatus.PLANNING,
        rollout_strategy=RolloutStrategy.USER_LIST
    ),
    "telemetry": FlagConfig(
        flag_id="telemetry",
        name="Telemetry",
        description="Enable telemetry collection",
        category=FlagCategory.ADMIN,
        default_value=False,
        status=FlagStatus.DEVELOPMENT,
        rollout_strategy=RolloutStrategy.PERCENTAGE,
        rollout_percentage=10
    ),
}

# Combine all flags
ALL_FLAGS = {
    **UI_FLAGS,
    **FEATURES_FLAGS,
    **TOOLS_FLAGS,
    **MCP_FLAGS,
    **STATE_FLAGS,
    **PERFORMANCE_FLAGS,
    **ADMIN_FLAGS,
}

# Count by category
CATEGORY_COUNTS = {
    FlagCategory.UI: len(UI_FLAGS),
    FlagCategory.FEATURES: len(FEATURES_FLAGS),
    FlagCategory.TOOLS: len(TOOLS_FLAGS),
    FlagCategory.MCP: len(MCP_FLAGS),
    FlagCategory.STATE: len(STATE_FLAGS),
    FlagCategory.PERFORMANCE: len(PERFORMANCE_FLAGS),
    FlagCategory.ADMIN: len(ADMIN_FLAGS),
}

TOTAL_FLAGS = len(ALL_FLAGS)
