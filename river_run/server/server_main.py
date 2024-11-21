import paramiko
import threading
import socket
import json
from dotenv import load_dotenv
import os
from server_logic import ServerGameLogic
import logging

# Load environment variables from .env file
load_dotenv()

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
    print(1)
    server = SSHServer()
    print(2)
    transport = paramiko.Transport(client_socket)
    print(3)
    key_filename = os.path.expanduser(os.getenv('SERVER_KEY_FILENAME'))
    print(4)
    transport.add_server_key(paramiko.RSAKey(filename=key_filename))
    try:
        print(5)
        transport.set_keepalive(30)  # Keep-alive packets every 30 seconds
        print(6)
        transport.start_server(server=server)
        print(7)
        chan = transport.accept(60)  # Increase timeout to 60 seconds
        print(8)
        if chan is None:
            logging.error("No channel")
            print("NO CHANNEL")
            return
        while True:
            try:
                print(9)
                command_bytes = chan.recv(1024)
                print(f"Received raw bytes: {command_bytes}")

                command = command_bytes.decode('utf-8').strip()
                print(10)
                logging.debug(f"Received command: {command}")
                print(f"command: {command}")
                if not command:
                    logging.error("Received empty command from client.")
                    print("Received empty command from client.")
                    break
                print(11)
                response = server.get_game_state(command)
                print(12)
                logging.debug(f"Sending response: {response}")
                chan.send(response.encode('utf-8'))
                print(13)
            except Exception as e:
                logging.error(f"Exception: {e}")
                print(f"Exception: {e}")
                break

    except Exception as e:
        logging.error(f"Error in handle_client: {e}")
        print(f"Exception handle_client: {e}")

    finally:
        chan.close()
        logging.debug("Channel closed")
        print("CHANNEL CLOSED")

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