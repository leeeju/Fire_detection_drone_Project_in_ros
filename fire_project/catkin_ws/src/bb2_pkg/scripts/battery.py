#!/usr/bin/python
#-*- coding: utf-8 -*-
import rospy
from bebop_msgs.msg import CommonCommonStateBatteryStateChanged as Battery # 비밥 드론의 메세지 토픽을 받아옴
from time import sleep                                                     # 시간
#from std_msgs.msg import Empty

'''
영문 이용시 한글프린터문에 #으로  주석처리 하고 영문의 #을 제거해 주세요.
'''

def callback(data):
	#rospy.loginfo("Battery level is %s%%",data.percent)
	rospy.loginfo("현재 남은 베터리 잔량 : %s%%",data.percent)
	#print(data.percent)

	if data.percent<15:
		rate = rospy.Rate(10)
		#rospy.loginfo("Battery is below 15%. Landing now.")
		rospy.loginfo("베터리 잔량이 15% 이하 입니다. 착륙 준비 하세요.")    #info 형식의 메시지 출력 // ex) [INFO] [1627887334.009190]: 베터리 잔량이 15% 이하 입니다. 착륙 준비 하세요.
		rospy.loginfo(" ** 베터리 잔량 경고 ** ")
		#while rospy.is_shutdown():
		#	pub = rospy.Publisher('/bebop/land', std_msgs/Empty, queue_size=0)
	#		pub.publish()
#			rate.sleep()


def main():
	rospy.init_node('Battery_Level')
	rospy.Subscriber("bebop/states/common/CommonState/BatteryStateChanged", Battery, callback) # Subscriber 한다 비밥이 던져 주는 베터리 토픽을
	rospy.spin()

if __name__ == '__main__':
	main()