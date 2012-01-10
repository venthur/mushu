#!/usb/bin/env python


import struct
import time
from exceptions import Exception

import usb

import amplifier


ID_VENDOR_GTEC = 0x153c
ID_PRODUCT_GUSB_AMP = 0x0001

CX_OUT = usb.TYPE_VENDOR | usb.ENDPOINT_OUT

AMP_START_REQUEST = 0xf7
AMP_STOP_REQUEST = 0xb8

AMP_SET_MODE_COMMON_REQUEST = 0xc2
AMP_SET_MODE_CALIBRATE_REQUEST = 0xc1
AMP_SET_MODE_CALIBRATE_COMMON_VALUE = 0x2
AMP_SET_MODE_IMPEDANCE_COMMON_VALUE = 0x3
AMP_SET_MODE_IMPEDANCE_REQUEST = 0xc9


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
        # start the amp, maybe the above should go into init.
        self.devh.controlMsg(CX_OUT, AMP_START_REQUEST, [])

    def stop(self):
        """Shut down the amplifier."""
        self.devh.controlMsg(CX_OUT, AMP_STOP_REQUEST, [])

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
            self.devh.controlMsg(CX_OUT,
                                 AMP_SET_MODE_COMMON_REQUEST,
                                 value=AMP_SET_MODE_IMPEDANCE_COMMON_VALUE,
                                 buffer=0)
            self.devh.controlMsg(CX_OUT,
                                 AMP_SET_MODE_IMPEDANCE_REQUEST,
                                 value=0,
                                 buffer=0)
        elif mode == 'calibrate':
            self.devh.controlMsg(CX_OUT,
                                 AMP_SET_MODE_COMMON_REQUEST,
                                 value=AMP_SET_MODE_CALIBRATE_COMMON_VALUE,
                                 buffer=0)
            self.devh.controlMsg(CX_OUT,
                                 AMP_SET_MODE_CALIBRATE_REQUEST,
                                 value=0,
                                 buffer=0)
            self.devh.controlMsg(CX_OUT, 0xb5, value=0x08, buffer=0)
            self.devh.controlMsg(CX_OUT, AMP_START_REQUEST, [])
        elif mode == 'data':
            self.devh.controlMsg(CX_OUT, 0xc0, value=0x00, buffer=0)
            self.devh.controlMsg(CX_OUT, 0xc2, value=0x0100, buffer=0)
            self.devh.controlMsg(CX_OUT, 0xb5, value=0x0800, buffer=0)
            self.devh.controlMsg(CX_OUT, 0xf7, value=0x00, buffer=0)
        else:
            raise AmpError('Unknown mode: %s' % mode)

    def calculate_impedance(u_measured, u_applied):
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

