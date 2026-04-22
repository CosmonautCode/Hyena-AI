"""Audit logging system for permissions and access."""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json

logger = logging.getLogger("hyena.permissions.audit")


class AuditEventType(Enum):
    """Types of audit events."""
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    PERMISSION_DENIED = "permission_denied"
    RESOURCE_CREATED = "resource_created"
    RESOURCE_DELETED = "resource_deleted"
    RESOURCE_ACCESSED = "resource_accessed"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    ROLE_CREATED = "role_created"
    ROLE_DELETED = "role_deleted"
    TEMP_GRANT_CREATED = "temp_grant_created"
    TEMP_GRANT_EXPIRED = "temp_grant_expired"
    TEMP_GRANT_REVOKED = "temp_grant_revoked"
    PERMISSION_CHANGED = "permission_changed"


class AuditSeverity(Enum):
    """Severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit log event."""
    event_type: AuditEventType
    timestamp: float
    actor_id: str  # Who performed the action
    subject_id: str  # Who/what was affected
    resource_id: Optional[str] = None
    action: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    severity: AuditSeverity = AuditSeverity.INFO
    result: str = "success"  # success, failure
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "actor_id": self.actor_id,
            "subject_id": self.subject_id,
            "resource_id": self.resource_id,
            "action": self.action,
            "details": self.details,
            "severity": self.severity.value,
            "result": self.result,
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


class AuditLogger:
    """Audit logging system."""
    
    def __init__(self, max_events: int = 10000):
        """Initialize audit logger."""
        self.events: List[AuditEvent] = []
        self.max_events = max_events
        self.listeners: List[callable] = []
    
    def log_event(
        self,
        event_type: AuditEventType,
        actor_id: str,
        subject_id: str,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        result: str = "success"
    ) -> AuditEvent:
        """Log audit event."""
        event = AuditEvent(
            event_type=event_type,
            timestamp=datetime.utcnow().timestamp(),
            actor_id=actor_id,
            subject_id=subject_id,
            resource_id=resource_id,
            action=action,
            details=details or {},
            severity=severity,
            result=result
        )
        
        self.events.append(event)
        
        # Remove oldest event if max reached
        if len(self.events) > self.max_events:
            self.events.pop(0)
        
        # Notify listeners
        for listener in self.listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error notifying audit listener: {e}")
        
        # Log to file
        log_level = {
            AuditSeverity.INFO: logging.INFO,
            AuditSeverity.WARNING: logging.WARNING,
            AuditSeverity.CRITICAL: logging.CRITICAL,
        }.get(severity, logging.INFO)
        
        logger.log(
            log_level,
            f"{event_type.value}: {actor_id} → {subject_id} ({result})"
        )
        
        return event
    
    def log_permission_granted(
        self,
        actor_id: str,
        subject_id: str,
        resource_id: Optional[str],
        permission: str,
        severity: AuditSeverity = AuditSeverity.INFO
    ) -> AuditEvent:
        """Log permission granted."""
        return self.log_event(
            AuditEventType.PERMISSION_GRANTED,
            actor_id,
            subject_id,
            resource_id,
            permission,
            {"permission": permission},
            severity
        )
    
    def log_permission_revoked(
        self,
        actor_id: str,
        subject_id: str,
        resource_id: Optional[str],
        permission: str,
        severity: AuditSeverity = AuditSeverity.INFO
    ) -> AuditEvent:
        """Log permission revoked."""
        return self.log_event(
            AuditEventType.PERMISSION_REVOKED,
            actor_id,
            subject_id,
            resource_id,
            permission,
            {"permission": permission},
            severity
        )
    
    def log_permission_denied(
        self,
        actor_id: str,
        resource_id: Optional[str],
        action: str,
        reason: str = "insufficient_permissions"
    ) -> AuditEvent:
        """Log permission denied."""
        return self.log_event(
            AuditEventType.PERMISSION_DENIED,
            actor_id,
            actor_id,
            resource_id,
            action,
            {"reason": reason},
            AuditSeverity.WARNING,
            result="failure"
        )
    
    def log_resource_accessed(
        self,
        user_id: str,
        resource_id: str,
        action: str
    ) -> AuditEvent:
        """Log resource access."""
        return self.log_event(
            AuditEventType.RESOURCE_ACCESSED,
            user_id,
            user_id,
            resource_id,
            action,
            {"action": action}
        )
    
    def log_role_assigned(
        self,
        actor_id: str,
        user_id: str,
        role_name: str
    ) -> AuditEvent:
        """Log role assignment."""
        return self.log_event(
            AuditEventType.ROLE_ASSIGNED,
            actor_id,
            user_id,
            None,
            role_name,
            {"role": role_name}
        )
    
    def log_role_removed(
        self,
        actor_id: str,
        user_id: str,
        role_name: str
    ) -> AuditEvent:
        """Log role removal."""
        return self.log_event(
            AuditEventType.ROLE_REMOVED,
            actor_id,
            user_id,
            None,
            role_name,
            {"role": role_name}
        )
    
    def log_temp_grant_created(
        self,
        actor_id: str,
        subject_id: str,
        permission: str,
        duration_seconds: int
    ) -> AuditEvent:
        """Log temporary grant creation."""
        return self.log_event(
            AuditEventType.TEMP_GRANT_CREATED,
            actor_id,
            subject_id,
            None,
            permission,
            {
                "permission": permission,
                "duration_seconds": duration_seconds
            }
        )
    
    def log_temp_grant_expired(
        self,
        subject_id: str,
        permission: str
    ) -> AuditEvent:
        """Log temporary grant expiration."""
        return self.log_event(
            AuditEventType.TEMP_GRANT_EXPIRED,
            "system",
            subject_id,
            None,
            permission,
            {"permission": permission}
        )
    
    def get_events(
        self,
        event_type: Optional[AuditEventType] = None,
        actor_id: Optional[str] = None,
        subject_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Query audit events."""
        events = self.events
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if actor_id:
            events = [e for e in events if e.actor_id == actor_id]
        if subject_id:
            events = [e for e in events if e.subject_id == subject_id]
        if resource_id:
            events = [e for e in events if e.resource_id == resource_id]
        
        # Return most recent events first
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[AuditEvent]:
        """Get user activity."""
        events = [e for e in self.events if e.actor_id == user_id or e.subject_id == user_id]
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    def get_resource_access_log(self, resource_id: str, limit: int = 100) -> List[AuditEvent]:
        """Get access log for resource."""
        events = [e for e in self.events if e.resource_id == resource_id]
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    def add_listener(self, callback: callable) -> None:
        """Add event listener."""
        self.listeners.append(callback)
    
    def remove_listener(self, callback: callable) -> None:
        """Remove event listener."""
        self.listeners.remove(callback)
    
    def export_events(self, filepath: str) -> None:
        """Export events to file."""
        with open(filepath, 'w') as f:
            for event in self.events:
                f.write(event.to_json() + '\n')
        logger.info(f"Exported {len(self.events)} audit events to {filepath}")
    
    def clear_events(self) -> None:
        """Clear all audit events."""
        self.events.clear()
        logger.info("Cleared all audit events")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit statistics."""
        event_counts = {}
        for event in self.events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "total_events": len(self.events),
            "event_types": event_counts,
            "denials": len([e for e in self.events if e.result == "failure"]),
            "criticals": len([e for e in self.events if e.severity == AuditSeverity.CRITICAL]),
        }
