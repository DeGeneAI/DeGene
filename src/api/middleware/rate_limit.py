from fastapi import Request, HTTPException
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Simple in-memory rate limiting
RATE_LIMIT_DURATION = 60  # seconds
MAX_REQUESTS = 100  # requests per duration
request_counts = defaultdict(lambda: {"count": 0, "start_time": 0})

async def rate_limit_middleware(request: Request, call_next):
    try:
        client_ip = request.client.host
        current_time = time.time()
        
        # Reset counter if duration has passed
        if current_time - request_counts[client_ip]["start_time"] >= RATE_LIMIT_DURATION:
            request_counts[client_ip] = {"count": 0, "start_time": current_time}
        
        # Increment request count
        request_counts[client_ip]["count"] += 1
        
        # Check if rate limit exceeded
        if request_counts[client_ip]["count"] > MAX_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        response = await call_next(request)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in rate limit middleware: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 