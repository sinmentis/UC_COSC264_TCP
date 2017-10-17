import sys
import socket
import hashlib
from struct import pack, unpack
import random
import select

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
    commond_line_input = [7782, 7784, 7779, 'result.txt'] #**Test code**
    ip_address = '127.0.0.1'
    ACKNOWLEDGEMENT_PACKET = 1
    DATA_PACKET = 0
    expected = 0

    """check if input vaild or not"""
    for i in commond_line_input[:3]:
        check_port_num(i)

    """Assign port number from input list"""
    try:
        R_in_num = int(commond_line_input[0])
        R_out_num = int(commond_line_input[1])
        C_r_in_num = int(commond_line_input[2])
        filename = commond_line_input[3]
        print('Passing assign port number...')
    except:
        print('error when assign port number, exit the program')
        exit()

    """Generating socket"""
    try:
        R_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        R_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Passing generate socket...')
    except:
        print('error when generating socket, exit the program')
        exit()

    """bind ip with port number"""
    try:
        R_in.bind((ip_address, R_in_num))
        R_out.bind((ip_address, R_out_num))
        print('Passing bind port number...')
    except:
        print('error when connecting sockets, exit the program')
        R_in.close()
        R_out.close()
        exit()

    print('All set, waiting for first connection')

    """listen and accept and connect"""
    try:
        R_out.connect((ip_address, C_r_in_num))
        R_in.listen(5)
        R_in_packet, R_in_addr = R_in.accept()
    except:
        print('Connecting sockets fail, exit the program')
        R_in.close()
        R_out.close()
        exit()

    """open file"""
    try:
        infile = open(filename, 'w')
    except:
        print('Error when open file, exit the program')
        R_int.close()
        R_out.close()
        exit()
    
    # infinite loop
    while True:
        print('waiting for rest connection')

        read, write, excep = select.select([R_in_packet],[],[])
        if not (read or write or excep):
            print('Time out')
        packet_r = R_in_packet.recv(528) # read packet
        packet_head = unpack('!Liii', packet_r[:16])
        new_magicno, new_datatype, new_sequno, new_datalen = packet_head
        print(new_sequno)
        '''
        if hashlib.md5(data_len.to_bytes(4, 'big')).hexdigest() != str_hash:
            print('There is a bit error, drop the packet.')
        '''
        # check [packet_magicno] and [packet_type]
        if new_magicno != 0x497E or new_datatype != DATA_PACKET:
            print('Invaild packet, dropping')
        else:
            # If [new_sequno] equal to [expected]
            if new_sequno == expected:
                expected = 1 - expected
                new_packet = pack('!Liii', new_magicno, ACKNOWLEDGEMENT_PACKET, new_sequno, 0)
                R_out.send(new_packet)                
                data = unpack(str(new_datalen)+"s", packet_r[16:])
                text = data[0]
                print("Ready to write")
                # write data into file
                try:
                    infile.write(text)
                    print('Data saved')
                except:
                    print('Data saving fail')

                if new_datalen == 0:
                    print('End of File, exit the program')
                    infile.close()
                    R_in.close()
                    R_out.close()
                    exit()
            else:
                print("--ELSE-new_sequno{0}---expected{1}----".format(new_sequno, expected))

main()