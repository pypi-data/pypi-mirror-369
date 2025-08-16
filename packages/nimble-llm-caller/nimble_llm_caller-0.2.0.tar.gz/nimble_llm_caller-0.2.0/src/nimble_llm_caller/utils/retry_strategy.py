"""
Retry strategies for LLM calls with exponential backoff and jitter.
"""

import time
import random
import logging
from typing import List, Callable, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class RetryableError(str, Enum):
    """Types of errors that should trigger retries."""
    RATE_LIMIT = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"
    SERVICE_UNAVAILABLE = "service_unavailable"
    TIMEOUT = "timeout"
    INTERNAL_SERVER_ERROR = "internal_server_error"
    BAD_GATEWAY = "bad_gateway"
    TOO_MANY_REQUESTS = "too_many_requests"
    CONNECTION_ERROR = "connection_error"
    TEMPORARY_FAILURE = "temporary_failure"


class RetryStrategy:
    """Configurable retry strategy with exponential backoff and jitter."""
    
    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        jitter_factor: float = 0.1
    ):
        """
        Initialize retry strategy.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            backoff_multiplier: Multiplier for exponential backoff
            jitter: Whether to add jitter to delays
            jitter_factor: Factor for jitter calculation (0.0 to 1.0)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.jitter_factor = jitter_factor
        
        # Default retryable error patterns
        self.retryable_patterns = [
            "rate limit",
            "quota exceeded",
            "service unavailable",
            "timeout",
            "internal server error",
            "bad gateway",
            "too many requests",
            "connection error",
            "temporary failure",
            "502",
            "503",
            "504"
        ]
    
    def is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error should trigger a retry.
        
        Args:
            error: The exception that occurred
            
        Returns:
            True if the error should be retried
        """
        error_str = str(error).lower()
        
        # Check for specific exception types
        import socket
        import requests
        
        retryable_exceptions = (
            socket.timeout,
            socket.gaierror,
            ConnectionError,
            TimeoutError,
        )
        
        # Add requests exceptions if available
        if hasattr(requests, 'exceptions'):
            retryable_exceptions += (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
            )
        
        if isinstance(error, retryable_exceptions):
            return True
        
        # Check for retryable patterns in error message
        return any(pattern in error_str for pattern in self.retryable_patterns)
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        # Calculate exponential backoff delay
        delay = min(self.base_delay * (self.backoff_multiplier ** attempt), self.max_delay)
        
        # Add jitter if enabled
        if self.jitter:
            jitter_amount = delay * self.jitter_factor
            jitter_offset = random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay + jitter_offset)
        
        return delay
    
    def execute_with_retry(
        self, 
        func: Callable[[], Any], 
        operation_name: str = "operation"
    ) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            operation_name: Name of the operation for logging
            
        Returns:
            Result of the function call
            
        Raises:
            Exception: The last exception if all retries failed
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.debug(f"Retry attempt {attempt}/{self.max_retries} for {operation_name}")
                
                result = func()
                
                if attempt > 0:
                    logger.info(f"{operation_name} succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Check if we should retry
                if not self.is_retryable_error(e) or attempt == self.max_retries:
                    if attempt == self.max_retries:
                        logger.error(f"Max retries ({self.max_retries}) reached for {operation_name}")
                    else:
                        logger.error(f"Non-retryable error for {operation_name}: {e}")
                    raise e
                
                # Calculate delay and wait
                delay = self.calculate_delay(attempt)
                logger.warning(f"Retryable error for {operation_name}: {e}. "
                             f"Retrying in {delay:.2f} seconds...")
                
                time.sleep(delay)
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError(f"Unexpected error in retry logic for {operation_name}")
    
    def get_stats(self) -> dict:
        """Get retry strategy statistics."""
        return {
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "backoff_multiplier": self.backoff_multiplier,
            "jitter_enabled": self.jitter,
            "jitter_factor": self.jitter_factor
        }


class AdaptiveRetryStrategy(RetryStrategy):
    """Adaptive retry strategy that adjusts based on success/failure patterns."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.success_count = 0
        self.failure_count = 0
        self.recent_failures = []
        self.adaptation_window = 10  # Number of recent calls to consider
    
    def record_success(self):
        """Record a successful operation."""
        self.success_count += 1
        # Gradually reduce delays if we're having consistent success
        if self.success_count % 5 == 0 and self.base_delay > 0.5:
            self.base_delay *= 0.9
            logger.debug(f"Reduced base delay to {self.base_delay:.2f}s due to consistent success")
    
    def record_failure(self, error: Exception):
        """Record a failed operation."""
        self.failure_count += 1
        self.recent_failures.append(time.time())
        
        # Keep only recent failures
        cutoff_time = time.time() - 300  # 5 minutes
        self.recent_failures = [t for t in self.recent_failures if t > cutoff_time]
        
        # Increase delays if we're having frequent failures
        if len(self.recent_failures) >= 3:
            self.base_delay = min(self.base_delay * 1.5, self.max_delay)
            logger.debug(f"Increased base delay to {self.base_delay:.2f}s due to recent failures")
    
    def execute_with_retry(self, func: Callable[[], Any], operation_name: str = "operation") -> Any:
        """Execute with adaptive retry logic."""
        try:
            result = super().execute_with_retry(func, operation_name)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure(e)
            raise
    
    def get_stats(self) -> dict:
        """Get adaptive retry strategy statistics."""
        base_stats = super().get_stats()
        base_stats.update({
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "recent_failures": len(self.recent_failures),
            "success_rate": self.success_count / (self.success_count + self.failure_count) if (self.success_count + self.failure_count) > 0 else 0.0
        })
        return base_stats


# Predefined retry strategies for common use cases
DEFAULT_RETRY = RetryStrategy()

AGGRESSIVE_RETRY = RetryStrategy(
    max_retries=10,
    base_delay=0.5,
    max_delay=30.0,
    backoff_multiplier=1.5
)

CONSERVATIVE_RETRY = RetryStrategy(
    max_retries=3,
    base_delay=2.0,
    max_delay=120.0,
    backoff_multiplier=3.0
)

FAST_RETRY = RetryStrategy(
    max_retries=5,
    base_delay=0.1,
    max_delay=5.0,
    backoff_multiplier=2.0
)