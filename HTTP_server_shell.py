# HTTP Server Shell
# Author: Barak Gonen
# Purpose: Provide a basis for Ex. 4.4
# Note: The code is written in a simple way, without classes, log files or other utilities, for educational purpose
# Usage: Fill the missing functions and constants

import socket
import os.path

IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 0.1
DEFAULT_URL = '/index.html'
DEFAULT_DIR = 'C:/tomer/webroot'
REDIRECTION_DICTIONARY = dic = {"/cat": '/imgs/abstract.jpg'}
status_ok = "HTTP/1.1 200 OK \r\n"
list_For = ['/sod.txt']
c = "Content-Length: "
rn = " \r\n\r\n"


def get_file_data(filename):
    """ Get data from file """
    with open(filename, "rb") as data2:
        data1 = data2.read()
        return str(len(data1)), data1


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    if resource == '/' and not ('favicon' in resource):
        url = DEFAULT_URL
    else:
        url = resource
    full_path = str(DEFAULT_DIR + url)
    http_header = ""
    if os.path.isfile(full_path):
        if url in list_For:
            client_socket.send("403 Forbidden")
        else:
            data_len, data = get_file_data(full_path)
            dataa = full_path.split(".")
            len_d = len(dataa)
            file_type = dataa[len_d - 1]
            if file_type == 'html':
                http_header = status_ok + "Content-Type: text/html; charset=UTF-8 \r\n" + c + data_len + rn
            elif file_type == 'jpg':
                http_header = status_ok + "Content-Type: image/jpeg \r\n" + c + data_len + rn
            elif file_type == 'js':
                http_header = status_ok + "Content-Type: text/javascript; charset=UTF-8 \r\n" + c + data_len + rn
            elif file_type == 'ico':
                http_header = status_ok + "Content-Type: image/vnd.microsoft.icon \r\n" + c + data_len + rn
            elif file_type == 'css':
                http_header = status_ok + "Content-Type: text/css \r\n" + c + data_len + rn
            http_response = http_header + str(data)
            client_socket.send(http_response)

    elif url in dic:
        http_header = client_socket.send("HTTP/1.1 302 Found\r\nContent-Type: text/html; charset=utf-8 \r\nLocation: " +
                                         dic[url] + "\r\n\r\n")
        data = ""
        http_response = str(http_header) + str(data)
        client_socket.send(http_response)
    elif "/calculate-next" in url:
        url = resource
        d1_split = url.split("=")
        d1 = int(d1_split[-1]) + 1
        data_len = str(len(str(d1)))
        http_header = status_ok + "Content-Type: text/html; charset=UTF-8 \r\n" + c + data_len + rn
        http_response = http_header + str(d1)
        client_socket.send(http_response)
    elif "/calculate-area" in url:
        url = resource
        d1_split = url.split("=")
        h = int(d1_split[-2][0])
        w = int(d1_split[-1])
        s = (w * h) / 2.0
        data_len = str(len(str(s)))
        http_header = status_ok + "Content-Type: text/html; charset=UTF-8 \r\n" + c + data_len + rn
        http_response = http_header + str(s)
        client_socket.send(http_response)
    else:
        client_socket.send("HTTP/1.0 404 Not Found \r\n\r\n")
        client_socket.send('404 Not Found')


def handle_client_request_p(resource, client_socket, client_request):
    full_path = str(DEFAULT_DIR + "/" + resource)
    print full_path
    list_split = client_request.split("\r\n")
    for i in list_split:
        if "Content-Length" in i:
            d1 = i.split()
            content_length = d1[-1]
    data = ''
    for i in xrange(int(content_length) / 1024):
        data += client_socket.recv(1024)
    if int(content_length) - len(data) != 0:
        data += client_socket.recv(int(content_length) - len(data))
    with open(full_path, "wb") as file_from_client:
        file_from_client.write(data)
    message = 'good'
    length_message = str(len(message))
    http_response = status_ok + "Content-Length: " + length_message, " \r\n\r\n" + message
    http_response = http_response[0] + http_response[1]
    client_socket.send(http_response)


def validate_http_request(request):
    """ Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL """
    list1 = request.split()
    if len(list1) >= 3:
        if list1[0] == "GET" and "/" in list1[1] and list1[2] == "HTTP/1.1":
            return 0, list1[1]
        elif list1[0] == "POST" and "/" in list1[1] and list1[2] == "HTTP/1.1":
            list2 = list1[1].split("=")
            return 1, list2[-1]
    else:
        return 2, ""


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print 'Client connected'
    while True:
        try:
            client_request = client_socket.recv(1024)
        except socket.timeout:
            break
        valid_http, resource = validate_http_request(client_request)
        if valid_http == 0:
            print 'Got a valid HTTP request'
            handle_client_request(resource, client_socket)
        elif valid_http == 1:
            print 'Got a valid HTTP request Post'
            handle_client_request_p(resource, client_socket, client_request)
        else:
            print 'Error: Not a valid HTTP request'
            break
    print 'Closing connection'
    client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(10)
    print "Listening for connections on port %d" % PORT

    while True:
        client_socket, client_address = server_socket.accept()
        print 'New connection received'
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    main()
