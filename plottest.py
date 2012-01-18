#!/usr/bin/env python


import itertools
import math
import sys
import time
import threading

import gobject
import matplotlib
matplotlib.use('GTKAgg')
from matplotlib import pyplot as plt
import numpy as np

import gtec

PAST_POINTS = 256
CHANNELS = 17
SCALE = 3000 #10

fig = plt.figure()

def main():
    amp = gtec.GTecAmp()
    amp.start()
    amp.stop_recording()
    amp.set_mode('calibrate')
    amp.start_recording()

    ax = plt.subplot(111)
    for i in range(CHANNELS):
        ax.plot(0)
    fig.canvas.draw()
    data_buffer = []
    data = []
    for i in itertools.count():
        t = time.time()

        #data_buffer = np.append(data_buffer, amp.get_data())
        data_buffer = amp.get_data()

        mask = (len(data_buffer) / CHANNELS) * CHANNELS
        #print 'truncating data with holds more than 17 channesl'
        data = np.append(data, data_buffer[:mask])
        data = data[-PAST_POINTS*CHANNELS:]
        data_buffer = data_buffer[mask:]
        data2 = np.reshape(data, (-1, CHANNELS))
        #print data
        data2 = data2[-PAST_POINTS:]
        # plot the data
        j = CHANNELS - 1
        for line in ax.lines:
            #line.set_data(x_values, y_values[j] + j*210)
            line.set_xdata([i for i in range(len(data2))])
            line.set_ydata(data2[:,j]/8.15 + j*SCALE)
            ax.draw_artist(line)
            j -= 1
        #ax.relim()
        #ax.autoscale()
        plt.ylim(-SCALE, CHANNELS*SCALE)
        plt.xlim(i-PAST_POINTS, i)
        fig.canvas.draw()
        print "\r%.2f FPS" % (1 / (time.time() - t)),

if __name__ == '__main__':
    gobject.idle_add(main)
    plt.show()

