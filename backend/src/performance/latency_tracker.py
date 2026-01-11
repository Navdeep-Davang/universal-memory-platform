import time
from contextlib import contextmanager
from typing import Dict, Any
from loguru import logger

class LatencyTracker:
    """
    A simple class to track and report latency of different stages in the pipeline.
    """
    
    def __init__(self):
        self.measurements: Dict[str, float] = {}

    @contextmanager
    def track(self, stage_name: str):
        """
        Context manager to track the duration of a specific block of code.
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self.measurements[stage_name] = duration
            logger.debug(f"Latency: {stage_name} took {duration*1000:.2f}ms")

    def get_report(self) -> Dict[str, float]:
        """
        Returns a dictionary of all measurements in seconds.
        """
        return self.measurements

    def get_formatted_report(self) -> Dict[str, str]:
        """
        Returns a dictionary of all measurements formatted as strings with 'ms' suffix.
        """
        return {k: f"{v*1000:.2f}ms" for k, v in self.measurements.items()}

    def total_latency(self) -> float:
        """
        Returns the sum of all measured stages.
        """
        return sum(self.measurements.values())

