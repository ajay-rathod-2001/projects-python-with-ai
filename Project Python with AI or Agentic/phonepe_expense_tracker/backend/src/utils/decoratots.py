"""
Utility Decorators for telemetry and performance monitoring
"""

import time
import logging
from typing import Callable

logger = logging.getLogger("PhonePeTracker")


def timer(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("%s executed in %.2f ms", func.__name__, duration_ms)
        return result

    return wrapper

