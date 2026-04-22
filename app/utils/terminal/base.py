"""Base TerminalExecutor class and core functionality."""

from typing import Dict, List, Optional, Any, Callable
import subprocess
import os
import signal
import threading
import time
from pathlib import Path
import shlex

from .sync import SyncMixin
from .async_ops import AsyncMixin
from .process import ProcessMixin


class TerminalExecutor(SyncMixin, AsyncMixin, ProcessMixin):
    """Enhanced terminal command executor with async support."""
    
    def __init__(self):
        """Initialize the terminal executor."""
        self.running_processes = {}
        self.command_history = []
        self.output_handlers = {}
        self.process_id_counter = 0
