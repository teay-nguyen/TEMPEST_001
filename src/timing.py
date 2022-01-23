
'''
    This python python is purely for debugging and timing purposes
    It is also used for performance tests
'''

# imports
from time import time

# main driver
class timer:
    def __init__(self):
        self.current_time = None
        self.time_log = []

    def init_time(self):
        self.current_time = time()

    def mark_time(self):
        assert self.current_time != None
        mark = time() - self.current_time
        self.time_log.append(mark)
