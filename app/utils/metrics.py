"""Performance metrics and monitoring system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import logging
from time import time

logger = logging.getLogger("hyena.metrics")


@dataclass
class ExecutionMetrics:
    """Metrics for a single operation execution."""
    
    operation: str
    start_time: float
    end_time: float = 0.0
    tokens_used: int = 0
    success: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """Get operation duration in seconds."""
        end = self.end_time or time()
        return end - self.start_time
    
    @property
    def duration_ms(self) -> float:
        """Get operation duration in milliseconds."""
        return self.duration * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'operation': self.operation,
            'duration_ms': self.duration_ms,
            'tokens': self.tokens_used,
            'success': self.success,
            'error': self.error,
            'metadata': self.metadata
        }


@dataclass
class SessionMetrics:
    """Aggregated metrics for a session."""
    
    session_start: float
    session_end: float = 0.0
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_tokens: int = 0
    total_duration: float = 0.0
    operations: List[ExecutionMetrics] = field(default_factory=list)
    
    @property
    def session_duration(self) -> float:
        """Get session duration in seconds."""
        end = self.session_end or time()
        return end - self.session_start
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_operations == 0:
            return 0.0
        return (self.successful_operations / self.total_operations) * 100
    
    @property
    def average_operation_time(self) -> float:
        """Get average operation duration in ms."""
        if self.total_operations == 0:
            return 0.0
        total_time = sum(op.duration for op in self.operations)
        return (total_time / self.total_operations) * 1000
    
    def add_operation(self, metrics: ExecutionMetrics) -> None:
        """Add operation metrics."""
        self.operations.append(metrics)
        self.total_operations += 1
        self.total_tokens += metrics.tokens_used
        
        if metrics.success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of session metrics."""
        return {
            'session_duration_seconds': self.session_duration,
            'total_operations': self.total_operations,
            'successful': self.successful_operations,
            'failed': self.failed_operations,
            'success_rate': f"{self.success_rate:.1f}%",
            'total_tokens': self.total_tokens,
            'average_operation_time_ms': f"{self.average_operation_time:.1f}",
            'operations': [op.to_dict() for op in self.operations]
        }


class MetricsCollector:
    """Collects and aggregates performance metrics."""
    
    def __init__(self, save_dir: Optional[str] = None):
        """Initialize metrics collector.
        
        Args:
            save_dir: Directory to save metrics (default: ~/.hyena/metrics)
        """
        self.save_dir = Path(save_dir) if save_dir else (Path.home() / ".hyena" / "metrics")
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session = SessionMetrics(session_start=time())
        self.operations_buffer: List[ExecutionMetrics] = []
        
        logger.info(f"Metrics collector initialized. Save dir: {self.save_dir}")
    
    def start_operation(self, operation_name: str) -> float:
        """Start tracking an operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            float: Start time for reference
        """
        start_time = time()
        logger.debug(f"Operation started: {operation_name}")
        return start_time
    
    def end_operation(
        self,
        operation_name: str,
        start_time: float,
        success: bool = True,
        tokens_used: int = 0,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> ExecutionMetrics:
        """End tracking an operation.
        
        Args:
            operation_name: Name of the operation
            start_time: Start time from start_operation()
            success: Whether operation succeeded
            tokens_used: Tokens consumed (for LLM ops)
            error: Error message if failed
            metadata: Additional metadata
            
        Returns:
            ExecutionMetrics: Collected metrics
        """
        metrics = ExecutionMetrics(
            operation=operation_name,
            start_time=start_time,
            end_time=time(),
            tokens_used=tokens_used,
            success=success,
            error=error,
            metadata=metadata or {}
        )
        
        self.current_session.add_operation(metrics)
        self.operations_buffer.append(metrics)
        
        level = logging.INFO if success else logging.WARNING
        logger.log(
            level,
            f"Operation completed: {operation_name} "
            f"({metrics.duration_ms:.1f}ms, "
            f"tokens={tokens_used}, "
            f"success={success})"
        )
        
        return metrics
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session summary."""
        return self.current_session.get_summary()
    
    def save_session(self, filename: Optional[str] = None) -> Path:
        """Save current session metrics to file.
        
        Args:
            filename: Custom filename (default: auto-generated)
            
        Returns:
            Path: Path to saved file
        """
        self.current_session.session_end = time()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.json"
        
        filepath = self.save_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.current_session.get_summary(), f, indent=2)
            logger.info(f"Session metrics saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
            raise
    
    def reset_session(self) -> None:
        """Reset session metrics."""
        self.current_session = SessionMetrics(session_start=time())
        self.operations_buffer.clear()
        logger.info("Session metrics reset")
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for a specific operation type.
        
        Args:
            operation_name: Name of operation to analyze
            
        Returns:
            Dict: Statistics for the operation
        """
        matching_ops = [
            op for op in self.current_session.operations
            if op.operation == operation_name
        ]
        
        if not matching_ops:
            return {"error": f"No operations found for {operation_name}"}
        
        durations = [op.duration_ms for op in matching_ops]
        tokens = [op.tokens_used for op in matching_ops]
        
        return {
            'operation': operation_name,
            'count': len(matching_ops),
            'successful': sum(1 for op in matching_ops if op.success),
            'failed': sum(1 for op in matching_ops if not op.success),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'avg_duration_ms': sum(durations) / len(durations),
            'total_tokens': sum(tokens)
        }
    
    def get_slowest_operations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get slowest operations from current session.
        
        Args:
            limit: Number of operations to return
            
        Returns:
            List: Sorted list of slowest operations
        """
        sorted_ops = sorted(
            self.current_session.operations,
            key=lambda op: op.duration,
            reverse=True
        )
        
        return [op.to_dict() for op in sorted_ops[:limit]]


# Global metrics instance
_metrics_instance: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance
