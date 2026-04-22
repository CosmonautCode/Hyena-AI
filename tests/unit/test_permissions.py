"""Comprehensive permission system tests."""

import pytest
from app.core.permissions.rbac import RBACSystem, PermissionName, PredefinedRole, Role
from app.core.permissions.resources import ResourcePermissionManager, ResourceType, ResourceAction, Resource
from app.core.permissions.audit import AuditLogger, AuditEventType, AuditSeverity
from app.core.permissions.grants import TemporaryGrantManager
from app.core.permissions.suggestions import PermissionSuggestionEngine, SuggestionType, RiskLevel


class TestRBACSystem:
    """Test RBAC system."""
    
    @pytest.fixture
    def rbac(self) -> RBACSystem:
        """Create RBAC instance."""
        return RBACSystem()
    
    def test_rbac_initialization(self, rbac):
        """Test RBAC initializes with predefined roles."""
        assert len(rbac.roles) == 5
        assert PredefinedRole.ADMIN.value in rbac.roles
        assert PredefinedRole.USER.value in rbac.roles
    
    def test_rbac_admin_role_has_all_permissions(self, rbac):
        """Test admin role has all permissions."""
        admin = rbac.get_role(PredefinedRole.ADMIN.value)
        assert admin is not None
        assert len(admin.permissions) == len(list(PermissionName))
    
    def test_rbac_viewer_role_read_only(self, rbac):
        """Test viewer role is read-only."""
        viewer = rbac.get_role(PredefinedRole.VIEWER.value)
        assert viewer is not None
        assert PermissionName.FILE_READ in viewer.permissions
        assert PermissionName.FILE_WRITE not in viewer.permissions
    
    def test_rbac_guest_role_minimal(self, rbac):
        """Test guest role has minimal permissions."""
        guest = rbac.get_role(PredefinedRole.GUEST.value)
        assert guest is not None
        assert len(guest.permissions) == 0
    
    def test_rbac_create_custom_role(self, rbac):
        """Test creating custom role."""
        role = rbac.create_role("custom", "Custom test role")
        assert role.name == "custom"
        assert role.is_custom is True
        assert role in rbac.list_roles()
    
    def test_rbac_delete_custom_role(self, rbac):
        """Test deleting custom role."""
        rbac.create_role("custom", "Custom test role")
        rbac.delete_role("custom")
        assert "custom" not in rbac.roles
    
    def test_rbac_cannot_delete_predefined_role(self, rbac):
        """Test cannot delete predefined role."""
        with pytest.raises(ValueError):
            rbac.delete_role(PredefinedRole.ADMIN.value)
    
    def test_rbac_assign_role_to_user(self, rbac):
        """Test assigning role to user."""
        rbac.assign_role("user1", PredefinedRole.USER.value)
        assert PredefinedRole.USER.value in rbac.get_user_roles("user1")
    
    def test_rbac_remove_role_from_user(self, rbac):
        """Test removing role from user."""
        rbac.assign_role("user1", PredefinedRole.USER.value)
        rbac.remove_role("user1", PredefinedRole.USER.value)
        assert PredefinedRole.USER.value not in rbac.get_user_roles("user1")
    
    def test_rbac_user_has_permission(self, rbac):
        """Test checking user permission."""
        rbac.assign_role("user1", PredefinedRole.USER.value)
        assert rbac.has_permission("user1", PermissionName.FILE_READ)
        assert not rbac.has_permission("user1", PermissionName.ADMIN_ALL)
    
    def test_rbac_get_user_permissions(self, rbac):
        """Test getting all user permissions."""
        rbac.assign_role("user1", PredefinedRole.USER.value)
        perms = rbac.get_user_permissions("user1")
        assert len(perms) > 0
        assert PermissionName.FILE_READ in perms
    
    def test_rbac_multiple_roles_per_user(self, rbac):
        """Test user can have multiple roles."""
        rbac.assign_role("user1", PredefinedRole.USER.value)
        rbac.assign_role("user1", PredefinedRole.POWER_USER.value)
        roles = rbac.get_user_roles("user1")
        assert len(roles) == 2
    
    def test_rbac_grant_permission_to_role(self, rbac):
        """Test granting permission to role."""
        role = rbac.create_role("custom", "Test")
        role.grant_permission(PermissionName.FILE_READ)
        assert PermissionName.FILE_READ in role.permissions
    
    def test_rbac_revoke_permission_from_role(self, rbac):
        """Test revoking permission from role."""
        role = rbac.create_role("custom", "Test")
        role.grant_permission(PermissionName.FILE_READ)
        role.revoke_permission(PermissionName.FILE_READ)
        assert PermissionName.FILE_READ not in role.permissions


class TestResourcePermissions:
    """Test resource-level permissions."""
    
    @pytest.fixture
    def manager(self) -> ResourcePermissionManager:
        """Create resource manager instance."""
        return ResourcePermissionManager()
    
    def test_create_resource(self, manager):
        """Test creating resource."""
        resource = manager.create_resource(
            "file1",
            ResourceType.FILE,
            "test.txt",
            owner_id="user1"
        )
        assert resource.id == "file1"
        assert resource.owner_id == "user1"
    
    def test_resource_owner_has_all_permissions(self, manager):
        """Test resource owner has all permissions."""
        manager.create_resource(
            "file1",
            ResourceType.FILE,
            "test.txt",
            owner_id="user1"
        )
        assert manager.has_permission("file1", "user1", ResourceAction.READ)
        assert manager.has_permission("file1", "user1", ResourceAction.WRITE)
        assert manager.has_permission("file1", "user1", ResourceAction.DELETE)
    
    def test_grant_resource_permission(self, manager):
        """Test granting resource permission."""
        manager.create_resource("file1", ResourceType.FILE, "test.txt")
        manager.grant_permission("file1", "user1", [ResourceAction.READ])
        assert manager.has_permission("file1", "user1", ResourceAction.READ)
        assert not manager.has_permission("file1", "user1", ResourceAction.WRITE)
    
    def test_revoke_resource_permission(self, manager):
        """Test revoking resource permission."""
        manager.create_resource("file1", ResourceType.FILE, "test.txt")
        manager.grant_permission("file1", "user1", [ResourceAction.READ, ResourceAction.WRITE])
        manager.revoke_permission("file1", "user1", [ResourceAction.WRITE])
        assert manager.has_permission("file1", "user1", ResourceAction.READ)
        assert not manager.has_permission("file1", "user1", ResourceAction.WRITE)
    
    def test_public_resources_readable(self, manager):
        """Test public resources are readable by all."""
        manager.create_resource(
            "file1",
            ResourceType.FILE,
            "test.txt",
            is_public=True
        )
        assert manager.has_permission("file1", "anyone", ResourceAction.READ)
    
    def test_transfer_resource_ownership(self, manager):
        """Test transferring resource ownership."""
        manager.create_resource("file1", ResourceType.FILE, "test.txt", owner_id="user1")
        manager.transfer_ownership("file1", "user1", "user2")
        resource = manager.get_resource("file1")
        assert resource.owner_id == "user2"
    
    def test_list_user_resources(self, manager):
        """Test listing resources for user."""
        manager.create_resource("file1", ResourceType.FILE, "test.txt", owner_id="user1")
        manager.create_resource("file2", ResourceType.FILE, "test2.txt", owner_id="user1")
        resources = manager.list_user_resources("user1")
        assert len(resources) >= 2
    
    def test_resource_permissions_dict(self, manager):
        """Test getting all permissions on resource."""
        manager.create_resource("file1", ResourceType.FILE, "test.txt")
        manager.grant_permission("file1", "user1", [ResourceAction.READ])
        manager.grant_permission("file1", "user2", [ResourceAction.WRITE])
        perms = manager.list_resource_permissions("file1")
        assert "user1" in perms
        assert "user2" in perms


class TestAuditLogging:
    """Test audit logging system."""
    
    @pytest.fixture
    def audit_logger(self) -> AuditLogger:
        """Create audit logger instance."""
        return AuditLogger()
    
    def test_log_event(self, audit_logger):
        """Test logging event."""
        event = audit_logger.log_event(
            AuditEventType.PERMISSION_GRANTED,
            "admin",
            "user1",
            resource_id="file1",
            action="read"
        )
        assert event.event_type == AuditEventType.PERMISSION_GRANTED
        assert event.actor_id == "admin"
    
    def test_log_permission_granted(self, audit_logger):
        """Test logging permission granted."""
        event = audit_logger.log_permission_granted(
            "admin",
            "user1",
            "file1",
            "file.read"
        )
        assert event.event_type == AuditEventType.PERMISSION_GRANTED
    
    def test_log_permission_denied(self, audit_logger):
        """Test logging permission denied."""
        event = audit_logger.log_permission_denied(
            "user1",
            "file1",
            "delete"
        )
        assert event.event_type == AuditEventType.PERMISSION_DENIED
        assert event.result == "failure"
    
    def test_query_events(self, audit_logger):
        """Test querying events."""
        audit_logger.log_permission_granted("admin", "user1", "file1", "read")
        audit_logger.log_permission_granted("admin", "user2", "file2", "write")
        
        events = audit_logger.get_events(subject_id="user1")
        assert len(events) == 1
        assert events[0].subject_id == "user1"
    
    def test_user_activity_log(self, audit_logger):
        """Test getting user activity."""
        audit_logger.log_permission_granted("admin", "user1", "file1", "read")
        audit_logger.log_resource_accessed("user1", "file1", "read")
        
        activity = audit_logger.get_user_activity("user1")
        assert len(activity) >= 1
    
    def test_resource_access_log(self, audit_logger):
        """Test getting resource access log."""
        audit_logger.log_resource_accessed("user1", "file1", "read")
        audit_logger.log_resource_accessed("user2", "file1", "write")
        
        access_log = audit_logger.get_resource_access_log("file1")
        assert len(access_log) >= 2
    
    def test_audit_event_max_capacity(self):
        """Test audit logger respects max capacity."""
        logger = AuditLogger(max_events=10)
        for i in range(20):
            logger.log_event(
                AuditEventType.PERMISSION_GRANTED,
                f"actor{i}",
                f"user{i}"
            )
        assert len(logger.events) <= 10
    
    def test_audit_stats(self, audit_logger):
        """Test audit statistics."""
        audit_logger.log_permission_granted("admin", "user1", "file1", "read")
        audit_logger.log_permission_denied("user1", "file1", "delete")
        
        stats = audit_logger.get_stats()
        assert stats["total_events"] == 2
        assert stats["denials"] == 1


class TestTemporaryGrants:
    """Test temporary grant system."""
    
    @pytest.fixture
    def grant_manager(self) -> TemporaryGrantManager:
        """Create grant manager instance."""
        return TemporaryGrantManager()
    
    def test_create_grant(self, grant_manager):
        """Test creating temporary grant."""
        grant = grant_manager.create_grant(
            "user1",
            "file.write",
            duration_seconds=3600,
            granted_by="admin"
        )
        assert grant.user_id == "user1"
        assert grant.permission == "file.write"
    
    def test_grant_not_expired(self, grant_manager):
        """Test grant not expired."""
        grant = grant_manager.create_grant(
            "user1",
            "file.write",
            duration_seconds=3600,
            granted_by="admin"
        )
        assert not grant.is_expired
    
    def test_grant_has_seconds_remaining(self, grant_manager):
        """Test grant has seconds remaining."""
        grant = grant_manager.create_grant(
            "user1",
            "file.write",
            duration_seconds=3600,
            granted_by="admin"
        )
        assert grant.seconds_remaining > 0
    
    def test_revoke_grant(self, grant_manager):
        """Test revoking grant."""
        grant = grant_manager.create_grant(
            "user1",
            "file.write",
            duration_seconds=3600,
            granted_by="admin"
        )
        grant_manager.revoke_grant(grant.grant_id)
        assert grant_manager.get_grant(grant.grant_id) is None
    
    def test_has_active_grant(self, grant_manager):
        """Test checking active grant."""
        grant_manager.create_grant(
            "user1",
            "file.write",
            duration_seconds=3600,
            granted_by="admin"
        )
        assert grant_manager.has_grant("user1", "file.write")
        assert not grant_manager.has_grant("user1", "file.delete")
    
    def test_get_user_grants(self, grant_manager):
        """Test getting user grants."""
        grant_manager.create_grant("user1", "file.write", 3600, "admin")
        grant_manager.create_grant("user1", "file.delete", 1800, "admin")
        
        grants = grant_manager.get_user_grants("user1")
        assert len(grants) == 2
    
    def test_revoke_all_user_grants(self, grant_manager):
        """Test revoking all user grants."""
        grant_manager.create_grant("user1", "file.write", 3600, "admin")
        grant_manager.create_grant("user1", "file.delete", 1800, "admin")
        
        count = grant_manager.revoke_all_user_grants("user1")
        assert count == 2
        assert len(grant_manager.get_user_grants("user1")) == 0
    
    def test_extend_grant(self, grant_manager):
        """Test extending grant."""
        grant = grant_manager.create_grant("user1", "file.write", 3600, "admin")
        original_expires = grant.expires_at
        
        grant_manager.extend_grant(grant.grant_id, 1800)
        grant = grant_manager.get_grant(grant.grant_id)
        
        assert grant.expires_at > original_expires
    
    def test_transfer_grant(self, grant_manager):
        """Test transferring grant."""
        grant = grant_manager.create_grant("user1", "file.write", 3600, "admin")
        grant_manager.transfer_grant(grant.grant_id, "user2")
        
        grant = grant_manager.get_grant(grant.grant_id)
        assert grant.user_id == "user2"
    
    def test_grant_stats(self, grant_manager):
        """Test grant statistics."""
        grant_manager.create_grant("user1", "file.write", 3600, "admin")
        grant_manager.create_grant("user2", "file.delete", 1800, "admin")
        
        stats = grant_manager.get_stats()
        assert stats["active_grants"] == 2


class TestPermissionSuggestions:
    """Test permission suggestion engine."""
    
    @pytest.fixture
    def engine(self) -> PermissionSuggestionEngine:
        """Create suggestion engine instance."""
        return PermissionSuggestionEngine()
    
    def test_suggest_grant(self, engine):
        """Test suggesting permission grant."""
        suggestion = engine.suggest_permission_grant(
            "user1",
            "file.read",
            "Frequently used permission"
        )
        assert suggestion.suggestion_type == SuggestionType.GRANT
        assert suggestion.permission == "file.read"
    
    def test_suggest_revoke(self, engine):
        """Test suggesting permission revoke."""
        suggestion = engine.suggest_permission_revoke(
            "user1",
            "file.delete",
            "Not used in recent history"
        )
        assert suggestion.suggestion_type == SuggestionType.REVOKE
    
    def test_suggest_based_on_usage(self, engine):
        """Test suggesting based on usage patterns."""
        current_perms = {"file.read"}
        recent_usage = {"file.read": 10, "file.write": 3}
        
        suggestions = engine.suggest_based_on_usage(
            "user1",
            current_perms,
            recent_usage
        )
        assert len(suggestions) > 0
    
    def test_least_privilege_suggestions(self, engine):
        """Test principle of least privilege suggestions."""
        current = {"file.read", "file.write", "file.delete", "admin.all"}
        required = {"file.read", "file.write"}
        
        suggestions = engine.suggest_principle_of_least_privilege(
            "user1",
            current,
            required
        )
        assert len(suggestions) > 0
    
    def test_security_improvement_suggestions(self, engine):
        """Test security improvement suggestions."""
        dangerous = {
            "system.shutdown",
            "system.install",
            "git.force_push",
            "file.delete"
        }
        
        suggestions = engine.suggest_security_improvements("user1", dangerous)
        assert len(suggestions) > 0
    
    def test_list_suggestions(self, engine):
        """Test listing suggestions."""
        engine.suggest_permission_grant("user1", "file.read", "Test")
        engine.suggest_permission_grant("user2", "file.write", "Test")
        
        suggestions = engine.list_suggestions(user_id="user1")
        assert all(s.user_id == "user1" for s in suggestions)
    
    def test_high_confidence_suggestions(self, engine):
        """Test filtering high confidence suggestions."""
        engine.suggest_permission_grant("user1", "file.read", "Test", confidence=0.9)
        engine.suggest_permission_grant("user1", "file.write", "Test", confidence=0.5)
        
        high_conf = engine.get_high_confidence_suggestions(0.85)
        assert len(high_conf) == 1
    
    def test_dismiss_suggestion(self, engine):
        """Test dismissing suggestion."""
        suggestion = engine.suggest_permission_grant("user1", "file.read", "Test")
        engine.dismiss_suggestion(suggestion.suggestion_id)
        
        assert engine.get_suggestion(suggestion.suggestion_id) is None


class TestPermissionIntegration:
    """Test integrated permission scenarios."""
    
    def test_rbac_with_resources(self):
        """Test RBAC system working with resource permissions."""
        rbac = RBACSystem()
        resource_mgr = ResourcePermissionManager()
        
        # Create resource owned by user1
        resource_mgr.create_resource(
            "project1",
            ResourceType.PROJECT,
            "MyProject",
            owner_id="user1"
        )
        
        # Assign user1 to user role
        rbac.assign_role("user1", PredefinedRole.USER.value)
        
        # Verify user can read resources
        assert rbac.has_permission("user1", PermissionName.FILE_READ)
        assert resource_mgr.has_permission("project1", "user1", ResourceAction.READ)
    
    def test_audit_with_permissions(self):
        """Test audit logging with permission grants."""
        rbac = RBACSystem()
        audit = AuditLogger()
        
        # Grant role to user
        rbac.assign_role("user1", PredefinedRole.USER.value)
        
        # Log the action
        audit.log_role_assigned("admin", "user1", PredefinedRole.USER.value)
        
        # Verify audit event
        events = audit.get_events(event_type=AuditEventType.ROLE_ASSIGNED)
        assert len(events) > 0
    
    def test_temp_grants_with_audit(self):
        """Test temporary grants with audit tracking."""
        grants = TemporaryGrantManager()
        audit = AuditLogger()
        
        # Create temporary grant
        grant = grants.create_grant(
            "user1",
            "file.delete",
            duration_seconds=3600,
            granted_by="admin"
        )
        
        # Log it
        audit.log_temp_grant_created(
            "admin",
            "user1",
            "file.delete",
            3600
        )
        
        # Verify tracking
        assert grants.has_grant("user1", "file.delete")
        events = audit.get_events(event_type=AuditEventType.TEMP_GRANT_CREATED)
        assert len(events) > 0
    
    def test_suggestions_from_rbac_state(self):
        """Test suggestions engine analyzing RBAC state."""
        rbac = RBACSystem()
        engine = PermissionSuggestionEngine()
        
        # Assign user to user role
        rbac.assign_role("user1", PredefinedRole.USER.value)
        current_perms = rbac.get_user_permissions("user1")
        
        # Get suggestions based on state
        suggestions = engine.suggest_principle_of_least_privilege(
            "user1",
            current_perms,
            {"file.read", "file.write"}
        )
        
        # Should suggest revoking excessive permissions
        assert len(suggestions) > 0
    
    def test_multi_role_permission_combination(self):
        """Test permissions from multiple roles combine correctly."""
        rbac = RBACSystem()
        
        # Create user with multiple roles
        rbac.assign_role("user1", PredefinedRole.USER.value)
        rbac.assign_role("user1", PredefinedRole.POWER_USER.value)
        
        # Get all permissions
        perms = rbac.get_user_permissions("user1")
        user_role = rbac.get_role(PredefinedRole.USER.value)
        power_role = rbac.get_role(PredefinedRole.POWER_USER.value)
        
        # Should have union of both roles' permissions
        assert perms >= user_role.permissions
        assert perms >= power_role.permissions
    
    def test_resource_ownership_hierarchy(self):
        """Test resource ownership and permission hierarchy."""
        mgr = ResourcePermissionManager()
        
        # Create resource hierarchy
        mgr.create_resource("project1", ResourceType.PROJECT, "Proj1", owner_id="owner1")
        mgr.create_resource("file1", ResourceType.FILE, "File1", owner_id="owner2")
        
        # Owner1 cannot access file1
        assert not mgr.has_permission("file1", "owner1", ResourceAction.READ)
        
        # But owner2 can
        assert mgr.has_permission("file1", "owner2", ResourceAction.READ)
    
    def test_audit_trail_completeness(self):
        """Test audit trail captures all permission changes."""
        rbac = RBACSystem()
        audit = AuditLogger()
        
        # Perform multiple permission operations
        rbac.assign_role("user1", PredefinedRole.USER.value)
        audit.log_role_assigned("admin", "user1", PredefinedRole.USER.value)
        
        rbac.remove_role("user1", PredefinedRole.USER.value)
        audit.log_role_removed("admin", "user1", PredefinedRole.USER.value)
        
        # Verify audit has both events
        all_events = audit.get_events(subject_id="user1")
        assert len(all_events) >= 2
        assert any(e.event_type == AuditEventType.ROLE_ASSIGNED for e in all_events)
        assert any(e.event_type == AuditEventType.ROLE_REMOVED for e in all_events)
    
    def test_temp_grant_with_revocation_audit(self):
        """Test temporary grant revocation is properly audited."""
        grants = TemporaryGrantManager()
        audit = AuditLogger()
        
        grant = grants.create_grant("user1", "file.delete", 3600, "admin")
        audit.log_temp_grant_created("admin", "user1", "file.delete", 3600)
        
        # Revoke it
        grants.revoke_grant(grant.grant_id)
        audit.log_temp_grant_expired("user1", "file.delete")
        
        # Verify audit shows revocation
        events = audit.get_events(subject_id="user1")
        assert len(events) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
