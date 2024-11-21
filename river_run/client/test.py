import os
from dotenv import load_dotenv
import paramiko
import json

# Load environment variables from .env file
load_dotenv()

# Retrieve connection details from the .env file
SSH_HOST = os.getenv("CLIENT_HOST")
SSH_PORT = int(os.getenv("CLIENT_PORT", 22))  # Default to 22 if not specified
SSH_USER = os.getenv("CLIENT_USERNAME")
SSH_KEY = os.getenv("CLIENT_KEY_FILENAME")  # Path to the SSH private key

def test_script():
    # Initialize SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically accept the host key

    try:
        # Connect to the server
        ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, key_filename=SSH_KEY)
        print(f"Connected to {SSH_HOST}")

        # Prepare the command in the expected format (JSON)
        command_data = {
            "action": "move_left"  # Example action to move left
        }
        command_json = json.dumps(command_data)  # Convert to JSON string

        # Send the command to the server
        for i in range(10):
            transport = ssh.get_transport()
            channel = transport.open_session()
            channel.send(command_json)  # Send JSON string via the SSH channel
            print(f"Command sent: {command_json}")

    except Exception as e:
        print(f"Error connecting to server: {e}")

    finally:
        ssh.close()
        print("Connection closed.")

if __name__ == "__main__":
    try:
        print("Trying")
        # Test running the hello.py script
        test_script()
    except Exception as e:
        print(f"An error occurred: {e}")

