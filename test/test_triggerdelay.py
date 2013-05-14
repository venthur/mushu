#!/usr/bin/env python

from __future__ import division

import unittest
import json
import socket
import time
import math

import libmushu
from libmushu.amps.randomamp import RandomAmp
from libmushu.amps.amplifier import Amplifier
import logging

import numpy as np
from matplotlib import pyplot as plt


logging.basicConfig(format='%(relativeCreated)10.0f %(processName)-11s %(threadName)-10s %(name)-10s %(levelname)8s %(message)s', level=logging.NOTSET)
logger = logging.getLogger(__name__)
logger.info('Logger started')


class TriggerTestAmp(Amplifier):
    """TriggerTestAmp.

    This amp sends marker just before and after its blocking sleep, along with
    the current timestamp as payload. On the receiving side one can use the
    payload to calculate the delay between sending and receiving triggers via
    TCP/IP.
    """

    def __init__(self):
        self.channels = 100
        self.fs = 100
        self.last_sample = time.time()

    def start(self):
        self._marker_count = 0
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('localhost', 12345))

    @property
    def sample_len(self):
        return 1. / self.fs

    @property
    def elapsed(self):
        return time.time() - self.last_sample

    def get_data(self):
        self.s.sendall("%f\n" % time.time())
        # simulate blocking until we have enough data
        elapsed = self.elapsed
        if elapsed < self.sample_len:
            time.sleep(self.sample_len - elapsed)
        self._marker_count += 1
        self.s.sendall("%f\n" % time.time())
        dt = self.elapsed
        samples = math.floor(self.fs * dt)
        data = np.random.randint(0, 1024, (samples, self.channels))
        self.last_sample = time.time()
        return data, [[samples-1, self._marker_count]]

    def configure(self, cfg):
        cfg = json.loads(cfg)
        self.fs = cfg['fs']


class TestTriggerDelay(unittest.TestCase):
    """Test the trigger delay."""

    def test_triggerdelay(self):
        """Mean and max delay must be reasonably small."""
        for i in 10, 100, 1000, 10000:
            logger.debug('Setting FS to {fs}kHz'.format(fs=(i / 1000)))
            amp = libmushu.AmpDecorator(TriggerTestAmp)
            amp._debug_tcp_marker_timestamps = True
            config = {"fs" : i}
            amp.configure(json.dumps(config))
            amp.start()
            delays = []
            for j in range(i*2):
                data, marker = amp.get_data()
                for timestamp, m in marker:
                    delta_t = (timestamp - float(m)) * 1000
                    delays.append(delta_t)
            amp.stop()
            delays = np.array(delays)
            logger.debug("Min: %.2f, Max: %.2f, Mean: %.2f, Std: %.2f" % (delays.min(), delays.max(), delays.mean(), delays.std()))
            self.assertLessEqual(delays.mean(), 1)
            self.assertLessEqual(delays.max(), 1)

if __name__ == '__main__':
    unittest.main()
