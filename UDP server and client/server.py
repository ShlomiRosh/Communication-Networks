import sys
import datetime
import socket

"""******************************************Description of the Function - update_file:
    Gaol: Update file line by line..
    Parameters: f_name, web_name, arr_data - IP,TTL,timestamp.
***********************************************************************************"""
def update_file(f_name):

    file = open(f_name, 'w')
    for web_key, data in ADDRESS_DICT.items():
        file.write(web_key + ',' + data[0] + ',' + data[1] + ',' + str(data[2]) + '\n')
    file.close()

"""******************************************Description of the Function - update_data:
    Gaol: Update the new line of data into the dict & file.
    Parameters: f_name, web_name, arr_data - IP,TTL,timestamp.
***********************************************************************************"""
def update_data(f_name, web_name, arr_data):

    ADDRESS_DICT.setdefault(web_name.strip().lower(), [arr_data[0], arr_data[1],
                                                datetime.datetime.now().timestamp()])
    update_file(f_name)

"""************************************Description of the Function - check_line_by_ttl:
    Gaol: To check If we have the web in the dict & its not permanent [that mean we
        need to check the TTL time for it] & TTl time expired [I check it by
        timestamp + TTL - current time].
    Parameters: web_name, f_name.
    Returns: line_arr from the dict - IP,TTL,timestamp.
***********************************************************************************"""
def check_line_by_ttl(web_name, f_name):

    if ADDRESS_DICT.get(web_name) and ADDRESS_DICT.get(web_name)[2] != 'permanent' and\
            float(ADDRESS_DICT.get(web_name)[2]) + float(ADDRESS_DICT.get(web_name)[1])\
            - datetime.datetime.now().timestamp() <= 0:
        # Delete the line from the data & from the file.
        del ADDRESS_DICT[web_name]
        update_file(f_name)

    return ADDRESS_DICT.get(web_name)

"""************************************Description of the Function - get_relevant_data:
    Gaol: Get an answer to the client queries if the information is in dict 
        then get the info from it else send the queries to the parent server.
    Parameters: s - socket, web_name, parent_address - (IP,port), f_name.
    Returns: line_arr from the dict - IP,TTL,timestamp.
***********************************************************************************"""
def get_relevant_data(s, web_name, parent_address, f_name):

    # Check if a specific line exist & if legal by TTL
    line_arr = check_line_by_ttl(web_name, f_name)
    if not line_arr:
        # If we dedent found the line in the dict ask the data from the parent
        s.sendto(web_name.encode(), parent_address)
        line, addr = s.recvfrom(2048)
        line_arr = str(line, 'utf-8').split(',')
        # Save the new line to the file & dict for future requests.
        update_data(f_name, web_name, line_arr)

    # if we hear we have the ens from the parent server in our dict.
    return ADDRESS_DICT.get(web_name)

"""*****************************************Description of the Function - start_server:
    Gaol: Set up a server to receive queries and return answers.
    Parameters: port - this port, parent_address - (IP,port), f_name.
***********************************************************************************"""
def start_server(port, parent_address, f_name):

    # Create a socket and start listening.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    while True:
        # Get web name from the client.
        data, addr = s.recvfrom(2048)
        web_name = str(data, 'utf-8').lower()
        # Get the relevant arr.
        line_arr = get_relevant_data(s, web_name, parent_address, f_name)
        # Connect arr to str type of data & send it "ip,ttl" to the client.
        line_str = str(line_arr[0]) + ',' + str(line_arr[1])
        s.sendto(line_str.encode(), addr)

"""*******************************************Description of the Function - init_dict:
    Gaol: Initializing a dictionary when the key is the site name and value
          is a list of TTL IP address and timestamp.
    Parameters: file name.
***********************************************************************************"""
def init_dict(f_name):

    file = open(f_name, 'r')
    lines = tuple(file)
    file.close()
    # Add to the dict the content of the file, key = web name.
    for line in lines:
        data = line.strip().split(',')
        if len(data) >= 3:
            # If its the first time we open the file timestamp will be permanent else
            # we take what we have in the file from the first time that its open.
            ADDRESS_DICT.setdefault(data[0].strip().lower(), [data[1].strip()
                , data[2].strip(), 'permanent' if len(data) < 4 else data[3].strip()])

# Main
if len(sys.argv) != 5:
    print('Four parameters expected')
else:
    # Get args param.
    ADDRESS_DICT = dict()
    this_port, parent_ip, parent_port, file_name = sys.argv[1:]
    init_dict(file_name)
    start_server(int(this_port), (parent_ip, int(parent_port)), file_name)
