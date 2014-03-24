# amplifier.py
# Copyright (C) 2013  Bastian Venthur
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


"""
This module provides the :class:`Amplifier` class, which is the base
class of all low level amplifier drivers. If you want to write a driver
for a specific amplifier your driver must derive from the
:class:`Amplifier` class and implement its methods.

Users will not use your driver directly but a decorated version of it
which provides additional features like writing data to a file and
receiving marker via TCP.

"""

class Amplifier(object):
    """Amplifier base class.

    The base class is very generic on purpose. Amplifiers from different
    vendors vary in so many ways that it is difficult to find a common
    set of methods that all support.

    In the spirit of "encapsulating what varies", I decided to
    encapsulate the configuration. So the main configuration of the
    amplifier, like setting the mode (e.g. data, impedance, etc.),
    sampling frequency, etc. happens in :meth:`configure` and is very
    specific for the amplifier at hand.

    :meth:`start`, :meth:`stop`, and :meth:`get_data` is very generic
    and must be supported by all derived amplifier classes.

    How an amplifier should be used::

        amp = Amp()

        # measure impedance
        amp.configure(**config)
        amp.start()
        while 1:
            data = amp.get_data()
            if enough:
                break
        amp.stop()

        # measure data
        amp.configure(**config)
        channels = amp.get_channels()
        amp.start()
        while 1:
            data = amp.get_data()
            if enough:
                break
        amp.stop()

    """

    presets = []


    def configure(self, **kwargs):
        """Configure the amplifier.

        Use this method to set the mode (i.e. impedance, data, ...),
        sampling frequency, filter, etc.

        This depends strongly on the amplifier.

        Parameters
        ----------
        kwargs : dict
            the configuration of the amplifier

        """
        pass

    def start(self):
        """Make the amplifier ready for delivering data."""
        pass

    def stop(self):
        """Stop the amplifier."""
        pass

    def get_data(self):
        """Get data from the amplifier.

        This method is called as fast as possible (e.g. hundreds of
        times per second) and returns the data and the marker (if
        supported).

        Returns
        -------
        data : ndarray
            a numpy array (time, channels) of the EEG data
        markers : list of (float, str)
            a list of markers. Each element is a tuple of timestamp and
            string. The timestamp is the time in ms relative to the
            onset of the block of data. Note that negative values are
            *allowed* as well as values bigger than the length of the
            block of data returned. That is to be interpreted as a
            marker from the last block and a marker for a future block
            respectively.

        Examples
        --------

        Create a very slow amplifier with 1Hz and 3 channels and send
        some markers:

        >>> amp = libmushu.get_amp('randomamp')
        >>> amp.configure(fs=1, channels=3)
        >>> amp.start()
        >>> while True:
        ...     time.sleep(.5)
        ...     data, marker = amp.get_data()
        ...     print '---'
        ...     print data
        ...     print marker
        ...
        ---
        [[590 938  72]]
        [[98.75297546386719, 'foo'], [553.4558296203613, 'bar']]
        ---
        [[167 168  40]]
        []
        ---
        [[727 705 934]]
        [[16.066789627075195, 'baz']]

        """
        pass

    def get_channels(self):
        """Return the list of channel names.

        The list has the same order as the data, i.e. the second name in
        the list represents the second colum of the data returned by
        :meth:`get_data`.

        Returns
        -------
        channels : list of strings
            the channel names

        """
        raise NotImplementedError

    def get_sampling_frequency(self):
        """Return the sampling frequency.

        This method returns the sampling frequency which is currently
        enabled in the amplifier.

        Returns
        -------
        fs : float
            the sampling frequency

        """
        raise NotImplementedError

    @staticmethod
    def is_available():
        """Is the amplifier connected to the computer?

        This method should be overwritten by derived classes and return
        True if the amplifier is connected to the computer or False if
        not.

        Returns
        -------
        available : boolean

        """
        raise NotImplementedError

