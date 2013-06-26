from __future__ import division

from importlib import import_module
import logging

from libmushu.ampdecorator import AmpDecorator


__all__ = ['supported_amps', 'get_available_amps', 'get_amp']


# TODO: low level driver must have a real name to 
supported_amps = {
    'epoc': ['emotiv', 'Epoc'],
    'gusbamp': ['gtec', 'GUSBamp'],
    'randomamp': ['randomamp', 'RandomAmp']
}


logger = logging.getLogger(__name__)
logger.info('Logger started')


def get_available_amps():
    """Retrieves all available (e.g. connected) amplifiers.

    This method tests all supported amplifiers if they are connected to the
    system. More precisely: if the amplifiers `is_available` method returns
    True.

    Returns:
        A list of the names of the amplifiers which are available.

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


    This factory method takes a low level amplifier driver, wraps it in an
    AmpDecorator and returns an instance.

    Args:
        ampname: A string representing the desired amplifier. The string must
            be a key in the supported_amps dictionary.

    Returns:
        An amplifier instance.

    """
    mod, cls = supported_amps.get(ampname)
    m = import_module('libmushu.driver.' + mod)
    c = getattr(m, cls)
    return AmpDecorator(c)

