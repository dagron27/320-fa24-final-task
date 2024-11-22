import paramiko
import os
from dotenv import load_dotenv
from shared.network_utils import serialize_message, deserialize_message
import json

load_dotenv()

class ClientNetwork:
    def __init__(self):
        self.host = os.getenv("CLIENT_HOST")
        self.port = int(os.getenv("CLIENT_PORT", 2200))
        self.username = os.getenv("CLIENT_USERNAME")
        self.key_filename = os.getenv("CLIENT_KEY_FILENAME")
        self.ssh_client = paramiko.SSHClient()

    def connect(self):
        """Establish an SSH connection to the server."""
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.host, port=self.port, username=self.username, key_filename=self.key_filename)
        self.channel = self.ssh_client.get_transport().open_session()
        self.buffer = ""  # Initialize buffer for received messages

    def send_message(self, message):
        """Send a message to the server."""
        message_json = serialize_message(message) + '\n'  # Add newline to delimit messages
        self.channel.send(message_json.encode('utf-8'))

    def receive_message(self):
        """Receive a message from the server."""
        while True:
            part = self.channel.recv(1024).decode('utf-8')
            self.buffer += part
            while '\n' in self.buffer:
                message, self.buffer = self.buffer.split('\n', 1)
                if message.strip():
                    try:
                        return deserialize_message(message)
                    except json.JSONDecodeError:
                        continue

    def close(self):
        """Close the SSH connection."""
        self.channel.close()
        self.ssh_client.close()
