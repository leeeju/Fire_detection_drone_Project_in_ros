#!/usr/bin/env python
#-*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
from bb2_pkg.MoveBB2_2 import MoveBB2
from bebop_msgs.msg import Ardrone3PilotingStateAttitudeChanged

'''
순찰모드 움직임 조절
'''

class RotateByAtti:   
  def __init__(self):
    rospy.Subscriber('/bebop/states/ardrone3/PilotingState/AttitudeChanged', Ardrone3PilotingStateAttitudeChanged, self.get_atti)
    self.atti_now = 0.0

  def get_atti(self, msg):
    self.atti_now = msg.yaw
  
  def roundgo(self):
    if not rospy.is_shutdown():
      tw  = Twist()
      bb2 = MoveBB2()
      print('순회 비행을 시작합니다.')
      rospy.sleep(1)
      #비밥의 실측결과 약 3m 높이에서 45도 각도로 카메라를 꺾었을 때 좌우 5.5m, 위아래 2m 정도의 범위를 촬영할 수 있었다. 따라서 좌우 이동은 5m 정도, 상하 이동은 3m 정도를 단위로 하여 움직여야 하겠다.
      xjump = 0.5
      yjump = 0.8

      for i in range(5):
        if i%2 == 0: 
          bb2.move_x(xjump, 0.01)   # 초회 직진 코드  (직진 거리, 오차 허용값)          
          bb2.move_y(yjump, 0.01)   # 2회차 직진
        else:
          bb2.move_x(-xjump, 0.01)   # 초회 직진 코드  (직진 거리, 오차 허용값)          
          bb2.move_y(-yjump, 0.01)   # 2회차 직진
          xjump = xjump + xjump
        yjump = yjump + yjump
    
      
      bb2.stopping()
      rospy.sleep(5)
      print("순회 비행을 마쳤습니다.")
    else:
      exit()

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
