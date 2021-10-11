import socket
import os
import sys

"""***********************************Description of the Function - extract_file_data:
    Gaol: Extract information about the file, the data itself, the length of the file
    and whether the file has been read in binary form.
    Parameters: name - files/ + name of file.
    return: is_binary, file_len, file_data.
***********************************************************************************"""
def extract_file_data(name):

    file_data = 'not_exists'
    file_len = 0
    is_binary = False
    if not os.path.exists(name) or name == 'files/':
        return is_binary, file_len, file_data
    # Depending on the file type we will read it in binary or normal form.
    if name.endswith('.jpg') or name.endswith('.ico'):
        with open(name, 'rb') as my_file:
            file_data = my_file.read()
            is_binary = True
    else:
        with open(name, 'r') as my_file:
            file_data = my_file.read()
    # Get size of file.
    file_len = os.path.getsize(name)

    return is_binary, file_len, file_data

"""*****************************************Description of the Function - extract_info:
    Gaol: The function receives a complete message and extracts relevant information
    from the message. The file name and the requested connection status.
    Parameters: message - complete message.
    return: f_name, connection_status.
***********************************************************************************"""
def extract_info(message):

    f_name = message.split()[1]
    lines_list = message.split('\r\n')
    connection_status = ''
    for line in lines_list:
        line = line.split(' ')
        if line[0] == 'Connection:':
            connection_status = line[1]
            break

    return f_name, connection_status

"""*******************************************Description of the Function - check_send:
    Gaol: The function receives a complete message and operates according to the
    content of the message and the instructions of the exercise. After the function 
    analyzes the information it sends the appropriate message to the client.
    Parameters: client_message - complete message from the client.
    return: 'close_connection' || 'continue_connection' - By this values we will be
    able to distinguish whether to leave the connection open or close it.
***********************************************************************************"""
def check_send(client_message):

    try:
        # Extract the file name & its relevant data.
        file_name, connection_stat = extract_info(client_message)
        # Check if he wants redirect or to present file/png ect.
        if file_name == '/redirect':
            message = 'HTTP/1.1 301 Moved Permanently\r\nConnection: close\r\nLocation: /result.html\r\n\r\n'
            client_socket.send(message.encode())
            return 'close_connection'
        else:
            if file_name == '/':
                file_name = 'index.html'
            flg_binary, f_len, f_data = extract_file_data('files/' + file_name)
            if f_data == 'not_exists':
                # If the file was not found.
                message = 'HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n'
                client_socket.send(message.encode())
                return 'close_connection'
            else:
                # Send the data to the client.
                message = 'HTTP/1.1 200 OK\r\n' + 'Connection: ' + str(
                    connection_stat) + '\r\n' + 'Content-Length: ' + str(f_len) + '\r\n\r\n'
                data = f_data if flg_binary else f_data.encode()
                client_socket.send(message.encode())
                client_socket.send(data)
                if connection_stat == 'close':
                    return 'close_connection'
    except:
        return 'close_connection'

    return 'continue_connection'


##########################################  Main  ##########################################

# Create socket in port from command line.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', int(sys.argv[1])))
server.listen(1)

# Start listen to clients.
while True:

    client_socket, client_address = server.accept()

    while True:
        # Set time out for the client to send message
        client_socket.settimeout(1)
        # Try to receive the message in time, if he do not send close his socket and
        # start listening to other clients.
        try:
            # Check if the client send emtpy message.
            data = client_socket.recv(1024)
            if not data:
                break
        except:
            break
        # Split the data into separate messages
        messages = data.decode().split('\r\n\r\n')
        print(data.decode())
        flg = False
        # We will now analyze and respond to the client messages message after message.
        for i in messages:
            if len(i) > 1 and i.split()[0] == 'GET':
                if check_send(i) == 'close_connection':
                    flg = True
                    break
        if flg:
            break

    client_socket.close()
