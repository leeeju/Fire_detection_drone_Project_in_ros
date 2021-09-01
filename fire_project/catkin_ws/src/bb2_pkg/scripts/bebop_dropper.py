#!/usr/bin/env python

import rospy, serial
from bb2_pkg.GetChar import GetChar

sp = serial.Serial('/dev/ttyUSB0', 9600)
kb = GetChar()
ch = ""

while(ch != 'Q'):
  ch = kb.getch()
  if ch == '1':
    sp.write('1')
    print("drop!")
  else:
    sp.write('0')
    print("nothing happen~")  
