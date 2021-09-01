#!/usr/bin/env python
#-*- coding: utf-8 -*-

import rospy, sys
from std_msgs.msg import Empty
from geometry_msgs.msg import Twist
from bebop_msgs.msg import Ardrone3PilotingStateAttitudeChanged, \
                           Ardrone3PilotingStatePositionChanged, \
                           Ardrone3PilotingStateAltitudeChanged, \
                           Ardrone3GPSStateNumberOfSatelliteChanged
from scipy import sqrt, cos, sin, arctan2, pi
from math import degrees, radians


'''
    GPS for center of map  ( 36.51994848698016, 127.17306581466163)
    Parot-Sphinx start GPS ( 48.878900,           2.367780        )
    diffrence              (-12.358951513,     +124.805285815     ) 
'''
#OFFSET_LAT = -12.358951513           #스핑크스 사용시
#OFFSET_LON = 124.805285815           #스핑크스 사용시

OFFSET_LAT = 0.0                      #비밥 드론 사용시
OFFSET_LON = 0.0                      #비밥 드론 사용시

LIN_SPD    = 0.40                      #회전 속도
ANG_SPD    = 0.25 * pi

FLIGHT_ALT = 0.5                    #  <---- 고도 조절
DEG_PER_M  = 0.00000899320363721
'''
                               p2 (lat2,lon2)
                       | | |   /         
                       | | |  / 
                       | | |0/  
                       | | |/              
                       | |0/    
                       | |/      
                       |0/<--- bearing         
                       |/________     
                       p1 (lat1,lon1)
                       
  when center is (a,b), equation of circle : pow((x-a),2) + pow((y-b),2) = pow(r,2)
'''
class MoveByGPS:
    
    def __init__(self):
        
        rospy.Subscriber('/bebop/states/ardrone3/PilotingState/AttitudeChanged',       # 비행상태 확인
                         Ardrone3PilotingStateAttitudeChanged,
                         self.cb_get_atti)
        rospy.Subscriber('/bebop/states/ardrone3/PilotingState/PositionChanged',       # 위도 경도 고도 정보 확인
                         Ardrone3PilotingStatePositionChanged,
                         self.cb_get_gps)
        rospy.Subscriber('/bebop/states/ardrone3/PilotingState/AltitudeChanged',       # 고도정보 확인
                         Ardrone3PilotingStateAltitudeChanged,
                         self.cb_get_alti)
        rospy.Subscriber('/bebop/states/ardrone3/GPSState/NumberOfSatelliteChanged',   # 위성갯수 확인
                         Ardrone3GPSStateNumberOfSatelliteChanged,
                         self.cb_get_num_sat)

        self.atti_now    = self.atti_tmp  =   0.0        
        self.use_tmp     = False        
        self.lati_now    = self.long_now  = 500.0
        self.alti_gps    = self.alti_bar  =   0.0
        self.bearing_now = self.bearing_ref = 0.0
        
        self.margin_angle  = radians(5.0)
        self.margin_radius = DEG_PER_M * 1.3
        self.margin_alt    = 0.25
        
        rospy.sleep(3.0)


    def cb_get_num_sat(self, msg):
        pass


    def cb_get_alti(self, msg):
        self.alti_bar = msg.altitude


    def cb_get_gps(self, msg):
        self.lati_now = msg.latitude  + OFFSET_LAT
        self.long_now = msg.longitude + OFFSET_LON
        self.alti_gps = msg.altitude


    def cb_get_atti(self, msg):
    
        self.atti_now = msg.yaw
        
        if   msg.yaw < 0:
            self.atti_tmp = msg.yaw + pi 
        elif msg.yaw > 0:
            self.atti_tmp = msg.yaw - pi
        else:
            self.atti_tmp = 0.0
            
    
    def get_atti(self):
        if self.use_tmp == True:
            return self.atti_tmp
        else:
            return self.atti_now
            
    
    def get_bearing(self, lat1, lon1, lat2, lon2):
    
        Lat1,  Lon1 = radians(lat1), radians(lon1) 
        Lat2,  Lon2 = radians(lat2), radians(lon2) 
        
        y = sin(Lon2-Lon1) * cos(Lat2) 
        x = cos(Lat1) * sin(Lat2) - sin(Lat1) * cos(Lat2) * cos(Lon2-Lon1) 
        
        return arctan2(y, x)
    
        
    def get_gps_now(self):
        return self.lati_now, self.long_now

    
    def rotate(self, lat2, lon2, speed):
        
        pub = rospy.Publisher('/bebop/cmd_vel', Twist, queue_size = 1)
        tw  = Twist()
        
        lat1, lon1 = self.get_gps_now()
        
        target  = self.get_bearing(lat1, lon1, lat2, lon2)
        
        current = self.atti_now;        angle = abs(target-current)
        
        if angle > pi:  #   if angle > radians(180):
            self.use_tmp = True            
            if   target > 0.0:
                target = target - pi
            elif target < 0.0:
                target = target + pi
            else:   pass
            current = self.get_atti();  angle = abs(target - current)
        else:           #   if angle > radians(180):
            self.use_tmp = False        
        
            
        if   target > current:    # cw, -angular.z
            
            tw.angular.z = -speed
            
            if   angle > radians(50):
                target = target - radians(5)
            elif angle > radians(20): 
                target = target - radians(10)
            else:
                tw.angular.z = -0.1125
                
            while target > current:
                if abs(tw.angular.z) > 0.125:
                    tw.angular.z = -speed * abs(target - current) / angle
                else:
                    tw.angular.z = -0.125
                current = self.get_atti();  pub.publish(tw)
                
        elif target < current:    # ccw,  angular.z            
            
            tw.angular.z =  speed
            
            if   angle > radians(50):
                target = target + radians(5)
            elif angle > radians(20): 
                target = target + radians(10)
            else:
                tw.angular.z =  0.1125
                
            while target < current:
                if abs(tw.angular.z) > 0.125:
                    tw.angular.z =  speed * abs(target - current) / angle
                else:
                    tw.angular.z =  0.125
                current = self.get_atti();  pub.publish(tw)
                
        else:   pass

        
    def check_route(self, lat2, lon2):
        
        lat_now, lon_now = self.get_gps_now()
        
        bearing = self.get_bearing(lat_now, lon_now, lat2, lon2)
        
        if bearing > self.bearing_ref - self.margin_angle and \
           bearing < self.bearing_ref + self.margin_angle:
            return True
        else:
            return False


    def check_alt(self):
        if self.alti_bar > FLIGHT_ALT - self.margin_alt and \
           self.alti_bar < FLIGHT_ALT + self.margin_alt:
            return True
        else:
            return False
            
    
    def check_arrived(self, lat2, lon2):
        '''
        when center is (a,b), equation of circle : pow((x-a),2) + pow((y-b),2) = pow(r,2)
        pow((lat_now-lat2), 2) + pow((lon_now-lon2), 2) = pow(self.margin_radius, 2)
        self.margin_radius = sqrt(pow((lat_now-lat2), 2) + pow((lon_now - lon2), 2))
        '''
        lat_now, lon_now = self.get_gps_now()
        radius = sqrt(pow((lat_now-lat2), 2) + pow((lon_now - lon2), 2))
        
        if radius < self.margin_radius:
            return True
        else:
            return False
    def move_to_target(self, lat1, lon1, lat2, lon2):
        
        pub = rospy.Publisher('/bebop/cmd_vel', Twist, queue_size=1)        
        tw  = Twist()
        
        while self.check_arrived(lat2, lon2) is False:
            
            if self.check_alt() is False:
                if self.check_alt() > FLIGHT_ALT:
                    tw.linear.z = -0.1
                else:
                    tw.linear.z =  0.1
            else:
                tw.linear.z = 0.0
            
            if self.check_route(lat2, lon2) is True:
                tw.linear.x = LIN_SPD;  pub.publish(tw)
                
            else:
                lat1, lon1 = self.get_gps_now()
                self.bearing_ref = self.get_bearing(lat1, lon1, lat2, lon2)
                self.rotate(lat2, lon2, radians(45))
                
        tw.linear.x = 0;  pub.publish(tw); rospy.sleep(2.0)

        rot_lati = self.lati_now + 10
        rot_long = self.long_now
        
        self.rotate(rot_lati, rot_long, radians(0))
        print "arrived to target gps position(%s, %s) %s(m) northbound direction above sea level!!!" \
              %(self.lati_now, self.long_now, self.alti_gps)

    def fly_to_target(self, p2_lati_deg, p2_long_deg):
        if not rospy.is_shutdown(): 
            cmd  = rospy.Publisher('/bebop/cmd_vel', Twist, queue_size = 1)
            pub4 = rospy.Publisher('/bebop/camera_control', Twist, queue_size = 1)

            tw   = Twist()            
            rospy.sleep(0.5)

            tw.linear.z = LIN_SPD
            while self.alti_bar < FLIGHT_ALT:
                cmd.publish(tw)
            tw.linear.z = 0.0;  cmd.publish(tw)       

            #카메라가 정면을 바라보도록 한다.
            tw.angular.y = 0.0
            pub4.publish(tw)

            p1_lati_deg = self.lati_now
            p1_long_deg = self.long_now
            print("{}, {}에서 {}, {}으로 이동합니다".format(p1_lati_deg, p1_long_deg, p2_lati_deg, p2_long_deg))

            self.bearing_ref = self.get_bearing(p1_lati_deg, p1_long_deg, p2_lati_deg, p2_long_deg)

            self.rotate(p2_lati_deg, p2_long_deg, radians(45))        
            self.move_to_target(p1_lati_deg, p1_long_deg, p2_lati_deg, p2_long_deg)

            #도착한 후 카메라가 45도를 바라보도록 한다.
            tw.angular.y = -45
            pub4.publish(tw)
        else:
            exit()
