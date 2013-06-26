# randomamp.py
# Copyright (C) 2013  Bastian Venthur
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from __future__ import division

import time
import math
import Tkinter as tk
import ttk
import json

import numpy as np

from libmushu.amplifier import Amplifier


class RandomAmp(Amplifier):
    """An amplifier that produces random data."""

    def __init__(self):
        self.channels = 17
        self.fs = 100
        self.last_sample = time.time()

    @property
    def sample_len(self):
        return 1 / self.fs

    @property
    def elapsed(self):
        return time.time() - self.last_sample

    def get_data(self):
        # simulate blocking until we have enough data
        elapsed = self.elapsed
        if elapsed < self.sample_len:
            time.sleep(self.sample_len - elapsed)
        dt = self.elapsed
        samples = math.floor(self.fs * dt)
        data = np.random.randint(0, 1024, (samples, self.channels))
        self.last_sample = time.time()
        return data, []

    def configure_with_gui(self):
        dialog = ConfigDialog(self)

    def configure(self, cfg):
        cfg = json.loads(cfg)
        self.fs = cfg['fs']
        self.channels = cfg['channels']

    def get_channels(self):
        return ['Ch_%d' % i for i in range(self.channels)]

    def get_sampling_frequency(self):
        return self.fs

    @staticmethod
    def is_available():
        return True

class ConfigDialog(tk.Toplevel):

    def __init__(self, amp):
        tk.Toplevel.__init__(self)
        self.amp = amp
        self.title('Configure Random Amplifier')

        frame1 = ttk.Frame(self)
        frame1.pack(fill='both', expand=True)
        frame1.columnconfigure(0, weight=3)
        frame1.columnconfigure(1, weight=1)
        self.label_chan = ttk.Label(frame1, text='Channels')
        self.label_chan.grid(column=0, row=0, sticky='W')
        self.label_fs = ttk.Label(frame1, text='Sampling Frequency')
        self.label_fs.grid(column=0, row=1, sticky='W')
        self.sbox_chan = tk.Spinbox(frame1, from_=1, to=128)
        self.sbox_chan.delete(0)
        self.sbox_chan.insert(0, self.amp.channels)
        self.sbox_chan.grid(column=1, row=0, sticky='E')
        self.sbox_fs = tk.Spinbox(frame1, from_=1, to=2048)
        self.sbox_fs.delete(0)
        self.sbox_fs.insert(0, self.amp.fs)
        self.sbox_fs.grid(column=1, row=1, sticky='E')

        frame2 = ttk.Frame(self)
        frame2.pack(side='right')
        self.ok_button = ttk.Button(frame2, text='Ok', command=self.ok_pressed)
        self.ok_button.pack(side='right')
        self.cancel_button = ttk.Button(frame2, text='Cancel', command=self.cancel_pressed)
        self.cancel_button.pack(side='right')

        # the modal window magic
        self.transient(self.master)
        self.grab_set()
        self.master.wait_window(self)

    def ok_pressed(self):
        fs = self.sbox_fs.get()
        channels = self.sbox_chan.get()
        cfg = {'fs' : int(fs),
               'channels' : int(channels)
               }
        self.amp.configure(json.dumps(cfg))
        self.destroy()

    def cancel_pressed(self):
        self.destroy()


def test_configgui():
    root = tk.Tk()
    amp = RandomAmp()
    amp.configure_with_gui()
    root.mainloop()

if __name__ == '__main__':
    test_configgui()

#    amp = RandomAmp()
#    amp.start()
#    for i in range(10):
#        t = time.time()
#        print amp.get_data()
#        print
#        print "FS:", 1 / (time.time() - t)
#        print
#    amp.stop()
#
#    # the same using a context manager, start and stop are called by the
#    # context manager
#    with amp as a:
#        for i in range(10):
#            print a.get_data()
