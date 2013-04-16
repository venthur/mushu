from importlib import import_module
import logging


_available_amps = [['emotiv', 'Epoc'],
                   ['gtec', 'GUSBamp'],
                   ['randomamp', 'RandomAmp']]


logger = logging.getLogger(__name__)
logger.info('Logger started')


class AmpDecorator():
    """This class 'decorates' the Low-Level Amplifier classes with Marker and
    Save-To-File functionality.
    """

    def __init__(self, ampcls):
        self.amp = ampcls()

    def start(self, filename=None):
        if filename is not None:
            self.fh = open(filename, 'bw')
        # TODO: start the marker server
        self.amp.start()

    def stop(self):
        self.amp.stop()
        # TODO: stop the marker server
        self.fh.close()

    def configure(self, config):
        self.amp.configure(config)

    def configure_with_gui(self):
        self.amp.configure_with_gui()

    def get_data(self):
        return self.amp.get_data()

    def get_channels(self):
        return self.amp.get_channels()



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
