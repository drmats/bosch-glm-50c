#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Connect laser rangefinder via bluetooth
and pass its readings as keyboard inputs.

https://github.com/drmats/bosch-glm50c
"""

import bluetooth
import signal
import struct
import subprocess
import sys

from evdev import UInput, ecodes as e


class Main (object):

    address = None
    socket = None
    channel = 0x0005
    command = { "init_logging": b"\xC0\x55\x02\x01\x00\x1A" }

    keymapping = {
        "0": e.KEY_0,
        "1": e.KEY_1,
        "2": e.KEY_2,
        "3": e.KEY_3,
        "4": e.KEY_4,
        "5": e.KEY_5,
        "6": e.KEY_6,
        "7": e.KEY_7,
        "8": e.KEY_8,
        "9": e.KEY_9,
        ".": e.KEY_DOT,
    }

    def __init__ (self, *args, **kwargs):
        self.address = kwargs.get("address", None)
        if self.address is None:
            print("Provide device bluetooth address")
            sys.exit()

        try:
            print(
                "[%s]: Connecting to bluetooth range finder (confirm pin)..."
                    % self.address
            )
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((self.address, self.channel))
            print("Connected")
        except:
            print("Connection error")
            sys.exit()

        signal.signal(signal.SIGINT, lambda _a, _b: self.exit())
        print("press [ctrl+C] to exit")

        self.process_measurements()


    def exit (self, exit_code=0):
        if self.socket:
            self.socket.close()
        if exit_code == 0:
            print("\nBye!")
        sys.exit(exit_code)


    def send_number_as_keystrokes (self, value):
        try:
            float(value)
        except ValueError:
            return False

        ui = UInput()
        for digit in str(value):
            try:
                ui.write(e.EV_KEY, self.keymapping[digit], 1)
                ui.write(e.EV_KEY, self.keymapping[digit], 0)
            except KeyError:
                pass
        ui.write(e.EV_KEY, e.KEY_ENTER, 1)
        ui.write(e.EV_KEY, e.KEY_ENTER, 0)
        ui.syn()
        ui.close()

        return True


    def process_measurements (self):
        try:
            self.socket.send(self.command["init_logging"])
            while True:
                data = self.socket.recv(1024)
                header = data[0:5]
                gap = data[5:6]
                err = data[6:7]
                reading = data[7:11]
                measurement = round(
                    struct.unpack("<f", reading)[0] * 10000
                ) / 10
                if reading.hex() != "00000000":
                    print(
                        header.hex(),
                        gap.hex(),
                        err.hex(),
                        reading.hex(),
                        "==>", measurement, "mm",
                    )
                    self.send_number_as_keystrokes(round(measurement))
        except bluetooth.btcommon.BluetoothError:
            print("Error reading data")
            self.exit(1)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: %s <bluetooth_address>\n" % sys.argv[0])
        if sys.platform == "linux":
            try:
                subprocess.run(
                    "bluetoothctl power on".split(),
                    capture_output=True,
                )
                try:
                    subprocess.run("bluetoothctl scan on".split(), timeout=6)
                except subprocess.TimeoutExpired:
                    print()
                result = subprocess.run(
                    "bluetoothctl devices".split(),
                    capture_output=True,
                )
                print(result.stdout.decode())
            except FileNotFoundError:
                pass
        sys.exit(1)

    mac = sys.argv[1]
    Main(address=mac)
