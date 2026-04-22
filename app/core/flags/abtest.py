"""A/B testing framework for feature flags."""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


logger = logging.getLogger("hyena.flags.abtest")


class TestStatus(str, Enum):
    """A/B test status."""
    PLANNING = "planning"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class TestMetric(str, Enum):
    """Metric types for A/B testing."""
    CONVERSION = "conversion"
    RETENTION = "retention"
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    ERROR_RATE = "error_rate"
    LATENCY = "latency"


@dataclass
class Variant:
    """A/B test variant."""
    name: str
    description: str
    traffic_percentage: int = 50  # 0-100
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "traffic_percentage": self.traffic_percentage,
            "metadata": self.metadata
        }


@dataclass
class MetricResult:
    """Result of a metric measurement."""
    metric_type: TestMetric
    control_value: float
    treatment_value: float
    improvement_percentage: float
    confidence_level: float  # 0.0-1.0
    is_significant: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "metric_type": self.metric_type.value,
            "control_value": self.control_value,
            "treatment_value": self.treatment_value,
            "improvement_percentage": self.improvement_percentage,
            "confidence_level": self.confidence_level,
            "is_significant": self.is_significant
        }


@dataclass
class ABTest:
    """A/B test configuration."""
    test_id: str
    flag_id: str
    name: str
    description: str
    control_variant: Variant
    treatment_variant: Variant
    status: TestStatus = TestStatus.PLANNING
    start_date: Optional[float] = None
    end_date: Optional[float] = None
    metrics: Dict[str, MetricResult] = field(default_factory=dict)
    winner: Optional[str] = None
    created_at: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    
    def is_active(self) -> bool:
        """Check if test is active."""
        return self.status == TestStatus.RUNNING
    
    def is_completed(self) -> bool:
        """Check if test is completed."""
        return self.status == TestStatus.COMPLETED
    
    def duration_days(self) -> Optional[float]:
        """Get test duration in days."""
        if self.start_date is None:
            return None
        
        end = self.end_date or datetime.utcnow().timestamp()
        return (end - self.start_date) / (24 * 3600)
    
    def update_timestamp(self) -> None:
        """Update last modified time."""
        self.updated_at = datetime.utcnow().timestamp()
    
    def get_winning_variant(self) -> Optional[str]:
        """Get winning variant based on metrics."""
        if not self.metrics:
            return None
        
        significant_improvements = [
            (variant, result.improvement_percentage)
            for variant, result in self.metrics.items()
            if result.is_significant
        ]
        
        if not significant_improvements:
            return None
        
        # Return variant with best improvement
        best_variant, _ = max(significant_improvements, key=lambda x: x[1])
        return best_variant
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "test_id": self.test_id,
            "flag_id": self.flag_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "control_variant": self.control_variant.to_dict(),
            "treatment_variant": self.treatment_variant.to_dict(),
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "winner": self.winner,
            "duration_days": self.duration_days()
        }


class ABTestManager:
    """Manages A/B tests."""
    
    def __init__(self):
        """Initialize manager."""
        self.tests: Dict[str, ABTest] = {}
        self.user_assignments: Dict[Tuple[str, str], str] = {}  # (test_id, user_id) -> variant
    
    def create_test(
        self,
        test_id: str,
        flag_id: str,
        name: str,
        description: str,
        control: Variant,
        treatment: Variant
    ) -> ABTest:
        """Create A/B test."""
        test = ABTest(
            test_id=test_id,
            flag_id=flag_id,
            name=name,
            description=description,
            control_variant=control,
            treatment_variant=treatment
        )
        
        self.tests[test_id] = test
        logger.info(f"A/B test created: {test_id}")
        return test
    
    def start_test(self, test_id: str) -> bool:
        """Start A/B test."""
        if test_id not in self.tests:
            logger.warning(f"Test not found: {test_id}")
            return False
        
        test = self.tests[test_id]
        test.status = TestStatus.RUNNING
        test.start_date = datetime.utcnow().timestamp()
        test.update_timestamp()
        
        logger.info(f"A/B test started: {test_id}")
        return True
    
    def complete_test(self, test_id: str) -> bool:
        """Complete A/B test."""
        if test_id not in self.tests:
            logger.warning(f"Test not found: {test_id}")
            return False
        
        test = self.tests[test_id]
        test.status = TestStatus.COMPLETED
        test.end_date = datetime.utcnow().timestamp()
        test.winner = test.get_winning_variant()
        test.update_timestamp()
        
        logger.info(f"A/B test completed: {test_id}, winner: {test.winner}")
        return True
    
    def pause_test(self, test_id: str) -> bool:
        """Pause A/B test."""
        if test_id not in self.tests:
            return False
        
        test = self.tests[test_id]
        test.status = TestStatus.PAUSED
        test.update_timestamp()
        return True
    
    def cancel_test(self, test_id: str) -> bool:
        """Cancel A/B test."""
        if test_id not in self.tests:
            return False
        
        test = self.tests[test_id]
        test.status = TestStatus.CANCELLED
        test.update_timestamp()
        return True
    
    def assign_user_to_variant(self, test_id: str, user_id: str, variant: str) -> bool:
        """Assign user to variant."""
        if test_id not in self.tests:
            return False
        
        test = self.tests[test_id]
        if variant not in [test.control_variant.name, test.treatment_variant.name]:
            logger.warning(f"Invalid variant: {variant}")
            return False
        
        self.user_assignments[(test_id, user_id)] = variant
        return True
    
    def get_user_variant(self, test_id: str, user_id: str) -> Optional[str]:
        """Get user's assigned variant."""
        return self.user_assignments.get((test_id, user_id))
    
    def record_metric(
        self,
        test_id: str,
        metric_type: TestMetric,
        control_value: float,
        treatment_value: float,
        confidence_level: float = 0.95
    ) -> bool:
        """Record metric result."""
        if test_id not in self.tests:
            return False
        
        test = self.tests[test_id]
        
        # Calculate improvement
        if control_value == 0:
            improvement = 0
        else:
            improvement = ((treatment_value - control_value) / control_value) * 100
        
        # Determine significance (simplified)
        is_significant = confidence_level >= 0.95
        
        result = MetricResult(
            metric_type=metric_type,
            control_value=control_value,
            treatment_value=treatment_value,
            improvement_percentage=improvement,
            confidence_level=confidence_level,
            is_significant=is_significant
        )
        
        test.metrics[metric_type.value] = result
        test.update_timestamp()
        
        logger.info(f"Metric recorded for test {test_id}: {metric_type.value}")
        return True
    
    def get_test(self, test_id: str) -> Optional[ABTest]:
        """Get test."""
        return self.tests.get(test_id)
    
    def get_active_tests(self) -> Dict[str, ABTest]:
        """Get active tests."""
        return {
            test_id: test
            for test_id, test in self.tests.items()
            if test.is_active()
        }
    
    def get_completed_tests(self) -> Dict[str, ABTest]:
        """Get completed tests."""
        return {
            test_id: test
            for test_id, test in self.tests.items()
            if test.is_completed()
        }
    
    def get_tests_for_flag(self, flag_id: str) -> Dict[str, ABTest]:
        """Get all tests for flag."""
        return {
            test_id: test
            for test_id, test in self.tests.items()
            if test.flag_id == flag_id
        }
    
    def get_tests_summary(self) -> Dict:
        """Get summary of all tests."""
        active = len(self.get_active_tests())
        completed = len(self.get_completed_tests())
        
        return {
            "total_tests": len(self.tests),
            "active_tests": active,
            "completed_tests": completed,
            "assignments": len(self.user_assignments)
        }
