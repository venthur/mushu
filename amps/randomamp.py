
import time
import math

import numpy as np

from amplifier import Amplifier


class RandomAmp(Amplifier):
    """An amplifier that produces random data."""

    def __init__(self):
        self.channels = 17
        self.fs = 100
        self.last_sample = time.time()

    @property
    def sample_len(self):
        return 1. / self.fs

    @property
    def elapsed(self):
        return time.time() - self.last_sample

    def get_data(self):
        # simulate blocking until we have enough data
        if self.elapsed < self.sample_len:
            time.sleep(self.sample_len - self.elapsed)
        dt = self.elapsed
        samples = math.floor(self.fs * dt)
        data = np.random.randint(0, 1024, (samples, self.channels))
        self.last_sample = time.time()
        return data


if __name__ == '__main__':
    amp = RandomAmp()
    amp.start()
    for i in range(10):
        t = time.time()
        print amp.get_data()
        print
        print "FS:", 1 / (time.time() - t)
        print
    amp.stop()

    # the same using a context manager, start and stop are called by the
    # context manager
    with amp as a:
        for i in range(10):
            print a.get_data()
