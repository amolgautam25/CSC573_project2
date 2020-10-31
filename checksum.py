def compute_checksum_client(chunk):
	checksum=0
	l=len(chunk)
	chunk=str(chunk)
	byte=0
	while byte<l:
		#Take 2 bytes of from the chunk data...takes 0xffff if the byte2 is not there because of odd chunk size
		byte1=chunk[byte]
		shifted_byte1=byte1<<8
		if byte+1==l:
			byte2=0xffff
		else:
			byte2=chunk[byte+1]
		#Merge the bytes in the form of byte1byte2 to make 16bits
		merged_bytes=shifted_byte1+byte2
		#Add to the 16 bit chekcsum computed till now
		checksum_add=checksum+merged_bytes
		#Compute the carryover
		carryover=checksum_add>>16
		#Compute the main part of the new checksum
		main_part=checksum_add&0xffff
		#Add the carryover to the main checksum again
		checksum=main_part+carryover
		#Do same for next 2 bytes
		byte=byte+2
	#Take 1's complement of the computed checksum and return it
	checksum_complement=checksum^0xffff
	return checksum_complement


def compute_checksum_server(chunk,checksum):
	l=len(chunk)
	byte=0
	#Take 2 bytes of from the chunk data...takes 0xffff if the byte2 is not there because of odd chunk size
	while byte<l:
		byte1=chunk[byte]
		shifted_byte1=byte1<<8
		if byte+1==l:
			byte2=0xffff
		else:
			byte2=chunk[byte+1]
		#Merge the bytes in the form of byte1byte2 to make 16bits
		merged_bytes=shifted_byte1+byte2
		#Add to the 16 bit chekcsum computed till now
		checksum_add=checksum+merged_bytes
		#Compute the carryover
		carryover=checksum_add>>16
		#Compute the main part of the new checksum
		main_part=checksum_add&0xffff
		#Add the carryover to the main checksum again
		checksum=main_part+carryover
		#Do same for next 2 bytes
		byte=byte+2
	#Take 1's complement of the computed checksum and return it
	checksum_complement=checksum^0xffff
	return checksum_complement