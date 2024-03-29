#!/usr/bin/env python3

import sys
import socket
import os
import checksum
import random
import pickle

server_port = int(sys.argv[1])
file_name = sys.argv[2]
loss_prob = float(sys.argv[3])

s_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_socket.bind(('0.0.0.0', server_port))
last_received_packet = -1

if os.path.isfile(file_name):
    os.remove(file_name)


def send_ack(ack_number):
    ack_packet = pickle.dumps([ack_number, "0000000000000000", "1010101010101010"])
    ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_socket.sendto(ack_packet, (ACK_HOST_NAME, 65012))
    ack_socket.close()


while 1:
    received_data1, addr = s_socket.recvfrom(65535)
    ACK_HOST_NAME = addr[0]
    data = pickle.loads(received_data1)
    if data[2] == "1111111111111111":
        s_socket.close()
        break
    elif data[2] == "0101010101010101":
        if random.random() < loss_prob:
            print("Packet loss, sequence number = " + str(data[0]))
        else:
            if checksum.server_checksum(data[3], data[1]) == 0:
                if data[0] == last_received_packet + 1:
                    send_ack(data[0] + 1)
                    last_received_packet += 1
                    with open(file_name, 'ab') as file:
                        file.write(data[3])
                else:
                    send_ack(last_received_packet + 1)
            else:
                print("Packet " + str(data[0]) + " has been dropped due to improper checksum")
