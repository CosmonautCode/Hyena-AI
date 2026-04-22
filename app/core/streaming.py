"""
Streaming response infrastructure for token-by-token LLM output.

Provides async streaming support with callbacks and error handling.
Enables real-time response display in UI.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional, AsyncIterator, List
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


@dataclass
class StreamToken:
    """Represents a single token in stream."""
    token: str
    position: int
    timestamp: float
    is_complete: bool = False


@dataclass
class StreamMetrics:
    """Metrics for streaming session."""
    total_tokens: int = 0
    total_time: float = 0.0
    tokens_per_second: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class StreamCallback(ABC):
    """Base class for stream callbacks."""

    @abstractmethod
    async def on_token(self, token: StreamToken) -> None:
        """Called when new token received."""
        pass

    @abstractmethod
    async def on_complete(self, metrics: StreamMetrics) -> None:
        """Called when stream complete."""
        pass

    @abstractmethod
    async def on_error(self, error: Exception) -> None:
        """Called when error occurs."""
        pass


class ConsoleStreamCallback(StreamCallback):
    """Prints tokens to console in real-time."""

    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.buffer = ""

    async def on_token(self, token: StreamToken) -> None:
        """Print token to console."""
        self.buffer += token.token
        print(token.token, end='', flush=True)

    async def on_complete(self, metrics: StreamMetrics) -> None:
        """Print completion info."""
        print()  # Newline
        logger.info(
            f"Stream complete: {metrics.total_tokens} tokens "
            f"in {metrics.total_time:.2f}s "
            f"({metrics.tokens_per_second:.1f} tok/s)"
        )

    async def on_error(self, error: Exception) -> None:
        """Log error."""
        logger.error(f"Stream error: {error}")
        print(f"\n[ERROR] {error}")


class ListStreamCallback(StreamCallback):
    """Collects tokens into a list."""

    def __init__(self):
        self.tokens: List[StreamToken] = []

    async def on_token(self, token: StreamToken) -> None:
        """Add token to list."""
        self.tokens.append(token)

    async def on_complete(self, metrics: StreamMetrics) -> None:
        """No-op."""
        pass

    async def on_error(self, error: Exception) -> None:
        """Log error."""
        logger.error(f"Stream error: {error}")

    def get_text(self) -> str:
        """Get concatenated tokens as text."""
        return ''.join(t.token for t in self.tokens)


class StreamManager:
    """Manages streaming operations with callbacks."""

    def __init__(self):
        self.callbacks: List[StreamCallback] = []
        self.metrics = StreamMetrics()

    def add_callback(self, callback: StreamCallback) -> None:
        """Register callback."""
        self.callbacks.append(callback)

    def remove_callback(self, callback: StreamCallback) -> None:
        """Unregister callback."""
        self.callbacks.remove(callback)

    async def emit_token(self, token: str, position: int) -> None:
        """Emit token to all callbacks."""
        stream_token = StreamToken(
            token=token,
            position=position,
            timestamp=datetime.now().timestamp()
        )
        
        for callback in self.callbacks:
            try:
                await callback.on_token(stream_token)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    async def emit_complete(self) -> None:
        """Emit completion to all callbacks."""
        if self.metrics.start_time:
            self.metrics.end_time = datetime.now().timestamp()
            self.metrics.total_time = self.metrics.end_time - self.metrics.start_time
            if self.metrics.total_time > 0:
                self.metrics.tokens_per_second = (
                    self.metrics.total_tokens / self.metrics.total_time
                )

        for callback in self.callbacks:
            try:
                await callback.on_complete(self.metrics)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    async def emit_error(self, error: Exception) -> None:
        """Emit error to all callbacks."""
        for callback in self.callbacks:
            try:
                await callback.on_error(error)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    async def stream(
        self,
        text_generator: AsyncIterator[str]
    ) -> str:
        """Stream text from generator, emitting tokens.

        Args:
            text_generator: Async generator yielding text chunks

        Returns:
            Complete text
        """
        self.metrics = StreamMetrics()
        self.metrics.start_time = datetime.now().timestamp()
        
        complete_text = ""
        position = 0

        try:
            async for chunk in text_generator:
                for token in chunk:
                    complete_text += token
                    await self.emit_token(token, position)
                    self.metrics.total_tokens += 1
                    position += 1
                    
                    # Brief yield to prevent blocking
                    await asyncio.sleep(0)

            await self.emit_complete()
        except Exception as e:
            logger.error(f"Stream error: {e}")
            await self.emit_error(e)
            raise

        return complete_text


class ResponseStreamer:
    """High-level interface for streaming LLM responses."""

    def __init__(self):
        self.manager = StreamManager()

    async def stream_response(
        self,
        response_generator: AsyncIterator[str],
        console: bool = True,
        collect: bool = False
    ) -> str:
        """Stream response with optional callbacks.

        Args:
            response_generator: Async generator yielding response chunks
            console: Print to console
            collect: Collect into list

        Returns:
            Complete response text
        """
        if console:
            self.manager.add_callback(ConsoleStreamCallback())

        list_callback = None
        if collect:
            list_callback = ListStreamCallback()
            self.manager.add_callback(list_callback)

        try:
            complete_text = await self.manager.stream(response_generator)
            return complete_text
        finally:
            if console and self.manager.callbacks:
                self.manager.callbacks.pop(0)
            if list_callback:
                self.manager.remove_callback(list_callback)


async def create_mock_stream(
    text: str,
    delay: float = 0.01
) -> AsyncIterator[str]:
    """Create mock stream for testing.

    Args:
        text: Text to stream
        delay: Delay between tokens

    Yields:
        Characters from text
    """
    for char in text:
        await asyncio.sleep(delay)
        yield char
