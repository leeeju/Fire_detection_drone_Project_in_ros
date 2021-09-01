#!/usr/bin/env python
#-*- coding: utf-8 -*-

from twilio.rest import Client
import rospy
from playsound import playsound
from bebop_msgs.msg import Ardrone3PilotingStatePositionChanged

#가상 모드의 스핑크스에서는 시작 위치가 48.878900, 2.367780이므로 이를 다른 위치에서 시작하는 경우 보정시켜줄 필요가 있다.

def cb_get_gps(msg):
    global lati_now
    global long_now
    lati_now = msg.latitude - 12.358951513    # 스핑크스 드론을 날릴 때
    long_now = msg.longitude + 124.805285815  # 스핑크스 드론을 날릴 때
    #lati_now = msg.latitude                    # 비밥 비행시 
    #long_now = msg.longitude                   # 비밥 비행시 

if __name__ == '__main__':
    rospy.init_node('play_alarm')
    rospy.Subscriber('/bebop/states/ardrone3/PilotingState/PositionChanged', Ardrone3PilotingStatePositionChanged, cb_get_gps)
    account_sid = 'twlilo_sid'
    auth_token = 'twlilo_token'
    client = Client(account_sid, auth_token)

    #일단, 구동하자마자 시작점의 위도, 경도를 파라미터에 저장한다.
    while not rospy.is_shutdown():
        try:
            if ( lati_now >=34.0 and lati_now <=38.0 and long_now >= 126.0 and long_now <=130.0 ):
                start_lati = lati_now 
                start_long = long_now 
                rospy.set_param("/ori_lati", start_lati)
                rospy.set_param("/ori_long", start_long)
                break
        except:
            continue

    try:
        while not rospy.is_shutdown():
            if rospy.get_param("/play_alarml/fire_detection_state") is True:
                playsound('/home/kicker/catkin_ws/src/bb2_pkg/scripts/alarm.mp3') 
                alarm_s1 = str(lati_now) + ', '
                alarm_s2 = str(long_now)
                alarm_s3 = "에서 화재가 발생하였습니다"
                alarm_message = alarm_s1+alarm_s2+alarm_s1+alarm_s3
                print(alarm_message)
                message = client.account.messages.create(to="+82개인휴대폰 번호", from_="+twlilo 공식 번호", body= alarm_message )
                rospy.sleep(3)
    except rospy.ROSInterruptException:
        exit()
        
