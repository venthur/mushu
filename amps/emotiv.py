#!/usr/bin/env python


from Crypto.Cipher import AES
import numpy as np

import usb.core
import usb.util

from amplifier import Amplifier


VENDOR_ID = 0x1234
PRODUCT_ID = 0xed02

ENDPOINT_IN = usb.util.ENDPOINT_IN | 2  # second endpoint


class Epoc(Amplifier):

    def __init__(self):
        # find amplifier
        self.dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if self.dev is None:
            raise RuntimeError('Emotiv device is not connected.')
        # pyusb docs say you *have* to call set_configuration, but it does not
        # work unless i *don't* call it.
        #dev.set_configuration()
        # get the serial number
        serial = usb.util.get_string(self.dev, 17, self.dev.iSerialNumber)
        # claim the device and it's two interfaces
        if self.dev.is_kernel_driver_active(0):
            self.dev.detach_kernel_driver(0)
        usb.util.claim_interface(self.dev, 0)
        if self.dev.is_kernel_driver_active(1):
            self.dev.detach_kernel_driver(1)
        usb.util.claim_interface(self.dev, 1)
        # prepare AES
        self.cipher = AES.new(self.generate_key(serial, True))

    def get_data(self):
        try:
            raw = self.dev.read(ENDPOINT_IN, 32, 1, timeout=1000)
            raw = self.decrypt(raw)
            data = self.parse_raw(raw)
            data = np.array(data)
        except Exception as e:
            print e
            data = np.array()
        return data.reshape(-1, 18)

    def generate_key(self, sn, research=True):
        """Generate the encryption key.

        The key is based on the serial number of the device and the information
        weather it is a research- or consumer device.

        """
        if research:
            key = ''.join([sn[15], '\x00', sn[14], '\x54',
                           sn[13], '\x10', sn[12], '\x42',
                           sn[15], '\x00', sn[14], '\x48',
                           sn[13], '\x00', sn[12], '\x50'])
        else:
            key = ''.join([sn[15], '\x00', sn[14], '\x48',
                           sn[13], '\x00', sn[12], '\x54',
                           sn[15], '\x10', sn[14], '\x42',
                           sn[13], '\x00', sn[12], '\x50'])
        return key

    def decrypt(self, raw):
        """Decrypt a raw package."""
        data = self.cipher.decrypt(raw[:16]) + self.cipher.decrypt(raw[16:])
        tmp = 0
        for i in range(32):
            tmp = tmp << 8
            tmp += ord(data[i])
        return tmp

    def parse_raw(self, raw):
        """Parse raw data."""
        # TODO: Handle battery and counter correctly
        data = []
        shift = 256
        # counter / battery
        shift -= 8
        data.append((raw >> shift) & 0b11111111)
        # 7x data, 1x quality
        for i in range(8):
            shift -= 14
            data.append((raw >> shift) & 0b11111111111111)
        shift -= 14
        # 7x data
        for i in range(7):
            shift -= 14
            data.append((raw >> shift) & 0b11111111111111)
        # 2x gyroscope
        for i in range(2):
            shift -= 8
            tmp = (raw >> shift) & 0b01111111
            tmp -= 100
            if (raw >> shift) & 0b10000000:
                tmp *= -1
            data.append(tmp)
        return [int(i) for i in data]


if __name__ == '__main__':
    amp = Epoc()
    print 'Reading...'
    while 1:
        try:
            print amp.get_data()
        except Exception as e:
            print e
        break
