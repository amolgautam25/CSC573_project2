def compute_checksum_client(chunk):
	checksum=0
	l=len(chunk)
	chunk=chunk.decode("utf-8")
	byte=0
	while byte<l:
		byte1=ord(str(chunk[byte]))
		shifted_byte1=byte1<<8
		if byte+1==l:
			byte2=0xffff
		else:
			byte2=ord(str(chunk[byte+1]))
		merged_bytes=shifted_byte1+byte2
		checksum_add=checksum+merged_bytes
		carryover=checksum_add>>16
		main_part=checksum_add&0xffff
		checksum=main_part+carryover
		byte=byte+2
	checksum_complement=checksum^0xffff
	print("client:" , checksum_complement)
	return checksum_complement


def compute_checksum_server(chunk,checksum):
	print("server:" ,checksum)
	l=len(chunk)
	byte=0
	while byte<l:
		byte1=chunk[byte]
		shifted_byte1=byte1<<8
		if byte+1==l:
			byte2=0xffff
		else:
			byte2=chunk[byte+1]
		merged_bytes=shifted_byte1+byte2
		checksum_add=checksum+merged_bytes
		carryover=checksum_add>>16
		main_part=checksum_add&0xffff
		checksum=main_part+carryover
		byte=byte+2
	checksum_complement=checksum^0xffff

	return checksum_complement