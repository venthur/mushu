#!/usr/bin/env python


import threading
from threading import Thread
from multiprocessing import Process, Pipe
import logging

import gtec


logging.basicConfig(format='%(asctime)s %(name)10s %(levelname)8s %(message)s', level=logging.NOTSET)
logger = logging.getLogger(__name__)
logger.info('Logger started')


amp = gtec = gtec.GTecAmp()
amp.start()
amp.start_recording()

# signal to stop the data fetching thread and visualizer process
FETCHER_THREAD_STOPPING = False


class Gui(object):


    def __init__(self):
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


    def onDeleteWindow(self, *args):
        global FETCHER_THREAD_STOPPING
        FETCHER_THREAD_STOPPING = True
        Gtk.main_quit(*args)

    def onConnectButtonClicked(self, button):
        print 'Connect.'

    def onDisconnectButtonClicked(self, button):
        print 'Disconnect.'

    def onStartButtonClicked(self, button):
        print 'Start.'
        amp.start_recording()

    def onStopButtonClicked(self, button):
        print 'Stop.'
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
        print 'ComboBox changed.'
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            print "Selected: ID=%s, name=%s" % (row_id, name)
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
                print 'Unknown row_id: %s' % row_id


    def onSamplingFrequencyComboBoxChanged(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            fs = int(row_id)
            amp.set_sampling_ferquency(fs, [False for i in range(16)], None, None)


def data_fetcher(amp, q):
    while not FETCHER_THREAD_STOPPING:
        try:
            data_buffer = amp.get_data()
        except:
            data_buffer = None
        q.send(data_buffer)
    print 'Sending visualizer process the stop marker.'
    q.send('quit')
    print 'Terminating data fetcher thread.'


def visualizer(q):
    # import our stuff, since we're in a new process
    import time

    import gobject
    import matplotlib
    matplotlib.use('GTKAgg')
    from matplotlib import pyplot as plt
    import numpy as np


    CHANNELS = 17
    PAST_POINTS = 256
    SCALE = 30000

    fig = plt.figure()

    def main():
        ax = plt.subplot(111)
        for i in range(CHANNELS):
            ax.plot(0)
        fig.canvas.draw()
        data = []
        data_buffer = []
        while 1:
            t = time.time()
            #if not q.poll(0.1):
            #    continue
            tmp = q.recv()
            if tmp == 'quit':
                break
            elif tmp is None:
                tmp = [0 for i in range(CHANNELS)]
            # get #CHANNELS * data points into data and the rest in data_buffer
            data_buffer = np.append(data_buffer, tmp)
            if len(data_buffer) % CHANNELS == 0:
                data = np.append(data, data_buffer)
                data_buffer = []
            else:
                data = np.append(data, data_buffer[:-(len(data_buffer) % CHANNELS)])
                data_buffer = data_buffer[-(len(data_buffer) % CHANNELS):]
            # reshape and shorten
            data = np.reshape(data, (-1, CHANNELS))
            data = data[-PAST_POINTS:]
            SCALE = np.max(data) / 8.15
            SCALE *= 2
            j = CHANNELS - 1
            for line in ax.lines:
                line.set_xdata([i for i in range(len(data))])
                line.set_ydata(data[:, j]/8.15 + j*SCALE)
                ax.draw_artist(line)
                j -= 1
            plt.ylim(-SCALE, CHANNELS*SCALE)
            plt.xlim(i-PAST_POINTS, i)
            fig.canvas.draw()
            print '%.2f FPS' % (1/ (time.time() - t))

    gobject.idle_add(main)
    plt.show()

    print 'Terminating visualizer process.'


if __name__ == '__main__':
    # setup the visualizer process
    parent_conn, child_conn = Pipe()
    p = Process(target=visualizer, args=(child_conn,))
    p.start()
    # setup the gtk gui
    from gi.repository import Gtk, GObject
    GObject.threads_init()

    gui = Gui()
    # setup the data fetcher
    t = Thread(target=data_fetcher, args=(amp, parent_conn))
    t.start()
    Gtk.main()
    print 'Waiting for thread and process to stop...'
    t.join()
    p.join()

