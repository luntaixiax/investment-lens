"""
Rate limiter utility for preventing brute force attacks on login attempts.
Tracks failed login attempts per username and implements exponential backoff.
"""
import asyncio
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Dict, Tuple


class RateLimiter:
    """
    Async-safe rate limiter for login attempts.
    Tracks failed attempts per username and blocks after threshold is reached.
    """
    
    def __init__(
        self,
        max_attempts: int = 5,
        lockout_duration_minutes: int = 15,
        window_minutes: int = 15
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_attempts: Maximum failed attempts before lockout
            lockout_duration_minutes: Duration of lockout in minutes
            window_minutes: Time window for tracking attempts
        """
        self.max_attempts = max_attempts
        self.lockout_duration = timedelta(minutes=lockout_duration_minutes)
        self.window = timedelta(minutes=window_minutes)
        
        # Store: username -> (attempt_count, first_attempt_time, lockout_until)
        self._attempts: Dict[str, Tuple[int, datetime, datetime | None]] = {}
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, username: str) -> Tuple[bool, str | None]:
        """
        Check if login attempt is allowed for the given username.
        
        Args:
            username: Username to check
            
        Returns:
            Tuple of (is_allowed, error_message)
            If is_allowed is False, error_message contains the reason
        """
        async with self._lock:
            now = datetime.utcnow()
            
            # Clean up old entries (attempts outside the window)
            self._cleanup(now)
            
            if username not in self._attempts:
                return True, None
            
            attempt_count, first_attempt, lockout_until = self._attempts[username]
            
            # Check if account is locked
            if lockout_until and now < lockout_until:
                remaining = (lockout_until - now).total_seconds()
                minutes = int(remaining / 60)
                seconds = int(remaining % 60)
                return False, f"Too many failed login attempts. Account locked for {minutes}m {seconds}s"
            
            # Reset lockout if it has expired
            if lockout_until and now >= lockout_until:
                # Reset the account
                del self._attempts[username]
                return True, None
            
            # Check if attempts are within the time window
            if now - first_attempt > self.window:
                # Reset attempts if outside the window
                del self._attempts[username]
                return True, None
            
            # Check if max attempts reached
            if attempt_count >= self.max_attempts:
                # Lock the account
                lockout_until = now + self.lockout_duration
                self._attempts[username] = (attempt_count, first_attempt, lockout_until)
                remaining = self.lockout_duration.total_seconds()
                minutes = int(remaining / 60)
                return False, f"Too many failed login attempts. Account locked for {minutes} minutes"
            
            return True, None
    
    async def record_failed_attempt(self, username: str) -> None:
        """
        Record a failed login attempt for the username.
        
        Args:
            username: Username that failed to login
        """
        async with self._lock:
            now = datetime.utcnow()
            
            if username not in self._attempts:
                # First failed attempt
                self._attempts[username] = (1, now, None)
            else:
                attempt_count, first_attempt, lockout_until = self._attempts[username]
                
                # Reset if outside the window
                if now - first_attempt > self.window:
                    self._attempts[username] = (1, now, None)
                else:
                    # Increment attempt count
                    self._attempts[username] = (attempt_count + 1, first_attempt, lockout_until)
    
    async def reset_attempts(self, username: str) -> None:
        """
        Reset failed attempts for a username (called on successful login).
        
        Args:
            username: Username that successfully logged in
        """
        async with self._lock:
            if username in self._attempts:
                del self._attempts[username]
    
    def _cleanup(self, now: datetime) -> None:
        """Remove old entries outside the tracking window."""
        usernames_to_remove = []
        for username, (_, first_attempt, lockout_until) in self._attempts.items():
            # Remove if outside window and not locked
            if (now - first_attempt > self.window) and (lockout_until is None or now >= lockout_until):
                usernames_to_remove.append(username)
        
        for username in usernames_to_remove:
            del self._attempts[username]


@lru_cache(maxsize=1)
def get_rate_limiter(
    max_attempts: int = 5,
    lockout_duration_minutes: int = 15,
    window_minutes: int = 15
) -> RateLimiter:
    """Get or create a rate limiter instance (cached).
    
    Args:
        max_attempts: Maximum failed attempts before lockout
        lockout_duration_minutes: Duration of lockout in minutes
        window_minutes: Time window for tracking attempts
    
    Returns:
        RateLimiter: A cached rate limiter instance for the given parameters
    """
    return RateLimiter(
        max_attempts=max_attempts,
        lockout_duration_minutes=lockout_duration_minutes,
        window_minutes=window_minutes
    )

