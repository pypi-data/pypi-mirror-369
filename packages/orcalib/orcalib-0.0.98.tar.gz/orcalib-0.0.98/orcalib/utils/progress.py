import logging
from typing import Any, Callable

OnProgressCallback = Callable[[int, int], Any]
"""
Callback to record progress.

Args:
    step: The current step
    total: The total number of steps
"""

OnLogCallback = Callable[[dict[str, float]], Any]
"""
Callback to record log messages.

Args:
    log: The log message
"""


def safely_call_on_progress(on_progress: OnProgressCallback | None, step: int, total: int) -> None:
    """Safely call an on_progress callback, catching and logging any errors."""
    if on_progress is None:
        return
    try:
        on_progress(step, total)
    except Exception as e:
        logging.error("Error calling `on_progress` callback", exc_info=e)
