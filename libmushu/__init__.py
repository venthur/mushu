# __init__.py
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
This module provides two functions: :func:`get_available_amps` which
will tell you which amplifiers are currently available on your computer,
and :func:`get_amp` which you can use to get an amplifier instance to
work with.

How to use libmushu with the decorated drivers (recommended)::

    import libmushu

    # you know what amp you want to use:
    amp = libmushu.get_amp('epoc')
    ...

    # Or: you select one of the available amps:
    amps = libmushu.get_available_amps()
    amp = libmushu.get_amp(amps[0])
    ...

How to use the libmushu's low level driver drivers::

    from libmushu.driver.randomamp import RandomAmp
    amp = RandomAmp()

You'll will most likely want to use the decorated drivers and only deal
with the low level drivers if you're a developer or find that the
:class:`libmushu.ampdecorator.AmpDecorator` does not provide the
features you need.

"""


from __future__ import division

from importlib import import_module
import logging

from libmushu.ampdecorator import AmpDecorator

__version__ = '0.2'

__all__ = ['supported_amps', 'get_available_amps', 'get_amp']


# TODO: low level driver must have a real name?
supported_amps = {
    'epoc': ['emotiv', 'Epoc'],
    'gusbamp': ['gtec', 'GUSBamp'],
    'randomamp': ['randomamp', 'RandomAmp'],
    'sinusamp' : ['sinusamp', 'SinusAmp'],
    'replayamp' : ['replayamp', 'ReplayAmp'],
    'lslamp' : ['labstreaminglayer', 'LSLAmp']
}


logger = logging.getLogger(__name__)
logger.info('Logger started')


def get_available_amps():
    """Retrieves all available (e.g. connected) amplifiers.

    This method tests all supported amplifiers if they are connected to
    the system. More precisely: if the amplifiers `is_available` method
    returns True.

    Returns
    -------
    available_amps : list of strings
        a list of the names of the amplifiers which are available

    Examples
    --------

    >>> import libmushu as lm
    >>> lm.get_available_amps()
    ['gusbamp', 'randomamp']

    """
    available_amps = []
    for name, (mod, cls) in supported_amps.items():
        try:
            m = import_module('libmushu.driver.' + mod)
        except ImportError:
            logger.warning('Unable to import %s' % mod, exc_info=True)
            continue
        try:
            c = getattr(m, cls)
            if c.is_available():
                available_amps.append(name)
        except:
            logger.warning('Unable to test if %s is available' % cls, exc_info=True)
    return available_amps


def get_amp(ampname):
    """Get an amplifier instance.


    This factory method takes a low level amplifier driver, wraps it in
    an AmpDecorator and returns an instance.

    Parameters
    ----------
    ampname : str
        the desired amplifier. The string must be a key in the
        :data:`supported_amps` dictionary.

    Returns
    -------
    amp : Amplifier
        an amplifier instance

    Examples
    --------

    >>> import libmushu as lm
    >>> amps = lm.get_available_amps()
    >>> amp = lm.get_amp(amps[0])

    """
    mod, cls = supported_amps.get(ampname)
    m = import_module('libmushu.driver.' + mod)
    c = getattr(m, cls)
    return AmpDecorator(c)

