import socket
import threading
import json
from server.server_logic import ServerGameLogic

class GameServer:
    def __init__(self, host='0.0.0.0', port=8443):
        self.host = host
        self.port = port
        self.game_logic = ServerGameLogic()
        self.clients = []

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Client connected from {client_address}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"Received: {data}")

                # Process the data, update game state
                player_command = json.loads(data)
                self.process_command(player_command)

                # Send updated game state back to client
                updated_state = self.game_logic.get_game_state()  # Use the method from game_logic
                #print(f"Sending updated state:{ updated_state}")
                client_socket.send(json.dumps(updated_state).encode('utf-8'))
            except ConnectionResetError:
                break
        client_socket.close()

    def process_command(self, command):
        action = command.get("action")
        if action == "move_left":
            self.game_logic.player.move("left")
        elif action == "move_right":
            self.game_logic.player.move("right")
        elif action == "shoot":
            missile = self.game_logic.player.shoot()
            self.game_logic.missiles.append(missile)
        elif action == "reset_game":
            self.game_logic.reset_game()
        self.game_logic.update_game_state()

#    def get_game_state(self):
#        state = {
#            "player": {
#                "x": self.game_logic.player.x,
#                "y": self.game_logic.player.y,
#                "fuel": self.game_logic.player.fuel,
#                "lives": self.game_logic.player.lives
#            },
#            "obstacles": [{"x": obs.x, "y": obs.y} for obs in self.game_logic.obstacles],
#            "fuel_depots": [{"x": depot.x, "y": depot.y} for depot in self.game_logic.fuel_depots],
#            "missiles": [{"x": missile.x, "y": missile.y} for missile in self.game_logic.missiles],
#            "score": self.game_logic.score
#        }
#        return state

if __name__ == "__main__":
    server = GameServer()
    server.start()