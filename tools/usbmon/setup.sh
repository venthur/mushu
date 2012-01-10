#!/bin/sh

mount -t debugfs none_debugs /sys/kernel/debug
modprobe usbmon

