from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import Player, Obstacle, FuelDepot, Missile
from network import NetworkClient

class ClientGameLogic:
    def __init__(self, host='74.208.201.216', port=8443): 
        self.network_client = NetworkClient(host, port) 
        self.reset_game()

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
        state = self.network_client.send_command({"action": "update_state"})
        
        # Update local game state based on the server response
        self.player.x = state["player"]["x"]
        self.player.y = state["player"]["y"]
        self.fuel = state["player"]["fuel"]
        self.lives = state["player"]["lives"]
        self.obstacles = [Obstacle(obs["x"], obs["y"], obs["direction"]) for obs in state["obstacles"]]
        self.fuel_depots = [FuelDepot(depot["x"], depot["y"]) for depot in state["fuel_depots"]]
        self.missiles = [Missile(missile["x"], missile["y"], missile["missile_type"]) for missile in state["missiles"]] 
        self.score = state["score"]
        self.game_running = state["game_running"]

    def player_move(self, direction):
        command = {"action": f"move_{direction}"}
        self.network_client.send_command(command)

    def player_shoot(self):
        command = {"action": "shoot"}
        self.network_client.send_command(command)
