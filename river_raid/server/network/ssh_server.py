import paramiko
import sys
import threading
import logging
from shared.network_utils import serialize_message, deserialize_message
from game.game_manager import GameManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),  # Log to a file named server.log
        logging.StreamHandler(sys.stdout)   # Also log to console
    ]
)

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.game_manager = GameManager()
        self.running = True
        self.buffer = ""
        
        # Start the game manager
        self.game_manager.start()
        logging.info("Game manager started.")

    def check_channel_request(self, kind, chanid):
        logging.info(f"Channel request: {kind}")
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        logging.info(f"Authentication request: username={username}")
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        logging.info(f"Public key authentication request: username={username}")
        return paramiko.AUTH_SUCCESSFUL

    def handle_client(self, channel):
        try:
            logging.info("Handling new client.")
            while True:
                data = channel.recv(1024).decode('utf-8')
                if not data:
                    logging.info("No more data from client. Closing connection.")
                    break
                
                self.buffer += data
                
                while '\n' in self.buffer:
                    message_str, self.buffer = self.buffer.split('\n', 1)
                    if message_str.strip():
                        try:
                            logging.info(f"Received message: {message_str[:25]}")
                            message = deserialize_message(message_str)
                            if "actions" in message:
                                responses = []
                                for action in message["actions"]:
                                    response = self.game_manager.process_message(action)
                                    responses.append(response)
                                response_str = serialize_message({"status": "ok", "responses": responses}) + '\n'
                            else:
                                response = self.game_manager.process_message(message)
                                response_str = serialize_message(response) + '\n'
                            logging.info(f"Sending response: {response_str.strip()[:25]}")
                            channel.send(response_str.encode('utf-8'))
                        except Exception as e:
                            logging.error(f"Error processing message: {e}")
                            
        except Exception as e:
            logging.error(f"Error handling client: {e}")
        finally:
            logging.info("Stopping game manager and closing channel.")
            self.game_manager.stop()
            channel.close()
