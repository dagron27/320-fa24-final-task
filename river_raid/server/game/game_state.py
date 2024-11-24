import threading
from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import Player, FuelDepot, Missile, EnemyB, EnemyJ, EnemyH

class GameState:
    # Add these as class variables
    STATE_RUNNING = "running"
    STATE_GAME_OVER = "game_over"
    
    def __init__(self):
        self.state_lock = threading.RLock()
        self.reset()
        
    def reset(self):
        """Initialize or reset all game state"""
        with self.state_lock:
            self.player = Player(BOARD_WIDTH // 2, BOARD_HEIGHT - 1.5)
            self.missiles = []
            self.fuel_depots = []
            self.enemies = []
            self.score = 0
            self.lives = 3
            self.fuel = 100
            self.game_state = self.STATE_RUNNING  # Set initial state to running
            
    def add_missile(self, missile):
        """Safely add a missile to the game state"""
        with self.state_lock:
            self.missiles.append(missile)
            
    def add_enemy(self, enemy):
        """Safely add an enemy to the game state"""
        with self.state_lock:
            self.enemies.append(enemy)
            
    def add_fuel_depot(self, depot):
        """Safely add a fuel depot to the game state"""
        with self.state_lock:
            self.fuel_depots.append(depot)
            
    def remove_missile(self, missile):
        """Safely remove a missile from the game state"""
        with self.state_lock:
            if missile in self.missiles:
                self.missiles.remove(missile)
                
    def remove_enemy(self, enemy):
        """Safely remove an enemy from the game state"""
        with self.state_lock:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
                
    def remove_fuel_depot(self, depot):
        """Safely remove a fuel depot from the game state"""
        with self.state_lock:
            if depot in self.fuel_depots:
                self.fuel_depots.remove(depot)
                
    def update_score(self, points):
        """Safely update the score"""
        with self.state_lock:
            self.score += points
            
    def update_fuel(self, amount):
        """Safely update fuel and handle fuel depletion"""
        with self.state_lock:
            self.fuel = max(0, min(100, self.fuel + amount))
            if self.fuel <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_state = self.STATE_GAME_OVER
                else:
                    self.fuel = 100
                    
    def get_state(self):
        """Get the current game state in a network-friendly format"""
        with self.state_lock:
            return {
                "player": {
                    "x": self.player.x,
                    "y": self.player.y
                },
                "enemies": [{
                    "x": enemy.x,
                    "y": enemy.y,
                    "type": enemy.type
                } for enemy in self.enemies],
                "fuel_depots": [{
                    "x": depot.x,
                    "y": depot.y
                } for depot in self.fuel_depots],
                "missiles": [{
                    "x": missile.x,
                    "y": missile.y,
                    "type": missile.missile_type
                } for missile in self.missiles],
                "score": self.score,
                "lives": self.lives,
                "fuel": self.fuel,
                "game_state": self.game_state
            }

    def is_running(self):
        """Check if the game is currently running"""
        with self.state_lock:
            return self.game_state == self.STATE_RUNNING

    def is_game_over(self):
        """Check if the game is over"""
        with self.state_lock:
            return self.game_state == self.STATE_GAME_OVER