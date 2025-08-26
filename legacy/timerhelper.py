class timmer:
    def __init__(self, timeout_ticks=1200):
        self.timeout_ticks = timeout_ticks
        self.start_tick = 0
        self.total_ticks = 0
        self.timed_out = False
        self.current_tick = 0
        self.printed = False

    def start(self):
        """Starts the timer."""
        self.start_tick = self.current_tick

    def check_timeout(self):
        """Checks if the timeout has been reached and updates timed_out."""
        if self.start_tick is not None:
            elapsed_ticks = self.current_tick - self.start_tick
            if elapsed_ticks > self.timeout_ticks:
                self.timed_out = True

    def reset(self):
        """Resets the timer to its initial state."""
        self.start_tick = 0
        self.current_tick = 0
        self.timed_out = False
        self.printed = False

    def get_timeout_duration(self):
        """Returns the number of seconds past the timeout as a float.
        If not timed out, returns 0.0.
        """
        if self.timed_out:
            elapsed_ticks = self.current_tick - self.start_tick - self.timeout_ticks
            duration = (elapsed_ticks * 0.001) + 1
            if not self.printed:
                print(f"Timeout duration :: {duration}")
                self.printed = True
            return duration
        return 0.0

    def get_total_ticks(self):
        return self.total_ticks

    def tick(self):
        """Increments the current tick counter."""
        self.current_tick += 1
        self.total_ticks += 1
