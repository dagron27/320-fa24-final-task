from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import Player, Obstacle, FuelDepot, Missile

class ClientGameLogic:
    def __init__(self, client):
        self.client = client
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

    def update_game_state(self, game_state):
        #print(game_state)
        self.player.x = game_state['player']['x']
        self.player.y = game_state['player']['y']
        self.obstacles = [Obstacle(obs['x'], obs['y'], obs['direction']) for obs in game_state['obstacles']]
        self.missiles = [Missile(missile['x'], missile['y'], missile['type']) for missile in game_state['missiles']]
        self.fuel_depots = [FuelDepot(depot['x'], depot['y']) for depot in game_state['fuel_depots']]
        self.score = game_state['score']
        self.lives = game_state['lives']
        self.fuel = game_state['fuel']
        self.game_running = game_state['game_running']

    def player_move(self, direction):
        if self.game_running:
            move_message = {"action": "move", "direction": direction}
            self.client.send_message(move_message)
            response = self.client.receive_message()
            self.update_game_state(response['game_state'])

    def player_shoot(self):
        if self.game_running:
            shoot_message = {"action": "shoot"}
            self.client.send_message(shoot_message)
            response = self.client.receive_message()
            self.update_game_state(response['game_state'])