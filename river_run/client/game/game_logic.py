from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import Player, EnemyB, EnemyJ, EnemyH, FuelDepot, Missile

class ClientGameLogic:
    def __init__(self, client):
        self.client = client
        self.reset_game()

    def reset_game(self):
        self.player = Player(BOARD_WIDTH // 2, BOARD_HEIGHT - 1)
        self.enemies = []
        self.missiles = []
        self.fuel_depots = []
        self.score = 0
        self.lives = 3
        self.fuel = 100
        self.game_running = True
        print("Game has been reset on client")

    def update_game_state(self, game_state):
        self.player.x = game_state['player']['x']
        self.player.y = game_state['player']['y']
        
        # Reset lists to ensure clean state
        self.enemies.clear()
        self.missiles.clear()
        self.fuel_depots.clear()
        
        # Create enemy instances with a placeholder game_logic reference
        for enemy in game_state['enemies']:
            if enemy['type'] == 'B':
                self.enemies.append(EnemyB(enemy['x'], enemy['y'], self))
            elif enemy['type'] == 'J':
                self.enemies.append(EnemyJ(enemy['x'], enemy['y'], self))
            elif enemy['type'] == 'H':
                self.enemies.append(EnemyH(enemy['x'], enemy['y'], self))

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