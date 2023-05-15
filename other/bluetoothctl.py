# ReachView code is placed under the GPL license.
# Written by Egor Fedorov (egor.fedorov@emlid.com)
# Copyright (c) 2015, Emlid Limited
# All rights reserved.

# If you are interested in using ReachView code as a part of a
# closed source project, please contact Emlid Limited (info@emlid.com).

# This file is part of ReachView.

# ReachView is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ReachView is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ReachView.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import time
import pexpect
import subprocess
import sys
import os


ASOUND_BT = """pcm.!default "bluealsa"
ctl.!default "bluealsa"
defaults.bluealsa.interface "hci0"
defaults.bluealsa.device "{}"
defaults.bluealsa.profile "a2dp"

pcm.btheadset {{
    type plug
    slave {{
        pcm {{
              type bluealsa
              device {}
              profile "auto"
         }}
    }}
    hint {{
         show on
         description "BT Headset"
    }}
}}
ctl.btheadset {{
    type bluetooth
}}
"""

ASOUND_JACK = """defaults.pcm.card 1
defaults.ctl.card 1
"""

ASOUND_PATH = "/etc/asound.conf"


class BluetoothctlError(Exception):
    """This exception is raised, when bluetoothctl fails to start."""
    pass


class Bluetoothctl:
    """A wrapper for bluetoothctl utility."""

    def __init__(self):
        #out = subprocess.check_output("rfkill unblock bluetooth", shell = True)
        self.child = pexpect.spawn("bluetoothctl", echo = False)

    def get_output(self, command, pause = 0):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.child.send(command + "\n")
        time.sleep(pause)
        start_failed = self.child.expect(["bluetooth", pexpect.EOF], timeout=60)

        if start_failed:
            raise BluetoothctlError("Bluetoothctl failed after running " + command)

        return self.child.before.split("\r\n")

    def start_scan(self):
        """Start bluetooth scanning process."""
        try:
            out = self.get_output("scan on")
        except BluetoothctlError, e:
            print(e)
            return None

    def make_discoverable(self):
        """Make device discoverable."""
        try:
            out = self.get_output("discoverable on")
        except BluetoothctlError, e:
            print(e)
            return None

    def parse_device_info(self, info_string):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        string_valid = not any(keyword in info_string for keyword in block_list)

        if string_valid:
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(" ", 2)
                    device = {
                        "mac_address": attribute_list[1],
                        "name": attribute_list[2]
                    }

        return device

    def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        try:
            out = self.get_output("devices")
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            available_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)

            return available_devices

    def get_paired_devices(self):
        """Return a list of tuples of paired devices."""
        try:
            out = self.get_output("paired-devices")
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            paired_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    paired_devices.append(device)

            return paired_devices

    def get_discoverable_devices(self):
        """Filter paired devices out of available."""
        available = self.get_available_devices()
        paired = self.get_paired_devices()

        return [d for d in available if d not in paired]

    def get_device_info(self, mac_address):
        """Get device info by mac address."""
        try:
            out = self.get_output("info " + mac_address)
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            return out

    def pair(self, mac_address):
        """Try to pair with a device by mac address."""
        try:
            out = self.get_output("pair " + mac_address, 4)
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to pair", "Pairing successful", pexpect.EOF], timeout=60)
            success = True if res == 1 else False
            return success

    def remove(self, mac_address):
        """Remove paired device by mac address, return success of the operation."""
        try:
            out = self.get_output("remove " + mac_address, 3)
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            res = self.child.expect(["not available", "Device has been removed", pexpect.EOF], timeout=60)
            success = True if res == 1 else False
            return success

    def connect(self, mac_address):
        """Try to connect to a device by mac address."""
        try:
            out = self.get_output("connect " + mac_address, 2)
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to connect", "Connection successful", pexpect.EOF], timeout=60)
            success = True if res == 1 else False
            return success

    def disconnect(self, mac_address):
        """Try to disconnect to a device by mac address."""
        try:
            out = self.get_output("disconnect " + mac_address, 2)
        except BluetoothctlError, e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to disconnect", "Successful disconnected", pexpect.EOF], timeout=60)
            success = True if res == 1 else False
            return success


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('uuid', type=str)
    args = parser.parse_args()
    print("Init bluetooth...")
    bl = Bluetoothctl()
    print("Ready!")

    try:
        subprocess.check_output('mount -o remount,rw /', shell=True).decode('utf-8')
    except subprocess.CalledProcessError:
        pass

    if not args.uuid:
        connected = subprocess.check_output(
            "grep \" device\" /etc/asound.conf | awk {'print $2'}",
            shell=True
        ).decode('utf-8')

        try:
            bl.remove(connected)
        except pexpect.exceptions.TIMEOUT:
            pass

        with open(ASOUND_PATH, "w") as a_file:
            a_file.write(ASOUND_JACK)

        with open('/home/starko/bt_auto_connect', "w") as myfile:
            myfile.write('#!/bin/bash')
            myfile.write('\n')

        os.chmod("/home/starko/bt_auto_connect", 0o777)

        subprocess.Popen('sync', shell=True)
        subprocess.Popen('rm -f /tmp/mpv*', shell=True)
        subprocess.Popen('pkill -KILL -u starko', shell=True)
        sys.exit(0)

    bl.start_scan()
    print("Scanning for 10 seconds...")
    for i in range(0, 15):
        print(i)
        time.sleep(1)

    time.sleep(5)

    # Check if already connected to this uuid
    paired = False

    with open(ASOUND_PATH, "r") as myfile:
        paired = args.uuid in myfile.read()

    if not paired:
        bl.pair(args.uuid)
        time.sleep(5)

    bl.connect(args.uuid)

    try:
        with open(ASOUND_PATH, "w") as asound_file:
            asound_file.write(ASOUND_BT.format(args.uuid, args.uuid))

        subprocess.Popen("service spotifyd restart", shell=True)

    except IOError:
        pass

    with open('/home/starko/bt_auto_connect', "w") as myfile:
        myfile.write('#!/bin/bash')
        myfile.write('\n')
        myfile.write('python /home/starko/bluetoothctl.py {0}'.format(args.uuid))
        myfile.write('\n')

    os.chmod("/home/starko/bt_auto_connect", 0o777)

    try:
        subprocess.check_output('mount -o remount,ro /', shell=True).decode('utf-8')
    except subprocess.CalledProcessError:
        pass

    subprocess.Popen('sync', shell=True)
