import paramiko
import os
import socket
from network.ssh_server import SSHServer
from dotenv import load_dotenv


load_dotenv()

class ServerNetwork:
    def __init__(self):
        self.host = os.getenv("SERVER_HOST", "127.0.0.1")
        self.port = int(os.getenv("SERVER_PORT", 2200))
        self.key_filename = os.getenv("SERVER_KEY_FILENAME")
        self.server_key = None
        self.sock = None

    def start_service(self):
        try:
            print("Starting SSH server...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(100)
            print(f"Server listening on {self.host}:{self.port}")
            
            self.server_key = paramiko.RSAKey(filename=self.key_filename)
            while True:
                client, addr = self.sock.accept()
                print(f"Connection from {addr}")
                transport = paramiko.Transport(client)
                transport.add_server_key(self.server_key)
                ssh_server = SSHServer()
                transport.start_server(server=ssh_server)
                channel = transport.accept(20)
                
                if channel is None:
                    print("No channel opened by client")
                    continue

                print("Channel opened, starting communication")
                ssh_server.handle_client(channel)
        except Exception as e:
            print(f"Failed to start service: {e}")
            raise

    def close_service(self):
        if self.sock:
            self.sock.close()
            print("Server service closed")

if __name__ == "__main__":
    server = ServerNetwork()
    server.start_service()
