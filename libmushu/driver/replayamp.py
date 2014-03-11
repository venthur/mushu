

from __future__ import division

import time

from libmushu.amplifier import Amplifier


class ReplayAmp(Amplifier):

    def configure(self, data, marker, channels, fs):
        self.data = data
        self.marker = marker
        self.channels = channels
        self.fs = fs

    def start(self):
        self.last_sample_time = time.time()

    def stop(self):
        pass

    def get_data(self):
        """

        Returns
        -------
        chunk, markers: Markers is time in ms since relative to the
        first sample of that block.

        """
        elapsed = time.time() - self.last_sample_time
        #self.last_sample_time = time.time()
        samples = int(self.fs * elapsed)
        elapsed = samples / self.fs
        self.last_sample_time += elapsed
        # data
        chunk = self.data[:samples]
        self.data = self.data[samples:]
        # markers
        markers = filter(lambda x: x[0] < elapsed * 1000, self.marker)
        self.marker = filter(lambda x: x[0] >= elapsed * 1000, self.marker)
        self.marker = map(lambda x: [x[0] - elapsed * 1000, x[1]], self.marker)
        return chunk, markers

    def get_channels(self):
        return self.channels

    def get_sampling_frequency(self):
        return self.fs

    @staticmethod
    def is_available():
        return True
