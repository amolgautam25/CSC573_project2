#!/usr/bin/env python3

import sys
import socket
import os
import checksum
import random
import pickle

server_port = int(sys.argv[1])
file_name = sys.argv[2]
if os.path.exists(file_name):
    os.remove(file_name)
loss_prob = float(sys.argv[3])

s_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_socket.bind(('0.0.0.0', server_port))
final_packet = -1

while 1:
    client_data, server_add = s_socket.recvfrom(65535)
    data = pickle.loads(client_data)
    if data[2] == "0101010101010101" and random.random() < loss_prob:
        print("Packet loss, sequence number =", str(data[0]))
    elif data[2] == "0101010101010101":
        if checksum.client_server_checksum(data[3], data[1]) == 0:
            a_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if data[0] == final_packet + 1:
                a_socket.sendto(pickle.dumps([data[0] + 1, "0000000000000000", "1010101010101010"]), (server_add[0], 65021))
                final_packet += 1
                with open(file_name, 'ab') as file:
                    file.write(data[3])
            else:
                a_socket.sendto(pickle.dumps([final_packet + 1, "0000000000000000", "1010101010101010"]),
                                (server_add[0], 65021))
            a_socket.close()
        else:
            print("Packet " + str(data[0]) + " dropped - checksum invalid")
    elif data[2] == "1111111100000001":
        s_socket.close()
        break
