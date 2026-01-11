import time
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import traceback
from src.config.environment import settings
import redis.asyncio as redis
from src.performance.production_monitoring import monitor

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
        
        # Record for production monitoring
        monitor.record_request(request.method, request.url.path, process_time)
        
        return response

class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
            
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != settings.API_KEY:
            logger.warning(f"Unauthorized access attempt to {request.url.path} from {request.client.host}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API Key"},
            )
        return await call_next(request)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: str, limit: int = 60):
        super().__init__(app)
        self.redis = redis.from_url(redis_url)
        self.limit = limit

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Use client IP or API Key for identification
        identifier = request.headers.get("X-API-Key") or request.client.host
        key = f"rate_limit:{identifier}"
        
        try:
            current_count = await self.redis.incr(key)
            if current_count == 1:
                await self.redis.expire(key, 60) # 1 minute window
            
            if current_count > self.limit:
                logger.warning(f"Rate limit exceeded for {identifier}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Please try again later."},
                )
        except Exception as e:
            logger.error(f"Rate limit error: {e}")
            # Fail open if Redis is down for development/stability
            pass
            
        return await call_next(request)

async def error_handler_middleware(request: Request, exc: Exception):
    logger.error(f"Error handling request {request.method} {request.url.path}: {exc}")
    logger.error(traceback.format_exc())
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

