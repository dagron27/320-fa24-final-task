# client/network/network.py
import paramiko
import os
import time
import json
import logging
from dotenv import load_dotenv
from shared.network_utils import serialize_message, deserialize_message

load_dotenv()

class ClientNetwork:
    def __init__(self):
        self.host = os.getenv("CLIENT_HOST")
        self.port = int(os.getenv("CLIENT_PORT", 2200))
        self.username = os.getenv("CLIENT_USERNAME")
        self.key_filename = os.getenv("CLIENT_KEY_FILENAME")
        self.ssh_client = paramiko.SSHClient()

    def connect(self):
        logging.info("Establishing SSH connection to server...")
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.host, port=self.port, username=self.username, key_filename=self.key_filename)
        self.channel = self.ssh_client.get_transport().open_session()
        self.buffer = ""
        logging.info("SSH connection established.")

    def send_message(self, message):
        message_json = serialize_message(message) + '\n'
        logging.info(f"Sending message: {message_json.strip()}")  # Remove '\n' from log
        self.channel.send(message_json.encode('utf-8'))

    def receive_message(self):
        while True:
            try:
                part = self.channel.recv(1024).decode('utf-8')
                self.buffer += part
                while '\n' in self.buffer:
                    message, self.buffer = self.buffer.split('\n', 1)
                    if message.strip():
                        try:
                            deserialized_message = json.loads(message)
                            if deserialized_message.get('status') == 'ok' and 'game_state' in deserialized_message:
                                game_state = deserialized_message['game_state']
                                # player_pos = game_state['player']
                                # enemies_count = len(game_state['enemies'])
                                # fuel_count = len(game_state['fuel_depots'])
                                # missiles_count = len(game_state['missiles'])
                                # score = game_state['score']
                                # lives = game_state['lives']
                                # fuel = game_state['fuel']
                                # game_status = game_state['game_state']
                                
                                # logging.info(f"Player Position: {player_pos}, "
                                #             f"Enemies Count: {enemies_count}, "
                                #             f"Fuel Depots Count: {fuel_count}, "
                                #             f"Missiles Count: {missiles_count}, "
                                #             f"Score: {score}, Lives: {lives}, "
                                #             f"Fuel: {fuel}, Game State: {game_status}")
                            return deserialized_message
                        except json.JSONDecodeError as e:
                            logging.warning(f"Failed to decode message: {message[:25]}, Error: {e}")
                            continue
                        except ValueError as e:
                            logging.warning(f"Malformed message: {message[:25]}, Error: {e}")
                            continue
                    else:
                        logging.warning(f"Received invalid JSON message: {message[:25]}")
            except Exception as e:
                logging.error(f"Error receiving message: {e}")
                time.sleep(0.1)

    def close(self):
        logging.info("Closing SSH connection.")
        self.channel.close()
        self.ssh_client.close()
