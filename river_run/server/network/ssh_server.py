import paramiko
import threading
from shared.network_utils import serialize_message, deserialize_message
from game.game_logic import ServerGameLogic

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