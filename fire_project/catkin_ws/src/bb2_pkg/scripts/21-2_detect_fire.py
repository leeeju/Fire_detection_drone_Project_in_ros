#!/usr/bin/env python
#-*- coding: utf-8 -*-

#불을 발견하고 이에 따라 비행을 제어하는 코드를 아래와 같다.

import rospy, cv2, datetime, time, subprocess, rosnode
import serial
from std_msgs.msg import String
from bb2_pkg.MoveBB2_2 import MoveBB2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
import numpy as np 

class DetectFire:

  def __init__(self):
    #self.sub = rospy.Subscriber("image_raw", Image, self.callback)
    #노트북의 캠을 쓰는 경우, 즉, rosrun uvc_camera uvc_camera_node를 실행한 경우
    self.sub = rospy.Subscriber("/bebop/image_raw", Image, self.callback)      #드론 비밥의 이미지를 구독할 경우
    
    self.bridge = CvBridge()
    self.cv_msg = cv2.imread("cimg.png")

  def callback(self,data):
    try:
      self.cv_msg = self.bridge.imgmsg_to_cv2(data, "bgr8")
        
    except CvBridgeError as e:
      print(e)

  def save_picture(self, picture):
    try:
      img = picture
      now = datetime.datetime.now() #datetime.strftime(format)은 명시적인 포맷 문자열에 의해 제어되는 날짜와 시간을 나타내는 문자열을 반환한다.
      date = now.strftime('%Y%m%d')
      hour = now.utcnow().strftime('%H%M%S%f')
      filename = '/home/kicker/fire_img/fire_{}_{}.png'.format(date, hour)
      cv2.imwrite(filename, img)
    except CvBridgeError as e:
      print(e)

if __name__ == '__main__':

    rospy.init_node('fire_detector', anonymous=False)
    fly = rospy.Publisher('/bebop/cmd_vel', Twist, queue_size = 1)
    sp = serial.Serial('/dev/ttyUSB0', 9600)
    df = DetectFire()
    tw = Twist()
    rospy.sleep(1.0)
    
    mb = MoveBB2()
    #드론 비행의 스피드를 저장하는 변수
    dspeed = 0.2

    #rosnode kill 코드 블록이 조건에 따라 실행되도록 하는 인덱스 변수를 아래와 같이 설정한다.
    i = 0
    #사진을 찍는 코드의 실행 횟수를 저장하는 인덱스 변수를 아래와 같이 설정한다.
    j = 0
    #불을 인지했는지 판단하는 내부 변수를 설정한다.
    per_fire = 0
    #불을 인지하지 못한 시간을 저장하는 변수.
    ztime = 0.0
    #불을 인지했을 때의 시간을 저장하는 변수
    ftime = 0.0

    try:
        #fire_cascade = cv2.CascadeClassifier('/home/kicker/catkin_ws/src/bb2_pkg/scripts/fire_detection.xml') 
        fire_cascade = cv2.CascadeClassifier('/home/kicker/catkin_ws/src/bb2_pkg/scripts/cascade025.xml')
            

        while not rospy.is_shutdown():
           cod1 = rospy.get_param("/fire_detectorl/param_of_detector")
           if cod1 == True:
            #print("화재 탐지를 시작합니다.") 여기세 이 출력문을 넣으면, 반복문이 돌 때 계~속 출력함.
            frame = df.cv_msg
            #gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fire  = fire_cascade.detectMultiScale(frame, 1.2, 5)

            # hsv 스케일 변환
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
            lower_red = np.array([-10, 100, 100])    #빨강색
            upper_red = np.array([10, 255, 255])
            maks_red = cv2.inRange(hsv, lower_red, upper_red)
            rec3 = cv2.bitwise_and(frame, hsv, mask = maks_red)

            # Contours 윤곽선 추출
            img_gray = cv2.cvtColor(rec3, cv2.COLOR_BGR2GRAY)
            ret, img_binary = cv2.threshold(img_gray, 127, 255, 0)
            contours, hierarchy = cv2.findContours(img_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) 
            
            
            
            #이는 불을 잠깐 인지했으나, 화면의 중앙에 맞추는 가운데 그 개체가 사라진 경우를 처리할 때 사용한다. 만일, 최초로 불을 발견한 시점과 불을 인지하지 못한 시점이 어느 한계를 넘어간다면 다시 Flytarget을 실행한다.
            
            if len(fire) == 0:
              #불이 발견되지 않은 경우에 "/play_alarm/fire_detection_state"를 0으로 설정한다. /play_alarm/fire_detection_state는 화재가 발생했음을 소리나 SMS 등으로 알리는 코드를 실행하기 위한 파라미터(parameter)이다.
              rospy.set_param("/play_alarml/fire_detection_state", False)
              #이전에 불을 발견했으나(즉, per_fire가 1이나) 발견되지 않은 시간을 저장한다
              if per_fire == 1:
                #불이 발견되지 않은 시간을 저장한다.
                ztime = time.time()
                #불을 발견했던 시간과 그 이후에 발견하지 못한 시간의 차이를 저장하기 위한 변수를 만든다.
                gap_time = ztime - ftime
                #불을 발견했던 시간과 그 이후에 발견하지 못한 시간의 차이가 30초 이상이면(즉 그 30초 동안 불을 발견하지 못했다면) 아래의 코드를 실행한다.
                #print(gapstr)
                if gap_time >= 10.0:
                  print("화재로 의심되는 개체가 잠까 발견되었으나 확실하지 않습니다.")
                  #불 감지 모드는 끝다.
                  per_fire = 0
                  #불을 발견했던 시간과 그 이후에 발견하지 못한 시간의 차이가 60초 이상이면(즉 그 10초 동안 불을 발견하지 못했다면) 다시 순행 비행을 시작한다.
                  #이후에 다시 실행하는 detect_fire.py에서 다시 FlyTarget.py를 시작할 수 있도록 i값을 다시 설정한다.
                  i = 0
                  #사진 촬영 횟수를 초기화한다.
                  j = 0
                  #열려진 창을 닫는다.
                  cv2.destroyWindow('frame')
                  #다시 순행비행을 시작하는 파마미터를 설정한다.
                  rospy.set_param("/fly_to_targetl/param_of_flying", 1)
                  #비행 노드를 실행하기 위하여 Manager 노드의 파라미터 값을 변경시킨다.
                  rospy.set_param("/Fire_drone_managerl/order", 1)
                  #rospy.sleep(15)

            else:
              for (x,y,w,h) in fire:
                  cv2.rectangle(frame,(x-20,y-20),(x+w+20,y+h+20),(255,0,0),2)
                  #roi_gray = gray[y:y+h, x:x+w]
                  #roi_color = frame[y:y+h, x:x+w]
                  print("화재가 의심되는 장면을 포착하였습니다.")
                  #일단 불을 발견했다면, 불을 인지했는지 판단하는 내부 변수(per_fire)를 변화시킨다.
                  per_fire = 1
              
              for cnt in contours:  #중심점 잡기
                  cv2.drawContours(img_gray, [cnt], 0, (255, 0, 0), 5)

              for cnt in contours:  #윤곽선 잡기
                  hull = cv2.convexHull(cnt)
                  cv2.drawContours(img_gray, [hull], 0, (0, 0, 255), 5)

                  #불을 발견했다면, 불을 인지한 시간을 저장한다.
                  ftime = time.time()

                  #불을 발견했다면 패트롤 모드(patrol mode)를 종료하고 adjust mode를 실행한다. 단, 한 번만 실행한다. 
                  if i == 0:
                    rosnode.kill_nodes(['/fly_to_targetl'])
                    i = 1

                  fx = x + (w * 0.5)
                  fy = y + (h * 0.5)

                  if ((fx >= 190)and(fx <= 450)) and ((fy >= 150)and(fy <= 330)):
                    #인식된 불이 화면의 중앙에 있을 경우에는 아래의 코드를 실행한다.
                    #드론의 비행을 멈춘다.
                    tw.linear.x = 0
                    tw.linear.y = 0
                    fly.publish(tw)
                    print("화재 장면을 화면의 중앙에 맞췄습니다({}, {})".format(fx, fy))
                    #화재 경보를 알리는 코드를 활성화한다.
                    rospy.set_param("/play_alarml/fire_detection_state", True)
                    #동일한 화재에 대한 사진 촬영의 횟수가 5미만이면 사진을 찍는다.
                    if j < 3:
                      #화재 사진을 찍는다.
                      df.save_picture(frame)
                      #화재 촬영하는 시간을 저장한다.
                      print("화재 장면을 {}회 찍었습니다.".format(j+1))
                      #사진 촬영의 횟수를 j에 반영한다.
                      j = j + 1
                      #rospy.sleep(5)
                      #사진을 촬영한 시간과 화재를 발견한 시간이 20초 이상 지났는지 확인한다

                    else:
                      mb.move_x(0.1, 0.1)
                      #sp.write('1')
                      print("소화탄을 투척합니다.")
                      #화재 경보를 알리는 코드를 비활성화한다.
                      rospy.set_param("/play_alarml/fire_detection_state", False)
                      #열려진 창을 닫는다.
                      cv2.destroyWindow('frame')
                      #처음 지점으로 되돌아 오는 비행 모드의 파라미터를 활성화한다.
                      rospy.set_param("/fly_to_targetl/param_of_flying", 2)
                      #매니저 노드가 비행 코드를 실행하도록 파라미터를 설정한다
                      rospy.set_param("/Fire_drone_managerl/order", 1)
                      #파라미터가 반영될 시간과 내부 코트의 작동 속도에 차이를 생각하여 일정한 시간동안 대기하고 있는다.
                      #rospy.sleep(10)
                      exit()

                  elif ((fx >= 190) and (fx <= 450)) and ((fy >= 331) and(fy <= 480)):
                      #화재가 화면의 아래에서 발견된 경우 뒤로 이동시킨다.
                      tw.linear.x = -dspeed
                      tw.linear.y = 0
                      fly.publish(tw)
                      
                  elif ((fx >= 190) and (fx <= 450)) and ((fy >= 0 ) and(fy <= 149)):
                      #화재가 화면의 위에서 발견된 경우 드론을 앞으로 이동시킨다.
                      tw.linear.x = dspeed
                      tw.linear.y = 0
                      fly.publish(tw)

                  elif ((fx >= 0) and (fx <= 189)) and ((fy >= 151 ) and(fy <= 329)):
                      #화재가 화면의 왼쪽에서 발견된 경우 드론을 왼쪽으로 이동시킨다
                      tw.linear.x = 0
                      tw.linear.y = dspeed
                      fly.publish(tw)

                  elif ((fx >= 0) and (fx <=189)) and ((fy >= 331) and (fy <= 480)):
                      #화재가 화면의 왼쪽 아래에서 발견된 경우 드론을 왼쪽 아래로 이동시킨다.
                      tw.linear.x = -dspeed
                      tw.linear.y = dspeed
                      fly.publish(tw)

                  elif ((fx >= 0) and (fx <=189)) and ((fy >= 0) and (fy <= 149)):
                      #화재가 화면의 왼쪽 위에서 발견된 경우 드론을 왼쪽 위로 이동시킨다.
                      #print("fire left up")
                      tw.linear.x = dspeed
                      tw.linear.y = dspeed
                      fly.publish(tw)

                  elif ((fx >= 450) and (fx <=640)) and ((fy >= 331) and (fy <= 640)):
                      #화재가 오른쪽 아래에서 발견된 경우 드론을 오른쪽 아래로 이동시킨다.
                      tw.linear.x = -dspeed
                      tw.linear.y = -dspeed
                      fly.publish(tw)

                  elif ((fx >= 450) and (fx <=640)) and ((fy >= 0) and (fy <= 149)):
                      #화재가 오른쪽 위에서 발견된 경우, 드론을 오른쪽 위로 이동시킨다.
                      tw.linear.x = dspeed
                      tw.linear.y = -dspeed
                      fly.publish(tw)
                  elif ((fx >= 451) and (fx <= 640)) and ((fy >= 150 ) and(fy <= 330)):
                      #화재가 오른쪽에 있을 경우, 드론을 오른쪽으로 이동시킨다.
                      tw.linear.x = 0
                      tw.linear.y = -dspeed
                      fly.publish(tw)                    
                  else:
                    pass
                    
            frame     = cv2.resize(frame,      dsize=(0, 0), fx=1.0, fy=1.0, interpolation=cv2.INTER_CUBIC)
            rec3      = cv2.resize(rec3,     dsize=(0, 0), fx=0.4, fy=0.4, interpolation=cv2.INTER_CUBIC)
            img_gray  = cv2.resize(img_gray, dsize=(0, 0), fx=0.4, fy=0.4, interpolation=cv2.INTER_CUBIC)        

            cv2.imshow('frame', frame)
            cv2.imshow('HSV', rec3)
            cv2.imshow('contours', img_gray) #img_binary
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        rospy.spin()

    except KeyboardInterrupt:
        print("Shutting down")
