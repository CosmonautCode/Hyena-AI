"""Retry logic and error recovery utilities."""

import asyncio
import logging
from typing import Callable, Any, Optional, TypeVar, Union
from functools import wraps
import random

logger = logging.getLogger("hyena.utils.retry")

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """Initialize retry configuration.
        
        Args:
            max_attempts: Maximum retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add randomness to delays
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number.
        
        Args:
            attempt: Attempt number (0-based)
            
        Returns:
            float: Delay in seconds
        """
        delay = self.initial_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add random jitter (±20%)
            jitter_amount = delay * 0.2 * random.random()
            delay += jitter_amount
        
        return delay


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: bool = True,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying failed function calls.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts (seconds)
        backoff: Whether to use exponential backoff
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            config = RetryConfig(
                max_attempts=max_attempts,
                initial_delay=delay,
                exponential_base=2.0 if backoff else 1.0
            )
            
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    logger.debug(f"Attempt {attempt + 1}/{max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        wait_time = config.get_delay(attempt)
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}): {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        asyncio.run(asyncio.sleep(wait_time)) if asyncio.iscoroutinefunction(func) else __import__('time').sleep(wait_time)
                    else:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
            
            raise last_exception or exceptions[0]("All retry attempts failed")
        
        return wrapper
    
    return decorator


async def async_retry(
    func: Callable,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: bool = True,
    exceptions: tuple = (Exception,)
) -> Any:
    """Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_attempts: Maximum retry attempts
        delay: Initial delay between attempts
        backoff: Whether to use exponential backoff
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Return value of the function
        
    Raises:
        Last exception if all attempts fail
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        initial_delay=delay,
        exponential_base=2.0 if backoff else 1.0
    )
    
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            logger.debug(f"Async attempt {attempt + 1}/{max_attempts} for {func.__name__}")
            return await func()
        except exceptions as e:
            last_exception = e
            
            if attempt < max_attempts - 1:
                wait_time = config.get_delay(attempt)
                logger.warning(
                    f"{func.__name__} failed (attempt {attempt + 1}): {e}. "
                    f"Retrying in {wait_time:.1f}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"{func.__name__} failed after {max_attempts} attempts")
    
    raise last_exception or exceptions[0]("All retry attempts failed")


def with_fallback(
    fallback_value: Any = None,
    fallback_func: Optional[Callable] = None,
    exceptions: tuple = (Exception,)
):
    """Decorator for providing fallback values on failure.
    
    Args:
        fallback_value: Value to return on failure
        fallback_func: Function to call on failure
        exceptions: Exceptions to catch
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logger.warning(f"{func.__name__} failed: {e}. Using fallback.")
                
                if fallback_func is not None:
                    return fallback_func()
                return fallback_value
        
        return wrapper
    
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern implementation for error handling."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures before breaking circuit
            recovery_timeout: Time before attempting recovery
            expected_exception: Exception type to track
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception if circuit is open
        """
        if self.state == "OPEN":
            if self._should_attempt_recovery():
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker is OPEN. Retry in {self.recovery_timeout}s")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self) -> None:
        """Handle successful execution."""
        self.failure_count = 0
        self.success_count += 1
        
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            logger.info("Circuit breaker recovered to CLOSED state")
    
    def _on_failure(self) -> None:
        """Handle failed execution."""
        import time
        
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")
    
    def _should_attempt_recovery(self) -> bool:
        """Check if circuit should attempt recovery."""
        import time
        
        if self.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.recovery_timeout
