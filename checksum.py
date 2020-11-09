def client_server_checksum(packet,checksum):
	packet_len = len(packet)
	packet=packet.decode("utf-8")
	for i in range(0, packet_len, 2):
		if i + 1 == packet_len:
			temp = (ord(str(packet[i])) << 8) + 0xffff
		else:
			temp = (ord(str(packet[i])) << 8) + ord(str(packet[i + 1]))
		csum = checksum + temp
		checksum = (csum >> 16) + (csum & 0xffff)
	return checksum ^ 0xffff

