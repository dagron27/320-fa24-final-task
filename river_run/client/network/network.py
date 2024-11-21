import paramiko
import os
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
        """Establish an SSH connection to the server."""
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.host, port=self.port, username=self.username, key_filename=self.key_filename)
        print(f"Connected to {self.host}")
        self.channel = self.ssh_client.get_transport().open_session()

    def send_message(self, message):
        """Send a message to the server."""
        message_json = serialize_message(message)
        self.channel.send(message_json.encode('utf-8'))
        print(f"Message sent: {message_json}")

    def receive_message(self):
        """Receive a message from the server."""
        response = self.channel.recv(1024)
        print(f"Raw response received: {response}")
        return deserialize_message(response.decode('utf-8'))

    def close(self):
        """Close the SSH connection."""
        self.channel.close()
        self.ssh_client.close()
        print("SSH connection closed")

#if __name__ == "__main__":
#    client = ClientNetwork()
#    client.connect()
#    client.send_message({"action": "start"})
#    print(f"Server response: {client.receive_message()}")
#    client.send_message({"action": "update", "command": "move player"})
#    print(f"Server response: {client.receive_message()}")
#    client.close()
