# /usr/bin/env python
#-*- coding: utf-8 -*-

'''
드론의 구동알 알리는 문자 전송
'''
from twilio.rest import Client

account_sid = 'twlilo_sid'   #twlilo 에서 받은 개인키
auth_token = 'twlilo_token'      #twlilo 에서 받은 개인키
client = Client(account_sid, auth_token)


message = client.messages.create(
      body='문자 내용!',      #메시지 내용
      from_='+twlilo 공식 번호',                           #텔로 공식 번호
      to = '+82개인휴대폰 번호'                            #받을 문자 번호
          )

print(message.sid)
