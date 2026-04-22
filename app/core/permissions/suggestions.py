"""Permission suggestions engine."""

from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger("hyena.permissions.suggestions")


class SuggestionType(Enum):
    """Types of suggestions."""
    GRANT = "grant"
    REVOKE = "revoke"
    PREVENT_ISSUE = "prevent_issue"
    OPTIMIZE = "optimize"
    SECURITY = "security"


class RiskLevel(Enum):
    """Risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PermissionSuggestion:
    """Permission suggestion."""
    suggestion_id: str
    user_id: str
    permission: str
    suggestion_type: SuggestionType
    reason: str
    risk_level: RiskLevel
    confidence: float  # 0.0 to 1.0
    affected_resources: List[str]
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "suggestion_id": self.suggestion_id,
            "user_id": self.user_id,
            "permission": self.permission,
            "type": self.suggestion_type.value,
            "reason": self.reason,
            "risk_level": self.risk_level.value,
            "confidence": round(self.confidence, 3),
            "affected_resources": self.affected_resources,
            "details": self.details,
        }


class PermissionSuggestionEngine:
    """AI-powered permission suggestion engine."""
    
    # Permission groups for related permissions
    FILE_PERMISSIONS = {
        "file.read",
        "file.write",
        "file.delete",
        "file.execute",
    }
    
    DANGEROUS_OPERATIONS = {
        "system.shutdown",
        "system.install",
        "git.force_push",
        "git.delete",
        "file.delete",
    }
    
    def __init__(self):
        """Initialize suggestion engine."""
        self.suggestions: Dict[str, PermissionSuggestion] = {}
        self.suggestion_counter = 0
        self.user_access_patterns: Dict[str, Dict[str, int]] = {}
    
    def _generate_suggestion_id(self) -> str:
        """Generate unique suggestion ID."""
        suggestion_id = f"sug_{self.suggestion_counter}"
        self.suggestion_counter += 1
        return suggestion_id
    
    def suggest_permission_grant(
        self,
        user_id: str,
        permission: str,
        reason: str,
        affected_resources: Optional[List[str]] = None,
        confidence: float = 0.8,
        risk_level: RiskLevel = RiskLevel.MEDIUM
    ) -> PermissionSuggestion:
        """Suggest granting permission."""
        suggestion = PermissionSuggestion(
            suggestion_id=self._generate_suggestion_id(),
            user_id=user_id,
            permission=permission,
            suggestion_type=SuggestionType.GRANT,
            reason=reason,
            risk_level=risk_level,
            confidence=confidence,
            affected_resources=affected_resources or [],
            details={
                "action": "grant",
                "permission": permission,
            }
        )
        
        self.suggestions[suggestion.suggestion_id] = suggestion
        logger.info(f"Generated suggestion: grant {permission} to {user_id} (confidence: {confidence})")
        
        return suggestion
    
    def suggest_permission_revoke(
        self,
        user_id: str,
        permission: str,
        reason: str,
        affected_resources: Optional[List[str]] = None,
        confidence: float = 0.8
    ) -> PermissionSuggestion:
        """Suggest revoking permission."""
        suggestion = PermissionSuggestion(
            suggestion_id=self._generate_suggestion_id(),
            user_id=user_id,
            permission=permission,
            suggestion_type=SuggestionType.REVOKE,
            reason=reason,
            risk_level=RiskLevel.LOW,
            confidence=confidence,
            affected_resources=affected_resources or [],
            details={
                "action": "revoke",
                "permission": permission,
            }
        )
        
        self.suggestions[suggestion.suggestion_id] = suggestion
        logger.info(f"Generated suggestion: revoke {permission} from {user_id}")
        
        return suggestion
    
    def suggest_based_on_usage(
        self,
        user_id: str,
        current_permissions: Set[str],
        recent_usage: Dict[str, int]
    ) -> List[PermissionSuggestion]:
        """Suggest permissions based on usage patterns."""
        suggestions = []
        
        # Track usage patterns
        if user_id not in self.user_access_patterns:
            self.user_access_patterns[user_id] = {}
        
        for perm, count in recent_usage.items():
            self.user_access_patterns[user_id][perm] = count
        
        # Suggest granting frequently used but missing permissions
        for perm, count in recent_usage.items():
            if perm not in current_permissions and count >= 3:
                suggestion = self.suggest_permission_grant(
                    user_id,
                    perm,
                    f"Used {count} times in recent history",
                    confidence=min(0.95, count / 10),
                    risk_level=RiskLevel.LOW if perm not in self.DANGEROUS_OPERATIONS else RiskLevel.HIGH
                )
                suggestions.append(suggestion)
        
        # Suggest revoking unused permissions
        for perm in current_permissions:
            if perm not in recent_usage:
                suggestion = self.suggest_permission_revoke(
                    user_id,
                    perm,
                    "Not used in recent history",
                    confidence=0.6
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def suggest_principle_of_least_privilege(
        self,
        user_id: str,
        current_permissions: Set[str],
        required_permissions: Set[str]
    ) -> List[PermissionSuggestion]:
        """Suggest permissions following principle of least privilege."""
        suggestions = []
        
        # Suggest revoking permissions beyond what's required
        excess_permissions = current_permissions - required_permissions
        for perm in excess_permissions:
            if perm not in self.DANGEROUS_OPERATIONS:
                suggestion = self.suggest_permission_revoke(
                    user_id,
                    perm,
                    f"Exceeds required permissions for role",
                    confidence=0.9,
                )
                suggestions.append(suggestion)
        
        # Suggest granting required but missing permissions
        missing_permissions = required_permissions - current_permissions
        for perm in missing_permissions:
            suggestion = self.suggest_permission_grant(
                user_id,
                perm,
                f"Required for role",
                confidence=0.95,
                risk_level=RiskLevel.LOW
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def suggest_related_permissions(
        self,
        user_id: str,
        permission: str,
        current_permissions: Set[str]
    ) -> List[PermissionSuggestion]:
        """Suggest related permissions."""
        suggestions = []
        
        # File operations - suggest related file permissions
        if permission in self.FILE_PERMISSIONS:
            for related in self.FILE_PERMISSIONS:
                if related not in current_permissions:
                    suggestion = self.suggest_permission_grant(
                        user_id,
                        related,
                        f"Related to {permission}",
                        confidence=0.7,
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def suggest_security_improvements(
        self,
        user_id: str,
        current_permissions: Set[str]
    ) -> List[PermissionSuggestion]:
        """Suggest security improvements."""
        suggestions = []
        
        # High risk permissions held by non-admins
        dangerous_count = len(current_permissions & self.DANGEROUS_OPERATIONS)
        
        if dangerous_count >= 3:
            # Suggestion to use temporary grants instead
            suggestion = PermissionSuggestion(
                suggestion_id=self._generate_suggestion_id(),
                user_id=user_id,
                permission="multiple_dangerous",
                suggestion_type=SuggestionType.SECURITY,
                reason="User has multiple dangerous permissions. Consider using temporary grants instead.",
                risk_level=RiskLevel.HIGH,
                confidence=0.9,
                affected_resources=list(current_permissions & self.DANGEROUS_OPERATIONS),
                details={
                    "action": "use_temporary_grants",
                    "dangerous_permissions": list(current_permissions & self.DANGEROUS_OPERATIONS),
                }
            )
            self.suggestions[suggestion.suggestion_id] = suggestion
            suggestions.append(suggestion)
        
        return suggestions
    
    def get_suggestion(self, suggestion_id: str) -> Optional[PermissionSuggestion]:
        """Get suggestion by ID."""
        return self.suggestions.get(suggestion_id)
    
    def list_suggestions(
        self,
        user_id: Optional[str] = None,
        suggestion_type: Optional[SuggestionType] = None,
        risk_level: Optional[RiskLevel] = None
    ) -> List[PermissionSuggestion]:
        """List suggestions."""
        suggestions = list(self.suggestions.values())
        
        if user_id:
            suggestions = [s for s in suggestions if s.user_id == user_id]
        if suggestion_type:
            suggestions = [s for s in suggestions if s.suggestion_type == suggestion_type]
        if risk_level:
            suggestions = [s for s in suggestions if s.risk_level == risk_level]
        
        # Sort by confidence descending
        suggestions.sort(key=lambda s: s.confidence, reverse=True)
        return suggestions
    
    def get_user_suggestions(self, user_id: str) -> List[PermissionSuggestion]:
        """Get all suggestions for user."""
        return self.list_suggestions(user_id=user_id)
    
    def get_high_confidence_suggestions(self, threshold: float = 0.85) -> List[PermissionSuggestion]:
        """Get high confidence suggestions."""
        return [s for s in self.suggestions.values() if s.confidence >= threshold]
    
    def dismiss_suggestion(self, suggestion_id: str) -> bool:
        """Dismiss suggestion."""
        if suggestion_id in self.suggestions:
            del self.suggestions[suggestion_id]
            logger.info(f"Dismissed suggestion: {suggestion_id}")
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        suggestions = list(self.suggestions.values())
        
        by_type = {}
        by_risk = {}
        
        for suggestion in suggestions:
            by_type[suggestion.suggestion_type.value] = by_type.get(suggestion.suggestion_type.value, 0) + 1
            by_risk[suggestion.risk_level.value] = by_risk.get(suggestion.risk_level.value, 0) + 1
        
        return {
            "total_suggestions": len(suggestions),
            "by_type": by_type,
            "by_risk_level": by_risk,
            "tracked_users": len(self.user_access_patterns),
        }
