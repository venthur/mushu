from __future__ import division

from importlib import import_module
import logging
import select
import socket
import time
from threading import Thread, Lock
from multiprocessing import Process, Queue, Event

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
        self.marker_queue = Queue()
        self.tcp_reader_running = Event()
        self.tcp_reader_running.set()
        tcp_reader_ready = Event()
        self.tcp_reader = Process(target=tcp_reader, args=(self.marker_queue, self.tcp_reader_running, tcp_reader_ready ))
        self.tcp_reader.start()
        logger.debug('Waiting for TCP reader to become ready...')
        tcp_reader_ready.wait()
        logger.debug('TCP reader is ready...')
        # start the amp
        self.time = time.time()
        self.amp.start()

    def stop(self):
        # stop the amp
        self.amp.stop()
        # stop the marker server
        self.tcp_reader_running.clear()
        logger.debug('Waiting for TCP reader process to stop...')
        self.tcp_reader.join()
        logger.debug('TCP reader process stopped.')
        # close the files
        #self.fh.close()

    def configure(self, config):
        self.amp.configure(config)

    def configure_with_gui(self):
        self.amp.configure_with_gui()

    def get_data(self):
        # get data and marker from underlying amp
        data, marker = self.amp.get_data()
        # get tcp marker and merge them with markers from the amp
        self.time_old = self.time
        self.time = time.time()
        # merge markers
        # duration of the block / #samples gives the length of a sample
        # independently from the current sampling frequency.
        delta_t = self.time - self.time_old
        samples = len(data)
        t_sample = delta_t / samples
        tcp_marker = []
        while not self.marker_queue.empty():
            m = self.marker_queue.get()
            if not self._debug_tcp_marker_timestamps:
                m[0] = (m[0] - self.time_old) // t_sample
            tcp_marker.append(m)
        for m in tcp_marker:
            delay = (m[0] - float(m[1])) * 1000
            if delay > .5:
                logger.warning("Marker delay: %.4fms" % delay)
            #logger.debug("Marker delay: %.4fms" % delay)
        marker = sorted(marker + tcp_marker)
        # save data to files
        return data, marker

    def get_channels(self):
        return self.amp.get_channels()



def tcp_reader(queue, running, ready):
    # setup the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(0)
    server_socket.bind(('localhost', PORT))
    server_socket.listen(5)
    ready.set()
    # read the socket until 'running' is set to false
    rlist, wlist, elist = [server_socket], [], []
    while running.is_set():
        readables, _, _ = select.select(rlist, wlist, elist, 1)
        t = time.time()
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
                        for m in messages:
                            queue.put([t, m])
    logger.debug('Terminated select-loop')
    sock.close()

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
