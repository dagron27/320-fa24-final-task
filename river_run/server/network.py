import paramiko
import os
import socket
import threading
from dotenv import load_dotenv
from shared.network_utils import serialize_message, deserialize_message

load_dotenv()

class ServerGameLogic:
    def __init__(self):
        pass

    def process_message(self, message):
        response = {"status": "processed", "message": message}
        return response

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.game_logic = ServerGameLogic()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def handle_client(self, channel):
        try:
            while True:
                data = channel.recv(1024)
                if not data:
                    break
                message = deserialize_message(data.decode('utf-8'))
                print(f"Received message: {message}")
                response = self.game_logic.process_message(message)
                print(f"Sending response: {response}")
                channel.send(serialize_message(response).encode('utf-8'))
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            channel.close()

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
