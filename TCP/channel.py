import sys
from struct import pack, unpack
import socket
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
    commond_line_input = [7777,7778,7779,7780,7781,7782,0.2] #**Test code**
    ip_address = '127.0.0.1'
    
    """check if input vaild or not"""
    for i in commond_line_input[:6]:
        check_port_num(i)

    loss_rate = float(commond_line_input[6])
    if loss_rate < 0 or loss_rate > 1:
        print('packet loss rate not vaild, exit the program', loss_rate)
        exit()

    """Assign port number from input list"""
    try:
        C_s_in_num = int(commond_line_input[0])
        C_s_out_num = int(commond_line_input[1])
        C_r_in_num = int(commond_line_input[2])
        C_r_out_num = int(commond_line_input[3])
        S_in_num = int(commond_line_input[4])
        R_in_num = int(commond_line_input[5])
        print('Passing assign number to port')
    except:
        print('error when assign port number, exit the program')
        exit()

    """Generating socket"""
    try:
        C_s_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        C_s_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        C_r_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        C_r_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Passing generating socket')
    except:
        print('error when generating socket, exit the program')
        exit()

    """bind ip with port number"""
    try:
        C_s_in.bind((ip_address, C_s_in_num))
        C_s_out.bind((ip_address, C_s_out_num))
        C_r_in.bind((ip_address, C_r_in_num))
        C_r_out.bind((ip_address, C_r_out_num))
        print('Passing bind socket with port number, just wait a sec or change the port number')
    except:
        print('error when bind port number, exit the program')
        C_s_in.close()
        C_s_out.close()
        C_r_in.close()
        C_r_out.close()
        exit()

    print('Passing all check, channel is now online, waitting for sender and receiver')

    """Listen and accept"""
    try:
        C_s_in.listen(5)
        C_s_packet, C_s_addr = C_s_in.accept()
        C_s_out.connect((ip_address, S_in_num))
        C_r_in.listen(5)
        C_r_packet, C_r_addr = C_r_in.accept()
        C_r_out.connect((ip_address, R_in_num))
        print('sender and receiver is noe online, ready to go!')
        print('')
    except:
        print('Error when accept and listen')
        C_s_in.close()
        C_s_out.close()
        C_r_in.close()
        C_r_out.close()
        exit()

    # infinite loop
    while True:
        print('Waiting for connection ......')
        socket_list, output, excep = select.select([C_s_packet, C_r_packet],[],[])
        for socket_channel in socket_list:
            # if socket is from C_s_in
            if socket_channel == C_s_packet:
                print('Getting packets from sender')
                packet_cs = socket_channel.recv(528)

                if len(packet_cs) < 16:
                    print('Transfer complete!, exit the program')
                    C_s_in.close()
                    C_s_out.close()
                    C_r_in.close()
                    C_r_out.close()
                    exit()

                data_head = unpack('!Liii', packet_cs[:16])
                new_magicno, new_datatype, new_sequno, new_datalen = data_head

                # check header
                if new_magicno != 0x497E:
                    print("header fail, Lossing packet")
                    break
                
                # check loss
                loss_u = random.uniform(0, 1)
                #print("The random loss rate is {0.:2f}%".format(float(loss_u)*100))
                if loss_u < loss_rate:
                    print("Oppps, packet lost")

                # If not loss
                else:
                    '''
                    # check bit error
                    bit_u = random.uniform(0, 1)
                    if bit_u < 0.1:
                        new_datalen += random.randint(1,10)
                        print('bit error, add packet into: ', new_datalen)
                    
                    data_full = data_head + unpack(str(new_datalen)+"s", packet_cs[16:])
                    new_packet = pack("!Liii" + str(new_datalen) + "s", new_magicno, new_datatype, new_sequno, new_datalen, data_full[4])
                    '''
                    # forwarding the packet
                    try:
                        #C_r_out.send(new_packet)
                        C_r_out.send(packet_cs)
                        print('Sending to C_r_out success')
                    except:
                        print('Sending fail')
                        C_s_in.close()
                        C_s_out.close()
                        C_r_in.close()
                        C_r_out.close()
                        exit()
            elif socket_channel == C_r_packet:
                print('Getting confirm packets from receiver')
                packet_cr = socket_channel.recv(528)
                data_head = unpack('!Liii', packet_cs[:16])
                new_magicno, new_datatype, new_sequno, new_datalen = data_head
                
                # check header
                if new_magicno != 0x497E:
                    print("header fail, Lossing packet")
                    break
                '''
                # check loss
                loss_u = random.uniform(0, 1)
                #print("The random loss rate is {0:.2f}%".format(float(loss_u)*100))
                if loss_u < loss_rate:
                    print("Oppps, packet lost")
                else:
                '''
                try:
                    C_s_out.send(packet_cr)
                    print('Sending to sender')
                except:
                    print('Sending packet fail')
                    C_s_in.close()
                    C_s_out.close()
                    C_r_in.close()
                    C_r_out.close()
                    exit()

main()
