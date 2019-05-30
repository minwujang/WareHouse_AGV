import socket
import struct
import time
import threading
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np

# it should import the positioning code.

# 'Start': 0, 'Start-1': 11, 'Start-2': 12, 'Start-3': 13, 'Start-4': 14, 
# 'Yongsan': 20, 'Yangcheon': 21, 'Songpa': 22, 'Seongbuk': 23, 'Dongjak': 24, 
# 'Seocho': 30, 'Seodaemun': 31, 'Mapo': 32, 'Jonno': 33, 'Guro': 34, 
# 'Gwangjin': 40, 'Nowon': 41, 'Gwanak': 42, 'Gangnam': 43, 'Gangbuk': 44}


# the point that the RC_car is on
# CURRENT_POSITION

# type of msg
BUSY = False
READY = True
FORWARD = 2
ROTATE = 3
WAIT = 4

SERVER_IP_ADDRESS = "192.168.0.101"
SERVER_PORT_NUM = 56774
PI_IP_ADDRESS = "192.168.0.102"
PI_PORT_NUM = 43179
PI_CMD_PORT = 56227

class pi_car(object):
    def __init__(self):
        self.cmd = None
        self.state = BUSY
        self.position = -1
        self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cmd_socket.bind((PI_IP_ADDRESS, PI_CMD_PORT))
        self.cmd_socket.listen()
    
    def position_detection(self):
        cap = cv2.VideoCapture(0) # the parameter(0) could be '1'
        
        while True:
            _, frame = cap.read()
    
            decoded_objects = pyzbar.decode(frame)
            for obj in decoded_objects:
                # print("Data", obj.data, type(obj.data), type(obj))
                # cv2.putText(frame, str(obj.data), (50, 50), font, 2, (255, 0, 0), 3)
                if ((self.position != int(obj.data)) & (int(obj.data)>=0) & (int(obj.data<= 44))):
                    self.position = int(obj.data)
                else:
                    # when car is forwarding QR_code would not be detected than return '-1'
                    self.position = -1


    # These functions should be executed after the server socket have been listen state.
    def send_msg_to_server(self):    
        time.sleep(0.5) 
    
        # while True:   
        clnt_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clnt_socket.connect((SERVER_IP_ADDRESS, SERVER_PORT_NUM))
        
        data = (self.state, self.position)
        payload_format = struct.Struct('? i')
        payload = payload_format.pack(*data)

        clnt_socket.send(payload)
        clnt_socket.close()

    def receive_cmd(self):
        # time.sleep(0.5) 
        # while True:   
        
        conn, addr = self.cmd_socket.accept()

        temp_msg = conn.recv(1024)
        datagram_format = struct.Struct("i")
        recv_value = datagram_format.unpack(temp_msg)
        self.cmd = int(recv_value)
        self.state = BUSY
        conn.close()


    '''
    def positioning(self):
        ~~~
        self.state = READY


    def forward(self):
        ~~~
        self.positioning()

    def rotate(self):
        ~~~
        self.positioning()
    '''           


if __name__ == "__main__": 
    pi_myself = pi_car()
    position_detection_thread = threading.Thread(target=pi_myself.position_detection)
    position_detection_thread.start()

    # pi_myself.positioning() 
    pi_myself.send_msg_to_server()
    pi_myself.receive_cmd()


    


