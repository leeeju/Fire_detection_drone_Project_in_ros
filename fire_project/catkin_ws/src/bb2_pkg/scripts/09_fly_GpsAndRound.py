#!/usr/bin/env python
#-*- coding: utf-8 -*-
import rospy, sys
from std_msgs.msg import Empty
from geometry_msgs.msg import Twist
from bb2_pkg.bebop_move_by_gps_module_5 import MoveByGPS
from bb2_pkg.round_move import RotateByAtti
'''
GPS 이동 및 순찰의 대한 코드 입니다 
'''
if __name__ == '__main__':
    rospy.init_node('bb2_move_to_gps', anonymous = True)
    pb0 = rospy.Publisher('/bebop/takeoff', Empty, queue_size = 0)   # Publisher 이륙
    pb1 = rospy.Publisher('/bebop/land', Empty, queue_size = 0)      # Publisher 착륙
    mbg = MoveByGPS()                                                # GPS이동 코드
    tw = Twist()                                                     # 방향 전환
    em = Empty()                                                    
    pb0.publish(em)

    try:
        target_lad1 = float(input("input target latitude : "))      # 도착해야 할 위도를 지정한다.
        target_lod1 = float(input("input target longitude: "))      # 도착해야 할 경도를 지정한다.
        
        target_lad2 = mbg.lati_now                                  # 입력된 위.경도의 값을 변수에 저장
        target_lod2 = mbg.long_now
        
        mbg.fly_to_target(target_lad1, target_lod1)                 # 목표 지점으로 도착

        go = RotateByAtti()                                         # 순찰코드
        go.roundgo()                                                # 순찰종료

        mbg.fly_to_target(target_lad2, target_lod2)                 # 최초 스타트 지점으로 돌아감

        pb1.publish(em)                                             # 착륙
        rospy.spin()                                                # 코드룰 종료 하지 않고 살려둔다[spin]

    except rospy.ROSInterruptException:
        pass