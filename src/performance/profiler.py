import time
import functools
import asyncio
from typing import Any, Callable
from loguru import logger

def profile_async(func: Callable) -> Callable:
    """
    Decorator for profiling asynchronous functions.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start_time
            logger.info(f"Profiler [Async]: {func.__name__} took {duration*1000:.2f}ms")
    return wrapper

def profile_sync(func: Callable) -> Callable:
    """
    Decorator for profiling synchronous functions.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start_time
            logger.info(f"Profiler [Sync]: {func.__name__} took {duration*1000:.2f}ms")
    return wrapper

class RecallProfiler:
    """
    A class to collect and analyze performance metrics across multiple recall operations.
    Can be used to calculate p95, averages, etc.
    """
    def __init__(self):
        self.metrics = []

    def record_operation(self, operation_name: str, duration: float, metadata: dict = None):
        metric = {
            "operation": operation_name,
            "duration": duration,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.metrics.append(metric)
        
        # Keep metrics manageable (e.g., last 1000)
        if len(self.metrics) > 1000:
            self.metrics.pop(0)

    def get_stats(self, operation_name: str = None) -> dict:
        target_metrics = self.metrics
        if operation_name:
            target_metrics = [m for m in self.metrics if m["operation"] == operation_name]
        
        if not target_metrics:
            return {}
            
        durations = [m["duration"] for m in target_metrics]
        durations.sort()
        
        count = len(durations)
        avg = sum(durations) / count
        p95 = durations[int(count * 0.95)]
        
        return {
            "count": count,
            "avg_ms": avg * 1000,
            "p95_ms": p95 * 1000,
            "min_ms": durations[0] * 1000,
            "max_ms": durations[-1] * 1000
        }

