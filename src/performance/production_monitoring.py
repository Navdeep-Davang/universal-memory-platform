import time
from loguru import logger
from src.performance.profiler import RecallProfiler
from typing import Dict, Any

class ProductionMonitor:
    """
    Aggregates and reports production metrics like p50, p95, p99 latencies.
    """
    
    def __init__(self):
        self.profiler = RecallProfiler()
        self.last_report_time = time.time()
        self.report_interval = 60  # Report every 60 seconds

    def record_request(self, method: str, path: str, duration: float):
        """
        Records a single request duration.
        """
        operation_name = f"{method} {path}"
        self.profiler.record_operation(operation_name, duration)
        
        # Check if it's time to report
        if time.time() - self.last_report_time > self.report_interval:
            self.report_metrics()

    def report_metrics(self):
        """
        Calculates and logs aggregated metrics.
        """
        # Get all operation names
        ops = set(m["operation"] for m in self.profiler.metrics)
        
        for op in ops:
            stats = self.profiler.get_stats(op)
            if stats:
                logger.info(
                    f"PROD_METRICS | {op} | "
                    f"Count: {stats['count']} | "
                    f"Avg: {stats['avg_ms']:.2f}ms | "
                    f"p95: {stats['p95_ms']:.2f}ms | "
                    f"Min: {stats['min_ms']:.2f}ms | "
                    f"Max: {stats['max_ms']:.2f}ms"
                )
        
        self.last_report_time = time.time()

# Global monitor instance
monitor = ProductionMonitor()

