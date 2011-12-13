#!/usr/bin/env python


import itertools
import math
import time
import threading

from matplotlib import pyplot as plt
import numpy as np

PAST_POINTS = 100

def main(fig):
    ax = plt.subplot(111)
    for i in range(16):
        ax.plot(0)
    fig.canvas.draw()
    x_values = np.array([])
    y_values = np.array([])
    for i in itertools.count():
        t = time.time()
        # set x/y data for the plot
        x_values = np.append(x_values[-PAST_POINTS:], i)
        y_values = np.append(y_values[-PAST_POINTS:], math.sin(i))
        # plot the data
        j = 0
        for line in ax.lines:
            line.set_data(x_values, y_values + j*10)
            ax.draw_artist(line)
            j += 1
        plt.ylim(-10, j*10+10)
        plt.xlim(i-PAST_POINTS, i)
        fig.canvas.draw()
        print 1 / (time.time() - t)

if __name__ == '__main__':
    fig = plt.figure()
    thread = threading.Thread(target=main, args=(fig,))
    thread.start()
    plt.show()

