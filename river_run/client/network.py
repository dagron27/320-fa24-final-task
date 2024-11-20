import paramiko
import json

class NetworkClient:
    def __init__(self, host, port, username, key_filename):
        self.host = host
        self.port = port
        self.username = username
        self.key_filename = key_filename
        self.client = None
        self.connect_to_server()

    def connect_to_server(self):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.host, port=self.port, username=self.username, key_filename=self.key_filename)

    def send_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(f'python3 server_script.py {json.dumps(command)}')
        response = stdout.read().decode('utf-8')
        return json.loads(response)
