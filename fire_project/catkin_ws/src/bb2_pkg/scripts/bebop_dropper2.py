#!/usr/bin/env python

import rospy, serial

sp = serial.Serial('/dev/ttyUSB0', 9600)
sp.write('1')
