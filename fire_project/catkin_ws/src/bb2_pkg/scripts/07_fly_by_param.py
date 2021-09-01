#!/usr/bin/env python
#-*- coding: utf-8 -*-
import rospy
from bb2_pkg.MoveBB2 import MoveBB2

'''
화재지점을 화면 중앙에 맞춰 주는 코드 입니다 
'''

if __name__ == '__main__':
  rospy.init_node('bb2_move_detect', anonymous = True)
  mvd = MoveBB2()

#         7     8     9       detect_fire_and_fir_5.py 에서 넘어온 param의 위치
#           \   |   /         던져 주는 param 값의 이동 한다 [불을 인식한 방향으로]
#            \  |  /         
#     4 --------0-------- 6
#            /  |  \
#           /   |   \
#         1     2     3

  while True:
    cod1 = rospy.get_param("/fly_by_param_07/param_to_fly")

    if cod1 == 5:
      pass 
    elif cod1 == 8:                # 전면
      mvd.move_x(0.5, 0.1)
    elif cod1 == 2:                 #후면
      mvd.move_x(-0.5, 0.1)
    elif cod1 == 4:                 #좌측
      mvd.move_y(0.5, 0.1)
    elif cod1 == 6:                 # 우측
      mvd.move_y(-0.5, 0.1)
    elif cod1 == 9:                 #우상단
      mvd.move_xy(-0.5, 0.1)      
    elif cod1 == 0:                 #중앙
      mvd.landing()