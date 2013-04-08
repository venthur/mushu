from importlib import import_module
import logging


_available_amps = [['emotiv', 'Epoc'],
                   ['gtec', 'GUSBamp'],
                   ['randomamp', 'RandomAmp']]


logger = logging.getLogger(__name__)
logger.info('Logger started')

def get_available_amps():
    available_amps = []
    for mod, cls in _available_amps:
        try:
            m = import_module('libmushu.amps.' + mod)
        except ImportError, e:
            logger.warning('Unable to import %s' % mod, exc_info=True)
            continue
        try:
            c = getattr(m, cls)
            if c.is_available():
                available_amps.append(c)
        except:
            logger.warning('Unable to test if %s is available' % cls, exc_info=True)
    return available_amps
