"""Context manager for handling timeouts."""

import contextlib
import signal


class TimeoutException(Exception):
    """Exception raised when a timeout occurs."""

    def __init__(self, seconds: int):
        super().__init__(f"Execution exceeded {seconds}s")
        self.seconds = seconds


@contextlib.contextmanager
def timeout(seconds: int):
    """
    Context manager that raises a TimeoutException if the block takes longer than the
    specified time.

    Uses signals, so it only works on Unix-like systems (Linux, macOS, etc.).
    """

    # function to execute when the timer expires
    def signal_handler(signum, frame):
        raise TimeoutException(seconds=seconds)

    signal.setitimer(signal.ITIMER_REAL, seconds)  # start timer
    signal.signal(signal.SIGALRM, signal_handler)  # set end of timer signal

    try:
        yield

    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)  # stop timer
