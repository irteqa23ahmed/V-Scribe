import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new

HOST=''
PORT=8089

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print ('Socket created')

s.bind((HOST,PORT))
print ('Socket bind complete')
s.listen(10)
print ('Socket now listening')

conn,addr=s.accept()

### new
data = b""
payload_size = struct.calcsize("Q") 
while True:
    while len(data) < payload_size:
        packet = conn.recv(4*1024) # 4K
        if not packet: break
        data = data + packet
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]
    while len(data) < msg_size:
        data += conn.recv(4*1024)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame=pickle.loads(frame_data)
    print(frame)

    # Show in webapp or send to webapp
    cv2.imshow('frame',frame)
    cv2.waitKey(1)