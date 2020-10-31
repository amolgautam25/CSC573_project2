#!/usr/bin/env python3

import socket
import pickle
import random
import sys
import os
import checksum

server_port = int(sys.argv[1])
file_name = sys.argv[2]
loss_prob = float(sys.argv[3])
TYPE_EOF = "1111111111111111"

s_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
HOST_NAME = '0.0.0.0'
s_socket.bind((HOST_NAME, server_port))
last_received_packet = -1

if os.path.isfile(file_name):
    os.remove(file_name)


def send_ack(ack_number):
    ack_packet = pickle.dumps([ack_number, "0000000000000000", "1010101010101010"])
    ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("server ack: ",ACK_HOST_NAME)
    ack_socket.sendto(ack_packet, (ACK_HOST_NAME, 65009))
    ack_socket.close()


while 1:
    received_data1, addr = s_socket.recvfrom(65535)
    ACK_HOST_NAME = addr[0]
    received_data = pickle.loads(received_data1)
    packet_sequence_number, packet_checksum, packet_type, packet_data = received_data[0], received_data[1], \
                                                                        received_data[2], received_data[3]
    if packet_type == TYPE_EOF:
        s_socket.close()
        break
    elif packet_type == "0101010101010101":
        drop_packet = random.random() < loss_prob
        if drop_packet == True:
            print("Packet loss, sequence number = " + str(packet_sequence_number))
        else:
            if checksum.compute_checksum_server(packet_data, packet_checksum) == 0:
                if packet_sequence_number == last_received_packet + 1:
                    send_ack(packet_sequence_number + 1)
                    last_received_packet = last_received_packet + 1
                    with open(file_name, 'ab') as file:
                        file.write(packet_data)
                else:
                    send_ack(last_received_packet + 1)
            else:
                print ("Packet " + str(packet_sequence_number) + " has been dropped due to improper checksum")
