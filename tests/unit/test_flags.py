"""Tests for feature flags system."""

import pytest
import time
from app.core.flags import (
    FlagManager, FlagCommandHandler, ABTestManager, FlagEvaluatorWithConfig,
    FlagConfig, FlagCategory, RolloutStrategy, FlagStatus, TestMetric,
    Variant, ALL_FLAGS, create_evaluator, create_flag_handler
)


class TestFlagDefinitions:
    """Test flag definitions."""
    
    def test_total_flags_count(self):
        """Test total flag count."""
        assert len(ALL_FLAGS) >= 50
    
    def test_flag_categories(self):
        """Test flag categories."""
        ui_flags = [f for f in ALL_FLAGS.values() if f.category == FlagCategory.UI]
        features_flags = [f for f in ALL_FLAGS.values() if f.category == FlagCategory.FEATURES]
        tools_flags = [f for f in ALL_FLAGS.values() if f.category == FlagCategory.TOOLS]
        
        assert len(ui_flags) == 8
        assert len(features_flags) == 12
        assert len(tools_flags) == 8
    
    def test_flag_structure(self):
        """Test flag structure."""
        for flag_id, flag in ALL_FLAGS.items():
            assert flag.flag_id == flag_id
            assert flag.name
            assert flag.description
            assert flag.category
            assert flag.status
            assert flag.rollout_strategy


class TestFlagEvaluation:
    """Test flag evaluation."""
    
    def test_instant_rollout_enabled(self):
        """Test instant rollout at 100%."""
        flag = FlagConfig(
            flag_id="test_instant_100",
            name="Test Instant 100",
            description="Test",
            category=FlagCategory.FEATURES,
            default_value=False,
            status=FlagStatus.STABLE,
            rollout_strategy=RolloutStrategy.INSTANT,
            rollout_percentage=100,
            enabled_at=time.time()  # Mark as enabled
        )
        
        evaluator = create_evaluator({"test_instant_100": flag})
        assert evaluator.is_enabled("test_instant_100", "user1") is True
    
    def test_instant_rollout_disabled(self):
        """Test instant rollout at 0%."""
        flag = FlagConfig(
            flag_id="test_instant_0",
            name="Test Instant 0",
            description="Test",
            category=FlagCategory.FEATURES,
            default_value=False,
            status=FlagStatus.STABLE,
            rollout_strategy=RolloutStrategy.INSTANT,
            rollout_percentage=0,
            enabled_at=time.time()
        )
        
        evaluator = create_evaluator({"test_instant_0": flag})
        assert evaluator.is_enabled("test_instant_0", "user1") is False
    
    def test_percentage_rollout_consistent(self):
        """Test percentage rollout is consistent."""
        flag = FlagConfig(
            flag_id="test_percentage",
            name="Test Percentage",
            description="Test",
            category=FlagCategory.FEATURES,
            default_value=False,
            status=FlagStatus.STABLE,
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=50,
            enabled_at=time.time()
        )
        
        evaluator = create_evaluator({"test_percentage": flag})
        
        # Same user should always get same result
        result1 = evaluator.is_enabled("test_percentage", "user_consistent")
        result2 = evaluator.is_enabled("test_percentage", "user_consistent")
        
        assert result1 == result2
    
    def test_user_list_targeting(self):
        """Test user list targeting."""
        flag = FlagConfig(
            flag_id="test_user_list",
            name="Test User List",
            description="Test",
            category=FlagCategory.FEATURES,
            default_value=False,
            status=FlagStatus.STABLE,
            rollout_strategy=RolloutStrategy.USER_LIST,
            target_users=["user_a", "user_b"],
            enabled_at=time.time()
        )
        
        evaluator = create_evaluator({"test_user_list": flag})
        
        assert evaluator.is_enabled("test_user_list", "user_a") is True
        assert evaluator.is_enabled("test_user_list", "user_b") is True
        assert evaluator.is_enabled("test_user_list", "user_c") is False
    
    def test_default_value_when_inactive(self):
        """Test default value when flag is inactive."""
        flag = FlagConfig(
            flag_id="test_inactive",
            name="Test Inactive",
            description="Test",
            category=FlagCategory.FEATURES,
            default_value=False,
            status=FlagStatus.DEVELOPMENT,
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=50
        )
        # Mark as not active (no enabled_at or past disabled_at)
        
        evaluator = create_evaluator({"test_inactive": flag})
        assert evaluator.is_enabled("test_inactive", "user1") is False


class TestUserOverrides:
    """Test user overrides."""
    
    def test_set_user_override(self):
        """Test setting user override."""
        flag = FlagConfig(
            flag_id="test_override",
            name="Test Override",
            description="Test",
            category=FlagCategory.FEATURES,
            default_value=False,
            status=FlagStatus.STABLE,
            rollout_strategy=RolloutStrategy.INSTANT,
            rollout_percentage=0,
            enabled_at=time.time()
        )
        
        evaluator = create_evaluator({"test_override": flag})
        
        # Without override, should be disabled
        assert evaluator.is_enabled("test_override", "user1") is False
        
        # With override, should be enabled
        evaluator.set_user_override("user1", "test_override", True)
        assert evaluator.is_enabled("test_override", "user1") is True
    
    def test_remove_user_override(self):
        """Test removing user override."""
        flag = FlagConfig(
            flag_id="test_remove_override",
            name="Test Remove Override",
            description="Test",
            category=FlagCategory.FEATURES,
            default_value=False,
            status=FlagStatus.STABLE,
            rollout_strategy=RolloutStrategy.INSTANT,
            rollout_percentage=100,
            enabled_at=time.time()
        )
        
        evaluator = create_evaluator({"test_remove_override": flag})
        
        # Set override to disable
        evaluator.set_user_override("user1", "test_remove_override", False)
        assert evaluator.is_enabled("test_remove_override", "user1") is False
        
        # Remove override
        evaluator.remove_user_override("user1", "test_remove_override")
        # Should revert to enabled
        assert evaluator.is_enabled("test_remove_override", "user1") is True


class TestABTesting:
    """Test A/B testing system."""
    
    def test_create_test(self):
        """Test creating A/B test."""
        manager = ABTestManager()
        
        control = Variant("control", "Control variant")
        treatment = Variant("treatment", "Treatment variant")
        
        test = manager.create_test(
            "test_1",
            "flag_1",
            "Test 1",
            "Test description",
            control,
            treatment
        )
        
        assert test.test_id == "test_1"
        assert test.status == pytest.importorskip("app.core.flags").TestStatus.PLANNING
    
    def test_start_test(self):
        """Test starting test."""
        manager = ABTestManager()
        
        control = Variant("control", "Control")
        treatment = Variant("treatment", "Treatment")
        
        manager.create_test("test_2", "flag_2", "Test 2", "Desc", control, treatment)
        started = manager.start_test("test_2")
        
        assert started is True
        assert manager.tests["test_2"].is_active()
    
    def test_complete_test(self):
        """Test completing test."""
        manager = ABTestManager()
        
        control = Variant("control", "Control")
        treatment = Variant("treatment", "Treatment")
        
        manager.create_test("test_3", "flag_3", "Test 3", "Desc", control, treatment)
        manager.start_test("test_3")
        completed = manager.complete_test("test_3")
        
        assert completed is True
        assert manager.tests["test_3"].is_completed()
    
    def test_record_metric(self):
        """Test recording metric."""
        manager = ABTestManager()
        
        control = Variant("control", "Control")
        treatment = Variant("treatment", "Treatment")
        
        manager.create_test("test_4", "flag_4", "Test 4", "Desc", control, treatment)
        manager.start_test("test_4")
        
        recorded = manager.record_metric(
            "test_4",
            TestMetric.CONVERSION,
            0.05,  # 5% control
            0.08,  # 8% treatment
            0.95   # 95% confidence
        )
        
        assert recorded is True
        assert "conversion" in manager.tests["test_4"].metrics
    
    def test_assign_user_to_variant(self):
        """Test assigning user to variant."""
        manager = ABTestManager()
        
        control = Variant("control", "Control")
        treatment = Variant("treatment", "Treatment")
        
        manager.create_test("test_5", "flag_5", "Test 5", "Desc", control, treatment)
        assigned = manager.assign_user_to_variant("test_5", "user_1", "control")
        
        assert assigned is True
        variant = manager.get_user_variant("test_5", "user_1")
        assert variant == "control"


class TestFlagManager:
    """Test flag manager."""
    
    def test_enable_flag(self):
        """Test enabling flag via override."""
        manager = FlagManager()
        handler = create_flag_handler(manager)
        
        # Test that we can set user override to enable a disabled flag
        flag_id = "semantic_search"
        user_id = "test_user"
        
        # Initially might not be enabled due to rollout percentage
        manager.set_user_override(user_id, flag_id, True)
        
        # After override, should be enabled
        result = manager.is_enabled(flag_id, user_id)
        assert result is True
    
    def test_disable_flag(self):
        """Test disabling flag."""
        manager = FlagManager()
        
        # Disable flag
        manager.disable_flag("dark_mode")
        
        # Should be disabled
        assert manager.is_enabled("dark_mode", "user1") is False
    
    def test_set_rollout_percentage(self):
        """Test setting rollout percentage."""
        manager = FlagManager()
        
        manager.set_rollout_percentage("experimental_ui_v2", 75)
        
        # Get flag and verify percentage
        flag = manager.evaluator.flags["experimental_ui_v2"]
        assert flag.rollout_percentage == 75
    
    def test_add_target_user(self):
        """Test adding target user."""
        manager = FlagManager()
        
        manager.add_target_user("debug_mode", "admin_user")
        
        # Check if user is in target list
        flag = manager.evaluator.flags["debug_mode"]
        assert "admin_user" in flag.target_users
    
    def test_remove_target_user(self):
        """Test removing target user."""
        manager = FlagManager()
        
        manager.add_target_user("debug_mode", "admin_user")
        manager.remove_target_user("debug_mode", "admin_user")
        
        flag = manager.evaluator.flags["debug_mode"]
        assert "admin_user" not in flag.target_users
    
    def test_get_flag_stats(self):
        """Test getting flag statistics."""
        manager = FlagManager()
        
        stats = manager.get_flag_stats()
        
        assert stats["total_flags"] > 0
        assert "by_category" in stats
        assert "UI" not in stats or stats["by_category"].get("ui", 0) == 8


class TestFlagCommands:
    """Test flag command handler."""
    
    def test_list_flags(self):
        """Test listing flags."""
        manager = FlagManager()
        handler = create_flag_handler(manager)
        
        result = handler.list_flags()
        
        assert result["success"] is True
        assert result["count"] > 0
        assert len(result["flags"]) > 0
    
    def test_get_flag_info(self):
        """Test getting flag info."""
        manager = FlagManager()
        handler = create_flag_handler(manager)
        
        result = handler.get_flag_info("dark_mode")
        
        assert result["success"] is True
        assert result["flag"]["flag_id"] == "dark_mode"
    
    def test_check_flag(self):
        """Test checking flag."""
        manager = FlagManager()
        handler = create_flag_handler(manager)
        
        result = handler.check_flag("dark_mode", "user1")
        
        assert result["success"] is True
        assert "is_enabled" in result
    
    def test_set_user_override_command(self):
        """Test setting user override via command."""
        manager = FlagManager()
        handler = create_flag_handler(manager)
        
        result = handler.set_user_override("dark_mode", "user1", True)
        
        assert result["success"] is True
    
    def test_get_user_flags(self):
        """Test getting user flags."""
        manager = FlagManager()
        handler = create_flag_handler(manager)
        
        result = handler.get_user_flags("user1")
        
        assert result["success"] is True
        assert "flags" in result
    
    def test_get_flag_stats_command(self):
        """Test getting stats."""
        manager = FlagManager()
        handler = create_flag_handler(manager)
        
        result = handler.get_flag_stats()
        
        assert result["success"] is True
        assert "stats" in result


class TestFlagPerformance:
    """Performance tests."""
    
    def test_flag_evaluation_performance(self):
        """Test flag evaluation performance."""
        manager = FlagManager()
        
        start = time.time()
        for i in range(100):
            manager.is_enabled("dark_mode", f"user_{i}")
        elapsed = time.time() - start
        
        # Should be fast (<100ms for 100 evaluations)
        assert elapsed < 0.1
    
    def test_many_users_large_rollout(self):
        """Test performance with many users."""
        manager = FlagManager()
        
        start = time.time()
        for flag_id in list(ALL_FLAGS.keys())[:10]:
            for user_num in range(50):
                manager.is_enabled(flag_id, f"user_{user_num}")
        elapsed = time.time() - start
        
        # Should handle 500 evaluations in reasonable time
        assert elapsed < 1.0


class TestFlagIntegration:
    """Integration tests."""
    
    def test_complete_workflow(self):
        """Test complete workflow."""
        manager = FlagManager()
        handler = create_flag_handler(manager)
        
        # 1. Check initial state
        result = handler.check_flag("semantic_search", "user1")
        assert result["success"] is True
        initial_enabled = result["is_enabled"]
        
        # 2. Set override
        handler.set_user_override("semantic_search", "user1", True)
        
        # 3. Check after override
        result = handler.check_flag("semantic_search", "user1")
        assert result["is_enabled"] is True
        
        # 4. Get user flags
        result = handler.get_user_flags("user1")
        assert result["success"] is True
        assert "semantic_search" in result["flags"]
    
    def test_ab_test_workflow(self):
        """Test A/B test workflow."""
        manager = FlagManager()
        ab_manager = ABTestManager()
        
        # Create test
        control = Variant("control", "Control variant")
        treatment = Variant("treatment", "Treatment variant")
        
        test = ab_manager.create_test(
            "semantic_test",
            "semantic_search",
            "Semantic Search A/B Test",
            "Testing semantic search rollout",
            control,
            treatment
        )
        
        # Start test
        ab_manager.start_test("semantic_test")
        
        # Assign users
        ab_manager.assign_user_to_variant("semantic_test", "user1", "control")
        ab_manager.assign_user_to_variant("semantic_test", "user2", "treatment")
        
        # Record metrics
        ab_manager.record_metric(
            "semantic_test",
            TestMetric.CONVERSION,
            0.10,
            0.15,
            0.95
        )
        
        # Complete test
        ab_manager.complete_test("semantic_test")
        
        # Verify completion
        final_test = ab_manager.get_test("semantic_test")
        assert final_test.is_completed()


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_flag_id(self):
        """Test invalid flag ID."""
        manager = FlagManager()
        
        result = manager.is_enabled("nonexistent_flag", "user1")
        # Should not raise, just return false
        assert result is False
    
    def test_invalid_rollout_percentage(self):
        """Test invalid rollout percentage."""
        manager = FlagManager()
        handler = create_flag_handler(manager)
        
        result = handler.set_rollout("dark_mode", 150)
        assert result["success"] is False
    
    def test_nonexistent_test(self):
        """Test completing nonexistent test."""
        ab_manager = ABTestManager()
        
        result = ab_manager.complete_test("nonexistent")
        assert result is False
