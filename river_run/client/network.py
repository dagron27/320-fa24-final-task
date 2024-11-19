import socket
import json

class NetworkClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.connect_to_server()

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def send_command(self, command):
        self.client_socket.send(json.dumps(command).encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        return json.loads(response)
