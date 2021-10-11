import sys
import socket

"""****************************************Description of the Function - start_client:
    Gaol: Start socket & send queries from user to the server in order to get the IP.
    Parameters: server_address - (server_ip server_port).
***********************************************************************************"""
def start_client(server_address):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    query = input()
    while not query == 'stop':
        s.sendto(query.encode(), server_address)
        data, addr = s.recvfrom(2048)
        # Print the first item from the str [IP,TTL] - IP.
        print(str(data, 'utf-8').split(',')[0])
        query = input()
    s.close()


# Main
if len(sys.argv) != 3:
    print('Two args expected')
else:
    server_ip, server_port = sys.argv[1:]
    start_client((server_ip, int(server_port)))
