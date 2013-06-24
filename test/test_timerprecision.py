from __future__ import division
import time
import unittest


class TestTimerPrecision(unittest.TestCase):

    def test_precision(self):
        """The precision of the timer must be at least 10us."""
        # collect as many timestamps as possible in 1 second, remove the
        # duplicates and count the number of elements
        times = []
        t_start = time.time()
        while time.time() < t_start + 1:
            times.append(time.time())
        # remove duplicates
        times = list(set(times))
        resolution = (max(times) - min(times)) / len(times)
        self.assertLessEqual(resolution, 10*1e-6)


if __name__ == '__main__':
    unittest.main()
