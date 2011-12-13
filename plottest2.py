#!/usr/bin/env python


import itertools
import math
import time
import threading

from matplotlib import pyplot as plt


def main(fig):
    #ax = plt.subplot(111)
    ax = []
    for i in range(16):
        ax.append(plt.subplot(16, 1, i))
        ax[i].plot(0)
    fig.canvas.draw()
    x_values = []
    y_values = []
    for i in itertools.count():
        t = time.time()
        # set x/y data for the plot
        x_values.append(i)
        x_values = x_values[-9:]
        y_values.append(math.sin(i))
        y_values = y_values[-9:]
        # plot the data
        t = time.time()
        for a in ax:
            a.lines[0].set_data(x_values, y_values)
            a.draw_artist(a.lines[0])
            a.relim()
            a.autoscale()
            #a.clear()
            #a.plot(x_values, y_values)
        fig.canvas.draw()
#        time.sleep(1)
        print 1 / (time.time() - t)

if __name__ == '__main__':
    fig = plt.figure()
    thread = threading.Thread(target=main, args=(fig,))
    thread.start()
    plt.show()

