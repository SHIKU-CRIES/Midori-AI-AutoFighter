import time

class timmer:
    def __init__(self, timeout_seconds=15):
        self.timeout_seconds = timeout_seconds
        self.start_time = 0.0
        self.timed_out = False

    def start(self):
        """Starts the timer."""
        self.start_time = time.time()

    def check_timeout(self):
        """Checks if the timeout has been reached and updates timed_out."""
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            if elapsed_time > self.timeout_seconds:
                self.timed_out = True

    def reset(self):
        """Resets the timer to its initial state."""
        self.start_time = 0.0
        self.timed_out = False

    def get_timeout_duration(self):
        """Returns the number of seconds past the timeout as a float.
        If not timed out, returns 0.0.
        """
        if self.timed_out:
            return time.time() - self.start_time - self.timeout_seconds
        else:
            return 0.0
