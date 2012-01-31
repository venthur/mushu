#!/usb/bin/env python


import struct
import time
from exceptions import Exception

import usb

import amplifier


ID_VENDOR_GTEC = 0x153c
ID_PRODUCT_GUSB_AMP = 0x0001

CX_OUT = usb.TYPE_VENDOR | usb.ENDPOINT_OUT



class GTecAmp(amplifier.Amplifier):

    def __init__(self):
        # list of available amps
        self.amps = []
        for bus in usb.busses():
            for device in bus.devices:
                if (device.idVendor == ID_VENDOR_GTEC and
                    device.idProduct == ID_PRODUCT_GUSB_AMP):
                    self.amps.append(device)
        self.connected = False
        self.devh = None

    def start(self):
        """Initialize the amplifier and make it ready."""
        device = self.amps[0]
        self.devh = device.open()
        # detach kernel driver if nessecairy
        config = device.configurations[0]
        self.devh.setConfiguration(config)
        assert(len(config.interfaces) > 0)
        first_interface = config.interfaces[0][1]
        first_setting = first_interface.alternateSetting
        self.devh.claimInterface(first_interface)
        self.devh.setAltInterface(first_interface)

    def start_recording(self):
        self.devh.controlMsg(CX_OUT, 0xb5, value=0x0800, buffer=0)
        self.devh.controlMsg(CX_OUT, 0xf7, value=0x0000, buffer=0)

    def stop_recording(self):
        """Shut down the amplifier."""
        self.devh.controlMsg(CX_OUT, 0xb8, [])

    def get_data(self):
        """Get data."""
        # TODO: what is the in-endpoint
        # 0x2 or 0x86
        endpoint = 0x86
        size = 512
        data = self.devh.bulkRead(endpoint, size)
        data = ''.join([chr(i) for i in data])
        data = struct.unpack_from('<'+'f'*(len(data)/4), data)
        return data

    def get_impedances(self):
        """Get the impedances."""
        pass

    def set_mode(self, mode):
        """Set mode, 'impedance', 'data'."""
        if mode == 'impedance':
            self.devh.controlMsg(CX_OUT, 0xc9, value=0x0000, buffer=0)
            self.devh.controlMsg(CX_OUT, 0xc2, value=0x0300, buffer=0)
        elif mode == 'calibrate':
            self.devh.controlMsg(CX_OUT, 0xc1, value=0x0000, buffer=0)
            self.devh.controlMsg(CX_OUT, 0xc2, value=0x0200, buffer=0)
        elif mode == 'data':
            self.devh.controlMsg(CX_OUT, 0xc0, value=0x0000, buffer=0)
            self.devh.controlMsg(CX_OUT, 0xc2, value=0x0100, buffer=0)
        else:
            raise AmpError('Unknown mode: %s' % mode)


    def set_calibration_mode(self, mode):
        # buffer: [0x03, 0xd0, 0x07, 0x02, 0x00, 0xff, 0x07]
        #          ====  ==========
        # (1) mode:
        # (2) amplitude: little endian (0x07d0 = 2000)
        if mode == 'sine':
            self.devh.controlMsg(CX_OUT, 0xcb, value=0x0000, buffer=[0x03, 0xd0, 0x07, 0x02, 0x00, 0xff, 0x07])
        elif mode == 'sawtooth':
            self.devh.controlMsg(CX_OUT, 0xcb, value=0x0000, buffer=[0x02, 0xd0, 0x07, 0x02, 0x00, 0xff, 0x07])
        elif mode == 'whitenoise':
            self.devh.controlMsg(CX_OUT, 0xcb, value=0x0000, buffer=[0x05, 0xd0, 0x07, 0x02, 0x00, 0xff, 0x07])
        elif mode == 'square':
            self.devh.controlMsg(CX_OUT, 0xcb, value=0x0000, buffer=[0x01, 0xd0, 0x07, 0x02, 0x00, 0xff, 0x07])
        else:
            raise AmpError('Unknown mode: %s' % mode)

    def calculate_impedance(self, u_measured, u_applied):
        return (u_measured * 1e6) / (u_applied - u_measured) - 1e4


class AmpError(Exception):
    pass


if __name__ == '__main__':
    amp = GTecAmp()
    amp.start()
    try:
        while True:
            t = time.time()
            data = amp.get_data()
            dt = time.time() - t
            if len(data) > 0:
                print "%.5f seconds (%.5f ps), length: %d" % (dt, (len(data) / 16.) * 1/dt, len(data))
    finally:
        amp.stop()

