import socket
import struct
import time
import threading
from TextDetection import WordDetect
import argparse
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#tab, shift tab
map = {'Start': 0, 'Start-1': 1, 'Start-2': 2, 'Start-3': 3, 'Start-4': 4, 'Yongsan': 10, 'Yangcheon': 11, 'Songpa': 12, 'Seongbuk': 13, 'Dongjak': 14, 'Seocho': 20, 'Seodaemun': 21, 'Mapo': 22, 'Jonno': 23, 'Guro': 24, 'Gwangjin': 30, 'Nowon': 31, 'Gwanak': 32, 'Gangnam': 33, 'Gangbuk': 34}
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
# PI2_IP_ADDRESS = "192.168.137.0"
PI_PORT_NUM = 43179
PI_CMD_PORT = 56227

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str, help="path to input image")
ap.add_argument("-east", "--east", type=str, help="path to input EAST text detector")
ap.add_argument("-c", "--min-confidence", type=float, default=0.5, help="minimum probability required to inspect a region")
ap.add_argument("-w", "--width", type=int, default=320, help="nearest multiple of 32 for resized width")
ap.add_argument("-e", "--height", type=int, default=320, help="nearest multiple of 32 for resized height")
ap.add_argument("-p", "--padding", type=float, default=0.0, help="amount of padding to add to each border of ROI")
args = vars(ap.parse_args())

class Node(object):
    def __init__(self, data):
        self.data = data
        self.next = None

class AGV(object):
    def __init__(self,_PORT_NUM):
        self.location = None
        self.status = False
        # implies Ready or notReady(on action or positioning)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((SERVER_IP_ADDRESS, _PORT_NUM))
        self.server_socket.listen()

    # def receiving_message():
    #
    #     while True:
    #         # recv_msg = input('What is the value u want?')
    #         # recv_int = int(recv_msg)
    #         # data = [recv_int]
    #         # data_format = struct.Struct("i")
    #         # code_value = data_format.pack(*data)
    #         # server_socket.send(code_value)
    #
    #         conn, addr = server_socket.accept()
    #
    #         temp_msg = conn.recv(1024)
    #         datagram_format = struct.Struct("? i")
    #         recv_list = datagram_format.unpack(temp_msg)
    #
    #         conn.close()
    #
    #     server_socket.close()


class Queue(object):
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None

    def isEmpty(self):
        return self.head == None

    def peek(self):
        return self.head.data

    def peeknext(self):
        self.current = self.head.next
        return self.current.data

    def enqueue(self, data):
        new_data = Node(data)
        if self.head is None:
            self.head = new_data
            self.tail = self.head
        else:
            self.tail.next = new_data
            self.tail = new_data

    def dequeue(self):
        data = self.head.data
        self.head = self.head.next
        if self.head is None:
            self.tail is None
        return data


def makeQueue(destination):
    q = Queue()
    if destination in map:
        key = map[destination]
        x = key % 10
        y = int(key / 10)
        print(x, y)

        #for i in range(0, x + 1):
        for j in range(1, y + 1):
            q.enqueue((0, j))
        if (x != 0):
            for i in range(1, x + 1):
                q.enqueue((i, y))
        for k in range(y-1, -1, -1):
                q.enqueue((x, k))
        for l in range(x-1, -1, -1):
            q.enqueue((l, 0))
    return q

def command(myself, current_location_myself, current_location_other, destination_myself):
    # is car direction as an input needed?
    if destination_myself in map:
        key = map[destination_myself]
        i = key % 10
        j = int(key / 10)

    x = current_location_myself % 10
    y = int(current_location_myself / 10)
    coordinate_myself = (x, y)

    a = current_location_other % 10
    b = int(current_location_other / 10)
    coordinate_other = (a, b)

    # car sending ready and his position at the origin after positioning and rotation, and no queue generated
    while (myself.isEmpty() == False):
        if (myself.peek() != coordinate_other):
            if (coordinate_myself == (0, 0) or coordinate_myself == (0, j) or coordinate_myself == (i, 0)):
                send_cmd_to_pi(ROTATE_FORWARD)
                print('sent ROTATE_FORWARD')
            elif (coordinate_myself == (i, j)):
                send_cmd_to_pi(ROTATE_FORWARD_PUTDOWN)
                print('sent ROTATE_FORWARD_PUTDOWN')
            else:
                myself.dequeue()
                send_cmd_to_pi(FORWARD)
                print('sent FORWARD')
        else:
            send_cmd_to_pi(WAIT)
            print('sent WAIT')

def send_cmd_to_pi(cmd):
    time.sleep(0.5)

    # while True:
    cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cmd_socket.connect((PI_IP_ADDRESS, PI_CMD_PORT))


    payload_format = struct.Struct('i')
    data = [cmd]
    payload = payload_format.pack(*data)

    cmd_socket.send(payload)
    cmd_socket.close()

def main (socket_location, socket_other_location, READY):
    myself = makeQueue('Start')
    # test whether myself.isEmtpy
    print(myself.isEmpty())
    while(True):
        if (myself.isEmpty() == True and socket_location == 0):
            destination = WordDetect.main(args)
            print('destionation is : ' + destination)
            if destination in map:
                print("Seongbuk is in the map")
                # destination_myself is the output of OCR text detection
                myself = makeQueue(destination)
                print("queue has been made")
                continue
            else:
                continue
        elif (READY == True):
            # between send command and receive ready, there should be no command to the car
            command(myself, socket_location, 33, destination)
            print('command sent')
            READY = False
            continue
        else:
            continue


if __name__ == '__main__':
    # import cho's socket and use it as an input
    # receive, send, main should be threaded
    car1 = AGV(SERVER_PORT_RECV_A)
    #car2 = AGV(SERVER_PORT_RECV_B)

    while(True):
        conn1, addr1 = car1.server_socket.accept()
        # #conn2, addr2 = car2.server_socket.accept()
        #
        temp_msg1 = conn1.recv(1024)
        datagram_format = struct.Struct("? i")
        recv_list1 = datagram_format.unpack(temp_msg1)
        conn1.close()
        car1.status = int(recv_list1[0])
        car1.location = int(recv_list1[1])

        print(car1.location)
        print(car1.status)


        # temp_msg2 = conn2.recv(1024)
        # recv_list2 = datagram_format.unpack(temp_msg2)
        # conn2.close()
        # car2.status = int(recv_list2[0])
        # car2.location = int(recv_list2[1])

        # for different host ip make AGV using the socket
        main(car1.location, 33, car1.status)
        # main(car2.location, car1.location, car2.status)