import time


class Timer:
    def __init__(self) -> None:
        self.timeout = None

    def restart(self, timeout):
        self.timeout = timeout
        self._start_time = time.perf_counter()
    
    @property
    def elapsed_time(self):
        return time.perf_counter() - self._start_time

    @property
    def time_left(self):
        return self.timeout - self.elapsed_time

    def is_passed(self) -> bool:
        return self.elapsed_time > self.timeout

    def __repr__(self) -> str:
        return f'Timer({self.timeout})'


