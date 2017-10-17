import sys
import socket
import hashlib
import random
import select
import time
import pickle
from struct import pack, unpack

def check_port_num(i):
    i = int(i)
    if i not in range(1024, 64000):
        print('Out of range. exit the program', i)
        exit()
    if not isinstance(i, int):
        print('Not integer, exit the program. ', i)
        exit()

def main():
    #commond_line_input = sys.argv[1:] # read input
    commond_line_input = [7781,7783,7777,'test.txt'] #**Test code**
    ip_address = '127.0.0.1'
    next_value = 0
    ACKNOWLEDGEMENT_PACKET = 1
    DATA_PACKET = 0
    packet_magicno = 0x497E
    packet_count = 0
    exitFlag = False

    """check if input vaild or not"""
    for i in commond_line_input[:3]:
        check_port_num(i)

    """Assign port number from input list"""
    try:
        S_in_num = int(commond_line_input[0])
        S_out_num = int(commond_line_input[1])
        C_s_in_num = int(commond_line_input[2])
        filename = str(commond_line_input[3])
        print('Passing assign port number...')
    except:
        print('Error when assign number from input, exit the program')
        exit()

    """Generating socket"""
    try:
        S_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        S_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Passing generate socket...')
    except:
        print('Error when generate socket, exit the program')
        exit()

    """bind with port number"""
    try:
        S_in.bind((ip_address, S_in_num))
        S_out.bind((ip_address, S_out_num))
        print('Passing bind port number...')
    except:
        print('Error when bind port number, exit the program')
        S_in.close()
        S_out.close()
        exit()

    """Connect and listen"""
    try:
        S_out.connect((ip_address, C_s_in_num))
        S_in.listen(5)
        S_in_packet, S_in_addr = S_in.accept()

    except:
        print('Error when connect/listen/accept, exit the program')
        S_in.close()
        S_out.close()
        exit()

    """Check file exist"""
    try:
        infile = open(filename, 'r')
        print('File opened')
    except:
        print('Error when open the file, exit the program')
        S_in.close()
        S_out.close()
        exit()

    print('Passing all check, sender now is online!')
    print('')
    while exitFlag == False:
        
        print('Reading data from file...')
        
        data = infile.read(512)
        data_len = len(data)
        #str_hash = hashlib.md5(data_len.to_bytes(4, 'big')).hexdigest() # 32 str

        # file is empty
        if data_len == 0 or data == '':
            exitFlag = True

        while True:
            packet_buffer = pack("!Liii"+str(data_len)+"s", packet_magicno, DATA_PACKET, next_value, data_len, data)
            print(next_value)
            S_out.send(packet_buffer)
            print('One packet is sending to channel...')
            packet_count += 1
            
            # 1s time out
            ready = select.select([S_in_packet], [], [], 1)
            if ready[0]:
                packet_s_in = S_in_packet.recv(512)
                packet_header = unpack("!Liii", packet_s_in[:16])
                new_magicno, new_datatype, new_sequno, new_datalen = packet_header
                '''
                if hashlib.md5(data_len.to_bytes(4, 'big')).hexdigest() != str_hash:
                    print('There is a bit error, drop the packet.')
                '''
                if new_magicno != 0x497E or new_datatype != ACKNOWLEDGEMENT_PACKET or new_datalen != 0 or new_sequno != next_value:
                    print('Packet is not excepted, dropping')
                else:
                    next_value = 1 - next_value
                    if exitFlag == True:
                        print('Transfer complete, There are {0} packets are sended, exit the program'.format( packet_count))
                        infile.close()
                        S_in.close()
                        S_out.close()
                        exit()
                    else:
                        break


main()