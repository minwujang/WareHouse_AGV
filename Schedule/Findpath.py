from TextDetection import WordDetect
import argparse

map = {'Start': 0, 'Start-1': 11, 'Start-2': 12, 'Start-3': 13, 'Start-4': 14, 'Yongsan': 20, 'Yangcheon': 21, 'Songpa': 22, 'Seongbuk': 23, 'Dongjak': 24, 'Seocho': 30, 'Seodaemun': 31, 'Mapo': 32, 'Jonno': 33, 'Guro': 34, 'Gwangjin': 40, 'Nowon': 41, 'Gwanak': 42, 'Gangnam': 43, 'Gangbuk': 44}
READY = 1
FORWARD = 2
ROTATE = 3
WAIT = 4
ROTATE_FORWARD = 5
ROTATE_FORWARD_PUTDOWN = 6

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
    def __init__(self):
        self.location = None
        self.status = None
        # status implies Ready or notReady(on action or positioning)

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
                return ROTATE_FORWARD
            elif (coordinate_myself == (i, j)):
                return ROTATE_FORWARD_PUTDOWN
            else:
                myself.dequeue()
                return FORWARD
        else:
            return WAIT

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
                break
            else:
                continue
        elif (READY == True):
            # between send command and receive ready, there should be no command to the car
            command(myself, socket_location, socket_other_location, destination)
            READY = False
            continue
        else:
            continue


if __name__ == '__main__':
    # import cho's socket and use it as an input
    # receive, send, main should be threaded
    car1, car2 = AGV()
    # for different host ip make AGV using the socket
    main(car1.location, car2.location, car1.status)
    main(car2.location, car1.location, car2.status)