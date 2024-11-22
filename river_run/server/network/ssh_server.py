import paramiko
import threading
import time
import sys
from shared.network_utils import serialize_message, deserialize_message
from game.game_logic import ServerGameLogic

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.game_logic = ServerGameLogic()
        self.running = True  # Flag to control the game loop

        # Start the game loop in a separate thread
        self.game_loop_thread = threading.Thread(target=self.game_loop)
        self.game_loop_thread.daemon = True  # Ensure the game loop thread stops when the main thread stops
        self.game_loop_thread.start()

    def game_loop(self):
        while True:
            if self.running:
                self.game_logic.update_game_state()
                #print("Game state updated:", self.game_logic.get_game_state())  # Add detailed logging
            time.sleep(0.2)  # Adjust the sleep time as necessary for your game

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
                #print(f"Received message: {message}")

                if message["action"] == "get_game_state":
                    game_state = self.game_logic.get_game_state()
                    response = {"status": "ok", "game_state": game_state}
                elif message["action"] == "reset_game":
                    self.game_logic.reset_game()  # Reset the game state
                    self.running = True  # Ensure the game loop is running
                    response = {"status": "ok", "game_state": self.game_logic.get_game_state()}
                    print(f"Sending response: {response}")
                elif message["action"] == "quit_game":
                    self.running = False  # Stop the game loop
                    response = {"status": "ok"}
                    print("Quitting server.")
                    channel.send((serialize_message(response) + '\n').encode('utf-8'))
                    self.event.set()  # Signal to quit
                    sys.exit() # Terminate the script
                    break
                else:
                    response = self.game_logic.process_message(message)

                #print(f"Sending response: {response}")
                channel.send((serialize_message(response) + '\n').encode('utf-8'))  # Ensure each response is delimited by a newline
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            channel.close()
