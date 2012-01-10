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
SCALE = 30000 #10 

fig = plt.figure()

def main():
    amp = gtec.GTecAmp()
    amp.start()
    amp.set_mode('calibrate')
    #amp.set_mode('data')
    ax = plt.subplot(111)
    for i in range(CHANNELS):
        ax.plot(0)
    fig.canvas.draw()
    x_values = np.array([])
    y_values = [np.array([]) for i in range(CHANNELS)]
    buffer = []
    data = []
    for i in itertools.count():
        t = time.time()

        #buffer.extend(amp.get_data())
        #print buffer
        #data = buffer[:CHANNELS]
        #buffer = buffer[CHANNELS:]
        data = amp.get_data()
        #print data
        for i in range(CHANNELS):
            y_values[i] = np.append(y_values[i], data[i::CHANNELS])
            #y_values[i] = np.append(y_values[i], data[i*32:(i+1)*32:])
            y_values[i] = y_values[i][-PAST_POINTS:]
        data = []
        # set x/y data for the plot
        x_values = np.append(x_values[-PAST_POINTS:], i)
        # plot the data
        j = 0
        for line in ax.lines:
            #line.set_data(x_values, y_values[j] + j*210)
            line.set_xdata([i for i in range(len(y_values[j]))])
            line.set_ydata(y_values[j]/8.15 + j*SCALE)
            ax.draw_artist(line)
            j += 1
        #ax.relim()
        #ax.autoscale()
        plt.ylim(-SCALE, CHANNELS*SCALE)
        plt.xlim(i-PAST_POINTS, i)
        fig.canvas.draw()
        print "\r%.2f FPS" % (1 / (time.time() - t)),

if __name__ == '__main__':
    gobject.idle_add(main)
    plt.show()

#    fig = plt.figure()
#    thread = threading.Thread(target=main, args=(fig,))
#    thread.start()
#    plt.show()

