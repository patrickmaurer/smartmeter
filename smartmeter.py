#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Initial work by Joost Baltissen and Romain Aviolat

import sys,time,serial,struct,argparse
from influxdb import InfluxDBClient

class smartmeter():
    def __init__(self):
        self.ser = serial.Serial(
            port = '/dev/ttyUSB0',
            baudrate = '300',
            parity=serial.PARITY_EVEN,
            bytesize=serial.SEVENBITS,
            stopbits=serial.STOPBITS_ONE,
            xonxoff = 0,
            rtscts = 0,
            timeout = 20
         )

    def readData(self):

        while True:

            self.ser.close()

            try:
                self.ser.open()
            except:
                sys.exit ("Error while opening serial-port:"  % self.ser.port)

            request = struct.pack('BBBBB', 0x2F, 0x3F, 0x21, 0x0D, 0x0A)
            self.ser.write(request)
            time.sleep(.2)                    #give time to send
            self.ser.flushInput()
            tdata = self.ser.read()           # Wait forever for anything
            time.sleep(1)                     # Sleep (or inWaiting() doesn't give the correct value)
            data_left = self.ser.inWaiting()  # Get the number of characters ready to be read
            tdata += self.ser.read(data_left) # Do the read and combine it with the first character
            meter = tdata.strip()

            self.ser.flushInput()
            ack= struct.pack('BBBBBB',0x06,0x30,0x30,0x30,0x0D,0x0A)
            self.ser.write(ack)
            time.sleep(.02)

            self.ser.flushInput()
            tdata = self.ser.read()           # Wait forever for anything
            time.sleep(12)                    # Sleep (or inWaiting() doesn't give the correct value)
            data_left = self.ser.inWaiting()  # Get the number of characters ready to be read
            tdata += self.ser.read(data_left) # Do the read and combine it with the first character
            self.ser.close()

            start = tdata.find('8.1(')+4
            end = tdata.find('*', start)
            use_high_str = tdata[start:end]
            use_high = float(use_high_str)

            start = tdata.find('8.2(')+4
            end = tdata.find('*', start)
            use_low_str = tdata[start:end]
            use_low = float(use_low_str)

            start = tdata.find('8.0(')+4
            end = tdata.find('*', start)
            use_total_str = tdata[start:end]
            use_total = float(use_total_str)

            json_body = {
                "measurement": "power",
                "tags": {
                    "tool": "smartmeter.py",
                    "interface": self.ser.port,
                    "meter": meter
                },
                "fields": {
                    "usage_low": use_low,
                    "usage_high": use_high,
                    "usage_total": use_total
                }
            }

            print(json_body)

            client = InfluxDBClient('localhost', 8086, 'user', 'pass', 'smartmeter_db')
            client.write_points([json_body])

            time.sleep(60)


if __name__ == '__main__':

    device = smartmeter()

    parser = argparse.ArgumentParser()
    parser.add_argument('-D', '--daemon', action="store_true", help="Fork and run in background")
    args = parser.parse_args()

    if args.daemon:

        if os.fork()==0:
            os.setsid()
            sys.stdout=open("/dev/null", 'w')
            sys.stdin=open("/dev/null", 'r')

            if os.fork()==0:
                device.readData()
            sys.exit(0)

    else:

        device.readData()
