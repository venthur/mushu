from __future__ import division
import time
import unittest


class TestTimerPrecision(unittest.TestCase):

    def test_precision(self):
        """The precision of the timer must be at least 1ms."""
        times = [time.time()]
        t_start = times[0]
        while 1:
            t = time.time()
            if t >= (t_start + 1):
                break
            if times[-1] != t:
                times.append(t)
        # how many different
        precision = 1000 / len(times)
        print precision
        self.assertLessEqual(precision, 1)


if __name__ == '__main__':
    unittest.main()
