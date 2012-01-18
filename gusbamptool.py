#!/usr/bin/env python


from threading import Thread

from gi.repository import Gtk

import gtec


amp = gtec = gtec.GTecAmp()
amp.start()

class Handler:

    def onDeleteWindow(self, *args):
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


class UsbDataFetcher(Thread):

    def run(self):
        while 1:
            data_buffer = amp.get_data()
            print data_buffer

if __name__ == '__main__':
    builder = Gtk.Builder()
    builder.add_from_file('gusbamptool.glade')
    builder.connect_signals(Handler())
    window = builder.get_object('window1')
    window.show_all()
    datafetcher = UsbDataFetcher()
    datafetcher.start()
    Gtk.main()

