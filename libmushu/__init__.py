from importlib import import_module
import logging
import select
import socket
import time
from threading import Thread, Lock


END_MARKER = '\n'
BUFSIZE = 2**16
PORT = 12345


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
        # prepare files for writing
        if filename is not None:
            self.fh = open(filename, 'bw')
        # start the marker server
        self.shared = {'running' : True,
                       'time': time.time(),
                       'block' : 0,
                       'lock' : Lock(),
                       'markers' : []
                       }
        self.tcp_reader = Thread(target=tcp_reader, args=(self.shared, ))
        self.tcp_reader.start()
        time.sleep(1)
        # start the amp
        self.amp.start()

    def stop(self):
        # stop the amp
        self.amp.stop()
        # stop the marker server
        self.shared['running'] = False
        self.tcp_reader.join()
        # close the files
        self.fh.close()

    def configure(self, config):
        self.amp.configure(config)

    def configure_with_gui(self):
        self.amp.configure_with_gui()

    def get_data(self):
        # get data and marker from underlying amp
        data, marker = self.amp.get_data()
        # get tcp marker and merge them with markers from the amp
        with self.shared['lock']:
            time_old = self.shared['time']
            self.shared['time'] = time.time()
            self.shared['block'] = self.shared['block'] + 1
        # merge markers
        # duration of the block / #samples gives the length of a sample
        # independently from the current sampling frequency.
        delta_t = self.shared['time'] - time_old
        samples = len(data)
        t_sample = delta_t / samples
        tcp_marker = map(lambda x: [int(x[1] // t_sample), x[2]], self.shared['markers'])
        self.shared['markers'] = []
        marker = sorted(marker + tcp_marker)
        # save data to files
        if marker:
            logger.debug(marker)
        return data, marker

    def get_channels(self):
        return self.amp.get_channels()



def tcp_reader(shared):
    # setup the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(0)
    server_socket.bind(('localhost', PORT))
    server_socket.listen(5)
    # read the socket until 'running' is set to false
    rlist, wlist, elist = [server_socket], [], []
    while shared['running']:
        readables, _, _ = select.select(rlist, wlist, elist, 1)
        delta_t  = time.time() - shared['time']
        with shared['lock']:
            for sock in readables:
                if sock == server_socket:
                    # a new connection is opened
                    connection, address = sock.accept()
                    logger.debug('Incoming connection from %s', address)
                    rlist.append(connection)
                    data_buffer = ''
                else:
                    data = sock.recv(BUFSIZE)
                    if not data:
                        # an open connection was closed
                        logger.debug('Connection closed')
                        sock.close()
                        rlist.remove(sock)
                    else:
                        # received maybe incomplete data from a
                        # connection
                        data_buffer = ''.join([data_buffer, data])
                        split = data_buffer.rsplit(END_MARKER, 1)
                        messages = []
                        if len(split) > 1:
                            # data_buffer contains at least one complete
                            # message
                            data_buffer = split[1]
                            messages = split[0].split(END_MARKER)
                            shared['markers'].extend([[shared['block'], delta_t, m] for m in messages])

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
