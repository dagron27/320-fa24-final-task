from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import Player, Obstacle, FuelDepot, Missile
from network import NetworkClient

class ClientGameLogic:
    def __init__(self, host='74.208.201.216', port=8443): 
        self.network_client = NetworkClient(host, port) 
        self.reset_game()

    def reset_game(game_logic):
        game_logic.player = Player(BOARD_WIDTH // 2, BOARD_HEIGHT - 1)
        game_logic.obstacles = []
        game_logic.missiles = []
        game_logic.fuel_depots = []
        game_logic.score = 0
        game_logic.lives = 3
        game_logic.fuel = 100
        game_logic.game_running = True

    def update_game_state(self):
        if not self.game_running:
            return
        
        # Send a command to the server to update game state
        print("Sending 'update_state' command to server...")
        state = self.network_client.send_command({"action": "update_state"})
        print(f"Received state from server: {state}")

        # Update local game state based on the server response
        print("Updating local game state with server response...")
        self.player.x = state["player"]["x"]
        self.player.y = state["player"]["y"]
        self.fuel = state["player"]["fuel"]
        self.lives = state["player"]["lives"]
        print(f"Player updated: x={self.player.x}, y={self.player.y}, fuel={self.fuel}, lives={self.lives}")

        self.obstacles = [Obstacle(obs["x"], obs["y"], obs["direction"]) for obs in state["obstacles"]]
        print(f"Obstacles updated: {len(self.obstacles)} obstacles")

        self.fuel_depots = [FuelDepot(depot["x"], depot["y"]) for depot in state["fuel_depots"]]
        print(f"Fuel depots updated: {len(self.fuel_depots)} depots")

        self.missiles = [Missile(missile["x"], missile["y"], missile["missile_type"]) for missile in state["missiles"]]
        print(f"Missiles updated: {len(self.missiles)} missiles")

        self.score = state["score"]
        print(f"Score updated: {self.score}")

        self.game_running = state["game_running"]
        print(f"Game running status: {self.game_running}")


    def player_move(self, direction):
        command = {"action": f"move_{direction}"}
        self.network_client.send_command(command)

    def player_shoot(self):
        command = {"action": "shoot"}
        self.network_client.send_command(command)
