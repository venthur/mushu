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

import libmushu

logging.basicConfig(format='%(relativeCreated)10.0f %(threadName)-10s %(name)-10s %(levelname)8s %(message)s', level=logging.NOTSET)
logger = logging.getLogger(__name__)
logger.info('Logger started')


class Gui(ttk.Frame):

    def __init__(self, master):
        self.amp_started = False

        ttk.Frame.__init__(self, master)
        self.master.title('Mushu')
        self.pack()

        available_amps = libmushu.get_available_amps()

        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=1)
        self.label1 = ttk.Label(frame, text='Select Amplifier')
        self.label1.grid(column=0, row=0, sticky='we')
        self.amp_combobox = ttk.Combobox(frame, values=[str(i) for i in available_amps])
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

        self.amp = available_amps[0]()

        self.channels = self.amp.get_channels()
        self.n_channels = len(self.channels)
        self.PAST_POINTS = 256
        self.SCALE = 30000

        self.init_plot()
        self.master.after_idle(self.visualizer)

    def onConnectButtonClicked(self):
        logger.debug('Connect.')

    def onDisconnectButtonClicked(self):
        logger.debug('Disconnect.')

    def onStartStopButtonClicked(self):
        logger.debug('Start.')
        if self.amp_started:
            logger.debug('Stop.')
            self.amp.stop()
            self.start_stop_button.config(text='Start')
            self.amp_started = False
        else:
            logger.debug('Start.')
            self.amp.start()
            self.start_stop_button.config(text='Stop')
            self.amp_started = True

    def onConfigureButtonClicked(self):
        self.amp.configure_with_gui()
        self.channels = self.amp.get_channels()
        self.n_channels = len(self.channels)

    def init_plot(self):
        self.axis.lines = []
        for i in range(self.n_channels):
            self.axis.plot(0)
        self.canvas.draw()
        self.data = np.array([]).reshape(-1, self.n_channels)
        self.data_buffer = []
        self.t2 = time.time()
        self.k = 0
        self.nsamples = 0

    def visualizer(self):
        tmp = self.amp.get_data()
        # display #samples / second
        if tmp is not None:
            self.nsamples += tmp.shape[0]
            self.k += 1
            if self.k == 100:
                sps = self.nsamples / (time.time() - self.t2)
                logger.debug('%.2f samples / second\r' % sps)
                self.t2 = time.time()
                self.nsamples = 0
                self.k = 0
        # check if nr of channels has changed since the last probe
        if tmp.shape[1] != self.data.shape[1]:
            logger.debug('Number of channels has changed, re-initializing the plot.')
            self.channels = self.amp.get_channels()
            self.n_channels = len(self.channels)
            self.init_plot()
        # append the new data
        new_data = tmp
        self.data = np.concatenate([self.data, new_data])
        self.data = self.data[-self.PAST_POINTS:]
        # plot the data
        data_clean = self.normalize(self.data)
        dmin = data_clean.min()
        dmax = data_clean.max()
        dr = (dmax - dmin) * 0.7
        SCALE = dr
        ticklocs = []
        x = [i for i in range(len(self.data))]
        for j, line in enumerate(self.axis.lines):
            line.set_xdata(x)
            #line.set_ydata(self.data[:, j] + j * SCALE)
            line.set_ydata(data_clean[:, j] + j * SCALE)
            ticklocs.append(j * SCALE)
        self.axis.set_ylim(-SCALE, self.n_channels * SCALE)
        self.axis.set_xlim(i - self.PAST_POINTS, i)
        self.axis.set_yticks(ticklocs)
        self.axis.set_yticklabels(self.channels)
        self.canvas.draw()
        #logger.debug('%.2f FPS' % (1 / (time.time() - t)))
        self.master.after(10, self.visualizer)

    def normalize(self, data):
        return data - np.average(data)

if __name__ == '__main__':
    root = tk.Tk()
    gui = Gui(root)
    gui.mainloop()

