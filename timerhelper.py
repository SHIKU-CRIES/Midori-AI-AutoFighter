class timmer:
    def __init__(self, timeout_ticks=2500):
        self.timeout_ticks = timeout_ticks
        self.start_tick = 0
        self.timed_out = False
        self.current_tick = 0

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
        self.timed_out = False

    def get_timeout_duration(self):
        """Returns the number of seconds past the timeout as a float.
        If not timed out, returns 0.0.
        """
        if self.timed_out:
            elapsed_ticks = self.current_tick - self.start_tick - self.timeout_ticks
            return (elapsed_ticks * 0.001) + 1
        else:
            return 0.0

    def tick(self):
        """Increments the current tick counter."""
        self.current_tick += 1
