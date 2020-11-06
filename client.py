#!/usr/bin/env python3

import socket
import sys
import collections
import pickle
import signal
import threading
from multiprocessing import Lock
import time
import checksum

global client_buffer ,max_seq_number,client_socket,N,PORT,HOST,MSS
RTT = 0.1
max_seq_number = 0
final_ack = -1
final_packet = -1

client_buffer = collections.OrderedDict()
thread_lock = Lock()
sliding_window = set()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
flag = False

t_start = 0
t_end = 0

HOST = sys.argv[1]
PORT = int(sys.argv[2])
filename = sys.argv[3]
N = int(sys.argv[4])
MSS = int(sys.argv[5])

def timeout_thread(timeout_th, frame):
    global final_ack
    if final_ack == final_packet - len(sliding_window):
        print("Timeout, sequence number = " + str(final_ack + 1))
        thread_lock.acquire()
        temp = final_ack + 1
        while temp < final_ack+len(sliding_window)+1:
            signal.alarm(0)
            signal.setitimer(signal.ITIMER_REAL, RTT)
            client_socket.sendto(client_buffer[temp], (HOST, PORT))
            temp += 1
        thread_lock.release()


def ackConn():
    global final_ack, final_packet, client_buffer, sliding_window, client_socket, PORT, HOST, flag, t_end, t_start, t_total
    ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_socket.bind(('0.0.0.0', 65021))

    while 1:
        reply = pickle.loads(ack_socket.recv(65535))
        if reply[2] == "1010101010101010":
            current_ack_seq_number = reply[0] - 1
            if final_ack >= -1:
                thread_lock.acquire()
            if current_ack_seq_number == max_seq_number:
                eof_packet = pickle.dumps(["0", "0", "1111111100000000", "0"])
                client_socket.sendto(eof_packet, (HOST, PORT))
                thread_lock.release()
                flag = True
                t_end = time.time()
                t_total = t_end - t_start
                print("\n--------TOTAL TIME------:", t_total)
                break
            elif current_ack_seq_number > final_ack:
                while final_ack < current_ack_seq_number:
                    signal.alarm(0)
                    signal.setitimer(signal.ITIMER_REAL, RTT)
                    final_ack = final_ack + 1
                    sliding_window.remove(final_ack)
                    client_buffer.pop(final_ack)
                    while len(sliding_window) < min(len(client_buffer), N):
                        if final_packet < max_seq_number:
                            client_socket.sendto(client_buffer[final_packet + 1], (HOST, PORT))
                            sliding_window.add(final_packet + 1)
                            final_packet = final_packet + 1
                thread_lock.release()
            else:
                thread_lock.release()
    ack_socket.close()

def rdt_send(client_socket):
    global sliding_window, client_buffer, final_packet, final_ack, t_start
    t_start = time.time()
    while len(sliding_window) < min(len(client_buffer), N):
        if final_ack == -1:
            client_socket.sendto(client_buffer[final_packet + 1], (HOST, PORT))
            signal.alarm(0)
            signal.setitimer(signal.ITIMER_REAL, RTT)
            final_packet += 1
            sliding_window.add(final_packet)
            for i in range(0, 100000):
                i += 1

count = 0
try:
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(int(MSS)).decode("utf-8-sig").encode("utf-8")
            if not chunk:
                break
            max_seq_number = count
            client_buffer[count] = pickle.dumps([count, checksum.client_server_checksum(chunk, 0), "0101010101010101", chunk])
            count += 1
except:
    sys.exit("File I/O Exception")

signal.signal(signal.SIGALRM, timeout_thread)
ackPacket = threading.Thread(target=ackConn)
ackPacket.start()
rdt_send(client_socket)
while True:
    if flag:
        break
ackPacket.join()
client_socket.close()
