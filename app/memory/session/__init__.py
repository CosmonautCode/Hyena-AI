"""Session management system for Hyena CLI."""

from .base import SessionManager
from .conversation import ConversationMixin
from .stats import StatsMixin

# Combine the classes
class UnifiedSessionManager(ConversationMixin, StatsMixin, SessionManager):
    """Unified session and conversation manager."""
    pass

__all__ = ['UnifiedSessionManager']
