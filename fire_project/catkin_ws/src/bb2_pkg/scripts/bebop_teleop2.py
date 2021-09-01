#!/usr/bin/env python
#-*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from bb2_pkg.GetChar import GetChar
 
msg = '''
---------------------------------------------------
 1:take off, 2:landing, 3:emergency, sp:stop(hover)
---------------------------------------------------
        w                           i                      
   a    s    d                j     k     l
---------------------------------------------------
w/s : up  / down           i/k : foward / backword
a/d : ccw / cw             j/l : left   / righ
---------------------------------------------------
-/+ : decrease / increase linear  speed by 10%
,/. : decrease / increase angular speed by 10%
---------------------------------------------------
Type 'Q' to quit

'''

# set direction for each move
moveBindings = {
    'w':( 0, 0, 1, 0), 'a':( 0, 0, 0, 1), 'i':( 1, 0, 0, 0), 'j':( 0, 1, 0, 0), 
    's':( 0, 0,-1, 0), 'd':( 0, 0, 0,-1), 'k':(-1, 0, 0, 0), 'l':( 0,-1, 0, 0),
    ' ':( 0, 0, 0, 0)
}

# '+', '-': for linear velocity / '>', '<': for angular velocity
speedBindings = {
#                   '+'             '<'             '>'
    '-':(0.9, 1.0), '=':(1.1, 1.0), ',':(1.0, 0.9), '.':(1.0, 1.1), '0':(1.0, 1.0)
}


class MoveBebop():

    def __init__(self):
    
        rospy.init_node('bebop_teleop_key')
        
        self.pub0 = rospy.Publisher('/bebop/cmd_vel', Twist, queue_size = 1)
        self.pub1 = rospy.Publisher('/bebop/takeoff', Empty, queue_size = 1)         # 이륙
        self.pub2 = rospy.Publisher('/bebop/land',    Empty, queue_size = 1)         # 착륙
        self.pub3 = rospy.Publisher('/bebop/reset',   Empty, queue_size = 1)         # 비상 정지
        self.pub4 = rospy.Publisher('/bebop/camera_control', Twist, queue_size = 1)  #카메라 컨트롤
        
        self.empty_msg = Empty()
        self.key_input = GetChar()
        self.pt        = Twist()
        
        self.lin_spd = rospy.get_param("~speed", 0.5)
        self.ang_spd = rospy.get_param("~turn",  1.0)
        
        self.lin_x   =  0      # for linear.x
        self.lin_y   =  0      # for linear.y
        self.lin_z   =  0      # for angular.z
        self.ang_z   =  0      # for linear.z
        self.count   =  0
        self.cnt4msg = 10      # print how2use every (cnt4msg)time
        
        rospy.sleep(3.0)
        
    def get_speed(self, lin, ang):
        return "current speed:\tlinear = %s, angular = %s " % (lin, ang)


if __name__ == '__main__': 
    try:
        mb = MoveBebop()
        
        print(msg)
        print(mb.get_speed(mb.lin_spd, mb.ang_spd))
        
        key = ' '
        
        while not rospy.is_shutdown():   # while not rospy.is_shutdown():
        
            key = mb.key_input.getch()
    
            if   key == '1':
                mb.pub1.publish(mb.empty_msg);  mb.count = (mb.count + 1) % mb.cnt4msg; print "taking off"
                
            elif key == '2':
                mb.pub2.publish(mb.empty_msg);  mb.count = (mb.count + 1) % mb.cnt4msg; print "landing"
            
            elif key == '3':
                mb.pub3.publish(mb.empty_msg);  mb.count = (mb.count + 1) % mb.cnt4msg; print "emergency stop!!!"
            
            elif key == '4':
                mb.pt.angular.y = -90     # (-)카메라 상승 하강 각도   (+) 상승각도
                mb.pub4.publish(mb.pt);  mb.count = (mb.count + 1) % mb.cnt4msg; print "tilt down!"
            
            elif key == '5':
                mb.pt.angular.y = 0     # 카메라 정면 보기
                mb.pub4.publish(mb.pt);  mb.count = (mb.count + 1) % mb.cnt4msg; print "tilt up!"
                
            elif key in moveBindings.keys():
            
                mb.lin_x = moveBindings[key][0]
                mb.lin_y = moveBindings[key][1]
                mb.lin_z = moveBindings[key][2]
                mb.ang_z = moveBindings[key][3]
                    
                if   mb.lin_x ==  1:
                    print "forward"
                elif mb.lin_x == -1:
                    print "backward"
                      
                if   mb.lin_y ==  1:
                    print "move left"
                elif mb.lin_y == -1:
                    print "move right"
                
                if   mb.lin_z ==  1:
                    print "ascending"
                elif mb.lin_z == -1:
                    print "descending"
                      
                if   mb.ang_z ==  1:
                    print "turn left"
                elif mb.ang_z == -1:
                    print "turn right"
            
                mb.count = (mb.count + 1) % mb.cnt4msg
                
            elif key in speedBindings.keys():
                mb.lin_spd = mb.lin_spd * speedBindings[key][0]
                mb.ang_spd = mb.ang_spd * speedBindings[key][1]
 
                print(mb.get_speed(mb.lin_spd, mb.ang_spd))
                
                mb.count = (mb.count + 1) % mb.cnt4msg
                
            else:            
                pass
            
            if (mb.count == 0):
                    print(msg)
 
            tw = Twist()
            
            tw.linear.x  = mb.lin_x * mb.lin_spd
            tw.linear.y  = mb.lin_y * mb.lin_spd
            tw.linear.z  = mb.lin_z * mb.lin_spd
            
            #tw.angular.x = tw.angular.y = 0
            tw.angular.z = mb.ang_z * mb.ang_spd
            
            mb.pub0.publish(tw)
            
        mb.pub2.publish(mb.empty_msg);  print "landing"
 
    except KeyboardInterrupt:   # rospy.ROSInterruptException:
        mb.pub2.publish(mb.empty_msg);  print "landing"