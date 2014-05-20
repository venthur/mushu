from __future__ import division

import time
import logging

import numpy as np
import pylsl

from libmushu.amplifier import Amplifier


logger = logging.getLogger(__name__)
logger.info('Logger started.')


class LSLAmp(Amplifier):
    """Pseudo Amplifier for lab streaming layer (lsl).

    This amplifier connects to an arbitrary EEG device that is
    publishing its data via lsl to the network. With this class you can
    use this amplifier like a normal `mushu` amplifier.

    https://code.google.com/p/labstreaminglayer/

    Examples
    --------

    >>> amp = libmushu.get_amp('lslamp')
    >>> amp.configure()
    >>> amp.start()
    >>> while True:
    ...     data, marker = amp.get_data()
    ...     # do something with data and/or break the loop
    >>> amp.stop()

    """

    def configure(self):
        """Configure the lsl device.

        This method looks for open lsl streams and picks the first `EEG`
        and `Markers` streams and opens lsl inlets for them.

        Note that lsl amplifiers cannot be configured via lsl, as the
        protocol was not designed for that. You can only connect (i.e.
        subscribe) to devices that connected (publishing) via the lsl
        protocol.

        """
        # lsl defined
        self.max_samples = 1024
        # open EEG stream
        streams = pylsl.resolve_stream('type', 'EEG')
        if len(streams) > 1:
            logger.warning('Number of EEG streams is > 0, picking the first one.')
        self.lsl_inlet = pylsl.StreamInlet(streams[0])
        # open marker stream
        streams = pylsl.resolve_stream('type', 'Markers')
        if len(streams) > 1:
            logger.warning('Number of Marker streams is > 0, picking the first one.')
        self.lsl_marker_inlet = pylsl.StreamInlet(streams[0])
        info = self.lsl_inlet.info()
        self.n_channels = info.channel_count()
        self.fs = info.nominal_srate()
        # storage for markers that arrived w/o samples
        self._markers = []
        self._m_timestamps = []

    def start(self):
        """Open the lsl inlets.

        """
        logger.debug('Opening lsl streams.')
        self.lsl_inlet.open_stream()
        self.lsl_marker_inlet.open_stream()

    def stop(self):
        """Close the lsl inlets.

        """
        logger.debug('Closing lsl streams.')
        self.lsl_inlet.close_stream()
        self.lsl_marker_inlet.close_stream()

    def get_data(self):
        """Receive a chunk of data an markers.

        Returns
        -------
        chunk, markers: Markers is time in ms since relative to the
        first sample of that block.

        """
        samples, timestamps = self.lsl_inlet.pull_chunk(timeout=0.0, max_samples=self.max_samples)
        markers, m_timestamps = self.lsl_marker_inlet.pull_chunk(timeout=0.0, max_samples=self.max_samples)

        # put any leftover markers back into the loop
        if self._markers:
            markers = self._markers + markers
            m_timestamps = self._m_timestamps + m_timestamps
            self._markers = []
            self._m_timestamps = []

        samples = np.array(samples).reshape(-1, self.n_channels)
        markers = np.array(markers)

        m_timestamps = np.array(timestamps)
        if len(m_timestamps) > 0:
            if len(timestamps) > 0:
                m_timestamps -= timestamps[0]
            else:
                # we received markers, but no data, so we cannot
                # calculate the relative time to the first sample, we
                # store the markers until the next sample arrived
                self._markers.extend(markers)
                self._m_timestamps.extend(m_timestamps)
                markers = []
                m_timestamps = []

        # convert timestamps to ms
        m_timestamps *= 1000

        return samples, zip(markers, m_timestamps)

    def get_channels(self):
        """Get channel names.

        """
        ['Ch %i' % i for i in range(self.n_channels)]
        return self.channels

    def get_sampling_frequency(self):
        """Get the sampling frequency of the lsl device.

        """
        return self.fs

    @staticmethod
    def is_available():
        """Check if an lsl stream is available on the network.

        Returns
        -------

        ok : Boolean
            True if there is a lsl stream, False otherwise

        """
        # Return True only if at least one lsl stream can be found on
        # the network
        if pylsl.resolve_streams():
            return True
        return False

