"""
Rate Limiter Middleware for FastAPI
"""
import time
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from typing import Dict, Tuple, List, Optional, Callable
import logging

# Configure logging
logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter middleware for FastAPI applications
    
    Implements a token bucket algorithm to limit API request rates.
    Requests are limited based on client IP address.
    """
    def __init__(
        self, 
        app: Optional[Callable] = None,
        requests_per_minute: int = 60,
        burst_limit: int = 10,
        exclude_paths: List[str] = None,
        exclude_ips: List[str] = None
    ):
        """
        Initialize the rate limiter
        
        Args:
            app: FastAPI application instance
            requests_per_minute: Maximum number of requests allowed per minute
            burst_limit: Maximum burst of requests allowed
            exclude_paths: List of path prefixes to exclude from rate limiting
            exclude_ips: List of IP addresses to exclude from rate limiting
        """
        self.app = app
        self.rate = requests_per_minute / 60  # Convert to requests per second
        self.max_tokens = burst_limit
        self.exclude_paths = exclude_paths or []
        self.exclude_ips = exclude_ips or []
        
        # Store token buckets for each client IP
        # {ip_address: (tokens, last_update_time)}
        self.buckets: Dict[str, Tuple[float, float]] = {}
        
        logger.info(f"Rate limiter initialized: {requests_per_minute} requests/minute, burst limit: {burst_limit}")
    
    def should_exclude_path(self, path: str) -> bool:
        """Check if the request path should be excluded from rate limiting"""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)
    
    def should_exclude_ip(self, ip: str) -> bool:
        """Check if the client IP should be excluded from rate limiting"""
        return ip in self.exclude_ips
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Try to get real IP from X-Forwarded-For header first (for proxied requests)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"
    
    def is_allowed(self, client_ip: str) -> bool:
        """
        Check if request is allowed based on rate limits
        
        Implements token bucket algorithm:
        - Each client has a bucket of tokens
        - Tokens are replenished at a fixed rate over time
        - Each request consumes a token
        - If no tokens are available, the request is rejected
        """
        current_time = time.time()
        
        # If this is a new client, initialize their bucket
        if client_ip not in self.buckets:
            self.buckets[client_ip] = (self.max_tokens - 1, current_time)
            return True
        
        # Get current token count and last update time
        tokens, last_update = self.buckets[client_ip]
        
        # Calculate time passed since last update
        time_passed = current_time - last_update
        
        # Replenish tokens based on time passed
        tokens = min(self.max_tokens, tokens + time_passed * self.rate)
        
        # If at least one token is available, allow the request
        if tokens >= 1:
            self.buckets[client_ip] = (tokens - 1, current_time)
            return True
        
        # Otherwise, update the last update time but don't allow the request
        self.buckets[client_ip] = (tokens, current_time)
        return False
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        FastAPI middleware entry point
        
        Args:
            request: FastAPI request object
            call_next: Function to call the next middleware or endpoint
        
        Returns:
            Response: Either the next middleware's response or a 429 error
        """
        # Skip rate limiting for excluded paths
        if self.should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Skip rate limiting for excluded IPs
        if self.should_exclude_ip(client_ip):
            return await call_next(request)
        
        # Check if request is allowed
        if self.is_allowed(client_ip):
            return await call_next(request)
        
        # Log rate limit exceeded
        logger.warning(f"Rate limit exceeded for IP: {client_ip}, path: {request.url.path}")
        
        # Return 429 Too Many Requests
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later."
            }
        ) 