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
last_ack_packet = -1
last_send_packet = -1
sliding_window = set()
client_buffer = collections.OrderedDict()
thread_lock = Lock()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sending_completed = False

t_start = 0
t_end = 0

HOST = sys.argv[1]
PORT = int(sys.argv[2])
filename = sys.argv[3]
N = int(sys.argv[4])
MSS = int(sys.argv[5])

def timeout_thread(timeout_th, frame):
    global last_ack_packet
    if last_ack_packet == last_send_packet - len(sliding_window):
        print("Timeout, sequence number = " + str(last_ack_packet + 1))
        thread_lock.acquire()
        for i in range(last_ack_packet + 1, last_ack_packet + 1 + len(sliding_window), 1):
            signal.alarm(0)
            signal.setitimer(signal.ITIMER_REAL, RTT)
            client_socket.sendto(client_buffer[i], (HOST, PORT))
        thread_lock.release()


def ack_process():
    global last_ack_packet, last_send_packet, client_buffer, sliding_window, client_socket, PORT, HOST, sending_completed, t_end, t_start, t_total
    ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_socket.bind(('0.0.0.0', 65021))

    while 1:
        reply = pickle.loads(ack_socket.recv(65535))
        if reply[2] == "1010101010101010":
            current_ack_seq_number = reply[0] - 1
            if last_ack_packet >= -1:
                thread_lock.acquire()
            if current_ack_seq_number == max_seq_number:
                eof_packet = pickle.dumps(["0", "0", "1111111111111111", "0"])
                client_socket.sendto(eof_packet, (HOST, PORT))
                thread_lock.release()
                sending_completed = True
                t_end = time.time()
                t_total = t_end - t_start
                break
            elif current_ack_seq_number > last_ack_packet:
                while last_ack_packet < current_ack_seq_number:
                    signal.alarm(0)
                    signal.setitimer(signal.ITIMER_REAL, RTT)
                    last_ack_packet = last_ack_packet + 1
                    sliding_window.remove(last_ack_packet)
                    client_buffer.pop(last_ack_packet)
                    while len(sliding_window) < min(len(client_buffer), N):
                        if last_send_packet < max_seq_number:
                            client_socket.sendto(client_buffer[last_send_packet + 1], (HOST, PORT))
                            sliding_window.add(last_send_packet + 1)
                            last_send_packet = last_send_packet + 1
                thread_lock.release()
            else:
                thread_lock.release()
    ack_socket.close()

def rdt_send(client_socket):
    global last_send_packet, last_ack_packet, sliding_window, client_buffer, t_start
    t_start = time.time()
    while len(sliding_window) < min(len(client_buffer), N):
        if last_ack_packet == -1:
            client_socket.sendto(client_buffer[last_send_packet + 1], (HOST, PORT))
            signal.alarm(0)
            signal.setitimer(signal.ITIMER_REAL, RTT)
            last_send_packet = last_send_packet + 1
            sliding_window.add(last_send_packet)
            y = 0
            while y < 100000:
                y = y + 1

sequence_number = 0
try:
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(int(MSS)).decode("utf-8-sig").encode("utf-8")
            if chunk:
                max_seq_number = sequence_number
                chunk_checksum = checksum.client_checksum(chunk, 0)
                #print("-------",chunk_checksum)
                client_buffer[sequence_number] = pickle.dumps([sequence_number, chunk_checksum, "0101010101010101", chunk])
                sequence_number = sequence_number + 1
            else:
                break
except:
    sys.exit("Failed to open file!")

signal.signal(signal.SIGALRM, timeout_thread)
ack_thread = threading.Thread(target=ack_process)
ack_thread.start()
rdt_send(client_socket)
while 1:
    if sending_completed:
        break
ack_thread.join()
client_socket.close()
