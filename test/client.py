import cv2
import numpy as np
import socket
import sys
import pickle
import struct
import imutils

clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
while True:
    try:
        clientsocket.connect(('localhost',8089))
        break
    except:
        continue
while True:
        vid = cv2.VideoCapture(0)
        while(vid.isOpened()):
            try:
                img,frame = vid.read()
                frame = imutils.resize(frame,width=320)
                a = pickle.dumps(frame)
                message = struct.pack("Q",len(a))+a
                clientsocket.sendall(message)
            except Exception as e:
                print(e)
                break
