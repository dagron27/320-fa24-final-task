import paramiko
import threading
import time
import sys
from shared.network_utils import serialize_message, deserialize_message
from server.game.game_logic import ServerGameLogic

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.game_logic = ServerGameLogic()
        self.running = True
        self.buffer = ""
        
        self.game_loop_thread = threading.Thread(target=self.game_loop)
        self.game_loop_thread.daemon = True
        self.game_loop_thread.start()

    def game_loop(self):
        while True:
            if self.running:
                self.game_logic.update_game_state()
            time.sleep(0.2)

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
                            #print(f"Received message: {message}")
                            
                            #print(1)
                            if message["action"] == "get_game_state":
                                #print(2)
                                game_state = self.game_logic.get_game_state()
                                response = {"status": "ok", "game_state": game_state}
                            elif message["action"] == "reset_game":
                                #print(3)
                                self.game_logic.reset_game()
                                self.running = True
                                response = {"status": "ok", "game_state": self.game_logic.get_game_state()}
                            elif message["action"] == "quit_game":
                                #print(4)
                                self.running = False
                                response = {"status": "ok"}
                                channel.send((serialize_message(response) + '\n').encode('utf-8'))
                                self.event.set()
                                sys.exit()
                            else:
                                response = self.game_logic.process_message(message)
                            
                            #print(5)
                            channel.send((serialize_message(response) + '\n').encode('utf-8'))
                            #print('next')
                            #print(f"Sent response: {response}")
                        except Exception as e:
                            print(f"Error processing message: {e}")
                            
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            channel.close()