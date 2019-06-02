import socket
import struct
import time
import threading
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import RC_CAR as rc

# it should import the positioning code.

# the point that the RC_car is on
# CURRENT_POSITION

# type of msg
BUSY = False
READY = True
FORWARD = 2
ROTATE = 3
WAIT = 4
ROTATE_FORWARD = 5
ROTATE_FORWARD_PUTDOWN = 6

SERVER_IP_ADDRESS = "192.168.43.170"
SERVER_PORT_NUM = 56774
SERVER_PORT_RECV_A = 47182
SERVER_PORT_RECV_B = 47183

PI_IP_ADDRESS = "192.168.43.111"
PI_PORT_NUM = 43179
PI_CMD_PORT = 56227

class pi_car(object):
    def __init__(self):
        self.cmd = None
        self.state = READY
        self.position = -1
        self.RC_CAR = rc.RC_CAR()
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

                if self.state != BUSY:
                    if ((self.position != int(obj.data)) & (int(obj.data)>=0) & (int(obj.data)<= 34)):
                        self.position = int(obj.data)
                        print(self.position)
                        break
                    else:
                        continue
                # else:
                #     # when car is forwarding QR_code would not be detected than return '-1'
                #     self.position = -1


    # These functions should be executed after the server socket have been listen state.


    def send_msg_to_server(self):
        time.sleep(0.5)

        # while True:   
        clnt_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("socket have been made")
        clnt_socket.connect((SERVER_IP_ADDRESS, SERVER_PORT_RECV_A))
        print("socket connected!!")

        payload_format = struct.Struct('? i')
        data = (self.state, self.position)
        payload = payload_format.pack(*data)

        clnt_socket.send(payload)
        print("sent the msg!!")
        clnt_socket.close()

    def receive_cmd(self):
        # time.sleep(0.5)
        # while True:

        conn, addr = self.cmd_socket.accept()

        temp_msg = conn.recv(1024)
        print("received the command")
        datagram_format = struct.Struct("i")
        recv_value = datagram_format.unpack(temp_msg)
        print("received the msg!! ", recv_value)
        self.cmd = int(recv_value[0])
        self.state = BUSY
        self.position = -1
        conn.close()

    def execute_cmd(self, cmd):
        if cmd == FORWARD:
            self.RC_CAR.forward(1.5)
        elif cmd == WAIT:
            time.sleep(4)
        elif cmd == ROTATE_FORWARD:
            self.RC_CAR.rotate_forward()

        elif cmd == ROTATE_FORWARD_PUTDOWN:
            self.RC_CAR.rotate()
            time.sleep(1)
            self.RC_CAR.stop()

        self.state = READY

        while True:
            if self.position != -1:
                break


if __name__ == "__main__":
    pi_myself = pi_car()
    # position_detection_thread = threading.Thread(target=pi_myself.position_detection)
    # position_detection_thread.start()
    pi_myself.position_detection()
    while True:
        if pi_myself.position != (-1):
            print("communication start!")
            pi_myself.send_msg_to_server()
            pi_myself.receive_cmd()
            pi_myself.execute_cmd(pi_myself.cmd)
            pi_myself.position_detection()
    # pi_myself.execute_command(pi_myself.cmd)

