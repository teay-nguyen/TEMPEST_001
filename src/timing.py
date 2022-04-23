
'''
    This python python is purely for debugging and timing purposes
    It is also used for performance tests
'''

'''
    Logic behind this code is extremely silly, but I just need a way to store the times I need
    because timing the performance of the code is important for speed and calculating power of PyPioneer
'''

# imports
from time import time

# main driver
class timer:
    def __init__(self):
        self.current_time = None
        self.timers_started = []
        self.time_log = []

    def init_time(self):
        self.current_time = time()
        self.timers_started.append(self.current_time)

    def mark_time(self):
        assert self.current_time != None
        mark = time() - self.current_time
        self.time_log.append(mark)

    @property
    def latest_time_mark(self):
        return self.time_log[-1]
