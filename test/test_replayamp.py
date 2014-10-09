from __future__ import division

from unittest import TestCase

import libmushu


class TestReplayAmp(TestCase):

    def setUp(self):
        self.amp = libmushu.get_amp('replayamp')

    def test_mutually_exclusive_blocksize_arguments(self):
        """blocksize_* are mutually exclusive."""
        try:
            self.amp.configure(data=None, marker=[], channels=None, fs=1000, blocksize_ms=10)
            self.amp.configure(data=None, marker=[], channels=None, fs=1000, blocksize_samples=10)
        except TypeError:
            self.fail()
        with self.assertRaises(TypeError):
            self.amp.configure(data=None, marker=[], channels=None, fs=1000, blocksize_ms=10, blocksize_samples=10)
        with self.assertRaises(TypeError):
            self.amp.configure(data=None, marker=[], channels=None, fs=1000, blocksize_ms=None, blocksize_samples=None)

    def test_blocksize_is_integer(self):
        """resulting blocksize must be integer."""
        with self.assertRaises(ValueError):
            # this will result in a blocksize of 2.4 and should fail
            self.amp.configure(data=None, marker=[], channels=None, fs=240, blocksize_ms=10)
        try:
            # this should result in a blocksize of 10
            self.amp.configure(data=None, marker=[], channels=None, fs=1000, blocksize_ms=10)
        except ValueError:
            self.fail()
