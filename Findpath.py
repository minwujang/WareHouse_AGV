import socket
import struct
import time
import threadimg
from Traffic-Sign-Detection import WordDetect

map = {'Start': 0, 'Start-1': 11, 'Start-2': 12, 'Start-3': 13, 'Start-4': 14, 'Yongsan': 20, 'Yangcheon': 21, 'Songpa': 22, 'Seongbuk': 23, 'Dongjak': 24, 'Seocho': 30, 'Seodaemun': 31, 'Mapo': 32, 'Jonno': 33, 'Guro': 34, 'Gwangjin': 40, 'Nowon': 41, 'Gwanak': 42, 'Gangnam': 43, 'Gangbuk': 44}
BUSY = False
READY = True
FORWARD = 2
ROTATE = 3
WAIT = 4
ROTATE_FORWARD = 5
ROTATE_FORWARD_PUTDOWN = 6

SERVER_IP_ADDRESS = "192.168.0.101"
SERVER_PORT_NUM = 56774
SERVER_PORT_RECV_A = 47182
SERVER_PORT_RECV_B = 47183

PI_IP_ADDRESS = "192.168.0.102"
# PI2_IP_ADDRESS = "192.168.137.0"
PI_PORT_NUM = 43179
PI_CMD_PORT = 56227

class Node(object):
    def __init__(self, data):
        self.data = data
        self.next = None

class AGV(object):
    def __init__(_PORT_NUM):
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
    if destination in map:
        key = map[destination]
        x = key % 10
        y = int(key / 10)
        print(x, y)

        q = Queue()
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
    # print(q.peek())
    # print(q.peeknext())
    # while (q.isEmpty() == False):
    #     print(q.dequeue())
    return q

def command(myself, current_location_myself, current_location_other, destination_myself):
    # is car direction as an input needed?
    if destination_myself in map:
        key = map[destination_myself]
        i = key % 10
        j = int(key / 10)

    if current_location_myself in map:
        key = map[current_location_myself]
        x = key % 10
        y = int(key / 10)
        coordinate_myself = (x, y)

    if current_location_other in map:
        key = map[current_location_other]
        a = key % 10
        b = int(key / 10)
        coordinate_other = (a, b)

    # car sending ready and his position at the origin after positioning and rotation, and no queue generated
    while (myself.isEmpty() == False):
        if (myself.peek() != coordinate_other):
            if (coordinate_myself == (0, 0) or coordinate_myself == (0, j) or coordinate_myself == (i, 0)):
                send_cmd_to_pi(ROTATE_FORWARD)
            elif (coordinate_myself == (i, j)):
                send_cmd_to_pi(ROTATE_FORWARD_PUTDOWN)
            else:
                myself.dequeue()
                send_cmd_to_pi(FORWARD)
        else:
            send_cmd_to_pi(WAIT)

def send_cmd_to_pi(self, cmd):
    time.sleep(0.5)

    # while True:
    cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cmd_socket.connect((PI_IP_ADDRESS, PI_CMD_PORT))

    data = cmd
    payload_format = struct.Struct('i')
    payload = payload_format.pack(*data)

    cmd_socket.send(payload)
    cmd_socket.close()

def main (socket_location, socket_other_location, READY):
    myself = makeQueue()
    # test whether myself.isEmtpy
    print(myself.isEmpty())
    while(True):
        if (myself.isEmpty() == True and socket_location == (0, 0)):
            destination = WordDetect.main(args)
            if destination in map:
                # destination_myself is the output of OCR text detection
                myself = makeQueue(destination)
                continue
            else:
                continue
        elif (READY == True):
            # between send command and receive ready, there should be no command to the car
            command(myself, socket_location, socket_other_location, destination)
            READY = False // should b syncronized...
            continue
        else:
            continue


if __name__ == '__main__':
    # import cho's socket and use it as an input
    # receive, send, main should be threaded
    car1 = AGV(SERVER_PORT_RECV_A)
    car2 = AGV(SERVER_PORT_RECV_B)

    while(True):
        conn1, addr1 = car1.server_socket.accept()
        conn2, addr2 = car2.server_socket.accept()

        temp_msg1 = conn1.recv(1024)
        datagram_format = struct.Struct("? i")
        recv_list1 = datagram_format.unpack(temp_msg1)
        conn.close()
        car1.status = int(recv_list1[0])
        car1.location = int(recv_list1[1])


        temp_msg2 = conn2.recv(1024)
        recv_list2 = datagram_format.unpack(temp_msg2)
        conn.close()
        car2.status = int(recv_list2[0])
        car2.location = int(recv_list2[1])

        # for different host ip make AGV using the socket
        main(car1.location, car2.location, car1.status)
        main(car2.location, car1.location, car2.status)
