def client_checksum(packet,checksum):
	packet_len = len(packet)
	packet=packet.decode("utf-8")
	for i in range(0, packet_len, 2):
		if i + 1 == packet_len:
			merged_bytes = (ord(str(packet[i])) << 8) + 0xffff
		else:
			merged_bytes = (ord(str(packet[i])) << 8) + ord(str(packet[i + 1]))
		csum = checksum + merged_bytes
		checksum = (csum >> 16) + (csum & 0xffff)
	return checksum ^ 0xffff


def server_checksum(packet,checksum):
	packet_len=len(packet)
	for i in range(0, packet_len, 2):
		if i + 1 == packet_len:
			merged_bytes = (packet[i] << 8) + 0xffff
		else:
			merged_bytes = (packet[i] << 8) + packet[i+1]
		csum = checksum + merged_bytes
		checksum = (csum >> 16) + (csum & 0xffff)
	return checksum^0xffff