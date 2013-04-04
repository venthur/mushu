#!/usr/bin/env python


from multiprocessing import Process, Pipe, Event
from threading import Thread
import logging
import time
import pkgutil
import ttk
import Tkinter as tk

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas

import numpy as np

from libmushu.amps import gtec
from libmushu.amps import emotiv
from libmushu.amps.randomamp import RandomAmp

logging.basicConfig(format='%(asctime)s %(name)-10s %(levelname)8s %(message)s', level=logging.NOTSET)
logger = logging.getLogger(__name__)
logger.info('Logger started')


#amp = gtec.GTecAmp()
amp = RandomAmp()
#amp = emotiv.Epoc()

class Gui(ttk.Frame):

    def __init__(self, master, q):
        self.amp_started = False

        ttk.Frame.__init__(self, master)
        self.master.title('Mushu')

        self.style = ttk.Style()
        self.style.theme_use('default')

        self.pack()
        self.q = q

        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=1)
        self.label1 = ttk.Label(frame, text='Select Amplifier')
        self.label1.grid(column=0, row=0, sticky='we')
        self.amp_combobox = ttk.Combobox(frame, values=['Foo', 'Bar', 'Baz'])
        self.amp_combobox.grid(column=0, row=1, sticky='we')
        self.label2 = ttk.Label(frame, text='Configure Amplifier')
        self.label2.grid(column=1, row=0, sticky='we')
        self.configure_button = ttk.Button(frame, text='Configure', command=self.onConfigureButtonClicked)
        self.configure_button.grid(column=1, row=1, sticky='we')
        self.label3 = ttk.Label(frame, text='Start/Stop Amplifier')
        self.label3.grid(column=2, row=0, sticky='we')
        self.start_stop_button = ttk.Button(frame, text='Start', command=self.onStartStopButtonClicked)
        self.start_stop_button.grid(column=2, row=1, sticky='we')

        # set up the figure
        fig = Figure()
        self.canvas = FigureCanvas(fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.show()
        self.axis = fig.add_subplot(111)

        self.CHANNELS = 14
        self.PAST_POINTS = 256
        self.SCALE = 30000

        self.init_plot()
        Thread(target=self.visualizer).start()

    def onConnectButtonClicked(self):
        logger.debug('Connect.')

    def onDisconnectButtonClicked(self):
        logger.debug('Disconnect.')

    def onStartStopButtonClicked(self):
        logger.debug('Start.')
        if self.amp_started:
            logger.debug('Stop.')
            amp.stop()
            self.start_stop_button.config(text='Start')
            self.amp_started = False
        else:
            logger.debug('Start.')
            amp.start()
            self.start_stop_button.config(text='Stop')
            self.amp_started = True

    def onConfigureButtonClicked(self):
        amp.configure_with_gui()

    def init_plot(self):
        for i in range(self.CHANNELS):
            self.axis.plot(0)
        self.canvas.draw()
        self.data = np.array([]).reshape(-1, self.CHANNELS)
        self.data_buffer = []
        self.t2 = time.time()
        self.k = 0
        self.nsamples = 0

    def visualizer(self):
        while 1:
            t = time.time()
            tmp = []
            tmp.append(self.q.recv())
            while self.q.poll():
                i = self.q.recv()
                if i == 'quit':
                    return
                if i is None:
                    continue
                tmp.append(i)
            # display #samples / second
            if tmp != None:
                self.nsamples += sum([i.shape[0] for i in tmp])
                self.k += 1
                if self.k == 100:
                    sps = self.nsamples / (time.time() - self.t2)
                    logger.debug('%.2f samples / second\r' % sps)
                    self.t2 = time.time()
                    self.nsamples = 0
                    self.k = 0
            # append the new data
            new_data = np.concatenate(tmp)
            self.data = np.concatenate([self.data, new_data])
            self.data = self.data[-self.PAST_POINTS:]
            # plot the data
            data_clean = self.normalize(self.data)
            dmin = data_clean.min()
            dmax = data_clean.max()
            dr = (dmax - dmin) * 0.7
            SCALE = dr
            x = [i for i in range(len(self.data))]
            for j, line in enumerate(self.axis.lines):
                line.set_xdata(x)
                #line.set_ydata(self.data[:, j] + j * SCALE)
                line.set_ydata(data_clean[:, j] + j * SCALE)
            self.axis.set_ylim(-SCALE, (1 + self.CHANNELS) * SCALE)
            self.axis.set_xlim(i - self.PAST_POINTS, i)
            self.canvas.draw()
            #logger.debug('%.2f FPS' % (1 / (time.time() - t)))
            continue

    def normalize(self, data):
        return data - np.average(data)

def data_fetcher(amp, q, e):
    while not e.is_set():
        try:
            data_buffer = amp.get_data()[:,[2,3,4,5,6,7,8,9, 10, 11, 12, 13, 14, 15]]
        except:
            data_buffer = None
        q.send(data_buffer)
    logger.debug('Sending visualizer process the stop marker.')
    q.send('quit')
    logger.debug('Terminating data fetcher thread.')


if __name__ == '__main__':
    # setup the visualizer process
    parent_conn, child_conn = Pipe()
    # setup the gtk gui
    root = tk.Tk()
    gui = Gui(root, child_conn)
    # setup the data fetcher
    e = Event()
    p = Process(target=data_fetcher, args=(amp, parent_conn, e))
    p.daemon = True
    logger.debug(p.daemon)
    p.start()
    gui.mainloop()
    logger.debug('Waiting for thread and process to stop...')
    e.set()
    p.join()

