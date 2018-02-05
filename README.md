# smartmeter.py: extract data from "smart" power-meters

This tool reads the values contained inside Landis+Gyr
power-meters and sends the output to InfluxDB. It has been 
tested with the ZMB120 model, but it should work with any
other IEC 62056 compliant devices too.

Some meters report usage data as floating point numbers.
Others report as integers only, unfortunately.

I'm using an USB infrared probe to read the data, they are
available assembled or as DIY kits:

* https://shop.weidmann-elektronik.de/index.php?page=product&info=24
* http://www.optical-probe.de/Optical%20probes/op200.html
* https://www.ebay.ch/sch/i.html?_sop=15&LH_PrefLoc=2&LH_BIN=1&_nkw=optical+probe+kit
* http://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf

# install

Install few dependencies using pip

* pyserial
* influxdb

# configure

You'll have to statically set the InfluxDB server IP address,
database and credential settings inside the code for now.

# run

``$ python ./smartmeter.py``

# install service
1. save smartmeter.service to /lib/systemd/system/
2. ``sudo chmod 644 /lib/systemd/system/smartmeter.service``
3. ``sudo systemctl daemon-reload``
4. ``sudo systemctl enable smartmeter.service``
5. ``sudo systemctl start smartmeter.service``
6. ``sudo systemctl status smartmeter.service``
The last command should report the service running.

# credits

Joost Baltissen is the author of the inital code.
Romain Aviolat added output to InfluxDB.
