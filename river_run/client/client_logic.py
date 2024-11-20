from dotenv import load_dotenv
import os
from shared.entities import Player, Obstacle, FuelDepot, Missile
from network import NetworkClient

# Load environment variables from .env file
load_dotenv(dotenv_path='client/.env')

class ClientGameLogic:
    def __init__(self, host='', port=22, username='', key_filename=''):
        host = os.getenv('CLIENT_HOST')
        port = int(os.getenv('CLIENT_PORT', port))
        username = os.getenv('CLIENT_USERNAME')
        key_filename = os.getenv('CLIENT_KEY_FILENAME')
        
        self.network_client = NetworkClient(host, port, username, key_filename)
        initial_state = self.network_client.send_command({"action": "get_initial_state"})
        self.reset_game(initial_state)

    def reset_game(self, initial_state):
        print("game reset")
        self.player = Player(initial_state["player"]["x"], initial_state["player"]["y"])
        self.obstacles = [Obstacle(obs["x"], obs["y"], obs["direction"]) for obs in initial_state["obstacles"]]
        self.missiles = [Missile(missile["x"], missile["y"], missile["missile_type"]) for missile in initial_state["missiles"]]
        self.fuel_depots = [FuelDepot(depot["x"], depot["y"]) for depot in initial_state["fuel_depots"]]
        self.score = initial_state["score"]
        self.lives = initial_state["player"]["lives"]
        self.fuel = initial_state["player"]["fuel"]
        self.game_running = initial_state["game_running"]

    def update_game_state(self):
        if not self.game_running:
            return

        # Send a command to the server to update game state
        state = self.network_client.send_command({"action": "update_state"})

        # Update local game state based on the server response
        self.update_local_state(state)

    def update_local_state(self, state):
        self.player.x = state["player"]["x"]
        self.player.y = state["player"]["y"]
        self.fuel = state["player"]["fuel"]
        self.lives = state["player"]["lives"]
        self.obstacles = [Obstacle(obs["x"], obs["y"], obs["direction"]) for obs in state["obstacles"]]
        self.fuel_depots = [FuelDepot(depot["x"], depot["y"]) for depot in state["fuel_depots"]]
        self.missiles = [Missile(missile["x"], missile["y"], missile["missile_type"]) for missile in state["missiles"]]
        self.score = state["score"]
        self.game_running = state["game_running"]

    def fetch_initial_state(self):
        return self.network_client.send_command({"action": "get_initial_state"})
    
    def reset_server_game(self):
        return self.network_client.send_command({"action": "reset_game"})

    def player_move(self, direction):
        command = {"action": f"move_{direction}"}
        self.network_client.send_command(command)

    def player_shoot(self):
        command = {"action": "shoot"}
        self.network_client.send_command(command)
