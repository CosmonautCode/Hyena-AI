"""Feature flags system - 50+ flags with A/B testing and rollout strategies."""

from .definitions import (
    FlagCategory,
    RolloutStrategy,
    FlagStatus,
    FlagConfig,
    ALL_FLAGS,
    TOTAL_FLAGS,
    UI_FLAGS,
    FEATURES_FLAGS,
    TOOLS_FLAGS,
    MCP_FLAGS,
    STATE_FLAGS,
    PERFORMANCE_FLAGS,
    ADMIN_FLAGS,
    CATEGORY_COUNTS,
)

from .engine import (
    FlagEvaluator,
    FlagEvaluatorWithConfig,
    UserConfig,
    create_evaluator,
)

from .abtest import (
    TestStatus,
    TestMetric,
    Variant,
    MetricResult,
    ABTest,
    ABTestManager,
)

from .storage import (
    FlagStore,
    FlagManager,
)

from .commands import (
    FlagCommandHandler,
    create_flag_handler,
)

__all__ = [
    # Enums
    "FlagCategory",
    "RolloutStrategy",
    "FlagStatus",
    "TestStatus",
    "TestMetric",
    # Core classes
    "FlagConfig",
    "FlagEvaluator",
    "FlagEvaluatorWithConfig",
    "UserConfig",
    # A/B Testing
    "Variant",
    "MetricResult",
    "ABTest",
    "ABTestManager",
    # Storage
    "FlagStore",
    "FlagManager",
    # Commands
    "FlagCommandHandler",
    # Flag definitions
    "ALL_FLAGS",
    "UI_FLAGS",
    "FEATURES_FLAGS",
    "TOOLS_FLAGS",
    "MCP_FLAGS",
    "STATE_FLAGS",
    "PERFORMANCE_FLAGS",
    "ADMIN_FLAGS",
    "TOTAL_FLAGS",
    "CATEGORY_COUNTS",
    # Factory functions
    "create_evaluator",
    "create_flag_handler",
]
