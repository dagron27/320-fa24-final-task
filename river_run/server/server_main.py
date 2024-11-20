import paramiko
import threading
import socket
import json
from dotenv import load_dotenv
import os
from server_logic import ServerGameLogic

# Load environment variables from .env file
load_dotenv(dotenv_path='server/.env')

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

    def get_game_state(self, command):
        self.process_command(json.loads(command))
        return json.dumps(self.game_logic.get_game_state())

    def process_command(self, command):
        action = command.get("action")
        if action == "move_left":
            self.game_logic.player.move("left")
        elif action == "move_right":
            self.game_logic.player.move("right")
        elif action == "shoot":
            missile = self.game_logic.player.shoot()
            self.game_logic.missiles.append(missile)
        elif action == "reset_game":
            self.game_logic.reset_game()
        self.game_logic.update_game_state()

def handle_client(client_socket):
    server = SSHServer()
    transport = paramiko.Transport(client_socket)
    key_filename = os.getenv('SERVER_KEY_FILENAME')
    transport.add_server_key(paramiko.RSAKey(filename=key_filename))
    transport.start_server(server=server)
    chan = transport.accept(20)
    if chan is None:
        print("No channel")
        return

    while True:
        try:
            command = chan.recv(1024).decode('utf-8')
            if not command:
                break
            response = server.get_game_state(command)
            chan.send(response.encode('utf-8'))
        except Exception as e:
            print(f"Exception: {e}")
            break

    chan.close()

if __name__ == "__main__":
    host = os.getenv('SERVER_HOST')
    port = int(os.getenv('SERVER_PORT'))
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Client connected from {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()