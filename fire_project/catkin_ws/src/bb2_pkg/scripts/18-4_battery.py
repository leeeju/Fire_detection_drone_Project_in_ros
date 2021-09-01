#!/usr/bin/python
#-*- coding: utf-8 -*-

import rospy, subprocess, rosnode
from bebop_msgs.msg import CommonCommonStateBatteryStateChanged as Battery # 비밥 드론의 메세지 토픽을 받아옴

def callback(data):
	global battery_percent
	battery_percent = 100
	battery_percent = int(data.percent)

if __name__ == '__main__':

	rospy.init_node('Battery_Level', anonymous = False)
	rospy.Subscriber("bebop/states/common/CommonState/BatteryStateChanged", Battery, callback)

	while not rospy.is_shutdown():
		try:
			#목적지의 위경도를 입력 받는다.
			inmessage = str(input("위도와 경도를 쉼표로 구분하여 입력하세요:"))
			inmessage = inmessage.replace(" ", "")
			inmessage = inmessage.replace("(", "")
			inmessage = inmessage.replace(")", "")
			slati = inmessage.split(",")[0]
			slong = inmessage.split(",")[1]
			target_la = float(slati)
			target_lo = float(slong)
			#위도와 경도가 유효한 숫자일 경우에 입력받은 위도, 경도를 파라미터 서버에 저장하고 다음 단계로 넘어간다.
			if ( target_la >=34.0 and target_la <=38.0 )and( target_lo >= 126.0 and target_lo <=130.0 ):
				#입력받은 위경도를 파라미터 서버에 저장한다.
				rospy.set_param("/tar_lati", target_la)
				rospy.set_param("/tar_long", target_lo)
				#목표 지점으로 이동하는 비행 모드의 파라미터를 설정한다.
				rospy.set_param("/fly_to_targetl/param_of_flying", 1)
				#반복문을 빠져 나간다.
				break
			else:
				print("다시 입력해주세요.")
		except:
			print("오류입니다. 다시 입력하세요.")
			continue

	#반복문 안에서 조건문을 한번 실행하고 다시 실행하지 않도록 하기 위한 인덱스 변수를 설정한다.
	i = 0
	while not rospy.is_shutdown():
		try:
			rospy.loginfo("배터리 잔량: %d%% ", battery_percent)
			rospy.sleep(20)
			if (i == 0) and (battery_percent < 15):
				#베터리의 잔량을 터미널에서 출력한다.
				print("베터리 잔량이 15% 이하 입니다. 되돌아 갑니다.")    
				#불 인식 코드를 비활성화한다.
				rospy.set_param("/fire_detectorl/param_of_detector", False)
				#처음 시작점으로 되돌아 오는 비행 코드를 활성화한다.
				rospy.set_param("/fly_to_targetl/param_of_flying", 2)
				#현재 실행 중인 비행 코드를 종료한다.
				rosnode.kill_nodes(['/fly_to_targetl'])
				rospy.sleep(10)
				#다시 비행 코드를 실행하도록 메니저의 파라미터를 설정한다.
				rospy.set_param("/Fire_drone_managerl/order", 1)
				i = 1
		except:
			continue
