

from __future__ import division

import time

import numpy as np

from libmushu.amplifier import Amplifier


class ReplayAmp(Amplifier):

    def configure(self, data, marker, channels, fs, realtime=True, blocksize_ms=None, blocksize_samples=None):
        """

        Parameters
        ----------
        data
        marker
        channels
        fs
        realtime
        blocksize_ms : float
            blocksize in milliseconds
        blocksize_samples : int
            blocksize in samples

        Raises
        ------
        TypeError :
            if ``blocksize_ms`` and ``blocksize_s`` are given.

        """
        if [blocksize_ms, blocksize_samples].count(None) != 1:
            raise TypeError("blocksize_ms and blocksize_samples are mutually exclusive.")

        self.data = data
        # slow python
        self.marker = marker
        # fast numpy
        self.marker_ts = np.array([ts for ts, s in marker])
        self.marker_s = np.array([s for ts, s in marker])
        self.channels = channels
        self.fs = fs
        self.realtime = realtime

        if blocksize_ms:
            samples = fs * (blocksize_ms / 1000)
            if not samples.is_integer():
                raise ValueError("Resulting blocksize is not integer, please fix the blocksize_ms.")
            self.samples = int(samples)
        if blocksize_samples:
            self.samples = blocksize_samples

    def start(self):
        self.last_sample_time = time.time()
        self.pos = 0

    def stop(self):
        pass

    def get_data(self):
        """

        Returns
        -------
        chunk, markers: Markers is time in ms since relative to the
        first sample of that block.

        """
        if self.realtime:
            elapsed = time.time() - self.last_sample_time
            blocks = (self.fs * elapsed) // self.samples
            samples = blocks * self.samples
        else:
            samples = self.samples
        elapsed = samples / self.fs
        self.last_sample_time += elapsed
        # data
        chunk = self.data[self.pos:self.pos+samples]
        #self.data = self.data[samples:]
        # markers

        # slow python version
        #markers = [x for x in self.marker if x[0] < elapsed * 1000]
        #self.marker = [x for x in self.marker if x[0] >= elapsed * 1000]
        #self.marker = [[x[0] - elapsed * 1000, x[1]] for x in self.marker]

        # fast numpy version
        mask = self.marker_ts < (elapsed * 1000)
        markers = zip(self.marker_ts[mask], self.marker_s[mask])
        self.marker_ts = self.marker_ts[~mask]
        self.marker_s = self.marker_s[~mask]
        self.marker_ts -= elapsed * 1000

        self.pos += samples
        return chunk, markers

    def get_channels(self):
        return self.channels

    def get_sampling_frequency(self):
        return self.fs

    @staticmethod
    def is_available():
        return True
