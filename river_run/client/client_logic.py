import socket
import json
import random
from shared.entities import Player, Obstacle, FuelDepot, Missile

BOARD_WIDTH = 10
BOARD_HEIGHT = 10

class ClientGameLogic:
    def __init__(self, host='74.208.201.216', port=8443):
        self.host = host
        self.port = port
        self.client_socket = None
        self.connect_to_server()
        self.reset_game()

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def send_command(self, command):
        self.client_socket.send(json.dumps(command).encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        return json.loads(response)

    def reset_game(self):
        self.player = Player(BOARD_WIDTH // 2, BOARD_HEIGHT - 1)
        self.obstacles = []
        self.missiles = []
        self.fuel_depots = []
        self.score = 0
        self.lives = 3
        self.fuel = 100
        self.game_running = True

    def update_game_state(self):
        if not self.game_running:
            return

        # Send a command to the server to update game state
        state = self.send_command({"action": "update_state"})

        # Update local game state based on the server response
        self.player.x = state["player"]["x"]
        self.player.y = state["player"]["y"]
        self.fuel = state["player"]["fuel"]
        self.lives = state["player"]["lives"]
        self.obstacles = [Obstacle(obs["x"], obs["y"]) for obs in state["obstacles"]]
        self.fuel_depots = [FuelDepot(depot["x"], depot["y"]) for depot in state["fuel_depots"]]
        self.missiles = [Missile(missile["x"], missile["y"], missile["missile_type"]) for missile in state["missiles"]]
        self.score = state["score"]
        self.game_running = state["game_running"]  # Update game running status

    def player_move(self, direction):
        command = {"action": f"move_{direction}"}
        self.send_command(command)

    def player_shoot(self):
        command = {"action": "shoot"}
        self.send_command(command)
