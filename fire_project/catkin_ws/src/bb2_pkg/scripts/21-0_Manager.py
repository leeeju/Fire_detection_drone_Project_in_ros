#!/usr/bin/python
#-*- coding: utf-8 -*-

#비행 및 탐지 기능을 관리하는 코드이다.

import rospy, subprocess

if __name__ == '__main__':
	rospy.init_node('Fire_drone_manager', anonymous = False)
	while not rospy.is_shutdown():
		#파라미터의 조건이 되면 코드를 실행한다.
		cod1 = rospy.get_param("/Fire_drone_managerl/order")
		if cod1 == 1:
			#순찰 비행 코드를 실행한다.
			subprocess.call(["rosrun", "bb2_pkg", "18-1_FlyTarget.py"])
			#파라미터 서버에 값을 전달하여 새로 설정되는 시간과 내부 코드의 실행 시간을 고려하여 일정한 시간을 대기하도록 한다.
			rospy.sleep(10)
		else:
			pass
