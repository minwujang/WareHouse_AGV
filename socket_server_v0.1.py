import socket
import struct
import threading
import socketserver

SERVER_IP_ADDRESS = "192.168.0.101"
SERVER_PORT_NUM = 56774
PI_IP_ADDRESS = "192.168.0.102"
PI_PORT_NUM = 43179

def server_generationg():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP_ADDRESS, SERVER_PORT_NUM))
    server_socket.listen()

    while True:
        # recv_msg = input('What is the value u want?')
        # recv_int = int(recv_msg)
        # data = [recv_int]
        # data_format = struct.Struct("i")
        # code_value = data_format.pack(*data)
        # server_socket.send(code_value)

        conn, addr = server_socket.accept()

        temp_msg = conn.recv(1024)
        datagram_format = struct.Struct("? i")
        recv_list = datagram_format.unpack(temp_msg)
        print("received msg: ", recv_list)
        conn.close()
        
    server_socket.close()


if __name__ == "__main__":
    server_communicate_thread = threading.Thread(target=server_generationg)
    server_communicate_thread.start()