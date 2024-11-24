# server/network/ssh_server.py
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

    def handle_client(self, channel):  # Ensure this method is correctly defined within the class
        try:
            #logging.info("Handling new client.")
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
                            # Deserialize the message from the client
                            message = deserialize_message(message_str)
                            if message is None:
                                logging.error("Failed to deserialize message")
                                continue

                            # Process the message and prepare a response
                            if "actions" in message:
                                responses = []
                                for action in message["actions"]:
                                    response = self.game_manager.process_message(action)
                                    responses.append(response)
                                response_dict = {"status": "ok", "responses": responses}
                                response_str = serialize_message(response_dict) + '\n'
                            else:
                                response = self.game_manager.process_message(message)
                                response_dict = response
                                response_str = serialize_message(response) + '\n'

                            # Log the response before sending
                            if not response_dict.get('status') == 'ok' or 'game_state' not in response_dict:
                                logging.error(f"Response missing proper 'game_state' or 'ok' information: {response_dict}")

                            # Send the response back to the client
                            channel.send(response_str.encode('utf-8'))
                        except Exception as e:
                            logging.error(f"Error processing message: {e}")
        except Exception as e:
            logging.error(f"Error handling client: {e}")
        finally:
            logging.info("Stopping game manager and closing channel.")
            self.game_manager.stop()
            channel.close()
