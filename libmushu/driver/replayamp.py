

from __future__ import division

import time

from libmushu.amplifier import Amplifier


class ReplayAmp(Amplifier):

    def configure(self, data, marker, channels, fs, realtime=True, samples=1):
        self.data = data
        self.marker = marker
        self.channels = channels
        self.fs = fs
        self.realtime = realtime
        self.samples = samples

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
            #self.last_sample_time = time.time()
            samples = int(self.fs * elapsed)
        else:
            samples = self.samples
        elapsed = samples / self.fs
        self.last_sample_time += elapsed
        # data
        chunk = self.data[self.pos:self.pos+samples]
        #self.data = self.data[samples:]
        # markers
        markers = [x for x in self.marker if x[0] < elapsed * 1000]
        self.marker = [x for x in self.marker if x[0] >= elapsed * 1000]
        self.marker = [[x[0] - elapsed * 1000, x[1]] for x in self.marker]

        self.pos += samples
        return chunk, markers

    def get_channels(self):
        return self.channels

    def get_sampling_frequency(self):
        return self.fs

    @staticmethod
    def is_available():
        return True
