#!/usr/bin/env python3

import signal

class TriggerableContext:
    def __init__(self):
        self.triggered = False
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return
    def trigger(self, triggered=True):
        self.triggered = triggered

class Timeout(TriggerableContext):
    class TimeoutException(Exception):
        pass
    _used = False
    @staticmethod
    def _handler(signum, frame):
      raise Timeout.TimeoutException()
    def __init__(self, seconds=0):
        super().__init__()
        self.seconds = seconds
    def __enter__(self):
        if Timeout._used:
            raise RuntimeError("Timeout contexts can't be nested")
        Timeout._used = True
        signal.signal(signal.SIGALRM, self._handler)
        signal.alarm(self.seconds)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
        Timeout._used = False
        self.trigger(exc_type is Timeout.TimeoutException)
        return exc_type is None or self.triggered
