#!/usr/bin/env python


from multiprocessing import Process, Pipe, Event
import logging
import time

import matplotlib
matplotlib.use('GTKAgg')
from gi.repository import Gtk, GObject
from matplotlib.figure import Figure
from backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

GObject.threads_init()

import numpy as np



from amps import gtec


logging.basicConfig(format='%(asctime)s %(name)-10s %(levelname)8s %(message)s', level=logging.NOTSET)
logger = logging.getLogger(__name__)
logger.info('Logger started')


#amp = gtec.GTecAmp()
#amp.start()
#amp.start_recording()

from amps.randomamp import RandomAmp
amp = RandomAmp()

class Gui(object):


    def __init__(self, q):
        self.q = q
        self.builder = Gtk.Builder()
        self.builder.add_from_file('gusbamptool.glade')
        handler = {
                'onDeleteWindow' : self.onDeleteWindow,
                'onConnectButtonClicked' : self.onConnectButtonClicked,
                'onDisconnectButtonClicked' : self.onDisconnectButtonClicked,
                'onStartButtonClicked' : self.onStartButtonClicked,
                'onStopButtonClicked' : self.onStopButtonClicked,
                'onSetFilterButtonClicked' : self.onSetFilterButtonClicked,
                'onComboBoxChanged' : self.onComboBoxChanged,
                'onComboBox2Changed' : self.onComboBox2Changed,
                'onSamplingFrequencyComboBoxChanged' : self.onSamplingFrequencyComboBoxChanged
                }
        self.builder.connect_signals(handler)
        window = self.builder.get_object('window1')
        window.show_all()

        # set up the figure
        fig = Figure()
        self.canvas = FigureCanvas(fig)
        self.canvas.show()
        self.canvas.set_size_request(800, 600)
        self.axis = fig.add_subplot(111)
        place = self.builder.get_object('box1')
        place.pack_start(self.canvas, True, True, 0)
        place.reorder_child(self.canvas, 1)

        self.CHANNELS = 17
        self.PAST_POINTS = 256
        self.SCALE = 30000

        self.init_plot()
        GObject.idle_add(self.visualizer)


    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onConnectButtonClicked(self, button):
        logger.debug('Connect.')

    def onDisconnectButtonClicked(self, button):
        logger.debug('Disconnect.')

    def onStartButtonClicked(self, button):
        logger.debug('Start.')
        amp.start_recording()

    def onStopButtonClicked(self, button):
        logger.debug('Stop.')
        amp.stop_recording()

    def onSetFilterButtonClicked(self, button):
        channels = [True for i in range(16)]

        combo = self.builder.get_object('comboboxtext_fs')
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            fs = int(row_id)


        if self.builder.get_object('checkbutton_notch').get_active():
            notch_order = self.builder.get_object('spin_order_notch').get_value_as_int()
            notch_hp = self.builder.get_object('spin_hp_notch').get_value()
            notch_lp = self.builder.get_object('spin_lp_notch').get_value()
            notchfilter = (notch_hp, notch_lp, fs, notch_order)
        else:
            notchfilter = None

        if self.builder.get_object('checkbutton_band').get_active():
            band_order = self.builder.get_object('spin_order_band').get_value_as_int()
            band_hp = self.builder.get_object('spin_hp_band').get_value()
            band_lp = self.builder.get_object('spin_lp_band').get_value()
            bpfilter = (band_hp, band_lp, fs, band_order)
        else:
            bpfilter = None

        amp.set_sampling_ferquency(fs, channels, bpfilter, notchfilter)
        pass


    def onComboBoxChanged(self, combo):
        logger.debug('ComboBox changed.')
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            logger.debug("Selected: ID=%s, name=%s" % (row_id, name))
            if row_id == 'Data':
                amp.set_mode('data')
            elif row_id == 'Impedance':
                amp.set_mode('impedance')
            elif row_id == 'Calibration':
                amp.set_mode('calibrate')


    def onComboBox2Changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            if row_id == 'Sine':
                amp.set_calibration_mode('sine')
            elif row_id == 'Sawtooth':
                amp.set_calibration_mode('sawtooth')
            elif row_id == 'White Noise':
                amp.set_calibration_mode('whitenoise')
            elif row_id == 'Square':
                amp.set_calibration_mode('square')
            elif row_id == 'DLR':
                amp.set_calibration_mode('dlr')
            else:
                logger.error('Unknown row_id: %s' % row_id)


    def onSamplingFrequencyComboBoxChanged(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            fs = int(row_id)
            amp.set_sampling_ferquency(fs, [False for i in range(16)], None, None)


    def init_plot(self):
        for i in range(self.CHANNELS):
            self.axis.plot(0)
        self.canvas.draw()
        self.data = []
        self.data_buffer = []
        self.t2 = time.time()
        self.k = 0
        self.nsamples = 0


    def visualizer(self):

        t = time.time()
        tmp = self.q.recv()
        while self.q.poll():
            tmp = np.append(tmp, self.q.recv())
        # display #samples / second
        if tmp != None:
            self.nsamples += len(tmp)
            self.k += 1
            if self.k == 100:
                sps = (self.nsamples / self.CHANNELS) / (time.time() - self.t2)
                logger.debug('%.2f samples / second\r' % sps)
                self.t2 = time.time()
                self.nsamples = 0
                self.k = 0
            #logger.debug(tmp)
        if tmp == 'quit':
            return False
        elif tmp is None:
            return True
        # get #CHANNELS * data points into data and the rest in data_buffer
        self.data_buffer = np.append(self.data_buffer, tmp)
        self.data = np.append(self.data, self.data_buffer)
        elements = (len(self.data) / self.CHANNELS) * self.CHANNELS
        self.data_buffer = self.data[elements:]
        self.data = self.data[:elements].reshape(-1, self.CHANNELS)

        self.data = self.data[-self.PAST_POINTS:]
        if len(self.data) == 0:
            return True
        #SCALE = np.max(self.data)
        #SCALE *= 2
        SPAN = 100000
        SCALE = SPAN
        j = self.CHANNELS - 1
        x = [i for i in range(len(self.data))]
        for line in self.axis.lines:
            line.set_xdata(x)
            line.set_ydata(self.data[:, j] + j * SCALE)
            j -= 1
        self.axis.set_ylim(-SCALE, self.CHANNELS * SCALE)
        self.axis.set_xlim(i - self.PAST_POINTS, i)
        #yticksmin = [-SCALE+SCALE*i for i in range(CHANNELS)]
        #yticksmax = [SCALE*i for i in range(CHANNELS)]
        #pos = []
        #for i in range(CHANNELS):
        #    pos.append(yticksmin[i])
        #    pos.append(yticksmax[i])
        #plt.yticks(pos, [-SCALE/2, SCALE]*CHANNELS)
        self.canvas.draw()
        logger.debug('%.2f FPS' % (1 / (time.time() - t)))
        return True


def data_fetcher(amp, q, e):
    while not e.is_set():
        try:
            data_buffer = amp.get_data()
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
    gui = Gui(child_conn)
    # setup the data fetcher
    e = Event()
    p = Process(target=data_fetcher, args=(amp, parent_conn, e))
    p.daemon = True
    logger.debug(p.daemon)
    p.start()
    Gtk.main()
    logger.debug('Waiting for thread and process to stop...')
    e.set()
    p.join()

