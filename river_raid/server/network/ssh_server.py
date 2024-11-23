import paramiko
import threading
import sys
from shared.network_utils import serialize_message, deserialize_message
from game.game_manager import GameManager

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.game_manager = GameManager()
        self.running = True
        self.buffer = ""
        
        # Start the game manager
        self.game_manager.start()

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
                data = channel.recv(1024).decode('utf-8')
                if not data:
                    break
                
                self.buffer += data
                
                while '\n' in self.buffer:
                    message_str, self.buffer = self.buffer.split('\n', 1)
                    if message_str.strip():
                        try:
                            message = deserialize_message(message_str)
                            if(message == {'action': 'reset_game'}):
                                print(message)
                                print(1)
                            response = self.game_manager.process_message(message)
                            channel.send((serialize_message(response) + '\n').encode('utf-8'))
                        except Exception as e:
                            print(f"Error processing message: {e}")
                            
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.game_manager.stop()
            channel.close()
