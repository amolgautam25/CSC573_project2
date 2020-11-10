#!/usr/bin/python3

import socket
import sys
import collections
import pickle
import signal
import threading
from multiprocessing import Lock
import time
import checksum

#global N, port, host, MSS, c_buffer ,max_val, c_socket

max_val = 0
final_ack = -1
final_packet = -1

c_buffer = collections.OrderedDict()
t_lock = Lock()
window = set()

c_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
flag = False

timer_start = 0

host = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]
N = int(sys.argv[4])
MSS = int(sys.argv[5])

def handler(timeout_th, frame):
    global final_ack
    win_len = len(window)
    if final_packet - win_len == final_ack:
        val = final_ack + 1
        print("Timeout, sequence number =", str(val))
        t_lock.acquire()
        while val < final_ack + win_len + 1:
            signal.alarm(0)
            signal.setitimer(signal.ITIMER_REAL, 0.1)
            c_socket.sendto(c_buffer[val], (host, port))
            val += 1
        t_lock.release()


def ack_handler():
    global window, c_socket, port, host, flag, final_ack, final_packet, c_buffer, timer_start
    ack = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack.bind(('0.0.0.0', 65021))

    while True:
        reply = pickle.loads(ack.recv(65535))
        if reply[2] == "1010101010101010":
            temp = reply[0]
            if final_ack >= -1:
                t_lock.acquire()
            if temp - 1 == max_val:
                c_socket.sendto(pickle.dumps(["0", "0", "1111111100000001", "0"]), (host, port))
                t_lock.release()
                flag = True
                print("\n TOTAL TIME:", ((time.time()) - timer_start))
                break
            elif temp - 1 > final_ack:
                while final_ack < temp - 1:
                    signal.alarm(0)
                    signal.setitimer(signal.ITIMER_REAL, 0.1)
                    final_ack += 1
                    c_buffer.pop(final_ack)
                    window.remove(final_ack)
                    while min(len(c_buffer), N) > len(window) and final_packet < max_val:
                        val = final_packet + 1
                        c_socket.sendto(c_buffer[val], (host, port))
                        window.add(final_packet + 1)
                        final_packet += 1
            else:
                pass
            t_lock.release()
    ack.close()

def rdt_send(c_socket):
    global window, c_buffer, final_packet, final_ack, timer_start
    timer_start = time.time()
    while min(len(c_buffer), N) > len(window) and final_ack == -1:
        val = final_packet + 1
        c_socket.sendto(c_buffer[val], (host, port))
        signal.alarm(0)
        signal.setitimer(signal.ITIMER_REAL, 0.1)
        final_packet += 1
        window.add(final_packet)


count = 0
try:
    with open(filename, 'rb') as f:
        while True:
            data = f.read(int(MSS)).decode("utf-8-sig").encode("utf-8")
            if not data:
                break
            max_val = count
            c_buffer[count] = pickle.dumps([count, checksum.client_server_checksum(data, 0), "0101010101010101", data])
            count += 1
except:
    sys.exit("File I/O Exception")

signal.signal(signal.SIGALRM, handler)
ackPacket = threading.Thread(target=ack_handler)
ackPacket.start()
rdt_send(c_socket)
while not flag:
    pass
ackPacket.join()
c_socket.close()
