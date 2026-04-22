"""Math Tools plugin - example of a tool-based plugin."""

import logging
import math
from ..base import BasePlugin, PluginMetadata, PluginStatus


logger = logging.getLogger(__name__)


class MathToolsPlugin(BasePlugin):
    """Plugin that provides mathematical tools and utilities."""

    def __init__(self):
        """Initialize math tools plugin."""
        metadata = PluginMetadata(
            name="math_tools",
            version="1.0.0",
            description="Mathematical tools and utilities plugin",
            author="Hyena AI",
            author_email="team@hyena.ai",
            url="https://github.com/hyena-ai/math-tools-plugin",
            keywords=["math", "tools", "utilities", "calculator"],
            tools=["basic_arithmetic", "advanced_math", "statistics"],
        )
        super().__init__(metadata)

    def init(self) -> None:
        """Initialize plugin - register tools."""
        logger.info("Math Tools plugin initializing")
        
        # Register tools
        self.register_tool("basic_arithmetic", self._tool_basic_arithmetic)
        self.register_tool("advanced_math", self._tool_advanced_math)
        self.register_tool("statistics", self._tool_statistics)
        
        self.set_status(PluginStatus.INITIALIZED)
        logger.info("Math Tools plugin initialized with 3 tools")

    def load(self) -> None:
        """Load plugin."""
        logger.info("Math Tools plugin loading")
        self.set_status(PluginStatus.LOADED)
        logger.info("Math Tools plugin loaded")

    def enable(self) -> None:
        """Enable plugin."""
        logger.info("Math Tools plugin enabling")
        self.set_status(PluginStatus.ENABLED)
        logger.info("Math Tools plugin enabled")

    def disable(self) -> None:
        """Disable plugin."""
        logger.info("Math Tools plugin disabling")
        self.set_status(PluginStatus.DISABLED)
        logger.info("Math Tools plugin disabled")

    def unload(self) -> None:
        """Unload plugin."""
        logger.info("Math Tools plugin unloading")
        self.set_status(PluginStatus.UNLOADED)
        logger.info("Math Tools plugin unloaded")

    def _tool_basic_arithmetic(self, operation: str, a: float, b: float) -> dict:
        """Perform basic arithmetic operations.
        
        Args:
            operation: One of 'add', 'subtract', 'multiply', 'divide'
            a: First operand
            b: Second operand
            
        Returns:
            Dictionary with result and metadata
        """
        result = None
        error = None
        
        try:
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    error = "Division by zero"
                else:
                    result = a / b
            else:
                error = f"Unknown operation: {operation}"
        except Exception as e:
            error = str(e)
        
        return {
            "success": error is None,
            "operation": operation,
            "operand_a": a,
            "operand_b": b,
            "result": result,
            "error": error,
            "plugin": self.metadata.name,
        }

    def _tool_advanced_math(self, operation: str, value: float = None, base: float = None) -> dict:
        """Perform advanced mathematical operations.
        
        Args:
            operation: One of 'sqrt', 'sin', 'cos', 'tan', 'log', 'exp'
            value: Value to operate on
            base: Base for log operation
            
        Returns:
            Dictionary with result and metadata
        """
        result = None
        error = None
        
        try:
            if operation == "sqrt":
                if value < 0:
                    error = "Cannot take sqrt of negative number"
                else:
                    result = math.sqrt(value)
            elif operation == "sin":
                result = math.sin(value)
            elif operation == "cos":
                result = math.cos(value)
            elif operation == "tan":
                result = math.tan(value)
            elif operation == "log":
                if base is None:
                    base = math.e
                if value <= 0:
                    error = "Cannot take log of non-positive number"
                else:
                    result = math.log(value, base)
            elif operation == "exp":
                result = math.exp(value)
            else:
                error = f"Unknown operation: {operation}"
        except Exception as e:
            error = str(e)
        
        return {
            "success": error is None,
            "operation": operation,
            "value": value,
            "base": base,
            "result": result,
            "error": error,
            "plugin": self.metadata.name,
        }

    def _tool_statistics(self, operation: str, values: list) -> dict:
        """Perform statistical operations.
        
        Args:
            operation: One of 'mean', 'median', 'stdev', 'variance', 'min', 'max'
            values: List of numeric values
            
        Returns:
            Dictionary with result and metadata
        """
        result = None
        error = None
        
        try:
            if not values:
                error = "Empty value list"
            elif operation == "mean":
                result = sum(values) / len(values)
            elif operation == "median":
                sorted_values = sorted(values)
                n = len(sorted_values)
                if n % 2 == 0:
                    result = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
                else:
                    result = sorted_values[n//2]
            elif operation == "stdev":
                mean = sum(values) / len(values)
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                result = math.sqrt(variance)
            elif operation == "variance":
                mean = sum(values) / len(values)
                result = sum((x - mean) ** 2 for x in values) / len(values)
            elif operation == "min":
                result = min(values)
            elif operation == "max":
                result = max(values)
            else:
                error = f"Unknown operation: {operation}"
        except Exception as e:
            error = str(e)
        
        return {
            "success": error is None,
            "operation": operation,
            "values_count": len(values) if values else 0,
            "result": result,
            "error": error,
            "plugin": self.metadata.name,
        }
